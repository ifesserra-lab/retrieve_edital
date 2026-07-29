"""
Testes do FinepSource após a migração para a API Liferay do portal.

Cobrem o que quebrou em produção e o que precisa continuar valendo:
filtro por prazo, deduplicação (inclusive das chaves do portal antigo),
mapeamento dos campos da API e resiliência a falha de rede.
"""

import pytest
import requests

from src.components.sources.finep_source import (
    DEADLINE_EVENT,
    PUBLICATION_EVENT,
    FinepCredentialResolver,
    FinepCredentials,
    FinepSource,
    _iso_date,
    _strip_html,
    _year_of,
)


def build_api_item(**overrides):
    """Item da API `/o/c/chamadapublicas`, no formato observado em produção."""
    item = {
        "id": 755376,
        "databaseId": 778,
        "titulo": "Finep Mais Inovação Brasil – Rodada 2 – Mobilidade Sustentável",
        "descricaoRawText": "Esta Seleção Pública tem por objetivo conceder subvenção econômica.",
        "descricao": "<p>Esta Seleção Pública tem por objetivo conceder subvenção econômica.</p>",
        "dataDePublicacao": "2026-03-06T00:00:00.000Z",
        "prazoProposto": "2026-08-31T17:00:00.000Z",
        "situacao": {"key": "aberta", "name": "Aberta"},
        "publicoAlvo": [
            {"key": "startup", "name": "Startup"},
            {"key": "cooperativa", "name": "Cooperativa"},
        ],
        "temaPrincipal": {"key": "180712", "name": "Mobilidade e Logística"},
        "taxonomyCategoryBriefs": [
            {"taxonomyCategoryId": 180706, "taxonomyCategoryName": "Meio Ambiente"}
        ],
        "tipoDeOportunidade": {"key": "naoReembolsavel", "name": "Não reembolsável"},
        "regiao": {"key": "todoBrasil", "name": "Todo Brasil"},
    }
    item.update(overrides)
    return item


def build_documento(**overrides):
    documento = {
        "legenda": "Regulamento",
        "documentoProprietario": {
            "link": {"href": "/documents/20117/206285/Regulamento.pdf/abc?download=true"}
        },
        "documentoAberto": {
            "link": {"href": "/documents/20117/206285/Regulamento.odt/def?download=true"}
        },
    }
    documento.update(overrides)
    return documento


class StubApiClient:
    """Cliente de API falso: devolve páginas e documentos pré-definidos."""

    def __init__(self, items=None, documentos=None, raise_on_list=None):
        self.items = items if items is not None else []
        self.documentos = documentos if documentos is not None else []
        self.raise_on_list = raise_on_list
        self.requested_paths = []

    def iter_items(self, path, params=None, page_size=100, max_pages=None):
        if self.raise_on_list is not None:
            raise self.raise_on_list
        self.requested_paths.append((path, params))
        return iter(self.items)

    def get_json(self, path, params=None):
        self.requested_paths.append((path, params))
        return {"items": self.documentos}


class TestDateHelpers:
    def test_iso_date_extracts_calendar_day_from_timestamp(self):
        assert _iso_date("2026-08-31T17:00:00.000Z") == "2026-08-31"
        assert _iso_date(None) == ""
        assert _iso_date("sem data") == ""

    def test_year_of(self):
        assert _year_of("2026-08-31") == 2026
        assert _year_of("") is None
        assert _year_of("31/08/2026") is None

    def test_strip_html_falls_back_when_raw_text_absent(self):
        assert _strip_html("<p>Objeto da  chamada</p>") == "Objeto da chamada"


class TestFinepCredentialResolver:
    def test_extracts_credentials_even_when_bundle_variables_are_renamed(self):
        bundle = (
            'const zz="clienteNovo",yy="segredoNovo",Q=async()=>{'
            "const p=btoa(`${zz}:${yy}`);}"
        )
        credentials = FinepCredentialResolver._extract_credentials(bundle)
        assert credentials == FinepCredentials("clienteNovo", "segredoNovo")

    def test_returns_none_when_pattern_is_absent(self):
        assert FinepCredentialResolver._extract_credentials("var x = 1;") is None
        assert FinepCredentialResolver._extract_credentials("") is None

    def test_falls_back_when_bundle_download_fails(self, monkeypatch):
        resolver = FinepCredentialResolver()

        def explode():
            raise requests.RequestException("sem rede")

        monkeypatch.setattr(resolver, "_download_bundle", explode)
        assert resolver.resolve() == resolver.fallback


class TestFinepSourceDeadlineFilter:
    def test_keeps_open_chamada_with_deadline_in_or_after_reference_year(self):
        source = FinepSource(
            reference_year=2026,
            api_client=StubApiClient(items=[build_api_item()]),
        )
        assert len(source.read()) == 1

    def test_keeps_open_chamada_with_distant_deadline(self):
        """A API já filtra por situação; prazo distante segue sendo oportunidade válida."""
        item = build_api_item(prazoProposto="2029-01-31T17:00:00.000Z")
        source = FinepSource(
            reference_year=2026, api_client=StubApiClient(items=[item])
        )
        assert len(source.read()) == 1

    def test_discards_chamada_with_deadline_before_reference_year(self):
        item = build_api_item(prazoProposto="2025-01-31T17:00:00.000Z")
        source = FinepSource(
            reference_year=2026, api_client=StubApiClient(items=[item])
        )
        assert source.read() == []

    def test_keeps_chamada_without_deadline(self):
        item = build_api_item(prazoProposto=None)
        source = FinepSource(
            reference_year=2026, api_client=StubApiClient(items=[item])
        )
        assert len(source.read()) == 1


class TestFinepSourceDeduplication:
    def test_skips_chamada_already_processed_by_new_url(self):
        source = FinepSource(
            reference_year=2026,
            api_client=StubApiClient(items=[build_api_item()]),
            processed_urls={
                "https://www.finep.gov.br/e/chamada-publica/222684/755376"
            },
        )
        assert source.read() == []

    def test_skips_chamada_registered_with_legacy_portal_url(self):
        """Os 10 editais coletados antes da migração usam a chave do portal antigo."""
        source = FinepSource(
            reference_year=2026,
            api_client=StubApiClient(items=[build_api_item()]),
            processed_urls={
                "http://www.finep.gov.br/chamadas-publicas/chamadapublica/778"
            },
        )
        assert source.read() == []


class TestFinepSourceMapping:
    @pytest.fixture
    def raw_edital(self):
        source = FinepSource(
            reference_year=2026,
            api_client=StubApiClient(
                items=[build_api_item()], documentos=[build_documento()]
            ),
        )
        return source.read()[0]

    def test_maps_identity_and_description(self, raw_edital):
        assert raw_edital.raw_agency == "FINEP"
        assert raw_edital.title.startswith("Finep Mais Inovação Brasil")
        assert raw_edital.raw_description.startswith("Esta Seleção Pública")
        assert raw_edital.raw_status == "aberta"

    def test_uses_public_detail_url_from_new_portal(self, raw_edital):
        assert raw_edital.url == (
            "https://www.finep.gov.br/e/chamada-publica/222684/755376"
        )

    def test_cronograma_labels_are_understood_by_the_normalizer(self, raw_edital):
        assert raw_edital.raw_cronograma == [
            {"evento": PUBLICATION_EVENT, "data": "2026-03-06"},
            {"evento": DEADLINE_EVENT, "data": "2026-08-31"},
        ]

    def test_tags_carry_native_api_metadata(self, raw_edital):
        assert "Mobilidade e Logística" in raw_edital.raw_tags
        assert "Startup" in raw_edital.raw_tags
        assert "Não reembolsável" in raw_edital.raw_tags

    def test_anexos_prefer_pdf_and_use_absolute_urls(self, raw_edital):
        assert raw_edital.raw_anexos == [
            {
                "titulo": "Regulamento",
                "link": "https://www.finep.gov.br/documents/20117/206285/Regulamento.pdf/abc?download=true",
                "tipo": "pdf",
            }
        ]

    def test_anexo_falls_back_to_open_format_when_pdf_missing(self):
        documento = build_documento(documentoProprietario=None)
        source = FinepSource(
            reference_year=2026,
            api_client=StubApiClient(
                items=[build_api_item()], documentos=[documento]
            ),
        )
        anexo = source.read()[0].raw_anexos[0]
        assert anexo["tipo"] == "formato aberto"
        assert anexo["link"].endswith("Regulamento.odt/def?download=true")


class TestFinepSourceResilience:
    def test_returns_empty_list_and_zeroes_counter_on_network_error(self):
        source = FinepSource(
            reference_year=2026,
            api_client=StubApiClient(
                raise_on_list=requests.RequestException("indisponível")
            ),
        )
        assert source.read() == []
        assert source.last_listing_count == 0

    def test_tracks_listing_count_before_deduplication(self):
        """O runner usa esse número para separar 'nada novo' de 'source quebrado'."""
        source = FinepSource(
            reference_year=2026,
            api_client=StubApiClient(items=[build_api_item()]),
            processed_urls={
                "https://www.finep.gov.br/e/chamada-publica/222684/755376"
            },
        )
        assert source.read() == []
        assert source.last_listing_count == 1

    def test_ignores_item_without_id_or_title(self):
        source = FinepSource(
            reference_year=2026,
            api_client=StubApiClient(items=[build_api_item(titulo="")]),
        )
        assert source.read() == []

    def test_missing_documents_endpoint_does_not_invalidate_edital(self):
        class FailingDocumentsClient(StubApiClient):
            def get_json(self, path, params=None):
                raise requests.RequestException("documentos indisponíveis")

        source = FinepSource(
            reference_year=2026,
            api_client=FailingDocumentsClient(items=[build_api_item()]),
        )
        raw_editais = source.read()
        assert len(raw_editais) == 1
        assert raw_editais[0].raw_anexos is None


class TestFinepApiPagination:
    def test_stops_when_total_count_is_reached(self):
        from src.components.sources.finep_source import FinepApiClient

        pages = [
            {"items": [{"id": 1}, {"id": 2}], "totalCount": 3},
            {"items": [{"id": 3}], "totalCount": 3},
        ]

        class PagedClient(FinepApiClient):
            def __init__(self):
                self.requested_pages = []

            def get_json(self, path, params=None):
                self.requested_pages.append(params["page"])
                return pages[params["page"] - 1]

        client = PagedClient()
        assert len(list(client.iter_items("/x", page_size=2))) == 3
        assert client.requested_pages == [1, 2]

    def test_hard_limit_prevents_endless_pagination(self):
        from src.components.sources.finep_source import (
            MAX_PAGES_HARD_LIMIT,
            FinepApiClient,
        )

        class EndlessClient(FinepApiClient):
            def __init__(self):
                self.calls = 0

            def get_json(self, path, params=None):
                self.calls += 1
                return {"items": [{"id": self.calls}]}  # nunca informa totalCount

        client = EndlessClient()
        collected = list(client.iter_items("/x"))
        assert len(collected) == MAX_PAGES_HARD_LIMIT
        assert client.calls == MAX_PAGES_HARD_LIMIT


class TestFinepSourceMalformedItems:
    def test_item_with_unexpected_shape_does_not_break_the_whole_read(self, caplog):
        """Um item fora do formato não pode custar a coleta das outras chamadas."""
        source = FinepSource(
            reference_year=2026,
            api_client=StubApiClient(items=["payload inesperado", build_api_item()]),
        )
        raw_editais = source.read()
        assert [r.url for r in raw_editais] == [
            "https://www.finep.gov.br/e/chamada-publica/222684/755376"
        ]
        assert "ignorada por erro de mapeamento" in caplog.text

    def test_tolerates_wrong_types_in_optional_metadata(self):
        """Campos de taxonomia com tipo inesperado viram tags vazias, não exceção."""
        item = build_api_item(publicoAlvo="não é lista", taxonomyCategoryBriefs="idem")
        source = FinepSource(
            reference_year=2026, api_client=StubApiClient(items=[item])
        )
        tags = source.read()[0].raw_tags
        assert "Mobilidade e Logística" in tags
        assert "Startup" not in tags
