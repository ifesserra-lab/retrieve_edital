from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../../docs/features/transform_editais.feature")

@given('the Transformation engine is ready to receive raw data dictionaries')
def transform_engine_ready():
    pass

@given(parsers.parse('a raw edital record with title "{raw_title}" and agency "{raw_agency}"'))
def raw_edital_record(raw_title, raw_agency):
    pass

@when('the Transform component processes the record')
def transform_processes_record():
    pass

@then(parsers.parse('the title should be normalized to "{clean_title}"'))
def title_normalized(clean_title):
    pass

@then(parsers.parse('the funding agency should be standardized to "{clean_agency}"'))
def agency_standardized(clean_agency):
    pass

@then('it should return a valid Edital domain object')
def valid_edital_domain_object():
    pass

@given('a raw edital contains the description "Apoio a projetos de extensão tecnológica"')
def raw_edital_with_description():
    pass

@then('the business logic should classify and set the "category" field as "Extensão"')
def category_is_extensao():
    pass

@given('a raw record failed extraction and has an empty title')
def record_empty_title():
    pass

@when('the Transform component attempts validation')
def transform_attempts_validation():
    pass

@then('a validation error should occur')
def validation_error_occurs():
    pass

@then('the record should be explicitly dropped from the pipeline')
def record_dropped():
    pass
