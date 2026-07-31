import os
import re
import io
import logging
from datetime import date
from typing import List, Dict, Optional
import pdfplumber

from src.core.interfaces import ITransform
from src.domain.models import RawEdital, EditalDomain
from src.components.transforms import publication_rules
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


# Rótulos de etapa que indicam início e fim do período de submissão. A ordem de
# precedência importa: `abertura das inscrições` descreve o marco do edital,
# enquanto `publicação` costuma ser a data em que o documento foi divulgado. Para
# uma chamada de fluxo contínuo, o início útil é a abertura das inscrições.
START_EVENT_TOKENS = (
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
PUBLICATION_EVENT_TOKENS = ("publicação", "publicacao")
END_EVENT_TOKENS = (
    "fim do período do edital",
    "fim do periodo do edital",
    "prazo para envio da proposta",
    "prazo para envio de propostas",
    "prazo para envio",
    "encerramento",
    "término",
    "termino",
)


def _is_iso_date(value) -> bool:
    return bool(re.match(r"\d{4}-\d{2}-\d{2}", str(value or "")))


def _first_date_matching(events: List[Dict[str, str]], tokens: tuple) -> str:
    for item in events:
        date_value = item.get("data") or ""
        if _is_iso_date(date_value) and _match_any_token(item.get("evento") or "", tokens):
            return date_value
    return ""


def derive_opening_date(events: List[Dict[str, str]]) -> str:
    """
    Data de abertura a partir do cronograma, ou vazio quando não há data alguma.

    Precedência: abertura de inscrições, depois publicação, depois a primeira data
    disponível. A abertura vem antes porque é o marco do edital; a publicação é
    quando o documento foi divulgado, e usá-la primeiro fazia a data do CMS
    sobrepor o início real das inscrições.

    Nunca inventa data: sem nenhuma etapa datada, devolve string vazia.
    """
    for tokens in (START_EVENT_TOKENS, PUBLICATION_EVENT_TOKENS):
        found = _first_date_matching(events, tokens)
        if found:
            return found
    for item in events:
        if _is_iso_date(item.get("data")):
            return item["data"]
    return ""


def derive_closing_date(
    raw_events: List[Dict[str, str]], normalized_events: List[Dict[str, str]]
) -> str:
    """
    Data de encerramento a partir do cronograma, ou vazio quando não há prazo.

    Vazio é resposta legítima: chamada de fluxo contínuo não tem encerramento.
    """
    for tokens in (END_EVENT_TOKENS, START_EVENT_TOKENS):
        for raw_item, normalized_item in zip(raw_events, normalized_events):
            end_date = _extract_last_schedule_date(raw_item.get("data") or "")
            if not end_date and _is_iso_date(normalized_item.get("data")):
                end_date = normalized_item["data"]
            if not end_date:
                continue
            if _match_any_token(normalized_item.get("evento") or "", tokens):
                return end_date
    return ""


def merge_cronograma(
    source_events: Optional[List[Dict[str, str]]],
    extracted_events: Optional[List[Dict[str, str]]],
) -> List[Dict[str, str]]:
    """
    Une o cronograma da fonte com o extraído do PDF, sem perder nenhum dos dois.

    Antes o cronograma da fonte simplesmente substituía o do Mistral. Como FAPES,
    CAPES e PROEX/IFES não fornecem cronograma, a substituição era por lista
    vazia e apagava o que o OCR havia extraído — 74 editais ficaram sem
    cronograma, e 23 sem data alguma.

    A fonte tem precedência em caso de mesmo evento, porque o dado dela é
    estruturado; os eventos que só o PDF traz são acrescentados ao fim.
    """
    merged: List[Dict[str, str]] = []
    seen: set = set()
    for events in (source_events or [], extracted_events or []):
        for item in events:
            if not isinstance(item, dict):
                continue
            event_name = (item.get("evento") or "").strip()
            key = event_name.lower()
            if not event_name or key in seen:
                continue
            seen.add(key)
            merged.append({"evento": event_name, "data": item.get("data") or ""})
    return merged

class EditalNormalizer(ITransform[RawEdital, EditalDomain]):
    """
    Normalizes the RawEdital data into a validated EditalDomain object.
    Applies regex cleaning on metadata and uses Mistral for high-accuracy extraction.
    """
    
    def __init__(self, extraction_service: Optional[MistralExtractionService] = None):
        self.extraction_service = extraction_service or MistralExtractionService()
        # Recusas desta execução, como {url: motivo}. O fluxo as registra no
        # índice de recusados para não repetir OCR de um edital que o portão já
        # rejeitou — sem isso, ele volta como novo em toda execução.
        self.rejections: Dict[str, str] = {}
    
    def process(self, raw_data: RawEdital) -> Optional[EditalDomain]:
        """
        Normaliza o RawEdital em EditalDomain.

        Devolve `None` quando o item não é uma oportunidade publicável — anexo
        solto, registro sem conteúdo extraído ou prazo já encerrado. Os sete
        fluxos já ignoram item nulo, então nada mais precisa mudar.
        """
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

        data_abertura = derive_opening_date(normalized_cronograma)
        data_encerramento = derive_closing_date(raw_cronograma, normalized_cronograma)

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
                    # Add tags based on document type
                    if raw_data.document_type == "alteração":
                        mistral_domain.tags.append("alteração")
                        mistral_domain.nome = f"[ALTERAÇÃO] {mistral_domain.nome}"
                    
                    mistral_domain.tags = list(dict.fromkeys((mistral_domain.tags or []) + tags))
                    mistral_domain.anexos = anexos

                    # Une o cronograma da fonte ao extraído do PDF. Antes o da
                    # fonte substituía o do Mistral, e como FAPES, CAPES e
                    # PROEX/IFES não fornecem cronograma, a substituição era por
                    # lista vazia: apagava o que o OCR já havia extraído.
                    merged = merge_cronograma(
                        normalized_cronograma, mistral_domain.cronograma
                    )
                    mistral_domain.cronograma = normalize_schedule_dates(merged)

                    # Rederiva as datas do cronograma resultante. A fonte tem
                    # precedência quando trouxe a data; senão vale o que o
                    # cronograma unido revelar, e só então o que o Mistral pôs
                    # nos campos escalares.
                    mistral_domain.data_abertura = (
                        data_abertura
                        or derive_opening_date(mistral_domain.cronograma)
                        or (mistral_domain.data_abertura or "")
                    )
                    mistral_domain.data_encerramento = (
                        data_encerramento
                        or derive_closing_date(merged, mistral_domain.cronograma)
                        or (mistral_domain.data_encerramento or "")
                    )

                    return self._publish_or_discard(mistral_domain, raw_data)
                else:
                    logger.warning(f"Mistral returned no domain for {clean_title}, falling back to basic extraction.")
            except Exception as e:
                logger.error(f"Error during Mistral extraction for {clean_title}: {e}")

        # Basic/Fallback extraction (for anexos or if Mistral fails)
        combined_text = (description + " " + clean_title).lower()
        category = raw_data.source_category or "outros"
        if "FINEP" in (raw_data.raw_agency or "").upper() and description:
            try:
                classified = self.extraction_service.categorize_finep_by_description(description)
                if classified:
                    category = classified
                    logger.info("FINEP edital categorizado por Mistral: %s", category)
                else:
                    # Classificador indisponível: mantém a categoria da fonte em
                    # vez de gravar um palpite como se fosse classificação.
                    logger.warning(
                        "Classificação FINEP indisponível; mantendo categoria da fonte: %s",
                        category,
                    )
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

        edital = EditalDomain(
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
        return self._publish_or_discard(edital, raw_data)

    def _publish_or_discard(
        self, edital: EditalDomain, raw_data: RawEdital
    ) -> Optional[EditalDomain]:
        """
        Aplica as regras de publicação e ajusta o status ao prazo.

        Item não publicável volta como `None`; os fluxos já o ignoram.
        """
        verdict = publication_rules.evaluate(edital, raw_data)
        if not verdict.publishable:
            logger.info(
                "Edital não publicado (%s): %s", verdict.reason, edital.nome[:70]
            )
            if raw_data.url:
                self.rejections[raw_data.url] = verdict.reason
            return None
        edital.status = publication_rules.resolve_status(edital)
        edital.categoria = publication_rules.canonical_category(
            edital.categoria, publication_rules.category_hint_text(edital)
        )
        edital.modalidade = publication_rules.resolve_modalidade(edital, raw_data)
        edital.ambito_geografico = publication_rules.resolve_ambito_geografico(
            edital, raw_data
        )
        edital.fonte_key = publication_rules.resolve_fonte_key(edital, raw_data)
        edital.publico_alvo = publication_rules.resolve_publico_alvo(edital, raw_data)
        return edital
