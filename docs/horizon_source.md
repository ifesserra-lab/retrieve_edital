# Source Horizon Europe

## Objetivo

O **HorizonSource** extrai chamadas abertas do **Horizon Europe** — incluindo o **EIC Accelerator** — do dataset bulk público do Funding & Tenders Portal da Comissão Europeia.

## Por que o dataset bulk e não a search-api

A `search-api` do SEDIA, indicada na análise original, **não funciona**:

| Tentativa | Resultado |
| :-- | :-- |
| `POST /search-api/prod/rest/search` + `query` + `languages` + `sort` | `500 An internal error occurred` |
| idem, sem `sort` | `500` |
| idem, query vazia | `500` |
| `GET` no mesmo endpoint | `405 Method not allowed` |

O serviço responde (devolve `apiVersion`), mas rejeita as queries. O caminho que funciona:

```
https://ec.europa.eu/info/funding-tenders/opportunities/data/referenceData/grantsTenders.json
```

Sem autenticação, sem API key, atualizado diariamente (`Last-Modified`).

## O EIC Accelerator já vem aqui

A análise original listava `EIC Accelerator` como fonte separada. Ela **está neste mesmo dataset**, identificável por `programmeDivision` conter `HORIZON.3.1` (*The European Innovation Council*). Um único source cobre as duas fontes.

## Volume e o filtro obrigatório

O dataset tem **11.141 registros** de todos os programas da Comissão: `Open` 361, `Forthcoming` 287, `Closed` 10.493. Só interessam os de `frameworkProgramme = HORIZON` com status `Open` ou `Forthcoming`.

**O filtro temático por divisão é obrigatório, e o default é vazio.** Medição de 2026-07-29 com as três divisões sugeridas: **192 chamadas relevantes, 185 publicáveis** — mais do que os 153 editais que o portal inteiro tinha. Publicar isso sem curadoria afogaria as fontes nacionais.

Sem `HORIZON_DIVISIONS` configurado, o source não devolve nada e nem baixa o dataset.

```bash
HORIZON_DIVISIONS="HORIZON.2.4,HORIZON.3.1" python -m src.flows.ingest_horizon_flow
```

Sugestão de partida, **pendente de validação da PRPPG** (constante `SUGGESTED_DIVISIONS`):

| Divisão | Área |
| :-- | :-- |
| `HORIZON.2.4` | Digital, Industry and Space |
| `HORIZON.2.5` | Climate, Energy and Mobility |
| `HORIZON.3.1` | European Innovation Council (inclui o EIC Accelerator) |

Um prefixo cobre as subdivisões: `HORIZON.2.4` casa com `HORIZON.2.4.1`.

## Mapeamento

| Campo do dataset | Uso no pipeline |
|------------------|-----------------|
| `title` (fallback `callTitle`) | **nome** |
| `identifier` | dedup e URL pública do tópico |
| `plannedOpeningDateLong` | cronograma `Abertura das inscrições` — **epoch em milissegundos** |
| `deadlineDatesLong` | cronograma; vários prazos viram `Prazo da fase N`, e o maior vira `Prazo para envio de propostas` |
| `status.abbreviation` | filtro (`Open`, `Forthcoming`) e **status** |
| `frameworkProgramme.abbreviation` | filtro (`HORIZON`) |
| `programmeDivision[]` | filtro temático, **tags** e **categoria** |
| `links[].url` | **anexos** |
| `keywords` | **tags** |

### Descrição

O dataset **não traz texto descritivo** — só título, identificador, datas, programa e links. A descrição é composta do título da chamada e da descrição das divisões, que é informação real e de custo zero. A alternativa seria uma requisição por chamada à página do tópico (~200 por execução), o que fica para quando houver demanda.

### Categoria

Derivada da divisão, dentro do vocabulário que o portal já usa: divisão do EIC → `inovação`; demais → `pesquisa`. Sem isso, as 185 chamadas caíam todas em `outros`, já que sem texto descritivo a inferência por palavra-chave do normalizer não tem onde se apoiar.

## Memória e cadência

O arquivo tem **126 MB** (≈22 MB com `Accept-Encoding: gzip`). Os objetos são decodificados um a um, o que evita materializar os 11 mil dicionários de uma vez; o payload cru ainda fica na memória, com **pico medido de ~900 MB** — confortável nos 7 GB do runner do GitHub Actions.

**Cadência semanal**, não diária: o dataset muda pouco de um dia para o outro e o download é pesado. Por isso este fluxo fica **fora** de `scripts/run_all_flows.py`, em [.github/workflows/run_horizon_weekly.yml](../.github/workflows/run_horizon_weekly.yml).

## Contrato (ISource)

- **Entrada:** nenhuma (baixa o dataset configurado).
- **Saída:** `List[RawEdital]` com `raw_agency="Horizon Europe"`, `document_type="edital"`.
- **Sem divisões configuradas**, devolve lista vazia sem fazer requisição.
- **Falha de rede** devolve lista vazia e zera `last_listing_count`.
- **`last_listing_count`** conta as chamadas relevantes antes da deduplicação — número que o runner usa para separar "portal sem novidade" de "source quebrado".

## Prazos vencidos na origem

Como na FINEP, o dataset marca como `Open` chamadas cujo prazo já passou (7 das 192 na medição). As regras de publicação (`src/components/transforms/publication_rules.py`) as descartam no Transform, então não chegam ao portal.
