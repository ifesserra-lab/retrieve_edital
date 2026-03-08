Feature: Carga dos Dados dos Editais em JSON (Sink)
  As the destination (Sink) of the ETL pipeline
  I want to save the validated edital objects
  So that a strictly formatted JSON file is generated as the primary requirement

  Background:
    Given a list in memory containing N validated Edital domain objects

  Scenario: Generate the mandatory JSON payload
    When the Sink component is triggered for Load
    Then a file named "editais_consolidados.json" should be created
    And each item in the JSON must strictly contain the following keys:
      | Field            |
      | nome do edital   |
      | órgão de fomento |
      | cronograma       |
      | descrição        |
      | categoria        |

  Scenario: Prevent duplication of legacy files
    Given an older JSON file from previous extractions exists on disk
    When the pipeline successfully loads new editais
    Then the older JSON file should be safely overwritten
    And the new JSON stored on disk should reflect only the newly extracted valid data
