"""
Encadeamento de provedores de extração: Mistral primeiro, OpenAI como reserva.

Regra: o provedor de reserva entra quando o principal **não está disponível** —
credencial ou assinatura recusada (`MistralUnavailableError`). Não entra por
qualquer erro: um PDF corrompido falha nos dois provedores, e reprocessá-lo só
duplica o custo e o tempo.

Se os dois falharem, a exceção sobe. Isso é deliberado: a única coisa pior que o
pipeline parar é ele continuar gravando editais vazios como se estivessem certos.
"""

import logging
from typing import Any, Dict, List, Optional

from src.components.transforms.extraction_contract import ExtractionUnavailableError
from src.components.transforms.mistral_client import MistralUnavailableError
from src.components.transforms.openai_client import OpenAIUnavailableError
from src.domain.models import EditalDomain

logger = logging.getLogger(__name__)


class AllProvidersUnavailableError(ExtractionUnavailableError):
    """Nenhum provedor de extração respondeu. O fluxo precisa falhar."""


class FallbackExtractionService:
    """
    Expõe a interface de extração e delega ao primeiro provedor que responder.

    Intercambiável com `MistralExtractionService` e `OpenAIExtractionService`:
    mesmos três métodos, mesmas assinaturas.
    """

    def __init__(self, primary: Any, secondary: Any) -> None:
        self.primary = primary
        self.secondary = secondary
        # Uma vez que o principal recusou a credencial, ele vai recusar todas as
        # chamadas seguintes desta execução. Sem esta memória, cada edital pagaria
        # de novo o roundtrip até o 402 antes de cair na reserva.
        self._primary_down = False

    # ------------------------------------------------------------------ #

    def _delegate(self, metodo: str, *args, **kwargs):
        if not self._primary_down:
            try:
                return getattr(self.primary, metodo)(*args, **kwargs)
            except MistralUnavailableError as exc:
                self._primary_down = True
                logger.warning(
                    "Provedor principal indisponível (%s). "
                    "As chamadas seguintes desta execução vão direto para a reserva.",
                    exc,
                )
        try:
            return getattr(self.secondary, metodo)(*args, **kwargs)
        except OpenAIUnavailableError as exc:
            raise AllProvidersUnavailableError(
                f"Principal indisponível e reserva falhou em '{metodo}': {exc}"
            ) from exc
        # `PdfTextNotExtractableError` não é tratada aqui de propósito: um PDF
        # digitalizado é problema daquele documento, não do provedor. Ela sobe
        # como erro comum e o normalizador a absorve caindo na extração básica,
        # do mesmo jeito que faz com um PDF corrompido.

    # ------------------------------------------------------------------ #

    def extract_from_pdf(
        self, pdf_bytes: bytes, filename: str
    ) -> Optional[EditalDomain]:
        return self._delegate("extract_from_pdf", pdf_bytes, filename)

    def classify_document_titles(self, titles: List[str]) -> Dict[str, str]:
        return self._delegate("classify_document_titles", titles)

    def categorize_finep_by_description(self, description: str) -> str:
        return self._delegate("categorize_finep_by_description", description)


def build_extraction_service() -> Any:
    """
    Monta o serviço de extração conforme as chaves presentes no ambiente.

    - Mistral + OpenAI  → encadeado, com a OpenAI de reserva.
    - Só Mistral        → Mistral sozinho (comportamento histórico).
    - Só OpenAI         → OpenAI sozinho, para o caso de a assinatura da Mistral
                          ter acabado e ninguém ter reposto.
    - Nenhuma           → levanta, como antes: sem chave não há extração.
    """
    from src.components.transforms import openai_client
    from src.components.transforms.mistral_client import MistralExtractionService
    from src.components.transforms.openai_client import OpenAIExtractionService

    try:
        mistral = MistralExtractionService()
    except ValueError:
        mistral = None

    reserva_disponivel = openai_client.is_configured()

    if mistral is not None and reserva_disponivel:
        logger.info("Extração: Mistral (principal) com OpenAI de reserva.")
        return FallbackExtractionService(mistral, OpenAIExtractionService())
    if mistral is not None:
        logger.info(
            "Extração: apenas Mistral. Defina %s para habilitar a reserva OpenAI.",
            openai_client.API_KEY_ENV_VARS[0],
        )
        return mistral
    if reserva_disponivel:
        logger.warning(
            "MISTRAL_API_KEY ausente; a extração vai rodar só na OpenAI, sem OCR. "
            "PDF digitalizado não será extraído."
        )
        return OpenAIExtractionService()

    raise ValueError(
        "Nenhuma chave de extração definida: defina MISTRAL_API_KEY ou "
        f"{openai_client.API_KEY_ENV_VARS[0]}."
    )
