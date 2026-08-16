"""
Testes do encadeamento Mistral → OpenAI.

Motivação: a Mistral respondeu `402 Check your subscription` de 2026-08-10 a
2026-08-16 e o pipeline ficou sem extração alguma. Com um provedor de reserva, a
recusa de credencial deixa de parar a coleta — mas o fallback só vale se
preservar duas garantias:

- o edital gravado é o **mesmo** independentemente do provedor;
- quando os **dois** falham, o fluxo ainda morre alto, em vez de gravar vazio.
"""

import json

import pytest

from src.components.transforms import openai_client
from src.components.transforms.extraction_contract import (
    ExtractionUnavailableError,
    map_to_domain,
)
from src.components.transforms.extraction_fallback import (
    AllProvidersUnavailableError,
    FallbackExtractionService,
    build_extraction_service,
)
from src.components.transforms.mistral_client import MistralUnavailableError
from src.components.transforms.openai_client import (
    MIN_EXTRACTABLE_CHARS,
    OpenAIExtractionService,
    OpenAIUnavailableError,
    PdfTextNotExtractableError,
)
from src.domain.models import RawEdital

BODY_402 = (
    'API error occurred: Status 402. Body: '
    '{"detail":"Check your subscription on https://admin.mistral.ai/subscription"}'
)

EDITAL_JSON = {
    "nome": "Edital Teste 01/2026",
    "descrição": "Apoio a projetos de inovação.",
    "orgão_fomento": "FAPES",
    "categoria": "inovação",
    "status": "aberto",
    "data_abertura": "2026-09-01",
    "data_encerramento": "2026-12-01",
    "cronograma": [{"evento": "Submissão", "data": "2026-09-01"}],
    "tags": ["inovação", "fapes", "pesquisa"],
}


class _MistralRecusado:
    """Principal com a assinatura recusada em toda chamada."""

    def extract_from_pdf(self, pdf_bytes, filename):
        raise MistralUnavailableError(BODY_402)

    def classify_document_titles(self, titles):
        raise MistralUnavailableError(BODY_402)

    def categorize_finep_by_description(self, description):
        raise MistralUnavailableError(BODY_402)


class _MistralSaudavel:
    def __init__(self):
        self.chamadas = 0

    def extract_from_pdf(self, pdf_bytes, filename):
        self.chamadas += 1
        return map_to_domain(EDITAL_JSON)

    def classify_document_titles(self, titles):
        self.chamadas += 1
        return {t: "edital" for t in titles}

    def categorize_finep_by_description(self, description):
        self.chamadas += 1
        return "inovação"


class _ReservaOk:
    def __init__(self):
        self.chamadas = 0

    def extract_from_pdf(self, pdf_bytes, filename):
        self.chamadas += 1
        return map_to_domain(EDITAL_JSON)

    def classify_document_titles(self, titles):
        self.chamadas += 1
        return {t: "edital" for t in titles}

    def categorize_finep_by_description(self, description):
        self.chamadas += 1
        return "extensão"


class _ReservaMorta:
    def extract_from_pdf(self, pdf_bytes, filename):
        raise OpenAIUnavailableError("Error code: 401 invalid_api_key")

    def classify_document_titles(self, titles):
        raise OpenAIUnavailableError("insufficient_quota")

    def categorize_finep_by_description(self, description):
        raise OpenAIUnavailableError("Error code: 429")


class TestFallbackAssume:
    def test_reserva_extrai_quando_principal_recusa(self):
        servico = FallbackExtractionService(_MistralRecusado(), _ReservaOk())
        edital = servico.extract_from_pdf(b"%PDF", "e.pdf")
        assert edital.nome == "EDITAL TESTE 01/2026"

    def test_reserva_classifica_titulos(self):
        servico = FallbackExtractionService(_MistralRecusado(), _ReservaOk())
        assert servico.classify_document_titles(["Edital 1"]) == {"Edital 1": "edital"}

    def test_reserva_categoriza_finep(self):
        servico = FallbackExtractionService(_MistralRecusado(), _ReservaOk())
        assert servico.categorize_finep_by_description("extensão universitária") == "extensão"

    def test_principal_saudavel_nao_aciona_a_reserva(self):
        principal, reserva = _MistralSaudavel(), _ReservaOk()
        servico = FallbackExtractionService(principal, reserva)
        servico.extract_from_pdf(b"%PDF", "e.pdf")
        assert principal.chamadas == 1
        assert reserva.chamadas == 0, "reserva não pode custar chamada à toa"

    def test_principal_morto_nao_e_retentado_a_cada_edital(self):
        """
        Sem esta memória, cada edital pagaria o roundtrip até o 402 antes de cair
        na reserva — com 30 editais por noite, são 30 chamadas jogadas fora.
        """

        class _ContaTentativas(_MistralRecusado):
            def __init__(self):
                self.tentativas = 0

            def extract_from_pdf(self, pdf_bytes, filename):
                self.tentativas += 1
                raise MistralUnavailableError(BODY_402)

        principal = _ContaTentativas()
        servico = FallbackExtractionService(principal, _ReservaOk())
        for _ in range(5):
            servico.extract_from_pdf(b"%PDF", "e.pdf")

        assert principal.tentativas == 1, "o principal só deve ser tentado uma vez"


class TestOsDoisMortos:
    @pytest.mark.parametrize(
        "metodo, args",
        [
            ("extract_from_pdf", (b"%PDF", "e.pdf")),
            ("classify_document_titles", (["Edital 1"],)),
            ("categorize_finep_by_description", ("inovação",)),
        ],
    )
    def test_falha_alto_quando_nenhum_provedor_responde(self, metodo, args):
        servico = FallbackExtractionService(_MistralRecusado(), _ReservaMorta())
        with pytest.raises(AllProvidersUnavailableError):
            getattr(servico, metodo)(*args)

    def test_e_capturavel_pela_base_comum(self):
        """
        As dez camadas de carve-out capturam `ExtractionUnavailableError`. Se este
        vínculo quebrar, o job volta a ficar verde com a extração morta.
        """
        servico = FallbackExtractionService(_MistralRecusado(), _ReservaMorta())
        with pytest.raises(ExtractionUnavailableError):
            servico.extract_from_pdf(b"%PDF", "e.pdf")

    def test_mistral_indisponivel_tambem_herda_da_base(self):
        assert issubclass(MistralUnavailableError, ExtractionUnavailableError)
        assert issubclass(OpenAIUnavailableError, ExtractionUnavailableError)


class TestPdfDigitalizado:
    """
    A OpenAI é usada sem OCR. PDF que é imagem escaneada não rende texto, e
    mandar o prompt vazio produziria um edital inventado — pior que falhar.
    """

    def test_pdf_sem_texto_recusa_em_vez_de_inventar(self):
        servico = OpenAIExtractionService(client=object(), api_key="x")
        with pytest.raises(PdfTextNotExtractableError):
            servico.extract_from_pdf(b"nao e um pdf de verdade", "scan.pdf")

    def test_pdf_ilegivel_devolve_texto_vazio(self):
        assert openai_client.extract_pdf_text(b"lixo binario") == ""

    def test_nao_e_falha_de_provedor(self):
        """
        Um documento ruim não pode derrubar o fluxo inteiro: só falha de provedor
        faz isso. Por isso esta exceção fica fora da base comum.
        """
        assert not issubclass(PdfTextNotExtractableError, ExtractionUnavailableError)

    def test_pdf_digitalizado_nao_derruba_o_fluxo_com_a_reserva_ativa(self):
        """Com o principal morto e um PDF escaneado, a falha continua por item."""

        class _ReservaSemOcr:
            def extract_from_pdf(self, pdf_bytes, filename):
                raise PdfTextNotExtractableError("scan.pdf: 0 caracteres")

        servico = FallbackExtractionService(_MistralRecusado(), _ReservaSemOcr())
        with pytest.raises(PdfTextNotExtractableError):
            servico.extract_from_pdf(b"%PDF", "scan.pdf")


class _RespostaFake:
    def __init__(self, payload):
        self.choices = [
            type("C", (), {"message": type("M", (), {"content": json.dumps(payload)})()})()
        ]


class _ClienteOpenAIFake:
    def __init__(self, payload):
        self.payload = payload
        self.kwargs = None
        completions = type("Comp", (), {"create": self._create})()
        self.chat = type("Chat", (), {"completions": completions})()

    def _create(self, **kwargs):
        self.kwargs = kwargs
        return _RespostaFake(self.payload)


class TestParidadeDeContrato:
    """
    O edital gravado precisa ser idêntico entre provedores. Se cada um tivesse o
    próprio prompt e o próprio mapeamento, trocar de provedor mudaria o formato
    dos dados sem ninguém perceber.
    """

    def test_mesmo_json_produz_o_mesmo_dominio(self):
        cliente = _ClienteOpenAIFake(EDITAL_JSON)
        servico = OpenAIExtractionService(client=cliente, api_key="x")
        pela_openai = servico._complete_json("sys", "user", "ctx")
        assert map_to_domain(pela_openai) == map_to_domain(EDITAL_JSON)

    def test_pede_json_ao_modelo(self):
        cliente = _ClienteOpenAIFake(EDITAL_JSON)
        servico = OpenAIExtractionService(client=cliente, api_key="x")
        servico.classify_document_titles(["Edital 1"])
        assert cliente.kwargs["response_format"] == {"type": "json_object"}

    def test_categoria_finep_e_canonizada(self):
        cliente = _ClienteOpenAIFake({"categoria": "INOVAÇÃO"})
        servico = OpenAIExtractionService(client=cliente, api_key="x")
        assert servico.categorize_finep_by_description("PD&I") == "inovação"

    def test_categoria_desconhecida_cai_no_padrao(self):
        cliente = _ClienteOpenAIFake({"categoria": "coisa nenhuma"})
        servico = OpenAIExtractionService(client=cliente, api_key="x")
        assert servico.categorize_finep_by_description("texto") == "inovação"


class TestCredencialDaReserva:
    def test_le_a_variavel_API_KEY(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "sk-teste")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert openai_client.is_configured() is True

    def test_aceita_OPENAI_API_KEY_como_alternativa(self, monkeypatch):
        monkeypatch.delenv("API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-teste")
        assert openai_client.is_configured() is True

    def test_sem_chave_nao_esta_configurada(self, monkeypatch):
        monkeypatch.delenv("API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert openai_client.is_configured() is False

    def test_sem_chave_a_construcao_falha_explicitamente(self, monkeypatch):
        monkeypatch.delenv("API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(OpenAIUnavailableError, match="API_KEY"):
            OpenAIExtractionService()

    @pytest.mark.parametrize(
        "mensagem",
        ["Error code: 401", "insufficient_quota", "invalid_api_key", "Error code: 429"],
    )
    def test_reconhece_recusa_da_openai(self, mensagem):
        assert openai_client._is_credential_error(RuntimeError(mensagem)) is True

    def test_erro_transitorio_nao_e_recusa(self):
        assert openai_client._is_credential_error(RuntimeError("Error code: 503")) is False


class TestFabrica:
    def test_com_as_duas_chaves_monta_o_encadeamento(self, monkeypatch):
        monkeypatch.setenv("MISTRAL_API_KEY", "m-teste")
        monkeypatch.setenv("API_KEY", "sk-teste")
        servico = build_extraction_service()
        assert isinstance(servico, FallbackExtractionService)

    def test_so_com_mistral_mantem_o_comportamento_historico(self, monkeypatch):
        from src.components.transforms.mistral_client import MistralExtractionService

        monkeypatch.setenv("MISTRAL_API_KEY", "m-teste")
        monkeypatch.delenv("API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert isinstance(build_extraction_service(), MistralExtractionService)

    def test_so_com_openai_roda_na_reserva(self, monkeypatch):
        monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
        monkeypatch.setenv("API_KEY", "sk-teste")
        assert isinstance(build_extraction_service(), OpenAIExtractionService)

    def test_sem_chave_alguma_falha(self, monkeypatch):
        monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
        monkeypatch.delenv("API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="Nenhuma chave"):
            build_extraction_service()


class TestFluxoSobreviveComAReserva:
    """
    Fecha o ciclo: com a Mistral recusando, o fluxo precisa **terminar bem** e
    gravar o edital — o oposto do que acontecia antes, quando ele morria.
    """

    def test_normalizador_publica_usando_a_reserva(self):
        from src.components.transforms.edital_normalizer import EditalNormalizer

        servico = FallbackExtractionService(_MistralRecusado(), _ReservaOk())
        normalizer = EditalNormalizer(extraction_service=servico)
        raw = RawEdital(
            title="EDITAL TESTE 01/2026",
            url="https://exemplo.test/e1",
            raw_agency="FAPES",
            pdf_content=b"%PDF-1.4",
            document_type="edital",
        )

        edital = normalizer.process(raw)

        assert edital is not None, "a reserva precisa salvar a extração"
        assert edital.link == "https://exemplo.test/e1"
