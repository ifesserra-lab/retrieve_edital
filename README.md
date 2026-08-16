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
| **CONFAP** | `ConfapSource` | Chamadas de cooperação internacional do CONFAP, cofinanciadas por FAPs participantes. HTML estático, prazo e status vêm de campo rotulado do portal | `data/output/*.json` |

> **CONFAP não é o agregador das 26 FAPs.** O PDF de análise
> ([§2.1](docs/analise_portal_ifes_serra.pdf)) o trata como hub que indexaria as
> chamadas de todas as FAPs. O recon de 2026-08-16 mostrou que não: ele publica
> as chamadas **dele** — cooperação internacional com agências estrangeiras,
> cofinanciada por um subconjunto de FAPs. Não há edital próprio da FAPESP ou da
> FAPERJ na listagem. Volume: ~115 chamadas desde 2017, ~13/ano.
>
> Como o IFES Serra é do Espírito Santo, a FAP relevante é a **FAPES**, que já
> tem fluxo próprio. As outras 25 são de outros estados e ficam como baixa
> prioridade.

### Duplicata entre fontes: a original vence

O mesmo edital pode chegar por dois caminhos — a Chamada CONFAP & CDTI 2026-2027
veio pela FAPES, que hospeda as diretrizes e recebe a submissão capixaba, e
também pelo CONFAP, que a republica. A regra está em
[`cross_source_dedup.py`](src/components/transforms/cross_source_dedup.py):

- **Chave canônica** = título normalizado (sem acento, caixa ou pontuação) **+**
  `data_encerramento`. Sem prazo não há chave: deduplicar por título parecido
  apagaria oportunidade real. Edições de anos diferentes têm prazos diferentes e
  não colidem.
- **Agregador chega depois** → é recusado no normalizador, e a recusa entra em
  `registry/rejected_editais.json` com validade. Descartar no sink faria a
  chamada voltar como nova toda noite, pagando coleta para ser jogada fora.
- **Fonte original chega depois** → o sink remove o arquivo do agregador.
- **Duas fontes primárias** → nada é descartado. Não há vencedor definido, e
  escolher um arbitrariamente apagaria dado sem critério.

Hoje o único agregador é o CONFAP (`AGGREGATOR_SOURCES`).

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

## Automação (GitHub Actions)

| Workflow | Arquivo | Quando roda |
|----------|---------|-------------|
| Daily Edital Scraper | `.github/workflows/run_scraper.yml` | diário, 03:00 UTC |
| Weekly Horizon Europe Scraper | `.github/workflows/run_horizon_weekly.yml` | segundas, 04:00 UTC |
| BDD Tests | `.github/workflows/tests.yml` | push/PR em `main` e `development` |

Para executar qualquer um deles na máquina, sem esperar o agendamento, veja
[docs/actions_local.md](docs/actions_local.md) (`act`).

### Mistral só para documento novo

O OCR e o LLM são a parte cara do pipeline. Dois índices em `registry/` evitam
gastá-los duas vezes no mesmo documento, e os oito sources consultam ambos
**antes** de baixar o PDF:

| Índice | O que guarda | Validade |
|--------|--------------|----------|
| `registry/processed_editais.json` | URLs já coletadas e publicadas | permanente |
| `registry/rejected_editais.json` | URLs recusadas pelas regras de publicação | 7 dias (`rejection_store.DEFAULT_TTL_DAYS`) |

A recusa expira de propósito: um edital cujo prazo foi prorrogado, ou cuja
extração passe a funcionar, volta a ser candidato depois da validade. As
entradas vencidas são podadas ao fim de cada execução do runner.

Os dois índices precisam ser versionados para valerem alguma coisa — o passo de
commit adiciona `registry` inteiro. Até 2026-08-16 ele nomeava só o arquivo de
processados, e o índice de recusados era reconstruído e descartado a cada noite:
os mesmos editais tinham PDF baixado e OCR refeito toda madrugada.

### Provedores de extração (Mistral → OpenAI)

A extração tem dois provedores encadeados. A reserva entra **só** quando o
principal recusa a credencial ou a assinatura (401/402/403) — não por qualquer
erro, porque um PDF corrompido falharia nos dois e só duplicaria custo.

| | Principal | Reserva |
|---|---|---|
| Serviço | Mistral | OpenAI |
| Variável | `MISTRAL_API_KEY` | `API_KEY` (ou `OPENAI_API_KEY`) |
| Modelo | `mistral-large-latest` | `OPENAI_MODEL`, padrão `gpt-4o` |
| OCR de PDF | sim (`mistral-ocr-latest`) | **não** — texto via `pdfplumber` |

Configurações possíveis, resolvidas por `build_extraction_service()`:

- **as duas chaves** → Mistral com OpenAI de reserva (recomendado);
- **só `MISTRAL_API_KEY`** → comportamento histórico;
- **só `API_KEY`** → roda inteiro na OpenAI, sem OCR;
- **nenhuma** → erro explícito na construção.

> **A reserva não faz OCR.** A OpenAI recebe o texto que o `pdfplumber` lê da
> camada de texto do PDF. Para edital nativo digital — a grande maioria — o
> resultado é equivalente. Para PDF que é imagem escaneada, o serviço **recusa**
> com `PdfTextNotExtractableError` em vez de mandar um prompt vazio ao modelo:
> um prompt sem texto devolve um edital inventado de aparência plausível, que é
> pior do que falhar. Essa recusa é por documento, não derruba o fluxo.

Os dois provedores compartilham prompt, schema e mapeamento
([`extraction_contract.py`](src/components/transforms/extraction_contract.py)),
para que trocar de provedor não mude o formato do edital gravado.

### Quando o job fica vermelho

O scraper falha de propósito quando **nenhum** provedor de extração responde —
`AllProvidersUnavailableError`, ou `MistralUnavailableError` quando não há
reserva configurada. Isso **não** é resiliência perdida: um PDF problemático, um
PDF escaneado, um portal fora do ar ou um 429 continuam sendo absorvidos por
item. O que mudou é que ficar sem extração alguma derruba o fluxo, em vez de
deixar cada edital virar `None` silenciosamente.

O motivo é concreto: entre 2026-08-10 e 2026-08-16 a Mistral respondeu
`402 Check your subscription` a toda chamada, e os sete jobs diários passaram
verdes com a extração inteiramente morta. Com `API_KEY` configurada, esse mesmo
402 hoje só troca de provedor e a coleta continua; sem ela, o job fica vermelho.

Diante de um job vermelho de extração, verifique a assinatura da Mistral em
<https://admin.mistral.ai/subscription> e a cota da OpenAI. Todas as camadas que
precisam deixar essa falha passar capturam a base comum
`ExtractionUnavailableError` — uma só, em vez de enumerar as exceções de cada
provedor e esquecer de atualizar a lista quando entrar um provedor novo.

O passo de commit roda com `if: always()`, então os editais já coletados pelos
fluxos saudáveis e o `docs/flow_processing_log.md` são preservados na falha.

## Skills do agente

- Gerenciamento ágil (`agile-product-owner`)
- Versionamento (`gitflow`)
