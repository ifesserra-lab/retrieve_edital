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
