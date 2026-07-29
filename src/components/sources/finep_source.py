"""
FINEP Chamadas Públicas Source (API Liferay).

O portal antigo (`finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta`)
foi descontinuado: passou a responder 301 para `/oportunidades`, uma SPA cujo HTML
não contém edital algum. O scraper baseado em Playwright seguiu rodando contra a
página nova e extraindo zero itens durante meses. Ver `docs/spec_finep_cnpq_horizon.md`.

Este source consome a mesma API que o widget oficial do portal usa:

    POST /o/oauth2/token                        -> client_credentials
    GET  /o/c/chamadapublicas                   -> listagem (filtro por situação)
    GET  /o/c/chamadapublicas/{id}/documentos   -> anexos

As credenciais são de cliente público — o Liferay as embute no bundle JS servido a
qualquer visitante anônimo. São descobertas em tempo de execução a partir do bundle,
com um par conhecido como fallback, para que uma rotação no portal não volte a
derrubar a coleta em silêncio.

Sem Playwright: a API devolve título, descrição, datas e anexos já estruturados.
"""

import html
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Set

import requests

from src.config import get_reference_year
from src.core.interfaces import ISource
from src.domain.models import RawEdital
from src.flow_health import warn_on_redirect

logger = logging.getLogger(__name__)

FINEP_BASE_URL = "https://www.finep.gov.br"
FINEP_OPORTUNIDADES_URL = f"{FINEP_BASE_URL}/oportunidades"

TOKEN_PATH = "/o/oauth2/token"
CHAMADAS_PATH = "/o/c/chamadapublicas"
DOCUMENTOS_PATH_TEMPLATE = "/o/c/chamadapublicas/{chamada_id}/documentos"

# Página pública da chamada no portal novo. O segmento 222684 é o id do layout
# da página de detalhe e se mostrou estável em todas as chamadas verificadas.
PUBLIC_DETAIL_TEMPLATE = f"{FINEP_BASE_URL}/e/chamada-publica/222684/{{chamada_id}}"
# Chave usada pelo portal antigo. Mantida apenas para reconhecer chamadas já
# registradas em registry/processed_editais.json antes desta migração.
LEGACY_DETAIL_TEMPLATE = (
    "http://www.finep.gov.br/chamadas-publicas/chamadapublica/{database_id}"
)

OPEN_SITUATION_KEY = "aberta"
OPEN_SITUATION_FILTER = f"situacao eq '{OPEN_SITUATION_KEY}'"
DEFAULT_PAGE_SIZE = 100
DEFAULT_TIMEOUT = 30
# Trava de segurança: se a API parar de informar `totalCount`, a paginação não
# pode virar laço infinito dentro do job diário.
MAX_PAGES_HARD_LIMIT = 50

FALLBACK_CLIENT_ID = "idClientPRD"
FALLBACK_CLIENT_SECRET = "secretClientPRD"

_BUNDLE_PATH_REGEX = re.compile(
    r"/o/finep-busca-chamadas-publicas/assets/[\w.-]+\.js"
)
# No bundle minificado: btoa(`${oh}:${dh}`) — os nomes das variáveis mudam a cada
# build, então localizamos o par pelo uso e só depois resolvemos os literais.
_BTOA_PAIR_REGEX = re.compile(r"btoa\(`\$\{(\w+)\}:\$\{(\w+)\}`\)")
_HTML_TAG_REGEX = re.compile(r"<[^>]+>")

# Rótulos reconhecidos pelo EditalNormalizer ao derivar data_abertura/data_encerramento.
PUBLICATION_EVENT = "Data de publicação"
DEADLINE_EVENT = "Prazo para envio de propostas"


@dataclass(frozen=True)
class FinepCredentials:
    """Par de credenciais do cliente público OAuth2 do portal."""

    client_id: str
    client_secret: str


def _iso_date(value: Optional[str]) -> str:
    """Converte '2026-08-31T17:00:00.000Z' em '2026-08-31'."""
    if not value:
        return ""
    text = str(value).strip()
    match = re.match(r"(\d{4}-\d{2}-\d{2})", text)
    return match.group(1) if match else ""


def _year_of(iso_date: str) -> Optional[int]:
    if not iso_date:
        return None
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").year
    except ValueError:
        return None


def _strip_html(raw_html: Optional[str]) -> str:
    if not raw_html:
        return ""
    text = _HTML_TAG_REGEX.sub(" ", raw_html)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _name_of(value: Any) -> str:
    """Extrai o rótulo legível de um campo do tipo {'key': ..., 'name': ...}."""
    if isinstance(value, dict):
        return (value.get("name") or "").strip()
    if isinstance(value, str):
        return value.strip()
    return ""


def _names_of(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []
    return [name for name in (_name_of(item) for item in values) if name]


def _absolute_url(href: str, base_url: str) -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return f"{base_url.rstrip('/')}/{href.lstrip('/')}"


class FinepCredentialResolver:
    """
    Descobre as credenciais do cliente público OAuth2 no bundle JS do portal.

    Isolado do cliente HTTP para respeitar o SRP: aqui só se resolve *qual* par
    usar; a autenticação em si é responsabilidade do `FinepApiClient`.
    """

    def __init__(
        self,
        base_url: str = FINEP_BASE_URL,
        listing_url: str = FINEP_OPORTUNIDADES_URL,
        timeout: int = DEFAULT_TIMEOUT,
        fallback: Optional[FinepCredentials] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url
        self.listing_url = listing_url
        self.timeout = timeout
        self.fallback = fallback or FinepCredentials(
            client_id=FALLBACK_CLIENT_ID,
            client_secret=FALLBACK_CLIENT_SECRET,
        )
        self.session = session or requests.Session()

    def resolve(self) -> FinepCredentials:
        """Retorna as credenciais do bundle; cai no fallback quando não as encontra."""
        try:
            bundle = self._download_bundle()
        except requests.RequestException as exc:
            logger.warning(
                "Não foi possível baixar o bundle do portal FINEP (%s). "
                "Usando credenciais de fallback.",
                exc,
            )
            return self.fallback

        credentials = self._extract_credentials(bundle)
        if credentials is None:
            logger.warning(
                "Padrão de credenciais não encontrado no bundle FINEP. "
                "Usando credenciais de fallback."
            )
            return self.fallback

        if credentials != self.fallback:
            logger.info(
                "Credenciais do portal FINEP mudaram em relação ao fallback; "
                "usando as descobertas no bundle."
            )
        return credentials

    def _download_bundle(self) -> str:
        response = self.session.get(self.listing_url, timeout=self.timeout)
        response.raise_for_status()
        warn_on_redirect(self.listing_url, response.url)

        match = _BUNDLE_PATH_REGEX.search(response.text)
        if not match:
            return ""
        bundle_url = _absolute_url(match.group(0), self.base_url)
        bundle_response = self.session.get(bundle_url, timeout=self.timeout)
        bundle_response.raise_for_status()
        return bundle_response.text

    @staticmethod
    def _extract_credentials(bundle: str) -> Optional[FinepCredentials]:
        if not bundle:
            return None
        pair_match = _BTOA_PAIR_REGEX.search(bundle)
        if not pair_match:
            return None
        values = []
        for variable_name in pair_match.groups():
            literal = re.search(
                rf"\b{re.escape(variable_name)}\s*=\s*\"([^\"]+)\"", bundle
            )
            if literal is None:
                return None
            values.append(literal.group(1))
        return FinepCredentials(client_id=values[0], client_secret=values[1])


class FinepApiClient:
    """Cliente HTTP autenticado da API Liferay da FINEP."""

    def __init__(
        self,
        base_url: str = FINEP_BASE_URL,
        credential_resolver: Optional[FinepCredentialResolver] = None,
        timeout: int = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.credential_resolver = credential_resolver or FinepCredentialResolver(
            base_url=base_url, timeout=timeout, session=self.session
        )
        self._access_token: Optional[str] = None

    def get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET autenticado; renova o token uma vez em caso de 401."""
        response = self._authenticated_get(path, params)
        if response.status_code == 401:
            logger.info("Token FINEP expirado ou inválido; renovando.")
            self._access_token = None
            response = self._authenticated_get(path, params)
        response.raise_for_status()
        return response.json()

    def iter_items(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
        max_pages: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Itera os itens de um endpoint paginado da API."""
        page_limit = min(max_pages, MAX_PAGES_HARD_LIMIT) if max_pages else MAX_PAGES_HARD_LIMIT
        collected = 0
        for page_number in range(1, page_limit + 1):
            page_params = dict(params or {})
            page_params.update({"page": page_number, "pageSize": page_size})
            payload = self.get_json(path, page_params)
            items = payload.get("items") or []
            if not items:
                return
            for item in items:
                yield item
            collected += len(items)
            total_count = payload.get("totalCount")
            if total_count is not None and collected >= total_count:
                return
        logger.warning(
            "Paginação da API FINEP interrompida no limite de %s páginas.", page_limit
        )

    def _authenticated_get(
        self, path: str, params: Optional[Dict[str, Any]]
    ) -> requests.Response:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._token()}",
        }
        return self.session.get(
            f"{self.base_url}{path}",
            params=params,
            headers=headers,
            timeout=self.timeout,
        )

    def _token(self) -> str:
        if self._access_token:
            return self._access_token
        credentials = self.credential_resolver.resolve()
        response = self.session.post(
            f"{self.base_url}{TOKEN_PATH}",
            data={"grant_type": "client_credentials"},
            auth=(credentials.client_id, credentials.client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise ValueError("Resposta de token da FINEP não contém access_token.")
        self._access_token = token
        return token


class FinepSource(ISource[RawEdital]):
    """
    Extrai as chamadas públicas abertas da FINEP pela API oficial do portal.

    Mantém o filtro por ano de referência dos prazos e a deduplicação por URL,
    reconhecendo também as chaves no formato do portal antigo para não
    reprocessar o que já está em `registry/processed_editais.json`.
    """

    def __init__(
        self,
        reference_year: Optional[int] = None,
        max_pages: Optional[int] = None,
        processed_urls: Optional[Set[str]] = None,
        api_client: Optional[FinepApiClient] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
        base_url: str = FINEP_BASE_URL,
    ) -> None:
        self.reference_year = (
            reference_year if reference_year is not None else get_reference_year()
        )
        self.max_pages = max_pages
        self.processed_urls = processed_urls or set()
        self.page_size = page_size
        self.base_url = base_url.rstrip("/")
        self.api_client = api_client or FinepApiClient(base_url=base_url)
        # Quantas chamadas a origem devolveu na última leitura, antes da
        # deduplicação. O runner usa esse número para distinguir "nada novo"
        # de "o source quebrou". Ver src/flow_health.py.
        self.last_listing_count = 0
        logger.info(
            "FinepSource usando a API do portal (reference_year=%s, prazos a partir de %s)%s.",
            self.reference_year,
            self.reference_year,
            f", max_pages={max_pages}" if max_pages else "",
        )

    def read(self) -> List[RawEdital]:
        try:
            items = list(
                self.api_client.iter_items(
                    CHAMADAS_PATH,
                    params={
                        "filter": OPEN_SITUATION_FILTER,
                        "sort": "dataDePublicacao:desc",
                    },
                    page_size=self.page_size,
                    max_pages=self.max_pages,
                )
            )
        except (requests.RequestException, ValueError) as exc:
            logger.error("Erro ao consultar a API de chamadas da FINEP: %s", exc)
            self.last_listing_count = 0
            return []

        self.last_listing_count = len(items)
        logger.info("API FINEP devolveu %s chamadas abertas.", len(items))

        raw_editais: List[RawEdital] = []
        for item in items:
            # Um item malformado não pode derrubar a coleta das outras chamadas.
            try:
                raw_edital = self._build_raw_edital(item)
            except (AttributeError, TypeError, ValueError) as exc:
                logger.error(
                    "Chamada FINEP %s ignorada por erro de mapeamento: %s",
                    item.get("id") if isinstance(item, dict) else item,
                    exc,
                )
                continue
            if raw_edital is not None:
                raw_editais.append(raw_edital)

        logger.info(
            "FinepSource selecionou %s chamadas novas de %s abertas.",
            len(raw_editais),
            len(items),
        )
        return raw_editais

    def _build_raw_edital(self, item: Dict[str, Any]) -> Optional[RawEdital]:
        chamada_id = item.get("id")
        title = (item.get("titulo") or "").strip()
        if not chamada_id or not title:
            logger.debug("Chamada FINEP sem id ou título; ignorando: %s", item.get("id"))
            return None

        deadline = _iso_date(item.get("prazoProposto"))
        if not self._deadline_is_relevant(deadline):
            logger.debug(
                "Chamada '%s' descartada: prazo %s anterior a %s.",
                title[:60],
                deadline,
                self.reference_year,
            )
            return None

        public_url = PUBLIC_DETAIL_TEMPLATE.format(chamada_id=chamada_id)
        if self._already_processed(public_url, item.get("databaseId")):
            logger.debug("Chamada já processada; ignorando: %s", public_url)
            return None

        description = (item.get("descricaoRawText") or "").strip() or _strip_html(
            item.get("descricao")
        )

        return RawEdital(
            title=title,
            url=public_url,
            source_category="chamada pública",
            raw_agency="FINEP",
            raw_description=description,
            document_type="edital",
            raw_status=_name_of(item.get("situacao")).lower() or "aberta",
            raw_cronograma=self._build_cronograma(item, deadline) or None,
            raw_tags=self._build_tags(item) or None,
            raw_anexos=self._fetch_anexos(chamada_id) or None,
        )

    def _deadline_is_relevant(self, deadline: str) -> bool:
        """
        Aceita chamadas cujo prazo caia no ano de referência ou depois.

        A API já filtra por `situacao = aberta`, então uma chamada aberta com
        prazo distante continua válida — diferente do parser antigo, que só
        aceitava o ano de referência e o seguinte.
        """
        year = _year_of(deadline)
        if year is None:
            return True
        return year >= self.reference_year

    def _already_processed(self, public_url: str, database_id: Any) -> bool:
        if public_url in self.processed_urls:
            return True
        if database_id is None:
            return False
        legacy_url = LEGACY_DETAIL_TEMPLATE.format(database_id=database_id)
        return legacy_url in self.processed_urls

    @staticmethod
    def _build_cronograma(item: Dict[str, Any], deadline: str) -> List[Dict[str, str]]:
        cronograma: List[Dict[str, str]] = []
        publication = _iso_date(item.get("dataDePublicacao")) or _iso_date(
            item.get("vigenciaInicio")
        )
        if publication:
            cronograma.append({"evento": PUBLICATION_EVENT, "data": publication})
        if deadline:
            cronograma.append({"evento": DEADLINE_EVENT, "data": deadline})
        return cronograma

    @staticmethod
    def _build_tags(item: Dict[str, Any]) -> List[str]:
        """
        Monta as tags a partir dos metadados nativos da API.

        `publicoAlvo` e `tipoDeOportunidade` entram aqui por ora; a tarefa INF-02
        os promove a campos próprios do domínio (`publico_alvo`, `modalidade`).
        """
        candidates: List[str] = []
        candidates.append(_name_of(item.get("temaPrincipal")))
        candidates.extend(
            (brief.get("taxonomyCategoryName") or "").strip()
            for brief in item.get("taxonomyCategoryBriefs") or []
            if isinstance(brief, dict)
        )
        candidates.extend(_names_of(item.get("publicoAlvo")))
        candidates.append(_name_of(item.get("tipoDeOportunidade")))
        candidates.append(_name_of(item.get("regiao")))

        tags: List[str] = []
        for candidate in candidates:
            if candidate and candidate not in tags:
                tags.append(candidate)
        return tags

    def _fetch_anexos(self, chamada_id: Any) -> List[Dict[str, str]]:
        """Busca os documentos da chamada; falha aqui não invalida o edital."""
        path = DOCUMENTOS_PATH_TEMPLATE.format(chamada_id=chamada_id)
        try:
            payload = self.api_client.get_json(path, {"pageSize": 500})
        except (requests.RequestException, ValueError) as exc:
            logger.warning(
                "Não foi possível obter os documentos da chamada %s: %s",
                chamada_id,
                exc,
            )
            return []

        anexos: List[Dict[str, str]] = []
        for documento in payload.get("items") or []:
            anexo = self._build_anexo(documento)
            if anexo:
                anexos.append(anexo)
        return anexos

    def _build_anexo(self, documento: Dict[str, Any]) -> Optional[Dict[str, str]]:
        titulo = (documento.get("legenda") or "").strip() or "Documento"
        # O formato proprietário é o PDF do edital; o aberto (ODT) é o espelho legal.
        for field, tipo in (
            ("documentoProprietario", "pdf"),
            ("documentoAberto", "formato aberto"),
        ):
            href = self._document_href(documento.get(field))
            if href:
                return {
                    "titulo": titulo,
                    "link": _absolute_url(href, self.base_url),
                    "tipo": tipo,
                }
        return None

    @staticmethod
    def _document_href(document_field: Any) -> str:
        if not isinstance(document_field, dict):
            return ""
        link = document_field.get("link")
        if isinstance(link, dict):
            return (link.get("href") or "").strip()
        if isinstance(link, str):
            return link.strip()
        return ""
