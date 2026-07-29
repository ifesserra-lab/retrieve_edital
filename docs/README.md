# Documentação do Projeto

Este diretório contém a documentação do projeto `retrieve_edital`: extração, normalização e carga incremental de editais com arquitetura ETL Source → Transform → Sink.

## Índice de Documentos

### Arquitetura e Fluxos
- [Arquitetura ETL (System Design Document)](etl_architecture.md)
  - Padrão T-Shape, fluxos **FAPES**, **FINEP**, **CONIF**, **PRPPG/IFES**, **PROEX/IFES**, **CAPES** e **CNPq**, com registry incremental, runner unificado e observabilidade operacional.
- [Source FINEP](finep_source.md)
  - FinepSource: **API Liferay do portal** (OAuth2 + `/o/c/chamadapublicas`), descrição/cronograma/tags/anexos nativos, variável de ano, deduplicação com as chaves do portal antigo, uso via `ingest_finep_flow`. Sem Playwright.
- [Source PROEX/IFES](proex_ifes_source.md)
  - ProexIfesSource: leitura da página pública de editais, filtro pelo bloco do ano corrente, escolha do PDF principal, anexos documentais e fallback com `curl` em respostas `403`.

### Regras e Desenvolvimento
- [Diretrizes de Desenvolvimento S.O.L.I.D](development_guidelines.md)
  - Premissas do repositório (OOP, Clean Code, anti-padrões).
- [Agentes e Skills](agents_and_skills.md)
  - Definição do agente e skills instaladas (agile-product-owner, gitflow, BDD, clean-code, SOLID, etc.).

### Ágil e Produto
- [Product Backlog](backlog.md)
  - Epics, User Stories e Tasks; link para Issues no GitHub.

### Specs de Expansão de Fontes
- 🟢 [Spec e Plano: FINEP, CNPq e Horizon Europe](spec_finep_cnpq_horizon.md)
  - FINEP e CNPq corrigidos, mais o canário anti-falha-silenciosa no runner. Resta **US-HORIZON**, com o dataset bulk do Horizon Europe já mapeado.
- [Source CNPq](cnpq_source.md)
  - CnpqSource: listagem `abertas-para-submissao` no gov.br, período de inscrições com rótulos variáveis, anexos filtrados por caminho e OCR do documento principal.
- [Plano de Execução: Fomento Empresarial](plan_fomento_empresarial.md)
  - Lista de tarefas com checkbox, dependências e critérios de aceite para EMBRAPII, ANEEL, SENAI e BNDES.
- [Spec: Expansão de Fontes de Fomento](spec_expansao_fontes.md)
  - Plano geral derivado da análise de lacunas do Portal IFES Serra: 26 FAPs/CONFAP, fomento empresarial e internacionais; source declarativo por YAML, runner resiliente e novos campos de domínio.
- [Spec: Fomento Empresarial (EMBRAPII, BNDES, ANEEL, ANP, SENAI)](spec_fomento_empresarial.md)
  - Recorte Tier B com **reconhecimento real dos portais em 2026-07-27**: EMBRAPII via RSS, BNDES em WebSphere com portlet instável, ANEEL de baixo volume, ANP descartada como fonte de editais, SENAI em HTML estático.

### Testes (BDD)
Features Gherkin como contrato e Definition of Done:
- [Extração (Extract)](features/extract_editais.feature)
- [Transformação (Transform)](features/transform_editais.feature)
- [Persistência (Load/Sink)](features/load_editais.feature)
- [Enriquecimento](features/enrich_editais.feature)

## Resumo das modificações recentes

- Novo **Source PROEX/IFES** com leitura de `https://proex.ifes.edu.br/editais`, restrição a `Editais abertos` do ano corrente e deduplicação pela URL do PDF principal.
- Novo **Fluxo** `ingest_proex_ifes_flow`.
- **Registry**: nova chave `proex_ifes` em `registry/processed_editais.json`.
- **Runner unificado**: `scripts/run_all_flows.py` agora inclui `PROEX_IFES`.
- **Workflow**: o pipeline diário deve persistir `data/output/`, `registry/processed_editais.json` e `docs/flow_processing_log.md`.
- **Log operacional**: execução do fluxo PROEX/IFES registrada em `docs/flow_processing_log.md`.
- Novo **Source FINEP** com extração por página de detalhe (descrição, cronograma, Tema(s)→tags, tabela Documentos→anexos).
- **Fluxo** `ingest_finep_flow` (primeira página por padrão; `--all` para todas).
- **Config** `get_reference_year()` e variável `REFERENCE_YEAR` para filtro de prazo FINEP (dinâmico: ano atual por padrão).
- **RawEdital**: campos opcionais `raw_cronograma`, `raw_tags`, `raw_anexos`.
- **EditalNormalizer**: mapeamento data publicação → `data_abertura`, prazo envio → `data_encerramento`; para FINEP, categorização via **Mistral** (divulgação de conhecimento / extensão / inovação).
- **MistralExtractionService**: método `categorize_finep_by_description(description)`.
- **Registry (índice de processados)**: `registry/processed_editais.json` com chaves FAPES e FINEP para não reprocessar editais já baixados; `src/processed_store.py` (get_keys_set, add_many, build_index_from_output_dir); fluxos FAPES e FINEP usam o índice e atualizam após o sink.
- **FinepSource** *(reescrito em 2026-07-27)*: consome a **API Liferay do portal** em vez de raspar HTML. O portal antigo passou a redirecionar para uma SPA e o source extraía zero itens desde 2026-03-15. Paginação pela própria API (`page`/`pageSize`, teto de segurança de 50 páginas), filtro de prazo a partir do ano de referência, e `processed_urls` reconhecendo tanto a URL nova quanto a chave do portal antigo. Sem Playwright. Ver [finep_source.md](finep_source.md).
- **Canário anti-falha-silenciosa** (`src/flow_health.py`): fluxos publicam `[flow-stats] raw=N new=M` e o runner passa a distinguir `Sucesso`, `Atenção` (origem devolveu 0 itens brutos, ou 7 execuções seguidas sem novidade) e `Falha`.
- **Mistral**: retry com backoff exponencial em caso de 429 (rate limit); todas as chamadas (upload, OCR, chat) e classificadores envolvidos em `_call_with_rate_limit_retry`.
- **Convenção**: anexos e diretrizes não são considerados editais (não persistem em `data/output`).
- **Testes**: `tests/step_defs/test_finep_source.py` valida filtro por prazo e parada de paginação quando não há editais com prazo ≥ ano corrente.
