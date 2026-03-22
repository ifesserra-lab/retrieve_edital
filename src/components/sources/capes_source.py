import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin
from urllib.request import urlopen

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from src.core.interfaces import ISource
from src.domain.models import RawEdital

logger = logging.getLogger(__name__)

CAPES_EDITAIS_URL = "https://www.gov.br/capes/pt-br/assuntos/editais-e-resultados-capes"
CAPES_BASE_URL = "https://www.gov.br"
PDF_URL_REGEX = re.compile(r"https://[^\s\"'<>]+\.pdf", re.IGNORECASE)
NEGATIVE_PDF_TOKENS = ("resultado", "manual", "flyer", "apresentacao", "cartao")


def _normalize_capes_url(href: str) -> str:
    if not href:
        return CAPES_EDITAIS_URL
    if href.startswith("http"):
        return href
    return urljoin(CAPES_BASE_URL, href)


def _is_pdf_link(url: str) -> bool:
    return url.lower().endswith(".pdf")


class CapesSource(ISource[RawEdital]):
    """
    Extractor for CAPES editais.
    Reads the "Editais Abertos" section, visits each detail page and collects
    PDF attachments, preferring edital/chamada PDFs as OCR input.
    """

    def __init__(
        self,
        start_url: str = CAPES_EDITAIS_URL,
        processed_urls: Optional[Set[str]] = None,
        current_year: Optional[int] = None,
    ) -> None:
        self.start_url = start_url
        self.processed_urls = processed_urls or set()
        self.current_year = current_year if current_year is not None else datetime.now().year

    def _infer_year_from_text(self, text: str) -> Optional[int]:
        years = [int(value) for value in re.findall(r"\b(20\d{2})\b", text or "")]
        return max(years) if years else None

    def _extract_listing_entries(self, html: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        section_header = None

        for candidate in soup.find_all(["h2", "h3"]):
            text = candidate.get_text(" ", strip=True)
            if "Editais Abertos" in text:
                section_header = candidate
                break

        if section_header is None:
            return []

        entries: List[Dict[str, str]] = []
        seen_urls = set()
        container = section_header.find_next(["div", "ul"])
        if container is None:
            return []

        for anchor in container.select("a[href]"):
            href = (anchor.get("href") or "").strip()
            title = anchor.get_text(" ", strip=True)
            if not href or not title:
                continue

            normalized_url = _normalize_capes_url(href)
            if _is_pdf_link(normalized_url):
                continue
            if normalized_url in self.processed_urls or normalized_url in seen_urls:
                continue
            if "gov.br/capes" not in normalized_url:
                continue
            inferred_year = self._infer_year_from_text(f"{title} {normalized_url}")
            if inferred_year is not None and inferred_year < self.current_year:
                continue

            entries.append({"title": title, "url": normalized_url})
            seen_urls.add(normalized_url)

        return entries

    def _extract_pdf_links(self, html: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        links_by_url: Dict[str, Dict[str, str]] = {}

        for anchor in soup.select("a[href]"):
            href = (anchor.get("href") or "").strip()
            normalized_url = _normalize_capes_url(href)
            if not _is_pdf_link(normalized_url):
                continue
            label = anchor.get_text(" ", strip=True) or normalized_url.rsplit("/", 1)[-1]
            links_by_url[normalized_url] = {
                "titulo": label,
                "link": normalized_url,
                "tipo": "anexo",
            }

        for pdf_url in PDF_URL_REGEX.findall(html):
            normalized_url = _normalize_capes_url(pdf_url)
            links_by_url.setdefault(
                normalized_url,
                {
                    "titulo": normalized_url.rsplit("/", 1)[-1],
                    "link": normalized_url,
                    "tipo": "anexo",
                },
            )

        return list(links_by_url.values())

    def _select_main_pdf_url(self, anexos: List[Dict[str, str]]) -> Optional[str]:
        best_url = None
        best_score = -10**9

        for item in anexos:
            url = item["link"]
            title = item["titulo"]
            haystack = f"{title} {url}".lower()
            score = 0

            if "/centrais-de-conteudo/editais/" in url.lower():
                score += 5
            if "edital" in haystack:
                score += 4
            if "chamada" in haystack or "publica" in haystack or "pública" in haystack:
                score += 3
            if any(token in haystack for token in NEGATIVE_PDF_TOKENS):
                score -= 6

            if score > best_score:
                best_score = score
                best_url = url

        return best_url if best_score > 0 else None

    def _download_file_bytes(self, url: str) -> Optional[bytes]:
        try:
            with urlopen(url, timeout=30) as response:
                return response.read()
        except Exception as exc:
            logger.error("Error downloading CAPES file %s: %s", url, exc)
            return None

    def _extract_detail_page(
        self,
        page,
        detail_url: str,
        fallback_title: str,
    ) -> Optional[RawEdital]:
        page.goto(detail_url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle", timeout=20000)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        title_el = soup.find(["h1", "h2"])
        title = title_el.get_text(" ", strip=True) if title_el else fallback_title

        paragraphs = []
        for element in soup.find_all(["p", "div"]):
            text = element.get_text(" ", strip=True)
            if len(text) < 60:
                continue
            if text == title:
                continue
            if "govbr-destaque-titulo" in " ".join(element.get("class", [])):
                continue
            paragraphs.append(text)

        description = paragraphs[0] if paragraphs else ""
        anexos = self._extract_pdf_links(html)
        main_pdf_url = self._select_main_pdf_url(anexos)
        inferred_year = self._infer_year_from_text(
            f"{title} {detail_url} {main_pdf_url or ''} "
            f"{' '.join(item['titulo'] for item in anexos)}"
        )
        if inferred_year is not None and inferred_year < self.current_year:
            return None
        pdf_content = self._download_file_bytes(main_pdf_url) if main_pdf_url else None

        return RawEdital(
            title=title or fallback_title,
            url=detail_url,
            raw_agency="CAPES",
            raw_description=description,
            pdf_content=pdf_content,
            raw_tags=["capes"],
            raw_anexos=anexos,
        )

    def read(self) -> List[RawEdital]:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(self.start_url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_load_state("networkidle", timeout=20000)

                listing_entries = self._extract_listing_entries(page.content())
                raw_editais: List[RawEdital] = []

                for item in listing_entries:
                    try:
                        raw = self._extract_detail_page(page, item["url"], item["title"])
                        if raw:
                            raw_editais.append(raw)
                    except Exception as exc:
                        logger.error("Error extracting CAPES detail %s: %s", item["url"], exc)

                browser.close()
                logger.info("CapesSource extracted %s editais.", len(raw_editais))
                return raw_editais
        except Exception as exc:
            logger.error("Error during CAPES extraction: %s", exc)
            return []
