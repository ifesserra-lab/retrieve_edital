"""
Testes das regras de publicação.

Levantamento de 2026-07-29: de 211 editais em `data/output/`, só 47 estavam
abertos com prazo futuro. O resto era 24 cards de anexo/alteração, 29 cascas
vazias, 4 órfãos de portal descontinuado e 63 já encerrados.
"""

from datetime import date

import pytest

from src.components.transforms import publication_rules
from src.components.transforms.publication_rules import evaluate, resolve_status
from src.domain.models import EditalDomain, RawEdital

HOJE = date(2026, 7, 29)


def build_edital(**overrides) -> EditalDomain:
    campos = {
        "nome": "EDITAL FAPES Nº 01/2026",
        "descrição": "Apoio a projetos de pesquisa aplicada.",
        "orgão_fomento": "FAPES",
        "categoria": "pesquisa",
        "status": "aberto",
        "data_abertura": "2026-06-01",
        "data_encerramento": "2026-12-31",
        "link": "https://exemplo.org/edital",
        "cronograma": [{"evento": "Abertura das inscrições", "data": "2026-06-01"}],
        "tags": ["pesquisa"],
        "anexos": [],
    }
    campos.update(overrides)
    return EditalDomain(**campos)


def build_raw(**overrides) -> RawEdital:
    campos = {"title": "Edital", "url": "https://exemplo.org/edital"}
    campos.update(overrides)
    return RawEdital(**campos)


class TestSupportingDocuments:
    @pytest.mark.parametrize("document_type", ["anexo", "alteração", "ALTERACAO"])
    def test_supporting_document_is_not_published(self, document_type):
        """Anexo e alteração são documentos de um edital, não editais."""
        verdict = evaluate(
            build_edital(), build_raw(document_type=document_type), today=HOJE
        )
        assert verdict.publishable is False
        assert "documento de apoio" in verdict.reason

    def test_edital_is_published(self):
        verdict = evaluate(
            build_edital(), build_raw(document_type="edital"), today=HOJE
        )
        assert verdict.publishable is True


class TestEmptyShells:
    def test_generated_description_without_schedule_or_deadline_is_rejected(self):
        """Assinatura da casca: descrição gerada do título, sem cronograma nem prazo."""
        verdict = evaluate(
            build_edital(
                descrição="Edital de fomento FAPES: 1ª CHAMADA RAMP",
                cronograma=[],
                data_encerramento="",
            ),
            build_raw(),
            today=HOJE,
        )
        assert verdict.publishable is False
        assert "extração não produziu" in verdict.reason

    def test_generated_description_with_a_schedule_is_kept(self):
        """Cronograma presente já mostra que houve extração."""
        verdict = evaluate(
            build_edital(
                descrição="Edital de fomento FAPES: 1ª CHAMADA RAMP",
                data_encerramento="",
            ),
            build_raw(),
            today=HOJE,
        )
        assert verdict.publishable is True

    def test_real_description_without_deadline_is_kept(self):
        """Chamada de fluxo contínuo não tem prazo e é oportunidade legítima."""
        verdict = evaluate(
            build_edital(cronograma=[], data_encerramento=""),
            build_raw(),
            today=HOJE,
        )
        assert verdict.publishable is True


class TestExpiredDeadline:
    def test_deadline_in_the_past_is_not_published(self):
        verdict = evaluate(
            build_edital(data_encerramento="2026-06-08"), build_raw(), today=HOJE
        )
        assert verdict.publishable is False
        assert "prazo encerrado" in verdict.reason

    def test_deadline_today_is_still_published(self):
        verdict = evaluate(
            build_edital(data_encerramento="2026-07-29"), build_raw(), today=HOJE
        )
        assert verdict.publishable is True

    def test_year_filter_alone_would_have_let_this_through(self):
        """
        Era esta a origem dos 63 vencidos: os sources filtram por ano, então em
        julho de 2026 um prazo de abril de 2026 ainda passava.
        """
        abril = build_edital(data_encerramento="2026-04-09")
        assert abril.data_encerramento[:4] == str(HOJE.year)
        assert evaluate(abril, build_raw(), today=HOJE).publishable is False

    def test_malformed_deadline_does_not_discard_the_edital(self):
        verdict = evaluate(
            build_edital(data_encerramento="31/12/2026"), build_raw(), today=HOJE
        )
        assert verdict.publishable is True


class TestResolveStatus:
    def test_expired_edital_becomes_encerrado(self):
        edital = build_edital(data_encerramento="2026-01-15", status="aberto")
        assert resolve_status(edital, today=HOJE) == "encerrado"

    def test_status_is_canonicalized_to_two_values(self):
        """
        `aberta` vinha de `situacao` na API da FINEP. Duas grafias para o mesmo
        estado tornavam o campo inútil como filtro no portal.
        """
        edital = build_edital(data_encerramento="2026-12-31", status="aberta")
        assert resolve_status(edital, today=HOJE) == "aberto"

    def test_edital_without_deadline_is_open(self):
        edital = build_edital(data_encerramento="", status="aberto")
        assert resolve_status(edital, today=HOJE) == "aberto"

    def test_closed_synonym_without_deadline_stays_closed(self):
        edital = build_edital(data_encerramento="", status="encerrada")
        assert resolve_status(edital, today=HOJE) == "encerrado"

    def test_empty_status_defaults_to_aberto(self):
        edital = build_edital(data_encerramento="2026-12-31", status="")
        assert resolve_status(edital, today=HOJE) == "aberto"

    def test_source_declared_closure_wins_over_a_future_deadline(self):
        """
        A PRPPG/IFES marca editais como encerrados antes do fim do período
        declarado. A palavra da fonte captura o encerramento antecipado; o prazo,
        isolado, não.
        """
        edital = build_edital(data_encerramento="2026-11-01", status="encerrado")
        assert resolve_status(edital, today=HOJE) == "encerrado"


def test_today_defaults_to_the_current_date():
    """Sem `today`, a regra usa a data corrente — não uma data fixa no código."""
    verdict = evaluate(build_edital(data_encerramento="1999-01-01"), build_raw())
    assert verdict.publishable is False
    assert publication_rules.FALLBACK_DESCRIPTION_PREFIX == "Edital de fomento"


class TestCanonicalCategory:
    """
    Havia nove valores de `categoria` em data/output/, e o campo é filtro no
    portal. As origens: `chamadas` vazava do slug da URL da FAPES, o Mistral
    devolvia combinações livres como `pesquisa e inovação`, e `internacional`
    descrevia âmbito em vez de tema.
    """

    @pytest.mark.parametrize("value", publication_rules.CANONICAL_CATEGORIES)
    def test_canonical_value_is_preserved(self, value):
        assert publication_rules.canonical_category(value) == value

    def test_case_and_whitespace_are_tolerated(self):
        assert publication_rules.canonical_category("  Pesquisa ") == "pesquisa"

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("pesquisa e inovação", "pesquisa"),
            ("inovação e pesquisa", "inovação"),
            ("formação e extensão", "extensão"),
            ("pesquisa, extensão", "pesquisa"),
        ],
    )
    def test_combined_value_keeps_the_first_term_mentioned(self, value, expected):
        """O Mistral escreve o tema principal primeiro."""
        assert publication_rules.canonical_category(value) == expected

    def test_non_theme_value_is_recovered_from_the_edital_text(self):
        """`chamadas` descreve o instrumento; o tema está no conteúdo."""
        assert (
            publication_rules.canonical_category(
                "chamadas", "CHAMADA CONFAP & WBI - projetos conjuntos de pesquisa"
            )
            == "pesquisa"
        )

    def test_falls_back_to_outros_without_any_evidence(self):
        assert publication_rules.canonical_category("chamadas") == "outros"
        assert publication_rules.canonical_category("") == "outros"
        assert publication_rules.canonical_category(None) == "outros"

    def test_hint_text_gathers_name_description_and_tags(self):
        edital = build_edital(
            nome="EDITAL X", descrição="Fomento a", tags=["inovação tecnológica"]
        )
        hint = publication_rules.category_hint_text(edital)
        assert "EDITAL X" in hint and "inovação tecnológica" in hint

    def test_result_is_always_inside_the_vocabulary(self):
        vocabulary = set(publication_rules.CANONICAL_CATEGORIES) | {
            publication_rules.CATEGORY_FALLBACK
        }
        for value in ["chamadas", "internacional", "qualquer coisa", "", None]:
            assert publication_rules.canonical_category(value) in vocabulary


class TestClassifierFailureIsNotDisguisedAsAResult:
    """
    Em 2026-07-31 a chave da API Mistral passou a responder 401. O classificador
    da FINEP engolia a falha e devolvia `inovação`, valor indistinguível de uma
    classificação real — o chamador recebia algo plausível e seguia adiante.

    Devolver vazio corrigiu o palpite, mas não o silêncio: entre 2026-08-10 e
    2026-08-16 a API respondeu 402 a toda chamada e o job seguiu verde por sete
    dias. Recusa de credencial/assinatura passou a subir como
    `MistralUnavailableError`; falha transitória continua devolvendo vazio.
    """

    def test_credential_refusal_raises_instead_of_returning_a_value(self):
        from unittest.mock import MagicMock, patch

        from src.components.transforms.mistral_client import (
            MistralExtractionService,
            MistralUnavailableError,
        )

        with patch.dict("os.environ", {"MISTRAL_API_KEY": "chave-de-teste"}):
            service = MistralExtractionService()
        service.client = MagicMock()
        service.client.chat.complete.side_effect = RuntimeError("Status 401")

        with pytest.raises(MistralUnavailableError):
            service.categorize_finep_by_description("Subvenção à inovação.")

    def test_transient_failure_still_returns_empty(self):
        """Erro passageiro não derruba o fluxo: devolve vazio, sem palpite."""
        from unittest.mock import MagicMock, patch

        from src.components.transforms.mistral_client import MistralExtractionService

        with patch.dict("os.environ", {"MISTRAL_API_KEY": "chave-de-teste"}):
            service = MistralExtractionService()
        service.client = MagicMock()
        service.client.chat.complete.side_effect = RuntimeError("Status 502")

        assert service.categorize_finep_by_description("Subvenção à inovação.") == ""

    def test_normalizer_keeps_the_source_category_when_classification_is_unavailable(self):
        from unittest.mock import MagicMock

        from src.components.transforms.edital_normalizer import EditalNormalizer

        service = MagicMock()
        service.categorize_finep_by_description.return_value = ""
        normalizer = EditalNormalizer(extraction_service=service)

        raw = RawEdital(
            title="Chamada FINEP",
            url="https://www.finep.gov.br/e/chamada-publica/222684/1",
            raw_agency="FINEP",
            raw_description="Subvenção econômica para projetos de pesquisa aplicada.",
            source_category="pesquisa",
            raw_cronograma=[
                {"evento": "Prazo para envio de propostas", "data": "2099-12-31"}
            ],
        )
        edital = normalizer.process(raw)

        assert edital is not None
        assert edital.categoria == "pesquisa"


class TestPlaceholderOpeningDate:
    """
    `data_abertura` sem data real recebia 1º de janeiro do ano corrente, e o
    portal exibia isso como se fosse informação da fonte — 64 editais mostravam
    uma abertura que ninguém publicou.
    """

    def test_normalizer_leaves_the_opening_date_empty_when_nothing_was_found(self):
        from unittest.mock import MagicMock

        from src.components.transforms.edital_normalizer import EditalNormalizer

        service = MagicMock()
        service.extract_from_pdf.return_value = None
        normalizer = EditalNormalizer(extraction_service=service)

        raw = RawEdital(
            title="Edital sem cronograma",
            url="https://exemplo.org/edital",
            raw_agency="FAPES",
            raw_description="Apoio a projetos de pesquisa aplicada no estado.",
        )
        edital = normalizer.process(raw)

        assert edital is not None
        assert edital.data_abertura == ""

    def test_normalizer_keeps_a_real_opening_date(self):
        from unittest.mock import MagicMock

        from src.components.transforms.edital_normalizer import EditalNormalizer

        service = MagicMock()
        service.extract_from_pdf.return_value = None
        normalizer = EditalNormalizer(extraction_service=service)

        raw = RawEdital(
            title="Edital com cronograma",
            url="https://exemplo.org/edital",
            raw_agency="FAPES",
            raw_description="Apoio a projetos de pesquisa aplicada no estado.",
            raw_cronograma=[
                {"evento": "Abertura das inscrições", "data": "2026-03-10"},
                {"evento": "Prazo para envio de propostas", "data": "2099-12-31"},
            ],
        )
        edital = normalizer.process(raw)

        assert edital.data_abertura == "2026-03-10"


def test_curation_clears_the_invented_opening_date():
    from scripts.curate_output import expected_opening_date

    # 1º de janeiro sem etapa que o confirme: era o placeholder.
    assert expected_opening_date({"data_abertura": "2026-01-01", "cronograma": []}) == ""
    # 1º de janeiro confirmado pelo cronograma: é data real, preservada.
    assert (
        expected_opening_date(
            {
                "data_abertura": "2026-01-01",
                "cronograma": [{"evento": "Abertura", "data": "2026-01-01"}],
            }
        )
        == "2026-01-01"
    )
    # Qualquer outra data passa intacta.
    assert (
        expected_opening_date({"data_abertura": "2026-05-20", "cronograma": []})
        == "2026-05-20"
    )


class TestCronogramaIsNotDiscarded:
    """
    `mistral_domain.cronograma = normalized_cronograma` substituía o cronograma
    extraído do PDF pelo da fonte. Como FAPES, CAPES e PROEX/IFES não fornecem
    cronograma, a substituição era por lista vazia: 74 editais ficaram sem
    cronograma e 23 sem data alguma, mesmo com o OCR já pago.
    """

    @staticmethod
    def _normalizer_with_extraction(cronograma, **campos):
        from unittest.mock import MagicMock

        from src.components.transforms.edital_normalizer import EditalNormalizer

        extraido = build_edital(cronograma=cronograma, **campos)
        service = MagicMock()
        service.extract_from_pdf.return_value = extraido
        return EditalNormalizer(extraction_service=service)

    def test_keeps_the_extracted_cronograma_when_the_source_has_none(self):
        normalizer = self._normalizer_with_extraction(
            [
                {"evento": "Abertura das inscrições", "data": "2026-02-25"},
                {"evento": "Prazo para envio de propostas", "data": "2099-04-13"},
            ],
            data_abertura="",
            data_encerramento="",
        )
        raw = RawEdital(
            title="Edital FAPES",
            url="https://fapes.es.gov.br/edital.pdf",
            raw_agency="FAPES",
            pdf_content=b"%PDF-fake",
            document_type="edital",
        )
        edital = normalizer.process(raw)

        assert [c["evento"] for c in edital.cronograma] == [
            "Abertura das inscrições",
            "Prazo para envio de propostas",
        ]
        assert edital.data_abertura == "2026-02-25"
        assert edital.data_encerramento == "2099-04-13"

    def test_merges_both_without_losing_either_side(self):
        """O CONIF traz só a publicação; o prazo vem do PDF."""
        normalizer = self._normalizer_with_extraction(
            [{"evento": "Prazo para envio de propostas", "data": "2099-08-31"}],
            data_encerramento="",
        )
        raw = RawEdital(
            title="Edital CONIF",
            url="https://portal.conif.org.br/editais/2026/edital-8",
            raw_agency="CONIF",
            pdf_content=b"%PDF-fake",
            document_type="edital",
            raw_cronograma=[{"evento": "data de publicação", "data": "2026-07-25"}],
        )
        edital = normalizer.process(raw)

        eventos = [c["evento"] for c in edital.cronograma]
        assert "data de publicação" in eventos
        assert "Prazo para envio de propostas" in eventos
        assert edital.data_encerramento == "2099-08-31"

    def test_source_wins_when_both_declare_the_same_event(self):
        normalizer = self._normalizer_with_extraction(
            [{"evento": "Prazo para envio de propostas", "data": "2099-01-01"}]
        )
        raw = RawEdital(
            title="Edital",
            url="https://exemplo.org/e.pdf",
            raw_agency="FINEP",
            pdf_content=b"%PDF-fake",
            document_type="edital",
            raw_cronograma=[
                {"evento": "Prazo para envio de propostas", "data": "2099-12-31"}
            ],
        )
        edital = normalizer.process(raw)
        assert edital.data_encerramento == "2099-12-31"


class TestModalidade:
    def test_source_declared_modality_is_used(self):
        edital = build_edital()
        raw = build_raw(raw_modalidade="fluxo-contínuo")
        assert publication_rules.resolve_modalidade(edital, raw) == "fluxo-contínuo"

    def test_detected_from_the_edital_text(self):
        edital = build_edital(
            nome="SUBVENÇÃO DESCENTRALIZADA EM FLUXO CONTÍNUO - PRÓ AMAZÔNIA"
        )
        assert (
            publication_rules.resolve_modalidade(edital, build_raw())
            == "fluxo-contínuo"
        )

    def test_absence_of_deadline_is_not_evidence_of_continuous_flow(self):
        """Deduzir da falta de prazo seria circular: é o que o campo desambigua."""
        edital = build_edital(data_encerramento="", cronograma=[])
        assert publication_rules.resolve_modalidade(edital, build_raw()) == ""


class TestCamposDeFonte:
    """
    Prioridade 6 do PDF de análise. `ambito_geografico` e `fonte_key` são
    conhecimento estático e certo sobre cada fonte; `publico_alvo` só é preenchido
    com o que a origem declara.
    """

    @pytest.mark.parametrize(
        "orgao, ambito, fonte_key",
        [
            ("FAPES", "estadual-ES", "fapes"),
            ("FINEP", "nacional", "finep"),
            ("HORIZON EUROPE", "internacional", "horizon"),
            ("PRPPG/IFES", "estadual-ES", "prppg_ifes"),
        ],
    )
    def test_perfil_da_fonte(self, orgao, ambito, fonte_key):
        edital = build_edital(orgão_fomento=orgao)
        raw = build_raw()
        assert publication_rules.resolve_ambito_geografico(edital, raw) == ambito
        assert publication_rules.resolve_fonte_key(edital, raw) == fonte_key

    def test_ambito_declarado_pela_origem_prevalece(self):
        """A FINEP informa a região da chamada, que não é sempre Todo Brasil."""
        edital = build_edital(orgão_fomento="FINEP")
        raw = build_raw(raw_ambito_geografico="Região Norte")
        assert publication_rules.resolve_ambito_geografico(edital, raw) == "Região Norte"

    def test_fonte_desconhecida_fica_vazia(self):
        edital = build_edital(orgão_fomento="AGÊNCIA NOVA")
        assert publication_rules.resolve_ambito_geografico(edital, build_raw()) == ""

    def test_publico_alvo_so_com_o_que_a_origem_declara(self):
        raw = build_raw(raw_publico_alvo=["empresa", "ict-empresa"])
        assert publication_rules.resolve_publico_alvo(build_edital(), raw) == [
            "empresa",
            "ict-empresa",
        ]

    def test_publico_alvo_vazio_quando_a_origem_nao_informa(self):
        """Inferir do texto produziria rótulo plausível e não verificável."""
        assert publication_rules.resolve_publico_alvo(build_edital(), build_raw()) == []

    def test_publico_alvo_descarta_valor_fora_do_vocabulario(self):
        raw = build_raw(raw_publico_alvo=["empresa", "qualquer coisa", "EMPRESA"])
        assert publication_rules.resolve_publico_alvo(build_edital(), raw) == ["empresa"]
