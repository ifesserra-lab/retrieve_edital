Feature: Carga dos Dados dos Editais em JSON (Sink)
  Como o destino (Sink) do pipeline ETL
  Eu quero salvar os objetos de editais já validados
  Para que gerem estritamente um arquivo JSON formatado como requisito central

  Scenario: Gerar payload de JSON obrigatório
    Given uma lista em memória contendo N objetos de Domínio (Editais Transformados) e validados
    When o componente `Sink` for acionado para realizar o "Load"
    Then um arquivo chamado "editais_consolidados.json" (ou similar) deve ser criado
    And cada item no JSON deve conter estritamente as chaves: "nome do edital", "órgão de fomento", "cronograma", "descrição" e "categoria"

  Scenario: Evitar duplicidade de arquivos antigos
    Given que já existe um arquivo JSON de extrações anteriores no disco
    When o pipeline realizar uma carga bem-sucedida de novos editais
    Then o arquivo JSON anterior deve ser sobrescrito (ou feito backup de acordo com a regra definida na implementação)
    And o novo JSON armazenado em disco refletirá apenas dados válidos recém-extraídos
