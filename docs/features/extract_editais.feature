Feature: Extração de Editais (Source)
  As a data engineering system
  I want to scrape public notices (editais) from the FAPES website
  So that I can build a raw funding information database

  Background:
    Given the FAPES website at "https://fapes.es.gov.br/editais-abertos" is accessible
    And the Playwright scraping engine is initialized

  Scenario: Successfully extract a list of open editais
    When the scraper navigates to the open editais page
    Then it should identify the HTML containers holding the editais
    And it should extract a raw list containing title and hyperlink
    And the extracted list should not be empty

  Scenario: Handle pagination across multiple pages
    Given there are multiple pages of open editais available
    When the scraper processes the first page
    And clicks the "Next Page" button
    Then it should continue extraction until no more pages are available
    And all iterations should be concatenated into a single raw list

  Scenario Outline: Network and connection error handling
    Given the network condition is "<condition>"
    When the scraper attempts to access the URL
    Then the system should catch a "<error_type>" exception
    And it should log the detailed error without crashing the pipeline

    Examples:
      | condition       | error_type       |
      | offline         | ConnectionError  |
      | high latency    | TimeoutException |
