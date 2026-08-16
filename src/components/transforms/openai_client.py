"""
Provedor de reserva: OpenAI assume a extração quando a Mistral não responde.

Motivação: entre 2026-08-10 e 2026-08-16 a API da Mistral respondeu
`402 Check your subscription` a toda chamada e o pipeline ficou sem extração
alguma. Com um segundo provedor, a recusa de credencial deixa de parar a coleta.

**Diferença importante em relação à Mistral:** a Mistral tem OCR de verdade
(`mistral-ocr-latest`), que lê PDF digitalizado. A OpenAI não expõe um endpoint
equivalente aqui, então o texto é extraído localmente com `pdfplumber` — que lê
a camada de texto do PDF e **não faz OCR**. Para edital nativo digital (a grande
maioria) o resultado é equivalente; para PDF que é imagem escaneada, o
`pdfplumber` devolve quase nada.

Esse caso é tratado explicitamente: abaixo de `MIN_EXTRACTABLE_CHARS` o serviço
recusa em vez de mandar um prompt vazio ao modelo. Um prompt sem texto produz um
edital inventado com aparência perfeitamente plausível, que é o pior resultado
possível — pior que falhar.
"""

import io
import json
import logging
import os
from typing import Any, Dict, List, Optional

from src.components.transforms.extraction_contract import (
    SYSTEM_PROMPT_CLASSIFY_TITLES,
    ExtractionUnavailableError,
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

# Nome da variável de ambiente, na ordem de preferência. `API_KEY` é o nome
# usado neste projeto; `OPENAI_API_KEY` é o padrão do SDK e vale como alternativa.
API_KEY_ENV_VARS = ("API_KEY", "OPENAI_API_KEY")

DEFAULT_MODEL = "gpt-4o"

# Abaixo disto o PDF é tratado como não extraível. Um edital real tem milhares de
# caracteres; um PDF digitalizado devolve algumas dezenas de resíduo de layout.
MIN_EXTRACTABLE_CHARS = 200

# Teto do texto enviado ao modelo. Editais longos cabem folgados; o corte existe
# só para não estourar a janela de contexto num documento anômalo.
MAX_PROMPT_CHARS = 120_000


class OpenAIUnavailableError(ExtractionUnavailableError):
    """
    A OpenAI recusou a credencial, a cota ou não está configurada.

    Pareia com `MistralUnavailableError`: quando as duas sobem, não há provedor
    de extração vivo e o fluxo precisa falhar de forma visível em vez de gravar
    editais vazios.
    """


class PdfTextNotExtractableError(RuntimeError):
    """
    O PDF não tem camada de texto utilizável — provavelmente é digitalizado.

    Não é falha do provedor: é limite do caminho sem OCR. Sobe como tipo próprio
    para que o chamador saiba que trocar de provedor não resolve.
    """


def _is_credential_error(exc: Exception) -> bool:
    """Reconhece recusa de credencial, cota ou faturamento na resposta da API."""
    s = str(exc).lower()
    if "insufficient_quota" in s or "invalid_api_key" in s or "unauthorized" in s:
        return True
    return any(f"status {code}" in s or f"error code: {code}" in s
               for code in ("401", "402", "403", "429"))


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """
    Lê a camada de texto do PDF com pdfplumber.

    Devolve string vazia quando o PDF é ilegível — o chamador decide o que fazer.
    """
    import pdfplumber  # import local: mantém o custo fora do caminho sem PDF

    partes: List[str] = []
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text() or ""
                if texto:
                    partes.append(texto)
    except Exception as exc:
        logger.warning("pdfplumber não conseguiu abrir o PDF: %s", exc)
        return ""
    return "\n".join(partes).strip()


class OpenAIExtractionService:
    """
    Mesma interface de `MistralExtractionService`, para ser intercambiável.

    Os três métodos públicos — `extract_from_pdf`, `classify_document_titles` e
    `categorize_finep_by_description` — têm assinatura e contrato de retorno
    idênticos, e usam os prompts compartilhados de `extraction_contract`, para
    que trocar de provedor não mude o formato do edital gravado.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        self.api_key = api_key or _first_env(API_KEY_ENV_VARS)
        self.model = model or os.getenv("OPENAI_MODEL") or DEFAULT_MODEL
        if client is not None:
            self.client = client
            return
        if not self.api_key:
            raise OpenAIUnavailableError(
                "Nenhuma chave da OpenAI definida "
                f"(procurado em {', '.join(API_KEY_ENV_VARS)})."
            )
        from openai import OpenAI  # import local: dependência opcional em teste

        self.client = OpenAI(api_key=self.api_key)

    # ------------------------------------------------------------------ #

    def _complete_json(self, system_prompt: str, user_prompt: str, context: str) -> dict:
        """Uma chamada de chat que devolve JSON, com o erro traduzido."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            if _is_credential_error(exc):
                raise OpenAIUnavailableError(
                    f"OpenAI recusou a credencial/cota em '{context}': {exc}"
                ) from exc
            raise
        return json.loads(response.choices[0].message.content or "{}")

    # ------------------------------------------------------------------ #

    def extract_from_pdf(
        self, pdf_bytes: bytes, filename: str
    ) -> Optional[EditalDomain]:
        """
        Extrai o edital estruturado do PDF, sem OCR.

        Levanta `PdfTextNotExtractableError` quando o PDF não tem texto legível —
        mandar o prompt vazio produziria um edital inventado.
        """
        texto = extract_pdf_text(pdf_bytes)
        if len(texto) < MIN_EXTRACTABLE_CHARS:
            raise PdfTextNotExtractableError(
                f"{filename}: apenas {len(texto)} caracteres extraíveis "
                f"(mínimo {MIN_EXTRACTABLE_CHARS}). PDF provavelmente digitalizado; "
                "a OpenAI é usada sem OCR."
            )
        if len(texto) > MAX_PROMPT_CHARS:
            logger.warning(
                "%s: texto truncado de %s para %s caracteres.",
                filename,
                len(texto),
                MAX_PROMPT_CHARS,
            )
            texto = texto[:MAX_PROMPT_CHARS]

        logger.info(
            "OpenAI (%s): extraindo %s a partir de %s caracteres de texto.",
            self.model,
            filename,
            len(texto),
        )
        dados = self._complete_json(
            SYSTEM_PROMPT_EXTRACTION,
            build_extraction_prompt(texto),
            context=f"extract {filename}",
        )
        return map_to_domain(dados)

    def classify_document_titles(self, titles: List[str]) -> Dict[str, str]:
        """Classifica os títulos de um grupo em edital/anexo/alteração."""
        if not titles:
            return {}
        classificacao = self._complete_json(
            SYSTEM_PROMPT_CLASSIFY_TITLES,
            build_classify_titles_prompt(titles),
            context="classify_document_titles",
        )
        logger.info("OpenAI classificou %s títulos.", len(titles))
        return classificacao

    def categorize_finep_by_description(self, description: str) -> str:
        """Categoriza uma chamada FINEP pela descrição."""
        if not (description or "").strip():
            return "inovação"
        dados = self._complete_json(
            SYSTEM_PROMPT_FINEP,
            build_finep_category_prompt(description),
            context="categorize_finep",
        )
        return canonical_finep_category(dados.get("categoria")) or "inovação"


def _first_env(names) -> Optional[str]:
    for name in names:
        valor = (os.getenv(name) or "").strip()
        if valor:
            return valor
    return None


def is_configured() -> bool:
    """True quando há chave da OpenAI no ambiente."""
    return _first_env(API_KEY_ENV_VARS) is not None
