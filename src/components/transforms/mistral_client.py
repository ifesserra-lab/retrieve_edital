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
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            uploaded_file_id = None
            try:
                logger.info(f"Uploading PDF {filename} to Mistral for OCR (Attempt {attempt})...")
                
                # 1. Upload file for OCR
                # Mistral client.files.upload takes a file object or a dictionary with content
                uploaded_file = self.client.files.upload(
                    file={
                        "file_name": filename,
                        "content": pdf_bytes,
                    },
                    purpose="ocr"
                )
                uploaded_file_id = uploaded_file.id
                
                logger.info(f"File uploaded with ID: {uploaded_file_id}. Processing OCR...")
                
                # 2. Process OCR
                ocr_response = self.client.ocr.process(
                    model=self.ocr_model,
                    document={
                        "type": "file",
                        "file_id": uploaded_file_id
                    }
                )
                
                # Concatenate all pages text
                # The structure of ocr_response might vary, but usually it has a 'pages' list
                full_ocr_text = ""
                for page in ocr_response.pages:
                    full_ocr_text += f"\n{page.markdown}" # markdown is common for mistral ocr
                
                logger.info("OCR completed. Extracting structured data...")
                
                # 3. Extract structured data via LLM
                # Delay to respect rate limits if processing many items
                time.sleep(5)
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
                    self.client.files.delete(file_id=uploaded_file_id)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to delete uploaded file {uploaded_file_id}: {cleanup_err}")
    
                return self._map_to_domain(extracted_data)
    
            except Exception as e:
                logger.error(f"Mistral extraction failed for {filename} on attempt {attempt}: {e}")
                
                if uploaded_file_id:
                    # Attempt cleanup on failure
                    try:
                        self.client.files.delete(file_id=uploaded_file_id)
                    except Exception:
                        pass

                if attempt < max_retries:
                    wait_time = attempt * 15
                    logger.info(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries reached for {filename}. Returning None.")
                    return None
    
    def classify_document_titles(self, titles: List[str]) -> Dict[str, str]:
        """
        Uses Mistral to classify a list of document titles within a notice group.
        Returns a mapping of title -> document_type (edital, anexo, alteração).
        """
        if not titles:
            return {}

        prompt = f"""
Classifique cada título de documento abaixo em uma das seguintes categorias:
- 'edital': O documento principal da chamada pública ou concurso.
- 'anexo': Documentos técnicos, formulários, declarações ou manuais complementares.
- 'alteração': Aditivos, retificações ou mudanças no edital original.

Retorne APENAS um JSON onde a chave é o título exato e o valor é a categoria.

Títulos:
{json.dumps(titles, indent=2, ensure_ascii=False)}
"""
        try:
            response = self.client.chat.complete(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em organizar documentos de editais de fomento."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            raw_json = response.choices[0].message.content
            classification = json.loads(raw_json)
            logger.info(f"Classified {len(titles)} titles: {classification}")
            return classification
        except Exception as e:
            logger.error(f"Failed to classify titles: {e}")
            # Fallback heuristic
            fallback = {}
            for t in titles:
                tl = t.lower()
                if "anexo" in tl or "formulário" in tl or "declaração" in tl:
                    fallback[t] = "anexo"
                elif "alteração" in tl or "retificação" in tl or "aditivo" in tl:
                    fallback[t] = "alteração"
                else:
                    fallback[t] = "edital"
            return fallback

    def _get_extraction_prompt(self, ocr_text: str) -> str:
        return f"""
Analise o seguinte texto OCR de um edital de fomento e extraia as informações estruturadas em formato JSON.

Para preencher o campo 'descrição', procure especificamente pela seção 'Objeto' ou pela seção 'Finalidade' (ou termos similares) no texto do edital e utilize-a para redigir um resumo claro e conciso.

O JSON deve seguir exatamente esta estrutura:
{{
    "nome": "Título oficial do edital",
    "descrição": "Resumo conciso baseado na seção 'Objeto' ou 'Finalidade' do edital",
    "orgão_fomento": "Nome da instituição (Ex: FAPES)",
    "categoria": "extensão, pesquisa, inovação ou outros",
    "status": "aberto",
    "data_abertura": "YYYY-MM-DD",
    "data_encerramento": "YYYY-MM-DD ou \"\"",
    "cronograma": [
        {{"evento": "Descrição da etapa", "data": "ISO YYYY-MM-DD ou texto original caso seja data relativa (ex: '5 dias úteis após...')"}}
    ],
    "tags": ["lista", "de", "palavras-chave", "(MÍNIMO 3 TAGS)"]
}}

IMPORTANTE para o CRONOGRAMA:
1. Priorize o formato ISO YYYY-MM-DD.
2. Se houver um intervalo (ex: '10/11/2025 a 16/12/2025'), use apenas a primeira data no formato ISO ('2025-11-10').
3. Se o texto disser 'A partir de 26/10/2026', use '2026-10-26'.
4. Se a data for relativa (ex: '5 dias úteis após o resultado preliminar'), mantenha o texto original para processamento posterior.

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
