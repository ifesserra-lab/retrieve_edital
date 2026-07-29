# Spec: Expansão de Fontes de Fomento (Coleta)

**Autor**: Horizon Project Agent
**Data**: 2026-07-27
**Status**: Draft — aguardando aprovação
**Origem**: `Analise_Portal_IFES_Serra.pdf` (Análise das Lacunas de Fontes de Fomento — abr/2026)
**Escopo do repositório**: `retrieve_edital` (camada de coleta ETL). O portal de exibição (`ifesserra-lab.github.io/portal_edital`) é outro repositório.

---

## 1. Contexto

O documento de análise identificou que o Portal de Editais indexa 8 fontes e deixa de fora três camadas inteiras de fomento: as 25 FAPs estaduais não-ES, o fomento empresarial federal e os programas internacionais.

Este repositório hoje mantém **7 flows** (`FAPES`, `FINEP`, `CONIF`, `PRPPG_IFES`, `PROEX_IFES`, `CAPES`, `CNPQ`), todos aderentes a `ISource → ITransform → ISink`.

**Divergência detectada**: o portal exibe *Belmont Forum / SBEP* como fonte monitorada, mas **não existe flow correspondente neste repositório** — hoje essa fonte é curadoria manual. Precisa entrar no inventário.

### 1.1 Divisão de responsabilidade com o portal

Das 6 prioridades do PDF, apenas 4 são deste repositório:

| Prioridade PDF | Ação | Repositório responsável |
| :--: | :-- | :-- |
| 1 | Filtro "Para Empresas" + indexar FINEP MIB Rodada 2 | `portal_edital` (front) — coleta FINEP já existe |
| 2 | CONFAP + 5 maiores FAPs | **`retrieve_edital`** |
| 3 | EMBRAPII + BNDES Funtec | **`retrieve_edital`** |
| 4 | Seção Internacionais (Horizon, EIC, CYTED) | **`retrieve_edital`** + front |
| 5 | GitHub Action semanal de scraping | **`retrieve_edital`** (já existe diário — precisa endurecer) |
| 6 | Campos `público-alvo`, `valor`, `TRL` | **`retrieve_edital`** (schema) + front (filtros) |

---

## 2. Objetivo e escopo

**Objetivo**: elevar a cobertura de coleta automatizada de 7 para ~40 fontes, sem multiplicar por 5 o custo de manutenção.

### Dentro do escopo
- Novos sources/flows para FAPs, fomento empresarial, internacionais.
- Extensão do modelo de domínio com os campos do §3.2 do PDF.
- Refatoração do núcleo para suportar fontes declarativas (config) em vez de uma classe Python por portal.
- Endurecimento do runner (hoje `fail-fast`: uma fonte quebrada derruba as 40).

### Fora do escopo
- Redesenho de navegação do portal (§3.1 do PDF) — outro repositório.
- Páginas informativas de instrumentos fiscais (Lei do Bem, Lei de Informática, CPSI) — conteúdo estático, não é coleta. **Exceção**: encomenda tecnológica no `compras.gov.br` tem API e entra como fonte real.
- Autenticação em portais que exijam login institucional.

---

## 3. Inventário de fontes-alvo

Legenda de dificuldade: **F** fácil (HTML estático / RSS / API) · **M** média (paginação, página de detalhe, PDF) · **D** difícil (SPA JS, postback ASP.NET, anti-bot/403, dados dispersos).

Dificuldades marcadas com `?` são **presumidas** — só se confirmam após o recon (US-01). O cronograma do §6 já embute essa incerteza.

### 3.1 Tier A — FAPs estaduais + hub CONFAP

| Prio | Sigla | UF | Portal | Dif. | Esforço |
| :--: | :-- | :-- | :-- | :--: | :--: |
| **P0** | CONFAP | Hub nacional | `confap.org.br` | M? | 8h |
| P1 | FAPESP | SP | `fapesp.br/chamadas` | M? | 6h |
| P1 | FAPERJ | RJ | `faperj.br/p_editais.phtml` | M? | 6h |
| P1 | FAPEMIG | MG | `fapemig.br/chamadas` | M? | 6h |
| P1 | FAPERGS | RS | `fapergs.rs.gov.br/editais` | M? | 6h |
| P1 | FAPESC | SC | `fapesc.sc.gov.br/editais` | M? | 6h |
| P2 | FAPESB | BA | `fapesb.ba.gov.br/chamadas-publicas` | M? | 5h |
| P2 | FAPEAM | AM | `fapeam.am.gov.br` | M? | 5h |
| P2 | FAPDF | DF | `fap.df.gov.br/editais` | M? | 5h |
| P2 | FACEPE | PE | `facepe.br/editais` | M? | 5h |
| P2 | FUNCAP | CE | `funcap.ce.gov.br/chamadas` | M? | 5h |
| P2 | FAPPR | PR | `fappr.pr.gov.br` | M? | 5h |
| P2 | FAPEMAT | MT | `fapemat.mt.gov.br` | M? | 5h |
| P2 | FUNDECT | MS | `fundect.ms.gov.br` | M? | 5h |
| P2 | FAPEG | GO | `fapeg.go.gov.br/editais` | M? | 5h |
| P2 | FAPEMA | MA | `fapema.br/chamadas` | M? | 5h |
| P2 | FAPESPA | PA | `fapespa.pa.gov.br` | M? | 5h |
| P3 | FAPEAL | AL | `fapeal.al.gov.br` | ? | 4h |
| P3 | FAPEPI | PI | `fapepi.pi.gov.br` | ? | 4h |
| P3 | FAPERO | RO | `fapero.ro.gov.br` | ? | 4h |
| P3 | FAPAC | AC | `fapac.ac.gov.br` | ? | 4h |
| P3 | FAPEAP | AP | `fapeap.ap.gov.br` | ? | 4h |
| P3 | FAPT | TO | `fapt.to.gov.br` | ? | 4h |
| P3 | FAPERN | RN | `fapern.rn.gov.br` | ? | 4h |
| P3 | FAPESQ | PB | `fapesq.pb.gov.br` | ? | 4h |
| P3 | FAPITEC | SE | `fapitec.se.gov.br` | ? | 4h |

*(FAPES/ES já coberta pelo flow existente.)*

**Subtotal Tier A**: 8h (CONFAP) + 30h (P1) + 55h (P2) + 36h (P3) = **129h** — assumindo que ~70% caiam em config declarativa. Ver §5.1 para o multiplicador de risco.

### 3.2 Tier B — Fomento empresarial federal

| Prio | Fonte | Portal | Particularidade | Dif. | Esforço |
| :--: | :-- | :-- | :-- | :--: | :--: |
| P1 | EMBRAPII | `embrapii.org.br/chamadas-publicas` | fluxo contínuo + chamadas datadas | M | 8h |
| P1 | BNDES | `bndes.gov.br/editais` | Funtec, BNDESPar, Smart Factory | M | 8h |
| P2 | SENAI / Plataforma Inovação | `plataformainovacao.com.br` | provável SPA JS | D? | 12h |
| P2 | ANP P&D | `anp.gov.br/pesquisa-desenvolvimento` | publicação contínua via operadoras | M | 8h |
| P3 | SEBRAE + EMBRAPII | `sebrae.com.br/inovacao` | fluxo contínuo, **sem edital** | F | 4h |
| P3 | ANEEL P&D | `aneel.gov.br/pesquisa-e-desenvolvimento` | chamadas espalhadas por N distribuidoras | D | 16h |
| P3 | Encomenda tecnológica | `compras.gov.br` (API) | API pública, filtro Lei 13.243/2016 | M | 12h |

**Subtotal Tier B**: **68h**

### 3.3 Tier C — Internacionais

| Prio | Fonte | Mecanismo | Dif. | Esforço |
| :--: | :-- | :-- | :--: | :--: |
| P1 | Horizon Europe | **API REST pública** — `api.tech.ec.europa.eu/open-data` | M | 12h |
| P1 | EIC Accelerator | mesmo Funding & Tenders Portal (reuso da API) | F | 4h |
| P2 | CYTED | `cyted.org/convocatorias` — HTML estático | F | 4h |
| P2 | Belmont Forum / SBEP | **lacuna atual** — exibido no portal sem coleta | M | 8h |
| P3 | Eureka / Eurostars | `eurekanetwork.org` | M | 8h |
| P3 | IDB Lab (BID) | `bidlab.org` | M | 8h |

**Subtotal Tier C**: **44h**

O volume da Horizon exige filtro por área temática antes do sink, senão inunda `data/output/` com centenas de chamadas irrelevantes para o IFES.

---

## 4. Mudanças arquiteturais requeridas

Adicionar 33 fontes copiando o padrão atual (uma classe Python + um `.feature` + um `step_defs` por portal) produziria ~6.000 linhas de parser quase-duplicado. Três mudanças evitam isso.

### 4.1 Source declarativo (config-driven)

Nova classe `DeclarativeHtmlSource(ISource[RawEdital])`, parametrizada por um YAML em `config/sources/*.yml`:

```yaml
# config/sources/fapemig.yml
key: fapemig
agency: FAPEMIG
listing_url: https://fapemig.br/chamadas
engine: requests          # requests | playwright | curl
item_selector: "div.chamada"
fields:
  title:   { selector: "h3 a", attr: text }
  link:    { selector: "h3 a", attr: href }
  deadline:{ selector: ".prazo", parser: dd_mm_yyyy }
detail:
  enabled: true
  description_selector: ".conteudo"
  pdf_selector: "a[href$='.pdf']"
filters:
  min_deadline_year: current
dedup_key: link
scope:
  publico_alvo: [pesquisador]
  ambito: estadual-MG
```

Sources com HTML atípico continuam como classe Python dedicada (mecanismo de escape). **Meta: ≥70% das FAPs cobertas por YAML.**

- **Padrão**: Strategy (engine de fetch) + Factory (`SourceFactory.from_config(path)`), coerente com `docs/development_guidelines.md` §2.
- Os 7 sources existentes **não são migrados** nesta fase (OCP: aberto para extensão, fechado para modificação).

### 4.2 Runner resiliente

`scripts/run_all_flows.py:124` hoje faz `raise SystemExit` na primeira falha. Com 40 fontes, uma FAP fora do ar zera a coleta diária inteira.

Mudanças:
- isolamento de falha por fonte (coleta erros, segue adiante, exit code ≠ 0 no fim);
- timeout por fonte (default 10min);
- paralelismo controlado (`ThreadPoolExecutor`, respeitando o limite do Mistral);
- execução seletiva: `--only fapemig,confap` e `--tier A`;
- `docs/flow_processing_log.md` com uma linha por fonte por execução;
- cadência dividida: P1 diário, P2/P3 semanal (o PDF pede semanal; diário × 40 fontes é gasto sem retorno).

### 4.3 Deduplicação entre fontes

CONFAP agrega chamadas das próprias FAPs → o mesmo edital chegará por dois caminhos. Necessário chave canônica (`orgão_fomento` normalizado + hash do título normalizado + `data_encerramento`) e política de precedência: **fonte primária (a FAP) vence o agregador (CONFAP)**.

---

## 5. Modelo de dados

`EditalDomain` ganha os campos do §3.2 do PDF:

| Campo | Tipo | Valores | Obrigatório |
| :-- | :-- | :-- | :--: |
| `publico_alvo` | `List[str]` | `pesquisador` \| `estudante` \| `empresa` \| `ict-empresa` \| `internacional` | sim |
| `valor_estimado` | `Optional[float]` | R$, `None` quando não declarado | não |
| `modalidade` | `str` | `subvenção` \| `bolsa` \| `crédito` \| `prêmio` \| `infraestrutura` \| `fluxo-contínuo` | sim |
| `ambito_geografico` | `str` | `nacional` \| `estadual-<UF>` \| `internacional` \| `regional` | sim |
| `trl_exigido` | `Optional[str]` | ex.: `"6-9"` | não |
| `fonte_key` | `str` | chave do source (rastreabilidade/dedup) | sim |

Preenchimento em duas vias: **estático** (o que o YAML já sabe da fonte — uma FAP estadual é sempre `estadual-<UF>`) e **inferido** (Mistral, para `valor_estimado`, `modalidade` e `trl_exigido` a partir do texto do edital). O inferido só é chamado quando o estático não resolve — controle de custo.

**Compatibilidade**: campos novos com default; JSONs antigos em `data/output/` permanecem válidos. Backfill via script separado, opcional.

---

## 6. Planejamento

**Premissas**: 1 desenvolvedor, 30h úteis/semana. Pontos na escala já usada no `docs/backlog.md` (5 pts ≈ um source novo).

### Fase 0 — Recon e fundação (Sprint 1)

| ID | História | Pts | Horas |
| :-- | :-- | :--: | :--: |
| US-01 | Script de reconhecimento: para os 38 portais-alvo, classificar status HTTP, presença de RSS/API, necessidade de JS, `robots.txt`, seletor candidato de listagem. Saída: `docs/source_recon_report.md`. | 5 | 8h |
| US-02 | `DeclarativeHtmlSource` + `SourceFactory` + schema YAML validado, com BDD. | 8 | 16h |
| US-03 | Extensão do `EditalDomain` (§5) + normalizer + testes. | 5 | 12h |
| US-04 | Runner resiliente: isolamento de falha, timeout, `--only`, `--tier`, paralelismo. | 5 | 8h |
| US-05 | Dedup entre fontes com precedência primária > agregador. | 3 | 6h |
| | **Subtotal** | **26** | **50h** |

**US-01 é bloqueante e barata.** Sem ela, toda estimativa de Tier A é chute — os `?` do §3 viram números reais e o cronograma abaixo pode ser recalibrado antes de qualquer compromisso.

### Fase 1 — Maior valor por hora (Sprints 2–3)

CONFAP + 5 maiores FAPs + EMBRAPII + BNDES + Horizon/EIC. Cobre as prioridades 2, 3 e 4 do PDF.

| Bloco | Horas |
| :-- | :--: |
| CONFAP (hub) | 8h |
| 5 FAPs P1 (FAPESP, FAPERJ, FAPEMIG, FAPERGS, FAPESC) | 30h |
| EMBRAPII + BNDES | 16h |
| Horizon Europe (API) + EIC | 16h |
| **Subtotal** | **70h** |

### Fase 2 — Ampliação (Sprints 4–6)

| Bloco | Horas |
| :-- | :--: |
| 11 FAPs P2 | 55h |
| ANP P&D, SENAI, SEBRAE | 24h |
| CYTED, Belmont Forum (fecha a lacuna atual do portal) | 12h |
| **Subtotal** | **91h** |

### Fase 3 — Cauda longa (Sprints 7–9)

| Bloco | Horas |
| :-- | :--: |
| 9 FAPs P3 | 36h |
| ANEEL P&D (N distribuidoras) | 16h |
| Encomenda tecnológica (compras.gov API) | 12h |
| Eureka/Eurostars, IDB Lab | 16h |
| **Subtotal** | **80h** |

### 6.1 Consolidado

| Fase | Horas | Semanas (30h) | Fontes entregues | Cobertura acumulada |
| :-- | :--: | :--: | :--: | :--: |
| 0 — Fundação | 50h | 1,7 | 0 | 7 |
| 1 — Alto valor | 70h | 2,3 | 9 | 16 |
| 2 — Ampliação | 91h | 3,0 | 16 | 32 |
| 3 — Cauda longa | 80h | 2,7 | 14 | 46 |
| **Total** | **291h** | **9,7** | **39** | **46** |

Com buffer de risco de 25% (portais quebrados, anti-bot, retrabalho pós-recon): **~364h ≈ 12 semanas** para o escopo completo.

**Recomendação: parar e reavaliar ao fim da Fase 1.** Fases 0+1 = 120h ≈ 4 semanas entregam CONFAP + as 5 FAPs que concentram a maior parte do orçamento estadual de C&T + o fomento empresarial de maior relevância + Horizon. É a maior parte do valor por ~1/3 do esforço. A cauda longa (Fase 3) tem 9 FAPs de estados pequenos, com baixo volume de editais e custo de manutenção idêntico ao das grandes.

---

## 7. Riscos

| Risco | Prob. | Impacto | Mitigação |
| :-- | :--: | :--: | :-- |
| **Manutenção linear**: 40 scrapers quebram ao ritmo de mudanças dos portais | Alta | Alto | Config declarativa (mudança de seletor = 1 linha de YAML, sem deploy de código); alerta automático quando uma fonte retorna 0 itens 3 execuções seguidas |
| Custo Mistral escala com o nº de fontes | Alta | Médio | Preenchimento estático prioritário; OCR só no PDF principal; teto mensal de chamadas com degradação para modo sem-OCR |
| Portais estaduais instáveis / 403 (já ocorrido com PROEX/IFES) | Alta | Médio | Fallback `curl` já existente promovido a engine reutilizável; runner resiliente (US-04) |
| Duplicação CONFAP × FAPs | Certa | Médio | US-05 (dedup canônico) |
| SPA JS exige Playwright em massa (CI lento/caro) | Média | Médio | Engine por fonte; Playwright só onde o recon comprovar necessidade |
| Volume Horizon Europe inunda a saída | Média | Médio | Filtro temático obrigatório antes do sink |
| `robots.txt` / ToS proibindo coleta | Baixa | Alto | Verificação no recon (US-01); rate limit educado (≥2s entre requisições no mesmo host); fonte reprovada vira link manual no portal |
| Tempo do job diário estoura o limite do GitHub Actions | Média | Baixo | Split P1 diário / P2-P3 semanal + paralelismo |

---

## 8. Métricas de sucesso

- Fontes coletadas automaticamente: 7 → 46.
- Taxa de sucesso por execução ≥ 95% das fontes ativas.
- Editais novos indexados por semana (baseline a medir na Fase 0).
- Editais com `publico_alvo = empresa | ict-empresa` > 0 (hoje efetivamente zero — é a lacuna nº 1 do PDF).
- Manutenção corretiva ≤ 4h/semana após a Fase 2.

---

## 9. Decisões pendentes

1. **Escopo final**: parar na Fase 1 (4 semanas, 16 fontes) ou ir até a Fase 3 (12 semanas, 46 fontes)?
2. **CONFAP como substituto ou complemento das FAPs?** Se o hub agregar chamadas com qualidade suficiente, as 9 FAPs P3 podem ser dispensadas — economia de ~36h de dev e de manutenção permanente. Decidir após o recon.
3. **Teto de custo Mistral/mês** — define se `valor_estimado` e `trl_exigido` são inferidos por LLM ou só extraídos quando explícitos no texto.
4. **Cadência**: diário para tudo, ou P1 diário + P2/P3 semanal (recomendado)?
5. **Instrumentos fiscais** (Lei do Bem, CPSI): páginas estáticas do portal ou ficam fora?

---

## 10. Próximo passo

Executar **US-01 (recon, 8h)**. É a única tarefa que transforma as estimativas presumidas do §3 em números confiáveis, e o custo de errar essa medição é o cronograma inteiro.
