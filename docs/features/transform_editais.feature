Feature: Transformação e Limpeza de Dados de Editais (Transform)
  As a normalization process in the ETL pipeline
  I want to process the raw scraped editais
  So that they comply with the data contract and business rules

  Background:
    Given the Transformation engine is ready to receive raw data dictionaries

  Scenario Outline: Normalize valid edital data
    Given a raw edital record with title "<raw_title>" and agency "<raw_agency>"
    When the Transform component processes the record
    Then the title should be normalized to "<clean_title>"
    And the funding agency should be standardized to "<clean_agency>"
    And it should return a valid Edital domain object

    Examples:
      | raw_title                  | raw_agency   | clean_title              | clean_agency |
      |   EDITAL FAPES N 01/2026   | Fapes-ES     | EDITAL FAPES N 01/2026   | FAPES        |
      | Apoio a projetos - CNPQ    | cnpq         | APOIO A PROJETOS - CNPQ  | CNPQ         |

  Scenario: Extract edital category from text description
    Given a raw edital contains the description "Apoio a projetos de extensão tecnológica"
    When the Transform component processes the record
    Then the business logic should classify and set the "category" field as "Extensão"

  Scenario: Invalidate edital without a name
    Given a raw record failed extraction and has an empty title
    When the Transform component attempts validation
    Then a validation error should occur
    And the record should be explicitly dropped from the pipeline
