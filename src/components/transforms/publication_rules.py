"""
Regras de publicação: o que é oportunidade de fomento e o que é ruído.

Levantamento de 2026-07-29 sobre os 211 editais em `data/output/`: apenas 47
estavam abertos com prazo futuro. O resto era ruído de três tipos:

- 24 cards de `[ANEXO]`/`[ALTERAÇÃO]` — documentos de um edital, não editais;
- 29 "cascas vazias" — a extração não produziu nada e o normalizer preencheu
  com placeholders (descrição gerada do título, sem cronograma, sem prazo);
- 63 já encerrados, visíveis porque os sources filtram por **ano** e não por
  data: em julho de 2026, um prazo de abril de 2026 ainda passa no filtro.

Estas regras rodam no fim do Transform. Como os fluxos já ignoram item nulo
(`if domain_item:`), rejeitar aqui basta para não publicar — sem alterar os
sete fluxos.
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.domain.models import EditalDomain, RawEdital

logger = logging.getLogger(__name__)

# Prefixo que o próprio normalizer usa quando não há descrição extraída.
FALLBACK_DESCRIPTION_PREFIX = "Edital de fomento"

# Tipos de documento que só fazem sentido acompanhando um edital.
SUPPORTING_DOCUMENT_TYPES = ("anexo", "alteração", "alteracao")

# Valores canônicos de `status`. O campo serve para filtrar oportunidade vigente
# de encerrada, então não admite variação de grafia.
STATUS_OPEN = "aberto"
STATUS_CLOSED = "encerrado"
CLOSED_SYNONYMS = ("encerrado", "encerrada", "fechado", "fechada", "finalizado")


@dataclass(frozen=True)
class PublicationVerdict:
    """Resultado da avaliação, com o motivo para registrar em log."""

    publishable: bool
    reason: str = ""


def _is_supporting_document(raw_data: RawEdital) -> bool:
    """
    Anexo ou alteração que chegou como item de topo.

    O FapesSource agrupa os documentos de um edital e aninha os demais em
    `attachments`, mas quando um anexo cai sozinho no grupo ele acaba eleito
    como principal por falta de candidato do tipo `edital` — e vira card.
    """
    return (raw_data.document_type or "").strip().lower() in SUPPORTING_DOCUMENT_TYPES


def _is_empty_shell(edital: EditalDomain) -> bool:
    """
    Registro sem conteúdo real: só título, com o resto preenchido por fallback.

    A assinatura é a combinação — descrição gerada a partir do título, nenhum
    cronograma e nenhum prazo. Qualquer uma isolada é aceitável: chamada de
    fluxo contínuo não tem prazo, e há editais legítimos sem cronograma.
    """
    has_generated_description = (edital.descrição or "").startswith(
        FALLBACK_DESCRIPTION_PREFIX
    )
    return (
        has_generated_description
        and not edital.cronograma
        and not (edital.data_encerramento or "").strip()
    )


def _deadline_has_passed(edital: EditalDomain, today: date) -> bool:
    """
    Prazo de encerramento anterior a hoje.

    Prazo ausente não conta como encerrado: pode ser chamada de fluxo contínuo.
    """
    deadline = (edital.data_encerramento or "").strip()
    if not deadline:
        return False
    try:
        return date.fromisoformat(deadline) < today
    except ValueError:
        # Data em formato inesperado não é motivo para descartar o edital.
        return False


def evaluate(
    edital: EditalDomain,
    raw_data: RawEdital,
    today: Optional[date] = None,
) -> PublicationVerdict:
    """Decide se o edital deve ser publicado, e por quê não quando for o caso."""
    reference_day = today or date.today()

    if _is_supporting_document(raw_data):
        return PublicationVerdict(
            False,
            f"documento de apoio ({raw_data.document_type}), não é um edital",
        )
    if _is_empty_shell(edital):
        return PublicationVerdict(
            False, "extração não produziu descrição, cronograma nem prazo"
        )
    if _deadline_has_passed(edital, reference_day):
        return PublicationVerdict(
            False, f"prazo encerrado em {edital.data_encerramento}"
        )
    return PublicationVerdict(True)


def resolve_status(edital: EditalDomain, today: Optional[date] = None) -> str:
    """
    Status coerente com o prazo, em dois valores canônicos.

    Usado tanto na normalização quanto na manutenção dos arquivos já gravados:
    um edital coletado como `aberto` não se corrige sozinho quando o prazo passa.

    O campo existe para filtrar aberto de encerrado, então só assume
    `STATUS_OPEN` ou `STATUS_CLOSED`. As fontes traziam grafias diferentes para o
    mesmo estado — `aberta` vinha de `situacao` na API da FINEP —, o que tornava o
    campo inútil como filtro.
    """
    reference_day = today or date.today()
    # A fonte tem a palavra final sobre encerramento: a PRPPG/IFES, por exemplo,
    # marca editais como encerrados antes do fim do período declarado. O prazo
    # sozinho não captura encerramento antecipado.
    if (edital.status or "").strip().lower() in CLOSED_SYNONYMS:
        return STATUS_CLOSED
    if _deadline_has_passed(edital, reference_day):
        return STATUS_CLOSED
    return STATUS_OPEN
