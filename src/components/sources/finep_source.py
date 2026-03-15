"""
FINEP Chamadas Públicas Source.

Extracts open chamadas from the list page, then visits each detail page
(e.g. http://www.finep.gov.br/chamadas-publicas/chamadapublica/777) to extract:
- Description: initial text block ("Esta Seleção Pública tem por objetivo...")
- Cronograma: Data de Publicação and Prazo para envio de propostas até
- Tags: from Tema(s)
- Anexos: links from the Documentos table

Filters by deadline: only chamadas whose "Prazo para envio de propostas"
falls in the reference year or the next year.
"""

import logging
import re
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from src.config import get_reference_year
from src.core.interfaces import ISource
from src.domain.models import RawEdital

logger = logging.getLogger(__name__)

FINEP_BASE_URL = "http://www.finep.gov.br"
FINEP_CHAMADAS_ABERTAS_URL = (
    f"{FINEP_BASE_URL}/chamadas-publicas/chamadaspublicas?situacao=aberta"
)

# "Prazo para envio de propostas até: 04/05/2026"
PRAZO_REGEX = re.compile(
    r"Prazo\s+para\s+envio\s+de\s+propostas\s+até\s*:\s*(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)

# Detail page: "Data de Publicação:\s*13/02/2026" and "Prazo para envio de propostas até:\s*31/08/2026"
DATA_PUBLICACAO_REGEX = re.compile(
    r"Data\s+de\s+[Pp]ublica[cç][aã]o\s*:\s*(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)
PRAZO_DETAIL_REGEX = re.compile(
    r"Prazo\s+para\s+envio\s+de\s+propostas\s+até\s*:\s*(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)

# "Tema(s):" seguido da lista de temas separados por ; (parar em Situacão ou Documentos)
# Procurar apenas após "Prazo para envio" ou "Data de Publicação" para evitar o menu lateral (Tema 5G...)
TEMAS_REGEX = re.compile(
    r"Tema\s*\(s\)\s*:\s*(.+?)(?=\s*Situacão|\s*Documentos|\n\s*\n[A-Z]|$)",
    re.IGNORECASE | re.DOTALL,
)


def _parse_deadline_year(text: str) -> Optional[int]:
    """Extract deadline date from block text and return its year, or None."""
    match = PRAZO_REGEX.search(text)
    if not match:
        return None
    date_str = match.group(1)
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        return dt.year
    except ValueError:
        return None


def _dd_mm_yyyy_to_iso(date_str: str) -> str:
    """Convert DD/MM/YYYY to YYYY-MM-DD."""
    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def _deadline_in_range(year: Optional[int], ref_year: int) -> bool:
    """True if deadline year is ref_year or ref_year + 1."""
    if year is None:
        return False
    return year in (ref_year, ref_year + 1)


def _normalize_finep_url(href: str) -> str:
    if not href:
        return FINEP_CHAMADAS_ABERTAS_URL
    if href.startswith("http"):
        return href
    return urljoin(FINEP_BASE_URL, href.lstrip("/"))


class FinepSource(ISource[RawEdital]):
    """
    Playwright-based extractor for FINEP chamadas públicas.
    Visits each chamada detail page to extract description, cronograma, tags and anexos.
    """

    def __init__(
        self,
        start_url: str = FINEP_CHAMADAS_ABERTAS_URL,
        reference_year: Optional[int] = None,
        max_pages: Optional[int] = None,
    ):
        self.start_url = start_url
        self.reference_year = (
            reference_year if reference_year is not None else get_reference_year()
        )
        self.max_pages = max_pages  # None = all pages; 1 = only first page (e.g. for quick test)
        logger.info(
            "FinepSource using reference_year=%s (deadline filter: %s or %s)%s",
            self.reference_year,
            self.reference_year,
            self.reference_year + 1,
            f", max_pages={max_pages}" if max_pages else "",
        )

    def read(self) -> List[RawEdital]:
        detail_links: List[Tuple[str, str]] = []  # (detail_url, title)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page_num = 1
                while True:
                    url = (
                        self.start_url
                        if page_num == 1
                        else f"{self.start_url}&limitstart={(page_num - 1) * 10}"
                    )
                    logger.info(
                        "Navigating to FINEP chamadas abertas (page %s): %s",
                        page_num,
                        url,
                    )
                    try:
                        page.goto(url, timeout=60000, wait_until="domcontentloaded")
                        page.wait_for_load_state("networkidle", timeout=20000)
                    except Exception as e:
                        logger.error("Error navigating to FINEP: %s", e)
                        break

                    try:
                        page.wait_for_selector(
                            "a[href*='chamadapublica/'], h3",
                            timeout=15000,
                        )
                    except PlaywrightTimeout:
                        logger.warning("Timeout waiting for results on page %s.", page_num)
                        break

                    # Collect links to detail pages (chamadapublica/ID)
                    link_els = page.locator("a[href*='chamadapublica/']").all()
                    seen_urls = set()
                    for link_el in link_els:
                        href = link_el.get_attribute("href")
                        if not href or "chamadapublica/" not in href:
                            continue
                        detail_url = _normalize_finep_url(href)
                        if detail_url in seen_urls:
                            continue
                        seen_urls.add(detail_url)
                        title = link_el.inner_text().strip() or "Chamada FINEP"
                        if not title or len(title) < 5:
                            continue
                        block = link_el.locator("xpath=..")
                        block_text = ""
                        for _ in range(3):
                            try:
                                block_text = block.inner_text()
                                if "Prazo" in block_text or "Data de" in block_text:
                                    break
                            except Exception:
                                pass
                            block = block.locator("xpath=..")
                        deadline_year = _parse_deadline_year(block_text)
                        if not _deadline_in_range(
                            deadline_year, self.reference_year
                        ):
                            logger.debug(
                                "Skipping '%s' (deadline year %s not in %s/%s).",
                                title[:50],
                                deadline_year,
                                self.reference_year,
                                self.reference_year + 1,
                            )
                            continue
                        detail_links.append((detail_url, title))

                    next_links = page.locator(
                        "a:has-text('Próx'), a:has-text('Próxima'), a:has-text('next'), .pagination a.next"
                    ).all()
                    has_next = False
                    for link in next_links:
                        if link.is_visible() and link.get_attribute("href"):
                            try:
                                link.click()
                                page.wait_for_load_state("networkidle")
                                page_num += 1
                                has_next = True
                                break
                            except Exception:
                                pass
                    if not has_next:
                        break
                    if self.max_pages is not None and page_num >= self.max_pages:
                        break

                raw_editais: List[RawEdital] = []
                for detail_url, list_title in detail_links:
                    try:
                        raw = self._extract_detail_page(
                            browser, detail_url, list_title
                        )
                        if raw:
                            raw_editais.append(raw)
                    except Exception as e:
                        logger.error(
                            "Error extracting detail page %s: %s", detail_url, e
                        )

                browser.close()
                logger.info(
                    "FinepSource extracted %s chamadas (deadline in %s or %s).",
                    len(raw_editais),
                    self.reference_year,
                    self.reference_year + 1,
                )
                return raw_editais

        except Exception as e:
            logger.error("Error during FINEP extraction: %s", e)
            return []

    def _extract_documentos_table(self, page, content) -> List[dict]:
        """Extrai anexos da tabela 'Documentos' (Nome do documento + link)."""
        anexos: List[dict] = []
        # Padrão de data na 1ª coluna para pular cabeçalho
        date_cell_re = re.compile(r"^\d{2}/\d{2}/\d{4}$")
        for container in [content, page]:
            tables = container.locator("table").all()
            for table in tables:
                try:
                    full_header = table.locator("thead, tr").first.inner_text()
                except Exception:
                    full_header = ""
                if "nome do documento" not in full_header.lower() and "documento" not in full_header.lower():
                    continue
                rows = table.locator("tbody tr, tr").all()
                for row in rows:
                    cells = row.locator("td").all()
                    if len(cells) < 2:
                        continue
                    try:
                        cell0_text = cells[0].inner_text().strip()
                        doc_name = cells[1].inner_text().strip()
                    except Exception:
                        continue
                    if not doc_name or len(doc_name) < 2:
                        continue
                    if date_cell_re.match(cell0_text) is None and date_cell_re.match(doc_name):
                        continue
                    links = row.locator("a[href]").all()
                    doc_url = ""
                    for link in links:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        h = href.lower()
                        is_doc = (
                            ".pdf" in h or ".odt" in h or ".doc" in h or ".pptx" in h or ".odp" in h
                            or "/images/" in href or "chamadas-publicas" in h
                        )
                        if is_doc:
                            doc_url = _normalize_finep_url(href)
                            break
                    if not doc_url and links:
                        doc_url = _normalize_finep_url(links[0].get_attribute("href") or "")
                    if doc_url:
                        anexos.append({
                            "titulo": doc_name,
                            "link": doc_url,
                            "tipo": "Documentos",
                        })
                if anexos:
                    return anexos
        return anexos

    def _extract_detail_page(
        self, browser, detail_url: str, list_title: str
    ) -> Optional[RawEdital]:
        page = browser.new_page()
        try:
            page.goto(detail_url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=20000)

            # Conteúdo principal: bloco que contém "Data de Publicação" (área do edital, não menu/lateral)
            content = page.locator(
                "div.item-page, main, article, [id='content'], .content"
            ).filter(has_text="Data de Publicação").first
            try:
                content.wait_for(state="visible", timeout=10000)
            except Exception:
                content = page.locator("body")

            full_text = ""
            try:
                full_text = content.inner_text()
            except Exception:
                full_text = page.inner_text("body")

            # Se pegou o body e não tem a descrição, tentar div que contém "Esta Seleção Pública"
            if not full_text.strip().startswith(("Esta Seleção", "Esta seleção")) and "Esta Seleção Pública" not in full_text:
                try:
                    alt = page.locator("div").filter(has_text="Esta Seleção Pública").first
                    if alt.count() > 0:
                        full_text = alt.inner_text()
                        content = alt
                except Exception:
                    pass

            # Título: primeiro h2 que não é "Chamadas Públicas"
            title = list_title
            for h2 in content.locator("h2").all():
                t = h2.inner_text().strip()
                if t and "Chamadas Públicas" not in t and len(t) > 15:
                    title = t
                    break

            # Descrição: bloco que começa com "Esta Seleção Pública" até Orçamento/Disponibilização/Data de Publicação
            description = ""
            for start_phrase in ("Esta Seleção Pública", "Esta seleção pública"):
                if start_phrase in full_text:
                    start = full_text.find(start_phrase)
                    end = len(full_text)
                    for stop in (
                        "Orçamento:",
                        "**Orçamento**",
                        "Disponibilização do sistema",
                        "Data de Publicação:",
                        "Data de publicação:",
                    ):
                        idx = full_text.find(stop, start)
                        if idx != -1 and idx < end:
                            end = idx
                    description = full_text[start:end].strip()
                    description = re.sub(r"\s+", " ", description)
                    break

            # Cronograma: Data de Publicação → data_abertura; Prazo para envio → data_encerramento
            cronograma: List[dict] = []
            m1 = DATA_PUBLICACAO_REGEX.search(full_text)
            if m1:
                cronograma.append({
                    "evento": "Data de publicação",
                    "data": _dd_mm_yyyy_to_iso(m1.group(1)),
                })
            m2 = PRAZO_DETAIL_REGEX.search(full_text)
            if m2:
                cronograma.append({
                    "evento": "Prazo de envio da proposta",
                    "data": _dd_mm_yyyy_to_iso(m2.group(1)),
                })

            # Tags: do campo Tema(s): (separado por ;) — só no bloco de metadados (após Prazo/Data de Publicação)
            tags: List[str] = []
            meta_start = full_text.find("Prazo para envio")
            if meta_start == -1:
                meta_start = full_text.find("Data de Publicação")
            search_text = full_text[meta_start:] if meta_start >= 0 else full_text
            tm = TEMAS_REGEX.search(search_text)
            if tm:
                tema_str = tm.group(1).strip()
                for part in re.split(r"\s*;\s*", tema_str):
                    t = part.strip()
                    if t and len(t) > 1:
                        tags.append(t)

            # Anexos: tabela "Documentos" — coluna "Nome do documento" + links (Formatos proprietários/abertos)
            # Estrutura: Data de publicação | Nome do documento | Formatos proprietários | Formatos abertos
            anexos = self._extract_documentos_table(page, content)

            return RawEdital(
                title=title,
                url=detail_url,
                source_category="chamada pública",
                raw_agency="FINEP",
                raw_description=description or full_text[:2000],
                document_type="edital",
                group_id=None,
                is_main=True,
                attachments=None,
                raw_cronograma=cronograma if cronograma else None,
                raw_tags=tags if tags else None,
                raw_anexos=anexos if anexos else None,
            )
        finally:
            page.close()
