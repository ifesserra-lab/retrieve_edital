from src.components.sources.capes_source import CapesSource


def test_extract_listing_entries_uses_editais_abertos_and_skips_processed_urls():
    html = """
    <html>
      <body>
        <h2>Editais Abertos</h2>
        <div>
          <ul>
            <li><a href="/capes/pt-br/assuntos/edital-a">Edital A</a></li>
            <li><a href="/capes/pt-br/assuntos/edital-b">Edital B</a></li>
            <li><a href="https://www.gov.br/capes/pt-br/assuntos/edital-a">Edital A duplicado</a></li>
            <li><a href="/media/documento.pdf">PDF solto</a></li>
          </ul>
        </div>
      </body>
    </html>
    """

    source = CapesSource(
        processed_urls={"https://www.gov.br/capes/pt-br/assuntos/edital-b"}
    )

    result = source._extract_listing_entries(html)

    assert result == [
        {
            "title": "Edital A",
            "url": "https://www.gov.br/capes/pt-br/assuntos/edital-a",
        }
    ]


def test_extract_listing_entries_filters_previous_year_items():
    html = """
    <html>
      <body>
        <h2>Editais Abertos</h2>
        <div>
          <ul>
            <li><a href="/capes/pt-br/assuntos/edital-2025">Edital CAPES 2025</a></li>
            <li><a href="/capes/pt-br/assuntos/edital-2026">Edital CAPES 2026</a></li>
            <li><a href="/capes/pt-br/assuntos/edital-2027">Edital CAPES 2027</a></li>
          </ul>
        </div>
      </body>
    </html>
    """

    source = CapesSource(current_year=2026)

    result = source._extract_listing_entries(html)

    assert result == [
        {
            "title": "Edital CAPES 2026",
            "url": "https://www.gov.br/capes/pt-br/assuntos/edital-2026",
        },
        {
            "title": "Edital CAPES 2027",
            "url": "https://www.gov.br/capes/pt-br/assuntos/edital-2027",
        },
    ]


def test_extract_pdf_links_and_select_main_pdf_url_prioritize_edital_document():
    html = """
    <html>
      <body>
        <a href="https://www.gov.br/capes/pt-br/centrais-de-conteudo/documentos/manual.pdf">Manual do programa</a>
        <a href="https://www.gov.br/capes/pt-br/centrais-de-conteudo/editais/edital-principal.pdf">Edital CAPES 2026</a>
        <script>
          var resultado = "https://www.gov.br/capes/pt-br/centrais-de-conteudo/resultados-dos-editais/resultado.pdf";
        </script>
      </body>
    </html>
    """

    source = CapesSource()
    anexos = source._extract_pdf_links(html)

    assert [item["link"] for item in anexos] == [
        "https://www.gov.br/capes/pt-br/centrais-de-conteudo/documentos/manual.pdf",
        "https://www.gov.br/capes/pt-br/centrais-de-conteudo/editais/edital-principal.pdf",
        "https://www.gov.br/capes/pt-br/centrais-de-conteudo/resultados-dos-editais/resultado.pdf",
    ]
    assert (
        source._select_main_pdf_url(anexos)
        == "https://www.gov.br/capes/pt-br/centrais-de-conteudo/editais/edital-principal.pdf"
    )


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


def test_extract_detail_page_collects_description_anexos_and_main_pdf():
    detail_url = "https://www.gov.br/capes/pt-br/assuntos/edital-a"
    html_by_url = {
        detail_url: """
        <html>
          <body>
            <h1>Edital CAPES 2026</h1>
            <p>Este edital promove a cooperação acadêmica internacional com apoio financeiro.</p>
            <a href="https://www.gov.br/capes/pt-br/centrais-de-conteudo/editais/edital-a.pdf">Edital CAPES 2026</a>
            <a href="https://www.gov.br/capes/pt-br/centrais-de-conteudo/resultados-dos-editais/resultado-a.pdf">Resultado preliminar</a>
          </body>
        </html>
        """
    }

    source = CapesSource()
    source._download_file_bytes = lambda url: b"%PDF-1.4 fake"
    raw = source._extract_detail_page(FakePage(html_by_url), detail_url, "Fallback")

    assert raw.title == "Edital CAPES 2026"
    assert raw.raw_agency == "CAPES"
    assert raw.raw_description.startswith("Este edital promove")
    assert raw.pdf_content == b"%PDF-1.4 fake"
    assert [item["link"] for item in raw.raw_anexos] == [
        "https://www.gov.br/capes/pt-br/centrais-de-conteudo/editais/edital-a.pdf",
        "https://www.gov.br/capes/pt-br/centrais-de-conteudo/resultados-dos-editais/resultado-a.pdf",
    ]


def test_extract_detail_page_discards_item_when_main_pdf_year_is_previous():
    detail_url = "https://www.gov.br/capes/pt-br/assuntos/edital-2025"
    html_by_url = {
        detail_url: """
        <html>
          <body>
            <h1>Edital CAPES 2025</h1>
            <p>Texto descritivo do edital.</p>
            <a href="https://www.gov.br/capes/pt-br/centrais-de-conteudo/editais/edital-2025.pdf">Edital CAPES 2025</a>
          </body>
        </html>
        """
    }

    source = CapesSource(current_year=2026)
    source._download_file_bytes = lambda url: b"%PDF-1.4 fake"
    source._infer_year_from_text = lambda text: 2025

    raw = source._extract_detail_page(FakePage(html_by_url), detail_url, "Fallback")

    assert raw is None
