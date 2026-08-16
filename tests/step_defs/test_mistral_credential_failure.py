"""
Testes da falha dura por credencial/assinatura recusada pela Mistral.

Motivação: entre 2026-08-10 e 2026-08-16 a API respondeu `402 Check your
subscription` a toda chamada. Cada PDF gastava três tentativas e ~45s, virava
`None`, o normalizador caía na extração básica e o fluxo terminava com
`Sucesso` e delta 0 — o job do GitHub Actions ficou verde por sete dias
seguidos com a extração inteiramente morta.

A regra que estes testes fixam: 401/402/403 não é caso de retry nem de
fallback. Sobe como `MistralUnavailableError` até derrubar o fluxo, para que o
job fique vermelho. Erro transitório (429, 5xx, PDF ruim) mantém a resiliência
por item que já existia.
"""

import pytest

from src.components.transforms import mistral_client
from src.components.transforms.edital_normalizer import EditalNormalizer
from src.components.transforms.mistral_client import (
    MistralUnavailableError,
    _call_with_rate_limit_retry,
    _is_credential_error,
)
from src.domain.models import RawEdital

BODY_402 = (
    'API error occurred: Status 402. Body: '
    '{"detail":"Check your subscription on https://admin.mistral.ai/subscription"}'
)


@pytest.fixture
def esperas(monkeypatch):
    """Captura as esperas sem realmente dormir."""
    registradas = []
    monkeypatch.setattr(mistral_client.time, "sleep", registradas.append)
    return registradas


class TestCredentialErrorDetection:
    @pytest.mark.parametrize(
        "mensagem",
        [
            BODY_402,
            "API error occurred: Status 401",
            "API error occurred: Status 403",
            "Unauthorized",
        ],
    )
    def test_reconhece_recusa_de_credencial(self, mensagem):
        assert _is_credential_error(RuntimeError(mensagem)) is True

    @pytest.mark.parametrize(
        "mensagem",
        [
            "Status 429 rate_limited",
            "API error occurred: Status 502 Content-Type text/html",
            "peer closed connection without sending complete message body",
        ],
    )
    def test_erro_transitorio_nao_e_recusa_de_credencial(self, mensagem):
        assert _is_credential_error(RuntimeError(mensagem)) is False


class TestFailFast:
    def test_402_sobe_como_mistral_unavailable_sem_esperar(self, esperas):
        def recusa_402():
            raise RuntimeError(BODY_402)

        with pytest.raises(MistralUnavailableError, match="402"):
            _call_with_rate_limit_retry(recusa_402, context="upload x.pdf")

        # Nenhum backoff: crédito não volta durante a espera.
        assert esperas == []

    def test_402_tenta_uma_unica_vez(self, esperas):
        chamadas = {"n": 0}

        def recusa_402():
            chamadas["n"] += 1
            raise RuntimeError(BODY_402)

        with pytest.raises(MistralUnavailableError):
            _call_with_rate_limit_retry(recusa_402)

        assert chamadas["n"] == 1

    def test_429_continua_com_backoff(self, esperas):
        """A resiliência a rate limit não pode ter sido perdida na mudança."""
        tentativas = {"n": 0}

        def falha_uma_vez():
            tentativas["n"] += 1
            if tentativas["n"] == 1:
                raise RuntimeError("Status 429")
            return "ok"

        assert _call_with_rate_limit_retry(falha_uma_vez) == "ok"
        assert esperas == [60]


class _ServicoRecusado:
    """Dublê que reproduz a conta sem crédito em toda chamada."""

    def extract_from_pdf(self, pdf_bytes, filename):
        raise MistralUnavailableError(BODY_402)

    def categorize_finep_by_description(self, description):
        raise MistralUnavailableError(BODY_402)

    def classify_document_titles(self, titles):
        raise MistralUnavailableError(BODY_402)


class _ServicoInstavel:
    """Dublê de falha transitória: um PDF ruim, não a conta inteira."""

    def extract_from_pdf(self, pdf_bytes, filename):
        raise RuntimeError("Status 502 Content-Type text/html")

    def categorize_finep_by_description(self, description):
        raise RuntimeError("Status 502")


class TestNormalizerPropagation:
    def test_conta_recusada_derruba_o_normalizador(self):
        """
        Sem isto o normalizador caía na extração básica e gravava um edital sem
        o conteúdo do PDF, indistinguível de um edital legitimamente magro.
        """
        normalizer = EditalNormalizer(extraction_service=_ServicoRecusado())
        raw = RawEdital(
            title="EDITAL FAPES Nº 03/2026",
            url="https://exemplo.test/edital-3",
            raw_agency="FAPES",
            pdf_content=b"%PDF-1.4 conteudo",
            document_type="edital",
        )

        with pytest.raises(MistralUnavailableError):
            normalizer.process(raw)

    def test_conta_recusada_derruba_tambem_na_categorizacao_finep(self):
        normalizer = EditalNormalizer(extraction_service=_ServicoRecusado())
        raw = RawEdital(
            title="CHAMADA PÚBLICA FINEP 01/2026",
            url="https://exemplo.test/finep-1",
            raw_agency="FINEP",
            raw_description="Apoio a projetos de inovação em empresas.",
        )

        with pytest.raises(MistralUnavailableError):
            normalizer.process(raw)

    def test_falha_transitoria_mantem_o_fallback(self):
        """Um PDF que falha não pode derrubar o fluxo — resiliência preservada."""
        normalizer = EditalNormalizer(extraction_service=_ServicoInstavel())
        raw = RawEdital(
            title="EDITAL FAPES Nº 09/2026",
            url="https://exemplo.test/edital-9",
            raw_agency="FAPES",
            pdf_content=b"%PDF-1.4 conteudo",
            document_type="edital",
        )

        # Não levanta: cai na extração básica, como antes.
        normalizer.process(raw)


class TestSourcePropagation:
    """
    O FapesSource chama o classificador dentro da própria raspagem, sob um
    `except Exception` que existe para não derrubar o pipeline quando o portal
    falha. Esse mesmo `except` engolia o 402: a leitura devolvia lista vazia e
    o fluxo encerrava em `raw=0` — reportado como origem sem novidade, exit 0.
    """

    def test_fapes_source_nao_engole_a_recusa_de_credencial(self, monkeypatch):
        from src.components.sources import fapes_source

        def explode(*args, **kwargs):
            raise MistralUnavailableError(BODY_402)

        monkeypatch.setattr(fapes_source, "sync_playwright", explode)
        source = fapes_source.FapesSource(classifier=_ServicoRecusado())

        with pytest.raises(MistralUnavailableError):
            source.read()

    def test_fapes_source_ainda_absorve_falha_de_raspagem(self, monkeypatch):
        """Portal fora do ar continua devolvendo lista vazia, sem derrubar nada."""
        from src.components.sources import fapes_source

        def explode(*args, **kwargs):
            raise RuntimeError("Playwright: net::ERR_CONNECTION_REFUSED")

        monkeypatch.setattr(fapes_source, "sync_playwright", explode)
        source = fapes_source.FapesSource(classifier=_ServicoRecusado())

        assert source.read() == []


class TestFlowPropagation:
    """
    O fluxo precisa terminar com exit code != 0: é o que o runner unificado lê
    para marcar `Falha` e devolver 1, deixando o job do Actions vermelho.
    """

    def test_run_pipeline_propaga_a_recusa(self):
        from src.flows import ingest_fapes_flow

        class _SourceComUmEdital:
            last_listing_count = 1

            def read(self):
                return [
                    RawEdital(
                        title="EDITAL FAPES Nº 03/2026",
                        url="https://exemplo.test/edital-3",
                        raw_agency="FAPES",
                        pdf_content=b"%PDF-1.4 conteudo",
                        document_type="edital",
                    )
                ]

        class _SinkQueNaoDeveSerChamado:
            def write(self, domains):
                raise AssertionError("sink não pode rodar com a extração morta")

        with pytest.raises(MistralUnavailableError):
            ingest_fapes_flow.run_pipeline(
                source=_SourceComUmEdital(),
                transform=EditalNormalizer(extraction_service=_ServicoRecusado()),
                sink=_SinkQueNaoDeveSerChamado(),
            )
