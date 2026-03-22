import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from src.core.interfaces import ISource
from src.domain.models import RawEdital

logger = logging.getLogger(__name__)

CNPQ_BASE_URL = "http://memoria2.cnpq.br"
CNPQ_CHAMADAS_ABERTAS_URL = (
    f"{CNPQ_BASE_URL}/web/guest/chamadas-publicas"
    "?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/"
)
DATE_RANGE_REGEX = re.compile(
    r"(\d{2}/\d{2}/\d{4})\s*a\s*(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)


def _normalize_cnpq_url(href: str) -> str:
    if not href:
        return CNPQ_CHAMADAS_ABERTAS_URL
    if href.startswith("http"):
        return href
    return urljoin(CNPQ_BASE_URL, href)


def _dd_mm_yyyy_to_iso(date_str: str) -> str:
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def _parse_inscricao_range(text: str) -> Tuple[str, str]:
    match = DATE_RANGE_REGEX.search(text or "")
    if not match:
        return "", ""
    start, end = match.groups()
    return _dd_mm_yyyy_to_iso(start), _dd_mm_yyyy_to_iso(end)


class CnpqSource(ISource[RawEdital]):
    """
    Extractor for CNPq chamadas públicas abertas.
    Parses the legacy portal cards directly from the "abertas" page and
    downloads the first available PDF attachment for OCR when present.
    """

    def __init__(
        self,
        start_url: str = CNPQ_CHAMADAS_ABERTAS_URL,
        processed_urls: Optional[Set[str]] = None,
        timeout: int = 30,
    ) -> None:
        self.start_url = start_url
        self.processed_urls = processed_urls or set()
        self.timeout = timeout

    def _download_file_bytes(self, url: str) -> Optional[bytes]:
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            content_type = (response.headers.get("content-type") or "").lower()
            if "application/pdf" not in content_type:
                logger.info(
                    "Skipping non-PDF CNPq attachment for OCR: %s (%s)",
                    url,
                    content_type or "unknown",
                )
                return None
            return response.content
        except Exception as exc:
            logger.error("Error downloading CNPq file %s: %s", url, exc)
            return None

    def _extract_permalink(self, card_container: Tag) -> str:
        input_el = card_container.find("input", attrs={"value": re.compile(r"idDivulgacao=\d+")})
        if input_el and input_el.get("value"):
            return _normalize_cnpq_url(input_el["value"].strip())

        for anchor in card_container.select("a[href]"):
            href = (anchor.get("href") or "").strip()
            if "idDivulgacao=" in href:
                return _normalize_cnpq_url(href)
        return ""

    def _extract_anexos(self, content_block: Tag) -> List[Dict[str, str]]:
        anexos: List[Dict[str, str]] = []
        for item in content_block.select("ul > li"):
            anchor = item.find("a", href=True)
            if anchor is None:
                continue
            href = _normalize_cnpq_url(anchor["href"].strip())
            label = item.get_text(" ", strip=True).replace(" link", "").strip(" :")
            anexos.append(
                {
                    "titulo": label or "Documento",
                    "link": href,
                    "tipo": "anexo",
                }
            )
        return anexos

    def _extract_raw_edital_from_card(self, card_container: Tag) -> Optional[RawEdital]:
        content_block = card_container.select_one("div.content")
        if content_block is None:
            return None

        title_el = content_block.find("h4")
        description_el = content_block.find("p")
        if title_el is None:
            return None

        title = title_el.get_text(" ", strip=True)
        description = description_el.get_text(" ", strip=True) if description_el else ""
        permalink = self._extract_permalink(card_container)
        anexos = self._extract_anexos(content_block)

        if not permalink:
            permalink = anexos[0]["link"] if anexos else title
        if permalink in self.processed_urls:
            return None

        inscricao_text = ""
        inscricao_item = content_block.select_one("div.inscricao li")
        if inscricao_item:
            inscricao_text = inscricao_item.get_text(" ", strip=True)

        data_abertura, data_encerramento = _parse_inscricao_range(inscricao_text)
        cronograma = []
        if data_abertura:
            cronograma.append({"evento": "abertura das inscrições", "data": data_abertura})
        if data_encerramento:
            cronograma.append({"evento": "encerramento das inscrições", "data": data_encerramento})

        pdf_content = None
        for anexo in anexos:
            pdf_content = self._download_file_bytes(anexo["link"])
            if pdf_content:
                break

        return RawEdital(
            title=title,
            url=permalink,
            raw_agency="CNPq",
            raw_description=description,
            pdf_content=pdf_content,
            raw_cronograma=cronograma,
            raw_tags=["cnpq"],
            raw_anexos=anexos,
        )

    def _extract_listing_entries(self, html: str) -> List[RawEdital]:
        soup = BeautifulSoup(html, "html.parser")
        raw_editais: List[RawEdital] = []

        for card_container in soup.select("li:has(div.content)"):
            raw = self._extract_raw_edital_from_card(card_container)
            if raw:
                raw_editais.append(raw)

        return raw_editais

    def read(self) -> List[RawEdital]:
        try:
            response = requests.get(self.start_url, timeout=self.timeout)
            response.raise_for_status()
            raw_editais = self._extract_listing_entries(response.text)
            logger.info("CnpqSource extracted %s chamadas.", len(raw_editais))
            return raw_editais
        except Exception as exc:
            logger.error("Error during CNPq extraction: %s", exc)
            return []
