from scripts import run_all_flows


def test_flow_commands_include_capes_and_cnpq_in_expected_order():
    assert [name for name, _ in run_all_flows.FLOW_COMMANDS] == [
        "FAPES",
        "FINEP",
        "CONIF",
        "PRPPG_IFES",
        "PROEX_IFES",
        "CAPES",
        "CNPQ",
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
    }


def test_main_runs_all_flows_in_sequence(monkeypatch):
    executed = []

    def fake_run_flow(name, command, workdir):
        executed.append((name, command[2]))

    monkeypatch.setattr(run_all_flows, "run_flow", fake_run_flow)

    exit_code = run_all_flows.main()

    assert exit_code == 0
    assert executed == [
        ("FAPES", "src.flows.ingest_fapes_flow"),
        ("FINEP", "src.flows.ingest_finep_flow"),
        ("CONIF", "src.flows.ingest_conif_flow"),
        ("PRPPG_IFES", "src.flows.ingest_prppg_ifes_flow"),
        ("PROEX_IFES", "src.flows.ingest_proex_ifes_flow"),
        ("CAPES", "src.flows.ingest_capes_flow"),
        ("CNPQ", "src.flows.ingest_cnpq_flow"),
    ]
