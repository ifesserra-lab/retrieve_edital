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
