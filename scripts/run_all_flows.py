import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.flow_health import FlowStats, parse_flow_stats  # noqa: E402


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

RESULT_SUCCESS = "Sucesso"
RESULT_WARNING = "Atenção"
RESULT_FAILURE = "Falha"

# Após tantas execuções seguidas sem nenhum edital novo, o fluxo passa a ser
# reportado como suspeito. Foi a ausência desse sinal que deixou as quedas da
# FINEP e do CNPq invisíveis por meses.
ZERO_DELTA_ALERT_THRESHOLD = 7

# Fontes cujo volume normal é próximo de zero (ex.: ANEEL publica de 0 a 2
# chamadas por ano). Para elas, `delta 0` prolongado é o comportamento
# esperado e não deve gerar alerta.
LOW_VOLUME_FLOWS = frozenset()

DELTA_REGEX = re.compile(r"\(delta (-?\d+)\)")
LOG_SEPARATOR = "| :-- | :-- | :-- | :-- |\n"


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


def count_zero_delta_streak(workdir: Path, flow_name: str) -> int:
    """
    Conta quantas execuções seguidas do fluxo terminaram com `delta 0`.

    As linhas são inseridas logo abaixo do separador, então a leitura de cima
    para baixo já percorre da mais recente para a mais antiga.
    """
    log_path = workdir / LOG_PATH
    if not log_path.exists():
        return 0

    streak = 0
    for line in log_path.read_text(encoding="utf-8").splitlines():
        row = _parse_log_row(line)
        if row is None:
            continue
        row_flow, observations = row
        if row_flow != flow_name:
            continue
        delta_match = DELTA_REGEX.search(observations)
        if delta_match is None or int(delta_match.group(1)) != 0:
            break
        streak += 1
    return streak


def _parse_log_row(line: str) -> Optional[Tuple[str, str]]:
    """Extrai (fluxo, observações) de uma linha da tabela do log operacional."""
    stripped = line.strip()
    if not stripped.startswith("|") or ":--" in stripped:
        return None
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    if len(cells) < 4:
        return None
    return cells[1].strip("`"), cells[3]


def resolve_result(
    flow_name: str,
    return_code: int,
    delta: int,
    zero_delta_streak: int,
    stats: Optional[FlowStats],
) -> str:
    """
    Traduz o resultado da execução para o log operacional.

    Distinção que o runner não fazia: um source que devolve **zero itens
    brutos** está quebrado; um que devolve **zero itens novos** apenas não
    encontrou novidade. Só o segundo caso é sucesso.
    """
    if return_code != 0:
        return RESULT_FAILURE
    if stats is not None and stats.source_returned_nothing:
        return RESULT_WARNING
    if REGISTRY_KEYS[flow_name] in LOW_VOLUME_FLOWS:
        return RESULT_SUCCESS
    if delta == 0 and zero_delta_streak >= ZERO_DELTA_ALERT_THRESHOLD:
        return RESULT_WARNING
    return RESULT_SUCCESS


def build_observations(
    flow_name: str,
    before_counts: dict[str, int],
    after_counts: dict[str, int],
    output_json_count: int,
    non_json: list[str],
    return_code: int,
    stats: Optional[FlowStats] = None,
    zero_delta_streak: int = 0,
) -> tuple[str, str]:
    registry_key = REGISTRY_KEYS[flow_name]
    added = after_counts[registry_key] - before_counts[registry_key]
    non_json_message = "nenhum" if not non_json else ", ".join(non_json)
    result = resolve_result(
        flow_name=flow_name,
        return_code=return_code,
        delta=added,
        zero_delta_streak=zero_delta_streak,
        stats=stats,
    )
    observations = (
        f"Registry `{registry_key}`: {before_counts[registry_key]} -> "
        f"{after_counts[registry_key]} (delta {added}); "
        f"`data/output/` com {output_json_count} JSONs; "
        f"arquivos não-JSON: {non_json_message}."
    )
    if stats is not None:
        observations += f" Origem devolveu {stats.raw_count} itens brutos."
        if stats.source_returned_nothing:
            observations += (
                " A origem não devolveu nenhum item — verificar se o portal mudou."
            )
    if result == RESULT_WARNING and stats is None and added == 0:
        observations += (
            f" Sem editais novos há {zero_delta_streak} execuções seguidas —"
            " verificar se o source ainda funciona."
        )
    if return_code != 0:
        observations += f" Fluxo encerrou com exit code {return_code}."
    return result, observations.replace("|", "/")


def append_flow_log_row(
    workdir: Path,
    flow_name: str,
    before_counts: dict[str, int],
    return_code: int,
    stats: Optional[FlowStats] = None,
) -> str:
    after_counts = load_registry_counts(workdir)
    output_json_count, non_json = get_output_file_stats(workdir)
    registry_key = REGISTRY_KEYS[flow_name]
    added = after_counts[registry_key] - before_counts[registry_key]
    zero_delta_streak = (
        count_zero_delta_streak(workdir, flow_name) + 1 if added == 0 else 0
    )
    result, observations = build_observations(
        flow_name,
        before_counts,
        after_counts,
        output_json_count,
        non_json,
        return_code,
        stats=stats,
        zero_delta_streak=zero_delta_streak,
    )

    log_path = workdir / LOG_PATH
    if not log_path.exists():
        return result

    row = (
        f"| {current_timestamp()} | `{flow_name}` | {result} | "
        f"{observations} |\n"
    )
    lines = log_path.read_text(encoding="utf-8").splitlines(keepends=True)
    try:
        insert_at = lines.index(LOG_SEPARATOR) + 1
    except ValueError:
        insert_at = len(lines)
    lines.insert(insert_at, row)
    log_path.write_text("".join(lines), encoding="utf-8")
    return result


def run_command_capturing_output(
    command: list[str], workdir: Path
) -> tuple[int, str]:
    """Executa o fluxo repassando a saída ao console e guardando-a para análise."""
    process = subprocess.Popen(
        command,
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    captured: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        captured.append(line)
    process.wait()
    return process.returncode, "".join(captured)


def run_flow(name: str, command: list[str], workdir: Path) -> None:
    print(f"[run_all_flows] Starting {name} flow...")
    before_counts = load_registry_counts(workdir)
    return_code, output = run_command_capturing_output(command, workdir)
    stats = parse_flow_stats(output)
    result = append_flow_log_row(workdir, name, before_counts, return_code, stats)
    if return_code != 0:
        raise SystemExit(
            f"[run_all_flows] {name} flow failed with exit code {return_code}."
        )
    if result == RESULT_WARNING:
        print(
            f"[run_all_flows] {name} flow completed with warnings — "
            "ver docs/flow_processing_log.md."
        )
        return
    print(f"[run_all_flows] {name} flow completed successfully.")


def refresh_edital_status(workdir: Path) -> None:
    """
    Realinha o `status` dos editais já gravados ao respectivo prazo.

    Um edital coletado como `aberto` não se corrige sozinho quando o prazo passa,
    então isso precisa rodar em toda execução — sem isso, o portal exibe
    oportunidade encerrada como vigente. Não remove arquivo algum.
    """
    from curate_output import curate  # import local: evita ciclo na importação

    print("[run_all_flows] Realinhando o status dos editais ao prazo...")
    curate(workdir=workdir, apply=True, refresh_status_only=True, today=date.today())


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    for name, command in FLOW_COMMANDS:
        run_flow(name, command, repo_root)
    refresh_edital_status(repo_root)
    print("[run_all_flows] All flows completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
