# Product Backlog: Retrieve Edital ETL

Este documento rastreia todas as funcionalidades a serem desenvolvidas para o agente de extração de editais. Conforme a metodologia ágil adotada, toda implementação terá sua referência formal via GitHub Issue.

## Sprint Atual (MVP)

## Epic 1: Pipeline ETL de Editais FAPES
**Objetivo**: Construir a infraestrutura base e o fluxo completo de extração, transformação e carga dos editais de "Difusão do Conhecimento" do site da FAPES.

### Lista de Backlog (Itens de Trabalho)

| Tipo | Status | Issue | Título / Descrição | Esforço (Pts) |
| :--: | :----: | :---: | :----------------- | :-----------: |
| 📚 | ✅ Done | [#1](https://github.com/ifesserra-lab/retrieve_edital/issues/1) | **US 01: Configuração da Estrutura Base MVC/ETL**<br>Como desenvolvedor, eu quero estruturar as interfaces base (`ISource`, `ITransform`, `ISink`), para garantir os princípios SOLID. | 3 |
| 🛠️ | ✅ Done | [#2](https://github.com/ifesserra-lab/retrieve_edital/issues/2) | **Task 01.1: Gherkin & BDD Specs Boilerplate**<br>Configurar a suite de testes rodando o Gherkin (pytest-bdd) para as requisições mandatórias do repositório. | 3 |
| 📚 | ✅ Done | [#3](https://github.com/ifesserra-lab/retrieve_edital/issues/3) | **US 02: Implementação do Source (Playwright Extractor)**<br>Como sistema, eu quero iniciar um navegador e varrer o site iterando "https://fapes.es.gov.br/difusao-do-conhecimento", para ter a massa de editais. | 5 |
| 📚 | ✅ Done | [#4](https://github.com/ifesserra-lab/retrieve_edital/issues/4) | **US 03: Implementação do Transform (Edital Normalizer)**<br>Como fluxo normalizador, quero limpar títulos e formatar nomes de órgãos a partir dos dados do Source. | 3 |
| 📚 | ✅ Done | [#5](https://github.com/ifesserra-lab/retrieve_edital/issues/5) | **US 04: Implementação do Sink (JSON Writer)**<br>Como armazenador, preciso pegar a lista iterada de editais e escrever para o disco gerando 1 Payload JSON por Edital. | 2 |
| 📚 | ✅ Done | [#6](https://github.com/ifesserra-lab/retrieve_edital/issues/15) | **Issue #6: PDF Parsing & Data Extraction**<br>Extração de objetivos e cronogramas diretamente dos arquivos PDF. | 5 |
| 📚 | ✅ Done | [#7](https://github.com/ifesserra-lab/retrieve_edital/issues/16) | **Issue #7: Gemini LLM & Incremental Load**<br>Implementação de carga incremental (Sieve) e extração semântica (revertida na Issue #8). | 8 |
| 📚 | ✅ Done | [#8](https://github.com/ifesserra-lab/retrieve_edital/issues/17) | **Issue #8: Revert LLM and New JSON Schema**<br>Remoção da dependência de LLM (custo) e adoção do novo padrão de schema em português. | 3 |
| 📚 | ✅ Done | [#9](https://github.com/ifesserra-lab/retrieve_edital/issues/18) | **Issue #9: Multi-URL Support for FAPES**<br>Adicionar suporte para varredura em múltiplas URLs: Extensão, Pesquisa, Inovação e Chamadas Internacionais. | 5 |
| 📚 | ✅ Done | [#10](https://github.com/ifesserra-lab/retrieve_edital/issues/19) | **Issue #10: Mistral AI Integration (OCR & LLM)**<br>Substituir o Gemini pelo Mistral para processamento de PDFs (Mistral OCR) e extração semântica de dados (LLM) com saída estruturada seguindo o novo padrão JSON. | 8 |
| 🛠️ | ✅ Done | [#11](https://github.com/ifesserra-lab/retrieve_edital/issues/20) | **Estabilização de Dados e Schema (Pós-Mistral)**<br>1. Inconsistência de Nomenclatura no Cronograma: Corrigido de `etapa` para `evento`.<br>2. Valores Nulos: Substituídos por strings vazias para validação.<br>3. Normalização de Categorias: Garantia de valores únicos permitidos pelo Enum do site.<br>4. Correção de Build: Build NPM agora completa sem erros de validação de dados.<br>5. Campos Obrigatórios: Garantir que `descrição`, `data_abertura` e `tags` estejam sempre presentes e populados. | 3 |
| 🛠️ | ✅ Done | [#12](https://github.com/ifesserra-lab/retrieve_edital/issues/21) | **Issue #12: Melhorias de Resiliência e Extração no Mistral**<br>1. Implementação de lógica de controle de concorrência (`max_workers=2`) e estratégia de Backoff/Retries (tentativas) automáticos em caso de erros `429` (Rate limits) ou `500` da API Mistral.<br>2. Atualização de prompt para inferir descrições estruturadas a partir de documentos que usam a seção "FINALIDADE" ao invés de "Objeto". | 3 |

---
*Este backlog reflete nosso planejamento e serve de ponto de partida principal antes de puxar o código (Code).*
