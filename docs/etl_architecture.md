# System Architecture: ETL Pipeline de Editais

**Author**: Horizon Project Agent
**Date**: 2026-03-31
**Status**: Approved

## Overview

Este documento descreve a arquitetura ETL do projeto `retrieve_edital`. O sistema extrai editais públicos de múltiplos fomentadores e portais institucionais, normaliza os dados em um formato comum e persiste um arquivo JSON por edital em `data/output/`.

Atualmente o repositório mantém fluxos dedicados para **FAPES**, **FINEP**, **CONIF**, **PRPPG/IFES**, **PROEX/IFES**, **CAPES** e **CNPq**, todos apoiados pelas mesmas interfaces `ISource`, `ITransform` e `ISink`.

## Architecture Diagram

Padrão T-Shape (Source, Transform, Sink); múltiplos Sources podem ser injetados no mesmo Transform e Sink.

```mermaid
graph TB
    subgraph Sources
        A1[FAPES] --> B1[FapesSource]
        A2[FINEP] --> B2[FinepSource]
        A3[CONIF] --> B3[ConifSource]
        A4[PRPPG/IFES] --> B4[PrppgIfesSource]
        A5[PROEX/IFES] --> B5[ProexIfesSource]
        A6[CAPES] --> B6[CapesSource]
        A7[CNPq] --> B7[CnpqSource]
    end

    B1 --> C[EditalNormalizer]
    B2 --> C
    B3 --> C
    B4 --> C
    B5 --> C
    B6 --> C
    B7 --> C
    C -->|OCR / enriquecimento / datas / categoria| D[LocalJSONSink]
    D --> E[(data/output/*.json)]
    D --> F[(registry/processed_editais.json)]
```

## Fluxos (Flows)

| Fluxo | Arquivo | Source | Descrição |
|-------|---------|--------|-----------|
| FAPES | `src/flows/ingest_fapes_flow.py` | `FapesSource` | Editais FAPES em múltiplas seções, com OCR Mistral quando há PDF principal. |
| FINEP | `src/flows/ingest_finep_flow.py` | `FinepSource` | Chamadas abertas via **API Liferay do portal** (OAuth2 + `/o/c/chamadapublicas`), com cronograma, tags, anexos e filtro por ano de prazo. Sem Playwright. |
| CONIF | `src/flows/ingest_conif_flow.py` | `ConifSource` | Editais do ano corrente, com leitura da página de detalhe e OCR do PDF principal. |
| PRPPG_IFES | `src/flows/ingest_prppg_ifes_flow.py` | `PrppgIfesSource` | Editais do SIGPesq/Ifes com paginação ASP.NET, URL estável `?cod=` e download do anexo principal. |
| PROEX_IFES | `src/flows/ingest_proex_ifes_flow.py` | `ProexIfesSource` | Editais abertos da PROEX/IFES, limitados ao ano corrente, com deduplicação pela URL do PDF principal e fallback para `curl` quando o portal retorna `403` a `requests`. |
| CAPES | `src/flows/ingest_capes_flow.py` | `CapesSource` | Editais e resultados da CAPES, com anexos em PDF e filtro por ano corrente/futuro. |
| HORIZON | `src/flows/ingest_horizon_flow.py` | `HorizonSource` | Chamadas abertas do Horizon Europe (inclui o EIC) a partir do dataset bulk público, com filtro temático obrigatório por divisão. Cadência semanal, fora do runner diário. |
| CNPQ | `src/flows/ingest_cnpq_flow.py` | `CnpqSource` | Chamadas abertas para submissão no **portal do gov.br** (Plone estático), com página de detalhe, período de inscrições, anexos e OCR do documento principal. |

## Configuração global

- `src/config.py`: `get_reference_year(override)` para fontes que filtram por ano de referência.
- Cronograma: quando há OCR, o cronograma da fonte é **unido** ao extraído do PDF, com a fonte tendo precedência em caso de mesmo evento. `data_abertura` e `data_encerramento` são derivadas do resultado, com precedência `abertura das inscrições` > `publicação` > primeira data. Nenhuma data é inventada: sem etapa datada, o campo sai vazio.
- `src/flow_health.py`: sinais de saúde dos fluxos — os fluxos publicam a contagem bruta pelo stdout (`[flow-stats] raw=N new=M`) e o runner usa esse número para distinguir **"o portal não publicou nada"** de **"o source quebrou"**. Antes disso, as duas situações apareciam no log como `Sucesso, delta 0`, o que manteve as quedas da FINEP e do CNPq invisíveis por meses.
- `.env`: `MISTRAL_API_KEY` para OCR e extrações estruturadas via Mistral.
- `registry/processed_editais.json`: índice de editais já processados por source (`fapes`, `finep`, `conif`, `prppg_ifes`, `proex_ifes`, `capes`, `cnpq`, `horizon`).
- `src/components/transforms/publication_rules.py`: decide o que é oportunidade publicável e mantém os campos de filtro em vocabulário fechado. Descarta anexo/alteração solto, registro sem conteúdo extraído e prazo já encerrado; canoniza `status` em `aberto`/`encerrado` e `categoria` em `divulgação de conhecimento`, `extensão`, `inovação`, `pesquisa` ou `outros`. Resolve também `modalidade`, hoje limitada a marcar `fluxo-contínuo` quando a origem declara ou o texto do edital diz — o que distingue "aberto permanentemente" de "prazo desconhecido", antes indistinguíveis com `data_encerramento` vazio.
- `scripts/curate_output.py`: cuida do acervo já gravado — realinha `status` ao prazo, canoniza `categoria` e preenche `orgão_fomento` pelo host do link (o runner chama a cada execução) e, com `--apply`, remove o que não é edital.
- Campos da prioridade 6 do PDF de análise, em `EditalDomain`: `publico_alvo`, `ambito_geografico`, `modalidade`, `valor_estimado`, `trl_exigido` e `fonte_key`.
  - `ambito_geografico` e `fonte_key` vêm do perfil da fonte (`SOURCE_PROFILES`) — conhecimento estático e certo. A origem pode sobrepor o âmbito quando é mais específica, como a FINEP informando a região da chamada.
  - `publico_alvo` só é preenchido com o que a origem declara: a FINEP pela taxonomia `publicoAlvo`, o Horizon pelas divisões (EIC inclui `empresa`). Fonte que não informa fica vazia — inferir do texto produziria rótulo plausível e não verificável.
  - `valor_estimado` e `trl_exigido` existem no schema e ficam vazios: só podem vir do texto do PDF, e ajustar a extração exige avaliá-la contra os documentos que hoje falham.
- `registry/rejected_editais.json`: editais recusados pelas regras de publicação, com motivo e validade de sete dias. Sem ele, um edital recusado volta como novo em toda execução, com PDF baixado e OCR refeito.
- `docs/flow_processing_log.md`: log operacional da última execução de cada fluxo.
- `scripts/run_all_flows.py`: runner unificado. Aceita `--only FINEP,CNPQ` para execução seletiva e `--timeout` para o teto de duração por fluxo (default 20 min).

## Components

### Component 1: Source (Extract)

- **Responsibility**: extrair dados brutos e montar `RawEdital`, sem aplicar regras finais de normalização.
- **Implementações atuais**:
  - `FapesSource`
  - `FinepSource`
  - `ConifSource`
  - `PrppgIfesSource`
  - `ProexIfesSource`
  - `CapesSource`
  - `CnpqSource`

**Destaque PROEX/IFES**:
- lê `https://proex.ifes.edu.br/editais`
- isola o bloco `Editais abertos` do ano corrente
- cria um `RawEdital` por edital
- preserva anexos documentais (`pdf`, `doc`, `docx`, `odt`, etc.)
- escolhe o PDF principal com heurística baseada em rótulos como `Edital` e `Retificação`
- usa fallback com `curl` para listagem e downloads quando o portal ou a AGIFES respondem `403` para `requests`

### Component 2: Transform (Process)

- **Responsibility**: validar e normalizar `RawEdital` em `EditalDomain`.
- **Atribuições principais**:
  - normalização de título e órgão
  - mapeamento de `raw_cronograma` para `cronograma`, `data_abertura` e `data_encerramento`
  - OCR e extração estruturada com Mistral quando `pdf_content` está disponível
  - fallback por descrição/título quando não há extração completa

### Component 3: Sink (Load)

- **Responsibility**: gravar um JSON por edital e manter a saída persistida.
- **Implementação**: `LocalJSONSink`
- **Saída**: `data/output/*.json`

## Data Flow

1. O flow dedicado carrega o conjunto já processado em `registry/processed_editais.json`.
2. O source lê a origem remota e devolve `List[RawEdital]`.
3. `EditalNormalizer` processa os itens em paralelo (`ThreadPoolExecutor(max_workers=2)`).
4. `LocalJSONSink.write()` persiste os `EditalDomain`.
5. O flow registra as chaves processadas no `registry`.
6. O runner unificado atualiza `docs/flow_processing_log.md` quando executado via `scripts/run_all_flows.py`.

## Runner e workflow

- `scripts/run_all_flows.py` executa os fluxos na ordem:
  `FAPES` → `FINEP` → `CONIF` → `PRPPG_IFES` → `PROEX_IFES` → `CAPES` → `CNPQ`.
- O runner captura a saída de cada fluxo e classifica o resultado em três estados:
  - **Sucesso** — a origem respondeu e o fluxo terminou bem (mesmo sem editais novos);
  - **Atenção** — a origem devolveu **zero itens brutos**, ou o fluxo está há `ZERO_DELTA_ALERT_THRESHOLD` (7) execuções seguidas sem nada novo;
  - **Falha** — exit code diferente de zero.
  Fontes de baixo volume declaradas em `LOW_VOLUME_FLOWS` ficam isentas da regra de sequência.
- **Falha de um fluxo não interrompe os demais.** Antes o runner fazia `raise SystemExit` na primeira falha: com oito fontes, uma indisponível zerava a coleta de todas as outras. Agora o erro é registrado, os fluxos seguintes rodam, e o exit code final reflete que houve falha — a informação não se perde. O realinhamento de status roda de todo modo.
- **Teto de duração por fluxo** (`--timeout`, default 20 min). Um fluxo travado — portal pendurado, backoff longo do Mistral — consumia a janela do job inteiro. Ao estourar, o processo é encerrado com exit code 124 e registrado como falha.
- **Sem paralelismo, deliberadamente.** O limite de requisições do Mistral é por chave de API, então rodar fluxos em paralelo multiplicaria os `429` em vez de acelerar. O ganho de tempo viria à custa de mais espera em backoff. Ver [mistral_usage.md](mistral_usage.md).
- **Evidência prevalece sobre proxy**: havendo `[flow-stats]`, a saúde da origem é fato — zero itens brutos é scraper quebrado, qualquer item prova que a origem respondeu. A regra de sequência só vale na ausência desse dado. Os oito fluxos publicam as estatísticas.
- Os parsers de listagem devolvem **tudo** o que a origem trouxe; a comparação com o registry acontece no `read()`. Com a deduplicação dentro do parser, a contagem bruta mediria "quantos são novos" e um portal saudável sem novidade pareceria quebrado.
- `.github/workflows/run_scraper.yml` chama o runner unificado e deve persistir:
  - `data/output/*.json`
  - `registry/processed_editais.json`
  - `docs/flow_processing_log.md`

## Key Design Decisions

### Decision 1: Reuso do núcleo ETL por interfaces

- **Contexto**: cada portal expõe HTML, paginação e anexos de forma diferente.
- **Decisão**: manter `ISource`, `ITransform` e `ISink` como contratos estáveis.
- **Rationale**: novos fomentadores entram como novos sources/flows, sem quebrar a malha principal.

### Decision 2: Deduplicação por chave específica do source

- **Contexto**: nem todo portal oferece uma página de detalhe estável.
- **Decisão**:
  - FAPES: chave pelo basename do arquivo
  - PRPPG/IFES: URL estável `?cod=...`
  - PROEX/IFES: URL do PDF principal do edital
  - demais fontes: permalink ou link principal do item
- **Rationale**: evita reprocessamento mesmo quando a listagem não possui identificador único uniforme.

### Decision 3: Fallback de rede para PROEX/IFES

- **Contexto**: em 2026-03-31 o portal `proex.ifes.edu.br` e links hospedados na AGIFES responderam `403 Forbidden` para `requests`, mas aceitaram `curl -L`.
- **Decisão**: incorporar fallback com `curl` apenas no `ProexIfesSource` para listagem e PDFs.
- **Rationale**: mantém o fluxo funcional sem alterar os demais sources ou exigir browser headless para esse portal estático.

## Technology Stack

- **Linguagem**: Python 3.12+
- **Extração Web**: `requests`, `BeautifulSoup`, `Playwright`, `curl` como fallback pontual na PROEX/IFES
- **Normalização**: Python + `EditalNormalizer`
- **OCR / Enriquecimento**: Mistral
- **Testes**: `pytest`, `pytest-bdd`
- **Automação**: GitHub Actions

## Directory Structure

```text
src/
├── processed_store.py
├── core/
├── domain/
├── components/
│   ├── sources/
│   │   ├── fapes_source.py
│   │   ├── finep_source.py
│   │   ├── conif_source.py
│   │   ├── prppg_ifes_source.py
│   │   ├── proex_ifes_source.py
│   │   ├── capes_source.py
│   │   └── cnpq_source.py
│   ├── transforms/
│   └── sinks/
└── flows/
    ├── ingest_fapes_flow.py
    ├── ingest_finep_flow.py
    ├── ingest_conif_flow.py
    ├── ingest_prppg_ifes_flow.py
    ├── ingest_proex_ifes_flow.py
    ├── ingest_capes_flow.py
    └── ingest_cnpq_flow.py
```

## Monitoring and Observability

- logs estruturam início, extração, transformação e persistência
- `docs/flow_processing_log.md` registra execuções operacionais relevantes
- a suíte `pytest` valida parsing, deduplicação, runner e regras específicas por source

## Disaster Recovery

- a persistência é atômica por arquivo JSON
- o registry mantém o estado incremental por source
- reruns controlados podem ser feitos limpando apenas a chave específica do source no `registry`, sem afetar os demais
