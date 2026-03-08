import re
from typing import List
from src.core.interfaces import ITransform
from src.domain.models import RawEdital, EditalDomain

class EditalNormalizer(ITransform[RawEdital, EditalDomain]):
    """
    Normalizes the RawEdital data into a validated EditalDomain object.
    Applies regex cleaning and basic business rules for categorization.
    """
    
    def process(self, raw_data: RawEdital) -> EditalDomain:
        # Mandatory validation
        if not raw_data.title or raw_data.title.strip() == "":
            raise ValueError("O título do edital não pode ser nulo ou vazio.")

        # Title normalization: remove extra spaces and newlines
        clean_title = re.sub(r'\s+', ' ', raw_data.title).strip().upper()

        # Agency standardization
        raw_orgao = (raw_data.raw_agency or "FAPES").upper()
        if "FAPES" in raw_orgao:
            clean_agency = "FAPES"
        elif "CNPQ" in raw_orgao:
            clean_agency = "CNPQ"
        else:
            clean_agency = raw_orgao

        # Category extraction by empirical rule on the description
        description = raw_data.raw_description or ""
        category = "Outros"
        if "extensão" in description.lower():
            category = "Extensão"
        elif "pesquisa" in description.lower():
            category = "Pesquisa"
        elif "inovação" in description.lower():
            category = "Inovação"

        # Cronograma defaults to empty list of dictionaries if not available from raw
        # (This avoids the type error and matches the `List[Dict[str, str]]` requirement)
        cronograma: List[dict] = []

        return EditalDomain(
            nome_do_edital=clean_title,
            orgao_de_fomento=clean_agency,
            cronograma=cronograma,
            descricao=description,
            categoria=category
        )
