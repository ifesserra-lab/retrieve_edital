import logging
import requests
from typing import List
from playwright.sync_api import sync_playwright, TimeoutError
from src.core.interfaces import ISource
from src.domain.models import RawEdital

logger = logging.getLogger(__name__)

class FapesSource(ISource[RawEdital]):
    """
    Playwright-based Extractor for the FAPES editais.
    Complies with ISource interface returning a List of RawEdition models.
    """
    
    def __init__(self, start_urls: List[str] = None, processed_titles: set = None):
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
        
    def _sanitize(self, filename: str) -> str:
        keepcharacters = (' ', '.', '_', '-')
        sanitized = "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()
        return sanitized.replace(' ', '_').lower()

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

                        # Simple heuristic: searching for PDF links
                        elements = page.locator('a[href$=".pdf"]').all()
                        
                        if not elements:
                            logger.warning(f"No PDF edital links found on the current page: {url}")
                        
                        unique_links = {}
                        for el in elements:
                            title = el.inner_text().strip()
                            href = el.get_attribute("href")
                            
                            if not href:
                                continue
                            
                            # Standardize URL
                            if href.startswith("/"):
                                href = f"https://fapes.es.gov.br{href}"
                                
                            # Fallback for empty texts but valid links
                            if not title or title.lower() in ["baixar", "clique aqui", "download"]:
                                title = href.split("/")[-1]
                                
                            if href in unique_links:
                                existing_title = unique_links[href]
                                # Prefer a more descriptive title (not just the .pdf filename)
                                if title and existing_title.lower().endswith('.pdf') and not title.lower().endswith('.pdf'):
                                    unique_links[href] = title
                                elif len(title) > len(existing_title) and not title.lower().endswith('.pdf'):
                                    unique_links[href] = title
                            else:
                                unique_links[href] = title
                                
                        for href, title in unique_links.items():
                            # Incremental Sieve
                            safe_title = self._sanitize(title)
                            if safe_title in self.processed_titles:
                                logger.info(f"Incremental Filter: Skipping already processed edital '{title}'")
                                continue

                            # Download PDF binary
                            pdf_bytes = None
                            try:
                                resp = requests.get(href, timeout=30)
                                if resp.status_code == 200:
                                    pdf_bytes = resp.content
                                else:
                                    logger.warning(f"Failed to download PDF {href} (status: {resp.status_code})")
                            except Exception as dl_error:
                                logger.error(f"Error downloading PDF {href}: {dl_error}")
                                
                            # Add to payload
                            raw_editais.append(
                                RawEdital(
                                    title=title,
                                    url=href,
                                    source_category=category,
                                    raw_agency="Fapes-ES",
                                    raw_description=None,
                                    pdf_content=pdf_bytes
                                )
                            )
                            
                        # Handle pagination according to BDD spec
                        try:
                            next_page_element = page.locator('a:has-text("Próxima Página"), a:has-text("Próxima")').first
                            if next_page_element.count() > 0 and next_page_element.evaluate("el => el.offsetParent !== null") and next_page_element.is_enabled():
                                logger.info("Moving to next page...")
                                next_page_element.click()
                                page.wait_for_load_state('networkidle')
                            else:
                                # Reached end of pagination
                                break
                        except Exception:
                            break # No next page found
                browser.close()
        except Exception as e:
            logger.error(f"Error during playwright extraction: {e}")
            # Do not crash the pipeline per BDD "it should log the detailed error without crashing the pipeline"
            pass
            
        return raw_editais
