Feature: Transformação e Limpeza de Dados de Editais (Transform)
  Como um processo de normalização no pipeline ETL
  Eu quero processar a base bruta de editais raspados
  Para garantir que eles obedeçam ao contrato de dados estruturados e regras de negócio

  Scenario: Normalizar dados de um edital válido
    Given que existe um registro de edital bruto contendo "  EDITAL FAPES N 01/2026  "
    And o órgão de fomento original é descrito de forma irregular
    When o componente `Transform` processa este registro
    Then os espaços em branco extras do título devem ser removidos e ele deve estar padronizado
    And o órgão de fomento deve ser normalizado para "FAPES"
    And deve ser retornado um modelo de edital válido (Domain)

  Scenario: Extração da categoria do edital a partir do texto
    Given que o edital bruto contém a descrição "Apoio a projetos de extensão tecnológica"
    When o componente `Transform` processa o registro
    Then a lógica de negócio deve classificar e construir a "categoria" como "Extensão" baseada no texto

  Scenario: Invalidação de edital sem nome
    Given que um registro bruto falhou ao ser extraído e não contém título (None ou vazio)
    When o componente `Transform` tenta validar o dado
    Then um erro de validação (ou descarte silencioso explícito) deve ocorrer
    And o registro não deve ser passado para a próxima etapa do pipeline
