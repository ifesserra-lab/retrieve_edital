import os
import json
import pytest
import shutil
from pytest_bdd import scenarios, given, when, then, parsers
from src.components.sinks.json_sink import LocalJSONSink
from src.domain.models import EditalDomain

scenarios("../../docs/features/load_editais.feature")

@pytest.fixture
def temp_output_dir(tmp_path):
    # tmp_path is a pytest fixture providing a temporary directory unique to the test invocation
    output_dir = tmp_path / "data" / "output"
    yield str(output_dir)
    # Cleanup happens automatically with tmp_path

@pytest.fixture
def context():
    return {"sink": None, "editais": [], "expected_files": []}

@given('a list in memory containing N validated Edital domain objects')
def list_in_memory(context):
    context["editais"] = [
        EditalDomain(
            nome_do_edital="Edital de Pesquisa X",
            orgao_de_fomento="FAPES",
            cronograma=[{"fase": "Inscrição", "data": "2025-01-01"}],
            descricao="Mock description",
            categoria="Pesquisa"
        ),
        EditalDomain(
            nome_do_edital="Edital de Inovação Y",
            orgao_de_fomento="FAPES",
            cronograma=[],
            descricao="Mock description 2",
            categoria="Inovação"
        )
    ]

@when('the Sink component is triggered for Load')
def sink_triggered_for_load(context, temp_output_dir):
    context["sink"] = LocalJSONSink(output_dir=temp_output_dir)
    context["sink"].write(context["editais"])

@then(parsers.parse('N separate files named "{expected_format}" should be created'))
def json_files_created(context, temp_output_dir, expected_format):
    created_files = os.listdir(temp_output_dir)
    assert len(created_files) == len(context["editais"])
    
    for item in context["editais"]:
        # our sanitization lowers and replaces space with underscore
        expected_filename = context["sink"]._sanitize_filename(item.nome_do_edital).replace(' ', '_').lower() + ".json"
        assert expected_filename in created_files
        context["expected_files"].append(os.path.join(temp_output_dir, expected_filename))

@then('each separate JSON must strictly contain the following keys:')
def check_json_keys(context, datatable):
    # datatable is implicitly handled by pytest-bdd as a parameter if typed,
    # but since we didn't inject the datatable parameter strictly in the feature parsing,
    # we can hardcode the expected keys based on EditalDomain.
    # Feature file has:
    # | Key              |
    # | nome_do_edital   |
    # | orgao_de_fomento |
    # | cronograma       |
    # | descricao        |
    # | categoria        |
    expected_keys = {"nome_do_edital", "orgao_de_fomento", "cronograma", "descricao", "categoria"}
    
    for filepath in context["expected_files"]:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert set(data.keys()) == expected_keys

@given('an older JSON file for a specific edital already exists on disk')
def older_json_exists(context, temp_output_dir):
    context["sink"] = LocalJSONSink(output_dir=temp_output_dir)
    os.makedirs(temp_output_dir, exist_ok=True)
    
    # Create fake older edital
    older_edital = EditalDomain(
        nome_do_edital="Edital Atualizacao",
        orgao_de_fomento="FAPES",
        cronograma=[],
        descricao="Descricao VELHA",
        categoria="Outros"
    )
    context["sink"].write([older_edital])
    
    # Store for further steps
    context["editais"] = [
        EditalDomain(
            nome_do_edital="Edital Atualizacao",
            orgao_de_fomento="FAPES",
            cronograma=[],
            descricao="Descricao NOVA E ATUALIZADA",
            categoria="Outros"
        )
    ]
    filename = context["sink"]._sanitize_filename("Edital Atualizacao").replace(' ', '_').lower() + ".json"
    context["target_file"] = os.path.join(temp_output_dir, filename)

@when('the pipeline successfully loads new updates for that edital')
def pipeline_loads_new_updates(context):
    context["sink"].write(context["editais"])

@then('the specific older JSON file should be safely overwritten')
def file_overwritten(context):
    assert os.path.exists(context["target_file"])

@then('the new JSON stored on disk should reflect only the newly extracted valid data')
def new_json_stored(context):
    with open(context["target_file"], 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data["descricao"] == "Descricao NOVA E ATUALIZADA"
