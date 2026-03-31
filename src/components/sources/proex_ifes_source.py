import logging
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag

from src.core.interfaces import ISource
from src.domain.models import RawEdital

logger = logging.getLogger(__name__)

PROEX_IFES_EDITAIS_URL = "https://proex.ifes.edu.br/editais"
PROEX_IFES_BASE_URL = "https://proex.ifes.edu.br"
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}
DOCUMENT_EXTENSIONS = (".pdf", ".doc", ".docx", ".odt", ".ods", ".zip", ".rar")
POSITIVE_MAIN_ATTACHMENT_TOKENS = (
    "edital",
    "chamada pública",
    "chamada publica",
    "retifica",
    "retificado",
)
NEGATIVE_MAIN_ATTACHMENT_TOKENS = (
    "resultado",
    "inscri",
    "matricul",
    "sorteio",
    "comunicado",
    "convoca",
    "recurso",
    "entrevista",
)


def _normalize_proex_ifes_url(href: str) -> str:
    if not href:
        return PROEX_IFES_EDITAIS_URL
    cleaned_href = href.replace("\t", "").strip()
    if cleaned_href.startswith("http"):
        return cleaned_href
    return urljoin(PROEX_IFES_BASE_URL, cleaned_href)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("\xa0", " ")).strip()


def _infer_attachment_type(url: str) -> str:
    path = urlparse(url).path.lower().strip()
    for extension in DOCUMENT_EXTENSIONS:
        if path.endswith(extension):
            return extension.lstrip(".")
    return "anexo"


def _is_document_link(url: str) -> bool:
    return _infer_attachment_type(url) != "anexo"


class ProexIfesSource(ISource[RawEdital]):
    """
    Extractor for PROEX/IFES editais.
    Reads the public listing page, keeps only the current-year "Editais abertos"
    entries and downloads the main edital PDF for OCR.
    """

    def __init__(
        self,
        start_url: str = PROEX_IFES_EDITAIS_URL,
        processed_urls: Optional[Set[str]] = None,
        current_year: Optional[int] = None,
        timeout: int = 30,
        session=None,
    ) -> None:
        self.start_url = start_url
        self.processed_urls = processed_urls or set()
        self.current_year = current_year if current_year is not None else datetime.now().year
        self.timeout = timeout
        self.session = session or requests.Session()
        if hasattr(self.session, "headers"):
            for header_name, header_value in DEFAULT_REQUEST_HEADERS.items():
                self.session.headers.setdefault(header_name, header_value)

    def _get_current_year_heading(self, soup: BeautifulSoup) -> Optional[Tag]:
        listing_heading = None
        for candidate in soup.find_all("h2"):
            if "Editais abertos" in _normalize_text(candidate.get_text(" ", strip=True)):
                listing_heading = candidate
                break
        if listing_heading is None:
            return None

        for sibling in listing_heading.find_next_siblings():
            if not isinstance(sibling, Tag):
                continue
            if sibling.name == "h3" and _normalize_text(sibling.get_text(" ", strip=True)) == str(self.current_year):
                return sibling
        return None

    def _is_edital_title_tag(self, tag: Tag) -> bool:
        if tag.name not in {"p", "h3", "h4"}:
            return False
        if tag.select_one("a[href]") is not None:
            return False

        text = _normalize_text(tag.get_text(" ", strip=True))
        lower_text = text.lower()
        if not text or str(self.current_year) not in text:
            return False
        if not (tag.find("strong") or tag.name.startswith("h")):
            return False
        return lower_text.startswith(("edital", "chamada"))

    def _extract_current_year_entries(self, html: str) -> List[Dict[str, object]]:
        soup = BeautifulSoup(html, "html.parser")
        year_heading = self._get_current_year_heading(soup)
        if year_heading is None:
            return []

        entries: List[Dict[str, object]] = []
        current_entry: Optional[Dict[str, object]] = None
        seen_titles = set()
        seen_links: Set[str] = set()

        for sibling in year_heading.find_next_siblings():
            if not isinstance(sibling, Tag):
                continue
            if sibling.name == "h3":
                break

            if self._is_edital_title_tag(sibling):
                title = _normalize_text(sibling.get_text(" ", strip=True))
                if title in seen_titles:
                    current_entry = None
                    continue
                current_entry = {"title": title, "attachments": []}
                entries.append(current_entry)
                seen_titles.add(title)
                continue

            if current_entry is None:
                continue

            for anchor in sibling.select("a[href]"):
                href = (anchor.get("href") or "").strip()
                label = _normalize_text(anchor.get_text(" ", strip=True))
                if not href or not label:
                    continue

                normalized_url = _normalize_proex_ifes_url(href)
                if normalized_url in seen_links or not _is_document_link(normalized_url):
                    continue

                current_entry["attachments"].append(
                    {
                        "titulo": label,
                        "link": normalized_url,
                        "tipo": _infer_attachment_type(normalized_url),
                    }
                )
                seen_links.add(normalized_url)

        return entries

    def _select_main_attachment(
        self,
        attachments: List[Dict[str, str]],
    ) -> Optional[Dict[str, str]]:
        best_attachment = None
        best_score = -10**9

        for attachment in attachments:
            if attachment.get("tipo") != "pdf":
                continue

            haystack = (
                f"{attachment.get('titulo', '')} {attachment.get('link', '')}"
            ).lower()
            score = 0

            if any(token in haystack for token in POSITIVE_MAIN_ATTACHMENT_TOKENS):
                score += 6
            if "edital" in haystack:
                score += 4
            if any(token in haystack for token in NEGATIVE_MAIN_ATTACHMENT_TOKENS):
                score -= 7

            if score > best_score:
                best_score = score
                best_attachment = attachment

        return best_attachment if best_score > 0 else None

    def _download_file_bytes(self, url: str) -> Optional[bytes]:
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            content_type = (response.headers.get("content-type") or "").lower()
            if "application/pdf" not in content_type and not url.lower().endswith(".pdf"):
                logger.info(
                    "Skipping non-PDF PROEX/IFES attachment for OCR: %s (%s)",
                    url,
                    content_type or "unknown",
                )
                return None
            return response.content
        except Exception as exc:
            logger.warning(
                "Requests download failed for PROEX/IFES file %s: %s. Trying curl fallback.",
                url,
                exc,
            )
            return self._download_file_bytes_with_curl(url)

    def _download_file_bytes_with_curl(self, url: str) -> Optional[bytes]:
        try:
            completed = subprocess.run(
                ["curl", "-L", "--max-time", str(self.timeout), url],
                capture_output=True,
                check=True,
            )
            return completed.stdout
        except Exception as exc:
            logger.error("Error downloading PROEX/IFES file with curl %s: %s", url, exc)
            return None

    def _fetch_listing_html(self) -> str:
        try:
            response = self.session.get(self.start_url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as exc:
            logger.warning(
                "Requests fetch failed for PROEX/IFES listing %s: %s. Trying curl fallback.",
                self.start_url,
                exc,
            )
            try:
                completed = subprocess.run(
                    ["curl", "-L", "--max-time", str(self.timeout), self.start_url],
                    capture_output=True,
                    check=True,
                    text=True,
                )
                return completed.stdout
            except Exception as curl_exc:
                raise RuntimeError(
                    f"Unable to fetch PROEX/IFES listing via requests or curl: {curl_exc}"
                ) from curl_exc

    def read(self) -> List[RawEdital]:
        try:
            listing_html = self._fetch_listing_html()

            raw_editais: List[RawEdital] = []
            for entry in self._extract_current_year_entries(listing_html):
                title = str(entry.get("title") or "").strip()
                attachments = list(entry.get("attachments") or [])
                main_attachment = self._select_main_attachment(attachments)
                if not title or main_attachment is None:
                    continue
                if main_attachment["link"] in self.processed_urls:
                    continue

                raw_editais.append(
                    RawEdital(
                        title=title,
                        url=main_attachment["link"],
                        raw_agency="PROEX/IFES",
                        raw_description="",
                        pdf_content=self._download_file_bytes(main_attachment["link"]),
                        raw_status="aberto",
                        raw_tags=["proex", "ifes", str(self.current_year)],
                        raw_anexos=attachments,
                    )
                )

            logger.info(
                "ProexIfesSource extracted %s current-year editais (year=%s).",
                len(raw_editais),
                self.current_year,
            )
            return raw_editais
        except Exception as exc:
            logger.error("Error during PROEX/IFES extraction: %s", exc)
            return []
