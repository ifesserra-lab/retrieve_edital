import re
import io
import logging
from typing import List, Dict
import pdfplumber
from src.core.interfaces import ITransform
from src.domain.models import RawEdital, EditalDomain

logger = logging.getLogger(__name__)

class EditalNormalizer(ITransform[RawEdital, EditalDomain]):
    """
    Normalizes the RawEdital data into a validated EditalDomain object.
    Applies regex cleaning and parses PDF bytes using pdfplumber to extract Object and Schedule.
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

        # Base properties
        description = raw_data.raw_description or ""
        cronograma: List[Dict[str, str]] = []
        
        # Enrichment parsing from PDF if available
        if raw_data.pdf_content:
            try:
                with pdfplumber.open(io.BytesIO(raw_data.pdf_content)) as pdf:
                    full_text = ""
                    # Keep memory usage somewhat low but capture headers
                    for page in pdf.pages[:15]:
                        extracted = page.extract_text()
                        if extracted:
                            full_text += f"\n{extracted}"
                            
                        # Try extracting tables for cronograma
                        tables = page.extract_tables()
                        for table in tables:
                            # Heuristic: the first row represents headers
                            # often 'Etapa' or 'Eventos' and 'Datas' or 'Previsão'
                            if len(table) > 1 and table[0]:
                                flat_header = " ".join([str(c) for c in table[0] if c]).lower()
                                if "etapa" in flat_header or "previsão" in flat_header or "data" in flat_header:
                                    # It's highly likely to be the chronogram table
                                    # Loop over rows avoiding header
                                    for row in table[1:]:
                                        # Clean None types and strings
                                        cleaned_row = [str(r).replace('\n', ' ').strip() if r else "" for r in row]
                                        
                                        # We only map the first two valid columns assuming Phase and Date
                                        valid_cols = [c for c in cleaned_row if c]
                                        if len(valid_cols) >= 2:
                                            cronograma.append({
                                                "Etapa": valid_cols[0],
                                                "Previsão": valid_cols[1]
                                            })
                                    # If found, avoid keeping extracting other tables
                                    if len(cronograma) > 0:
                                        break
                                        
                    # Extract "1. OBJETO" text using Regex over the joined pages text
                    # Match "1. OBJETO" up to the next "2. " or "CRONOGRAMA" or End of String
                    objetivo_pattern = r'(?:\d+\.\s*)?OBJETO\s*\n(.*?)(?=\n\s*\d+\.\s*[A-Z]|\n\s*CRONOGRAMA|\Z)'
                    match = re.search(objetivo_pattern, full_text, re.IGNORECASE | re.DOTALL)
                    if match:
                        extracted_desc = match.group(1).strip()
                        # Clean newlines from pdf extraction
                        description = re.sub(r'\s+', ' ', extracted_desc)
                        
            except Exception as e:
                logger.warning(f"Failed to parse PDF for Edital {clean_title}: {e}")

        # Category extraction by empirical rule on the description/title
        combined_text = (description + " " + clean_title).lower()
        category = "Outros"
        if "extensão" in combined_text:
            category = "Extensão"
        elif "pesquisa" in combined_text:
            category = "Pesquisa"
        elif "inovação" in combined_text:
            category = "Inovação"

        return EditalDomain(
            nome_do_edital=clean_title,
            orgao_de_fomento=clean_agency,
            cronograma=cronograma,
            link=raw_data.url,
            descricao=description,
            categoria=category
        )
