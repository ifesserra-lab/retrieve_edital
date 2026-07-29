# Plano de Execução: Fomento Empresarial

**Status**: 🔵 Não iniciado
**Criado**: 2026-07-27
**Spec de referência**: [spec_fomento_empresarial.md](spec_fomento_empresarial.md)
**Recon**: executado em 2026-07-27 — dados dos portais medidos, não presumidos

> **Como processar este arquivo**: cada tarefa é autocontida (arquivos a criar, critérios de aceite, comando de verificação). Executar na ordem das ondas; dentro de uma onda, respeitar `Depende de`. Ao concluir, trocar `[ ]` por `[x]` e atualizar o **Status** no topo. Tarefas bloqueadas por decisão de negócio estão marcadas 🔒 e **não devem ser iniciadas** sem resposta do §5.

---

## 1. Resumo executável

| Onda | Tarefas | Horas | Entrega |
| :--: | :-- | :--: | :-- |
| 1 | INF-01, US-EMB, US-ANEEL, DOC-ANP | 16h | 2 fontes novas, sem dependência de decisão |
| 2 | INF-02, US-SENAI | 20h | filtro "Para Empresas" do portal passa a ter dado |
| 3 | INF-03, US-BNDES | 24h | runner deixa de ser ponto único de falha |
| | **Total** | **60h** | 4 fontes (+25% buffer = 75h) |

**Fora do escopo**: ANP como source (não publica editais — ver DOC-ANP).

---

## 2. Onda 1 — 16h

### [ ] INF-01 · Engine RSS reutilizável · 6h

**Depende de**: nada.
**Criar**: `src/components/sources/rss_listing_source.py`, `docs/features/ingest_rss_listing.feature`, `tests/step_defs/test_rss_listing_source.py`

`RssListingSource(ISource[RawEdital])` — nenhum source atual lê RSS; habilita EMBRAPII agora e portais WordPress depois.

Critérios de aceite:
1. extrai `title`, `link`, `pubDate`, `description` de RSS 2.0 em `RawEdital`;
2. converte `pubDate` (RFC 822) para ISO `YYYY-MM-DD`;
3. filtra por ano de referência via `get_reference_year()` de [src/config.py](../src/config.py);
4. ignora itens cujo `link` já esteja no conjunto `processed_urls`;
5. erro de rede ou XML inválido retorna lista vazia e loga o erro — não propaga exceção.

Verificar: `pytest tests/step_defs/test_rss_listing_source.py`

---

### [ ] US-EMB · Source e flow EMBRAPII · 5h

**Depende de**: INF-01.
**Criar**: `src/components/sources/embrapii_source.py`, `src/flows/ingest_embrapii_flow.py`, `docs/features/ingest_embrapii.feature`, `tests/step_defs/test_embrapii_source.py`
**Alterar**: [scripts/run_all_flows.py](../scripts/run_all_flows.py) (`FLOW_COMMANDS` + `REGISTRY_KEYS`), [docs/etl_architecture.md](etl_architecture.md)

Dados confirmados no recon:

| Item | Valor |
| :-- | :-- |
| Feed | `https://embrapii.org.br/chamadas-publicas/feed/` — RSS 2.0, 31 itens |
| Detalhe | server-rendered, `requests` + BeautifulSoup — **sem Playwright** |
| Cronograma | `<table>` do detalhe, colunas `Atividade` \| `Novos Prazos Limites` |
| Anexos | `a[href$=".pdf"]` em **dois domínios**: `embrapii.org.br/wp-content/…` e `storage.googleapis.com/uploads-site-embrapii/…` |
| PDFs no RSS | **0 de 31** → visita ao detalhe é obrigatória |
| `registry` key | `embrapii` |

Valores estáticos: `orgão_fomento = "EMBRAPII"`, `publico_alvo = [empresa, ict-empresa]`, `ambito_geografico = nacional`, `tags = ["embrapii", "fomento-empresarial"]`.

Critérios de aceite:
1. lê o feed e coleta ≥1 chamada;
2. descarta chamadas com `data_encerramento` anterior ao ano corrente (o feed traz histórico de 2025 e antes);
3. extrai cronograma da tabela do detalhe **sem chamar o Mistral**;
4. coleta PDFs dos dois domínios;
5. `data_encerramento` = linha do cronograma que casar `/submiss|encerr|prazo final|entrega/i`; fallback = maior data;
6. ignora permalinks já registrados em `registry/processed_editais.json` chave `embrapii`;
7. o flow registra os permalinks processados após o sink.

Verificar: `python -m src.flows.ingest_embrapii_flow && ls data/output | grep -ci embrapii`

---

### [ ] US-ANEEL · Source e flow ANEEL P&D · 3h

**Depende de**: nada.
**Criar**: `src/components/sources/aneel_source.py`, `src/flows/ingest_aneel_flow.py`, `docs/features/ingest_aneel.feature`, `tests/step_defs/test_aneel_source.py`
**Alterar**: `scripts/run_all_flows.py`, `docs/etl_architecture.md`

| Item | Valor |
| :-- | :-- |
| Listagem | `https://www.gov.br/aneel/pt-br/assuntos/programa-de-pesquisa-desenvolvimento-e-inovacao/chamadas-de-projetos-de-pdi-estrategicos` |
| Engine | `requests` — Plone estático |
| Estrutura | pasta Plone; cada chamada é subpágina com slug legível |
| PDFs | `git.aneel.gov.br/publico/centralconteudo/-/raw/main/…` e `www2.aneel.gov.br/cedoc/…` |
| `registry` key | `aneel` |

⚠ **Volume esperado: 0 a 2 chamadas novas por ano** (a página inteira tem 3 chamadas desde 2018). Retorno vazio é resultado válido.

Critérios de aceite:
1. coleta as subpáginas de chamada da pasta, ignorando links de compartilhamento social (`facebook.com/sharer`, `api.whatsapp.com`, `twitter.com/share`, `linkedin.com/shareArticle`) e a autorreferência da própria pasta;
2. coleta PDFs dos dois hosts;
3. dedup por URL da subpágina;
4. **lista vazia não é falha** — o flow encerra com sucesso e o alerta de "0 itens" fica desabilitado para esta fonte.

---

### [ ] DOC-ANP · Registrar decisão sobre a ANP · 2h

**Depende de**: nada. Sem código.
**Criar**: `docs/anp_decision.md`

Conteúdo: a ANP **regula** a cláusula de PD&I mas não publica editais — quem publica é a operadora (Petrobras, Equinor, Shell). Evidência: a página `gov.br/anp/pt-br/assuntos/tecnologia-meio-ambiente/pesquisa-desenvolvimento-inovacao` tem 5 links e nenhuma listagem de chamadas. Registrar as 3 alternativas do §3/D1 da spec e a recomendação (página informativa no portal).

---

## 3. Onda 2 — 20h

### [ ] INF-02 · Campos de fomento empresarial no domínio · 12h

**Depende de**: nada (mas só rende valor com ≥1 source empresarial pronto).
**Alterar**: [src/domain/models.py](../src/domain/models.py), [src/components/transforms/edital_normalizer.py](../src/components/transforms/edital_normalizer.py), features e testes de transform

Novos campos em `EditalDomain`:

| Campo | Tipo | Valores | Obrigatório |
| :-- | :-- | :-- | :--: |
| `publico_alvo` | `List[str]` | `pesquisador` \| `estudante` \| `empresa` \| `ict-empresa` \| `internacional` | sim |
| `modalidade` | `str` | `subvenção` \| `bolsa` \| `crédito` \| `prêmio` \| `infraestrutura` \| `fluxo-contínuo` | sim |
| `ambito_geografico` | `str` | `nacional` \| `estadual-<UF>` \| `internacional` \| `regional` | sim |
| `valor_estimado` | `Optional[float]` | R$ | não |
| `trl_exigido` | `Optional[str]` | ex. `"6-9"` | não |
| `fonte_key` | `str` | chave do source | sim |

Critérios de aceite:
1. campos com default — JSONs já em `data/output/` continuam carregáveis;
2. os três obrigatórios são populáveis **estaticamente pelo source**, sem chamada a LLM;
3. `fonte_key` gravado em todo edital, inclusive nos 7 flows existentes;
4. sources antigos não quebram (valores default coerentes).

🔒 **Decisão pendente nº 5**: `valor_estimado` e `trl_exigido` inferidos via Mistral, ou só quando explícitos no texto? Implementar a via estática primeiro — ela não depende da resposta.

---

### [ ] US-SENAI · Source e flow SENAI/Plataforma Inovação · 8h

**Depende de**: INF-02 (para `publico_alvo`).
**Criar**: `src/components/sources/senai_source.py`, `src/flows/ingest_senai_flow.py`, `docs/features/ingest_senai.feature`, `tests/step_defs/test_senai_source.py`

| Item | Valor |
| :-- | :-- |
| Hub | `https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/` |
| Redirect | `plataformainovacao.com.br` → 301 para a URL acima |
| Engine | `requests` — HTML estático confirmado (88KB, não é SPA) |
| Estrutura | hub → `/categoria/<slug>/` → chamadas |
| Slugs vistos | `chamada-regional-senai`, `chamada-tecnica-sesi-senai-evolucao-da-e`, `empreendedorismo-industrial-*`, `ecossistemas-de-inovacao-em-saude-*` |
| `registry` key | `senai` |

Critérios de aceite:
1. descobre as categorias a partir do hub;
2. **distingue chamada aberta de resultado divulgado** (categorias têm âncora `#resultados`) — resultado não é oportunidade;
3. **nunca acessa `/busca/*` nem `*/rss/*`** (proibidos no `robots.txt` do host);
4. dedup por URL;
5. `publico_alvo = [empresa, ict-empresa]`, `orgão_fomento` = `SENAI` ou `SESI-SENAI` conforme o slug.

---

## 4. Onda 3 — 24h

### [ ] INF-03 · Runner resiliente e rate limit por host · 8h

**Depende de**: nada.
**Alterar**: [scripts/run_all_flows.py](../scripts/run_all_flows.py), `.github/workflows/run_scraper.yml`, `tests/step_defs/test_run_all_flows.py`

Hoje [run_all_flows.py:124](../scripts/run_all_flows.py#L124) faz `raise SystemExit` na primeira falha: com o BNDES instável na fila, a indisponibilidade dele zera a coleta diária de todas as outras fontes.

Critérios de aceite:
1. falha de uma fonte não interrompe as demais;
2. exit code ≠ 0 se qualquer fonte falhar (a informação de erro não se perde);
3. timeout por fonte configurável (default 10min);
4. `Crawl-delay` respeitado por host — **BNDES = 2s**, exigido pelo `robots.txt`;
5. uma linha por fonte por execução em `docs/flow_processing_log.md`;
6. flag `--only <fonte,fonte>` para execução seletiva.

---

### [ ] US-BNDES 🔒 · Source e flow BNDES · 16h

**Depende de**: INF-03. **Bloqueado pela decisão pendente nº 2.**
**Criar**: `src/components/sources/bndes_source.py`, `src/flows/ingest_bndes_flow.py`, `docs/features/ingest_bndes.feature`, `tests/step_defs/test_bndes_source.py`

| Item | Valor |
| :-- | :-- |
| Listagem | `.../site/home/transparencia/chamadas-publicas-selecao-projetos` e `/financiamento/produto/bndes-funtec` |
| Engine | **Playwright** — obrigatório |
| Dedup key | **hash(título normalizado + órgão)** |
| `registry` key | `bndes` |

Achados do recon que definem o desenho:
- rotas retornam shell de 8KB (Dojo + `pelev2` web components);
- a rota de 79KB traz **stack trace Java no HTML** (`at com.ibm.wor…ServletContext.java:147`) e headings `Aviso` — portlet em erro;
- `sitemap.xml` → 404, descoberta só por navegação renderizada;
- permalinks `!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zifSy9XT1M_A18DIwD3AwcPXw…` **codificam estado de navegação e não são estáveis** → dedup por URL geraria duplicata a cada execução.

Critérios de aceite:
1. renderiza a listagem e extrai chamadas;
2. dedup por hash de título+órgão, **não** por URL `!ut/p/`;
3. detecta página com portlet em erro (heurística: `com.ibm.` no corpo ou heading `Aviso`) e **aborta a fonte sem persistir dado parcial**;
4. respeita crawl-delay de 2s;
5. distingue Funtec (subvenção não-reembolsável) de crédito.

⏱ **Timebox rígido de 16h.** Se o portlet estiver quebrado de forma persistente, a fonte pode ser inviável sem contato institucional com o BNDES — parar e reportar, não insistir.

---

## 5. Decisões pendentes 🔒

| # | Questão | Bloqueia | Recomendação |
| :--: | :-- | :-- | :-- |
| 1 | ANP: página informativa, trocar alvo para operadoras (+12h) ou fora do escopo? | DOC-ANP (parcial) | Página informativa |
| 2 | BNDES: autorizar 16h com risco de inviabilidade, ou adiar? | US-BNDES | Adiar até haver demanda |
| 3 | ANEEL: aceitar fonte de volume quase nulo? | US-ANEEL | Sim — 3h é barato |
| 4 | Cadência: EMBRAPII/SENAI/ANEEL diários e BNDES semanal? | INF-03 | Sim |
| 5 | `valor_estimado`/`trl_exigido` via Mistral ou só quando explícito? | INF-02 (parcial) | Só quando explícito (custo zero) |

Nenhuma decisão bloqueia a **Onda 1**.

---

## 6. Verificação final

```bash
pytest                                                  # suíte completa verde
python scripts/run_all_flows.py --only embrapii,aneel   # fontes novas isoladas
python -c "
import json; r=json.load(open('registry/processed_editais.json'))
print({k: len(v) for k, v in r.items()})"               # chaves novas populadas
grep -l '\"publico_alvo\"' data/output/*.json | wc -l   # >0 após INF-02
```

Métrica que define sucesso do bloco: **editais com `publico_alvo ∈ {empresa, ict-empresa}` passam de 0 para >0** — é a lacuna nº 1 do PDF de análise.
