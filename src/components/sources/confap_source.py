"""
CONFAP — chamadas de cooperação internacional.

O CONFAP é o conselho das 26 Fundações Estaduais de Amparo à Pesquisa, e o PDF
de análise do portal (`docs/analise_portal_ifes_serra.pdf`, §2.1) o aponta como
"hub nacional — indexar prioritariamente", sugerindo que ele agregaria as
chamadas das FAPs.

**O recon de 2026-08-16 mostrou que não é isso.** Cinco editais amostrados
(114, 113, 110, 107, 100) seguem o mesmo padrão sem exceção: chamada do próprio
CONFAP em parceria com uma agência estrangeira, cofinanciada por um subconjunto
de FAPs participantes. Exemplo:

    Chamada CONFAP & CDTI 2026-2027
      CONFAP + CDTI (Espanha)
      FAPs participantes: F. Araucária (PR), FAPEAM, FAPEG, FAPEMA,
                          FAPERGS, FAPES, FAPESB

Não há edital próprio da FAPESP, da FAPERJ ou de qualquer outra FAP nessa
listagem. Este source portanto **acrescenta** cooperação internacional ao
acervo; ele não substitui a coleta por FAP. Como o IFES Serra é do Espírito
Santo, a FAP relevante é a FAPES, que já tem flow próprio — as demais ficam
como baixa prioridade por serem de outros estados.

Estrutura do portal (HTML estático, sem JS — `requests` basta):

    listagem  https://confap.org.br/pt/editais/            (10 itens)
              https://confap.org.br/pt/editais/pagina=N    (10 em 10)
    detalhe   https://confap.org.br/pt/editais/{id}/{slug}

`robots.txt` permite `/pt/editais/`; o que ele bloqueia é `/news/`.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.core.interfaces import ISource
from src.domain.models import RawEdital
from src.flow_health import warn_on_redirect

logger = logging.getLogger(__name__)

CONFAP_BASE_URL = "https://confap.org.br"
CONFAP_EDITAIS_URL = "https://confap.org.br/pt/editais/"

# Cada página traz 10 itens e o offset vai no próprio caminho, não em query
# string: /pt/editais/pagina=10 é a segunda página.
PAGE_SIZE = 10
DEFAULT_MAX_PAGES = 3

DETAIL_PATH_REGEX = re.compile(r"/pt/editais/(\d+)/[^\"'\s]+")
DATE_REGEX = re.compile(r"(\d{2})/(\d{2})/(\d{4})")

# Título do edital na página de detalhe. O `h1` é o rótulo fixo da seção
# ("Editais"); o título real é o primeiro `h2` do bloco de conteúdo.
TITLE_SELECTOR = "h2.text-primary.h5"
DESCRIPTION_SELECTOR = "p.mb-md-4"

# Bloco de metadados da chamada, com rótulos em <b>:
#
#     <p class="mb-4">
#       <b>Objeto:</b> <br>
#       <b>​Data de Encerramento:</b> 08/10/2026<br>
#       <b>Status:</b> Em andamento
#     </p>
#
# É a fonte autoritativa do prazo. Antes o prazo saía de `max()` das datas do
# texto corrido, o que é chute: a maior data de um edital pode ser o fim da
# execução do projeto, não o fim das submissões.
# O rótulo vem precedido de um zero-width space (U+200B) no HTML do portal, e o
# valor é irmão do <b>, não filho — por isso a leitura é por regex no texto do
# bloco, e não por travessia de nós.
METADATA_SELECTOR = "p.mb-4"
DEADLINE_REGEX = re.compile(
    r"data\s+de\s+encerramento\s*:?\s*(\d{2}/\d{2}/\d{4})", re.I
)
STATUS_REGEX = re.compile(r"status\s*:?\s*([A-Za-zÀ-ú ]+)", re.I)

# O corpo escreve a data de lançamento por extenso ("lançou, em 25 de maio de
# 2026, o edital..."), então o formato numérico sozinho não a encontra.
MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}
LONG_DATE_REGEX = re.compile(
    r"(\d{1,2})\s+de\s+(" + "|".join(MESES) + r")\s+de\s+(\d{4})", re.I
)

# Vocabulário de status do portal → o do domínio.
STATUS_MAP = {
    "em andamento": "aberto",
    "finalizado": "encerrado",
}

DOCUMENT_EXTENSIONS = (".pdf", ".doc", ".docx", ".xls", ".xlsx")

# Sigla de FAP citada no corpo do edital. Serve para registrar quais fundações
# aderiram à chamada — é a informação que o pesquisador do IFES precisa para
# saber se a FAPES está entre elas.
FAP_REGEX = re.compile(
    r"\b(FAP[A-Z]{1,4}|FUNCAP|FUNDECT|FACEPE|Funda[çc][ãa]o Arauc[áa]ria)\b"
)

CATEGORY = "pesquisa"
AGENCY = "CONFAP"


def _parse_date(value: str) -> str:
    """Converte dd/mm/aaaa em ISO; devolve vazio quando não casa."""
    match = DATE_REGEX.search(value or "")
    if not match:
        return ""
    day, month, year = match.groups()
    try:
        return datetime(int(year), int(month), int(day)).date().isoformat()
    except ValueError:
        return ""


def _first_date_in_text(texto: str) -> str:
    """
    Primeira data do texto, aceitando `dd/mm/aaaa` e `25 de maio de 2026`.

    O portal usa as duas formas: a numérica nos metadados, a por extenso no
    corpo. Vence a que aparecer antes, para que a data de lançamento citada na
    abertura do texto não seja passada para trás por uma data posterior.
    """
    candidatos = []
    curta = DATE_REGEX.search(texto or "")
    if curta:
        candidatos.append((curta.start(), _parse_date(curta.group(0))))
    longa = LONG_DATE_REGEX.search(texto or "")
    if longa:
        dia, mes, ano = longa.groups()
        try:
            iso = datetime(int(ano), MESES[mes.lower()], int(dia)).date().isoformat()
        except (ValueError, KeyError):
            iso = ""
        candidatos.append((longa.start(), iso))
    for _, iso in sorted(candidatos):
        if iso:
            return iso
    return ""


class ConfapSource(ISource[RawEdital]):
    """Lê as chamadas do CONFAP, da listagem paginada até a página de detalhe."""

    def __init__(
        self,
        listing_url: str = CONFAP_EDITAIS_URL,
        processed_urls: Optional[Set[str]] = None,
        max_pages: int = DEFAULT_MAX_PAGES,
        current_year: Optional[int] = None,
        timeout: int = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.listing_url = listing_url
        self.processed_urls = processed_urls or set()
        self.max_pages = max_pages
        self.current_year = (
            current_year if current_year is not None else datetime.now().year
        )
        self.timeout = timeout
        self.session = session or requests.Session()
        # Quantos itens a listagem devolveu antes da deduplicação. O runner usa
        # esse número para distinguir "portal sem novidade" de "source quebrado".
        self.last_listing_count = 0

    # ------------------------------------------------------------------ #

    def read(self) -> List[RawEdital]:
        entradas = self._collect_listing_entries()
        self.last_listing_count = len(entradas)
        logger.info("ConfapSource encontrou %s chamadas na listagem.", len(entradas))

        raw_editais: List[RawEdital] = []
        for detail_url in entradas:
            if detail_url in self.processed_urls:
                logger.debug("Chamada já processada; ignorando: %s", detail_url)
                continue
            try:
                raw = self._build_raw_edital(detail_url)
            except requests.RequestException as exc:
                logger.error("Erro ao ler a chamada %s: %s", detail_url, exc)
                continue
            if raw is not None:
                raw_editais.append(raw)

        logger.info(
            "ConfapSource selecionou %s chamadas novas de %s na listagem.",
            len(raw_editais),
            len(entradas),
        )
        return raw_editais

    # ------------------------------------------------------------------ #

    def _collect_listing_entries(self) -> List[str]:
        """
        URLs de detalhe, da página mais recente para a mais antiga, sem repetir.

        A paginação é por offset no caminho. Para quando uma página não traz
        nenhum item novo — o portal responde 200 com a primeira página quando o
        offset passa do fim, e sem essa parada o laço giraria até `max_pages`
        relendo sempre o mesmo conteúdo.
        """
        vistos: Set[str] = set()
        ordenadas: List[str] = []

        for indice in range(self.max_pages):
            url = (
                self.listing_url
                if indice == 0
                else urljoin(self.listing_url, f"pagina={indice * PAGE_SIZE}")
            )
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                if indice == 0:
                    warn_on_redirect(self.listing_url, response.url)
            except requests.RequestException as exc:
                logger.error("Erro ao ler a listagem do CONFAP (%s): %s", url, exc)
                break

            novos = [u for u in self._extract_detail_urls(response.text) if u not in vistos]
            if not novos:
                logger.debug("Página %s não trouxe item novo; encerrando paginação.", indice)
                break
            vistos.update(novos)
            ordenadas.extend(novos)

        return ordenadas

    @staticmethod
    def _extract_detail_urls(html: str) -> List[str]:
        """URLs de detalhe da listagem, na ordem em que aparecem, sem repetir."""
        soup = BeautifulSoup(html, "html.parser")
        urls: List[str] = []
        vistos: Set[str] = set()
        for anchor in soup.find_all("a", href=True):
            if not DETAIL_PATH_REGEX.search(anchor["href"]):
                continue
            url = urljoin(CONFAP_BASE_URL, anchor["href"])
            if url not in vistos:
                vistos.add(url)
                urls.append(url)
        return urls

    # ------------------------------------------------------------------ #

    def _build_raw_edital(self, detail_url: str) -> Optional[RawEdital]:
        response = self.session.get(detail_url, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = self._extract_title(soup)
        if not title:
            logger.warning("Chamada sem título reconhecível; ignorando: %s", detail_url)
            return None

        description = self._extract_description(soup)
        metadados = self._extract_metadata(soup)
        cronograma = self._extract_cronograma(soup, metadados.get("encerramento", ""))
        anexos = self._extract_anexos(soup)
        faps = self._extract_faps(soup)

        # As FAPs participantes viram tag: é por elas que o pesquisador descobre
        # se a fundação do seu estado aderiu à chamada.
        tags = ["cooperação internacional", "CONFAP"] + sorted(faps)

        return RawEdital(
            title=title,
            url=detail_url,
            source_category=CATEGORY,
            raw_agency=AGENCY,
            raw_description=description,
            raw_cronograma=cronograma or None,
            raw_tags=tags,
            raw_anexos=anexos or None,
            raw_ambito_geografico="internacional",
            raw_status=metadados.get("status") or None,
            document_type="edital",
        )

    @staticmethod
    def _extract_metadata(soup: BeautifulSoup) -> Dict[str, str]:
        """
        Lê prazo e status do bloco de metadados rotulado do portal.

        Devolve dicionário possivelmente vazio: nem toda chamada traz o bloco, e
        ausência de prazo é resposta legítima — melhor vazio do que um palpite.
        """
        dados: Dict[str, str] = {}
        for bloco in soup.select(METADATA_SELECTOR):
            texto = bloco.get_text(" ", strip=True)
            prazo = DEADLINE_REGEX.search(texto)
            if prazo:
                iso = _parse_date(prazo.group(1))
                if iso:
                    dados["encerramento"] = iso
            status = STATUS_REGEX.search(texto)
            if status:
                bruto = status.group(1).strip().lower()
                dados["status"] = STATUS_MAP.get(bruto, bruto)
        return dados

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        node = soup.select_one(TITLE_SELECTOR)
        return node.get_text(" ", strip=True) if node else ""

    @staticmethod
    def _extract_description(soup: BeautifulSoup) -> str:
        partes = [
            p.get_text(" ", strip=True) for p in soup.select(DESCRIPTION_SELECTOR)
        ]
        return "\n".join(t for t in partes if t).strip()

    @staticmethod
    def _extract_cronograma(
        soup: BeautifulSoup, encerramento: str = ""
    ) -> List[Dict[str, str]]:
        """
        Cronograma da chamada: publicação (do texto) e prazo (dos metadados).

        A publicação sai da primeira data do corpo — o portal escreve "lançou,
        em 25 de maio de 2026, o edital...". A leitura é restrita aos parágrafos
        de conteúdo, não à página inteira: a barra lateral traz "Notícias"
        datadas, e uma data de notícia entrando aqui viraria data de edital.

        O prazo **não** é inferido do texto: vem do campo rotulado
        `Data de Encerramento`. Sem esse campo, o edital fica sem prazo, que é o
        estado correto para uma chamada de fluxo contínuo ou de prazo ainda não
        publicado.
        """
        corpo = soup.select(DESCRIPTION_SELECTOR)
        texto = " ".join(p.get_text(" ", strip=True) for p in corpo)

        cronograma: List[Dict[str, str]] = []
        publicacao = _first_date_in_text(texto)

        # A publicação só entra se for estritamente anterior ao prazo. A primeira
        # data do corpo nem sempre é a de lançamento — pode ser a de um evento
        # citado antes dele — e o resultado apareceu na amostragem: a chamada
        # nexBio saía com publicação 2026-08-14 e prazo 2026-05-18, e a DAAD com
        # as duas iguais. Data incoerente é pior que data ausente: o normalizador
        # deriva `data_abertura` do cronograma e gravaria um edital que abre
        # depois de fechar. O prazo, esse é campo rotulado do portal e fica.
        if publicacao and encerramento and publicacao >= encerramento:
            logger.debug(
                "Publicação inferida (%s) não é anterior ao prazo (%s); descartando.",
                publicacao,
                encerramento,
            )
            publicacao = ""

        if publicacao:
            cronograma.append({"evento": "Publicação da chamada", "data": publicacao})
        if encerramento:
            cronograma.append(
                {"evento": "Prazo para envio da proposta", "data": encerramento}
            )
        return cronograma

    @staticmethod
    def _extract_anexos(soup: BeautifulSoup) -> List[Dict[str, str]]:
        anexos: List[Dict[str, str]] = []
        vistos: Set[str] = set()
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if not href.lower().endswith(DOCUMENT_EXTENSIONS):
                continue
            url = urljoin(CONFAP_BASE_URL, href)
            if url in vistos:
                continue
            vistos.add(url)
            anexos.append(
                {
                    "titulo": anchor.get_text(" ", strip=True) or "Documento",
                    "link": url,
                    "tipo": "pdf",
                }
            )
        return anexos

    @staticmethod
    def _extract_faps(soup: BeautifulSoup) -> Set[str]:
        texto = soup.get_text(" ", strip=True)
        return {m.group(0) for m in FAP_REGEX.finditer(texto)}
