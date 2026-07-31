from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class RawEdital:
    title: str
    url: str
    source_category: Optional[str] = None
    raw_agency: Optional[str] = None
    raw_description: Optional[str] = None
    pdf_content: Optional[bytes] = None
    document_type: str = "edital"  # edital, anexo, alteração, desconhecido
    group_id: Optional[str] = None
    is_main: bool = True
    attachments: Optional[List['RawEdital']] = None  # Nested attachments
    raw_status: Optional[str] = None
    # Optional structured data from detail pages (e.g. FINEP chamadapublica)
    raw_cronograma: Optional[List[Dict[str, str]]] = None  # [{"evento": "...", "data": "YYYY-MM-DD"}]
    raw_tags: Optional[List[str]] = None
    raw_anexos: Optional[List[Dict[str, str]]] = None  # [{"titulo": "...", "link": "...", "tipo": "pdf"}]
    # Modalidade declarada pela origem. Hoje só `fluxo-contínuo`, quando a
    # fonte indica explicitamente que a chamada não tem prazo de encerramento.
    raw_modalidade: Optional[str] = None
    # Público-alvo e âmbito declarados pela origem, quando ela os informa. A FINEP
    # traz o público na taxonomia `publicoAlvo` e a região em `regiao`; o Horizon,
    # pelas divisões do programa. Fontes sem essa informação deixam vazio, em vez
    # de receber palpite.
    raw_publico_alvo: Optional[List[str]] = None
    raw_ambito_geografico: Optional[str] = None

@dataclass
class EditalDomain:
    nome: str
    descrição: str
    orgão_fomento: str
    categoria: str
    status: str
    data_abertura: str
    data_encerramento: str
    link: str
    cronograma: List[Dict[str, str]]
    tags: List[str]
    anexos: List[Dict[str, str]] = None # List of {title, url, type}
    # Distingue "aberto permanentemente" de "prazo desconhecido": sem este
    # campo, `data_encerramento` vazio significava as duas coisas ao mesmo
    # tempo e o portal não tinha como diferenciá-las.
    modalidade: str = ""
    # Campos da prioridade 6 do PDF de análise. `publico_alvo` e
    # `ambito_geografico` são preenchidos quando há evidência da origem;
    # `valor_estimado` e `trl_exigido` existem no schema mas só podem vir do texto
    # do PDF, e ficam vazios até que a extração seja avaliada contra os documentos
    # que hoje falham — preencher por palpite seria pior que deixar vazio.
    publico_alvo: List[str] = field(default_factory=list)
    ambito_geografico: str = ""
    valor_estimado: Optional[float] = None
    trl_exigido: str = ""
    # Qual fonte monitorada produziu este edital. `orgão_fomento` é rótulo de
    # exibição; esta é a chave técnica, estável, usada para rastrear origem.
    fonte_key: str = ""
