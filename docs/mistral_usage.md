# Uso do Mistral: onde entra, quanto custa, onde dói

Documento operacional sobre a dependência de LLM do pipeline. Existe porque o
rate limit já apareceu em execuções reais e será o gargalo da expansão de fontes.

## Onde o Mistral é chamado

Três pontos, com custos bem diferentes:

| Chamada | Onde | Quando | Custo por edital |
| :-- | :-- | :-- | :-- |
| `extract_from_pdf` | [edital_normalizer.py:189](../src/components/transforms/edital_normalizer.py#L189) | quando o `RawEdital` tem `pdf_content` | **OCR + LLM** — o mais caro |
| `categorize_finep_by_description` | [edital_normalizer.py:229](../src/components/transforms/edital_normalizer.py#L229) | editais FINEP com descrição | 1 chamada de texto curta |
| `classify_document_titles` | [fapes_source.py:177](../src/components/sources/fapes_source.py#L177) | agrupamento de documentos na FAPES | 1 chamada por página da listagem |

## Quais fontes disparam OCR

Só as que preenchem `pdf_content`:

| Fonte | OCR | Observação |
| :-- | :--: | :-- |
| FAPES | sim | mais o `classify_document_titles` por página |
| CONIF | sim | PDF principal do edital |
| CAPES | sim | |
| CNPq | sim | documento rotulado `Chamada` |
| PRPPG/IFES | sim | anexo principal |
| PROEX/IFES | sim | |
| **FINEP** | **não** | a API do portal entrega descrição e datas prontas |
| **Horizon Europe** | **não** | o dataset bulk dispensa OCR |

As duas fontes mais recentes não usam OCR — quando a origem oferece dados
estruturados, sai mais barato e mais confiável que ler o PDF.

## Rate limit observado

Medições de 2026-07-29, com `MISTRAL_API_KEY` de conta individual:

| Execução | Chamadas | Resultado |
| :-- | --: | :-- |
| FINEP (categoria, texto curto) | 26 | vários `429`, esperas de 60s e 120s |
| CNPq (OCR do documento principal) | 10 | 2 × `429`, espera de 60s |

O backoff em [mistral_client.py:22-24](../src/components/transforms/mistral_client.py#L22-L24) absorveu todos os casos:

```python
RATE_LIMIT_MAX_RETRIES = 10
RATE_LIMIT_INITIAL_WAIT_SEC = 60
RATE_LIMIT_BACKOFF_FACTOR = 2.0
```

A espera cresce 60s → 120s → 240s… até 10 tentativas. No pior caso teórico, uma
única chamada pode segurar o fluxo por mais de 17 horas antes de falhar — bem
acima de qualquer janela de job aceitável.

## Consequência para a expansão de fontes

A concorrência é limitada a `max_workers=2` em todos os fluxos, o que já é
conservador. Com **2 fontes com OCR por dia** o backoff dá conta. O plano de
expansão prevê ~40 fontes; nesse cenário o rate limit deixa de ser incômodo e
passa a ser o fator que define a duração do job.

Três caminhos, em ordem de custo-benefício:

1. **Não usar OCR quando a origem tem dados estruturados.** Foi o que aconteceu
   com FINEP e Horizon, e é o ganho mais barato: elimina a chamada em vez de
   otimizá-la. Vale checar API, RSS ou dataset antes de escrever um scraper de
   PDF.
2. **Teto de chamadas por execução**, com degradação explícita: ao atingir o
   teto, os editais restantes ficam para a próxima execução em vez de arrastar o
   job. Hoje não existe teto.
3. **Plano pago com limite maior**, se as duas medidas acima não bastarem.

## Limite prático do backoff atual

`RATE_LIMIT_MAX_RETRIES = 10` combinado com fator 2 e início em 60s é generoso
demais para um job diário. Um teto de espera acumulada por execução seria mais
adequado que um número de tentativas — fica registrado como melhoria pendente,
não implementada.

## Quando a chave expira: o que se vê

Em 2026-07-31 a chave passou a responder `401 Unauthorized`. O efeito em cascata
vale registrar, porque nenhum passo grita:

1. `extract_from_pdf` falha em toda fonte com OCR;
2. o `EditalNormalizer` cai no fallback e monta o edital só com o título;
3. as regras de publicação reconhecem isso como casca vazia e **descartam**;
4. o fluxo termina com zero editais novos e sai como `Sucesso`, porque a origem
   respondeu normalmente — o portal está de pé, é o LLM que não está.

Foi assim que 15 editais novos da FAPES ficaram parados: a listagem os trazia, a
extração não conseguia processá-los, e o portão corretamente recusou publicar
registros vazios. Antes do portão, eles teriam entrado como cascas — é essa a
origem das 29 que a curadoria removeu.

**Diagnóstico rápido**, quando um fluxo com OCR fica sem novidade e a origem está
saudável:

```bash
grep -c "Status 401" <log-do-fluxo>
```

O classificador da FINEP **não** disfarça mais a falha: devolvia `inovação`, valor
indistinguível de uma classificação real, e agora devolve vazio para o chamador
decidir. O normalizer mantém a categoria da fonte e registra em log.

## A FAPES reprocessava tudo a cada execução

Descoberto ao validar a chave nova, em 2026-07-31: o `FapesSource` deduplicava por
`key_from_nome(título da página)`, enquanto o registry guardava o nome do arquivo,
derivado do nome que o **Mistral reescreve**. As duas chaves nunca fechavam, então
os mesmos editais voltavam como novos em toda execução, consumindo OCR e batendo
em rate limit — a FAPES era a maior consumidora de Mistral do pipeline sem
produzir nada.

A dedup passou a ser por URL do documento, como nas demais fontes. E como o
"edital principal" do grupo é eleito pela classificação do Mistral, que varia
entre execuções, o registry guarda **todas** as URLs do grupo: qualquer documento
que reapareça identifica o edital já coletado.

Efeito medido: de 12 editais reapresentados como novos para 4.

**Resíduo conhecido**: os 4 restantes são itens que as regras de publicação
rejeitam — anexo, alteração e prazo vencido. Como não são publicados, suas URLs
nunca entram no registry e voltam a cada execução, gastando OCR. Registrá-los
resolveria o desperdício, mas impediria a recoleta de um edital cuja extração
falhou e depois passou a funcionar. A escolha entre as duas coisas fica pendente.

## Chave de acesso

`MISTRAL_API_KEY` no `.env` local e como secret do repositório no GitHub
Actions. Ver [.env.example](../.env.example). `MistralExtractionService` levanta
`ValueError` na construção se a chave não estiver definida, então o fluxo falha
cedo e de forma visível em vez de produzir editais sem extração.
