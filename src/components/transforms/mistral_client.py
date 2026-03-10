import os
import logging
import base64
import json
import time
from typing import Optional, Dict, Any, List
from mistralai import Mistral
from src.domain.models import EditalDomain

logger = logging.getLogger(__name__)

class MistralExtractionService:
    """
    Service to extract structured data from PDF editais using Mistral OCR and LLM.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY is not set.")
        self.client = Mistral(api_key=self.api_key)
        self.ocr_model = "mistral-ocr-latest"
        self.llm_model = "mistral-large-latest"

    def extract_from_pdf(self, pdf_bytes: bytes, filename: str) -> Optional[EditalDomain]:
        """
        Processes PDF bytes through Mistral OCR and extracts structured data using LLM.
        """
        try:
            logger.info(f"Uploading PDF {filename} to Mistral for OCR...")
            
            # 1. Upload file for OCR
            # Mistral client.files.upload takes a file object or a dictionary with content
            uploaded_file = self.client.files.upload(
                file={
                    "file_name": filename,
                    "content": pdf_bytes,
                },
                purpose="ocr"
            )
            
            logger.info(f"File uploaded with ID: {uploaded_file.id}. Processing OCR...")
            
            # 2. Process OCR
            ocr_response = self.client.ocr.process(
                model=self.ocr_model,
                document={
                    "type": "file",
                    "file_id": uploaded_file.id
                }
            )
            
            # Concatenate all pages text
            # The structure of ocr_response might vary, but usually it has a 'pages' list
            full_ocr_text = ""
            for page in ocr_response.pages:
                full_ocr_text += f"\n{page.markdown}" # markdown is common for mistral ocr
            
            logger.info("OCR completed. Extracting structured data...")
            
            # 3. Extract structured data via LLM
            # Small delay to respect rate limits if processing many items
            time.sleep(2)
            prompt = self._get_extraction_prompt(full_ocr_text)
            
            response = self.client.chat.complete(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de editais públicos de fomento (FAPES, CNPq, etc)."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            raw_json = response.choices[0].message.content
            extracted_data = json.loads(raw_json)
            
            # Cleanup: Delete the uploaded file to save space/cost
            try:
                self.client.files.delete(file_id=uploaded_file.id)
            except Exception as cleanup_err:
                logger.warning(f"Failed to delete uploaded file {uploaded_file.id}: {cleanup_err}")

            return self._map_to_domain(extracted_data)

        except Exception as e:
            logger.error(f"Mistral extraction failed for {filename}: {e}", exc_info=True)
            return None

    def _get_extraction_prompt(self, ocr_text: str) -> str:
        return f"""
Analise o seguinte texto OCR de um edital de fomento e extraia as informações estruturadas em formato JSON.

O JSON deve seguir exatamente esta estrutura:
{{
    "nome": "Título oficial do edital",
    "descrição": "Resumo objetivo do edital (objeto)",
    "orgão_fomento": "Nome da instituição (Ex: FAPES)",
    "categoria": "extensão, pesquisa, inovação ou outros",
    "status": "aberto",
    "data_abertura": "YYYY-MM-DD (OBRIGATÓRIO, use data aproximada se necessário)",
    "data_encerramento": "YYYY-MM-DD ou \"\"",
    "cronograma": [
        {{"evento": "Descrição da etapa", "data": "Data ou período"}}
    ],
    "tags": ["lista", "de", "palavras-chave", "(MÍNIMO 3 TAGS)"]
}}

Texto do Edital:
{ocr_text}
"""

    def _map_to_domain(self, data: Dict[str, Any]) -> EditalDomain:
        # Basic mapping and defaults
        return EditalDomain(
            nome=data.get("nome", "").upper(),
            descrição=data.get("descrição", ""),
            orgão_fomento=data.get("orgão_fomento", "FAPES").upper(),
            categoria=data.get("categoria", "outros").lower(),
            status=data.get("status", "aberto"),
            data_abertura=data.get("data_abertura") or "2026-01-01", # Default if missing
            data_encerramento=data.get("data_encerramento") or "",
            link="", # This will be set by the normalizer who has the URL
            cronograma=[{"evento": item.get("evento") or item.get("etapa", ""), "data": item.get("data") or ""} for item in data.get("cronograma", [])],
            tags=data.get("tags") if data.get("tags") and len(data.get("tags")) > 0 else ["fapes", "edital", "inovação"]
        )
