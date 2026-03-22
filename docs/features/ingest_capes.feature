Feature: Ingestão de Editais CAPES
  As an ETL pipeline
  I want to extract editais and results from the CAPES portal
  So that CAPES notices can be normalized and persisted without reprocessing duplicates

  Scenario: Extract CAPES edital entries from the official listing
    Given the CAPES page lists edital and resultado links
    When the CAPES source reads the listing page
    Then it should collect raw edital entries with title and detail URL
    And the extracted CAPES raw list should not be empty

  Scenario: Ignore CAPES entries already present in the processed registry
    Given the processed registry already contains a CAPES detail URL
    When the CAPES source reads the listing page
    Then it should skip the CAPES edital already present in the registry

  Scenario: Ignore CAPES editais whose end date is earlier than the current year
    Given the CAPES source identifies an edital with end date earlier than the current year
    When the CAPES source evaluates the edital
    Then it should discard the CAPES edital from the extracted list

  Scenario: Persist CAPES editais through a dedicated flow
    Given the CAPES source returns new raw editais
    When the CAPES ingest flow runs successfully
    Then it should write normalized CAPES editais to the sink
    And it should register the processed CAPES detail URLs in the processed registry
