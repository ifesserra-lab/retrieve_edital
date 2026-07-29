# Spec: Fomento Empresarial — EMBRAPII, BNDES, ANEEL, ANP, SENAI

**Autor**: Horizon Project Agent
**Data**: 2026-07-27
**Status**: Draft — aguardando aprovação
**Origem**: [analise_portal_ifes_serra.pdf](analise_portal_ifes_serra.pdf) §2.2 · recorte do [spec_expansao_fontes.md](spec_expansao_fontes.md) Tier B
**Prioridade no PDF**: nº 3 (curto prazo) — "abre acesso ao modelo de financiamento mais ágil do Brasil para ICTs"

---

## 1. Contexto

O PDF classifica o fomento empresarial federal como **ausência total** no portal: nenhuma das 6 fontes que financiam PD&I em arranjo ICT‑empresa é coletada hoje. Este documento cobre as 5 fontes solicitadas e é **baseado em reconhecimento real dos portais**, não em estimativa.

Diferente do resto do backlog, essas fontes atendem um público que hoje o portal não serve: `publico_alvo = empresa | ict-empresa`. Hoje esse filtro retornaria zero resultados.

---

## 2. Reconhecimento executado

**Data da coleta**: 2026-07-27. **Método**: `curl` com User-Agent de navegador, sem JS. Classificação: HTML server‑rendered vs. shell JS, presença de RSS/API, `robots.txt`, permalinks estáveis.

### 2.1 Conformidade com robots.txt

| Host | Regra relevante | Veredito |
| :-- | :-- | :-- |
| `embrapii.org.br` | `User-agent: * / Disallow:` (vazio) + sitemap | Liberado |
| `www.bndes.gov.br` | `Disallow: /wps` **mas** `Allow: /wps/portal/site/home`; `Crawl-delay: 2` | Liberado no caminho‑alvo — **crawl-delay 2s obrigatório** |
| `www.gov.br` | Sem restrição nos caminhos ANEEL/ANP | Liberado |
| `www.portaldaindustria.com.br` | `Disallow: /busca/*`, `*/rss/*`; caminho `/canais/` livre | Liberado — **não usar a busca do site** |

### 2.2 Resultado por fonte

| Fonte | Dificuldade presumida | **Medida** | Evidência coletada |
| :-- | :--: | :--: | :-- |
| **EMBRAPII** | M (8h) | **F (5h)** ⬇ | `/chamadas-publicas/feed/` → RSS 2.0 válido, **31 itens**, `lastBuildDate` 23/07/2026, `content:encoded` com corpo completo. Página de detalhe **server-rendered** (146KB) com cronograma em `<table>` e PDFs em `href`. |
| **BNDES** | M (8h) | **D (16h)** ⬆ | WebSphere Portal. Rotas retornam shell de 8KB (Dojo + `pelev2` web components). A rota com 79KB tem **stack trace Java vazando no HTML** (`at com.ibm.wor…ServletContext.java:147`) e headings `Aviso` — portlet com erro. `sitemap.xml` → 404. Permalinks no formato `!ut/p/z1/04_Sj9…` (estado codificado, **não estáveis**). |
| **ANEEL** | D (16h) | **F (3h)** ⬇ mas **rendimento ~0** | Plone estático. `/chamadas-de-projetos-de-pdi-estrategicos` lista **3 chamadas no total** (2018, 2024, armazenamento). `plone.restapi` presente porém **401** (`Missing 'plone.restapi: Use REST API' permission`). Sem RSS (`/RSS`, `/rss.xml`, `/@@rss.xml` → 404). |
| **ANP** | M (8h) | **fonte inválida** ✕ | A página de PD&I tem 5 links e **nenhuma listagem de chamadas**. Aponta para "investimentos-em-pd-i" e dados abertos. A ANP **regula** a cláusula de PD&I; quem publica chamada é a operadora (Petrobras et al.). |
| **SENAI** | D (12h) | **M (8h)** ⬇ | `plataformainovacao.com.br` redireciona 301 → `portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/`. HTML **estático** (88KB), 31 links, categorias em `/categoria/<slug>/` incluindo `chamada-regional-senai` e `chamada-tecnica-sesi-senai-*`. Não é SPA. |

### 2.3 Reprodutibilidade

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"
curl -sSL -A "$UA" https://embrapii.org.br/chamadas-publicas/feed/ | grep -c "<item>"     # 31
curl -sSL -A "$UA" -o /dev/null -w "%{size_download}\n" \
  "https://www.bndes.gov.br/wps/portal/site/home/onde-atuamos/inovacao/chamadas-publicas" # 8189 = shell
curl -sSL -A "$UA" -H "Accept: application/json" \
  "https://www.gov.br/aneel/pt-br/@search" | head -c 100                                  # 401
```

---

## 3. Decisões que o reconhecimento força

### D1 — Remover a ANP do escopo de coleta

A ANP não é fonte de editais. Manter um scraper apontado para ela produziria um flow que nunca retorna item — custo de manutenção sem receita.

**Alternativas** (a decidir, fora deste escopo):
- **(a)** Página informativa no portal explicando a cláusula de PD&I (equivalente ao tratamento de Lei do Bem/CPSI no §2.4 do PDF) — custo zero de coleta;
- **(b)** Trocar o alvo para as **operadoras** que efetivamente publicam chamadas (Petrobras `petrobras.com.br/canal-de-oportunidades`, Equinor, Shell) — fonte real, ~12h, escopo novo;
- **(c)** Consumir os **dados abertos de PD&I da ANP** — são dados de *investimento executado*, não de oportunidade aberta. Não serve ao portal.

**Recomendação: (a) agora, (b) avaliar depois.**

### D2 — ANEEL entra, mas como fonte de baixo volume

O scraper é barato (3h, Plone estático) porém a página inteira tem 3 chamadas desde 2018. O volume real do P&D ANEEL está nas chamadas das **distribuidoras** — dezenas de portais próprios, sem índice central. Isso era o "D/16h" da estimativa original e **continua verdadeiro para o volume real**.

**Recomendação**: implementar só o scraper barato de gov.br (3h), aceitar o baixo rendimento e **não** perseguir as distribuidoras nesta fase. Reavaliar se a demanda aparecer.

### D3 — BNDES é a fonte mais cara e a de maior risco

Portal com portlet quebrado, sem sitemap, permalinks `!ut/p/z1/...` que codificam estado de navegação — inservíveis como chave de deduplicação. Exige Playwright, `Crawl-delay: 2` e chave de dedup derivada de conteúdo, não de URL.

**Recomendação**: implementar **por último** no bloco, depois que EMBRAPII/SENAI já estiverem entregando valor. Se estourar o orçamento de 16h, cortar sem bloquear o resto.

### D4 — EMBRAPII é a melhor relação valor/esforço do repositório inteiro

RSS estável + detalhe server-rendered + cronograma em tabela HTML. **Não precisa de Playwright nem de OCR Mistral** — o cronograma sai por parsing direto. É também a fonte nº 1 em relevância para ICT‑empresa segundo o próprio PDF.

**Recomendação**: primeira a ser implementada.

---

## 4. Design por fonte

### 4.1 EMBRAPII

| Item | Definição |
| :-- | :-- |
| `fonte_key` | `embrapii` |
| Listagem | `https://embrapii.org.br/chamadas-publicas/feed/` (RSS 2.0) |
| Engine | `requests` + `xml.etree` / `feedparser` — **sem Playwright** |
| Detalhe | `<item><link>` — server-rendered, `requests` + BeautifulSoup |
| Dedup key | `link` (permalink limpo e estável) |
| `orgão_fomento` | `EMBRAPII` (estático) |
| `publico_alvo` | `[empresa, ict-empresa]` (estático) |
| `ambito_geografico` | `nacional` (estático) |
| `modalidade` | `subvenção` por padrão; `fluxo-contínuo` quando o título casar com `/credenciamento|fluxo cont/i` |

**Mapeamento de campos**

| Destino | Origem |
| :-- | :-- |
| `nome` | `<item><title>` |
| `link` | `<item><link>` |
| `descrição` | `<description>` (CDATA, já é o resumo do objeto) |
| `data_abertura` | `<pubDate>` → ISO |
| `cronograma` | `<table>` da página de detalhe: colunas `Atividade` \| `Novos Prazos Limites` → `[{evento, data}]` |
| `data_encerramento` | linha do cronograma que casar `/submiss|encerr|prazo final|entrega/i`; fallback = maior data do cronograma |
| `anexos` | `a[href$=".pdf"]` do detalhe — **dois domínios**: `embrapii.org.br/wp-content/...` e `storage.googleapis.com/uploads-site-embrapii/...` |
| `tags` | `["embrapii", "fomento-empresarial"]` |

**Confirmado no recon**: item `chamada-publica-unidades-embrapii-no-03-2025` traz cronograma legível (`Abertura do processo de seleção 18/12/2025`, `Submissão da proposta de credenciamento (Etapa 1) 30/01/2026`) e 2 PDFs. **0 de 31 itens** trazem PDF no RSS → a visita ao detalhe é obrigatória.

**Cuidado**: o RSS traz o histórico (itens de 2025 e anteriores). Aplicar o filtro de ano corrente já usado em `CnpqSource` e `CapesSource`.

**Esforço**: 5h (após INF-01).

---

### 4.2 SENAI / Plataforma Inovação

| Item | Definição |
| :-- | :-- |
| `fonte_key` | `senai` |
| Listagem | `https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/` |
| Engine | `requests` — HTML estático confirmado |
| Estrutura | hub de categorias → `/categoria/<slug>/` → chamadas |
| Dedup key | URL da categoria/chamada |
| `orgão_fomento` | `SENAI` / `SESI-SENAI` conforme o slug |
| `publico_alvo` | `[empresa, ict-empresa]` |
| `modalidade` | `subvenção` |

Percurso em dois níveis: a raiz lista categorias (`chamada-regional-senai`, `chamada-tecnica-sesi-senai-evolucao-da-e`, `empreendedorismo-industrial-*`, `ecossistemas-de-inovacao-em-saude-*`); cada categoria lista chamadas e resultados.

**Filtro necessário**: as categorias têm âncora `#resultados` — separar *chamada aberta* de *resultado divulgado*. Resultado não é oportunidade; descartar ou marcar `status`.

**Restrição robots**: `Disallow: /busca/*` e `*/rss/*` → navegar apenas por links de `/canais/`, nunca pela busca.

**Esforço**: 8h.

---

### 4.3 ANEEL P&D

| Item | Definição |
| :-- | :-- |
| `fonte_key` | `aneel` |
| Listagem | `https://www.gov.br/aneel/pt-br/assuntos/programa-de-pesquisa-desenvolvimento-e-inovacao/chamadas-de-projetos-de-pdi-estrategicos` |
| Engine | `requests` — Plone estático |
| Dedup key | URL da subpágina (estável, slug legível) |
| `orgão_fomento` | `ANEEL` |
| `publico_alvo` | `[empresa, ict-empresa]` |
| `modalidade` | `subvenção` (recurso obrigatório de 1% da receita das distribuidoras) |

Padrão: pasta Plone cujas subpáginas são as chamadas (`chamada-n-o-023-2024-hidrogenio-no-contexto-do-setor-eletrico-brasileiro`, `sistemas-de-armazenamento-de-energia`). PDFs em dois hosts: `git.aneel.gov.br/publico/centralconteudo/-/raw/main/...` e `www2.aneel.gov.br/cedoc/...`.

**Expectativa de volume: 0 a 2 chamadas novas por ano.** O alerta de "fonte retornou 0 itens" precisa ser *desligado* para esta fonte, ou vira ruído permanente.

**Esforço**: 3h.

---

### 4.4 BNDES

| Item | Definição |
| :-- | :-- |
| `fonte_key` | `bndes` |
| Listagem | `.../site/home/transparencia/chamadas-publicas-selecao-projetos` (+ `/financiamento/produto/bndes-funtec`) |
| Engine | **Playwright** — obrigatório |
| Dedup key | **hash(título normalizado + órgão)** — URLs `!ut/p/z1/...` não servem |
| `orgão_fomento` | `BNDES` |
| `publico_alvo` | `[empresa, ict-empresa]` |
| `modalidade` | `crédito` \| `subvenção` (Funtec é não-reembolsável; distinguir por rótulo) |

**Requisitos específicos**
- respeitar `Crawl-delay: 2` do `robots.txt` (≥2s entre requisições ao host);
- detectar e falhar explicitamente quando a página vier com portlet em erro (heurística: presença de `com.ibm.` ou heading `Aviso` no corpo) — **não** persistir edital extraído de página quebrada;
- sem `sitemap.xml`, a descoberta depende da navegação renderizada;
- timeout maior no runner (portal lento e instável).

**Esforço**: 16h. **Maior risco do bloco** — se o portlet estiver quebrado de forma persistente, a fonte pode ser inviável sem contato institucional com o BNDES.

---

### 4.5 ANP — **não implementar como source**

Ver §3/D1. Entrega desta spec: registrar a conclusão do reconhecimento e a recomendação de página informativa no portal. **Esforço de coleta: 0h.**

---

## 5. Infraestrutura compartilhada necessária

| ID | Componente | Justificativa | Horas |
| :-- | :-- | :-- | :--: |
| **INF-01** | `RssListingSource` — engine RSS reutilizável (`ISource`) | Nenhum source atual lê RSS. Habilita EMBRAPII hoje e várias FAPs depois (WordPress é padrão de fato em portais públicos). | 6h |
| **INF-02** | Campos empresariais no `EditalDomain`: `publico_alvo`, `modalidade`, `ambito_geografico`, `valor_estimado`, `trl_exigido`, `fonte_key` | Sem `publico_alvo`, o filtro "Para Empresas" do portal (prioridade nº 1 do PDF) não tem dado para filtrar — as 4 fontes entrariam invisíveis. Preenchimento **estático** por fonte (§4), sem custo de LLM. | 12h |
| **INF-03** | Runner resiliente + rate limit por host | [run_all_flows.py:124](../scripts/run_all_flows.py#L124) hoje aborta na primeira falha. Com o BNDES instável no meio da fila, uma indisponibilidade dele zera a coleta diária das outras 10 fontes. Inclui `Crawl-delay` por host. | 8h |
| | **Subtotal** | | **26h** |

**INF-02 é pré-requisito de valor**: sem ele o trabalho de coleta é feito mas o portal não consegue exibir o recorte empresarial que motivou a demanda.

Integração no runner: 4 novas entradas em `FLOW_COMMANDS` e `REGISTRY_KEYS` (`embrapii`, `senai`, `aneel`, `bndes`) em [scripts/run_all_flows.py](../scripts/run_all_flows.py).

---

## 6. Backlog

Formato alinhado a [docs/backlog.md](backlog.md). Cada história exige `.feature` em `docs/features/` e `step_defs` em `tests/step_defs/`, conforme a convenção vigente.

| Tipo | ID | História | Pts | Horas |
| :--: | :-- | :-- | :--: | :--: |
| 🛠️ | INF-01 | **Engine RSS reutilizável**<br>`RssListingSource` aderente a `ISource`, parseando RSS 2.0 em `RawEdital`. Critérios: (1) extrai `title`, `link`, `pubDate`, `description`; (2) filtra por ano de referência via `get_reference_year()`; (3) ignora itens já presentes no registry; (4) erro de rede/XML inválido não derruba o flow. | 5 | 6h |
| 🛠️ | INF-02 | **Campos de fomento empresarial no domínio**<br>Novos campos em `EditalDomain` (§5), com default para não invalidar os JSONs já em `data/output/`. Critérios: (1) `publico_alvo`, `modalidade`, `ambito_geografico` obrigatórios e populáveis estaticamente pelo source; (2) `valor_estimado` e `trl_exigido` opcionais; (3) `fonte_key` gravado em todo edital; (4) JSONs antigos seguem carregáveis. | 5 | 12h |
| 📚 | US-EMB | **Source e flow EMBRAPII**<br>`EmbrapiiSource` (RSS + detalhe) e `ingest_embrapii_flow`. Critérios: (1) lê o feed e coleta ≥1 chamada; (2) descarta chamadas com encerramento anterior ao ano corrente; (3) extrai cronograma da tabela do detalhe sem usar Mistral; (4) coleta PDFs dos dois domínios (`wp-content` e `storage.googleapis.com`); (5) ignora permalinks já no registry `embrapii`; (6) marca `publico_alvo = [empresa, ict-empresa]`. | 5 | 5h |
| 📚 | US-ANEEL | **Source e flow ANEEL P&D**<br>`AneelSource` sobre a pasta Plone de PDI estratégicos. Critérios: (1) coleta as subpáginas de chamada da pasta; (2) coleta PDFs de `git.aneel.gov.br` e `www2.aneel.gov.br`; (3) dedup por URL da subpágina; (4) retorno vazio é resultado **válido**, não falha. | 3 | 3h |
| 📚 | US-SENAI | **Source e flow SENAI/Plataforma Inovação**<br>`SenaiSource` em dois níveis (hub → categoria). Critérios: (1) descobre categorias a partir de `/canais/plataforma-inovacao-para-industria/`; (2) distingue chamada aberta de `#resultados`; (3) nunca acessa `/busca/*` nem `*/rss/*` (robots); (4) dedup por URL. | 5 | 8h |
| 🛠️ | INF-03 | **Runner resiliente e rate limit por host**<br>Critérios: (1) falha de uma fonte não interrompe as demais; (2) exit code ≠ 0 se qualquer fonte falhar; (3) timeout por fonte configurável; (4) `Crawl-delay` respeitado por host (BNDES = 2s); (5) uma linha por fonte em `docs/flow_processing_log.md`; (6) `--only <fontes>`. | 5 | 8h |
| 📚 | US-BNDES | **Source e flow BNDES**<br>`BndesSource` com Playwright. Critérios: (1) renderiza a listagem e extrai chamadas; (2) dedup por hash de título+órgão, **não** por URL `!ut/p/`; (3) detecta página com portlet em erro (`com.ibm.` / heading `Aviso`) e aborta a fonte sem persistir dado parcial; (4) respeita crawl-delay 2s; (5) distingue Funtec (subvenção) de crédito. | 8 | 16h |
| 📋 | DOC-ANP | **Registrar decisão sobre a ANP**<br>Documentar que a ANP não publica editais e propor página informativa no portal. Sem código. | 1 | 2h |
| | | **Total** | **37** | **60h** |

---

## 7. Cronograma

**Premissa**: 1 desenvolvedor, 30h úteis/semana.

| Onda | Conteúdo | Horas | Entrega |
| :--: | :-- | :--: | :-- |
| **1** | INF-01 + US-EMB + US-ANEEL + DOC-ANP | 16h | **2 fontes novas em ~3 dias.** EMBRAPII é a de maior relevância do bloco segundo o PDF. |
| **2** | INF-02 + US-SENAI | 20h | 3 fontes com `publico_alvo` populado → o filtro "Para Empresas" do portal passa a ter dado real. |
| **3** | INF-03 + US-BNDES | 24h | 4 fontes; runner deixa de ser ponto único de falha. |
| | **Total** | **60h** | **2 semanas** |

Com buffer de risco de 25% (BNDES instável): **75h ≈ 2,5 semanas**.

**Comparação com a estimativa cega**: o [spec_expansao_fontes.md](spec_expansao_fontes.md) previa 52h só de sources para as 5 fontes. O recon derrubou para **32h de sources** (EMBRAPII 8→5, ANEEL 16→3, SENAI 12→8, ANP 8→0, BNDES 8→16), e expôs 26h de infra que a estimativa cega não tinha visto. Saldo próximo, composição bem diferente — e agora com uma fonte a menos e um risco nomeado.

**Ponto de corte**: se for preciso cortar, corte a **Onda 3**. As Ondas 1–2 entregam 3 das 4 fontes viáveis por 36h e não dependem do portal mais frágil.

---

## 8. Riscos

| Risco | Prob. | Impacto | Mitigação |
| :-- | :--: | :--: | :-- |
| BNDES: portlet permanentemente quebrado torna a fonte inviável | Média | Alto | Detecção explícita de erro (US-BNDES cr. 3); timebox de 16h; cortar sem bloquear as demais |
| BNDES: permalink `!ut/p/z1/` muda a cada sessão → duplicatas na saída | **Alta** | Médio | Dedup por hash de conteúdo, decidido em projeto |
| EMBRAPII muda o tema WordPress e o RSS sai do ar | Baixa | Médio | Fallback para a página de detalhe via sitemap (`sitemap_index.xml` existe e está declarado no robots) |
| ANEEL gera 0 itens por meses e dispara alerta falso | **Alta** | Baixo | Fonte marcada como *baixo volume*; alerta de "0 itens" desabilitado para ela |
| SENAI mistura chamada aberta com resultado divulgado | Média | Médio | Critério explícito de separação (US-SENAI cr. 2) |
| Playwright do BNDES estoura o tempo do job no GitHub Actions | Média | Baixo | INF-03 (timeout por fonte) + mover BNDES para cadência semanal |
| gov.br libera `plone.restapi` e o scraper HTML vira dívida | Baixa | Baixo | Aceitar; a migração seria barata |

---

## 9. Métricas de sucesso

- Editais com `publico_alvo ∈ {empresa, ict-empresa}` em `data/output/`: **0 → >0** (é a lacuna nº 1 do PDF).
- 4 fontes novas no `registry/processed_editais.json`: `embrapii`, `senai`, `aneel`, `bndes`.
- Falha de uma fonte deixa de zerar a coleta diária (verificável derrubando o BNDES de propósito).
- EMBRAPII com cronograma preenchido **sem chamada ao Mistral** — economia direta de custo por edital.

---

## 10. Decisões pendentes

1. **ANP**: página informativa (recomendado), alvo trocado para operadoras (Petrobras et al., +12h), ou fora do escopo?
2. **BNDES**: autorizar as 16h com risco de inviabilidade, ou adiar até haver demanda concreta?
3. **ANEEL**: aceitar a fonte de baixíssimo volume (3h), ou também não vale o custo de manutenção?
4. **Cadência**: EMBRAPII/SENAI/ANEEL diários e BNDES semanal (recomendado), ou tudo diário?
5. **INF-02**: preencher `valor_estimado` e `trl_exigido` via Mistral, ou só quando explícito no texto (custo zero)?

---

## 11. Próximo passo

Onda 1 — INF-01 + EMBRAPII. 16h, dependência zero de decisão pendente, e coloca no ar a fonte que o PDF aponta como a mais relevante para o modelo ICT‑empresa.
