"""
Contrato de extração compartilhado entre os provedores de LLM.

O pipeline tem dois provedores — Mistral (principal) e OpenAI (reserva) — e eles
precisam produzir **exatamente o mesmo objeto de domínio**. Se cada um carregasse
seu próprio prompt e seu próprio mapeamento, a troca de provedor mudaria
silenciosamente o formato dos editais gravados, e o fallback deixaria de ser
transparente para virar uma segunda fonte de verdade.

Por isso o prompt, o schema pedido e o mapeamento para `EditalDomain` moram aqui,
e não dentro de nenhum cliente. Os clientes cuidam só do transporte: como falar
com a API, como tratar erro e como obter o texto do PDF.
"""

import json
from typing import Any, Dict, List

from src.domain.models import EditalDomain

SYSTEM_PROMPT_EXTRACTION = (
    "Você é um especialista em análise de editais públicos de fomento "
    "(FAPES, CNPq, etc)."
)
SYSTEM_PROMPT_CLASSIFY_TITLES = (
    "Você é um assistente especializado em organizar documentos de editais de fomento."
)
SYSTEM_PROMPT_FINEP = (
    "Você é um classificador de editais de fomento. Responda apenas com o JSON solicitado."
)

FINEP_CATEGORIES = ("divulgação de conhecimento", "extensão", "inovação")


class ExtractionUnavailableError(RuntimeError):
    """
    Base de "não há provedor de extração vivo".

    Existe para que as camadas que precisam deixar essa falha passar — source,
    normalizador e os oito fluxos — capturem **um** tipo, em vez de enumerar as
    exceções de cada provedor e esquecerem de atualizar a lista quando entrar um
    provedor novo. Foi assim que o 402 da Mistral ficou invisível por sete dias.

    Herda de `RuntimeError` por compatibilidade com quem já capturava isso.

    Não confundir com falha de **um documento** (PDF corrompido, PDF digitalizado
    sem camada de texto): essa continua sendo absorvida por item, e por isso não
    herda daqui.
    """


def build_extraction_prompt(ocr_text: str) -> str:
    """Prompt de extração estruturada a partir do texto do edital."""
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


def build_classify_titles_prompt(titles: List[str]) -> str:
    """Prompt de classificação dos documentos de um grupo de edital."""
    return f"""
Classifique cada título de documento abaixo em uma das seguintes categorias:
- 'edital': O documento principal da chamada pública ou concurso.
- 'anexo': Documentos técnicos, formulários, declarações ou manuais complementares.
- 'alteração': Aditivos, retificações ou mudanças no edital original.

Retorne APENAS um JSON onde a chave é o título exato e o valor é a categoria.

Títulos:
{json.dumps(titles, indent=2, ensure_ascii=False)}
"""


def build_finep_category_prompt(description: str) -> str:
    """Prompt de categorização de uma chamada FINEP pela descrição."""
    return f"""
Classifique o edital de chamada pública FINEP abaixo em exatamente UMA destas categorias:
- divulgação de conhecimento: difusão científica, popularização da ciência, museus, feiras, eventos de divulgação, educação científica para o público.
- extensão: extensão universitária, projetos que levam conhecimento à comunidade, parcerias universidade-sociedade, ações extensionistas.
- inovação: PD&I, desenvolvimento tecnológico, inovação em empresas, subvenção econômica, startups, produtos/processos inovadores.

Retorne APENAS um JSON com uma única chave "categoria" e o valor sendo exatamente uma das três opções acima (use a grafia exata).

Descrição do edital:
{description[:4000]}
"""


def map_to_domain(data: Dict[str, Any]) -> EditalDomain:
    """Converte o JSON devolvido pelo LLM no objeto de domínio."""
    return EditalDomain(
        nome=data.get("nome", "").upper(),
        descrição=data.get("descrição", ""),
        orgão_fomento=data.get("orgão_fomento", "FAPES").upper(),
        categoria=data.get("categoria", "outros").lower(),
        status=data.get("status", "aberto"),
        data_abertura=data.get("data_abertura") or "2026-01-01",  # Default if missing
        data_encerramento=data.get("data_encerramento") or "",
        link="",  # This will be set by the normalizer who has the URL
        cronograma=[
            {
                "evento": item.get("evento") or item.get("etapa", ""),
                "data": item.get("data") or "",
            }
            for item in data.get("cronograma", [])
        ],
        tags=(
            data.get("tags")
            if data.get("tags") and len(data.get("tags")) > 0
            else ["fapes", "edital", "inovação"]
        ),
    )


def canonical_finep_category(raw: str) -> str:
    """
    Normaliza a resposta do LLM para uma das três categorias FINEP.

    Devolve string vazia quando a resposta não corresponde a nenhuma — cabe ao
    chamador decidir o fallback, em vez de receber um palpite plausível.
    """
    cat = (raw or "").strip().lower()
    if cat in FINEP_CATEGORIES:
        return cat
    for allowed in FINEP_CATEGORIES:
        if allowed in cat or cat in allowed:
            return allowed
    return ""
