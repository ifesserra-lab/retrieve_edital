from pytest_bdd import scenarios, given, when, then

scenarios("../../docs/features/load_editais.feature")

@given('a list in memory containing N validated Edital domain objects')
def list_in_memory():
    pass

@when('the Sink component is triggered for Load')
def sink_triggered_for_load():
    pass

@then('N separate files named "edital_[ID].json" should be created')
def json_files_created():
    pass

@then('each separate JSON must strictly contain the following keys:')
def check_json_keys(datatable):
    pass

@given('an older JSON file for a specific edital already exists on disk')
def older_json_exists():
    pass

@when('the pipeline successfully loads new updates for that edital')
def pipeline_loads_new_updates():
    pass

@then('the specific older JSON file should be safely overwritten')
def file_overwritten():
    pass

@then('the new JSON stored on disk should reflect only the newly extracted valid data')
def new_json_stored():
    pass
