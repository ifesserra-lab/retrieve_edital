# Source FINEP (Chamadas Públicas)

## Objetivo

O **FinepSource** extrai as chamadas públicas em situação **aberta** da FINEP consumindo a **API oficial do portal** (Liferay Headless / Objects) — a mesma que o widget de busca do site usa no navegador.

## Por que a API e não scraping

Em 2026 o portal foi migrado. A URL antiga passou a redirecionar:

```
http://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta
  → 301 → https://www.finep.gov.br/oportunidades
```

A página nova é uma SPA: o HTML servido **não contém nenhum edital**, e o parser baseado em Playwright passou a extrair zero itens. Como o runner reportava `Sucesso, delta 0`, a queda ficou invisível de **2026-03-15 até 2026-07-27**. Diagnóstico completo em [spec_finep_cnpq_horizon.md](spec_finep_cnpq_horizon.md).

## Endpoints usados

| Endpoint | Uso |
|----------|-----|
| `POST /o/oauth2/token` | Token OAuth2 (`grant_type=client_credentials`, Basic auth) |
| `GET /o/c/chamadapublicas?filter=situacao eq 'aberta'` | Listagem paginada das chamadas abertas |
| `GET /o/c/chamadapublicas/{id}/documentos?pageSize=500` | Anexos da chamada |

### Credenciais

O Liferay embute o par de cliente público no bundle JS servido a qualquer visitante anônimo — é o mecanismo padrão para expor dados públicos a um front-end. O `FinepCredentialResolver` **descobre o par no bundle em tempo de execução**, localizando o uso `btoa(\`${id}:${secret}\`)` e resolvendo os literais (os nomes das variáveis mudam a cada build). Há um par conhecido como fallback.

Isso é deliberado: se a FINEP rotacionar o segredo, o source se adapta em vez de quebrar em silêncio de novo.

## Mapeamento de campos

| Campo da API | Uso no pipeline |
|--------------|-----------------|
| `titulo` | **nome** |
| `descricaoRawText` (fallback: `descricao` sem HTML) | **descrição** |
| `dataDePublicacao` (fallback: `vigenciaInicio`) | cronograma `Data de publicação` → **data_abertura** |
| `prazoProposto` | cronograma `Prazo para envio de propostas` → **data_encerramento** |
| `situacao` | **status** |
| `temaPrincipal`, `taxonomyCategoryBriefs`, `publicoAlvo`, `tipoDeOportunidade`, `regiao` | **tags** |
| `documentoProprietario` (PDF) / `documentoAberto` (ODT) | **anexos** — prefere o PDF |
| `id` | URL pública `finep.gov.br/e/chamada-publica/222684/{id}` |
| `databaseId` | chave do portal antigo, usada só para deduplicação |

> Os rótulos do cronograma (`Data de publicação`, `Prazo para envio de propostas`) são exatamente os que o `EditalNormalizer` reconhece. O rótulo antigo (`Prazo de envio da proposta`) **não casava** com nenhum token do normalizer, e por isso deixava `data_encerramento` vazio.

> `publicoAlvo` e `tipoDeOportunidade` entram como tags por ora. A tarefa **INF-02** os promove a campos próprios do domínio (`publico_alvo`, `modalidade`).

## Filtro por ano de referência

Aceita chamadas cujo prazo caia **no ano de referência ou depois**. A API já garante `situacao = aberta`, então uma chamada aberta com prazo distante continua sendo oportunidade válida — diferente do parser antigo, que só aceitava o ano de referência e o seguinte.

Chamadas **sem `prazoProposto`** são mantidas: são de fluxo contínuo (ex.: `COOPERAÇÃO ICT-EMPRESA – 01/2017`, aberta desde 2017). Elas ficam com `data_encerramento` vazio, o que é o dado correto.

Quando também faltam `vigenciaFim` **e** `tipoDeOportunidade`, o source declara `modalidade = fluxo-contínuo`: a combinação das três ausências é o padrão dessas peças na API. Assim o portal distingue "candidate-se a qualquer momento" de "prazo desconhecido" — antes, `data_encerramento` vazio significava as duas coisas.

| Origem do ano | Prioridade |
|---------------|------------|
| Parâmetro `reference_year=` | 1 |
| Variável de ambiente `REFERENCE_YEAR` | 2 |
| Ano atual do sistema | 3 |

Implementação: `src.config.get_reference_year()`.

## Deduplicação

O source aceita **`processed_urls`** e reconhece **duas** chaves para a mesma chamada:

- a URL pública nova: `https://www.finep.gov.br/e/chamada-publica/222684/{id}`
- a chave do portal antigo: `http://www.finep.gov.br/chamadas-publicas/chamadapublica/{databaseId}`

Os 10 editais coletados antes da migração estão registrados no formato antigo. Sem esse reconhecimento, todos voltariam como novos e duplicariam a saída.

## Categorização (Transform)

No **EditalNormalizer**, a **categoria** dos editais FINEP continua sendo definida pelo **Mistral** a partir da descrição, em uma de: **divulgação de conhecimento**, **extensão**, **inovação**. Requer `MISTRAL_API_KEY`.

É uma chamada de texto barata, não OCR — o source nunca baixa PDF para o Mistral. Manter essa etapa preserva o enum de categorias que o portal espera.

## Uso

```bash
python -m src.flows.ingest_finep_flow
```

```python
from src.flows.ingest_finep_flow import run_pipeline

run_pipeline(reference_year=2026)
run_pipeline(reference_year=2026, max_pages=1)  # limita as páginas da API (100 itens/página)
```

## Contrato (ISource)

- **Entrada:** nenhuma (consome a API configurada).
- **Saída:** `List[RawEdital]` com `raw_agency="FINEP"`, `document_type="edital"`, `raw_status` da API e os campos opcionais `raw_cronograma`, `raw_tags`, `raw_anexos` preenchidos quando disponíveis.
- **Falha de rede** devolve lista vazia e zera `last_listing_count`; falha ao buscar documentos **não** invalida o edital.
- **`last_listing_count`** expõe quantas chamadas a origem devolveu antes da deduplicação. É o número que o runner usa para separar "portal sem novidade" de "source quebrado" (ver [src/flow_health.py](../src/flow_health.py)).

## Dependências

Não usa mais **Playwright**. O source depende apenas de `requests`.
