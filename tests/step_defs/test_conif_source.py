from src.components.sources.conif_source import ConifSource, _extract_iso_date_from_pt_text


def test_extract_iso_date_from_pt_text():
    assert _extract_iso_date_from_pt_text("5 agosto 2025") == "2025-08-05"
    assert _extract_iso_date_from_pt_text("16 de junho de 2026") == "2026-06-16"
    assert _extract_iso_date_from_pt_text("sem data") is None


def test_extract_current_year_links_filters_non_current_year_and_processed_urls():
    html = """
    <html>
      <body>
        <h3><a href="/editais/2026/edital-1">Edital 1 - Atual</a></h3>
        <p><a href="/editais/2026/edital-1">Leia Mais</a></p>
        <h3><a href="/editais/2025/edital-2">Edital 2 - Antigo</a></h3>
        <h3><a href="/editais/2026/edital-3">Edital 3 - Processado</a></h3>
      </body>
    </html>
    """

    source = ConifSource(
        current_year=2026,
        processed_urls={"https://portal.conif.org.br/editais/2026/edital-3"},
    )

    result = source._extract_current_year_links(html)

    assert result == [
        {
            "title": "Edital 1 - Atual",
            "url": "https://portal.conif.org.br/editais/2026/edital-1",
        }
    ]


class FakePage:
    def __init__(self, html_by_url):
        self.html_by_url = html_by_url
        self.current_url = None

    def goto(self, url, timeout=None, wait_until=None):
        self.current_url = url

    def wait_for_load_state(self, state, timeout=None):
        return None

    def content(self):
        return self.html_by_url[self.current_url]


def test_extract_detail_page_maps_description_date_and_attachments():
    detail_url = "https://portal.conif.org.br/editais/2026/edital-1"
    html_by_url = {
        detail_url: """
        <html>
          <body>
            <h1>Edital 1 - Atual</h1>
            <p>22 março 2026</p>
            <p>O CONIF torna público o processo seletivo para inovação colaborativa.</p>
            <ul>
              <li><a href="/media/edital-1.pdf">EDITAL CONIF 01/2026</a></li>
              <li><a href="/media/resultado.pdf">Resultado preliminar</a></li>
            </ul>
          </body>
        </html>
        """
    }
    page = FakePage(html_by_url)
    source = ConifSource(current_year=2026)

    raw = source._extract_detail_page(page, detail_url, "Fallback")

    assert raw.title == "Edital 1 - Atual"
    assert raw.raw_agency == "CONIF"
    assert raw.raw_description.startswith("O CONIF torna público")
    assert raw.raw_cronograma == [{"evento": "data de publicação", "data": "2026-03-22"}]
    assert raw.pdf_content is None
    assert [item["link"] for item in raw.raw_anexos] == [
        "https://portal.conif.org.br/media/edital-1.pdf",
        "https://portal.conif.org.br/media/resultado.pdf",
    ]


def test_extract_detail_page_downloads_main_edital_pdf_when_available():
    detail_url = "https://portal.conif.org.br/editais/2026/edital-2"
    html_by_url = {
        detail_url: """
        <html>
          <body>
            <h1>Edital 2 - Inovacao</h1>
            <p>6 fevereiro 2026</p>
            <p>Texto de contexto do edital para a extração.</p>
            <ul>
              <li><a href="/images/Editais/2026/edital-2.pdf">Edital Conif/Contic nº 02, de 6 de fevereiro de 2026</a></li>
              <li><a href="/images/Editais/2026/anexo-i.pdf">Anexo I - Modelo de Proposta</a></li>
            </ul>
          </body>
        </html>
        """
    }
    page = FakePage(html_by_url)
    source = ConifSource(current_year=2026)
    source._download_file_bytes = lambda url: b"%PDF-1.4 fake"

    raw = source._extract_detail_page(page, detail_url, "Fallback")

    assert raw.url == detail_url
    assert raw.pdf_content == b"%PDF-1.4 fake"
    assert [item["link"] for item in raw.raw_anexos] == [
        "https://portal.conif.org.br/images/Editais/2026/edital-2.pdf",
        "https://portal.conif.org.br/images/Editais/2026/anexo-i.pdf",
    ]
    assert raw.raw_anexos[0]["titulo"].lower().startswith("edital")
