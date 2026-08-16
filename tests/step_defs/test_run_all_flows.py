import pytest

from scripts import run_all_flows
from src.flow_health import FlowStats

# Referência capturada antes de qualquer stub, para o teste que exercita a poda
# de verdade contra um diretório temporário.
_purge_real = run_all_flows.purge_expired_rejections


@pytest.fixture(autouse=True)
def _nao_poda_o_registry_real(monkeypatch):
    """
    `main()` poda o índice de recusados do repositório em que roda.

    Sem esta trava, todo teste que chama `main()` reescreve
    `registry/rejected_editais.json` de verdade — foi o que aconteceu ao ligar a
    poda: quatro testes já existentes apagaram as 21 entradas versionadas. Teste
    não pode alterar dado versionado do projeto.
    """
    monkeypatch.setattr(run_all_flows, "purge_expired_rejections", lambda workdir: 0)


def test_flow_commands_include_capes_and_cnpq_in_expected_order():
    assert [name for name, _ in run_all_flows.FLOW_COMMANDS] == [
        "FAPES",
        "FINEP",
        "CONIF",
        "PRPPG_IFES",
        "PROEX_IFES",
        "CAPES",
        "CNPQ",
        "CONFAP",
    ]


def test_registry_keys_include_new_integrated_flows():
    assert run_all_flows.REGISTRY_KEYS == {
        "FAPES": "fapes",
        "FINEP": "finep",
        "CONIF": "conif",
        "PRPPG_IFES": "prppg_ifes",
        "PROEX_IFES": "proex_ifes",
        "CAPES": "capes",
        "CNPQ": "cnpq",
        "CONFAP": "confap",
    }


def test_main_runs_all_flows_in_sequence(monkeypatch, tmp_path):
    executed = []

    def fake_run_flow(name, command, workdir, timeout_sec=None):
        executed.append((name, command[2]))
        return run_all_flows.RESULT_SUCCESS

    monkeypatch.setattr(run_all_flows, "run_flow", fake_run_flow)
    monkeypatch.setattr(run_all_flows, "refresh_edital_status", lambda workdir: None)

    exit_code = run_all_flows.main([])

    assert exit_code == 0
    assert executed == [
        ("FAPES", "src.flows.ingest_fapes_flow"),
        ("FINEP", "src.flows.ingest_finep_flow"),
        ("CONIF", "src.flows.ingest_conif_flow"),
        ("PRPPG_IFES", "src.flows.ingest_prppg_ifes_flow"),
        ("PROEX_IFES", "src.flows.ingest_proex_ifes_flow"),
        ("CAPES", "src.flows.ingest_capes_flow"),
        ("CNPQ", "src.flows.ingest_cnpq_flow"),
        ("CONFAP", "src.flows.ingest_confap_flow"),
    ]


class TestSelecaoDeFluxos:
    def test_sem_only_roda_todos(self):
        assert len(run_all_flows.select_flows(None)) == len(run_all_flows.FLOW_COMMANDS)

    def test_only_filtra_e_preserva_a_ordem(self):
        selecionados = [nome for nome, _ in run_all_flows.select_flows("CNPQ,FINEP")]
        # A ordem é a de FLOW_COMMANDS, não a do argumento.
        assert selecionados == ["FINEP", "CNPQ"]

    def test_nome_desconhecido_e_erro_explicito(self):
        """Silenciosamente não rodar nada seria pior que falhar."""
        with pytest.raises(SystemExit, match="Fluxo desconhecido"):
            run_all_flows.select_flows("FAPEMIG")

    def test_espacos_e_caixa_sao_tolerados(self):
        assert [nome for nome, _ in run_all_flows.select_flows(" finep , cnpq ")] == [
            "FINEP",
            "CNPQ",
        ]


class TestIsolamentoDeFalha:
    """
    Com oito fontes, uma indisponível zerava a coleta de todas as outras: o runner
    fazia `raise SystemExit` na primeira falha. Agora registra e segue, e o exit
    code final preserva a informação de que houve falha.
    """

    def test_falha_de_um_fluxo_nao_interrompe_os_demais(self, monkeypatch):
        executados = []

        def fake_run_flow(name, command, workdir, timeout_sec=None):
            executados.append(name)
            return (
                run_all_flows.RESULT_FAILURE
                if name == "FINEP"
                else run_all_flows.RESULT_SUCCESS
            )

        monkeypatch.setattr(run_all_flows, "run_flow", fake_run_flow)
        monkeypatch.setattr(run_all_flows, "refresh_edital_status", lambda workdir: None)

        exit_code = run_all_flows.main([])

        assert len(executados) == len(run_all_flows.FLOW_COMMANDS)
        assert exit_code == 1, "a falha precisa aparecer no exit code"

    def test_apenas_atencao_nao_falha_a_execucao(self, monkeypatch):
        monkeypatch.setattr(
            run_all_flows,
            "run_flow",
            lambda *a, **k: run_all_flows.RESULT_WARNING,
        )
        monkeypatch.setattr(run_all_flows, "refresh_edital_status", lambda workdir: None)
        assert run_all_flows.main([]) == 0

    def test_status_e_realinhado_mesmo_havendo_falha(self, monkeypatch):
        chamado = []
        monkeypatch.setattr(
            run_all_flows, "run_flow", lambda *a, **k: run_all_flows.RESULT_FAILURE
        )
        monkeypatch.setattr(
            run_all_flows, "refresh_edital_status", lambda workdir: chamado.append(True)
        )
        run_all_flows.main([])
        assert chamado, "o realinhamento de status não depende do sucesso dos fluxos"


class TestTetoDeDuracao:
    def test_fluxo_travado_e_encerrado_e_reportado_como_falha(self, tmp_path):
        import sys

        # Processo que escreve e depois dorme muito além do teto.
        codigo = "import sys,time\nprint('inicio', flush=True)\ntime.sleep(30)\nprint('fim', flush=True)"
        return_code, saida = run_all_flows.run_command_capturing_output(
            [sys.executable, "-c", codigo], tmp_path, timeout_sec=0
        )
        assert return_code == run_all_flows.TIMEOUT_RETURN_CODE
        assert "Teto de" in saida
        assert "fim" not in saida, "o processo foi encerrado antes de concluir"

    def test_fluxo_rapido_nao_e_afetado(self, tmp_path):
        import sys

        return_code, saida = run_all_flows.run_command_capturing_output(
            [sys.executable, "-c", "print('ok')"], tmp_path, timeout_sec=60
        )
        assert return_code == 0
        assert "ok" in saida


def write_log(workdir, rows):
    """Monta um flow_processing_log.md com as linhas dadas (mais recente primeiro)."""
    docs_dir = workdir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    header = (
        "# Flow Processing Log\n\n"
        "| Data/Hora | Fluxo | Resultado | Observações |\n"
        "| :-- | :-- | :-- | :-- |\n"
    )
    (docs_dir / "flow_processing_log.md").write_text(
        header + "".join(rows), encoding="utf-8"
    )


def log_row(flow, delta, result="Sucesso"):
    return (
        f"| 2026-07-27 03:00:00 -03:00 | `{flow}` | {result} | "
        f"Registry `x`: 10 -> 10 (delta {delta}); outras notas. |\n"
    )


class TestZeroDeltaStreak:
    def test_counts_consecutive_zero_delta_runs_for_the_flow(self, tmp_path):
        write_log(tmp_path, [log_row("FINEP", 0), log_row("FINEP", 0), log_row("FINEP", 3)])
        assert run_all_flows.count_zero_delta_streak(tmp_path, "FINEP") == 2

    def test_stops_at_the_first_run_that_collected_something(self, tmp_path):
        write_log(tmp_path, [log_row("FINEP", 2), log_row("FINEP", 0)])
        assert run_all_flows.count_zero_delta_streak(tmp_path, "FINEP") == 0

    def test_ignores_rows_of_other_flows(self, tmp_path):
        write_log(tmp_path, [log_row("CNPQ", 0), log_row("FINEP", 0), log_row("CNPQ", 0)])
        assert run_all_flows.count_zero_delta_streak(tmp_path, "FINEP") == 1

    def test_returns_zero_when_log_is_absent(self, tmp_path):
        assert run_all_flows.count_zero_delta_streak(tmp_path, "FINEP") == 0


class TestResolveResult:
    def test_failure_wins_over_every_other_signal(self):
        assert (
            run_all_flows.resolve_result("FINEP", 1, 5, 0, FlowStats(36, 5))
            == run_all_flows.RESULT_FAILURE
        )

    def test_source_returning_no_raw_item_is_a_warning_not_success(self):
        """Foi assim que a queda da FINEP passou meses reportada como Sucesso."""
        assert (
            run_all_flows.resolve_result("FINEP", 0, 0, 1, FlowStats(0, 0))
            == run_all_flows.RESULT_WARNING
        )

    def test_no_new_editais_but_healthy_source_is_success(self):
        assert (
            run_all_flows.resolve_result("FINEP", 0, 0, 1, FlowStats(36, 0))
            == run_all_flows.RESULT_SUCCESS
        )

    def test_proven_healthy_source_overrides_a_long_zero_delta_streak(self):
        """
        Em 2026-07-31, 6 dos 7 fluxos saíram como Atenção. FINEP e CNPq estavam
        provadamente saudáveis (36 e 9 itens brutos) e foram marcados só pela
        sequência de deltas zero. Alerta que dispara sempre não informa nada.
        """
        streak = run_all_flows.ZERO_DELTA_ALERT_THRESHOLD * 3
        assert (
            run_all_flows.resolve_result("FINEP", 0, 0, streak, FlowStats(36, 0))
            == run_all_flows.RESULT_SUCCESS
        )

    def test_empty_source_is_a_warning_even_on_the_first_occurrence(self):
        assert (
            run_all_flows.resolve_result("FINEP", 0, 0, 1, FlowStats(0, 0))
            == run_all_flows.RESULT_WARNING
        )

    def test_long_zero_delta_streak_without_stats_is_a_warning(self):
        streak = run_all_flows.ZERO_DELTA_ALERT_THRESHOLD
        assert (
            run_all_flows.resolve_result("CNPQ", 0, 0, streak, None)
            == run_all_flows.RESULT_WARNING
        )

    def test_short_zero_delta_streak_is_still_success(self):
        assert (
            run_all_flows.resolve_result("CNPQ", 0, 0, 2, None)
            == run_all_flows.RESULT_SUCCESS
        )

    def test_low_volume_flows_are_exempt_from_the_streak_rule(self, monkeypatch):
        monkeypatch.setattr(run_all_flows, "LOW_VOLUME_FLOWS", frozenset({"cnpq"}))
        streak = run_all_flows.ZERO_DELTA_ALERT_THRESHOLD + 5
        assert (
            run_all_flows.resolve_result("CNPQ", 0, 0, streak, None)
            == run_all_flows.RESULT_SUCCESS
        )


class TestBuildObservations:
    def test_reports_raw_count_and_flags_empty_source(self):
        result, observations = run_all_flows.build_observations(
            "FINEP",
            {"finep": 10},
            {"finep": 10},
            175,
            [],
            0,
            stats=FlowStats(raw_count=0, new_count=0),
            zero_delta_streak=1,
        )
        assert result == run_all_flows.RESULT_WARNING
        assert "Origem devolveu 0 itens brutos" in observations
        assert "verificar se o portal mudou" in observations

    def test_healthy_run_stays_successful(self):
        result, observations = run_all_flows.build_observations(
            "FINEP",
            {"finep": 10},
            {"finep": 36},
            201,
            [],
            0,
            stats=FlowStats(raw_count=36, new_count=26),
            zero_delta_streak=0,
        )
        assert result == run_all_flows.RESULT_SUCCESS
        assert "(delta 26)" in observations


@pytest.mark.parametrize(
    "line, expected",
    [
        ("| ts | `FINEP` | Sucesso | Registry (delta 0); |", ("FINEP", "Registry (delta 0);")),
        ("| :-- | :-- | :-- | :-- |", None),
        ("texto solto", None),
        ("| incompleto |", None),
    ],
)
def test_parse_log_row(line, expected):
    assert run_all_flows._parse_log_row(line) == expected


class TestIndiceDeRecusadosPersiste:
    """
    O índice de recusados existe para não repetir OCR (ver src/rejection_store.py),
    mas o passo de commit do workflow só adicionava `registry/processed_editais.json`.
    O runner reescrevia `registry/rejected_editais.json` a cada noite e o descartava
    junto com o container: o arquivo não mudava desde 2026-07-31 e os mesmos editais
    recusados tinham PDF baixado e OCR refeito toda madrugada.
    """

    @pytest.mark.parametrize(
        "workflow", ["run_scraper.yml", "run_horizon_weekly.yml"]
    )
    def test_workflow_versiona_o_indice_de_recusados(self, workflow):
        from pathlib import Path

        from src import rejection_store

        repo_root = Path(__file__).resolve().parents[2]
        conteudo = (repo_root / ".github/workflows" / workflow).read_text(
            encoding="utf-8"
        )
        linha_add = next(
            linha for linha in conteudo.splitlines() if linha.strip().startswith("git add")
        )
        alvos = linha_add.split("git add", 1)[1].split("||")[0].split()

        # Staging do diretório inteiro cobre qualquer arquivo do registry; um
        # caminho específico precisa nomear o índice de recusados.
        indice = rejection_store.DEFAULT_PATH  # registry/rejected_editais.json
        assert "registry" in alvos or indice in alvos, (
            f"{workflow} não versiona {indice}: as recusas se perdem e o OCR se repete."
        )

    def test_main_poda_as_recusas_vencidas(self, monkeypatch):
        chamadas = []

        monkeypatch.setattr(
            run_all_flows, "run_flow", lambda *a, **k: run_all_flows.RESULT_SUCCESS
        )
        monkeypatch.setattr(run_all_flows, "refresh_edital_status", lambda workdir: None)
        monkeypatch.setattr(
            run_all_flows,
            "purge_expired_rejections",
            lambda workdir: chamadas.append(workdir),
        )

        assert run_all_flows.main([]) == 0
        assert len(chamadas) == 1, "a poda precisa rodar uma vez por execução"

    def test_poda_remove_apenas_o_que_venceu(self, tmp_path):
        import json
        from datetime import date, timedelta

        hoje = date.today()
        indice = tmp_path / "registry" / "rejected_editais.json"
        indice.parent.mkdir(parents=True)
        indice.write_text(
            json.dumps(
                {
                    "fapes": {
                        "https://exemplo.test/vencido": {
                            "motivo": "prazo encerrado",
                            "valida_ate": (hoje - timedelta(days=1)).isoformat(),
                        },
                        "https://exemplo.test/vigente": {
                            "motivo": "prazo encerrado",
                            "valida_ate": (hoje + timedelta(days=3)).isoformat(),
                        },
                    }
                }
            ),
            encoding="utf-8",
        )

        assert _purge_real(tmp_path) == 1

        restante = json.loads(indice.read_text(encoding="utf-8"))
        assert list(restante["fapes"]) == ["https://exemplo.test/vigente"]
