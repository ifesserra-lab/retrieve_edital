# Product Backlog: Retrieve Edital ETL

Este documento rastreia todas as funcionalidades a serem desenvolvidas para o agente de extração de editais. Conforme a metodologia ágil adotada, toda implementação terá sua referência formal via GitHub Issue.

## Sprint Atual (MVP)

| Status | Issue | Título / História de Usuário (User Story) | Esforço (Pts) | Componente |
| :----: | :---: | :---------------------------------------- | :-----------: | :--------- |
| 📝 Todo | #1 | **Configuração da Estrutura Base MVC/ETL**<br>Como desenvolvedor, eu quero estruturar as pastas e definir as interfaces base (`ISource`, `ITransform`, `ISink`), para organizar o fluxo sólido do projeto. | 3 | Core |
| 📝 Todo | #2 | **Gherkin & BDD Specs Boilerplate (pytest-bdd)**<br>Como engenharia de dados, preciso da configuração inicial de testes rodando o Gherkin para que as requisições mandatórias passem a funcionar. | 3 | Testes |
| 📝 Todo | #3 | **Implementação do Source (Playwright Extractor)**<br>Como sistema, eu quero iniciar um navegador e varrer o site da FAPES iterando paginas, para ter a massa de editais. | 5 | Source |
| 📝 Todo | #4 | **Implementação do Transform (Edital Normalizer)**<br>Como fluxo normalizador, quero limpar títulos e formatar nomes de órgãos a partir dos dados extraídos do Source. | 3 | Transform |
| 📝 Todo | #5 | **Implementação do Sink (JSON Writer)**<br>Como armazenador, preciso pegar a lista iterada de editais e escrever para o disco num Payload JSON rigoroso obrigatoriamente formatado. | 2 | Sink |

---
*Este backlog reflete nosso planejamento e serve de ponto de partida principal antes de puxar o código (Code).*
