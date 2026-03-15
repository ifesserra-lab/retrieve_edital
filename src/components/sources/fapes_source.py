import logging
import requests
from typing import List, Optional
from playwright.sync_api import sync_playwright, TimeoutError
from src.core.interfaces import ISource
from src.domain.models import RawEdital
from src.components.transforms.mistral_client import MistralExtractionService
from src.components.sinks.json_sink import key_from_nome

logger = logging.getLogger(__name__)

class FapesSource(ISource[RawEdital]):
    """
    Playwright-based Extractor for the FAPES editais.
    Complies with ISource interface returning a List of RawEdition models.
    """
    
    def __init__(self, start_urls: List[str] = None, processed_titles: set = None, classifier: Optional[MistralExtractionService] = None):
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
        self.processed_titles = processed_titles or set()
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
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                for url in self.start_urls:
                    # Determine category based on URL suffix
                    # Example: https://fapes.es.gov.br/inovacao -> inovacao
                    # https://fapes.es.gov.br/editais-abertos-pesquisa-4 -> pesquisa
                    category = url.split("/")[-1].replace("editais-abertos-", "").split("-")[0]
                    if "difusao" in url:
                        category = "divulgação de conhecimento"
                    elif "extensao" in url:
                        category = "extensão"
                    elif "pesquisa" in url:
                        category = "pesquisa"
                    elif "inovacao" in url:
                        category = "inovação"
                    elif "internacional" in url:
                        category = "internacional"

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
                            
                            # Map back to RawEdital objects
                            group_raw_editais = []
                            for doc in temp_docs:
                                href = doc["url"]
                                title = doc["title"]
                                doc_type = classifications.get(title, "edital")
                                
                                # Heuristic if Mistral didn't see it (e.g., if we skipped it)
                                if title.lower() in ["baixar", "clique aqui"]:
                                    # If it's a generic link with same href as something else, we already deduplicated.
                                    # If it's unique but generic, it's likely the edital itself.
                                    doc_type = "edital"

                                safe_title = key_from_nome(title)
                                if safe_title in self.processed_titles:
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

                            # Identify the main edital in the group
                            # Strategy: First one classified as 'edital', or first one overall
                            main_candidates = [r for r in group_raw_editais if r.document_type == "edital"]
                            if main_candidates:
                                main_edital = main_candidates[0]
                            else:
                                main_edital = group_raw_editais[0]
                            
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
