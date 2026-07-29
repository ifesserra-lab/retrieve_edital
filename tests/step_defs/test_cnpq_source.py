"""
Testes do CnpqSource após a migração do portal descontinuado para o gov.br.

O source antigo lia `memoria2.cnpq.br`, que responde 200 com 137 KB mas contém
um único card — o fluxo parecia saudável coletando quase nada. Ver
`docs/spec_finep_cnpq_horizon.md`.
"""

import requests

from src.components.sources.cnpq_source import (
    CNPQ_ABERTAS_URL,
    DEADLINE_EVENT,
    OPENING_EVENT,
    CnpqSource,
    _dd_mm_yyyy_to_iso,
    _is_document_url,
)

CHAMADA_URL = (
    "https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026"
    "/chamada-no-25-2026/chamada-publica-cnpq-N-25-2026"
)
CHAMADA_DIR = CHAMADA_URL.rsplit("/", 1)[0]

LISTING_HTML = f"""
<html><body>
  <p class="callout"><a href="https://www.gov.br/cnpq/pt-br/chamadas/Busca_abertas">Busca</a></p>
  <div class="item visualIEFloatFix">
    <h2 class="headline"><a class="summary url" href="{CHAMADA_URL}">Chamada CNPq nº 25/2026</a></h2>
    <div class="social-links">
      <a href="http://www.facebook.com/sharer.php?u={CHAMADA_URL}">Facebook</a>
    </div>
  </div>
  <div class="item visualIEFloatFix">
    <h2 class="headline"><a class="summary url" href="{CHAMADA_DIR}/Chamada252026.pdf">PDF solto</a></h2>
  </div>
</body></html>
"""


def build_detail_html(inscricoes: str = "INSCRIÇÕES: 10/07/2026 a 12/08/2026") -> str:
    return f"""
    <html><body>
      <h1 class="documentFirstHeading">Chamada CNPq/MCTI nº 25/2026 - Endometriose</h1>
      <div id="content-core"><div id="parent-fieldname-text">
        <p>Publicado em 10/07/2026 14h37</p>
        <p>O CNPq torna pública a Chamada nº 25/2026, que tem por objeto o apoio à pesquisa.</p>
        <a href="{CHAMADA_DIR}/Chamada252026.pdf">Chamada</a>
        <a href="{CHAMADA_DIR}/AnexoI.docx">Anexo I - Modelo de Projeto (Word)</a>
        <a href="https://www.gov.br/cnpq/pt-br/acesso-a-informacao/acoes-e-programas/carta-de-servicos-06-25.pdf">Carta de Serviços</a>
        <p>{inscricoes}</p>
      </div></div>
    </body></html>
    """


class FakeResponse:
    def __init__(self, text="", content=b"", headers=None, url=""):
        self.text = text
        self.content = content
        self.headers = headers or {}
        self.url = url

    def raise_for_status(self):
        return None


class FakeSession:
    """Sessão falsa: devolve conteúdo por URL e registra o que foi pedido."""

    def __init__(self, pages=None, pdf_bytes=b"%PDF-fake", raise_on=None):
        self.pages = pages if pages is not None else {}
        self.pdf_bytes = pdf_bytes
        self.raise_on = raise_on or set()
        self.requested = []

    def get(self, url, timeout=None):
        self.requested.append(url)
        if url in self.raise_on:
            raise requests.RequestException("indisponível")
        if url.lower().endswith(".pdf"):
            return FakeResponse(
                content=self.pdf_bytes,
                headers={"content-type": "application/pdf"},
                url=url,
            )
        return FakeResponse(text=self.pages.get(url, ""), url=url)


def build_source(session=None, **kwargs):
    session = session or FakeSession(
        pages={CNPQ_ABERTAS_URL: LISTING_HTML, CHAMADA_URL: build_detail_html()}
    )
    kwargs.setdefault("current_year", 2026)
    return CnpqSource(session=session, **kwargs), session


class TestHelpers:
    def test_dd_mm_yyyy_to_iso(self):
        assert _dd_mm_yyyy_to_iso("12/08/2026") == "2026-08-12"
        assert _dd_mm_yyyy_to_iso("nao e data") == ""

    def test_is_document_url_requires_the_chamadas_path(self):
        assert _is_document_url(f"{CHAMADA_DIR}/Chamada.pdf") is True
        # Boilerplate do portal, presente em toda página do gov.br.
        assert (
            _is_document_url(
                "https://www.gov.br/cnpq/pt-br/acesso-a-informacao/carta-de-servicos.pdf"
            )
            is False
        )
        assert _is_document_url(f"{CHAMADA_DIR}/pagina-sem-extensao") is False


class TestListingExtraction:
    def test_collects_one_entry_per_chamada_page(self):
        source, _ = build_source()
        raw_editais = source.read()
        assert len(raw_editais) == 1
        assert raw_editais[0].url == CHAMADA_URL

    def test_ignores_share_links(self):
        """A listagem repete a URL da chamada dentro dos links de compartilhamento."""
        source, session = build_source()
        source.read()
        assert not any("facebook" in url for url in session.requested)

    def test_tracks_listing_count_before_deduplication(self):
        source, _ = build_source(processed_urls={CHAMADA_URL})
        assert source.read() == []
        assert source.last_listing_count == 1

    def test_no_longer_references_the_discontinued_portal(self):
        source, _ = build_source()
        assert "memoria2" not in source.listing_url


class TestDetailMapping:
    def test_maps_identity_and_agency(self):
        source, _ = build_source()
        raw = source.read()[0]
        assert raw.raw_agency == "CNPq"
        assert raw.title.startswith("Chamada CNPq/MCTI nº 25/2026")
        assert "apoio à pesquisa" in raw.raw_description

    def test_cronograma_carries_the_inscricao_period(self):
        source, _ = build_source()
        raw = source.read()[0]
        assert raw.raw_cronograma == [
            {"evento": OPENING_EVENT, "data": "2026-07-10"},
            {"evento": DEADLINE_EVENT, "data": "2026-08-12"},
        ]

    def test_cms_publication_date_is_not_part_of_the_cronograma(self):
        """O normalizer prioriza eventos de publicação e sobreporia a abertura real."""
        source, _ = build_source()
        eventos = [c["evento"] for c in source.read()[0].raw_cronograma]
        assert not any("publica" in e.lower() for e in eventos)

    def test_description_does_not_repeat_the_inscricao_line(self):
        source, _ = build_source()
        assert "INSCRIÇÕES" not in source.read()[0].raw_description

    def test_anexos_exclude_portal_boilerplate(self):
        source, _ = build_source()
        titulos = [a["titulo"] for a in source.read()[0].raw_anexos]
        assert "Chamada" in titulos
        assert "Anexo I - Modelo de Projeto (Word)" in titulos
        assert "Carta de Serviços" not in titulos

    def test_downloads_the_document_labelled_chamada_for_ocr(self):
        source, session = build_source()
        raw = source.read()[0]
        assert raw.pdf_content == session.pdf_bytes
        assert f"{CHAMADA_DIR}/Chamada252026.pdf" in session.requested


class TestYearFilter:
    def test_discards_chamada_closed_before_the_current_year(self):
        session = FakeSession(
            pages={
                CNPQ_ABERTAS_URL: LISTING_HTML,
                CHAMADA_URL: build_detail_html("INSCRIÇÕES: 01/02/2025 a 30/06/2025"),
            }
        )
        source, _ = build_source(session=session, current_year=2026)
        assert source.read() == []

    def test_keeps_chamada_closing_in_a_future_year(self):
        session = FakeSession(
            pages={
                CNPQ_ABERTAS_URL: LISTING_HTML,
                CHAMADA_URL: build_detail_html("INSCRIÇÕES: 01/02/2026 a 30/06/2027"),
            }
        )
        source, _ = build_source(session=session, current_year=2026)
        assert len(source.read()) == 1

    def test_accepts_the_chamamento_wording_for_the_period(self):
        """Chamamentos públicos rotulam o período como "Recebimento das propostas"."""
        session = FakeSession(
            pages={
                CNPQ_ABERTAS_URL: LISTING_HTML,
                CHAMADA_URL: build_detail_html(
                    "Recebimento das propostas: 02/07/2026 a 17/08/2026"
                ),
            }
        )
        source, _ = build_source(session=session, current_year=2026)
        assert source.read()[0].raw_cronograma == [
            {"evento": OPENING_EVENT, "data": "2026-07-02"},
            {"evento": DEADLINE_EVENT, "data": "2026-08-17"},
        ]

    def test_keeps_chamada_without_a_declared_period(self):
        session = FakeSession(
            pages={
                CNPQ_ABERTAS_URL: LISTING_HTML,
                CHAMADA_URL: build_detail_html("sem periodo declarado"),
            }
        )
        source, _ = build_source(session=session, current_year=2026)
        raw_editais = source.read()
        assert len(raw_editais) == 1
        assert raw_editais[0].raw_cronograma is None


class TestResilience:
    def test_listing_failure_returns_empty_and_zeroes_counter(self):
        session = FakeSession(pages={}, raise_on={CNPQ_ABERTAS_URL})
        source, _ = build_source(session=session)
        assert source.read() == []
        assert source.last_listing_count == 0

    def test_detail_failure_skips_only_that_chamada(self):
        session = FakeSession(
            pages={CNPQ_ABERTAS_URL: LISTING_HTML}, raise_on={CHAMADA_URL}
        )
        source, _ = build_source(session=session)
        assert source.read() == []
        assert source.last_listing_count == 1

    def test_non_pdf_response_is_not_used_as_ocr_content(self):
        class HtmlInsteadOfPdfSession(FakeSession):
            def get(self, url, timeout=None):
                self.requested.append(url)
                if url.lower().endswith(".pdf"):
                    return FakeResponse(
                        content=b"<html>erro</html>",
                        headers={"content-type": "text/html"},
                        url=url,
                    )
                return FakeResponse(text=self.pages.get(url, ""), url=url)

        session = HtmlInsteadOfPdfSession(
            pages={CNPQ_ABERTAS_URL: LISTING_HTML, CHAMADA_URL: build_detail_html()}
        )
        source, _ = build_source(session=session)
        assert source.read()[0].pdf_content is None
