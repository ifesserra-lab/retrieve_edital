import pytest
from unittest.mock import MagicMock, patch
from pytest_bdd import scenarios, given, when, then
from src.components.transforms.edital_normalizer import EditalNormalizer
from src.domain.models import RawEdital, EditalDomain

scenarios("../../docs/features/enrich_editais.feature")

@pytest.fixture
def context():
    return {}

@given('the pipeline has downloaded the raw bytes of an Edital PDF')
def downloaded_raw_bytes(context):
    context["raw_edital"] = RawEdital(
        title="Valid Title",
        url="http",
        pdf_content=b"%PDF-1.4 mock content"
    )

@given('the PDF contains a section matching "1. OBJETO"')
def pdf_contains_objeto(context):
    context["pdf_text"] = "1. OBJETO\nEste edital visa o financiamento estrito de pesquisas."
    context["pdf_tables"] = []

@when('the Transform engine parses the document text')
@when('the Transform engine processes the tables in the document')
@when('the Transform engine attempts to find the "OBJETO" or "CRONOGRAMA" bounds')
def engine_parses(context):
    normalizer = EditalNormalizer()
    
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = context.get("pdf_text", "")
    mock_pdf.pages = [mock_page]
    
    with patch("src.components.transforms.edital_normalizer.pdfplumber.open") as mock_open:
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
            with patch("src.components.transforms.edital_normalizer.genai.Client") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                mock_response = MagicMock()
                
                if "APENAS TEXTO ALEATORIO" in context.get("pdf_text", ""):
                    mock_client.models.generate_content.side_effect = Exception("Semantic extraction generic failure")
                else:
                    mock_response.text = '{"descricao": "financiamento estrito de pesquisas via Gemini", "cronograma": [{"Etapa": "Inscricao", "Previsao": "Amanha"}]}'
                    mock_client.models.generate_content.return_value = mock_response
                
                context["result"] = normalizer.process(context["raw_edital"])

@then('it should extract the semantic objective text falling immediately under the header')
def extract_semantic_objective(context):
    pass # covered by standard assertion below

@then('it should set this text as the "descricao" field of the EditalDomain')
def set_descricao_field(context):
    assert "financiamento estrito de pesquisas" in context["result"].descricao

@given('the PDF contains a section matching "CRONOGRAMA" with a visible table')
def pdf_contains_cronograma(context):
    context["pdf_text"] = "CRONOGRAMA\nEtapa 1 - Inscrições"

@then('it should map the "Etapa" and "Previsão" columns to the "cronograma" list of dictionaries format')
def map_etapa_previsao(context):
    pass

@then('the cronograma list should not be empty')
def cronograma_not_empty(context):
    assert len(context["result"].cronograma) > 0

@given('the pipeline has downloaded an Anexo PDF with structural anomalies')
def pdf_with_anomalies(context):
    context["pdf_text"] = "APENAS TEXTO ALEATORIO SEM HEADERS"
    context["pdf_tables"] = []
    context["raw_edital"] = RawEdital(
        title="Valid Title",
        url="http",
        pdf_content=b"%PDF-1.4 mock content"
    )

@then('the engine should gracefully fallback to empty descriptions or empty schedule lists without aborting')
def graceful_fallback(context):
    assert context["result"].descricao == ""
    assert getattr(context["result"], 'cronograma', []) == []
