Feature: Ingestão de Chamadas Públicas CNPq
  As an ETL pipeline
  I want to extract public calls from the CNPq portal
  So that CNPq notices can be normalized and persisted without reprocessing duplicates

  Scenario: Extract CNPq chamada entries from the official listing
    Given the CNPq page lists chamadas públicas with links
    When the CNPq source reads the listing page
    Then it should collect raw chamada entries with title and detail URL
    And the extracted CNPq raw list should not be empty

  Scenario: Ignore CNPq entries already present in the processed registry
    Given the processed registry already contains a CNPq detail URL
    When the CNPq source reads the listing page
    Then it should skip the CNPq chamada already present in the registry

  Scenario: Ignore CNPq chamadas whose end date is earlier than the current year
    Given the CNPq source identifies a chamada with end date earlier than the current year
    When the CNPq source evaluates the chamada
    Then it should discard the CNPq chamada from the extracted list

  Scenario: Persist CNPq chamadas through a dedicated flow
    Given the CNPq source returns new raw chamadas
    When the CNPq ingest flow runs successfully
    Then it should write normalized CNPq chamadas to the sink
    And it should register the processed CNPq detail URLs in the processed registry
