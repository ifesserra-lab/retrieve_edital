import logging
import re
import requests
from typing import List, Optional
from playwright.sync_api import sync_playwright, TimeoutError
from src.core.interfaces import ISource
from src.domain.models import RawEdital
from src.components.transforms.mistral_client import MistralExtractionService

logger = logging.getLogger(__name__)

# Cada seção do site da FAPES corresponde a uma categoria. O mapeamento é
# explícito de propósito: antes, a categoria saía do slug da URL e só era
# corrigida por uma cadeia de `if`, então uma seção não prevista virava
# categoria. Era o caso de `chamadas-internacionais`, cujo slug vazava como
# `chamadas` — a URL termina em "internacionais", que não contém
# "internacional", então a comparação por substring nunca casava.
#
# Chamadas internacionais são cooperação em pesquisa; `internacional` é âmbito,
# não tema, e vira tag em vez de categoria.
FAPES_URL_CATEGORIES = (
    ("difusao", "divulgação de conhecimento"),
    ("extensao", "extensão"),
    ("inovacao", "inovação"),
    ("pesquisa", "pesquisa"),
    ("internaciona", "pesquisa"),
)
FAPES_FALLBACK_CATEGORY = "outros"


# Palavras que identificam o documento principal do grupo e as que identificam
# documentos de apoio. A eleição do principal precisa ser determinística: ela
# define a identidade do edital e, por consequência, a chave de deduplicação.
MAIN_DOCUMENT_HINTS = ("edital", "chamada", "diretrizes", "regulamento", "chamamento")
SUPPORTING_DOCUMENT_HINTS = (
    "anexo",
    "formulário",
    "formulario",
    "modelo",
    "retificação",
    "retificacao",
    "alteração",
    "alteracao",
    "faq",
    "manual",
    "planilha",
    "declaração",
    "declaracao",
    "resultado",
    "cronograma",
)
GENERIC_LINK_TITLES = ("baixar", "clique aqui", "download", "acesse")


def _tokens(text: str) -> set:
    return {
        token
        for token in re.split(r"[^0-9a-zà-ú]+", (text or "").lower())
        if len(token) > 2
    }


def score_main_document(title: str, url: str, group_title: str) -> tuple:
    """
    Pontua um documento como candidato a principal do grupo.

    Maior é melhor. A ordem dos critérios é o que garante determinismo:

    1. quantos termos o título compartilha com o título do grupo — o cabeçalho do
       bloco nomeia o edital, então quem mais se parece com ele é o principal;
    2. o título menciona edital, chamada, diretrizes, regulamento ou chamamento;
    3. penaliza menção a anexo, formulário, modelo, retificação, FAQ e afins;
    4. penaliza título genérico como "baixar" ou "clique aqui", que não informa.

    Nenhum critério depende de LLM. A classificação do Mistral variava entre
    execuções e, ao decidir quem era o principal, mudava a identidade do edital
    de uma rodada para a outra.
    """
    lowered = f"{title} {url}".lower()
    shared = len(_tokens(title) & _tokens(group_title))
    looks_main = any(hint in lowered for hint in MAIN_DOCUMENT_HINTS)
    looks_supporting = any(hint in lowered for hint in SUPPORTING_DOCUMENT_HINTS)
    is_generic = (title or "").strip().lower() in GENERIC_LINK_TITLES
    return (
        shared,
        1 if looks_main else 0,
        -1 if looks_supporting else 0,
        -1 if is_generic else 0,
    )


def elect_main_document_index(docs: list, group_title: str) -> int:
    """
    Índice do documento principal do grupo, ou -1 quando o grupo está vazio.

    Empate é resolvido pela ordem em que os links aparecem no HTML, o que mantém
    a escolha estável entre execuções.
    """
    if not docs:
        return -1
    melhor = 0
    melhor_score = score_main_document(
        docs[0].get("title", ""), docs[0].get("url", ""), group_title
    )
    for indice in range(1, len(docs)):
        score = score_main_document(
            docs[indice].get("title", ""), docs[indice].get("url", ""), group_title
        )
        if score > melhor_score:
            melhor, melhor_score = indice, score
    return melhor


def category_for_url(url: str) -> str:
    """Categoria da seção da FAPES; nunca devolve pedaço da URL."""
    lowered = (url or "").lower()
    for token, category in FAPES_URL_CATEGORIES:
        if token in lowered:
            return category
    logger.warning(
        "Seção da FAPES sem categoria mapeada: %s. Usando %s.",
        url,
        FAPES_FALLBACK_CATEGORY,
    )
    return FAPES_FALLBACK_CATEGORY

class FapesSource(ISource[RawEdital]):
    """
    Playwright-based Extractor for the FAPES editais.
    Complies with ISource interface returning a List of RawEdition models.
    """
    
    def __init__(self, start_urls: List[str] = None, processed_urls: set = None, classifier: Optional[MistralExtractionService] = None):
        if start_urls is None:
            self.start_urls = [
                "https://fapes.es.gov.br/editais-abertos-pesquisa-4",
                "https://fapes.es.gov.br/editais-abertos-extensao-2",
                "https://fapes.es.gov.br/inovacao",
                "https://fapes.es.gov.br/chamadas-internacionais",
                "https://fapes.es.gov.br/difusao-do-conhecimento"
            ]
        else:
            self.start_urls = start_urls
        self.processed_urls = processed_urls or set()
        # Quantos itens a listagem da origem devolveu, antes da deduplicação e
        # dos filtros. É o que permite ao runner distinguir "portal sem
        # novidade" de "source quebrado". Ver src/flow_health.py.
        self.last_listing_count = 0
        self.classifier = classifier or MistralExtractionService()
        
    def _download_pdf(self, url: str) -> Optional[bytes]:
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.content
        except Exception as e:
            logger.error(f"Error downloading PDF from {url}: {e}")
        return None

    def read(self) -> List[RawEdital]:
        raw_editais: List[RawEdital] = []
        self.last_listing_count = 0
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                for url in self.start_urls:
                    category = category_for_url(url)

                    logger.info(f"Navigating to open editais page at {url} (Category: {category})")
                    try:
                        page.goto(url, timeout=30000)
                    except Exception as e:
                        logger.error(f"Error navigating to {url}: {e}")
                        continue

                    while True:
                        # Wait for items to load
                        try:
                            # The selector might vary, but 'a' is a safe broad bet to check if page loaded
                            page.wait_for_selector('a', timeout=10000)
                        except TimeoutError:
                            logger.warning(f"Timeout waiting for anchors to load on {url}.")
                            break

                        # FAPES organizes editais in accordions or panels. 
                        # Each group is usually within an element that has a title.
                        # Based on browser analysis: Documents are grouped within a specific table relevant to each notice.
                        # The tables are often preceded by a header or within an accordion.
                        
                        # Find notice groups (e.g., accordions or panels)
                        # FAPES often uses elements with specific classes for their notice lists.
                        notice_blocks = page.locator('div.accordion-group, div.panel-group, div.item-edital, div.view-editais tr.edital-row').all()
                        
                        if not notice_blocks:
                            # If no structural blocks, try to find tables and use their preceding headers
                            # Or just treat the whole content as one group if necessary
                            notice_blocks = page.locator('table:has(a[href$=".pdf"])').all()

                        if not notice_blocks:
                            logger.warning(f"No document groups found on {url}.")
                            break

                        for block in notice_blocks:
                            # Try to find a descriptive group title
                            # Look for h1-h4 or specific classes nearby
                            group_title_el = block.locator('h3, h4, .title, strong, td.col-titulo').first
                            group_id = group_title_el.inner_text().strip() if group_title_el.count() > 0 else "Grupo desconhecido"
                            
                            logger.info(f"Processing document group: {group_id}")
                            
                            # Using a more flexible selector to find links that likely contain PDFs
                            links_elements = block.locator('a').all()
                            unique_docs = {} # href -> title
                            
                            found_any_pdf = False
                            for el in links_elements:
                                title = el.inner_text().strip()
                                href = el.get_attribute("href")
                                if not href:
                                    continue
                                
                                # Standardize URL
                                if href.startswith("/"):
                                    href = f"https://fapes.es.gov.br{href}"
                                
                                # Check if it's a document link or looks like one
                                extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".odt"]
                                is_doc_link = any(ext in href.lower() for ext in extensions)
                                
                                if is_doc_link or "baixar" in title.lower():
                                    found_any_pdf = True
                                    # Standardize title: if title is too short or generic, try to get from URL
                                    if not title or title.lower() in ["baixar", "clique aqui", "download", "pdf", "docx"]:
                                        # But only if we don't already have a better title for this href
                                        if href not in unique_docs or unique_docs[href].lower() in ["baixar", "clique aqui"]:
                                            # Try to extract from URL segments
                                            url_title = href.split("/")[-1].replace(".pdf", "").replace(".docx", "").replace("_", " ")
                                            title = url_title
                                    
                                    is_generic = title.lower() in ["baixar", "clique aqui", "download", "pdf"]
                                    if href not in unique_docs:
                                        unique_docs[href] = title
                                    else:
                                        # If existing title is generic or shorter, replace
                                        if (unique_docs[href].lower() in ["baixar", "clique aqui"]) and not is_generic:
                                            unique_docs[href] = title
                                        elif not is_generic and len(title) > len(unique_docs[href]):
                                            unique_docs[href] = title

                            if not unique_docs:
                                if not found_any_pdf:
                                    logger.debug(f"No PDF links found in group {group_id}")
                                continue

                            logger.info(f"Foud {len(unique_docs)} unique document links in group {group_id}")
                            temp_docs = [{"title": t, "url": h} for h, t in unique_docs.items()]

                            # Classify titles in bulk using Mistral
                            titles_to_classify = [d["title"] for d in temp_docs if d["title"].lower() not in ["baixar", "clique aqui"]]
                            classifications = {}
                            if titles_to_classify:
                                classifications = self.classifier.classify_document_titles(titles_to_classify)
                            
                            # O principal é eleito por evidência da página, antes
                            # e independentemente do Mistral: era a classificação
                            # do LLM que decidia quem era `edital`, e como ela
                            # varia entre execuções, a identidade do edital — e
                            # com ela a chave de deduplicação — mudava de rodada
                            # para rodada.
                            main_index = elect_main_document_index(temp_docs, group_id)

                            # Map back to RawEdital objects
                            group_raw_editais = []
                            for indice, doc in enumerate(temp_docs):
                                href = doc["url"]
                                title = doc["title"]
                                if indice == main_index:
                                    # O principal é sempre `edital`: é ele que
                                    # recebe OCR e passa pelas regras de
                                    # publicação, que descartam anexo e alteração.
                                    doc_type = "edital"
                                else:
                                    # O Mistral agora só rotula os documentos de
                                    # apoio, o que é informação de exibição e não
                                    # de identidade.
                                    doc_type = classifications.get(title, "anexo")

                                # Deduplica pela URL do documento, não pelo
                                # título. O título da página passava por
                                # `key_from_nome`, mas o registry guardava o
                                # basename derivado do nome que o Mistral
                                # reescreve — as duas chaves não fechavam, e a
                                # FAPES reprocessava os mesmos editais em toda
                                # execução, gastando OCR e batendo em rate limit.
                                if doc["url"] in self.processed_urls:
                                    continue
                                
                                # Download content only for edital and alteração
                                # But wait, if it's nested, maybe we only want to download the main one?
                                # For now, let's keep the logic: only download if type is edital or alteração
                                pdf_bytes = None
                                if doc_type in ["edital", "alteração"] and ".pdf" in doc["url"].lower():
                                    pdf_bytes = self._download_pdf(doc["url"])
                                
                                raw = RawEdital(
                                    title=doc["title"],
                                    url=doc["url"],
                                    source_category=category,
                                    raw_agency="FAPES",
                                    pdf_content=pdf_bytes,
                                    document_type=doc_type,
                                    group_id=group_id,
                                    is_main=False # Default to false, will set one to true
                                )
                                group_raw_editais.append(raw)

                            if not group_raw_editais:
                                continue

                            # Conta grupos com documento, não blocos do HTML: os
                            # seletores de bloco variam com a seção e chegavam a
                            # zerar em páginas que ainda produziam editais. Um
                            # contador que reporta zero com itens presentes faria
                            # o canário do runner acusar a origem de quebrada.
                            self.last_listing_count += 1

                            # O principal é o que foi eleito acima. Se ele caiu
                            # na deduplicação, o grupo inteiro já é conhecido.
                            main_candidates = [
                                r for r in group_raw_editais if r.document_type == "edital"
                            ]
                            if not main_candidates:
                                logger.debug(
                                    "Grupo %s sem documento principal novo; ignorando.",
                                    group_id,
                                )
                                continue
                            main_edital = main_candidates[0]
                            main_edital.is_main = True
                            
                            # All other documents in the group are attachments
                            main_edital.attachments = [r for r in group_raw_editais if r != main_edital]
                            
                            raw_editais.append(main_edital)
                                
                        # Handle pagination
                        try:
                            next_page_element = page.locator('a:has-text("Próxima Página"), a:has-text("Próxima")').first
                            if next_page_element.count() > 0 and next_page_element.evaluate("el => el.offsetParent !== null") and next_page_element.is_enabled():
                                next_page_element.click()
                                page.wait_for_load_state('networkidle')
                            else:
                                break
                        except Exception:
                            break
                browser.close()
        except Exception as e:
            logger.error(f"Error during playwright extraction: {e}")
            # Do not crash the pipeline per BDD "it should log the detailed error without crashing the pipeline"
            pass
            
        return raw_editais
