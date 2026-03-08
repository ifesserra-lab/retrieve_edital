from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class RawEdital:
    title: str
    url: str
    raw_agency: Optional[str] = None
    raw_description: Optional[str] = None
    pdf_content: Optional[bytes] = None

@dataclass
class EditalDomain:
    nome_do_edital: str
    orgao_de_fomento: str
    cronograma: List[Dict[str, str]]
    link: str
    descricao: str
    categoria: str
