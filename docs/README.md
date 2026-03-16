# Documentação do Projeto

Este diretório contém a documentação do projeto `retrieve_edital`: extração e normalização de editais (FAPES e FINEP) com arquitetura ETL Source → Transform → Sink.

## Índice de Documentos

### Arquitetura e Fluxos
- [Arquitetura ETL (System Design Document)](etl_architecture.md)
  - Padrão T-Shape, fluxos **FAPES** e **FINEP**, componentes (Sources, EditalNormalizer, Sink), configuração (`REFERENCE_YEAR`), extensões do modelo (`raw_cronograma`, `raw_tags`, `raw_anexos`) e categorização Mistral para FINEP.
- [Source FINEP](finep_source.md)
  - FinepSource: listagem, página de detalhe, descrição/cronograma/tags/anexos, variável de ano, uso via `ingest_finep_flow`, categorização Mistral.

### Regras e Desenvolvimento
- [Diretrizes de Desenvolvimento S.O.L.I.D](development_guidelines.md)
  - Premissas do repositório (OOP, Clean Code, anti-padrões).
- [Agentes e Skills](agents_and_skills.md)
  - Definição do agente e skills instaladas (agile-product-owner, gitflow, BDD, clean-code, SOLID, etc.).

### Ágil e Produto
- [Product Backlog](backlog.md)
  - Epics, User Stories e Tasks; link para Issues no GitHub.

### Testes (BDD)
Features Gherkin como contrato e Definition of Done:
- [Extração (Extract)](features/extract_editais.feature)
- [Transformação (Transform)](features/transform_editais.feature)
- [Persistência (Load/Sink)](features/load_editais.feature)
- [Enriquecimento](features/enrich_editais.feature)

## Resumo das modificações recentes

- Novo **Source FINEP** com extração por página de detalhe (descrição, cronograma, Tema(s)→tags, tabela Documentos→anexos).
- **Fluxo** `ingest_finep_flow` (primeira página por padrão; `--all` para todas).
- **Config** `get_reference_year()` e variável `REFERENCE_YEAR` para filtro de prazo FINEP (dinâmico: ano atual por padrão).
- **RawEdital**: campos opcionais `raw_cronograma`, `raw_tags`, `raw_anexos`.
- **EditalNormalizer**: mapeamento data publicação → `data_abertura`, prazo envio → `data_encerramento`; para FINEP, categorização via **Mistral** (divulgação de conhecimento / extensão / inovação).
- **MistralExtractionService**: método `categorize_finep_by_description(description)`.
- **Registry (índice de processados)**: `registry/processed_editais.json` com chaves FAPES e FINEP para não reprocessar editais já baixados; `src/processed_store.py` (get_keys_set, add_many, build_index_from_output_dir); fluxos FAPES e FINEP usam o índice e atualizam após o sink.
- **FinepSource**: para de navegar quando todos os editais da página têm prazo em ano anterior ao de referência; suporte a `processed_urls` para pular chamadas já processadas. **Paginação** por clique nos números das páginas (1, 2, 3, …), com fallback por URL (`limitstart`) se não houver link numérico.
- **Mistral**: retry com backoff exponencial em caso de 429 (rate limit); todas as chamadas (upload, OCR, chat) e classificadores envolvidos em `_call_with_rate_limit_retry`.
- **Convenção**: anexos e diretrizes não são considerados editais (não persistem em `data/output`).
- **Testes**: `tests/step_defs/test_finep_source.py` valida filtro por prazo e parada de paginação quando não há editais com prazo ≥ ano corrente.
