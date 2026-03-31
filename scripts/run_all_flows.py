import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


FLOW_COMMANDS = (
    ("FAPES", [sys.executable, "-m", "src.flows.ingest_fapes_flow"]),
    ("FINEP", [sys.executable, "-m", "src.flows.ingest_finep_flow"]),
    ("CONIF", [sys.executable, "-m", "src.flows.ingest_conif_flow"]),
    ("PRPPG_IFES", [sys.executable, "-m", "src.flows.ingest_prppg_ifes_flow"]),
    ("PROEX_IFES", [sys.executable, "-m", "src.flows.ingest_proex_ifes_flow"]),
    ("CAPES", [sys.executable, "-m", "src.flows.ingest_capes_flow"]),
    ("CNPQ", [sys.executable, "-m", "src.flows.ingest_cnpq_flow"]),
)
REGISTRY_KEYS = {
    "FAPES": "fapes",
    "FINEP": "finep",
    "CONIF": "conif",
    "PRPPG_IFES": "prppg_ifes",
    "PROEX_IFES": "proex_ifes",
    "CAPES": "capes",
    "CNPQ": "cnpq",
}
LOG_PATH = Path("docs/flow_processing_log.md")
REGISTRY_PATH = Path("registry/processed_editais.json")
OUTPUT_PATH = Path("data/output")


def load_registry_counts(workdir: Path) -> dict[str, int]:
    registry_path = workdir / REGISTRY_PATH
    if not registry_path.exists():
        return {value: 0 for value in REGISTRY_KEYS.values()}
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    return {
        source: len(data.get(source, []))
        for source in REGISTRY_KEYS.values()
    }


def get_output_file_stats(workdir: Path) -> tuple[int, list[str]]:
    output_dir = workdir / OUTPUT_PATH
    if not output_dir.exists():
        return 0, []
    files = [path.name for path in output_dir.iterdir() if path.is_file()]
    non_json = sorted(name for name in files if not name.endswith(".json"))
    json_count = sum(1 for name in files if name.endswith(".json"))
    return json_count, non_json


def current_timestamp() -> str:
    now = datetime.now(ZoneInfo("America/Sao_Paulo"))
    offset = now.strftime("%z")
    formatted_offset = f"{offset[:3]}:{offset[3:]}"
    return now.strftime("%Y-%m-%d %H:%M:%S ") + formatted_offset


def build_observations(
    flow_name: str,
    before_counts: dict[str, int],
    after_counts: dict[str, int],
    output_json_count: int,
    non_json: list[str],
    return_code: int,
) -> tuple[str, str]:
    registry_key = REGISTRY_KEYS[flow_name]
    added = after_counts[registry_key] - before_counts[registry_key]
    non_json_message = "nenhum" if not non_json else ", ".join(non_json)
    result = "Sucesso" if return_code == 0 else "Falha"
    observations = (
        f"Registry `{registry_key}`: {before_counts[registry_key]} -> "
        f"{after_counts[registry_key]} (delta {added}); "
        f"`data/output/` com {output_json_count} JSONs; "
        f"arquivos não-JSON: {non_json_message}."
    )
    if return_code != 0:
        observations += f" Fluxo encerrou com exit code {return_code}."
    return result, observations.replace("|", "/")


def append_flow_log_row(
    workdir: Path,
    flow_name: str,
    before_counts: dict[str, int],
    return_code: int,
) -> None:
    log_path = workdir / LOG_PATH
    if not log_path.exists():
        return

    after_counts = load_registry_counts(workdir)
    output_json_count, non_json = get_output_file_stats(workdir)
    result, observations = build_observations(
        flow_name,
        before_counts,
        after_counts,
        output_json_count,
        non_json,
        return_code,
    )
    row = (
        f"| {current_timestamp()} | `{flow_name}` | {result} | "
        f"{observations} |\n"
    )

    lines = log_path.read_text(encoding="utf-8").splitlines(keepends=True)
    separator = "| :-- | :-- | :-- | :-- |\n"
    try:
        insert_at = lines.index(separator) + 1
    except ValueError:
        insert_at = len(lines)
    lines.insert(insert_at, row)
    log_path.write_text("".join(lines), encoding="utf-8")


def run_flow(name: str, command: list[str], workdir: Path) -> None:
    print(f"[run_all_flows] Starting {name} flow...")
    before_counts = load_registry_counts(workdir)
    completed = subprocess.run(command, cwd=workdir)
    append_flow_log_row(workdir, name, before_counts, completed.returncode)
    if completed.returncode != 0:
        raise SystemExit(
            f"[run_all_flows] {name} flow failed with exit code {completed.returncode}."
        )
    print(f"[run_all_flows] {name} flow completed successfully.")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    for name, command in FLOW_COMMANDS:
        run_flow(name, command, repo_root)
    print("[run_all_flows] All flows completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
