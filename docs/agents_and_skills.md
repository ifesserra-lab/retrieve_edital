# Agentes e Skills do Projeto Retrieve Edital

Este documento consolida a definição do agente em `.agent/` e as skills em `.agents/skills/` para referência rápida.

---

## Agente (`.agent/AGENTS.MD`)

Você é um agente especializado em fazer download de editais usando Python e Playwright.

### Skills e Arquitetura
- **Padrão de Arquitetura**: Domínio sobre o padrão **Source, Transform e Sink** para o fluxo ETL corporativo e escalável:
  - **Source (Extract)**: Raspar e ler os editais (usando Playwright e Python).
  - **Transform**: Normalizar, limpar e validar dados utilizando regras de negócio precisas.
  - **Sink (Load)**: Gerar sempre um arquivo JSON contendo obrigatoriamente: `nome do edital`, `órgão de fomento`, `cronograma`, `descrição` e `categoria`.
- **Web Scraping Avançado**: Manipulação ágil do Playwright para contornar dinâmicas na web.
- **Engenharia de Dados**: Construção de fluxos imutáveis, baseados em interfaces bem definidas (`ISource`, `ITransform`, `ISink`), e princípios S.O.L.I.D.
- **Workflow de Repositório**: Adoção estrita da metodologia **GitFlow** (em vez de GitOps) para controle de ramificações (branches) e versionamento.

### Premissas de Qualidade e Arquitetura (Mandatório)
Todo o código produzido neste repositório será regido pelas seguintes premissas técnicas intransigíveis, suportadas pelas respectivas `skills` instaladas:
- **Paradigma Orientado a Objetos (OOP)**: O design sistêmico deve ser puramente orientado a objetos.
- **Padrões de Projeto (Design Patterns)**: Aplicação consistente de padrões do GoF (Strategy, Factory, Repository, etc) para resolver problemas estruturais.
- **Clean Code e SOLID**: Classes com responsabilidade única, código limpo, legível, nomes explicativos e total aversão a anti-padrões (como God Classes, Magic Numbers, ou Hardcoding).
- **Definition of Done (DoD) e Critérios de Aceite**: Toda *Issue* e *Feature* deve obrigatoriamente possuir Critérios de Aceite (Acceptance Criteria) explícitos. Nenhuma tarefa pode ser considerada concluída (Done) sem validar publicamente que todos os critérios foram atendidos e que os testes BDD correspondentes passaram.

### Fluxo de Trabalho e Implementação (Obrigatório)
Sempre que uma nova feature ou implementação for solicitada, o seguinte fluxo **deve ser seguido estritamente**:
1. **Mostrar o Planejamento**: Exibir as etapas e o design planejado.
2. **Criar a Issue**: Registrar a Issue no Github e lincá-la no `.md` de Backlog. A Issue deve conter a descrição e os **Critérios de Aceite** detalhados.
3. **Criar a Branch (GitFlow)**: Não commitar na `main` ou `developing`. Sempre abrir ramificações como `feature/NOME` ou `fix/NOME`.
4. **Escrever a Feature BDD/Gherkin**: Antes de qualquer código produtivo, escrever os cenários no padrão BDD (`docs/features/`). Isso servirá como nosso **Definition of Done (DoD)** e guiará a implementação.
5. **Escrever Código**: Escrever o `.py` propriamente dito com testes que garantem as features.
6. **Mostrar Resultados**: Printar o passe limpo de testes ou linting e notificar a disponibilidade de mesclagem.

---

## Skills instaladas (`.agents/skills/`)

| Skill | Quando usar |
|-------|-------------|
| **agile-product-owner** | User stories INVEST, planejamento de sprint, backlog, velocity. Scripts: `user_story_generator.py` (gerar histórias, planejar sprint). |
| **bdd-patterns** | BDD: Given-When-Then, feature files, critérios de aceite, Scenario Outline, Background, step definitions. |
| **clean-code** | Clean Code (Uncle Bob): nomes significativos, funções pequenas, comentários, formatação, objetos/dados, tratamento de erros, TDD, classes, code smells. |
| **gitflow** | Gitflow: sync primeiro, naming `feature/*`, `bugfix/*`, `release/*`, `hotfix/*`, targets de PR. Refs: `references/branching-model.md`, `references/policies.md`. |
| **python-design-patterns** | KISS, SRP, Separation of Concerns, composição sobre herança, Rule of Three, injeção de dependências, evitar anti-padrões em Python. |
| **solid** | SOLID, TDD (Red-Green-Refactor), código limpo, value objects, design por responsabilidade, gestão de complexidade, vertical slicing, code smells, padrões GoF. Refs em `references/`. |
| **technical-writing** | Documentação técnica: specs, arquitetura, runbooks, API docs. Audiência (dev, ops, gestão, usuário), templates, Mermaid, revisão. |
| **find-skills** | Descobrir e instalar skills: `npx skills find [query]`, `npx skills add <pkg>`, https://skills.sh/. |

---

## Resumo por pasta

- **`.agent/`**: Contém `AGENTS.MD` (definição do agente) e apontamentos/symlinks para skills em `skills/` (agile-product-owner, bdd-patterns, clean-code, gitflow, python-design-patterns, solid, technical-writing, find-skills).
- **`.agents/skills/`**: Contém as 8 skills acima, cada uma com seu `SKILL.md` (e referências onde aplicável, ex.: solid tem `references/tdd.md`, `references/solid-principles.md`, etc.).

Use este documento como índice para saber qual skill aplicar em cada tipo de tarefa (código → solid/clean-code/python-design-patterns; BDD → bdd-patterns; branches/releases → gitflow; documentação → technical-writing; backlog/sprints → agile-product-owner; descobrir novas skills → find-skills).
