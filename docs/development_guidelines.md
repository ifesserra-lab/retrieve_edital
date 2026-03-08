# Diretrizes de Desenvolvimento e Arquitetura

Este documento estabelece as **premissas técnicas intransigíveis** que governam toda e qualquer implementação no projeto `retrieve_edital`. O objetivo é garantir um software escalável, sustentável, legível e livre de dívidas técnicas desde o seu início.

Estas diretrizes são suportadas pelas habilidades (`skills`) providas ao agente (`python-design-patterns`, `clean-code`, `solid`).

## 1. Orientação a Objetos (OOP) Estrita
Todo o código central (`core`), componentes e fluxos operacionais (`flows`) devem ser implementados utilizando o **Paradigma Orientado a Objetos**.
- **Encapsulamento**: Oculte a representação interna dos objetos. Atributos da classe devem ser privados ou protegidos quando expostos diretamente causarem quebra de contrato abstrato.
- **Herança vs Composição**: Favoreça a Composição sobre a Herança para garantir o baixo acoplamento, mas utilize herança de Interfaces (Classes Abstratas no Python) para estruturar os contratos arquiteturais (`ISource`, `ITransform`, `ISink`).

## 2. Padrões de Projeto (Design Patterns - GoF)
Problemas recorrentes devem ser resolvidos com abordagens testadas e consagradas:
- **Strategy**: Para mapeamentos e lógicas de normalização itercambiáveis na camada `Transform`.
- **Factory**: Para a criação isolada de instâncias dinâmicas e gerenciamento de injeção de dependência.
- **Repository / Sink**: Abstração clara do destino final da informação (no nosso caso, adaptadores de JSON).
- É terminantemente **proibido** reinventar a roda quando um padrão de projeto conhecido (GoF) resolve o problema de forma mais limpa.

## 3. Princípios S.O.L.I.D.
O design das classes deve passar obrigatoriamente pelo escrutínio dos princípios SOLID:
- **Single Responsibility (SRP)**: Uma classe deve ter um, e apenas um, motivo para mudar. (Ex: O scrapper do site não pode ser o mesmo que formata o json final).
- **Open/Closed (OCP)**: Entidades devem estar abertas para extensão, mas fechadas para modificação.
- **Liskov Substitution (LSP)**: Classes derivadas devem ser substituíveis por suas classes base sem quebrar a execução.
- **Interface Segregation (ISP)**: Interfaces finas e coesas, com funções estritas.
- **Dependency Inversion (DIP)**: Módulos de alto nível não devem depender de módulos de baixo nível. Ambos devem depender de abstrações.

## 4. Práticas de "Clean Code"
As regras do *Uncle Bob* (Robert C. Martin) aplicam-se a todos os Pull Requests e conversas geradoras de código:
- **Nomenclaturas Explicativas**: Variáveis e métodos devem indicar **o quê** fazem. Sem rodeios ou abreviações obscuras (Evitar `x`, `df2`, `val`).
- **Funções Pequenas**: Funções devem fazer uma coisa. Devem fazê-la bem. Devem fazer apenas ela.
- **Aversão a Anti-padrões**: Fica terminantemente vetada a criação de "God Classes" (Classes que fazem tudo), código duplicado, "Magic Numbers/Strings" sem constantes bem definidas e tratamentos de erro genéricos (`except Exception: pass`).
- **Tratamento Elegante de Exceções**: O código não deve falhar silenciosamente ou mascarar a raiz dos problemas na rede (`ConnectionError` real time) e parseamento (`ValidationError`).
