# Source FINEP (Chamadas Públicas)

## Objetivo

O **FinepSource** extrai chamadas públicas em situação **aberta** do portal da FINEP e entrega apenas aquelas cujo **Prazo para envio de propostas** termina no **ano de referência** ou no **ano seguinte**. Para cada chamada, o source **acessa a página de detalhe** e extrai:

| Dado na página | Uso no pipeline |
|----------------|------------------|
| Texto inicial (“Esta Seleção Pública tem por objetivo…”) | **Descrição** do edital |
| Data de publicação | **Cronograma** + **data_abertura** |
| Prazo para envio de propostas até | **Cronograma** + **data_encerramento** |
| Tema(s) (separados por `;`) | **Tags** |
| Tabela **Documentos** (nome + link) | **Anexos** (`tipo`: "Documentos") |

- **Listagem:** [Chamadas Públicas - Situação Aberta](http://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta)
- **Detalhe (ex.):** [chamadapublica/777](http://www.finep.gov.br/chamadas-publicas/chamadapublica/777)

## Variável de ano (referência)

O ano usado no filtro de prazo é configurável:

| Origem | Prioridade |
|--------|------------|
| Parâmetro no construtor `reference_year=` | 1 |
| Variável de ambiente `REFERENCE_YEAR` | 2 |
| Ano atual do sistema | 3 |

Implementação: `src.config.get_reference_year()`.

## Categorização (Transform)

No **EditalNormalizer**, para editais FINEP a **categoria** é definida pelo **Mistral** com base na descrição, em uma de:

- **divulgação de conhecimento**
- **extensão**
- **inovação**

Requer `MISTRAL_API_KEY` no ambiente.

## Fluxo recomendado: ingest_finep_flow

Use o fluxo dedicado FINEP em `src/flows/ingest_finep_flow.py`:

```bash
# Só a primeira página (teste)
python -m src.flows.ingest_finep_flow

# Todas as páginas da listagem
python -m src.flows.ingest_finep_flow --all
```

Parâmetros opcionais via código:

```python
from src.flows.ingest_finep_flow import run_pipeline

run_pipeline(reference_year=2026, max_pages=1)  # 1ª página, ano 2026
run_pipeline(reference_year=2027, max_pages=None)  # todas as páginas, ano 2027
```

## Uso do Source diretamente

```python
from src.components.sources.finep_source import FinepSource
from src.flows.ingest_finep_flow import run_pipeline

source = FinepSource(reference_year=2026, max_pages=1)
run_pipeline(source=source)
```

## Contrato (ISource)

- **Entrada:** nenhuma (lê da URL configurada).
- **Saída:** `List[RawEdital]` com `raw_agency="FINEP"`, `document_type="edital"`, e apenas itens cujo prazo tem ano em `[reference_year, reference_year + 1]`. Campos opcionais preenchidos quando disponíveis: `raw_cronograma`, `raw_tags`, `raw_anexos`.

## Paginação e parada antecipada

O source navega pela paginação clicando nos números das páginas (1, 2, 3, …); a primeira é carregada via URL e as seguintes pelo clique no número (com fallback por URL se não houver link numérico). O source percorre as páginas (link “Próx”/“Próxima”) até não haver mais páginas. O source **para de navegar** quando todos os editais da página têm prazo em ano anterior ao de referência (log: *"All chamadas on page X are from previous years. Stopping pagination."*). O parâmetro **`max_pages`** (ex.: `1`) limita o número de páginas para testes.

## Registry (editais já processados)

O **FinepSource** aceita **`processed_urls`** (set de URLs já processadas). O flow carrega as chaves FINEP de **`registry/processed_editais.json`** e, após o sink, adiciona as URLs gravadas ao índice, evitando reprocessar chamadas já baixadas.
