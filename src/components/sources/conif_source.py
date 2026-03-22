import logging
import re
from datetime import datetime
from typing import List, Optional, Set
from urllib.parse import urljoin
from urllib.request import urlopen

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from src.core.interfaces import ISource
from src.domain.models import RawEdital

logger = logging.getLogger(__name__)

CONIF_EDITAIS_URL = "https://portal.conif.org.br/editais"
CONIF_BASE_URL = "https://portal.conif.org.br"

PT_MONTHS = {
    "janeiro": "01",
    "fevereiro": "02",
    "marco": "03",
    "março": "03",
    "abril": "04",
    "maio": "05",
    "junho": "06",
    "julho": "07",
    "agosto": "08",
    "setembro": "09",
    "outubro": "10",
    "novembro": "11",
    "dezembro": "12",
}


def _normalize_conif_url(href: str) -> str:
    if not href:
        return CONIF_EDITAIS_URL
    if href.startswith("http"):
        return href
    return urljoin(CONIF_BASE_URL, href)


def _extract_iso_date_from_pt_text(text: str) -> Optional[str]:
    normalized = re.sub(r"\s+de\s+", " ", text.lower())
    match = re.search(r"(\d{1,2})\s+([a-zç]+)\s+(\d{4})", normalized)
    if not match:
        return None
    day, month_name, year = match.groups()
    month = PT_MONTHS.get(month_name)
    if not month:
        return None
    return f"{year}-{month}-{int(day):02d}"


class ConifSource(ISource[RawEdital]):
    """
    Extractor for CONIF editais.
    Reads the editais listing, keeps only current-year detail links and
    visits each detail page to enrich title, description, publication date and attachments.
    """

    def __init__(
        self,
        start_url: str = CONIF_EDITAIS_URL,
        current_year: Optional[int] = None,
        processed_urls: Optional[Set[str]] = None,
    ) -> None:
        self.start_url = start_url
        self.current_year = current_year if current_year is not None else datetime.now().year
        self.processed_urls = processed_urls or set()

    def _extract_current_year_links(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        current_year_token = f"/editais/{self.current_year}/"
        found = {}

        for anchor in soup.select("a[href]"):
            href = anchor.get("href", "").strip()
            if current_year_token not in href:
                continue

            title = anchor.get_text(" ", strip=True)
            if not title or title.lower() == "leia mais":
                heading = anchor.find_parent(["h1", "h2", "h3", "h4"])
                if heading:
                    title = heading.get_text(" ", strip=True)
            if not title or title.lower() == "leia mais":
                continue

            normalized_url = _normalize_conif_url(href)
            if normalized_url in self.processed_urls:
                continue

            found[normalized_url] = {
                "title": title,
                "url": normalized_url,
            }

        return list(found.values())

    def _download_file_bytes(self, url: str) -> Optional[bytes]:
        try:
            with urlopen(url, timeout=30) as response:
                return response.read()
        except Exception as exc:
            logger.error("Error downloading CONIF file %s: %s", url, exc)
            return None

    def _is_detail_attachment(self, normalized_url: str, label: str) -> bool:
        lower_href = normalized_url.lower()
        lower_label = label.lower()
        return (
            lower_href.endswith(".pdf")
            or "anexo" in lower_label
            or "retifica" in lower_label
            or "resultado" in lower_label
            or "edital" in lower_label
        )

    def _extract_detail_page(self, page, detail_url: str, fallback_title: str) -> Optional[RawEdital]:
        page.goto(detail_url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle", timeout=20000)

        soup = BeautifulSoup(page.content(), "html.parser")
        title_el = soup.find(["h1", "h2"], string=True)
        title = title_el.get_text(" ", strip=True) if title_el else fallback_title

        date_iso = ""
        date_candidates = [el.get_text(" ", strip=True) for el in soup.find_all(["time", "p", "div", "span"])]
        for candidate in date_candidates:
            parsed = _extract_iso_date_from_pt_text(candidate)
            if parsed:
                date_iso = parsed
                break

        paragraphs = []
        for paragraph in soup.find_all(["p", "div"]):
            text = paragraph.get_text(" ", strip=True)
            if len(text) < 40:
                continue
            if text == title:
                continue
            if "assine nossa newsletter" in text.lower():
                continue
            paragraphs.append(text)
        description = paragraphs[0] if paragraphs else ""

        anexos = []
        seen_links = set()
        main_pdf_url = None
        for anchor in soup.select("a[href]"):
            href = anchor.get("href", "").strip()
            label = anchor.get_text(" ", strip=True)
            normalized_url = _normalize_conif_url(href)
            if normalized_url == detail_url or normalized_url in seen_links:
                continue
            is_attachment = self._is_detail_attachment(normalized_url, label)
            if not is_attachment:
                continue
            if main_pdf_url is None and "edital" in label.lower() and normalized_url.lower().endswith(".pdf"):
                main_pdf_url = normalized_url
            anexos.append(
                {
                    "titulo": label or "Documento",
                    "link": normalized_url,
                    "tipo": "anexo",
                }
            )
            seen_links.add(normalized_url)

        cronograma = []
        if date_iso:
            cronograma.append({"evento": "data de publicação", "data": date_iso})

        pdf_content = None
        if main_pdf_url:
            pdf_content = self._download_file_bytes(main_pdf_url)

        return RawEdital(
            title=title or fallback_title,
            url=detail_url,
            raw_agency="CONIF",
            raw_description=description,
            pdf_content=pdf_content,
            raw_cronograma=cronograma,
            raw_tags=["conif", str(self.current_year)],
            raw_anexos=anexos,
        )

    def read(self) -> List[RawEdital]:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(self.start_url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_load_state("networkidle", timeout=20000)

                links = self._extract_current_year_links(page.content())
                raw_editais: List[RawEdital] = []

                for item in links:
                    try:
                        raw = self._extract_detail_page(page, item["url"], item["title"])
                        if raw:
                            raw_editais.append(raw)
                    except Exception as exc:
                        logger.error("Error extracting CONIF detail %s: %s", item["url"], exc)

                browser.close()
                logger.info(
                    "ConifSource extracted %s current-year editais (year=%s).",
                    len(raw_editais),
                    self.current_year,
                )
                return raw_editais
        except Exception as exc:
            logger.error("Error during CONIF extraction: %s", exc)
            return []
