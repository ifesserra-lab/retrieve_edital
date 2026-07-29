"""
Horizon Europe Source (dataset bulk do Funding & Tenders Portal).

A `search-api` do SEDIA, citada na análise original, responde `500 An internal
error occurred` a todas as variantes de query testadas, e `405` no GET. O
caminho que funciona é o dataset bulk público:

    https://ec.europa.eu/info/funding-tenders/opportunities/data/referenceData/grantsTenders.json

Sem autenticação e sem API key, atualizado diariamente. São 11.141 registros de
todos os programas da Comissão Europeia, dos quais interessam os do
`frameworkProgramme` HORIZON com status `Open` ou `Forthcoming`.

**O EIC Accelerator já está aqui**, identificável pela divisão `HORIZON.3.1`
(*The European Innovation Council*) — não precisa de fonte separada.

Dois cuidados que o volume impõe:

- o arquivo tem ~126 MB (≈22 MB com `Accept-Encoding: gzip`), então os objetos
  são decodificados um a um, o que evita materializar os 11 mil dicionários de
  uma vez. O payload cru ainda fica na memória: o pico medido é de ~900 MB,
  confortável nos 7 GB do runner do GitHub Actions;
- há ~200 chamadas HORIZON abertas a qualquer momento, a maioria irrelevante
  para o IFES. **O filtro temático por divisão é obrigatório**: sem divisões
  configuradas o source não devolve nada, em vez de afogar o portal.
"""

import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional, Sequence, Set

import requests

from src.core.interfaces import ISource
from src.domain.models import RawEdital
from src.flow_health import warn_on_redirect

logger = logging.getLogger(__name__)

HORIZON_BULK_URL = (
    "https://ec.europa.eu/info/funding-tenders/opportunities/data"
    "/referenceData/grantsTenders.json"
)
# Página pública da chamada no Funding & Tenders Portal.
HORIZON_TOPIC_URL_TEMPLATE = (
    "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen"
    "/opportunities/topic-details/{identifier}"
)

FRAMEWORK_PROGRAMME = "HORIZON"
PUBLISHABLE_STATUSES = ("Open", "Forthcoming")

# Nenhuma divisão por padrão: sem triagem temática explícita, o source não
# devolve nada. Medição de 2026-07-29: as três divisões sugeridas abaixo rendem
# 192 chamadas relevantes, das quais 185 publicáveis — mais do que o portal
# inteiro tinha (153). Publicar isso sem curadoria afogaria as fontes nacionais.
#
# Configure `HORIZON_DIVISIONS` (separado por vírgula) para habilitar.
DEFAULT_DIVISIONS: tuple[str, ...] = ()

# Sugestão de partida, **pendente de validação da PRPPG**. Um prefixo cobre as
# subdivisões: `HORIZON.2.4` casa com `HORIZON.2.4.1` e assim por diante.
SUGGESTED_DIVISIONS = (
    "HORIZON.2.4",  # Digital, Industry and Space
    "HORIZON.2.5",  # Climate, Energy and Mobility
    "HORIZON.3.1",  # The European Innovation Council (inclui o EIC Accelerator)
)
EIC_DIVISION_PREFIX = "HORIZON.3.1"

# Categorias dentro do vocabulário já usado pelo portal. O EIC financia
# inovação empresarial; as demais divisões, pesquisa colaborativa.
CATEGORY_EIC = "inovação"
CATEGORY_RESEARCH = "pesquisa"

DEFAULT_TIMEOUT = 180

_OBJECT_LIST_KEY = "GrantTenderObj"


def _epoch_millis_to_iso(value: Any) -> str:
    """Converte epoch em milissegundos para `YYYY-MM-DD`."""
    if value is None:
        return ""
    try:
        millis = int(value)
    except (TypeError, ValueError):
        return ""
    return datetime.fromtimestamp(millis / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def _abbreviation_of(value: Any) -> str:
    if isinstance(value, dict):
        return (value.get("abbreviation") or "").strip()
    return ""


def _divisions_of(item: Dict[str, Any]) -> List[Dict[str, str]]:
    divisions = item.get("programmeDivision")
    if not isinstance(divisions, list):
        return []
    return [division for division in divisions if isinstance(division, dict)]


def get_configured_divisions(
    override: Optional[Sequence[str]] = None,
) -> tuple[str, ...]:
    """
    Divisões relevantes, por ordem de precedência: argumento, ambiente, default.

    Devolver tupla vazia é decisão válida e significa "não publicar nada" — mais
    seguro que publicar as ~200 chamadas abertas sem triagem.
    """
    if override is not None:
        return tuple(str(item).strip() for item in override if str(item).strip())
    raw = os.getenv("HORIZON_DIVISIONS", "").strip()
    if raw:
        return tuple(part.strip() for part in raw.split(",") if part.strip())
    return DEFAULT_DIVISIONS


def iter_json_objects(text: str, list_key: str = _OBJECT_LIST_KEY) -> Iterator[dict]:
    """
    Decodifica os objetos da lista um a um, sem materializar a estrutura inteira.

    `json.loads` sobre os 126 MB criaria mais de 11 mil dicionários de uma vez,
    quando só ~200 interessam.
    """
    marker = re.search(rf'"{re.escape(list_key)}"\s*:\s*\[', text)
    if marker is None:
        logger.error("Lista %s não encontrada no dataset do Horizon.", list_key)
        return

    decoder = json.JSONDecoder()
    position = marker.end()
    length = len(text)
    while position < length:
        while position < length and text[position] in " \t\r\n,":
            position += 1
        if position >= length or text[position] == "]":
            return
        try:
            obj, position = decoder.raw_decode(text, position)
        except ValueError as exc:
            logger.error("Dataset do Horizon malformado na posição %s: %s", position, exc)
            return
        if isinstance(obj, dict):
            yield obj


class HorizonSource(ISource[RawEdital]):
    """Extrai chamadas abertas do Horizon Europe do dataset bulk oficial."""

    def __init__(
        self,
        bulk_url: str = HORIZON_BULK_URL,
        divisions: Optional[Sequence[str]] = None,
        processed_urls: Optional[Set[str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.bulk_url = bulk_url
        self.divisions = get_configured_divisions(divisions)
        self.processed_urls = processed_urls or set()
        self.timeout = timeout
        self.session = session or requests.Session()
        # Quantas chamadas relevantes a origem devolveu antes da deduplicação.
        self.last_listing_count = 0
        if not self.divisions:
            logger.warning(
                "Nenhuma divisão do Horizon configurada: o source não devolverá "
                "chamadas. Defina HORIZON_DIVISIONS para habilitar."
            )
        else:
            logger.info(
                "HorizonSource filtrando pelas divisões: %s", ", ".join(self.divisions)
            )

    def read(self) -> List[RawEdital]:
        if not self.divisions:
            self.last_listing_count = 0
            return []

        try:
            payload = self._download_bulk()
        except requests.RequestException as exc:
            logger.error("Erro ao baixar o dataset do Horizon: %s", exc)
            self.last_listing_count = 0
            return []

        relevant: List[Dict[str, Any]] = [
            item for item in iter_json_objects(payload) if self._is_relevant(item)
        ]
        self.last_listing_count = len(relevant)
        logger.info(
            "Dataset do Horizon: %s chamadas relevantes nas divisões configuradas.",
            len(relevant),
        )

        raw_editais: List[RawEdital] = []
        for item in relevant:
            raw_edital = self._build_raw_edital(item)
            if raw_edital is not None:
                raw_editais.append(raw_edital)

        logger.info(
            "HorizonSource selecionou %s chamadas novas de %s relevantes.",
            len(raw_editais),
            len(relevant),
        )
        return raw_editais

    def _download_bulk(self) -> str:
        response = self.session.get(
            self.bulk_url,
            timeout=self.timeout,
            headers={"Accept-Encoding": "gzip, deflate"},
        )
        response.raise_for_status()
        warn_on_redirect(self.bulk_url, response.url)
        return response.text

    def _is_relevant(self, item: Dict[str, Any]) -> bool:
        if _abbreviation_of(item.get("status")) not in PUBLISHABLE_STATUSES:
            return False
        if _abbreviation_of(item.get("frameworkProgramme")) != FRAMEWORK_PROGRAMME:
            return False
        return self._matches_configured_division(item)

    def _matches_configured_division(self, item: Dict[str, Any]) -> bool:
        """Um prefixo configurado cobre as subdivisões abaixo dele."""
        for division in _divisions_of(item):
            abbreviation = _abbreviation_of(division)
            if any(abbreviation.startswith(prefix) for prefix in self.divisions):
                return True
        return False

    def _build_raw_edital(self, item: Dict[str, Any]) -> Optional[RawEdital]:
        identifier = (item.get("identifier") or "").strip()
        title = (item.get("title") or item.get("callTitle") or "").strip()
        if not identifier or not title:
            logger.debug("Chamada do Horizon sem identifier ou título; ignorando.")
            return None

        topic_url = HORIZON_TOPIC_URL_TEMPLATE.format(identifier=identifier)
        if topic_url in self.processed_urls or identifier in self.processed_urls:
            logger.debug("Chamada do Horizon já processada; ignorando: %s", identifier)
            return None

        return RawEdital(
            title=title,
            url=topic_url,
            source_category=self._category_of(item),
            raw_agency="Horizon Europe",
            raw_description=self._build_description(item, identifier),
            document_type="edital",
            raw_status=_abbreviation_of(item.get("status")).lower(),
            raw_cronograma=self._build_cronograma(item) or None,
            raw_tags=self._build_tags(item) or None,
            raw_anexos=self._build_anexos(item) or None,
        )

    @staticmethod
    def _category_of(item: Dict[str, Any]) -> str:
        """
        Categoria dentro do vocabulário que o portal já usa.

        Sem isso, todas as chamadas caíam em `outros`: o dataset não traz texto
        descritivo, então a inferência por palavra-chave do normalizer não tem
        onde se apoiar.
        """
        for division in _divisions_of(item):
            if _abbreviation_of(division).startswith(EIC_DIVISION_PREFIX):
                return CATEGORY_EIC
        return CATEGORY_RESEARCH

    @staticmethod
    def _build_description(item: Dict[str, Any], identifier: str) -> str:
        """
        Descrição composta dos metadados.

        O dataset bulk **não traz texto descritivo** — só título, identificador,
        datas, programa e links. A alternativa seria uma requisição por chamada à
        página do tópico; enquanto isso não existir, compõe-se do título da
        chamada e da descrição das divisões, que é informação real e barata.
        """
        parts: List[str] = []
        call_title = (item.get("callTitle") or "").strip()
        if call_title and call_title != (item.get("title") or "").strip():
            parts.append(f"Chamada: {call_title}.")
        descriptions = [
            (division.get("description") or "").strip()
            for division in _divisions_of(item)
        ]
        thematic = [text for text in descriptions if text]
        if thematic:
            parts.append("Área: " + "; ".join(dict.fromkeys(thematic)) + ".")
        parts.append(f"Identificador da chamada no Funding & Tenders Portal: {identifier}.")
        return " ".join(parts)

    @staticmethod
    def _build_cronograma(item: Dict[str, Any]) -> List[Dict[str, str]]:
        cronograma: List[Dict[str, str]] = []
        opening = _epoch_millis_to_iso(item.get("plannedOpeningDateLong"))
        if opening:
            cronograma.append({"evento": "Abertura das inscrições", "data": opening})

        deadlines = item.get("deadlineDatesLong")
        if not isinstance(deadlines, list):
            deadlines = [deadlines] if deadlines else []
        # Vários prazos indicam chamada em fases; o último é o encerramento.
        iso_deadlines = [d for d in (_epoch_millis_to_iso(v) for v in deadlines) if d]
        for index, deadline in enumerate(sorted(iso_deadlines)[:-1], start=1):
            cronograma.append({"evento": f"Prazo da fase {index}", "data": deadline})
        if iso_deadlines:
            cronograma.append(
                {"evento": "Prazo para envio de propostas", "data": max(iso_deadlines)}
            )
        return cronograma

    def _build_tags(self, item: Dict[str, Any]) -> List[str]:
        tags: List[str] = ["horizon europe", "internacional"]
        for division in _divisions_of(item):
            abbreviation = _abbreviation_of(division)
            if abbreviation.startswith(EIC_DIVISION_PREFIX):
                tags.append("eic")
            description = (division.get("description") or "").strip()
            if description and description not in tags:
                tags.append(description)
        keywords = item.get("keywords")
        if isinstance(keywords, list):
            tags.extend(str(word).strip() for word in keywords if str(word).strip())
        return list(dict.fromkeys(tags))

    @staticmethod
    def _build_anexos(item: Dict[str, Any]) -> List[Dict[str, str]]:
        anexos: List[Dict[str, str]] = []
        seen: Set[str] = set()
        for link in item.get("links") or []:
            if not isinstance(link, dict):
                continue
            url = (link.get("url") or "").strip()
            if not url or url in seen:
                continue
            seen.add(url)
            anexos.append(
                {
                    "titulo": (link.get("criterionDescription") or "Documento").strip(),
                    "link": url,
                    "tipo": "link",
                }
            )
        return anexos
