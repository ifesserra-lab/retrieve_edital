# Source CNPq (Chamadas Públicas)

## Objetivo

O **CnpqSource** extrai as chamadas públicas do CNPq **abertas para submissão** do portal atual, no gov.br.

## Por que o alvo mudou

O source anterior lia `memoria2.cnpq.br`. O host **responde 200 com 137 KB**, o que fazia o fluxo parecer saudável, mas o conteúdo tem **um único card**:

```
div class="content"  → 1
idDivulgacao=\d+     → 1
<h4>                 → 1
```

O próprio nome do host (`memoria2`) indica arquivo morto. Era essa a causa da cobertura parcial relatada — o alvo, não o parser. Diagnóstico completo em [spec_finep_cnpq_horizon.md](spec_finep_cnpq_horizon.md).

## Origem

```
https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao
```

Plone estático — `requests` + BeautifulSoup, sem JS e sem Playwright.

**Sobre o volume**: a página traz **10 chamadas** e não tem paginação. O link `Próximo »` do rodapé aponta para `Busca_abertas`, que é uma busca paginada — e cujo conjunto completo, verificado página por página, é exatamente **o mesmo dessas 10**. Não há chamada aberta fora dessa listagem.

> Cuidado ao contar links na página: cada chamada aparece também dentro das URLs de compartilhamento (Facebook, Twitter, LinkedIn, WhatsApp), que embutem o endereço da chamada como parâmetro. Contar `href` sem filtrar infla o total em várias vezes.

## Estrutura

**Listagem** — um bloco por chamada:

```html
<div class="item visualIEFloatFix">
  <h2 class="headline"><a class="summary url" href="...">Título</a></h2>
</div>
```

**Detalhe** — descrição em `#content-core`, período de inscrições em texto e documentos como links diretos.

O slug da chamada (`/chamadas/todas-as-chamadas/chamadas-<ano>/chamada-no-NN-YYYY/...`) é estável e serve como chave de deduplicação.

## Período de inscrições

O rótulo varia conforme o tipo de peça:

| Rótulo na página | Onde aparece |
|------------------|--------------|
| `INSCRIÇÕES: dd/mm/aaaa a dd/mm/aaaa` | chamadas comuns |
| `Recebimento das propostas: dd/mm/aaaa a dd/mm/aaaa` | chamamentos públicos |
| `Submissão das propostas`, `Prazo para submissão` | variantes aceitas |

O início vira `Abertura das inscrições` e o fim `Prazo para envio de propostas` no cronograma — rótulos que o `EditalNormalizer` reconhece ao derivar `data_abertura` e `data_encerramento`.

A data de `Publicado em` **voltou ao cronograma**. Ela havia sido removida porque o normalizer dava precedência a eventos de publicação ao derivar `data_abertura`, e a data do CMS sobrepunha a abertura real das inscrições. Com a precedência corrigida — `abertura das inscrições` antes de `publicação` — ela pode ser registrada como a informação adicional que é.

Chamada sem período declarado na página **é mantida**: a data costuma estar apenas no PDF, e o OCR a recupera. Foi o caso da `Nº 20/2026 - Atlânticas`, cujo encerramento (2026-09-30) só existia no documento.

## Anexos e OCR

Só entram documentos sob `/chamadas/todas-as-chamadas/` com extensão de documento (`.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.odt`, `.odp`). Esse filtro por caminho descarta o boilerplate que o gov.br repete em toda página, como a `Carta de Serviços`.

O documento principal para OCR é o rotulado exatamente como **`Chamada`**; sem ele, o primeiro PDF disponível. Resposta que não seja `application/pdf` não é usada como conteúdo de OCR.

## Categoria

O source **não define `source_category`**, de propósito. Quando definido, o `EditalNormalizer` o impõe sobre a categoria que o Mistral extraiu do PDF, e o valor entraria como item novo no vocabulário de categorias que o portal consome. Sem ele, a categoria vem do conteúdo do edital, como nas demais fontes.

## Filtro por ano

Descarta chamadas cujo encerramento seja anterior ao ano corrente. Mesma regra já vigente em `CapesSource`.

## Contrato (ISource)

- **Entrada:** nenhuma (lê a listagem configurada).
- **Saída:** `List[RawEdital]` com `raw_agency="CNPq"`, `document_type="edital"`, e `raw_cronograma`, `raw_tags`, `raw_anexos`, `pdf_content` preenchidos quando disponíveis.
- **Falha de rede na listagem** devolve lista vazia e zera `last_listing_count`; falha em uma chamada específica descarta só ela.
- **`last_listing_count`** expõe quantas chamadas a origem devolveu antes da deduplicação — é o número que o runner usa para separar "portal sem novidade" de "source quebrado" (ver [src/flow_health.py](../src/flow_health.py)).

## Uso

```bash
python -m src.flows.ingest_cnpq_flow
```

## Resultado da primeira coleta (2026-07-29)

10 chamadas, **todas as 10** com `data_encerramento` e com anexos. Categorias: `pesquisa` (7), `extensão` (2), `inovação` (1).

Os 4 registros CNPq coletados do portal antigo continuam em `data/output/` como órfãos: apontam para `memoria2.cnpq.br`, três deles sem `data_encerramento`, e um (`PROAFRICA`) é a mesma chamada que voltou como `nº 15/2026`. Removê-los é decisão pendente.
