from src.components.sources.prppg_ifes_source import (
    PRPPG_IFES_EDITAIS_URL,
    PrppgIfesSource,
)


def _build_listing_page(rows_html: str, pager_links: str = "") -> str:
    return f"""
    <html>
      <body>
        <table id="Conteudo_gvwLista" class="gvwTable">
          <tr>
            <th>Edital</th>
          </tr>
          {rows_html}
          <tr class="gvwPager">
            <td><table><tr>{pager_links}</tr></table></td>
          </tr>
        </table>
        <input type="hidden" id="__VIEWSTATE" value="state" />
        <input type="hidden" id="__VIEWSTATEGENERATOR" value="generator" />
        <input type="hidden" id="__EVENTVALIDATION" value="validation" />
      </body>
    </html>
    """


def _build_listing_row(
    status: str,
    title: str,
    summary: str,
    detail_target: str,
    date_text: str,
) -> str:
    return f"""
    <tr>
      <td align="center">
        <table class="w-100" style="height:135px">
          <tr>
            <td style="width:100px; text-align:center">
              <span class="badge">{status}</span>
            </td>
            <td colspan="2" class="font-weight-bold">
              {title}
              <div class="float-right">
                <span class="badge badge-outline-dark">
                  {date_text}
                </span>
              </div>
            </td>
          </tr>
          <tr>
            <td colspan="2">{summary}</td>
            <td style="width:110px">
              <a href="javascript:__doPostBack('{detail_target}','')">Detalhes</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    """


def _build_detail_page(
    title: str,
    subtitle: str,
    info_text: str,
    attachment_rows: str,
    cronograma_rows: str,
) -> str:
    return f"""
    <html>
      <body>
        <div id="Conteudo_pnlDetalhesEdital">
          <h4>
            <a id="Conteudo_btnVoltar" href="javascript:__doPostBack('ctl00$Conteudo$btnVoltar','')">Voltar</a>
            <br />
            {title}
          </h4>
          <p class="card-subtitle text-muted mb-2">{subtitle}</p>
          <b>Informações gerais:</b><br />
          <p>{info_text}</p>
          <table class="gvwTable mb-2">
            <tr><th colspan="3">Anexos</th></tr>
            {attachment_rows}
          </table>
          <table class="gvwTable mb-2">
            <tr><th colspan="2">Cronograma</th></tr>
            {cronograma_rows}
          </table>
        </div>
        <input type="hidden" id="__VIEWSTATE" value="detail-state" />
        <input type="hidden" id="__VIEWSTATEGENERATOR" value="detail-generator" />
        <input type="hidden" id="__EVENTVALIDATION" value="detail-validation" />
      </body>
    </html>
    """


class FakeResponse:
    def __init__(
        self,
        *,
        text: str = "",
        url: str = PRPPG_IFES_EDITAIS_URL,
        content: bytes = b"",
        status_code: int = 200,
    ):
        self.text = text
        self.url = url
        self.content = content
        self.status_code = status_code
        self.headers = {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, first_page: str, post_responses: dict[tuple[str, str], FakeResponse]):
        self.first_page = first_page
        self.post_responses = post_responses
        self.posts = []

    def get(self, url, timeout=None):
        return FakeResponse(text=self.first_page, url=url)

    def post(self, url, data=None, timeout=None, allow_redirects=True):
        key = (data.get("__EVENTTARGET", ""), data.get("__EVENTARGUMENT", ""))
        self.posts.append(key)
        return self.post_responses[key]


def test_extract_listing_rows_maps_status_dates_and_postback_targets():
    html = _build_listing_page(
        _build_listing_row(
            "Aberto",
            "Reitoria 04/2026 - Propop-Ciência",
            "Resumo do edital.",
            "ctl00$Conteudo$gvwLista$ctl02$btnDetalhes",
            "30/03/2026 até 01/11/2026",
        )
    )
    source = PrppgIfesSource()

    rows = source._extract_listing_rows(html)

    assert rows == [
        {
            "status": "aberto",
            "title": "Reitoria 04/2026 - Propop-Ciência",
            "summary": "Resumo do edital.",
            "detail_event_target": "ctl00$Conteudo$gvwLista$ctl02$btnDetalhes",
            "listing_start_date": "2026-03-30",
            "listing_end_date": "2026-11-01",
        }
    ]


def test_select_main_attachment_prefers_edital_or_chamada_over_results():
    source = PrppgIfesSource()
    attachments = [
        {
            "titulo": "Resultado Final",
            "link": "https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=284#downloadTarget=result",
            "tipo": "pdf",
            "event_target": "target-result",
        },
        {
            "titulo": "Chamada Pública",
            "link": "https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=284#downloadTarget=main",
            "tipo": "pdf",
            "event_target": "target-main",
        },
    ]

    main = source._select_main_attachment(attachments)

    assert main["titulo"] == "Chamada Pública"
    assert main["event_target"] == "target-main"


def test_extract_detail_page_uses_cronograma_fallback_when_listing_date_is_missing():
    detail_html = _build_detail_page(
        "Edital 01/2026 - Finep",
        "CHAMADA PÚBLICA PRPPG/IFES Nº 01/2026",
        "Os interessados deverão preencher o formulário eletrônico.",
        """
        <tr>
          <td>pdf</td>
          <td><a href="javascript:__doPostBack('ctl00$Conteudo$Consulta_Arquivo$rptArquivo$ctl01$Download','')">Chamada Pública</a></td>
          <td>02/03/2026</td>
        </tr>
        <tr>
          <td>pdf</td>
          <td><a href="javascript:__doPostBack('ctl00$Conteudo$Consulta_Arquivo$rptArquivo$ctl02$Download','')">Etapa 3 - Resultado Final</a></td>
          <td>13/03/2026</td>
        </tr>
        """,
        """
        <tr>
          <td>Publicação da Chamada Interna PRPPG/Ifes</td>
          <td>24/02/2026</td>
        </tr>
        <tr>
          <td>Período de Manifestação de Interesse</td>
          <td>24/02/2026 a 02/03/2026 18:00</td>
        </tr>
        """,
    )
    source = PrppgIfesSource()
    source._download_attachment_bytes = lambda detail_url, detail_html, event_target: b"%PDF-1.4 fake"

    raw = source._extract_detail_page(
        detail_html=detail_html,
        detail_url="https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=284",
        listing_item={
            "status": "encerrado",
            "title": "Reitoria 01/2026 - Finep",
            "summary": "Resumo da chamada.",
            "detail_event_target": "ctl00$Conteudo$gvwLista$ctl05$btnDetalhes",
            "listing_start_date": "",
            "listing_end_date": "",
        },
    )

    assert raw.title == "Edital 01/2026 - Finep"
    assert raw.raw_agency == "PRPPG/IFES"
    assert raw.raw_status == "encerrado"
    assert raw.raw_description.startswith("CHAMADA PÚBLICA")
    assert raw.pdf_content == b"%PDF-1.4 fake"
    assert raw.raw_cronograma[:3] == [
        {"evento": "início do período do edital", "data": "2026-02-24"},
        {"evento": "fim do período do edital", "data": "2026-03-02"},
        {"evento": "Publicação da Chamada Interna PRPPG/Ifes", "data": "2026-02-24"},
    ]
    assert raw.raw_anexos == [
        {
            "titulo": "Chamada Pública",
            "link": "https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=284#downloadTarget=ctl00%24Conteudo%24Consulta_Arquivo%24rptArquivo%24ctl01%24Download",
            "tipo": "pdf",
        },
        {
            "titulo": "Etapa 3 - Resultado Final",
            "link": "https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=284#downloadTarget=ctl00%24Conteudo%24Consulta_Arquivo%24rptArquivo%24ctl02%24Download",
            "tipo": "pdf",
        },
    ]


def test_read_paginates_filters_current_year_and_skips_processed_urls():
    page_one_html = _build_listing_page(
        rows_html="".join(
            [
                _build_listing_row(
                    "Aberto",
                    "Reitoria 04/2026 - Propop-Ciência",
                    "Resumo 2026 com data na listagem.",
                    "ctl00$Conteudo$gvwLista$ctl02$btnDetalhes",
                    "30/03/2026 até 01/11/2026",
                ),
                _build_listing_row(
                    "Encerrado",
                    "Reitoria 01/2026 - Finep",
                    "Resumo 2026 sem data na listagem.",
                    "ctl00$Conteudo$gvwLista$ctl03$btnDetalhes",
                    "Não Informado",
                ),
            ]
        ),
        pager_links="<td><a href=\"javascript:__doPostBack('ctl00$Conteudo$gvwLista','Page$2')\">2</a></td>",
    )
    page_two_html = _build_listing_page(
        rows_html=_build_listing_row(
            "Encerrado",
            "Reitoria 20/2025 - Propós",
            "Resumo de 2025.",
            "ctl00$Conteudo$gvwLista$ctl02$btnDetalhes",
            "10/11/2025 até 30/11/2025",
        )
    )
    detail_2026_html = _build_detail_page(
        "Edital 04/2026 - Propop-Ciência",
        "EDITAL PRPPG 04/2026",
        "Fluxo contínuo para participação em feiras.",
        """
        <tr>
          <td>pdf</td>
          <td><a href="javascript:__doPostBack('ctl00$Conteudo$Consulta_Arquivo$rptArquivo$ctl01$Download','')">Edital PRPPG 04/2026</a></td>
          <td>30/03/2026</td>
        </tr>
        """,
        """
        <tr>
          <td>Inscrição no SIGPesq - fluxo contínuo</td>
          <td>30/03/2026 a 01/11/2026 23:59</td>
        </tr>
        """,
    )
    detail_finep_html = _build_detail_page(
        "Edital 01/2026 - Finep",
        "CHAMADA PÚBLICA PRPPG/IFES Nº 01/2026",
        "Manifestação de interesse para composição da proposta institucional.",
        """
        <tr>
          <td>pdf</td>
          <td><a href="javascript:__doPostBack('ctl00$Conteudo$Consulta_Arquivo$rptArquivo$ctl01$Download','')">Chamada Pública</a></td>
          <td>02/03/2026</td>
        </tr>
        """,
        """
        <tr>
          <td>Publicação da Chamada Interna PRPPG/Ifes</td>
          <td>24/02/2026</td>
        </tr>
        <tr>
          <td>Período de Manifestação de Interesse</td>
          <td>24/02/2026 a 02/03/2026 18:00</td>
        </tr>
        """,
    )
    fake_session = FakeSession(
        page_one_html,
        {
            ("ctl00$Conteudo$gvwLista", "Page$2"): FakeResponse(
                text=page_two_html,
                url=PRPPG_IFES_EDITAIS_URL,
            ),
            ("ctl00$Conteudo$gvwLista$ctl02$btnDetalhes", ""): FakeResponse(
                text=detail_2026_html,
                url="https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=290",
            ),
            ("ctl00$Conteudo$gvwLista$ctl03$btnDetalhes", ""): FakeResponse(
                text=detail_finep_html,
                url="https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=284",
            ),
            (
                "ctl00$Conteudo$Consulta_Arquivo$rptArquivo$ctl01$Download",
                "",
            ): FakeResponse(
                content=b"%PDF-1.4 fake",
                url="https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=290",
            ),
        },
    )
    source = PrppgIfesSource(
        session=fake_session,
        current_year=2026,
        processed_urls={"https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=290"},
    )

    raw_items = source.read()

    assert [item.url for item in raw_items] == [
        "https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=284"
    ]
    assert raw_items[0].title == "Edital 01/2026 - Finep"
    assert raw_items[0].pdf_content == b"%PDF-1.4 fake"
    assert ("ctl00$Conteudo$gvwLista", "Page$2") in fake_session.posts
