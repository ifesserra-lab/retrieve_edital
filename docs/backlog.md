# Product Backlog: Retrieve Edital ETL

Este documento rastreia todas as funcionalidades a serem desenvolvidas para o agente de extração de editais. Conforme a metodologia ágil adotada, toda implementação terá sua referência formal via GitHub Issue.

## Sprint Atual (MVP)

## Epic 1: Pipeline ETL de Editais FAPES
**Objetivo**: Construir a infraestrutura base e o fluxo completo de extração, transformação e carga dos editais de "Difusão do Conhecimento" do site da FAPES.

### Lista de Backlog (Itens de Trabalho)

| Tipo | Status | Issue | Título / Descrição | Esforço (Pts) |
| :--: | :----: | :---: | :----------------- | :-----------: |
| 📚 | ✅ Done | [#1](https://github.com/ifesserra-lab/retrieve_edital/issues/1) | **US 01: Configuração da Estrutura Base MVC/ETL**<br>Como desenvolvedor, eu quero estruturar as interfaces base (`ISource`, `ITransform`, `ISink`), para garantir os princípios SOLID. | 3 |
| 🛠️ | ⏳ In Progress | [#2](https://github.com/ifesserra-lab/retrieve_edital/issues/2) | **Task 01.1: Gherkin & BDD Specs Boilerplate**<br>Configurar a suite de testes rodando o Gherkin (pytest-bdd) para as requisições mandatórias do repositório. | 3 |
| 📚 | ⏳ In Progress | [#3](https://github.com/ifesserra-lab/retrieve_edital/issues/3) | **US 02: Implementação do Source (Playwright Extractor)**<br>Como sistema, eu quero iniciar um navegador e varrer o site iterando "https://fapes.es.gov.br/difusao-do-conhecimento", para ter a massa de editais. | 5 |
| 📚 | ⏳ In Progress | [#4](https://github.com/ifesserra-lab/retrieve_edital/issues/4) | **US 03: Implementação do Transform (Edital Normalizer)**<br>Como fluxo normalizador, quero limpar títulos e formatar nomes de órgãos a partir dos dados do Source. | 3 |
| 📚 | ⏳ In Progress | [#5](https://github.com/ifesserra-lab/retrieve_edital/issues/5) | **US 04: Implementação do Sink (JSON Writer)**<br>Como armazenador, preciso pegar a lista iterada de editais e escrever para o disco gerando 1 Payload JSON por Edital. | 2 |

---
*Este backlog reflete nosso planejamento e serve de ponto de partida principal antes de puxar o código (Code).*
