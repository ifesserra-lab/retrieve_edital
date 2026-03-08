# Retrieve Edital

Este é um agente especializado em fazer o download e raspagem de dados de editais utilizando Python e Playwright.

## Arquitetura ETL

O projeto implementa uma arquitetura **Source, Transform e Sink**:

- **Source (Extract)**: Extrai os dados dos editais da web (ex: site da FAPES), navegando e interagindo com a página usando Playwright.
- **Transform (Transformação)**: Limpa, valida e normaliza os dados extraídos utilizando regras de negócio focadas e orientadas a domínio (Domain-Driven Design).
- **Sink (Load)**: Carrega e exporta obrigatoriamente um arquivo JSON que consolida o `nome do edital`, `órgão de fomento`, `cronograma`, `descrição` e `categoria`.

Consulte a documentação completa em [docs/etl_architecture.md](docs/etl_architecture.md).

## Skills do Agente

O agente utiliza as seguintes *skills* (via pacote `@vercel/skills`):
- Gerenciamento Ágil (`agile-product-owner`)
- Metodologia de versionamento (`gitflow`)
