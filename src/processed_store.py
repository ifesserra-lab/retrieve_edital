"""
Índice JSON de editais já baixados e processados.
Evita reprocessar os mesmos itens nos fluxos FAPES, FINEP, CONIF, PRPPG/IFES, CAPES e CNPq.
"""

import json
import logging
import os
from typing import Set, List

logger = logging.getLogger(__name__)

DEFAULT_PATH = "registry/processed_editais.json"
SOURCES = ("fapes", "finep", "conif", "prppg_ifes", "capes", "cnpq")


def _load_raw(path: str) -> dict:
    if not os.path.exists(path):
        return {s: [] for s in SOURCES}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.warning("Could not load processed index %s: %s", path, e)
        return {s: [] for s in SOURCES}
    for s in SOURCES:
        if s not in data or not isinstance(data[s], list):
            data[s] = []
    return data


def get_keys(source: str, path: str = DEFAULT_PATH) -> List[str]:
    """Retorna a lista de chaves já processadas para o source."""
    if source not in SOURCES:
        return []
    data = _load_raw(path)
    return list(data.get(source, []))


def get_keys_set(source: str, path: str = DEFAULT_PATH) -> Set[str]:
    """Retorna um set das chaves já processadas para o source."""
    return set(get_keys(source, path))


def contains(source: str, key: str, path: str = DEFAULT_PATH) -> bool:
    """Verifica se a chave já foi processada para o source."""
    return key in get_keys_set(source, path)


def add(source: str, key: str, path: str = DEFAULT_PATH) -> None:
    """Registra uma chave como processada."""
    if source not in SOURCES or not key:
        return
    data = _load_raw(path)
    if key not in data[source]:
        data[source].append(key)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.debug("Processed index: added %s for %s", key[:60], source)


def add_many(source: str, keys: List[str], path: str = DEFAULT_PATH) -> None:
    """Registra várias chaves como processadas (uma única escrita no arquivo)."""
    if source not in SOURCES or not keys:
        return
    data = _load_raw(path)
    existing = set(data[source])
    added = 0
    for k in keys:
        if k and k not in existing:
            data[source].append(k)
            existing.add(k)
            added += 1
    if added == 0:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Processed index: added %s keys for %s", added, source)


def build_index_from_output_dir(
    output_dir: str = "data/output",
    path: str = DEFAULT_PATH,
) -> None:
    """
    Popula o índice a partir dos JSON já existentes em output_dir.
    FAPES: chave = nome do arquivo sem .json.
    FINEP/CONIF/PRPPG-IFES/CAPES/CNPq: chave = campo link do JSON.
    """
    data = _load_raw(path)
    fapes_set = set(data["fapes"])
    finep_set = set(data["finep"])
    conif_set = set(data["conif"])
    prppg_ifes_set = set(data["prppg_ifes"])
    cnpq_set = set(data["cnpq"])
    capes_set = set(data["capes"])
    if not os.path.isdir(output_dir):
        logger.warning("Output dir does not exist: %s", output_dir)
        return
    for filename in os.listdir(output_dir):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                obj = json.load(f)
        except Exception as e:
            logger.warning("Could not load %s: %s", filepath, e)
            continue
        orgao = (obj.get("orgão_fomento") or "").strip().upper()
        if orgao == "FAPES":
            key = filename.replace(".json", "")
            fapes_set.add(key)
        elif orgao == "FINEP":
            link = (obj.get("link") or "").strip()
            if link:
                finep_set.add(link)
        elif orgao == "CONIF":
            link = (obj.get("link") or "").strip()
            if link:
                conif_set.add(link)
        elif orgao == "PRPPG/IFES":
            link = (obj.get("link") or "").strip()
            if link:
                prppg_ifes_set.add(link)
        elif orgao == "CAPES":
            link = (obj.get("link") or "").strip()
            if link:
                capes_set.add(link)
        elif orgao == "CNPQ":
            link = (obj.get("link") or "").strip()
            if link:
                cnpq_set.add(link)
    data["fapes"] = sorted(fapes_set)
    data["finep"] = sorted(finep_set)
    data["conif"] = sorted(conif_set)
    data["prppg_ifes"] = sorted(prppg_ifes_set)
    data["capes"] = sorted(capes_set)
    data["cnpq"] = sorted(cnpq_set)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(
        "Built index from %s: fapes=%s, finep=%s, conif=%s, prppg_ifes=%s, capes=%s, cnpq=%s",
        output_dir,
        len(data["fapes"]),
        len(data["finep"]),
        len(data["conif"]),
        len(data["prppg_ifes"]),
        len(data["capes"]),
        len(data["cnpq"]),
    )
