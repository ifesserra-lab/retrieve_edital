Feature: PDF Data Extraction and Enrichment
  As a data pipeline orchestrator
  I want to parse the downloaded PDF files of the editais
  So that I can extract rich metadata like the exact Description/Objetivo and the Schedule/Cronograma table

  Scenario: Extracting the Objective text from an Edital PDF
    Given the pipeline has downloaded the raw bytes of an Edital PDF
    And the PDF contains a section matching "1. OBJETO"
    When the Transform engine parses the document text
    Then it should extract the semantic objective text falling immediately under the header
    And it should set this text as the "descricao" field of the EditalDomain

  Scenario: Extracting the Schedule table from an Edital PDF
    Given the pipeline has downloaded the raw bytes of an Edital PDF
    And the PDF contains a section matching "CRONOGRAMA" with a visible table
    When the Transform engine processes the tables in the document
    Then it should map the "Etapa" and "Previsão" columns to the "cronograma" list of dictionaries format
    And the cronograma list should not be empty

  Scenario: Handling PDFs that miss expected extraction blocks
    Given the pipeline has downloaded an Anexo PDF with structural anomalies
    When the Transform engine attempts to find the "OBJETO" or "CRONOGRAMA" bounds
    Then the engine should gracefully fallback to empty descriptions or empty schedule lists without aborting
