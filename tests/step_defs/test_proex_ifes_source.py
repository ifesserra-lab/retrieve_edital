from src.components.sources.proex_ifes_source import (
    PROEX_IFES_EDITAIS_URL,
    ProexIfesSource,
)


CURRENT_YEAR_HTML = """
<html>
  <body>
    <div class="item-page">
      <h2>Editais abertos</h2>
      <h3>2026</h3>
      <p><strong>EDITAL Nº 05/2026 - Prêmio Assistec Inova</strong></p>
      <p><a href="/images/editais/2026/05/edital-05.pdf">Edital</a></p>
      <p><a href="/images/editais/2026/05/retificacao-05.pdf">Retificação do Edital</a></p>
      <p><a href="/images/editais/2026/05/anexo-i.docx">Anexo I</a></p>
      <hr />
      <p><strong>EDITAL Nº 04/2026 - Projetos Inovadores</strong></p>
      <p><a href="/images/editais/2026/04/edital-04.pdf">Edital</a></p>
      <p><a href="https://forms.gle/abc123">Inscreva-se</a></p>
      <h3>2025</h3>
      <p><strong>EDITAL Nº 38/2025 - Antigo</strong></p>
      <p><a href="/images/editais/2025/38/edital-38.pdf">Edital</a></p>
    </div>
  </body>
</html>
"""


class FakeResponse:
    def __init__(
        self,
        text: str = "",
        content: bytes = b"",
        status_code: int = 200,
        headers=None,
    ):
        self.text = text
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self):
        self.requests = []

    def get(self, url, timeout=None):
        self.requests.append(url)
        if url == PROEX_IFES_EDITAIS_URL:
            return FakeResponse(text=CURRENT_YEAR_HTML, headers={"content-type": "text/html"})
        return FakeResponse(
            content=b"%PDF-1.4 fake",
            headers={"content-type": "application/pdf"},
        )


def test_extract_current_year_entries_collects_only_current_year_blocks():
    source = ProexIfesSource(current_year=2026)

    entries = source._extract_current_year_entries(CURRENT_YEAR_HTML)

    assert entries == [
        {
            "title": "EDITAL Nº 05/2026 - Prêmio Assistec Inova",
            "attachments": [
                {
                    "titulo": "Edital",
                    "link": "https://proex.ifes.edu.br/images/editais/2026/05/edital-05.pdf",
                    "tipo": "pdf",
                },
                {
                    "titulo": "Retificação do Edital",
                    "link": "https://proex.ifes.edu.br/images/editais/2026/05/retificacao-05.pdf",
                    "tipo": "pdf",
                },
                {
                    "titulo": "Anexo I",
                    "link": "https://proex.ifes.edu.br/images/editais/2026/05/anexo-i.docx",
                    "tipo": "docx",
                },
            ],
        },
        {
            "title": "EDITAL Nº 04/2026 - Projetos Inovadores",
            "attachments": [
                {
                    "titulo": "Edital",
                    "link": "https://proex.ifes.edu.br/images/editais/2026/04/edital-04.pdf",
                    "tipo": "pdf",
                },
            ],
        },
    ]


def test_select_main_attachment_prefers_edital_over_results():
    source = ProexIfesSource()
    attachments = [
        {
            "titulo": "Resultado final do edital",
            "link": "https://proex.ifes.edu.br/images/editais/2026/05/resultado-final.pdf",
            "tipo": "pdf",
        },
        {
            "titulo": "Edital",
            "link": "https://proex.ifes.edu.br/images/editais/2026/05/edital-05.pdf",
            "tipo": "pdf",
        },
    ]

    main_attachment = source._select_main_attachment(attachments)

    assert main_attachment["link"].endswith("/edital-05.pdf")


def test_read_downloads_main_pdf_and_skips_processed_urls():
    fake_session = FakeSession()
    source = ProexIfesSource(
        current_year=2026,
        processed_urls={"https://proex.ifes.edu.br/images/editais/2026/04/edital-04.pdf"},
        session=fake_session,
    )

    items = source.read()

    assert [item.url for item in items] == [
        "https://proex.ifes.edu.br/images/editais/2026/05/edital-05.pdf"
    ]
    assert items[0].title == "EDITAL Nº 05/2026 - Prêmio Assistec Inova"
    assert items[0].raw_agency == "PROEX/IFES"
    assert items[0].pdf_content == b"%PDF-1.4 fake"
    assert items[0].raw_tags == ["proex", "ifes", "2026"]
