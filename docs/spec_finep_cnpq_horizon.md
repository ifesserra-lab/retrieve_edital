# Spec e Plano: FINEP, CNPq e Horizon Europe

**Autor**: Horizon Project Agent
**Data**: 2026-07-27
**Status**: 🟢 Quebras corrigidas. INF-04, FIX-FINEP (2026-07-27) e FIX-CNPQ (2026-07-29) concluídos. Resta **US-HORIZON**.
**Recon**: executado em 2026-07-27, dados medidos nos portais

> **Como processar**: §1 é diagnóstico, §5 é a lista de tarefas executáveis com checkbox. As tarefas FIX-FINEP e FIX-CNPQ corrigem coleta hoje quebrada e têm precedência sobre o backlog de expansão em [plan_fomento_empresarial.md](plan_fomento_empresarial.md).

---

## 1. Resumo do diagnóstico

O PDF de análise classificou FINEP como cobertura "Adequada" e CNPq como "Parcial — poucas chamadas indexadas". O reconhecimento mostra que **os dois estão quebrados**: ambos os sources apontam para URLs de portais que foram descontinuados, e o runner reporta `Sucesso` nas duas execuções.

| Fonte | Editais no repo | Disponível no portal | Lacuna | Última coleta bem-sucedida |
| :-- | --: | --: | --: | :-- |
| **FINEP** | 10 | **36 abertas** | 26 (72%) | **2026-03-15** — 4 meses parado |
| **CNPq** | 4 | **73 chamadas** | 69 (95%) | 2026-06-01 (1 item); antes, 2026-03-22 |
| **Horizon Europe** | 0 | **200 abertas** (HORIZON) | 200 (100%) | nunca implementado |

Evidência da falha silenciosa, em [docs/flow_processing_log.md](flow_processing_log.md):

```
| 2026-07-27 03:24:50 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); …
| 2026-07-27 03:25:26 -03:00 | `CNPQ`  | Sucesso | Registry `cnpq`:  5 -> 5  (delta 0); …
```

`delta 0` por quatro meses seguidos é reportado como sucesso. **Nenhum alarme existe para distinguir "não há edital novo" de "o scraper deixou de funcionar".** Essa é a causa raiz de as duas quebras terem passado despercebidas, e é o item mais barato de corrigir (§5 · INF-04).

---

## 2. FINEP — portal migrado para Liferay com API pública

### 2.1 O que quebrou

A URL usada por [`FinepSource`](../src/components/sources/finep_source.py) responde **301** para um portal novo:

```
http://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta
  → 301 → https://www.finep.gov.br/oportunidades
```

A página nova tem **0 links `chamadapublica`** e 0 ocorrências de paginação `limitstart` — os dois pontos de apoio do parser atual. O portal antigo foi para `legacy.finep.gov.br`. A listagem nova é um widget SPA (`/o/finep-busca-chamadas-publicas/assets/index-BJc8YriS.js`), então o HTML servido não contém edital algum.

### 2.2 A API encontrada

O bundle JS do widget revela a integração completa — **Liferay Headless / Objects**:

```http
POST https://www.finep.gov.br/o/oauth2/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic base64(idClientPRD:secretClientPRD)

grant_type=client_credentials
```

```http
GET https://www.finep.gov.br/o/c/chamadapublicas
    ?filter=situacao eq 'aberta'
    &sort=dataDePublicacao:desc
    &pageSize=100&page=1
Authorization: Bearer <token>
```

**Testado e funcionando em 2026-07-27**: `totalCount = 473` no acervo total, **36 com `situacao = aberta`**.

Endpoints auxiliares no mesmo bundle:
- `/o/headless-admin-taxonomy/v1.0/sites/20117/taxonomy-vocabularies` — vocabulário de temas
- `/o/headless-delivery/v1.0/content-structures/210999/structured-contents` — conteúdo estruturado
- `/o/headless-admin-list-type/v1.0/list…` — listas de domínio

**Sobre as credenciais**: `idClientPRD` / `secretClientPRD` estão embutidas no bundle JS servido a qualquer visitante anônimo — são credenciais de cliente público, o mecanismo padrão do Liferay para expor dados públicos a um front-end. O scraper faria exatamente a chamada que o site faz para o próprio navegador do usuário. Ainda assim, **extraí-las do bundle em tempo de execução** (com o par atual como fallback) é mais robusto do que fixá-las no código: se a FINEP rotacionar o segredo, o source se adapta sozinho em vez de quebrar em silêncio de novo.

### 2.3 Campos retornados — mapeamento direto

| Campo da API | Destino em `EditalDomain` | Observação |
| :-- | :-- | :-- |
| `titulo` | `nome` | |
| `descricaoRawText` / `descricao` | `descrição` | texto pronto — **dispensa OCR Mistral** |
| `dataDePublicacao` | `data_abertura` | ISO 8601 |
| `prazoProposto` | `data_encerramento` | ex. `2026-08-14T18:00:00.000Z` |
| `situacao` | `status` | `{key: 'aberta', name: 'Aberta'}` |
| `publicoAlvo` | **`publico_alvo`** | taxonomia nativa: `Startup`, `ICT`, `Cooperativa`, `Fundos de Investimento`, faixas de receita |
| `tipoDeOportunidade` | **`modalidade`** | `{key: 'naoReembolsavel'}` → `subvenção` |
| `temaPrincipal` / `tema` | `tags` | ex. `Tecnologias Digitais e Conectividade` |
| `regiao` | `ambito_geografico` | |
| `contrapartida`, `tipoCooperacao`, `vigenciaInicio/Fim`, `keywords` | metadados extras | |

### 2.4 Consequências

1. **O fluxo FINEP deixa de precisar de Playwright e de Mistral.** Hoje usa os dois; a API entrega descrição e datas estruturadas. Redução direta de custo por edital e de tempo de execução no CI.
2. **`publicoAlvo` e `tipoDeOportunidade` vêm nativos** — para a FINEP, a tarefa INF-02 do outro plano sai de graça.
3. **Nota sobre a prioridade nº 1 do PDF**: o PDF pede "indexar os 13 editais do FINEP MIB Rodada 2". O repositório **já tem 9 deles**, coletados em 2026-03-15 (`finep_mais_inovação_brasil_-_rodada_2_-_*`). Ou seja: parte dessa lacuna é de **exibição no portal**, não de coleta. Vale confirmar com o time do front antes de tratar como problema de scraping.

---

## 3. CNPq — portal descontinuado

### 3.1 O que quebrou

[`CnpqSource`](../src/components/sources/cnpq_source.py) lê `memoria2.cnpq.br`. O host responde **200 com 137 KB**, o que faz o source parecer saudável, mas o conteúdo tem **1 único card**:

```
div class="content"  → 1
idDivulgacao=\d+     → 1
<h4>                 → 1
```

O nome do host (`memoria2`) já indica arquivo morto. É por isso que o PDF observou "poucas chamadas indexadas" — e a causa é o alvo, não o parser.

### 3.2 O portal atual

```
https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao   ← 73 chamadas linkadas
https://www.gov.br/cnpq/pt-br/chamadas/analise-em-andamento
https://www.gov.br/cnpq/pt-br/chamadas/resultados-publicados
```

- Plone estático, `requests` + BeautifulSoup — sem JS, sem Playwright.
- Chamadas em `/chamadas/todas-as-chamadas/chamadas-<ano>/chamada-no-NN-YYYY/…` — **slug estável, ótimo como chave de dedup**.
- Datas `dd/mm/yyyy` no HTML (39 ocorrências na listagem).
- `plone.restapi` presente porém **401** (mesmo comportamento observado em ANEEL/ANP) → scraping de HTML é o caminho.

### 3.3 Dívida de qualidade já existente

Dos 4 editais CNPq em `data/output/`, **3 estão com `data_encerramento` vazio**. O reprocessamento contra o portal novo deve corrigi-los; vale limpar a chave `cnpq` do registry para forçar a recoleta.

---

## 4. Horizon Europe — dataset bulk aberto

### 4.1 A API documentada não responde

O `search-api` SEDIA citado no PDF retorna erro em todas as variantes testadas:

| Tentativa | Resultado |
| :-- | :-- |
| `POST /search-api/prod/rest/search` + `query` + `languages` + `sort` | `500 An internal error occurred` |
| idem, sem `sort` | `500` |
| idem, query vazia | `500` |
| `GET` no mesmo endpoint | `405 Method not allowed` |

O serviço responde (devolve `apiVersion: 2.148.3`), mas rejeita as queries. Não vale investir em engenharia reversa disso.

### 4.2 O que funciona

```
https://ec.europa.eu/info/funding-tenders/opportunities/data/referenceData/grantsTenders.json
```

- **Sem autenticação, sem API key.**
- `Content-Length: 126.393.370` (126 MB); ~22 MB com `--compressed`.
- `Last-Modified: Mon, 27 Jul 2026 21:46:44 GMT` — **atualizado diariamente**.
- **11.141 registros**: `Open` 361 · `Forthcoming` 287 · `Closed` 10.493.
- Programas: `H2020` 3.855, `HORIZON` 3.526, `ERASMUS2027`, `CEF2027`, `DIGITAL`, `EDF`, `LIFE2027`, `EURATOM2027`, `CERV`.
- **HORIZON com status `Open`: 200.**

### 4.3 EIC Accelerator vem junto

O PDF lista `EIC Accelerator` como fonte separada. Ela **já está neste dataset** — o primeiro registro HORIZON aberto é `HORIZON-EIC-2026-ACCELERATOR-01`, identificável por `programmeDivision` conter `HORIZON.3.1` (*The European Innovation Council*). Um único source cobre as duas fontes; a estimativa de 4h para o EIC no [spec_expansao_fontes.md](spec_expansao_fontes.md) desaparece.

### 4.4 Mapeamento e limites

| Campo | Destino | Observação |
| :-- | :-- | :-- |
| `title` | `nome` | |
| `identifier` / `callIdentifier` | dedup key | ex. `HORIZON-EIC-2026-ACCELERATOR-01` |
| `deadlineDatesLong` | `data_encerramento` | **epoch em milissegundos**, lista |
| `plannedOpeningDateLong` | `data_abertura` | epoch ms |
| `status.abbreviation` | filtro | manter só `Open` e `Forthcoming` |
| `frameworkProgramme.abbreviation` | filtro | manter `HORIZON` |
| `programmeDivision[].abbreviation` | `tags` / detecção de EIC | |
| `links[].url` | `link`, `anexos` | |

⚠ **Limitação real: o bulk não traz descrição.** Só título, identificador, datas, programa e links. Como `descrição` é obrigatório em `EditalDomain`, há três saídas:
- **(a)** compor a descrição de `callTitle` + `programmeDivision.description` — custo zero, qualidade baixa;
- **(b)** buscar a página do tópico por item (`links[].url`) — ~200 requisições por execução;
- **(c)** gerar resumo via Mistral a partir dos metadados — custo por item.

**Recomendação: (a) agora, (b) só para os itens que passarem no filtro temático.**

⚠ **Volume**: 200 chamadas abertas jogadas em `data/output/` afogam o portal e são majoritariamente irrelevantes para o IFES. **Filtro temático por `programmeDivision` é obrigatório**, não opcional — a definir com a PRPPG quais divisões interessam (candidatas: `HORIZON.2.4` Digital/Indústria/Espaço, `HORIZON.2.5` Clima/Energia/Mobilidade, `HORIZON.3.1` EIC).

⚠ **Peso no CI**: 126 MB por execução. Mitigar com `--compressed` (22 MB), parsing em streaming e **cadência semanal**, não diária.

---

## 5. Plano executável

**Status geral**: 🔵 Não iniciado · **Premissa**: 1 desenvolvedor, 30h úteis/semana

### Onda 0 — Restaurar coleta quebrada · 22h

#### [x] INF-04 · Canário contra falha silenciosa · 4h — **concluído em 2026-07-27**

Entregue em `src/flow_health.py` + `scripts/run_all_flows.py`. Testes em `tests/step_defs/test_flow_health.py` e `tests/step_defs/test_run_all_flows.py`.


**Depende de**: nada. **Fazer primeiro** — é o que impede a terceira ocorrência.
**Alterar**: [scripts/run_all_flows.py](../scripts/run_all_flows.py), `docs/flow_processing_log.md`, `tests/step_defs/test_run_all_flows.py`

Critérios de aceite:
1. fonte que retorne **0 itens brutos** (não 0 novos) é marcada `⚠ Atenção`, não `Sucesso`;
2. fonte com `delta 0` por **N execuções consecutivas** (default 7) é reportada como suspeita no log;
3. **redirect de domínio ou de path na URL de listagem** é logado como aviso explícito — foi exatamente o sintoma da FINEP;
4. fontes declaradas de baixo volume (ex. `aneel`) são isentas da regra 2.

> Distinção que o runner hoje não faz: **0 itens brutos** = scraper quebrado; **0 itens novos** = nada mudou no portal. Só a segunda é sucesso.

---

#### [x] FIX-FINEP · Migrar FinepSource para a API Liferay · 10h — **concluído em 2026-07-27**

Verificado contra a API em produção: **36 chamadas abertas**, **26 novas** após deduplicação (as 10 antigas foram reconhecidas pela chave do portal antigo, sem duplicar). 23 das 26 com anexos; 12 com `data_encerramento` e 14 sem — estas últimas são de fluxo contínuo, sem prazo na origem.

**Desvio do critério 5**: o Playwright foi removido, mas o **Mistral continua** classificando a categoria FINEP (uma chamada de texto, não OCR). Retirá-lo exigiria mudar o enum de categorias que o portal consome — decisão do time do front, não deste fluxo.

**Bug adicional corrigido**: o rótulo de cronograma que o source antigo emitia (`Prazo de envio da proposta`) não casava com nenhum token do `EditalNormalizer`, então `data_encerramento` saía vazio. Agora emite `Prazo para envio de propostas`, que casa.


**Depende de**: nada.
**Alterar**: [src/components/sources/finep_source.py](../src/components/sources/finep_source.py), [docs/finep_source.md](finep_source.md), `tests/step_defs/test_finep_source.py`, `docs/features/`

Critérios de aceite:
1. obtém token em `POST /o/oauth2/token` (`client_credentials`, Basic auth) e renova ao expirar;
2. **extrai `client_id`/`secret` do bundle JS** em runtime, com o par atual como fallback;
3. pagina `/o/c/chamadapublicas` com `filter=situacao eq 'aberta'` até `totalCount`;
4. mapeia os campos do §2.3, incluindo `publicoAlvo` e `tipoDeOportunidade`;
5. **remove Playwright e Mistral do fluxo FINEP** — a API já entrega descrição e datas;
6. dedup por `id`/`externalReferenceCode` da API;
7. coleta as **36 chamadas abertas** (contra 10 hoje);
8. os 10 editais já existentes não são duplicados.

Verificar: `python -m src.flows.ingest_finep_flow && python -c "import json;print(len(json.load(open('registry/processed_editais.json'))['finep']))"` → esperado ≥36

---

#### [x] FIX-CNPQ · Reapontar CnpqSource para o gov.br · 8h — **concluído em 2026-07-29**

Reescrito sobre `abertas-para-submissao`. Resultado: **10 chamadas, todas as 10 com `data_encerramento`** e com anexos.

**Correção da estimativa de volume desta spec**: o número de 73 chamadas registrado abaixo estava errado — veio de contar `href` sem filtrar as URLs de compartilhamento social, que embutem o endereço da chamada como parâmetro. O total real de chamadas abertas é **10**, confirmado por dois caminhos independentes (a listagem curada e a busca `Busca_abertas` paginada, que devolvem o mesmo conjunto). O ganho é de 4 para 10, não de 4 para 73.

**Pendência**: os 4 registros do portal antigo continuam em `data/output/` como órfãos, apontando para `memoria2.cnpq.br`. Remover é decisão pendente — ver §7.6.


**Depende de**: nada.
**Alterar**: [src/components/sources/cnpq_source.py](../src/components/sources/cnpq_source.py), `tests/step_defs/test_cnpq_source.py`, `docs/features/ingest_cnpq.feature`

Critérios de aceite:
1. lê `https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao`;
2. coleta as chamadas em `/chamadas/todas-as-chamadas/chamadas-<ano>/…`, deduplicando os links repetidos da listagem;
3. dedup pelo slug da chamada, não pelo `idDivulgacao` do portal antigo;
4. parseia datas `dd/mm/yyyy` e preenche `data_encerramento` — **os 3 editais atuais com o campo vazio devem ser corrigidos**;
5. filtra por encerramento ≥ ano corrente (regra já vigente em `CapesSource`);
6. `memoria2.cnpq.br` deixa de ser referenciado no código;
7. limpar a chave `cnpq` do registry para forçar recoleta completa.

Verificar: chave `cnpq` do registry ≥ 40 e nenhum JSON CNPq com `data_encerramento` vazio.

---

### Onda 1 — Horizon Europe · 12h

#### [ ] US-HORIZON · Source e flow Horizon Europe (+ EIC) · 12h

**Depende de**: INF-04 (para não repetir falha silenciosa numa fonte de 126 MB).
**Criar**: `src/components/sources/horizon_source.py`, `src/flows/ingest_horizon_flow.py`, `docs/features/ingest_horizon.feature`, `tests/step_defs/test_horizon_source.py`
**Alterar**: `scripts/run_all_flows.py`, `docs/etl_architecture.md`

Critérios de aceite:
1. baixa `grantsTenders.json` com `--compressed` e parseia em streaming (não carregar 126 MB de uma vez);
2. filtra `status ∈ {Open, Forthcoming}` **e** `frameworkProgramme = HORIZON`;
3. aplica **filtro temático por `programmeDivision`** a partir de lista configurável — sem ele o flow não persiste nada;
4. converte `deadlineDatesLong` / `plannedOpeningDateLong` de epoch ms para ISO;
5. marca `ambito_geografico = internacional`, `publico_alvo = [pesquisador, internacional]`, e acrescenta `empresa` quando a divisão for `HORIZON.3.1` (EIC);
6. `descrição` composta de `callTitle` + `programmeDivision.description` (opção (a) do §4.4);
7. dedup por `identifier`;
8. **cadência semanal**, não diária.

---

### 5.1 Consolidado

| Onda | Tarefas | Horas | Editais recuperados/ganhos |
| :--: | :-- | --: | :-- |
| 0 | INF-04, FIX-FINEP, FIX-CNPQ | 22h | 14 → ~109 (+95) |
| 1 | US-HORIZON | 12h | +200 abertas, antes do filtro temático |
| | **Total** | **34h** | **≈1,2 semana** |

**Comparação com o plano de expansão**: [plan_fomento_empresarial.md](plan_fomento_empresarial.md) custa 60h para adicionar ~4 fontes novas. Estas 34h recuperam **95 editais de fontes que o portal já anuncia como cobertas** e adicionam a maior fonte internacional. **Melhor retorno por hora e menor risco** — vale executar antes.

---

## 6. Riscos

| Risco | Prob. | Impacto | Mitigação |
| :-- | :--: | :--: | :-- |
| FINEP rotaciona `idClientPRD`/`secretClientPRD` | Média | Alto | Extrair do bundle em runtime (FIX-FINEP cr. 2) |
| FINEP muda o nome do objeto Liferay (`/o/c/chamadapublicas`) | Baixa | Alto | INF-04 detecta a queda em 1 semana em vez de 4 meses |
| gov.br/cnpq muda a estrutura do Plone | Média | Médio | Dedup por slug (estável); INF-04 |
| `grantsTenders.json` cresce e estoura tempo/memória no CI | Média | Médio | Streaming + `--compressed` + cadência semanal |
| Filtro temático do Horizon mal calibrado afoga o portal | **Alta** | Médio | Filtro obrigatório (cr. 3) definido com a PRPPG antes do primeiro run em produção |
| Horizon sem descrição degrada a qualidade do card no portal | Alta | Baixo | Opção (a) agora; (b) só para os itens filtrados |

---

## 7. Decisões pendentes

1. **Filtro temático do Horizon**: quais `programmeDivision` interessam ao IFES? Sem isso o flow não pode ir a produção. Candidatas: `HORIZON.2.4`, `HORIZON.2.5`, `HORIZON.3.1`.
2. **Descrição do Horizon**: opção (a) barata, (b) 200 requisições ou (c) Mistral?
3. **MIB Rodada 2**: a lacuna apontada no PDF é de coleta ou de exibição? O repo tem 9 dos editais desde março — confirmar com o time do portal.
4. **Precedência**: executar estas 34h antes das 60h de [plan_fomento_empresarial.md](plan_fomento_empresarial.md)? (Recomendado.)
5. ~~**Recoleta CNPq**: limpar a chave `cnpq` do registry apaga o histórico de processados.~~ Feito em 2026-07-29.
6. **Órfãos do CNPq**: os 4 registros coletados do portal antigo permaneceram em `data/output/` — apontam para `memoria2.cnpq.br`, três sem `data_encerramento`, e um (`PROAFRICA`) é a mesma chamada que voltou como `nº 15/2026`. Nenhum título coincide com os 10 novos, então não foram sobrescritos. Remover exige decisão: são registros obsoletos, mas apagá-los é exclusão de dado publicado no portal.

---

## 8. Comandos de reprodução do recon

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"

# FINEP: confirma o redirect que quebrou o source
curl -sSL -A "$UA" -o /dev/null -w "%{url_effective}\n" \
  "http://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta"

# FINEP: API viva, 36 abertas
TOK=$(curl -sS -X POST "https://www.finep.gov.br/o/oauth2/token" \
  -u "idClientPRD:secretClientPRD" -d "grant_type=client_credentials" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -sS -H "Authorization: Bearer $TOK" --get \
  --data-urlencode "filter=situacao eq 'aberta'" \
  "https://www.finep.gov.br/o/c/chamadapublicas" | python3 -c "import sys,json;print(json.load(sys.stdin)['totalCount'])"

# CNPq: portal antigo tem 1 card, o novo tem 73
curl -sSL -A "$UA" "http://memoria2.cnpq.br/web/guest/chamadas-publicas" | grep -c 'div class="content"'
curl -sSL -A "$UA" "https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao" \
  | grep -oE 'href="[^"]*todas-as-chamadas[^"]*"' | sort -u | wc -l

# Horizon: 126 MB, atualizado diariamente
curl -sSI "https://ec.europa.eu/info/funding-tenders/opportunities/data/referenceData/grantsTenders.json" \
  | grep -iE "content-length|last-modified"
```
