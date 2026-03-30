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


def _extract_last_schedule_date(text: str) -> str:
    if not text:
        return ""

    iso_matches = re.findall(r"\d{4}-\d{2}-\d{2}", str(text))
    if iso_matches:
        return iso_matches[-1]

    br_matches = re.findall(r"(\d{2})/(\d{2})/(\d{4})", str(text))
    if br_matches:
        day, month, year = br_matches[-1]
        return f"{year}-{month}-{day}"

    return ""


def _match_any_token(event_name: str, tokens: tuple[str, ...]) -> bool:
    lowered = (event_name or "").lower()
    return any(token in lowered for token in tokens)

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
        status = (raw_data.raw_status or "aberto").strip().lower() or "aberto"

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

        normalized_cronograma = normalize_schedule_dates(cronograma)
        raw_cronograma = list(cronograma)

        data_abertura = "2026-01-01"
        data_encerramento = ""
        start_fallback_tokens = (
            "início do período do edital",
            "inicio do período do edital",
            "abertura das inscrições",
            "abertura das inscricoes",
            "abertura da inscrição",
            "abertura da inscricao",
            "inscrição",
            "inscricao",
            "manifestação de interesse",
            "manifestacao de interesse",
            "início",
            "inicio",
            "período",
            "periodo",
        )
        end_fallback_tokens = (
            "fim do período do edital",
            "fim do periodo do edital",
            "prazo para envio da proposta",
            "prazo para envio de propostas",
            "prazo para envio",
            "encerramento",
            "término",
            "termino",
        )

        for item in normalized_cronograma:
            event_name = item.get("evento") or ""
            date_value = item.get("data") or ""
            if not re.match(r"\d{4}-\d{2}-\d{2}", str(date_value)):
                continue
            if _match_any_token(event_name, ("publicação", "publicacao")):
                data_abertura = date_value
                break

        if data_abertura == "2026-01-01":
            for item in normalized_cronograma:
                event_name = item.get("evento") or ""
                date_value = item.get("data") or ""
                if not re.match(r"\d{4}-\d{2}-\d{2}", str(date_value)):
                    continue
                if _match_any_token(event_name, start_fallback_tokens):
                    data_abertura = date_value
                    break

        if data_abertura == "2026-01-01":
            for item in normalized_cronograma:
                date_value = item.get("data") or ""
                if re.match(r"\d{4}-\d{2}-\d{2}", str(date_value)):
                    data_abertura = date_value
                    break

        for raw_item, normalized_item in zip(raw_cronograma, normalized_cronograma):
            event_name = normalized_item.get("evento") or ""
            normalized_date = normalized_item.get("data") or ""
            end_date = _extract_last_schedule_date(raw_item.get("data") or "")
            if not end_date and re.match(r"\d{4}-\d{2}-\d{2}", str(normalized_date)):
                end_date = normalized_date
            if not end_date:
                continue
            if _match_any_token(event_name, end_fallback_tokens):
                data_encerramento = end_date
                break

        if not data_encerramento:
            for raw_item, normalized_item in zip(raw_cronograma, normalized_cronograma):
                event_name = normalized_item.get("evento") or ""
                end_date = _extract_last_schedule_date(raw_item.get("data") or "")
                if not end_date:
                    continue
                if _match_any_token(event_name, start_fallback_tokens):
                    data_encerramento = end_date
                    break

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
                    mistral_domain.orgão_fomento = clean_agency
                    mistral_domain.status = status
                    # Force the category from the source website as requested
                    if raw_data.source_category:
                        mistral_domain.categoria = raw_data.source_category
                    if data_abertura:
                        mistral_domain.data_abertura = data_abertura
                    if data_encerramento:
                        mistral_domain.data_encerramento = data_encerramento
                    
                    # Add tags based on document type
                    if raw_data.document_type == "alteração":
                        mistral_domain.tags.append("alteração")
                        mistral_domain.nome = f"[ALTERAÇÃO] {mistral_domain.nome}"
                    
                    mistral_domain.tags = list(dict.fromkeys((mistral_domain.tags or []) + tags))
                    mistral_domain.anexos = anexos
                    
                    # Normalize dates
                    mistral_domain.cronograma = normalized_cronograma
                    
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

        return EditalDomain(
            nome=clean_title,
            descrição=description or f"Edital de fomento {clean_agency}: {clean_title}",
            orgão_fomento=clean_agency,
            categoria=category,
            status=status,
            data_abertura=data_abertura,
            data_encerramento=data_encerramento,
            link=raw_data.url,
            cronograma=normalized_cronograma,
            tags=tags,
            anexos=anexos
        )
