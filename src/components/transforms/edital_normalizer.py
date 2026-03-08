import os
import re
import io
import json
import logging
from typing import List, Dict
import pdfplumber
from pydantic import BaseModel, Field
from google import genai

from src.core.interfaces import ITransform
from src.domain.models import RawEdital, EditalDomain

logger = logging.getLogger(__name__)

class CronogramaItem(BaseModel):
    Etapa: str = Field(description="O nome da etapa ou evento no cronograma.")
    Previsao: str = Field(description="A data ou string apontando o período previsto para referida etapa.")

class EditalExtraction(BaseModel):
    descricao: str = Field(description="O objetivo principal e a descrição semântica profunda do edital.")
    cronograma: List[CronogramaItem] = Field(description="A lista em ordem cronológica das etapas e datas do fluxo.")

class EditalNormalizer(ITransform[RawEdital, EditalDomain]):
    """
    Normalizes the RawEdital data into a validated EditalDomain object.
    Applies regex cleaning on metadata and parses PDF bytes using Gemini LLM for deep Semantic Extraction.
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
                    # Keep memory usage somewhat low but capture enough pages
                    for page in pdf.pages[:15]:
                        extracted = page.extract_text()
                        if extracted:
                            full_text += f"\n{extracted}"
                            
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key and full_text.strip():
                    client = genai.Client(api_key=api_key)
                    prompt = f"Você é uma IA de extração de dados públicos. Analise o seguinte extrato bruto do PDF de um edital de pesquisa. Extraia de forma acurada o Objetivo (descricao) e mapeie todas as etapas e previsões para compor a tabela de Cronograma:\n\n{full_text}"
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config={
                            'response_mime_type': 'application/json',
                            'response_schema': EditalExtraction
                        }
                    )
                    
                    extracted_data = json.loads(response.text)
                    description = extracted_data.get("descricao", "")
                    
                    for item in extracted_data.get("cronograma", []):
                        cronograma.append({
                            "Etapa": item.get("Etapa", ""),
                            "Previsão": item.get("Previsao", "")
                        })
                else:
                    logger.warning("GEMINI_API_KEY missing or PDF empty. Applying fallback to empty structured data.")
                    
            except Exception as e:
                logger.warning(f"Failed to parse PDF and query LLM for Edital {clean_title}: {e}")

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
