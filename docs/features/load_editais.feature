Feature: Carga dos Dados dos Editais em JSON (Sink)
  As the destination (Sink) of the ETL pipeline
  I want to save the validated edital objects
  So that a separate, strictly formatted JSON file is generated for each edital

  Background:
    Given a list in memory containing N validated Edital domain objects

  Scenario: Generate the mandatory JSON payload per edital
    When the Sink component is triggered for Load
    Then N separate files named "edital_[ID].json" should be created
    And each separate JSON must strictly contain the following keys:
      | Field            |
      | nome do edital   |
      | órgão de fomento |
      | cronograma       |
      | descrição        |
      | categoria        |

  Scenario: Prevent duplication of legacy files per edital
    Given an older JSON file for a specific edital already exists on disk
    When the pipeline successfully loads new updates for that edital
    Then the specific older JSON file should be safely overwritten
    And the new JSON stored on disk should reflect only the newly extracted valid data
