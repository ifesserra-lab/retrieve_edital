"""
Sinais de saúde compartilhados entre os fluxos ETL e o runner unificado.

Motivação: o runner tratava como `Sucesso` duas situações muito diferentes:

- o source devolveu **zero itens brutos** — o scraper quebrou;
- o source devolveu **zero itens novos** — o portal simplesmente não publicou nada.

Como as duas apareciam no log como "Sucesso, delta 0", as quedas da FINEP e do
CNPq passaram meses despercebidas. Ver `docs/spec_finep_cnpq_horizon.md`.

Os fluxos informam a contagem bruta pelo stdout, num formato que o runner
consegue ler sem acoplar-se ao código de cada fluxo.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

FLOW_STATS_PREFIX = "[flow-stats]"

_FLOW_STATS_REGEX = re.compile(
    rf"{re.escape(FLOW_STATS_PREFIX)}\s+raw=(\d+)(?:\s+new=(\d+))?"
)


@dataclass(frozen=True)
class FlowStats:
    """Contagens que um fluxo reporta ao runner."""

    raw_count: int
    new_count: Optional[int] = None

    @property
    def source_returned_nothing(self) -> bool:
        """True quando o source não trouxe nenhum item bruto da origem."""
        return self.raw_count == 0


def emit_flow_stats(raw_count: int, new_count: Optional[int] = None) -> None:
    """
    Publica as contagens do fluxo no stdout para o runner unificado ler.

    `raw_count` é o total lido da origem (antes de deduplicação); `new_count`,
    quando informado, é quanto sobrou depois de descartar o que já estava no
    registry.
    """
    line = f"{FLOW_STATS_PREFIX} raw={raw_count}"
    if new_count is not None:
        line += f" new={new_count}"
    print(line, flush=True)


def parse_flow_stats(output: str) -> Optional[FlowStats]:
    """
    Extrai as contagens da saída de um fluxo.

    Retorna `None` quando o fluxo não publicou estatísticas — fluxos ainda não
    instrumentados continuam funcionando, apenas sem esse sinal.
    """
    if not output:
        return None
    match = None
    for match in _FLOW_STATS_REGEX.finditer(output):
        pass  # a última ocorrência é a que vale
    if match is None:
        return None
    raw_count = int(match.group(1))
    new_count = int(match.group(2)) if match.group(2) is not None else None
    return FlowStats(raw_count=raw_count, new_count=new_count)


def warn_on_redirect(requested_url: str, final_url: str) -> bool:
    """
    Avisa quando a URL de listagem redirecionou para outro domínio ou caminho.

    Foi exatamente esse o sintoma da queda da FINEP: a URL antiga passou a
    responder 301 para um portal novo e o parser seguiu rodando contra uma
    página sem editais. Retorna True quando houve redirecionamento relevante.
    """
    if not requested_url or not final_url:
        return False
    if _canonical(requested_url) == _canonical(final_url):
        return False
    logger.warning(
        "URL de listagem redirecionou: %s -> %s. "
        "Se o parser depender da estrutura antiga, ele pode estar extraindo zero itens.",
        requested_url,
        final_url,
    )
    return True


def _canonical(url: str) -> str:
    """Normaliza esquema, 'www.' e barra final para comparar apenas domínio + caminho."""
    without_scheme = re.sub(r"^https?://", "", url.strip(), flags=re.IGNORECASE)
    without_www = re.sub(r"^www\.", "", without_scheme, flags=re.IGNORECASE)
    return without_www.rstrip("/").lower()
