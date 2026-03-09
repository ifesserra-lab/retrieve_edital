import os
import re
import io
import logging
from typing import List, Dict
import pdfplumber

from src.core.interfaces import ITransform
from src.domain.models import RawEdital, EditalDomain

logger = logging.getLogger(__name__)

class EditalNormalizer(ITransform[RawEdital, EditalDomain]):
    """
    Normalizes the RawEdital data into a validated EditalDomain object.
    Applies regex cleaning on metadata and basic extraction from PDF.
    """
    
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
        
        # Simple extraction from PDF if available (reverting from LLM)
        if raw_data.pdf_content:
            try:
                with pdfplumber.open(io.BytesIO(raw_data.pdf_content)) as pdf:
                    full_text = ""
                    for page in pdf.pages[:5]:
                        extracted = page.extract_text()
                        if extracted:
                            full_text += f"\n{extracted}"
                
                # Basic description extraction: first 200 chars if not present
                if not description and full_text.strip():
                    # Look for "OBJETO" section as a fallback
                    objeto_match = re.search(r'OBJETO\s*\n*(.*?)(?:\n\d+\.|\n[A-Z]{2,}|$)', full_text, re.DOTALL | re.IGNORECASE)
                    if objeto_match:
                        description = objeto_match.group(1).strip()
                    else:
                        description = full_text.strip()[:300] + "..."
            except Exception as e:
                logger.warning(f"Failed to extract basic text from PDF for Edital {clean_title}: {e}")

        # Category extraction by empirical rule on the description/title
        combined_text = (description + " " + clean_title).lower()
        category = "outros"
        tags = []
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
            descrição=description,
            orgão_fomento=clean_agency,
            categoria=category,
            status="aberto",
            data_abertura="", # To be implemented/extracted in future versions
            data_encerramento="", # To be implemented/extracted in future versions
            link=raw_data.url,
            cronograma=cronograma,
            tags=tags
        )
