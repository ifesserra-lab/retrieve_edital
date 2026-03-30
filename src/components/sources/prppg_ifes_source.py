import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup, Tag

from src.core.interfaces import ISource
from src.domain.models import RawEdital

logger = logging.getLogger(__name__)

PRPPG_IFES_EDITAIS_URL = "https://sigpesq.ifes.edu.br/publico/Editais.aspx"
POSTBACK_TARGET_REGEX = re.compile(r"__doPostBack\('([^']+)'")
LISTING_DATE_REGEX = re.compile(r"(\d{2}/\d{2}/\d{4})")
POSITIVE_MAIN_PDF_TOKENS = (
    "edital",
    "chamada pública",
    "chamada publica",
    "chamada",
    "retificado",
    "retificação",
    "retificacao",
)
NEGATIVE_MAIN_PDF_TOKENS = ("resultado", "ata", "portaria", "etapa", "anexo")
PRIMARY_PERIOD_TOKENS = (
    "inscrição",
    "inscricao",
    "manifestação",
    "manifestacao",
    "interesse",
    "período",
    "periodo",
    "submiss",
    "envio",
    "fluxo",
)


def _dd_mm_yyyy_to_iso(date_str: str) -> str:
    return datetime.strptime(date_str.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")


class PrppgIfesSource(ISource[RawEdital]):
    """
    Extractor for PRPPG/IFES editais from the public SIGPesq portal.
    Uses ASP.NET postbacks with requests.Session, resolves detail pages to the
    stable `?cod=` URL and downloads only the main PDF for Mistral OCR.
    """

    def __init__(
        self,
        start_url: str = PRPPG_IFES_EDITAIS_URL,
        current_year: Optional[int] = None,
        processed_urls: Optional[Set[str]] = None,
        timeout: int = 30,
        session=None,
    ) -> None:
        self.start_url = start_url
        self.current_year = current_year if current_year is not None else datetime.now().year
        self.processed_urls = processed_urls or set()
        self.timeout = timeout
        self.session = session or requests.Session()

    def _to_soup(self, html_or_soup) -> BeautifulSoup:
        if isinstance(html_or_soup, BeautifulSoup):
            return html_or_soup
        return BeautifulSoup(html_or_soup, "html.parser")

    def _extract_hidden_fields(self, html_or_soup) -> Dict[str, str]:
        soup = self._to_soup(html_or_soup)
        result: Dict[str, str] = {}
        for field_name in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION"):
            field = soup.select_one(f"#{field_name}")
            if field and field.get("value"):
                result[field_name] = field["value"]
        return result

    def _extract_postback_target(self, href: str) -> str:
        if not href:
            return ""
        match = POSTBACK_TARGET_REGEX.search(href)
        return match.group(1) if match else ""

    def _extract_start_end_dates(self, text: str) -> Tuple[str, str]:
        matches = LISTING_DATE_REGEX.findall(text or "")
        if not matches:
            iso_matches = re.findall(r"\d{4}-\d{2}-\d{2}", text or "")
            if not iso_matches:
                return "", ""
            return iso_matches[0], iso_matches[-1] if len(iso_matches) > 1 else ""
        start = _dd_mm_yyyy_to_iso(matches[0])
        end = _dd_mm_yyyy_to_iso(matches[-1]) if len(matches) > 1 else ""
        return start, end

    def _extract_listing_rows(self, html_or_soup) -> List[Dict[str, str]]:
        soup = self._to_soup(html_or_soup)
        table = soup.select_one("#Conteudo_gvwLista")
        if table is None:
            return []

        listing_rows: List[Dict[str, str]] = []
        for row in table.find_all("tr", recursive=False):
            classes = row.get("class", [])
            if "gvwPager" in classes:
                continue

            detail_anchor = row.select_one("a[href*='btnDetalhes']")
            title_cell = row.select_one("td.font-weight-bold")
            if detail_anchor is None or title_cell is None:
                continue

            date_badge = row.select_one("span.badge-outline-dark")
            status_badge = row.select_one("span.badge:not(.badge-outline-dark)")
            summary_row = row.select("table.w-100 > tr")
            summary = ""
            if len(summary_row) >= 2:
                summary_cells = summary_row[1].find_all("td")
                if summary_cells:
                    summary = summary_cells[0].get_text(" ", strip=True)

            full_title = title_cell.get_text(" ", strip=True)
            date_text = date_badge.get_text(" ", strip=True) if date_badge else ""
            clean_title = re.sub(r"\s+", " ", full_title.replace(date_text, "")).strip()
            start_date, end_date = self._extract_start_end_dates(date_text)

            listing_rows.append(
                {
                    "status": (status_badge.get_text(" ", strip=True) if status_badge else "aberto").lower(),
                    "title": clean_title,
                    "summary": summary,
                    "detail_event_target": self._extract_postback_target(detail_anchor.get("href", "")),
                    "listing_start_date": start_date,
                    "listing_end_date": end_date,
                }
            )

        return listing_rows

    def _parse_total_pages(self, html_or_soup) -> int:
        soup = self._to_soup(html_or_soup)
        max_page = 1
        for anchor in soup.select("#Conteudo_gvwLista tr.gvwPager a[href]"):
            href = anchor.get("href", "")
            match = re.search(r"Page\$(\d+)", href)
            if match:
                max_page = max(max_page, int(match.group(1)))
        return max_page

    def _fetch_listing_page_html(self, page_number: int, previous_html: Optional[str] = None) -> str:
        if page_number == 1:
            response = self.session.get(self.start_url, timeout=self.timeout)
        else:
            payload = self._extract_hidden_fields(previous_html)
            payload["__EVENTTARGET"] = "ctl00$Conteudo$gvwLista"
            payload["__EVENTARGUMENT"] = f"Page${page_number}"
            response = self.session.post(
                self.start_url,
                data=payload,
                timeout=self.timeout,
                allow_redirects=True,
            )
        response.raise_for_status()
        return response.text

    def _resolve_detail_page(self, listing_html: str, event_target: str) -> Tuple[str, str]:
        payload = self._extract_hidden_fields(listing_html)
        payload["__EVENTTARGET"] = event_target
        payload["__EVENTARGUMENT"] = ""
        response = self.session.post(
            self.start_url,
            data=payload,
            timeout=self.timeout,
            allow_redirects=True,
        )
        response.raise_for_status()
        return response.url, response.text

    def _build_attachment_link(self, detail_url: str, event_target: str) -> str:
        return f"{detail_url}#downloadTarget={quote(event_target, safe='')}"

    def _find_table_by_heading(self, detail_container: Tag, heading: str) -> Optional[Tag]:
        for table in detail_container.select("table.gvwTable"):
            header = table.find("th")
            if header and heading.lower() in header.get_text(" ", strip=True).lower():
                return table
        return None

    def _extract_attachment_entries(self, detail_container: Tag, detail_url: str) -> List[Dict[str, str]]:
        table = self._find_table_by_heading(detail_container, "Anexos")
        if table is None:
            return []

        attachments: List[Dict[str, str]] = []
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 3:
                continue
            anchor = cells[1].find("a", href=True)
            if anchor is None:
                continue
            event_target = self._extract_postback_target(anchor["href"])
            if not event_target:
                continue
            extension = cells[0].get_text(" ", strip=True).lower() or "anexo"
            title = anchor.get_text(" ", strip=True)
            attachments.append(
                {
                    "titulo": title,
                    "link": self._build_attachment_link(detail_url, event_target),
                    "tipo": extension,
                    "event_target": event_target,
                }
            )
        return attachments

    def _select_main_attachment(self, attachments: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        best_attachment = None
        best_score = -10**9

        for attachment in attachments:
            if attachment.get("tipo") != "pdf":
                continue

            haystack = attachment.get("titulo", "").lower()
            score = 0
            if any(token in haystack for token in POSITIVE_MAIN_PDF_TOKENS):
                score += 5
            if "edital" in haystack:
                score += 4
            if any(token in haystack for token in NEGATIVE_MAIN_PDF_TOKENS):
                score -= 6

            if score > best_score:
                best_attachment = attachment
                best_score = score

        return best_attachment

    def _extract_primary_period(
        self,
        cronograma_rows: List[Dict[str, str]],
    ) -> Tuple[str, str]:
        for row in cronograma_rows:
            event_name = row["evento"].lower()
            if row["start"] and any(token in event_name for token in PRIMARY_PERIOD_TOKENS):
                return row["start"], row["end"]

        for row in cronograma_rows:
            if row["start"] and row["end"]:
                return row["start"], row["end"]

        for row in cronograma_rows:
            if row["start"]:
                return row["start"], row["end"]

        return "", ""

    def _extract_cronograma(
        self,
        detail_container: Tag,
        listing_start_date: str,
        listing_end_date: str,
    ) -> Tuple[List[Dict[str, str]], str, str]:
        table = self._find_table_by_heading(detail_container, "Cronograma")
        cronograma_rows: List[Dict[str, str]] = []
        cronograma: List[Dict[str, str]] = []

        if table is not None:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) != 2:
                    continue
                event_name = cells[0].get_text(" ", strip=True)
                raw_date = cells[1].get_text(" ", strip=True)
                start_date, end_date = self._extract_start_end_dates(raw_date)
                cronograma_rows.append(
                    {
                        "evento": event_name,
                        "raw_date": raw_date,
                        "start": start_date,
                        "end": end_date,
                    }
                )

        primary_start = listing_start_date
        primary_end = listing_end_date
        if not primary_start:
            primary_start, primary_end = self._extract_primary_period(cronograma_rows)

        if primary_start:
            cronograma.append({"evento": "início do período do edital", "data": primary_start})
        if primary_end:
            cronograma.append({"evento": "fim do período do edital", "data": primary_end})

        for row in cronograma_rows:
            if row["start"]:
                cronograma.append({"evento": row["evento"], "data": row["start"]})

        return cronograma, primary_start, primary_end

    def _extract_detail_description(self, detail_container: Tag) -> str:
        subtitle = detail_container.select_one("p.card-subtitle")
        subtitle_text = subtitle.get_text(" ", strip=True) if subtitle else ""

        info_paragraph = ""
        for bold in detail_container.find_all("b"):
            if "informações gerais" in bold.get_text(" ", strip=True).lower():
                sibling = bold.find_next("p")
                if sibling:
                    info_paragraph = sibling.get_text(" ", strip=True)
                break

        parts = [part for part in (subtitle_text, info_paragraph) if part]
        return "\n\n".join(parts)

    def _download_attachment_bytes(
        self,
        detail_url: str,
        detail_html: str,
        event_target: str,
    ) -> Optional[bytes]:
        payload = self._extract_hidden_fields(detail_html)
        payload["__EVENTTARGET"] = event_target
        payload["__EVENTARGUMENT"] = ""
        try:
            response = self.session.post(
                detail_url,
                data=payload,
                timeout=self.timeout,
                allow_redirects=True,
            )
            response.raise_for_status()
            return response.content
        except Exception as exc:
            logger.error("Error downloading PRPPG/IFES attachment %s: %s", event_target, exc)
            return None

    def _extract_detail_page(
        self,
        detail_html: str,
        detail_url: str,
        listing_item: Dict[str, str],
    ) -> Optional[RawEdital]:
        soup = self._to_soup(detail_html)
        detail_container = soup.select_one("#Conteudo_pnlDetalhesEdital")
        if detail_container is None:
            return None

        title_el = detail_container.find("h4")
        raw_title = title_el.get_text(" ", strip=True) if title_el else listing_item["title"]
        title = re.sub(r"^\s*Voltar\s+", "", re.sub(r"\s+", " ", raw_title)).strip()

        cronograma, primary_start, _primary_end = self._extract_cronograma(
            detail_container,
            listing_item["listing_start_date"],
            listing_item["listing_end_date"],
        )
        if not primary_start or not primary_start.startswith(str(self.current_year)):
            return None

        internal_attachments = self._extract_attachment_entries(detail_container, detail_url)
        main_attachment = self._select_main_attachment(internal_attachments)
        pdf_content = None
        if main_attachment:
            pdf_content = self._download_attachment_bytes(
                detail_url,
                detail_html,
                main_attachment["event_target"],
            )

        return RawEdital(
            title=title,
            url=detail_url,
            raw_agency="PRPPG/IFES",
            raw_description=self._extract_detail_description(detail_container),
            pdf_content=pdf_content,
            raw_status=listing_item["status"],
            raw_cronograma=cronograma,
            raw_tags=["prppg", "ifes", str(self.current_year)],
            raw_anexos=[
                {
                    "titulo": attachment["titulo"],
                    "link": attachment["link"],
                    "tipo": attachment["tipo"],
                }
                for attachment in internal_attachments
            ],
        )

    def read(self) -> List[RawEdital]:
        try:
            page_html = self._fetch_listing_page_html(page_number=1)
            total_pages = self._parse_total_pages(page_html)
            raw_editais: List[RawEdital] = []

            for page_number in range(1, total_pages + 1):
                if page_number > 1:
                    page_html = self._fetch_listing_page_html(
                        page_number=page_number,
                        previous_html=page_html,
                    )

                for listing_item in self._extract_listing_rows(page_html):
                    if listing_item["listing_start_date"]:
                        if not listing_item["listing_start_date"].startswith(str(self.current_year)):
                            continue

                    try:
                        detail_url, detail_html = self._resolve_detail_page(
                            page_html,
                            listing_item["detail_event_target"],
                        )
                        if detail_url in self.processed_urls:
                            continue
                        raw = self._extract_detail_page(detail_html, detail_url, listing_item)
                        if raw is not None:
                            raw_editais.append(raw)
                    except Exception as exc:
                        logger.error(
                            "Error extracting PRPPG/IFES detail %s: %s",
                            listing_item["title"],
                            exc,
                        )

            logger.info(
                "PrppgIfesSource extracted %s editais with start date in %s.",
                len(raw_editais),
                self.current_year,
            )
            return raw_editais
        except Exception as exc:
            logger.error("Error during PRPPG/IFES extraction: %s", exc)
            return []
