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

# Vocabulário canônico de `categoria`. O campo é filtro no portal, e havia nove
# valores distintos em `data/output/` — incluindo `chamadas` (vazamento do slug
# da URL da FAPES), combinações livres devolvidas pelo Mistral como
# `pesquisa e inovação`, e `internacional`, que é âmbito e não tema.
#
# A ordem importa: ao procurar um termo dentro de texto livre, vale o que
# aparecer primeiro, que é como o Mistral escreve o tema principal.
CANONICAL_CATEGORIES = (
    "divulgação de conhecimento",
    "extensão",
    "inovação",
    "pesquisa",
)
CATEGORY_FALLBACK = "outros"

# Modalidade `fluxo-contínuo` marca a chamada aberta permanentemente. Sem ela,
# `data_encerramento` vazio significava tanto "candidate-se a qualquer momento"
# quanto "não sabemos o prazo", e quem usa o portal não distinguia os dois.
#
# Só sinal explícito conta: a ausência de prazo **não** é evidência de fluxo
# contínuo, é exatamente a ambiguidade que este campo resolve.
MODALITY_CONTINUOUS = "fluxo-contínuo"
CONTINUOUS_FLOW_MARKERS = ("fluxo contínuo", "fluxo continuo", "fluxo-contínuo")

# Âmbito geográfico e chave técnica por fonte monitorada. É conhecimento estático
# e certo: a FAPES é a fundação estadual do Espírito Santo, PRPPG e PROEX são
# unidades do IFES, o Horizon é europeu. Não há inferência aqui — o que a origem
# não permite afirmar fica vazio.
SOURCE_PROFILES = {
    "FAPES": ("estadual-ES", "fapes"),
    "FINEP": ("nacional", "finep"),
    "CAPES": ("nacional", "capes"),
    "CNPQ": ("nacional", "cnpq"),
    "CONIF": ("nacional", "conif"),
    "PRPPG/IFES": ("estadual-ES", "prppg_ifes"),
    "PROEX/IFES": ("estadual-ES", "proex_ifes"),
    "HORIZON EUROPE": ("internacional", "horizon"),
}

# Valores canônicos de `publico_alvo`, conforme o §3.2 do PDF de análise.
PUBLICO_PESQUISADOR = "pesquisador"
PUBLICO_ESTUDANTE = "estudante"
PUBLICO_EMPRESA = "empresa"
PUBLICO_ICT_EMPRESA = "ict-empresa"
PUBLICO_INTERNACIONAL = "internacional"
CANONICAL_PUBLICO_ALVO = (
    PUBLICO_PESQUISADOR,
    PUBLICO_ESTUDANTE,
    PUBLICO_EMPRESA,
    PUBLICO_ICT_EMPRESA,
    PUBLICO_INTERNACIONAL,
)


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


def _first_canonical_term(text: str) -> str:
    """Primeiro termo canônico que aparece no texto, por posição."""
    lowered = (text or "").lower()
    positions = [
        (lowered.find(category), category)
        for category in CANONICAL_CATEGORIES
        if lowered.find(category) >= 0
    ]
    if not positions:
        return ""
    return min(positions)[1]


def canonical_category(value: Optional[str], hint_text: str = "") -> str:
    """
    Reduz `categoria` ao vocabulário canônico.

    Três tentativas, em ordem: o valor já é canônico; o valor contém um termo
    canônico (`pesquisa e inovação` → `pesquisa`); ou o tema aparece no texto do
    edital (`hint_text`, com título, descrição e tags). Só então cai em
    `outros` — assim valores que descrevem o instrumento em vez do tema, como
    `chamadas` ou `internacional`, ainda podem ser recuperados pelo conteúdo.
    """
    normalized = (value or "").strip().lower()
    if normalized in CANONICAL_CATEGORIES:
        return normalized
    from_value = _first_canonical_term(normalized)
    if from_value:
        return from_value
    from_hint = _first_canonical_term(hint_text)
    if from_hint:
        return from_hint
    return CATEGORY_FALLBACK


def category_hint_text(edital: EditalDomain) -> str:
    """Texto onde procurar o tema quando `categoria` não é conclusiva."""
    return " ".join(
        [
            edital.nome or "",
            edital.descrição or "",
            " ".join(edital.tags or []),
        ]
    )


def resolve_modalidade(edital: EditalDomain, raw_data: RawEdital) -> str:
    """
    Modalidade da chamada, hoje limitada a marcar fluxo contínuo.

    Duas evidências valem, ambas explícitas: a origem declarou a modalidade em
    `raw_modalidade`, ou o próprio texto do edital diz "fluxo contínuo".

    Deduzir fluxo contínuo da falta de prazo seria circular — é justamente o que
    este campo existe para desambiguar.
    """
    declared = (raw_data.raw_modalidade or "").strip().lower()
    if declared:
        return declared
    haystack = f"{edital.nome or ''} {edital.descrição or ''}".lower()
    if any(marker in haystack for marker in CONTINUOUS_FLOW_MARKERS):
        return MODALITY_CONTINUOUS
    return (edital.modalidade or "").strip().lower()


def _profile_of(edital: EditalDomain) -> tuple:
    return SOURCE_PROFILES.get((edital.orgão_fomento or "").strip().upper(), ("", ""))


def resolve_ambito_geografico(edital: EditalDomain, raw_data: RawEdital) -> str:
    """
    Âmbito geográfico: o declarado pela origem, ou o perfil da fonte.

    A origem tem precedência porque pode ser mais específica — a FINEP informa a
    região da chamada, que não é sempre "Todo Brasil".
    """
    declarado = (raw_data.raw_ambito_geografico or "").strip()
    if declarado:
        return declarado
    if (edital.ambito_geografico or "").strip():
        return edital.ambito_geografico.strip()
    return _profile_of(edital)[0]


def resolve_fonte_key(edital: EditalDomain, raw_data: RawEdital) -> str:
    """Chave técnica da fonte. `orgão_fomento` é rótulo de exibição."""
    return _profile_of(edital)[1] or (edital.fonte_key or "").strip()


def resolve_publico_alvo(edital: EditalDomain, raw_data: RawEdital) -> list:
    """
    Público-alvo, apenas com o que a origem declara.

    Fonte que não informa fica com lista vazia. Inferir do texto produziria
    rótulo plausível e não verificável — o mesmo erro que fazia uma chave de API
    inválida parecer classificação.
    """
    declarado = raw_data.raw_publico_alvo or edital.publico_alvo or []
    vistos = []
    for valor in declarado:
        normalizado = (str(valor) or "").strip().lower()
        if normalizado in CANONICAL_PUBLICO_ALVO and normalizado not in vistos:
            vistos.append(normalizado)
    return vistos


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
