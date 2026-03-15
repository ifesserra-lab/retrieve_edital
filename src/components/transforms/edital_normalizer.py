import os
import re
import io
import logging
from typing import List, Dict, Optional
import pdfplumber

from src.core.interfaces import ITransform
from src.domain.models import RawEdital, EditalDomain
from src.components.transforms.mistral_client import MistralExtractionService
from src.components.transforms.date_utils import normalize_schedule_dates

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

        description = raw_data.raw_description or ""
        cronograma: List[Dict[str, str]] = []
        anexos: List[Dict[str, str]] = []
        tags: List[str] = []

        # Use structured data from detail page (e.g. FINEP chamadapublica) when present
        if getattr(raw_data, "raw_cronograma", None):
            cronograma = list(raw_data.raw_cronograma)
        if getattr(raw_data, "raw_anexos", None):
            anexos = list(raw_data.raw_anexos)
        if getattr(raw_data, "raw_tags", None):
            tags = list(raw_data.raw_tags)

        # Collect nested attachments (merge with raw_anexos if any)
        if raw_data.attachments:
            for att in raw_data.attachments:
                anexos.append({
                    "titulo": att.title,
                    "link": att.url,
                    "tipo": att.document_type
                })
        
        # Mistral extraction from PDF if available
        # Only extract full content for 'edital' or 'alteração' types, and if pdf_content is present
        if raw_data.pdf_content and raw_data.document_type in ["edital", "alteração"]:
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
                    
                    # Add tags based on document type
                    if raw_data.document_type == "alteração":
                        mistral_domain.tags.append("alteração")
                        mistral_domain.nome = f"[ALTERAÇÃO] {mistral_domain.nome}"
                    
                    mistral_domain.anexos = anexos
                    
                    # Normalize dates
                    mistral_domain.cronograma = normalize_schedule_dates(mistral_domain.cronograma)
                    
                    return mistral_domain
                else:
                    logger.warning(f"Mistral returned no domain for {clean_title}, falling back to basic extraction.")
            except Exception as e:
                logger.error(f"Error during Mistral extraction for {clean_title}: {e}")

        # Basic/Fallback extraction (for anexos or if Mistral fails)
        combined_text = (description + " " + clean_title).lower()
        category = raw_data.source_category or "outros"
        if "FINEP" in (raw_data.raw_agency or "").upper() and description:
            try:
                category = self.extraction_service.categorize_finep_by_description(description)
                logger.info("FINEP edital categorizado por Mistral: %s", category)
            except Exception as e:
                logger.warning("Mistral categorização FINEP falhou, usando fallback: %s", e)
        if not tags:
            tags = ["fapes", "documento"]
            if "FINEP" in (raw_data.raw_agency or "").upper():
                tags = ["finep", "chamada pública"]
        
        if raw_data.document_type == "anexo":
            if "anexo" not in tags:
                tags.append("anexo")
            clean_title = f"[ANEXO] {clean_title}"
        elif raw_data.document_type == "alteração":
            if "alteração" not in tags:
                tags.append("alteração")
            clean_title = f"[ALTERAÇÃO] {clean_title}"
            
        if "FINEP" not in (raw_data.raw_agency or "").upper():
            if "extensão" in combined_text:
                category = "extensão"
                if "extensão" not in tags:
                    tags.append("extensão")
            elif "pesquisa" in combined_text:
                category = "pesquisa"
                if "pesquisa" not in tags:
                    tags.append("pesquisa")
            elif "inovação" in combined_text:
                category = "inovação"
                if "inovação" not in tags:
                    tags.append("inovação")
        else:
            if category not in tags:
                tags.append(category)

        if "bolsa" in combined_text and "bolsa" not in tags:
            tags.append("bolsa")

        # Map cronograma to data_abertura / data_encerramento explicitly:
        # - Data de publicação → data_abertura
        # - Prazo de envio da proposta / Prazo para envio de propostas → data_encerramento
        data_abertura = "2026-01-01"
        data_encerramento = ""
        if cronograma:
            for item in cronograma:
                ev = (item.get("evento") or "").lower()
                d = item.get("data") or ""
                if not d or not re.match(r"\d{4}-\d{2}-\d{2}", str(d)):
                    continue
                if "publicação" in ev or "publicacao" in ev:
                    data_abertura = d
                    break
            for item in cronograma:
                ev = (item.get("evento") or "").lower()
                d = item.get("data") or ""
                if not d or not re.match(r"\d{4}-\d{2}-\d{2}", str(d)):
                    continue
                if ("prazo" in ev and "envio" in ev) or "prazo de envio da proposta" in ev:
                    data_encerramento = d
                    break

        return EditalDomain(
            nome=clean_title,
            descrição=description or f"Edital de fomento {clean_agency}: {clean_title}",
            orgão_fomento=clean_agency,
            categoria=category,
            status="aberto",
            data_abertura=data_abertura,
            data_encerramento=data_encerramento,
            link=raw_data.url,
            cronograma=normalize_schedule_dates(cronograma),
            tags=tags,
            anexos=anexos
        )
