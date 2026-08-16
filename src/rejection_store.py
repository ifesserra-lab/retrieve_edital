"""
Índice de editais recusados pelas regras de publicação, com validade.

Motivação: um edital que o portão recusa nunca chega ao sink, então sua URL nunca
entra em `registry/processed_editais.json`. Na execução seguinte ele volta como
novo, tem o PDF baixado e passa por OCR — para ser recusado de novo. Medido na
FAPES: **8 editais por execução**, todos recusados por prazo vencido.

Registrar a recusa de forma permanente resolveria o desperdício mas criaria outro
problema: um edital cuja extração falhou e depois passou a funcionar nunca seria
recoletado. Por isso a recusa **expira**. Passada a validade, o edital é tentado
novamente.

Índice separado do de processados de propósito: são coisas distintas. Um edital
processado está publicado; um recusado não está, e pode voltar a ser candidato.

**Este arquivo só funciona se for versionado.** Entre 2026-07-31 e 2026-08-16 o
passo de commit do workflow adicionava apenas `registry/processed_editais.json`:
o runner reescrevia este índice a cada noite e o descartava junto com o
container, então a economia de OCR que ele existe para dar nunca aconteceu em
produção. O `git add` dos workflows cobre `registry` inteiro por causa disso, e
`tests/step_defs/test_run_all_flows.py` guarda a regra.
"""

import json
import logging
import os
from datetime import date, timedelta
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)

DEFAULT_PATH = "registry/rejected_editais.json"

# Quanto tempo uma recusa vale antes de o edital ser tentado de novo. Sete dias
# equilibram os dois riscos: não repetir OCR todo dia, e não ignorar para sempre
# um edital cuja extração possa melhorar ou cujo prazo seja prorrogado.
DEFAULT_TTL_DAYS = 7


def _load(path: str) -> Dict[str, Dict[str, dict]]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as exc:
        logger.warning("Índice de recusados ilegível (%s); tratando como vazio.", exc)
        return {}
    return data if isinstance(data, dict) else {}


def _save(data: Dict[str, Dict[str, dict]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)


def get_active_keys(
    source: str,
    path: str = DEFAULT_PATH,
    today: Optional[date] = None,
) -> Set[str]:
    """
    URLs cuja recusa ainda vale, e que portanto devem ser puladas nesta execução.

    Recusa expirada não é devolvida: o edital volta a ser candidato.
    """
    reference_day = today or date.today()
    ativos: Set[str] = set()
    for key, info in (_load(path).get(source) or {}).items():
        limite = (info or {}).get("valida_ate") or ""
        try:
            if date.fromisoformat(limite) >= reference_day:
                ativos.add(key)
        except ValueError:
            # Registro sem validade utilizável não segura o edital.
            continue
    return ativos


def record(
    source: str,
    rejections: Dict[str, str],
    path: str = DEFAULT_PATH,
    today: Optional[date] = None,
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> int:
    """
    Registra recusas como `{url: motivo}` e devolve quantas foram gravadas.

    Recusa já registrada tem a validade renovada: se o edital continua sendo
    recusado, não há por que tentá-lo de novo antes do prazo.
    """
    if not rejections:
        return 0
    reference_day = today or date.today()
    limite = (reference_day + timedelta(days=ttl_days)).isoformat()

    data = _load(path)
    por_fonte = data.setdefault(source, {})
    for key, motivo in rejections.items():
        if not key:
            continue
        por_fonte[key] = {
            "motivo": motivo,
            "recusado_em": reference_day.isoformat(),
            "valida_ate": limite,
        }
    _save(data, path)
    logger.info(
        "Índice de recusados: %s entradas para %s, válidas até %s.",
        len(rejections),
        source,
        limite,
    )
    return len(rejections)


def purge_expired(
    path: str = DEFAULT_PATH, today: Optional[date] = None
) -> int:
    """Remove recusas vencidas do índice e devolve quantas saíram."""
    reference_day = today or date.today()
    data = _load(path)
    removidas = 0
    for source, entradas in list(data.items()):
        mantidas = {}
        for key, info in (entradas or {}).items():
            limite = (info or {}).get("valida_ate") or ""
            try:
                if date.fromisoformat(limite) >= reference_day:
                    mantidas[key] = info
                    continue
            except ValueError:
                pass
            removidas += 1
        data[source] = mantidas
    if removidas:
        _save(data, path)
    return removidas
