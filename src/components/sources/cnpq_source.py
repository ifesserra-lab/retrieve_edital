"""
CNPq Chamadas Públicas Source.

O source anterior lia `memoria2.cnpq.br`, portal descontinuado que responde 200
com 137 KB mas contém **um único** card — por isso o fluxo parecia saudável
enquanto coletava quase nada. Ver `docs/spec_finep_cnpq_horizon.md`.

Passa a ler o portal atual, no gov.br:

    https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao

É um Plone estático (sem JS, sem Playwright). A listagem traz um `div.item` por
chamada; a página de detalhe traz o objeto da chamada, o período de inscrições
no formato `INSCRIÇÕES: dd/mm/aaaa a dd/mm/aaaa` e os documentos.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from src.core.interfaces import ISource
from src.domain.models import RawEdital
from src.flow_health import warn_on_redirect

logger = logging.getLogger(__name__)

CNPQ_BASE_URL = "https://www.gov.br"
CNPQ_ABERTAS_URL = "https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao"

# Só links sob este caminho são documentos da chamada. Filtra o boilerplate do
# portal, como a "Carta de Serviços", que aparece em toda página do gov.br.
CHAMADAS_PATH_MARKER = "/chamadas/todas-as-chamadas/"
DOCUMENT_EXTENSIONS = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".odt", ".odp")

# O rótulo do período varia por chamada: "INSCRIÇÕES" nas chamadas comuns,
# "Recebimento das propostas" nos chamamentos públicos.
PERIOD_LABELS = (
    r"INSCRI[ÇC][ÕO]ES",
    r"RECEBIMENTO\s+D[AE]S?\s+PROPOSTAS?",
    r"SUBMISS[ÃA]O\s+D[AE]S?\s+PROPOSTAS?",
    r"PRAZO\s+PARA\s+SUBMISS[ÃA]O",
)
INSCRICOES_REGEX = re.compile(
    rf"(?:{'|'.join(PERIOD_LABELS)})\s*:?\s*"
    r"(\d{2}/\d{2}/\d{4})\s*a\s*(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)
PUBLICADO_REGEX = re.compile(
    r"Publicado\s+em\s+(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)

# Rótulos reconhecidos pelo EditalNormalizer ao derivar as datas.
OPENING_EVENT = "Abertura das inscrições"
DEADLINE_EVENT = "Prazo para envio de propostas"

# Rótulo do documento principal da chamada na página de detalhe.
MAIN_DOCUMENT_LABEL = "chamada"


def _dd_mm_yyyy_to_iso(date_str: str) -> str:
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""


def _year_of(iso_date: str) -> Optional[int]:
    if not iso_date:
        return None
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").year
    except ValueError:
        return None


def _is_document_url(url: str) -> bool:
    return CHAMADAS_PATH_MARKER in url and url.lower().endswith(DOCUMENT_EXTENSIONS)


class CnpqSource(ISource[RawEdital]):
    """
    Extrai as chamadas públicas do CNPq abertas para submissão.

    Para cada chamada, entra na página de detalhe para obter descrição, período
    de inscrições e documentos, e baixa o PDF principal para OCR.
    """

    def __init__(
        self,
        listing_url: str = CNPQ_ABERTAS_URL,
        processed_urls: Optional[Set[str]] = None,
        current_year: Optional[int] = None,
        timeout: int = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.listing_url = listing_url
        self.processed_urls = processed_urls or set()
        self.current_year = (
            current_year if current_year is not None else datetime.now().year
        )
        self.timeout = timeout
        self.session = session or requests.Session()
        # Quantas chamadas a origem devolveu antes da deduplicação. O runner usa
        # esse número para distinguir "nada novo" de "source quebrado".
        self.last_listing_count = 0

    def read(self) -> List[RawEdital]:
        try:
            response = self.session.get(self.listing_url, timeout=self.timeout)
            response.raise_for_status()
            warn_on_redirect(self.listing_url, response.url)
        except requests.RequestException as exc:
            logger.error("Erro ao ler a listagem de chamadas do CNPq: %s", exc)
            self.last_listing_count = 0
            return []

        listing_entries = self._extract_listing_entries(response.text)
        self.last_listing_count = len(listing_entries)
        logger.info("CnpqSource encontrou %s chamadas na listagem.", len(listing_entries))

        raw_editais: List[RawEdital] = []
        for detail_url, listing_title in listing_entries:
            if detail_url in self.processed_urls:
                logger.debug("Chamada já processada; ignorando: %s", detail_url)
                continue
            try:
                raw_edital = self._build_raw_edital(detail_url, listing_title)
            except requests.RequestException as exc:
                logger.error("Erro ao ler a chamada %s: %s", detail_url, exc)
                continue
            if raw_edital is not None:
                raw_editais.append(raw_edital)

        logger.info(
            "CnpqSource selecionou %s chamadas novas de %s na listagem.",
            len(raw_editais),
            len(listing_entries),
        )
        return raw_editais

    def _extract_listing_entries(self, html: str) -> List[Tuple[str, str]]:
        """Devolve (url_detalhe, titulo) por chamada, na ordem da listagem."""
        soup = BeautifulSoup(html, "html.parser")
        entries: List[Tuple[str, str]] = []
        seen: Set[str] = set()

        for anchor in soup.select("div.item h2.headline a[href], h2.headline a.summary[href]"):
            href = (anchor.get("href") or "").strip()
            if not href or CHAMADAS_PATH_MARKER not in href:
                continue
            detail_url = urljoin(CNPQ_BASE_URL, href)
            if detail_url.lower().endswith(DOCUMENT_EXTENSIONS):
                continue
            if detail_url in seen:
                continue
            seen.add(detail_url)
            entries.append((detail_url, anchor.get_text(" ", strip=True)))
        return entries

    def _build_raw_edital(
        self, detail_url: str, listing_title: str
    ) -> Optional[RawEdital]:
        response = self.session.get(detail_url, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = self._extract_title(soup) or listing_title
        if not title:
            logger.debug("Chamada sem título; ignorando: %s", detail_url)
            return None

        page_text = soup.get_text(" ", strip=True)
        data_abertura, data_encerramento = self._extract_inscricao_period(page_text)

        encerramento_year = _year_of(data_encerramento)
        if encerramento_year is not None and encerramento_year < self.current_year:
            logger.debug(
                "Chamada '%s' descartada: encerramento %s anterior a %s.",
                title[:60],
                data_encerramento,
                self.current_year,
            )
            return None

        anexos = self._extract_anexos(soup)
        pdf_content = self._download_main_pdf(anexos)

        return RawEdital(
            title=title,
            # `source_category` fica de fora de propósito: quando definido, o
            # EditalNormalizer o impõe sobre a categoria que o Mistral extraiu do
            # PDF, e o valor viraria um item novo no vocabulário de categorias que
            # o portal consome. Sem ele, a categoria segue vindo do conteúdo do
            # edital, como nas outras fontes.
            url=detail_url,
            raw_agency="CNPq",
            raw_description=self._extract_description(soup),
            pdf_content=pdf_content,
            document_type="edital",
            raw_status="aberto",
            raw_cronograma=self._build_cronograma(
                page_text, data_abertura, data_encerramento
            )
            or None,
            raw_tags=["cnpq", "chamada pública"],
            raw_anexos=anexos or None,
        )

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        for selector in ("h1.documentFirstHeading", "h1", "h2.headline"):
            element = soup.select_one(selector)
            if element:
                title = element.get_text(" ", strip=True)
                if title:
                    return title
        return ""

    @staticmethod
    def _extract_description(soup: BeautifulSoup) -> str:
        content = soup.select_one("#content-core") or soup.select_one(
            "#parent-fieldname-text"
        )
        if content is None:
            return ""
        text = content.get_text(" ", strip=True)
        # O período de inscrições vira cronograma; não precisa poluir a descrição.
        return INSCRICOES_REGEX.sub("", text).strip()

    @staticmethod
    def _extract_inscricao_period(page_text: str) -> Tuple[str, str]:
        match = INSCRICOES_REGEX.search(page_text)
        if match is None:
            return "", ""
        return (
            _dd_mm_yyyy_to_iso(match.group(1)),
            _dd_mm_yyyy_to_iso(match.group(2)),
        )

    @staticmethod
    def _build_cronograma(
        page_text: str, data_abertura: str, data_encerramento: str
    ) -> List[Dict[str, str]]:
        """
        Período de inscrições e, quando disponível, a data de publicação.

        A publicação voltou ao cronograma: o normalizer passou a dar precedência
        a `abertura das inscrições` sobre `publicação` ao derivar `data_abertura`,
        então a data do CMS não sobrepõe mais o início real e pode ser registrada
        como a informação adicional que é.
        """
        cronograma: List[Dict[str, str]] = []
        if data_abertura:
            cronograma.append({"evento": OPENING_EVENT, "data": data_abertura})
        if data_encerramento:
            cronograma.append({"evento": DEADLINE_EVENT, "data": data_encerramento})
        publicacao_match = PUBLICADO_REGEX.search(page_text or "")
        if publicacao_match:
            publicacao = _dd_mm_yyyy_to_iso(publicacao_match.group(1))
            if publicacao:
                cronograma.append({"evento": "Data de publicação", "data": publicacao})
        return cronograma

    @staticmethod
    def _extract_anexos(soup: BeautifulSoup) -> List[Dict[str, str]]:
        anexos: List[Dict[str, str]] = []
        seen: Set[str] = set()
        for anchor in soup.select("a[href]"):
            href = urljoin(CNPQ_BASE_URL, (anchor.get("href") or "").strip())
            if not _is_document_url(href) or href in seen:
                continue
            seen.add(href)
            label = anchor.get_text(" ", strip=True) or "Documento"
            anexos.append(
                {
                    "titulo": label,
                    "link": href,
                    "tipo": href.rsplit(".", 1)[-1].lower(),
                }
            )
        return anexos

    def _download_main_pdf(self, anexos: List[Dict[str, str]]) -> Optional[bytes]:
        main_pdf_url = self._select_main_pdf_url(anexos)
        if not main_pdf_url:
            return None
        try:
            response = self.session.get(main_pdf_url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Erro ao baixar o PDF %s: %s", main_pdf_url, exc)
            return None

        content_type = (response.headers.get("content-type") or "").lower()
        if "application/pdf" not in content_type:
            logger.info(
                "Documento principal do CNPq não é PDF, ignorando para OCR: %s (%s)",
                main_pdf_url,
                content_type or "desconhecido",
            )
            return None
        return response.content

    @staticmethod
    def _select_main_pdf_url(anexos: List[Dict[str, str]]) -> str:
        """
        O documento principal é o rotulado exatamente como "Chamada" na página.
        Sem ele, cai no primeiro PDF disponível.
        """
        pdfs = [a for a in anexos if a["link"].lower().endswith(".pdf")]
        for anexo in pdfs:
            if anexo["titulo"].strip().lower() == MAIN_DOCUMENT_LABEL:
                return anexo["link"]
        return pdfs[0]["link"] if pdfs else ""
