import os
import re
import io
import logging
from typing import List, Dict, Optional
import pdfplumber

from src.core.interfaces import ITransform
from src.domain.models import RawEdital, EditalDomain
from src.components.transforms.mistral_client import MistralExtractionService

logger = logging.getLogger(__name__)

class EditalNormalizer(ITransform[RawEdital, EditalDomain]):
    """
    Normalizes the RawEdital data into a validated EditalDomain object.
    Applies regex cleaning on metadata and uses Mistral for high-accuracy extraction.
    """
    
    def __init__(self, extraction_service: Optional[MistralExtractionService] = None):
        self.extraction_service = extraction_service or MistralExtractionService()
    
    def process(self, raw_data: RawEdital) -> EditalDomain:
        # Mandatory validation
        if not raw_data.title or raw_data.title.strip() == "":
            raise ValueError("O título do edital não pode ser nulo ou vazio.")

        # Title normalization: remove extra spaces and newlines
        clean_title = re.sub(r'\s+', ' ', raw_data.title).strip().upper()

        # Agency standardization
        raw_orgao = (raw_data.raw_agency or "FAPES").upper()
        if "FAPES" in raw_orgao:
            clean_agency = "FAPES"
        else:
            clean_agency = raw_orgao

        # Base properties
        description = raw_data.raw_description or ""
        cronograma: List[Dict[str, str]] = []
        
        # Mistral extraction from PDF if available
        if raw_data.pdf_content:
            try:
                # Use Mistral for high-quality extraction
                mistral_domain = self.extraction_service.extract_from_pdf(
                    raw_data.pdf_content, 
                    f"{clean_title}.pdf"
                )
                
                if mistral_domain:
                    # Enrich/Merge Mistral result with metadata
                    mistral_domain.link = raw_data.url
                    # Force the category from the source website as requested
                    if raw_data.source_category:
                        mistral_domain.categoria = raw_data.source_category
                    return mistral_domain
                else:
                    logger.warning(f"Mistral returned no domain for {clean_title}, falling back to basic extraction.")
            except Exception as e:
                logger.error(f"Error during Mistral extraction for {clean_title}: {e}")

        # Basic/Fallback extraction (retained for resilience or if no PDF)
        # Category extraction by empirical rule on the description/title
        combined_text = (description + " " + clean_title).lower()
        category = raw_data.source_category or "outros"
        tags = ["fapes", "edital"]
        if "extensão" in combined_text:
            category = "extensão"
            tags.append("extensão")
        elif "pesquisa" in combined_text:
            category = "pesquisa"
            tags.append("pesquisa")
        elif "inovação" in combined_text:
            category = "inovação"
            tags.append("inovação")
            
        if "bolsa" in combined_text:
            tags.append("bolsa")

        return EditalDomain(
            nome=clean_title,
            descrição=description or f"Edital de fomento FAPES: {clean_title}",
            orgão_fomento=clean_agency,
            categoria=raw_data.source_category or category,
            status="aberto",
            data_abertura="2026-01-01",
            data_encerramento="",
            link=raw_data.url,
            cronograma=cronograma,
            tags=tags
        )
