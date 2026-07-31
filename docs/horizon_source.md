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

## Volume e o filtro por divisão

O dataset tem **11.141 registros** de todos os programas da Comissão. Filtrando por
`frameworkProgramme = HORIZON` com status `Open` ou `Forthcoming`, sobram **481**.

**Decisão em 2026-07-31: indexar o programa inteiro.** A configuração em produção é:

```
HORIZON_DIVISIONS=HORIZON
```

Como a comparação é por prefixo e toda subdivisão começa com `HORIZON`, esse
único valor cobre as 13 subáreas.

O raciocínio: dividir por área só compensa se volume custar algo, e aqui quase não
custa. Horizon **não usa OCR**, então não consome Mistral; o portal filtra por
órgão, então quem procura edital nacional não tropeça nas chamadas europeias; e o
download é pago de uma vez independentemente do recorte.

O **default no código continua vazio** — sem `HORIZON_DIVISIONS` o source não
devolve nada e nem baixa o dataset. É proteção contra habilitar 474 editais por
omissão, não recomendação contra o programa inteiro.

Subáreas disponíveis, com o número de chamadas abertas ou previstas medido em
2026-07-31:

| Código | Chamadas | Área |
| :-- | --: | :-- |
| `HORIZON.1.1` | 4 | European Research Council (ERC) |
| `HORIZON.1.2` | 8 | Divulgação científica |
| `HORIZON.1.3` | 10 | Infraestruturas de pesquisa |
| `HORIZON.2.1` | 76 | Saúde |
| `HORIZON.2.2` | 85 | Cultura, criatividade e sociedade |
| `HORIZON.2.3` | 76 | Segurança civil |
| `HORIZON.2.4` | 91 | Digital, Indústria e Espaço |
| `HORIZON.2.5` | 114 | Clima, Energia e Mobilidade |
| `HORIZON.2.6` | 138 | Alimentos, Bioeconomia e Agricultura |
| `HORIZON.3.1` | 18 | European Innovation Council (EIC) |
| `HORIZON.3.2` | 4 | Ecossistemas de inovação |
| `HORIZON.4.1` | 7 | Widening participation |
| `HORIZON.4.2` | 8 | Reforma do sistema europeu de P&I |

*(A soma passa de 481 porque uma chamada pode pertencer a mais de uma subárea.)*

Para restringir depois, basta listar os códigos separados por vírgula:

```bash
HORIZON_DIVISIONS="HORIZON.3.1,HORIZON.2.4" python -m src.flows.ingest_horizon_flow
```

### Elegibilidade: o cuidado que sobra

O Brasil participa do Horizon como terceiro país, e as regras variam por chamada
— algumas admitem parceiro brasileiro financiado, outras só participação
associada sem recurso. **O dataset não traz esse campo**, então o portal exibe
chamadas em que o IFES pode não ser elegível. É limitação conhecida da fonte, não
do coletor.

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

## Download: janelas de Range

O arquivo tem **126 MB**, e baixá-lo numa transferência só falha de forma
reprodutível. Medições contra o servidor da UE em 2026-07-30:

| Formato | Resultado |
| :-- | :-- |
| transferência única de 126 MB | `Connection reset by peer` no meio, sempre por volta dos 71 MB |
| `Range: bytes=N-` (aberto), como o `curl -C -` envia | `206`, mas estola e é cortado em ~54 MB |
| `Range: bytes=N-M` (limitado a 8 MiB) | `206` com os bytes exatos, rápido |

Retry que reinicia do zero não resolve, e a retomada com `Range` aberto também
não. O que funciona é **janela com fim explícito**: o download é sequencial em
janelas de 8 MiB, cada uma com retentativas próprias, então uma falha custa uma
janela e não o download inteiro. O tamanho total vem do cabeçalho
`Content-Range`, e a montagem só é aceita quando completa — download parcial
levanta erro em vez de entregar JSON truncado ao parser.

O caminho comprimido com `gzip` (~22 MB) é tentado primeiro, por ser mais barato;
as janelas são o fallback.

Tempo medido do dataset completo: **47 segundos**.

## Memória e cadência

Os objetos são decodificados um a um, o que evita materializar os 11 mil
dicionários de uma vez; o payload cru ainda fica na memória, com **pico medido de
~900 MB** — confortável nos 7 GB do runner do GitHub Actions.

**Cadência semanal**, não diária: o dataset muda pouco de um dia para o outro e o
download é pesado. Por isso este fluxo fica **fora** de `scripts/run_all_flows.py`,
em [.github/workflows/run_horizon_weekly.yml](../.github/workflows/run_horizon_weekly.yml).

## Primeira coleta (2026-07-31)

481 chamadas relevantes, **474 publicadas** — 7 descartadas pelas regras de
publicação por prazo já encerrado. Categorias: `pesquisa` 462, `inovação` 12
(as do EIC).

O sink registrou **7 colisões de nome**: o Horizon tem chamadas homônimas, como
`ERA FELLOWSHIPS` e `BIOTECHNOLOGY FOR HEALTHY AGEING`, que aparecem em fases ou
edições diferentes. Cada uma recebeu sufixo derivado do link em vez de sobrescrever
a anterior.

## Contrato (ISource)

- **Entrada:** nenhuma (baixa o dataset configurado).
- **Saída:** `List[RawEdital]` com `raw_agency="Horizon Europe"`, `document_type="edital"`.
- **Sem divisões configuradas**, devolve lista vazia sem fazer requisição.
- **Falha de rede** devolve lista vazia e zera `last_listing_count`.
- **`last_listing_count`** conta as chamadas relevantes antes da deduplicação — número que o runner usa para separar "portal sem novidade" de "source quebrado".

## Prazos vencidos na origem

Como na FINEP, o dataset marca como `Open` chamadas cujo prazo já passou (7 das 192 na medição). As regras de publicação (`src/components/transforms/publication_rules.py`) as descartam no Transform, então não chegam ao portal.
