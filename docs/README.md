# Documentação do Projeto

Este diretório contém toda a documentação vital do projeto `retrieve_edital`. A manutenção atualizada destes arquivos garante a sustentabilidade arquitetural do robô de Extração da FAPES.

## Índice de Documentos

### Arquitetura e Regras
- [Diretrizes de Desenvolvimento S.O.L.I.D](development_guidelines.md)
  - Descreve as premissas inegociáveis do repositório (OOP Estrito, Clean Code, Anti-padrões mapeados).
- [Arquitetura ETL (System Design Document)](etl_architecture.md)
  - Descreve o padrão T-Shape (`Source` -> `Transform` -> `Sink`) e como os dados fluem desde a coleta até o arquivo JSON final.

### Ágil e Produto
- [Product Backlog](backlog.md)
  - Visão detalhada de Epics, User Stories e Tasks. Linkado ativamente com a central de Issues do GitHub no formato sprint.

### Testes Baseados em Comportamento (BDD)
Os arquivos a seguir (`.feature` em Gherkin) são a principal fonte de verdade sobre o comportamento esperado da nossa pipeline técnica e atuam como contrato obrigatório *(Definition of Done)* para aceitação de pull requests:
- [Extração (Extract)](features/extract_editais.feature)
- [Transformação (Transform)](features/transform_editais.feature)
- [Persistência (Load/Sink)](features/load_editais.feature)
