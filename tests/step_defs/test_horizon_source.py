"""
Testes do HorizonSource.

A `search-api` do SEDIA responde 500 a toda query testada, então a fonte é o
dataset bulk público do Funding & Tenders Portal: 11.141 registros de todos os
programas, dos quais interessam os HORIZON abertos nas divisões configuradas.
"""

import json

import pytest
import requests

from src.components.sources.horizon_source import (
    DEFAULT_DIVISIONS,
    SUGGESTED_DIVISIONS,
    HORIZON_BULK_URL,
    HorizonSource,
    _epoch_millis_to_iso,
    get_configured_divisions,
    iter_json_objects,
)

# Valores reais do dataset: 2026-12-17 e 2025-11-06 em epoch de milissegundos.
DEADLINE_MILLIS = 1797465600000
OPENING_MILLIS = 1762387200000


def build_item(**overrides):
    """Registro do dataset, no formato observado em produção."""
    item = {
        "identifier": "HORIZON-EIC-2026-ACCELERATOR-01",
        "title": "EIC Accelerator 2026 - Short proposal",
        "callTitle": "EIC Accelerator 2026 - Short application",
        "status": {"id": 31094502, "abbreviation": "Open", "description": "Open"},
        "frameworkProgramme": {"abbreviation": "HORIZON"},
        "programmeDivision": [
            {"abbreviation": "HORIZON.3.1.2", "description": "The Accelerator"},
            {
                "abbreviation": "HORIZON.3.1",
                "description": "The European Innovation Council (EIC)",
            },
        ],
        "deadlineDatesLong": [DEADLINE_MILLIS],
        "plannedOpeningDateLong": OPENING_MILLIS,
        "keywords": [],
        "links": [
            {
                "criterionDescription": "HORIZON EIC Accelerator",
                "url": "https://ec.europa.eu/research/participants/submission",
            }
        ],
    }
    item.update(overrides)
    return item


def build_payload(items):
    return json.dumps({"fundingData": {"GrantTenderObj": items}})


class FakeResponse:
    def __init__(self, text, url=HORIZON_BULK_URL):
        self.text = text
        self.url = url

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self, payload="", raise_error=None):
        self.payload = payload
        self.raise_error = raise_error
        self.requests_made = 0

    def get(self, url, timeout=None, headers=None, stream=False):
        self.requests_made += 1
        if self.raise_error is not None:
            raise self.raise_error
        self.headers_sent = headers or {}
        return FakeResponse(self.payload)


def build_source(items=None, **kwargs):
    payload = build_payload(items if items is not None else [build_item()])
    kwargs.setdefault("divisions", ["HORIZON.3.1"])
    session = FakeSession(payload=payload)
    return HorizonSource(session=session, **kwargs), session


class TestHelpers:
    def test_epoch_millis_to_iso(self):
        assert _epoch_millis_to_iso(DEADLINE_MILLIS) == "2026-12-17"
        assert _epoch_millis_to_iso(None) == ""
        assert _epoch_millis_to_iso("não é número") == ""

    def test_iter_json_objects_yields_one_at_a_time(self):
        """Evita materializar os 11 mil registros do dataset de 126 MB."""
        payload = build_payload([build_item(identifier=f"ID-{i}") for i in range(5)])
        identifiers = [obj["identifier"] for obj in iter_json_objects(payload)]
        assert identifiers == [f"ID-{i}" for i in range(5)]

    def test_iter_json_objects_handles_empty_list(self):
        assert list(iter_json_objects(build_payload([]))) == []

    def test_iter_json_objects_without_the_expected_key(self):
        assert list(iter_json_objects('{"outraCoisa": []}')) == []

    def test_iter_json_objects_stops_on_malformed_payload(self):
        truncated = build_payload([build_item()])[:-40]
        assert isinstance(list(iter_json_objects(truncated)), list)


class TestDivisionConfiguration:
    def test_argument_wins_over_environment(self, monkeypatch):
        monkeypatch.setenv("HORIZON_DIVISIONS", "HORIZON.9")
        assert get_configured_divisions(["HORIZON.2.4"]) == ("HORIZON.2.4",)

    def test_environment_wins_over_default(self, monkeypatch):
        monkeypatch.setenv("HORIZON_DIVISIONS", "HORIZON.2.4, HORIZON.3.1")
        assert get_configured_divisions() == ("HORIZON.2.4", "HORIZON.3.1")

    def test_default_is_empty_so_nothing_is_published_without_a_decision(self, monkeypatch):
        """
        As divisões sugeridas rendem 185 chamadas publicáveis — mais que o portal
        inteiro. Habilitar isso é decisão da PRPPG, não default do código.
        """
        monkeypatch.delenv("HORIZON_DIVISIONS", raising=False)
        assert get_configured_divisions() == ()
        assert DEFAULT_DIVISIONS == ()
        assert "HORIZON.3.1" in SUGGESTED_DIVISIONS

    def test_empty_configuration_publishes_nothing(self):
        """
        Sem triagem temática, as ~200 chamadas abertas afogariam o portal.
        Devolver nada é o comportamento seguro.
        """
        source, session = build_source(divisions=[])
        assert source.read() == []
        assert session.requests_made == 0, "não deve nem baixar o dataset"


class TestRelevanceFilter:
    def test_keeps_open_horizon_call_in_a_configured_division(self):
        source, _ = build_source()
        assert len(source.read()) == 1

    def test_keeps_forthcoming_calls(self):
        item = build_item(status={"abbreviation": "Forthcoming"})
        source, _ = build_source([item])
        assert len(source.read()) == 1

    def test_discards_closed_calls(self):
        item = build_item(status={"abbreviation": "Closed"})
        source, _ = build_source([item])
        assert source.read() == []

    def test_discards_other_framework_programmes(self):
        item = build_item(frameworkProgramme={"abbreviation": "H2020"})
        source, _ = build_source([item])
        assert source.read() == []

    def test_discards_divisions_outside_the_configuration(self):
        item = build_item(
            programmeDivision=[{"abbreviation": "HORIZON.2.1", "description": "Health"}]
        )
        source, _ = build_source([item], divisions=["HORIZON.2.4"])
        assert source.read() == []

    def test_configured_prefix_covers_subdivisions(self):
        """`HORIZON.2.4` deve cobrir `HORIZON.2.4.1`."""
        item = build_item(
            programmeDivision=[
                {"abbreviation": "HORIZON.2.4.1", "description": "Manufacturing"}
            ]
        )
        source, _ = build_source([item], divisions=["HORIZON.2.4"])
        assert len(source.read()) == 1


class TestMapping:
    @pytest.fixture
    def raw_edital(self):
        source, _ = build_source()
        return source.read()[0]

    def test_identity_and_public_url(self, raw_edital):
        assert raw_edital.raw_agency == "Horizon Europe"
        assert raw_edital.title == "EIC Accelerator 2026 - Short proposal"
        assert "HORIZON-EIC-2026-ACCELERATOR-01" in raw_edital.url
        assert raw_edital.url.startswith("https://ec.europa.eu/info/funding-tenders")

    def test_dates_come_from_epoch_millis(self, raw_edital):
        assert raw_edital.raw_cronograma == [
            {"evento": "Abertura das inscrições", "data": "2025-11-06"},
            {"evento": "Prazo para envio de propostas", "data": "2026-12-17"},
        ]

    def test_multiple_deadlines_become_phases(self):
        item = build_item(
            deadlineDatesLong=[DEADLINE_MILLIS, OPENING_MILLIS],
        )
        source, _ = build_source([item])
        eventos = [c["evento"] for c in source.read()[0].raw_cronograma]
        assert "Prazo da fase 1" in eventos
        assert eventos[-1] == "Prazo para envio de propostas"

    def test_description_is_composed_from_metadata(self, raw_edital):
        """O dataset bulk não traz texto descritivo."""
        assert "European Innovation Council" in raw_edital.raw_description
        assert "HORIZON-EIC-2026-ACCELERATOR-01" in raw_edital.raw_description

    def test_eic_calls_are_tagged(self, raw_edital):
        assert "eic" in raw_edital.raw_tags
        assert "internacional" in raw_edital.raw_tags

    def test_non_eic_division_is_not_tagged_as_eic(self):
        item = build_item(
            programmeDivision=[
                {"abbreviation": "HORIZON.2.4", "description": "Digital and Space"}
            ]
        )
        source, _ = build_source([item], divisions=["HORIZON.2.4"])
        assert "eic" not in source.read()[0].raw_tags

    def test_links_become_anexos(self, raw_edital):
        assert raw_edital.raw_anexos == [
            {
                "titulo": "HORIZON EIC Accelerator",
                "link": "https://ec.europa.eu/research/participants/submission",
                "tipo": "link",
            }
        ]


class TestDeduplication:
    def test_skips_calls_already_processed_by_url(self):
        source, _ = build_source(
            processed_urls={
                "https://ec.europa.eu/info/funding-tenders/opportunities/portal"
                "/screen/opportunities/topic-details/HORIZON-EIC-2026-ACCELERATOR-01"
            }
        )
        assert source.read() == []

    def test_skips_calls_already_processed_by_identifier(self):
        source, _ = build_source(
            processed_urls={"HORIZON-EIC-2026-ACCELERATOR-01"}
        )
        assert source.read() == []

    def test_tracks_relevant_count_before_deduplication(self):
        source, _ = build_source(
            processed_urls={"HORIZON-EIC-2026-ACCELERATOR-01"}
        )
        assert source.read() == []
        assert source.last_listing_count == 1


class TestResilience:
    def test_network_failure_returns_empty_and_zeroes_counter(self):
        source = HorizonSource(
            divisions=["HORIZON.3.1"],
            session=FakeSession(raise_error=requests.RequestException("timeout")),
        )
        assert source.read() == []
        assert source.last_listing_count == 0

    def test_requests_gzip_to_avoid_downloading_126_mb(self):
        source, session = build_source()
        source.read()
        assert "gzip" in session.headers_sent.get("Accept-Encoding", "")

    def test_item_without_identifier_is_ignored(self):
        source, _ = build_source([build_item(identifier="")])
        assert source.read() == []


class TestCategory:
    def test_eic_calls_are_innovation(self):
        """Sem isso, tudo caía em `outros`: o dataset não traz texto descritivo."""
        source, _ = build_source()
        assert source.read()[0].source_category == "inovação"

    def test_other_divisions_are_research(self):
        item = build_item(
            programmeDivision=[
                {"abbreviation": "HORIZON.2.5", "description": "Climate and Energy"}
            ]
        )
        source, _ = build_source([item], divisions=["HORIZON.2.5"])
        assert source.read()[0].source_category == "pesquisa"

    def test_category_stays_within_the_existing_vocabulary(self):
        source, _ = build_source()
        assert source.read()[0].source_category in {"inovação", "pesquisa"}


class TestWholeProgrammeShortcut:
    def test_the_horizon_prefix_indexes_every_division(self):
        """
        A comparação é por prefixo, então `HORIZON` cobre todo o programa — não é
        preciso listar as 13 subdivisões.
        """
        items = [
            build_item(
                identifier="A",
                programmeDivision=[{"abbreviation": "HORIZON.1.1", "description": "ERC"}],
            ),
            build_item(
                identifier="B",
                programmeDivision=[{"abbreviation": "HORIZON.2.6", "description": "Food"}],
            ),
            build_item(
                identifier="C",
                programmeDivision=[{"abbreviation": "HORIZON.4.1", "description": "Widening"}],
            ),
        ]
        source, _ = build_source(items, divisions=["HORIZON"])
        assert len(source.read()) == 3

    def test_session_has_transport_level_retry(self):
        """Um `Connection reset by peer` não pode custar a execução semanal."""
        session = HorizonSource._build_session()
        adapter = session.get_adapter("https://ec.europa.eu")
        assert adapter.max_retries.total >= 3
        assert 429 in adapter.max_retries.status_forcelist


class TestWindowedDownload:
    """
    Medições de 2026-07-30 contra o servidor da UE:

    - transferência única dos 126 MB: `Connection reset by peer` no meio;
    - `Range: bytes=N-` (aberto), como o `curl -C -` envia: responde `206`, mas a
      transferência estola e é cortada;
    - `Range: bytes=N-M` (limitado a 8 MB): `206` com os bytes exatos, rápido.

    Daí o download em janelas com fim explícito.
    """

    def build_window_session(self, payload: str, failures_per_window=None,
                             honour_range=True):
        raw = payload.encode("utf-8")
        remaining = dict(failures_per_window or {})

        class WindowResponse:
            def __init__(self, content, status_code, headers):
                self.content = content
                self.status_code = status_code
                self.headers = headers
                self.url = HORIZON_BULK_URL

            def raise_for_status(self):
                return None

        class WindowSession:
            def __init__(self):
                self.ranges = []
                self.compressed_attempts = 0

            def get(self, url, timeout=None, headers=None, stream=False):
                headers = headers or {}
                range_header = headers.get("Range")
                if range_header is None:
                    # Caminho comprimido: indisponível neste cenário.
                    self.compressed_attempts += 1
                    raise requests.RequestException("compressed path unavailable")

                self.ranges.append(range_header)
                start = int(range_header.split("=")[1].split("-")[0])
                if remaining.get(start, 0) > 0:
                    remaining[start] -= 1
                    raise requests.RequestException("connection reset")

                if not honour_range:
                    return WindowResponse(raw, 200, {})
                end = int(range_header.split("-")[1])
                body = raw[start : end + 1]
                return WindowResponse(
                    body,
                    206,
                    {"Content-Range": f"bytes {start}-{start + len(body) - 1}/{len(raw)}"},
                )

        return WindowSession()

    def test_assembles_the_payload_from_successive_windows(self, monkeypatch):
        monkeypatch.setattr(
            "src.components.sources.horizon_source.DOWNLOAD_WINDOW_SIZE", 4096
        )
        payload = build_payload([build_item(identifier=f"ID-{i}") for i in range(40)])
        session = self.build_window_session(payload)
        source = HorizonSource(divisions=["HORIZON.3.1"], session=session)

        assert len(source.read()) == 40
        assert len(session.ranges) > 1, "payload maior que a janela exige várias idas"

    def test_every_range_request_is_bounded(self, monkeypatch):
        """`Range` aberto é justamente o que o servidor não entrega."""
        monkeypatch.setattr(
            "src.components.sources.horizon_source.DOWNLOAD_WINDOW_SIZE", 4096
        )
        payload = build_payload([build_item(identifier=f"ID-{i}") for i in range(30)])
        session = self.build_window_session(payload)
        HorizonSource(divisions=["HORIZON.3.1"], session=session).read()

        for range_header in session.ranges:
            start, _, end = range_header.partition("=")[2].partition("-")
            assert start.isdigit() and end.isdigit(), f"Range sem fim: {range_header}"

    def test_a_failing_window_is_retried_without_losing_the_rest(self, monkeypatch):
        monkeypatch.setattr(
            "src.components.sources.horizon_source.DOWNLOAD_WINDOW_SIZE", 4096
        )
        payload = build_payload([build_item(identifier=f"ID-{i}") for i in range(40)])
        session = self.build_window_session(payload, failures_per_window={4096: 2})
        source = HorizonSource(divisions=["HORIZON.3.1"], session=session)

        assert len(source.read()) == 40
        assert session.ranges.count("bytes=4096-8191") == 3, "duas falhas e um acerto"

    def test_falls_back_to_windows_when_the_compressed_path_fails(self):
        payload = build_payload([build_item()])
        session = self.build_window_session(payload)
        source = HorizonSource(divisions=["HORIZON.3.1"], session=session)
        assert len(source.read()) == 1
        assert session.compressed_attempts == 1

    def test_server_ignoring_range_returns_the_whole_body_once(self):
        payload = build_payload([build_item()])
        session = self.build_window_session(payload, honour_range=False)
        source = HorizonSource(divisions=["HORIZON.3.1"], session=session)
        assert len(source.read()) == 1
        assert len(session.ranges) == 1

    def test_gives_up_after_the_retry_budget(self):
        from src.components.sources.horizon_source import DOWNLOAD_MAX_RETRIES

        payload = build_payload([build_item()])
        session = self.build_window_session(
            payload, failures_per_window={0: DOWNLOAD_MAX_RETRIES + 5}
        )
        source = HorizonSource(divisions=["HORIZON.3.1"], session=session)
        assert source.read() == []
        assert source.last_listing_count == 0
