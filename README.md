# Retrieve Edital

Agente especializado em download e raspagem de dados de editais (chamadas públicas) usando Python e Playwright. Suporta **FAPES** e **FINEP** com arquitetura ETL desacoplada.

## Arquitetura ETL

O projeto implementa o padrão **Source → Transform → Sink**:

- **Source (Extract)**: Extrai dados brutos da web (Playwright). Ex.: FAPES (múltiplas URLs), FINEP (chamadas abertas + página de detalhe por edital).
- **Transform**: Normaliza, valida e enriquece os dados (regras de negócio, Mistral para PDF/FINEP). Produz objetos de domínio validados.
- **Sink (Load)**: Grava um arquivo JSON por edital em `data/output/` com `nome`, `órgão de fomento`, `cronograma`, `descrição`, `categoria`, `tags`, `anexos`.

Documentação detalhada: [docs/etl_architecture.md](docs/etl_architecture.md).

## Fluxos disponíveis

| Fluxo | Source | Uso | Saída |
|-------|--------|-----|--------|
| **FAPES** | `FapesSource` | Editais FAPES (múltiplas seções), com PDF e Mistral OCR quando disponível | `data/output/*.json` |
| **FINEP** | `FinepSource` | Chamadas públicas FINEP (abertas), uma página de detalhe por chamada; categorização Mistral pela descrição | `data/output/*.json` |
| **CONIF** | `ConifSource` | Editais do portal CONIF, restritos ao ano corrente, com deduplicação por `registry/processed_editais.json` e leitura do PDF principal via Mistral OCR | `data/output/*.json` |

### Como rodar

**Requisitos:** Python 3.12+, dependências em `requirements.txt`, Playwright (`playwright install chromium`). Para categorização FINEP e OCR: `MISTRAL_API_KEY` no `.env`.

```bash
# Instalar dependências
pip install -r requirements.txt
playwright install chromium

# Pipeline FAPES (editais FAPES)
python -m src.flows.ingest_fapes_flow

# Pipeline FINEP (chamadas abertas; por padrão só a 1ª página)
python -m src.flows.ingest_finep_flow

# FINEP — todas as páginas da listagem
python -m src.flows.ingest_finep_flow --all

# Pipeline CONIF (apenas editais do ano corrente)
python -m src.flows.ingest_conif_flow
```

Variável opcional para FINEP: **`REFERENCE_YEAR`** (ano de referência para filtrar por prazo de envio). Ver [docs/finep_source.md](docs/finep_source.md) e `.env.example`.

## O que foi modificado / novidades

- **Novo source FINEP** (`FinepSource`): listagem em [chamadas abertas](http://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta), entrada em cada link de detalhe para extrair descrição, cronograma (data de publicação + prazo de envio), tags (Tema(s)) e anexos (tabela Documentos). Filtro por ano de prazo configurável (`REFERENCE_YEAR` ou construtor).
- **Novo source CONIF** (`ConifSource`): leitura da listagem em `https://portal.conif.org.br/editais`, filtrando apenas URLs com o ano corrente, entrando na página de detalhe, baixando o PDF principal do edital para processamento via Mistral OCR e pulando URLs já registradas em `registry/processed_editais.json`.
- **Configuração de ano** (`src.config`): `get_reference_year()` para uso no filtro de prazos (FINEP).
- **Modelo de domínio** (`RawEdital`): campos opcionais `raw_cronograma`, `raw_tags`, `raw_anexos` para dados já estruturados na página de detalhe (ex.: FINEP).
- **Normalizador**:
  - Mapeamento explícito: data de publicação → `data_abertura`, prazo de envio da proposta → `data_encerramento`.
  - Para editais FINEP: categorização via **Mistral** pela descrição em uma de: **divulgação de conhecimento**, **extensão**, **inovação**.
- **Mistral** (`MistralExtractionService`): novo método `categorize_finep_by_description(description)` para classificar FINEP.
- **Novo fluxo** `ingest_finep_flow`: orquestra Source FINEP + Transform + Sink; parâmetro `max_pages` (ex.: 1 para teste).
- **Documentação**: [docs/finep_source.md](docs/finep_source.md), [docs/agents_and_skills.md](docs/agents_and_skills.md), e este README atualizado.

## Estrutura do repositório

```text
src/
├── core/           # Interfaces ISource, ITransform, ISink
├── config.py       # get_reference_year() (REFERENCE_YEAR)
├── domain/         # RawEdital, EditalDomain
├── components/
│   ├── sources/    # FapesSource, FinepSource
│   ├── transforms/ # EditalNormalizer, date_utils, mistral_client
│   └── sinks/      # LocalJSONSink
└── flows/          # ingest_fapes_flow, ingest_finep_flow, ingest_conif_flow
docs/               # Arquitetura, backlog, features BDD, finep_source, agents_and_skills
data/output/        # JSONs gerados (1 por edital)
```

## Skills do agente

- Gerenciamento ágil (`agile-product-owner`)
- Versionamento (`gitflow`)
