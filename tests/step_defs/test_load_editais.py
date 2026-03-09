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
    output_dir = tmp_path / "data" / "output"
    yield str(output_dir)

@pytest.fixture
def context():
    return {"sink": None, "editais": [], "expected_files": []}

@given('a list in memory containing N validated Edital domain objects')
def list_in_memory(context):
    context["editais"] = [
        EditalDomain(
            nome="Edital de Pesquisa X",
            orgão_fomento="FAPES",
            cronograma=[{"evento": "Inscrição", "data": "2025-01-01"}],
            link="http://mocked",
            descrição="Mock description",
            categoria="pesquisa",
            status="aberto",
            data_abertura="2025-01-10",
            data_encerramento="2025-03-31",
            tags=["pesquisa"]
        ),
        EditalDomain(
            nome="Edital de Inovação Y",
            orgão_fomento="FAPES",
            cronograma=[],
            link="http://mocked2",
            descrição="Mock description 2",
            categoria="inovação",
            status="aberto",
            data_abertura="",
            data_encerramento="",
            tags=["inovação"]
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
    
    context["expected_files"] = []
    for item in context["editais"]:
        expected_filename = context["sink"]._sanitize_filename(item.nome).replace(' ', '_').lower() + ".json"
        assert expected_filename in created_files
        context["expected_files"].append(os.path.join(temp_output_dir, expected_filename))

@then('each separate JSON must strictly contain the following keys:')
def check_json_keys(context, datatable):
    expected_keys = {"nome", "descrição", "orgão_fomento", "categoria", "status", "data_abertura", "data_encerramento", "link", "cronograma", "tags"}
    
    for filepath in context["expected_files"]:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert set(data.keys()) == expected_keys

@given('an older JSON file for a specific edital already exists on disk')
def older_json_exists(context, temp_output_dir):
    context["sink"] = LocalJSONSink(output_dir=temp_output_dir)
    os.makedirs(temp_output_dir, exist_ok=True)
    
    older_edital = EditalDomain(
        nome="Edital Atualizacao",
        orgão_fomento="FAPES",
        cronograma=[],
        link="http://mocked3",
        descrição="Descricao VELHA",
        categoria="outros",
        status="aberto",
        data_abertura="",
        data_encerramento="",
        tags=[]
    )
    context["sink"].write([older_edital])
    
    context["editais"] = [
        EditalDomain(
            nome="Edital Atualizacao",
            orgão_fomento="FAPES",
            cronograma=[],
            link="http://mocked3",
            descrição="Descricao NOVA E ATUALIZADA",
            categoria="outros",
            status="aberto",
            data_abertura="",
            data_encerramento="",
            tags=[]
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
        assert data["descrição"] == "Descricao NOVA E ATUALIZADA"
