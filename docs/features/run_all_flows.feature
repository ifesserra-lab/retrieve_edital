Feature: Runner unificado com todos os fluxos
  As an ETL operator
  I want to execute all supported flows from a single runner
  So that the workflow automation can process every source consistently

  Scenario: Execute runner with CAPES and CNPq included
    Given dedicated flows exist for FAPES, FINEP, CONIF, CAPES and CNPq
    When the unified runner executes the configured flow sequence
    Then it should invoke all five flows in the expected order

  Scenario: Stop the runner when any integrated flow fails
    Given one integrated flow exits with a non-zero status
    When the unified runner processes the flow sequence
    Then it should stop execution and return an error

  Scenario: Append processing log entries for newly integrated flows
    Given the unified runner executes CAPES and CNPq successfully
    When the runner appends operational logs
    Then the processing log should contain rows for CAPES and CNPq
