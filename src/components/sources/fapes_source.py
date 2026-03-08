import logging
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
    
    def __init__(self, start_url: str = "https://fapes.es.gov.br/difusao-do-conhecimento"):
        self.start_url = start_url

    def read(self) -> List[RawEdital]:
        raw_editais: List[RawEdital] = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                logger.info(f"Navigating to open editais page at {self.start_url}")
                page.goto(self.start_url, timeout=30000)
                
                while True:
                    # Wait for items to load
                    try:
                        page.wait_for_selector('a', timeout=10000)
                    except TimeoutError:
                        logger.warning("Timeout waiting for anchors to load.")
                        break

                    # Simple heuristic: searching for PDF links
                    elements = page.locator('a[href$=".pdf"]').all()
                    
                    if not elements:
                        logger.warning("No PDF edital links found on the current page.")
                    
                    for el in elements:
                        title = el.inner_text().strip()
                        href = el.get_attribute("href")
                        
                        if not href:
                            continue
                        
                        # Fallback for empty texts but valid links
                        if not title or title.lower() in ["baixar", "clique aqui", "download"]:
                            title = href.split("/")[-1]
                            
                        # Standardize URL
                        if href.startswith("/"):
                            href = f"https://fapes.es.gov.br{href}"
                            
                        # Add to payload
                        raw_editais.append(
                            RawEdital(
                                title=title,
                                url=href,
                                raw_agency="Fapes-ES", # Assumed by context
                                raw_description=None
                            )
                        )
                        
                    # Handle pagination according to BDD spec
                    next_button = page.locator('text="Próxima"', has_text="Página Seguinte")
                    
                    # Alternatively match a simpler generic `>>` or `Próxima`
                    try:
                        next_page_element = page.locator('a:has-text("Próxima Página"), a:has-text("Próxima")').first
                        if next_page_element.evaluate("el => el.offsetParent !== null") and next_page_element.is_enabled():
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
