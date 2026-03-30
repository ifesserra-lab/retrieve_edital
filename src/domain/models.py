from dataclasses import dataclass
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
