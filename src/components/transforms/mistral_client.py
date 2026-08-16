import os
import logging
import base64
import json
import time
from typing import Optional, Dict, Any, List, Callable, TypeVar

try:
    from mistralai import Mistral  # type: ignore[attr-defined]
except ImportError:
    try:
        from mistralai.client import Mistral  # type: ignore[attr-defined]
    except ImportError:
        from mistralai.client import MistralClient as Mistral

from src.components.transforms.extraction_contract import (
    FINEP_CATEGORIES,
    ExtractionUnavailableError,
    SYSTEM_PROMPT_CLASSIFY_TITLES,
    SYSTEM_PROMPT_EXTRACTION,
    SYSTEM_PROMPT_FINEP,
    build_classify_titles_prompt,
    build_extraction_prompt,
    build_finep_category_prompt,
    canonical_finep_category,
    map_to_domain,
)
from src.domain.models import EditalDomain

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Retry config for rate limit (429)
RATE_LIMIT_MAX_RETRIES = 10
RATE_LIMIT_INITIAL_WAIT_SEC = 60
RATE_LIMIT_BACKOFF_FACTOR = 2.0

# Teto de espera acumulada por chamada. Contar tentativas não limita o tempo: dez
# retentativas dobrando a partir de 60s somam mais de 17 horas, muito além de
# qualquer janela de job aceitável. O que importa é quanto tempo a chamada pode
# segurar o fluxo, então o corte é por tempo — a última espera é encurtada para
# não passar do teto, e depois disso a falha sobe para o chamador.
RATE_LIMIT_MAX_TOTAL_WAIT_SEC = 15 * 60


class MistralUnavailableError(ExtractionUnavailableError):
    """
    A API do Mistral recusou a credencial ou a assinatura (401/402/403).

    Diferente de um 429 ou de um PDF problemático, isto não é transitório: a
    conta não volta a ter crédito no meio da execução. Tratar como falha comum
    fazia cada PDF gastar três tentativas e ~45s antes de virar `None`, e o
    fluxo então seguia como se o edital apenas não tivesse conteúdo — o job
    terminava verde com a extração inteira morta. É por isso que esta exceção
    existe e atravessa os `except Exception` do caminho de extração.
    """


def _is_rate_limit_error(exc: Exception) -> bool:
    s = str(exc).lower()
    return "429" in s or "rate" in s and "limit" in s or "rate_limited" in s


def _is_credential_error(exc: Exception) -> bool:
    """
    Reconhece recusa de credencial ou de assinatura na resposta da API.

    Casa pelo código de status na mensagem do SDK (`Status 402`) e também pelo
    texto do corpo, porque o 402 da Mistral vem com `Check your subscription`.
    """
    s = str(exc).lower()
    if "check your subscription" in s or "unauthorized" in s:
        return True
    return any(f"status {code}" in s for code in ("401", "402", "403"))


def _call_with_rate_limit_retry(
    fn: Callable[[], T],
    context: str = "",
) -> T:
    """
    Executa fn(); em caso de 429 (rate limit) tenta de novo com backoff exponencial.

    O corte é por **tempo acumulado**, não por número de tentativas: contar
    tentativas não limita a duração, e dez retentativas dobrando a partir de 60s
    somariam mais de 17 horas. Ao esgotar o teto, a exceção sobe para o chamador,
    que registra a falha — e o canário do runner a torna visível.
    """
    last_exc = None
    total_waited = 0.0
    for attempt in range(RATE_LIMIT_MAX_RETRIES):
        try:
            return fn()
        except MistralUnavailableError:
            raise
        except Exception as e:
            last_exc = e
            # Credencial ou assinatura recusada não é caso de espera: nenhum
            # backoff devolve crédito à conta. Sobe já, e como tipo próprio,
            # para não ser confundida com um PDF que falhou.
            if _is_credential_error(e):
                raise MistralUnavailableError(
                    f"Mistral recusou a credencial/assinatura em '{context or 'Mistral API'}': {e}"
                ) from e
            if not _is_rate_limit_error(e) or attempt == RATE_LIMIT_MAX_RETRIES - 1:
                raise

            remaining = RATE_LIMIT_MAX_TOTAL_WAIT_SEC - total_waited
            if remaining <= 0:
                logger.error(
                    "Rate limit persistente: teto de %.0fs de espera esgotado após "
                    "%s tentativas. Desistindo. Contexto: %s",
                    RATE_LIMIT_MAX_TOTAL_WAIT_SEC,
                    attempt,
                    context or "Mistral API",
                )
                raise

            wait_sec = RATE_LIMIT_INITIAL_WAIT_SEC * (RATE_LIMIT_BACKOFF_FACTOR ** attempt)
            # Encurta a última espera para não estourar o teto.
            wait_sec = min(wait_sec, remaining)
            logger.warning(
                "Rate limit hit (%s). Waiting %.0fs before retry %s/%s "
                "(%.0fs de %.0fs do teto usados). Context: %s",
                e,
                wait_sec,
                attempt + 1,
                RATE_LIMIT_MAX_RETRIES,
                total_waited + wait_sec,
                RATE_LIMIT_MAX_TOTAL_WAIT_SEC,
                context or "Mistral API",
            )
            time.sleep(wait_sec)
            total_waited += wait_sec
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("Unexpected retry exit")


class MistralExtractionService:
    """
    Service to extract structured data from PDF editais using Mistral OCR and LLM.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY is not set.")
        self.client = Mistral(api_key=self.api_key)
        self.ocr_model = "mistral-ocr-latest"
        self.llm_model = "mistral-large-latest"

    def extract_from_pdf(self, pdf_bytes: bytes, filename: str) -> Optional[EditalDomain]:
        """
        Processes PDF bytes through Mistral OCR and extracts structured data using LLM.
        """
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            uploaded_file_id = None
            try:
                logger.info(f"Uploading PDF {filename} to Mistral for OCR (Attempt {attempt})...")
                
                # 1. Upload file for OCR (with rate-limit retry)
                uploaded_file = _call_with_rate_limit_retry(
                    lambda: self.client.files.upload(
                        file={
                            "file_name": filename,
                            "content": pdf_bytes,
                        },
                        purpose="ocr",
                    ),
                    context=f"upload {filename}",
                )
                uploaded_file_id = uploaded_file.id
                
                logger.info(f"File uploaded with ID: {uploaded_file_id}. Processing OCR...")
                
                # 2. Process OCR (with rate-limit retry)
                ocr_response = _call_with_rate_limit_retry(
                    lambda: self.client.ocr.process(
                        model=self.ocr_model,
                        document={
                            "type": "file",
                            "file_id": uploaded_file_id,
                        },
                    ),
                    context=f"OCR {filename}",
                )
                
                # Concatenate all pages text
                full_ocr_text = ""
                for page in ocr_response.pages:
                    full_ocr_text += f"\n{page.markdown}"
                
                logger.info("OCR completed. Extracting structured data...")
                
                # 3. Extract structured data via LLM (with rate-limit retry)
                time.sleep(2)
                prompt = build_extraction_prompt(full_ocr_text)
                
                response = _call_with_rate_limit_retry(
                    lambda: self.client.chat.complete(
                        model=self.llm_model,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT_EXTRACTION},
                            {"role": "user", "content": prompt},
                        ],
                        response_format={"type": "json_object"},
                    ),
                    context=f"extract LLM {filename}",
                )
                
                raw_json = response.choices[0].message.content
                extracted_data = json.loads(raw_json)
                
                # Cleanup: Delete the uploaded file to save space/cost
                try:
                    self.client.files.delete(file_id=uploaded_file_id)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to delete uploaded file {uploaded_file_id}: {cleanup_err}")
    
                return map_to_domain(extracted_data)

            except MistralUnavailableError:
                # Não conta como tentativa perdida: repetir não recupera crédito.
                if uploaded_file_id:
                    try:
                        self.client.files.delete(file_id=uploaded_file_id)
                    except Exception:
                        pass
                raise
            except Exception as e:
                logger.error("Mistral extraction failed for %s on attempt %s: %s", filename, attempt, e)
                if uploaded_file_id:
                    try:
                        self.client.files.delete(file_id=uploaded_file_id)
                    except Exception:
                        pass
                if attempt >= max_retries:
                    logger.error("Max retries reached for %s. Returning None.", filename)
                    return None
                wait_time = 120 if _is_rate_limit_error(e) else attempt * 15
                logger.info("Waiting %s seconds before next attempt...", wait_time)
                time.sleep(wait_time)
    
    def classify_document_titles(self, titles: List[str]) -> Dict[str, str]:
        """
        Uses Mistral to classify a list of document titles within a notice group.
        Returns a mapping of title -> document_type (edital, anexo, alteração).
        """
        if not titles:
            return {}

        prompt = build_classify_titles_prompt(titles)
        try:
            response = _call_with_rate_limit_retry(
                lambda: self.client.chat.complete(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT_CLASSIFY_TITLES},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                ),
                context="classify_document_titles",
            )
            raw_json = response.choices[0].message.content
            classification = json.loads(raw_json)
            logger.info("Classified %s titles: %s", len(titles), classification)
            return classification
        except MistralUnavailableError:
            # A heurística de fallback abaixo mascararia a conta sem crédito.
            raise
        except Exception as e:
            logger.error(f"Failed to classify titles: {e}")
            # Fallback heuristic
            fallback = {}
            for t in titles:
                tl = t.lower()
                if "anexo" in tl or "formulário" in tl or "declaração" in tl:
                    fallback[t] = "anexo"
                elif "alteração" in tl or "retificação" in tl or "aditivo" in tl:
                    fallback[t] = "alteração"
                else:
                    fallback[t] = "edital"
            return fallback

    # Mantido como atributo de classe por compatibilidade: código existente lê
    # `service.FINEP_CATEGORIES`. A fonte da verdade é o contrato compartilhado.
    FINEP_CATEGORIES = FINEP_CATEGORIES

    def categorize_finep_by_description(self, description: str) -> str:
        """
        Classifica um edital FINEP em uma das categorias, com base na descrição.
        Retorna: "divulgação de conhecimento", "extensão" ou "inovação".
        """
        if not (description or "").strip():
            return "inovação"
        prompt = build_finep_category_prompt(description)
        try:
            response = _call_with_rate_limit_retry(
                lambda: self.client.chat.complete(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT_FINEP},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                ),
                context="categorize_finep",
            )
            data = json.loads(response.choices[0].message.content or "{}")
            return canonical_finep_category(data.get("categoria")) or "inovação"
        except MistralUnavailableError:
            raise
        except Exception as e:
            # Devolve vazio, não um palpite: retornar "inovação" aqui tornava uma
            # chave de API inválida indistinguível de uma classificação real — o
            # chamador recebia um valor plausível e seguia adiante. Cabe a ele
            # decidir o fallback.
            logger.warning("Mistral categorize_finep_by_description failed: %s", e)
            return ""

