Feature: Extração de Editais (Source)
  Como um sistema de engenharia de dados
  Eu quero raspar os editais do site da FAPES usando Playwright
  Para construir a base bruta de informações de financiamento

  Scenario: Extrair lista de editais abertos com sucesso
    Given que o site da FAPES "https://fapes.es.gov.br/editais-abertos" está acessível
    When o scraper do Playwright acessa a página de editais
    Then ele deve identificar os elementos HTML que contêm os editais
    And deve extrair uma lista de dados brutos contendo título, link e outras descrições básicas
    And a lista retornada não deve ser vazia

  Scenario: Lidar com paginação no site de editais
    Given que existem múltiplas páginas de editais abertos
    When o scraper extrai os dados da primeira página
    And há um botão de "Próxima Página"
    Then o scraper deve clicar no botão
    And deve continuar a extração até que não haja mais páginas disponíveis
    And deve concatenar todos os resultados iterados

  Scenario: Tratamento de erro de conexão
    Given que a rede está indisponível ou o site demora a responder
    When o scraper tenta acessar a url do site
    Then o sistema deve capturar uma exceção de timeout ou falha de conexão
    And deve registrar o erro detalhado nos logs
    And não deve quebrar a execução global do pipeline silenciosamente
