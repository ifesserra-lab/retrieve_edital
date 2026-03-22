Feature: Ingestão de Editais CONIF
  As an ETL pipeline
  I want to extract editais from the CONIF portal
  So that only current-year editais are ingested and previously processed items are skipped

  Scenario: Extract only current-year editais from the CONIF listing
    Given the CONIF portal lists editais grouped by publication year
    When the CONIF source reads the listing page
    Then it should collect only editais from the current year
    And each extracted item should include title and detail URL

  Scenario: Load the main edital PDF from the CONIF detail page
    Given a CONIF edital detail page contains the main edital PDF and attachments
    When the CONIF source extracts the detail page
    Then it should download the main edital PDF bytes
    And it should keep the detail URL as the edital link
    And it should include every PDF from the detail page in the edital attachments

  Scenario: Ignore CONIF editais already present in the processed registry
    Given the processed registry already contains a CONIF edital detail URL
    When the CONIF source reads the listing page
    Then it should skip the edital already present in the registry

  Scenario: Persist new CONIF editais and update the processed registry
    Given the CONIF source returns new raw editais
    When the CONIF ingest flow runs successfully
    Then it should write the normalized CONIF editais to the sink
    And it should register the processed CONIF detail URLs in the processed registry
