from pytest_bdd import scenarios, given, when, then, parsers
from src.domain.models import RawEdital, EditalDomain
from src.components.transforms.edital_normalizer import EditalNormalizer
from unittest.mock import MagicMock
import pytest

scenarios("../../docs/features/transform_editais.feature")

@pytest.fixture
def context():
    return {"raw_data": None, "transform_engine": None, "result": None, "error": None, "raw_editais": []}

@given('the Transformation engine is ready to receive raw data dictionaries')
def transform_engine_ready(context):
    mock_service = MagicMock()
    context["transform_engine"] = EditalNormalizer(extraction_service=mock_service)
    context["normalizer"] = context["transform_engine"]

@given(parsers.parse('a raw edital record with title "{raw_title}" and agency "{raw_agency}"'))
def raw_edital_record(context, raw_title, raw_agency):
    context["raw_data"] = RawEdital(
        title=raw_title,
        url="http://mock.com",
        raw_agency=raw_agency
    )

@when('the Transform component processes the record')
def transform_processes_record(context):
    try:
        context["result"] = context["transform_engine"].process(context["raw_data"])
    except Exception as e:
        context["error"] = e

@then(parsers.parse('the title should be normalized to "{clean_title}"'))
def title_normalized(context, clean_title):
    assert context["result"].nome == clean_title

@then(parsers.parse('the funding agency should be standardized to "{clean_agency}"'))
def agency_standardized(context, clean_agency):
    assert context["result"].orgão_fomento == clean_agency

@then('it should return a valid Edital domain object')
def valid_edital_domain_object(context):
    assert isinstance(context["result"], EditalDomain)

@given('a raw edital contains the description "Apoio a projetos de extensão tecnológica"')
def raw_edital_with_description(context):
    context["raw_data"] = RawEdital(
        title="Valid Title",
        url="http://mock.com",
        raw_description="Apoio a projetos de extensão tecnológica"
    )
    if not context.get("transform_engine"):
        context["transform_engine"] = EditalNormalizer()

@then('the business logic should classify and set the "category" field as "Extensão"')
def category_is_extensao(context):
    assert context["result"].categoria == "extensão"

@given('a raw record failed extraction and has an empty title')
def record_empty_title(context):
    context["raw_data"] = RawEdital(
        title="",
        url="http://mock.com"
    )
    if not context.get("transform_engine"):
        context["transform_engine"] = EditalNormalizer()

@when('the Transform component attempts validation')
def transform_attempts_validation(context):
    try:
        context["result"] = context["transform_engine"].process(context["raw_data"])
    except ValueError as e:
        context["error"] = e

@then('a validation error should occur')
def validation_error_occurs(context):
    assert isinstance(context["error"], ValueError)

@then('the record should be explicitly dropped from the pipeline')
def record_dropped(context):
    # Validation error ensures dropping
    assert context.get("result") is None
