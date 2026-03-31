# Source PROEX/IFES (Editais Abertos)

## Objetivo

O **ProexIfesSource** extrai os editais da página pública da PROEX/IFES e entrega apenas os itens do bloco **Editais abertos** cujo cabeçalho de ano corresponde ao **ano corrente**.

- **Listagem**: [https://proex.ifes.edu.br/editais](https://proex.ifes.edu.br/editais)
- **Ano validado na implementação**: `2026`, em execução realizada em **2026-03-31**

## Como o source identifica os editais

O portal não possui uma página de detalhe por edital. A estrutura real da listagem é um conteúdo HTML estático com:

1. um cabeçalho `Editais abertos`
2. um subtítulo do ano, por exemplo `2026`
3. um bloco de título do edital
4. uma sequência de links para edital, retificações, anexos, resultados e formulários

O source:

- localiza o `h2` com texto `Editais abertos`
- encontra o `h3` do ano corrente
- percorre os irmãos seguintes até o próximo `h3`
- monta um item por título de edital
- coleta apenas links documentais (`pdf`, `doc`, `docx`, `odt`, `ods`, `zip`, `rar`)
- ignora links não documentais, como formulários, YouTube e páginas externas sem arquivo

## Chave de deduplicação

Como a PROEX/IFES não expõe permalink por edital, o fluxo usa a **URL do PDF principal do edital** como chave em `registry/processed_editais.json`, na seção `proex_ifes`.

Exemplos processados em 2026-03-31:

- `https://agifes.ifes.edu.br/wp-content/uploads/2026/03/Edital-Premio-Assistec-Inova-de-Pos-Graduacao-Stricto-Sensu-pos-BSB-Edital-No-05.2026.pdf`
- `https://proex.ifes.edu.br/images/M_images/Proex/Editais/2026/01/Edital_012026_-_Selecao_de_estudantes_Partiu_IF_2026_-_Retificacao_20-01-26.pdf`

## Escolha do PDF principal

O source pontua os anexos em PDF e escolhe como principal o documento com maior aderência a termos como:

- `edital`
- `chamada pública`
- `retificação`

E penaliza links com termos como:

- `resultado`
- `inscrição`
- `matrícula`
- `sorteio`
- `comunicado`

Esse PDF principal é baixado para OCR e sua URL é preservada no campo `link` do JSON final.

## Fallback de rede

Na execução de **2026-03-31**, o portal da PROEX/IFES e arquivos hospedados na AGIFES responderam `403 Forbidden` para `requests`, mas aceitaram `curl -L`.

Por isso, o `ProexIfesSource` aplica a seguinte estratégia:

1. tenta carregar listagem e PDFs com `requests.Session`
2. em caso de falha HTTP, registra warning
3. faz fallback com `curl -L --max-time <timeout>`

Esse fallback foi incorporado apenas para a PROEX/IFES, sem alterar os outros sources.

## Fluxo recomendado

Use o fluxo dedicado em `src/flows/ingest_proex_ifes_flow.py`:

```bash
python -m src.flows.ingest_proex_ifes_flow
```

Via código:

```python
from src.flows.ingest_proex_ifes_flow import run_pipeline

run_pipeline(current_year=2026)
```

## Contrato

- **Entrada**: nenhuma
- **Saída**: `List[RawEdital]` com:
  - `raw_agency="PROEX/IFES"`
  - `raw_status="aberto"`
  - `raw_tags=["proex", "ifes", "<ano>"]`
  - `raw_anexos` com todos os anexos documentais do bloco do edital
  - `pdf_content` preenchido com o PDF principal quando o download é bem-sucedido

## Execução registrada em 2026-03-31

Resultado operacional validado:

- `5` editais de 2026 extraídos
- `5` registros transformados
- `5` JSONs persistidos em `data/output/`
- `5` URLs adicionadas ao registry `proex_ifes`

Arquivos gerados:

- `prêmio_assistec_inova_de_pesquisas_em_inovação_e_empreendedorismo_no_âmbito_da_pós-graduação_stricto_sensu_da_rede_federal_de_educação_profi_0ba207.json`
- `prêmio_projetos_inovadores_na_educação_profissional_e_tecnológica.json`
- `edital_nº_032026_-_chamamento_público_para_seleção_de_boas_práticas_em_ações_de_inovação_e_empreendedorismo_desenvolvidos_na_rfepct_ou_na_re_df1116.json`
- `edital_nº_022026__mapaenagro__ifes_-_seleção_de_bolsistas_para_compor_equipe_de_apoio_ao_projeto_de_desenvolvimento_de_ações_estratégicas_de_66e8e4.json`
- `edital_0012026_-_seleção_de_estudantes_para_o_curso_de_extensão_partiu_if_curso_preparatório_para_o_ensino_médio_integrado_do_instituto_fede_3ff8c5.json`
