"""
Curadoria de `data/output/`: mantém o status coerente com o prazo e remove o que
não é oportunidade de fomento.

Motivação: as regras de publicação (`src/components/transforms/publication_rules.py`)
impedem que ruído novo entre, mas não corrigem o que já está gravado. Levantamento
de 2026-07-29, sobre 211 arquivos: 24 cards de anexo/alteração, 29 cascas vazias,
4 órfãos do portal descontinuado do CNPq e 63 com prazo já encerrado — apenas 47
abertos com prazo futuro.

Duas ações distintas, com riscos distintos:

- **Status**: recalculado a cada execução. Um edital coletado como `aberto` não se
  corrige sozinho quando o prazo passa, então isso precisa rodar sempre — o
  runner unificado o faz. Não remove nada.
- **Remoção**: só do que não é edital (anexo, alteração, casca vazia, órfão de
  portal morto). Editais encerrados **não** são removidos: viram `encerrado` e o
  portal decide se os exibe.

Uso:
    python scripts/curate_output.py                # relatório, não altera nada
    python scripts/curate_output.py --refresh-status  # só corrige status
    python scripts/curate_output.py --apply        # corrige status e remove ruído
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.components.transforms.publication_rules import (  # noqa: E402
    CLOSED_SYNONYMS,
    FALLBACK_DESCRIPTION_PREFIX,
    STATUS_CLOSED,
    STATUS_OPEN,
)

OUTPUT_DIR = Path("data/output")
REGISTRY_PATH = Path("registry/processed_editais.json")

SUPPORTING_TITLE_PREFIXES = ("[ANEXO]", "[ALTERAÇÃO]", "[ALTERACAO]")
DISCONTINUED_HOSTS = ("memoria2.cnpq.br",)

# Motivos de remoção, na ordem em que são avaliados.
REASON_SUPPORTING = "documento de apoio, não é edital"
REASON_SHELL = "casca vazia: sem descrição, cronograma nem prazo"
REASON_DISCONTINUED = "aponta para portal descontinuado"


def load_editais(output_dir: Path) -> List[Tuple[Path, dict]]:
    editais = []
    for path in sorted(output_dir.glob("*.json")):
        try:
            editais.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except ValueError as exc:
            print(f"  ! ilegível, mantido: {path.name} ({exc})")
    return editais


def removal_reason(edital: dict) -> str:
    """Motivo para não manter o arquivo, ou string vazia para manter."""
    nome = (edital.get("nome") or "").strip()
    if nome.startswith(SUPPORTING_TITLE_PREFIXES):
        return REASON_SUPPORTING

    link = (edital.get("link") or "").lower()
    if any(host in link for host in DISCONTINUED_HOSTS):
        return REASON_DISCONTINUED

    descricao = (edital.get("descrição") or edital.get("descricao") or "").strip()
    if (
        descricao.startswith(FALLBACK_DESCRIPTION_PREFIX)
        and not edital.get("cronograma")
        and not (edital.get("data_encerramento") or "").strip()
    ):
        return REASON_SHELL
    return ""


def expected_status(edital: dict, today: date) -> str:
    """
    Mesma regra de `publication_rules.resolve_status`, aplicada ao JSON gravado.

    Prazo vencido vira `encerrado`; prazo futuro vira `aberto`, inclusive quando
    o arquivo estava marcado como encerrado e o prazo foi prorrogado.
    """
    current = (edital.get("status") or "").strip().lower()
    deadline = (edital.get("data_encerramento") or "").strip()
    if deadline:
        try:
            if date.fromisoformat(deadline) < today:
                return STATUS_CLOSED
            return STATUS_OPEN
        except ValueError:
            pass
    return STATUS_CLOSED if current in CLOSED_SYNONYMS else STATUS_OPEN


def drop_registry_keys(registry_path: Path, keys: List[str], apply: bool) -> int:
    """
    Remove chaves do índice para que o edital possa ser recoletado.

    Usado só nas cascas vazias: são editais reais cuja extração falhou, e sem
    liberar a chave eles nunca voltariam. Anexos e órfãos mantêm a chave, para
    não serem baixados de novo à toa.
    """
    if not registry_path.exists() or not keys:
        return 0
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    targets = set(keys)
    removed = 0
    for source, entries in registry.items():
        if not isinstance(entries, list):
            continue
        kept = [entry for entry in entries if entry not in targets]
        removed += len(entries) - len(kept)
        registry[source] = kept
    if apply and removed:
        registry_path.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return removed


def curate(
    workdir: Path, apply: bool, refresh_status_only: bool, today: date
) -> Dict[str, int]:
    output_dir = workdir / OUTPUT_DIR
    if not output_dir.is_dir():
        print(f"Diretório inexistente: {output_dir}")
        return {}

    editais = load_editais(output_dir)
    print(f"{len(editais)} arquivos em {OUTPUT_DIR}\n")

    status_changes: List[Tuple[Path, str, str]] = []
    removals: Dict[str, List[Path]] = {}
    shell_keys: List[str] = []

    for path, edital in editais:
        reason = "" if refresh_status_only else removal_reason(edital)
        if reason:
            removals.setdefault(reason, []).append(path)
            if reason == REASON_SHELL:
                shell_keys.append(path.stem)
                link = (edital.get("link") or "").strip()
                if link:
                    shell_keys.append(link)
            continue

        wanted = expected_status(edital, today)
        if wanted != (edital.get("status") or "").strip():
            status_changes.append((path, edital.get("status") or "", wanted))
            if apply:
                edital["status"] = wanted
                path.write_text(
                    json.dumps(edital, ensure_ascii=False, indent=4), encoding="utf-8"
                )

    verb = "" if apply else " (simulação)"
    print(f"Status a corrigir{verb}: {len(status_changes)}")
    for path, before, after in status_changes[:10]:
        print(f"  {before or '(vazio)'!r} -> {after!r}  {path.name[:64]}")
    if len(status_changes) > 10:
        print(f"  ... e outros {len(status_changes) - 10}")

    total_removed = 0
    for reason, paths in removals.items():
        print(f"\nRemover — {reason}{verb}: {len(paths)}")
        for path in paths[:8]:
            print(f"  {path.name[:72]}")
        if len(paths) > 8:
            print(f"  ... e outros {len(paths) - 8}")
        total_removed += len(paths)
        if apply:
            for path in paths:
                path.unlink()

    freed = drop_registry_keys(workdir / REGISTRY_PATH, shell_keys, apply)
    if shell_keys:
        print(
            f"\nChaves liberadas no registry{verb}: {freed} "
            "(cascas vazias podem ser recoletadas)"
        )

    print(f"\nResumo{verb}: {len(status_changes)} status, {total_removed} removidos.")
    if not apply:
        print("Nada foi alterado. Use --apply para efetivar.")
    return {"status": len(status_changes), "removed": total_removed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="efetiva as mudanças (por padrão apenas relata)",
    )
    parser.add_argument(
        "--refresh-status",
        action="store_true",
        help="só recalcula o status; não remove arquivo algum",
    )
    args = parser.parse_args()

    curate(
        workdir=Path(__file__).resolve().parents[1],
        apply=args.apply or args.refresh_status,
        refresh_status_only=args.refresh_status,
        today=date.today(),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
