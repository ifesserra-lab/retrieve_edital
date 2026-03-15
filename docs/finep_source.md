# Source FINEP (Chamadas Públicas)

## Objetivo

O **FinepSource** extrai chamadas públicas em situação **aberta** do portal da FINEP e entrega apenas aquelas cujo **Prazo para envio de propostas** termina no **ano de referência** ou no **ano seguinte**. Para cada chamada, o source **acessa a página de detalhe** (ex.: `http://www.finep.gov.br/chamadas-publicas/chamadapublica/777`) e extrai:

- **Descrição:** texto inicial da página (ex.: "Esta Seleção Pública tem por objetivo conceder recursos de subvenção econômica...")
- **Cronograma:** Data de publicação e Prazo para envio de propostas até (como itens de cronograma)
- **Tags:** temas listados no campo Tema(s), separados por `;`
- **Anexos:** links da tabela de Documentos (nome do documento + link para PDF/documento)

- **Listagem:** [Chamadas Públicas - Situação Aberta](http://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta)
- **Detalhe (ex.):** [Chamada 777](http://www.finep.gov.br/chamadas-publicas/chamadapublica/777)

## Variável de ano (referência)

O ano usado no filtro de prazo é configurável:

| Origem | Prioridade |
|--------|------------|
| Parâmetro no construtor `reference_year=` | 1 |
| Variável de ambiente `REFERENCE_YEAR` | 2 |
| Ano atual do sistema | 3 |

Exemplos:

- Usar ano atual (padrão): não defina `REFERENCE_YEAR` e não passe `reference_year` no construtor.
- Fixar em 2026: no `.env` defina `REFERENCE_YEAR=2026` ou use `FinepSource(reference_year=2026)`.
- Injetar em fluxo: `run_pipeline(source=FinepSource(reference_year=2027))`.

Implementação centralizada em `src.config.get_reference_year()`.

## Uso no pipeline

```python
from src.components.sources.finep_source import FinepSource
from src.flows.ingest_fapes_flow import run_pipeline

# Ano pelo .env ou ano atual
source = FinepSource()
run_pipeline(source=source, ...)

# Ano fixo
source = FinepSource(reference_year=2026)
run_pipeline(source=source, ...)
```

## Contrato (ISource)

- **Entrada:** nenhuma (lê da URL configurada).
- **Saída:** `List[RawEdital]`, com `raw_agency="FINEP"`, `document_type="edital"`, e apenas itens cujo prazo (campo “Prazo para envio de propostas até”) tem ano em `[reference_year, reference_year + 1]`.

## Paginação

O source percorre todas as páginas de resultados (link “Próx”/“Próxima”) até não haver mais páginas.
