from bs4 import BeautifulSoup

from src.components.sources.cnpq_source import CnpqSource, _parse_inscricao_range


def test_parse_inscricao_range():
    assert _parse_inscricao_range("25/02/2026  a  13/04/2026") == (
        "2026-02-25",
        "2026-04-13",
    )
    assert _parse_inscricao_range("sem datas") == ("", "")


def test_extract_raw_edital_from_card_maps_description_dates_and_anexos():
    html = """
    <li>
      <div class="content">
        <h4>Chamada CNPq Nº 5/2026</h4>
        <p>Fomentar projetos de empreendedorismo inovador nas ICTs.</p>
        <ul>
          <li>Documento principal: <a href="http://resultado.cnpq.br/111">link</a></li>
          <li>Anexo complementar: <a href="http://resultado.cnpq.br/222">link</a></li>
        </ul>
        <div class="inscricao">
          <ul class="datas">
            <li>25/02/2026  a  13/04/2026</li>
          </ul>
        </div>
      </div>
      <input type="text" value="http://memoria2.cnpq.br/web/guest/chamadas-publicas?idDivulgacao=13405">
    </li>
    """

    source = CnpqSource()
    source._download_file_bytes = lambda url: b"%PDF-1.4 fake"
    card = BeautifulSoup(html, "html.parser").find("li")

    raw = source._extract_raw_edital_from_card(card)

    assert raw.title == "Chamada CNPq Nº 5/2026"
    assert raw.url.endswith("idDivulgacao=13405")
    assert raw.raw_agency == "CNPq"
    assert raw.raw_description.startswith("Fomentar projetos")
    assert raw.pdf_content == b"%PDF-1.4 fake"
    assert raw.raw_cronograma == [
        {"evento": "abertura das inscrições", "data": "2026-02-25"},
        {"evento": "encerramento das inscrições", "data": "2026-04-13"},
    ]
    assert [item["link"] for item in raw.raw_anexos] == [
        "http://resultado.cnpq.br/111",
        "http://resultado.cnpq.br/222",
    ]


def test_extract_raw_edital_from_card_tries_next_attachment_when_first_is_not_pdf():
    html = """
    <li>
      <div class="content">
        <h4>Chamada CNPq Nº 7/2026</h4>
        <p>Descricao da chamada.</p>
        <ul>
          <li>Documento Word: <a href="http://resultado.cnpq.br/word">link</a></li>
          <li>Documento PDF: <a href="http://resultado.cnpq.br/pdf">link</a></li>
        </ul>
      </div>
      <input type="text" value="http://memoria2.cnpq.br/web/guest/chamadas-publicas?idDivulgacao=7">
    </li>
    """

    source = CnpqSource()
    attempts = []

    def fake_download(url):
        attempts.append(url)
        return None if url.endswith("/word") else b"%PDF-1.4 fake"

    source._download_file_bytes = fake_download
    card = BeautifulSoup(html, "html.parser").find("li")

    raw = source._extract_raw_edital_from_card(card)

    assert raw.pdf_content == b"%PDF-1.4 fake"
    assert attempts == [
        "http://resultado.cnpq.br/word",
        "http://resultado.cnpq.br/pdf",
    ]


def test_extract_listing_entries_skips_processed_urls():
    html = """
    <html>
      <body>
        <ul>
          <li>
            <div class="content">
              <h4>Chamada CNPq Nº 1/2026</h4>
              <p>Descricao 1</p>
            </div>
            <input type="text" value="http://memoria2.cnpq.br/web/guest/chamadas-publicas?idDivulgacao=1">
          </li>
          <li>
            <div class="content">
              <h4>Chamada CNPq Nº 2/2026</h4>
              <p>Descricao 2</p>
            </div>
            <input type="text" value="http://memoria2.cnpq.br/web/guest/chamadas-publicas?idDivulgacao=2">
          </li>
        </ul>
      </body>
    </html>
    """

    source = CnpqSource(
        processed_urls={"http://memoria2.cnpq.br/web/guest/chamadas-publicas?idDivulgacao=2"}
    )

    result = source._extract_listing_entries(html)

    assert len(result) == 1
    assert result[0].title == "Chamada CNPq Nº 1/2026"
