# Rodar os GitHub Actions localmente

Os workflows deste repositório podem ser executados na máquina com
[`act`](https://github.com/nektos/act), sem consumir minutos do GitHub nem
esperar o agendamento das 03:00 UTC.

## Pré-requisitos

| Item | Verificar com |
|------|---------------|
| `act` | `act --version` (instalar: `brew install act`) |
| Docker rodando | `docker info` |
| Imagem do runner | `docker images \| grep catthehacker` |

A imagem `catthehacker/ubuntu:act-latest` tem ~2.3 GB e é baixada na primeira
execução.

## Configuração

Já versionada em [`.actrc`](../.actrc): imagem do runner, arquitetura do
container e o arquivo de segredos. Falta apenas criar os segredos locais:

```bash
cp .secrets.example .secrets
# preencha MISTRAL_API_KEY
```

`.secrets` está no `.gitignore`. Nunca versione esse arquivo — ele contém a
chave real da API.

> **Sobre `--container-architecture linux/amd64`:** os runners do GitHub são
> x86_64. Em Mac Apple Silicon, sem essa flag o container sobe em arm64 e o
> passo `playwright install chromium` falha, porque a Microsoft só publica o
> Chromium do Playwright para `linux/amd64`.

## Comandos

```bash
# Listar os jobs de todos os workflows
act --list

# Suíte BDD (tests.yml) — o mais rápido, e o que roda em todo PR
act push -j test

# Scraper diário completo (run_scraper.yml)
act workflow_dispatch -j scrape-editais

# Horizon Europe semanal (run_horizon_weekly.yml)
act workflow_dispatch -j scrape-horizon

# Simular o disparo agendado, em vez do manual
act schedule -j scrape-editais

# Ver o que rodaria, sem executar
act workflow_dispatch -j scrape-editais --dryrun
```

## Cuidados

- **O scraper acessa os portais reais.** Não há modo de simulação: rodar
  `scrape-editais` faz requisições de verdade a FAPES, FINEP, CONIF, IFES,
  CAPES e CNPq. Use com parcimônia.
- **O scraper consome cota da Mistral.** Cada PDF novo gasta uma chamada de OCR
  mais uma de LLM. Para rodar sem gastar cota, exercite um fluxo isolado com
  `python scripts/run_all_flows.py --only CNPQ` (o CNPq não usa OCR na
  listagem) em vez do workflow inteiro.
- **O passo de commit/push.** Deixe `GITHUB_TOKEN` vazio no `.secrets`: o push
  falha de forma visível em vez de publicar dados de teste no repositório. O
  passo roda com `if: always()`, então ele será alcançado mesmo quando a
  extração falhar.
- **`--reuse`** está ligado no `.actrc`. O container sobrevive entre execuções,
  o que evita reinstalar dependências e Chromium a cada rodada. Para começar
  limpo: `act push -j test --rm` ou remova o container com
  `docker rm -f $(docker ps -aq --filter name=act-)`.

## Problema conhecido: `Post Set up Python` falha com `node: not found`

Sintoma: todos os passos passam (inclusive `286 passed` do pytest) e mesmo
assim o job termina vermelho, no passo final:

```
❌  Failure - Post Set up Python 3.12
OCI runtime exec failed: exec: "node": executable file not found in $PATH
exitcode '127': command not found
```

É limitação do `act` ([nektos/act#107](https://github.com/nektos/act/issues/107)),
não do repositório: no runner do GitHub isso não acontece. A causa é que
`actions/setup-python` reescreve o `PATH` do job e o post-step perde
`/opt/acttoolcache/node/<versão>/x64/bin`, onde vive o Node da imagem.

Correção — criar o symlink uma vez por container (com `--reuse` ele persiste):

```bash
docker exec "$(docker ps -aq --filter name=act- | head -1)" \
  bash -c 'ln -sf /opt/acttoolcache/node/*/x64/bin/node /usr/local/bin/node'
```

Depois disso `act push -j test` termina com exit code 0. Se você rodar sem
`--reuse`, o container é descartado a cada execução e o symlink precisa ser
refeito — nesse caso é mais simples ignorar o post-step e olhar o resultado do
pytest, que é o que de fato importa.

## Diferenças conhecidas em relação ao runner do GitHub

- `actions/setup-python` usa o Python já presente na imagem quando a versão
  bate; no GitHub ele baixa uma build própria.
- Segredos vêm de `.secrets`, não de `secrets.*` do repositório.
- `github.event` é sintético. Workflows que dependem do payload real de um push
  ou PR precisam de `--eventpath` com um JSON de evento.
