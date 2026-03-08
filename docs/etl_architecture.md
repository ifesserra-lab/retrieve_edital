# Padrão de Arquitetura ETL: Source, Transform e Sink

Este documento descreve o padrão arquitetural utilizado no projeto para os pipelines de ETL (Extract, Transform, Load), baseado em componentes fracamente acoplados.

A arquitetura é dividida em três componentes principais: **Source** (Origem), **Transform** (Transformação) e **Sink** (Destino).

## Terminologia

- **Source (Origem)**: De onde os dados provêm. Pode ser uma API, um site via web scraping (ex: site da FAPES), arquivos locais ou um banco de dados legado. A responsabilidade do Source é apenas *extrair* os dados brutos.
- **Transform (Transformação)**: Aplica regras de negócio, limpeza e validação aos dados brutos. Transforma os dados de um formato cru para um formato de domínio padronizado.
- **Sink (Destino)**: Para onde os dados são enviados e armazenados. Neste projeto, o Sink **sempre irá gerar um arquivo JSON** contendo os campos obrigatórios: `nome do edital`, `órgão de fomento`, `cronograma`, `descrição` e `categoria`. A responsabilidade do Sink é apenas *carregar*/salvar os dados transformados.

## 1. Estrutura de Diretórios Recomendada

A aplicação deve ser estruturada da seguinte forma:

```text
src/
├── core/              # Utilitários e interfaces comuns
│   ├── interfaces.py  # Classes abstratas (ISource, ITransform, ISink)
│
├── components/        # Blocos de construção reutilizáveis
│   ├── sources/       # Implementações de origens de dados
│   │   └── fapes_source.py
│   │
│   ├── transforms/    # Implementações de normalização e regras de negócio
│   │   └── edital_normalizer.py
│   │
│   └── sinks/         # Implementações de destino de dados
│       └── supabase_sink.py
│
└── flows/             # Orquestração (onde os componentes são montados)
    └── ingest_fapes_flow.py
```

## 2. Interfaces Centrais

Estas interfaces em Python garantem que todos os componentes "falem a mesma língua", permitindo o uso de Generics para tipagem.

```python
# src/core/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, List, Generic, TypeVar

T = TypeVar("T")  # Tipo genérico (pode ser Edital, Usuario, etc)

class ISource(ABC, Generic[T]):
    """Interface para origens de dados (Extract)."""
    @abstractmethod
    def read(self) -> List[T]:
        """Lê os dados da origem e retorna uma lista de itens."""
        pass

class ITransform(ABC, Generic[T]):
    """Interface para transformação de dados (Transform)."""
    @abstractmethod
    def process(self, raw_data: Any) -> T:
        """Processa os dados brutos e retorna um objeto de domínio validado."""
        pass

class ISink(ABC, Generic[T]):
    """Interface para destinos de dados (Load)."""
    @abstractmethod
    def write(self, items: List[T]) -> None:
        """Escreve/salva os itens no destino."""
        pass
```

## 3. Benefícios desta Arquitetura

1. **Reutilização**: Um mesmo `Sink` (ex: `SupabaseSink`) pode ser reaproveitado por diferentes pipelines.
2. **Testabilidade**: Cada porção pode ser testada isoladamente. É possível testar o `Transform` injetando dados falsos (mock) sem precisar acessar a rede (sem rodar o `Source`).
3. **Escalabilidade**: Adicionar uma nova origem de dados não exige alterar como os dados são transformados ou salvos, basta criar uma nova implementação de `ISource`.
4. **Padronização**: Define um limite claro de responsabilidade, facilitando o entendimento de onde o código deve estar. Todo código de *scrape* fica isolado do código de *regras de negócio*.

## 4. Orquestração (O Flow)

Ao montar tudo em um *Flow* (podendo usar bibliotecas como Prefect, Dagster, ou chamadas puras), fazemos injeção de dependência dos componentes, o que permite criar pipelines variados como blocos de montar (LEGO).

```python
# flows/ingest_fapes_flow.py

def run_pipeline(source: ISource, transform: ITransform, sink: ISink):
    # 1. EXTRACT (read)
    raw_data = source.read()
    
    # 2. TRANSFORM (process)
    clean_data = [transform.process(item) for item in raw_data]
    
    # 3. LOAD (write)
    sink.write(clean_data)

def fapes_flow():
    # Injeção de dependências
    source = FapesSource()
    transform = EditalNormalizer()
    sink = SupabaseSink()
    
    run_pipeline(source, transform, sink)
```
