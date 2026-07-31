"""
Testes da eleição do documento principal de um grupo da FAPES.

O principal definia a identidade do edital e, por consequência, a chave de
deduplicação. Ele era o primeiro documento que o Mistral classificasse como
`edital` — e como essa classificação varia entre execuções, o mesmo edital
mudava de identidade de uma rodada para a outra, era reprocessado por OCR e
sobrescrevia o arquivo anterior.
"""

import pytest

from src.components.sources.fapes_source import (
    elect_main_document_index,
    score_main_document,
)


def doc(title, url="documento.pdf"):
    return {"title": title, "url": url}


class TestEleicao:
    def test_prefers_the_document_matching_the_group_title(self):
        docs = [
            doc("Anexo I - Formulário de Submissão"),
            doc("Edital FAPES 04/2026 - Estágio Técnico"),
            doc("FAQ"),
        ]
        assert elect_main_document_index(docs, "Edital FAPES 04/2026 - Estágio Técnico") == 1

    def test_prefers_the_edital_over_its_retificacao(self):
        docs = [
            doc("Retificação do Edital 08/2026"),
            doc("Edital 08/2026 Nova Economia"),
        ]
        assert elect_main_document_index(docs, "Edital 08/2026 Nova Economia") == 1

    def test_supporting_documents_are_penalised(self):
        docs = [doc("Anexo II - Planilha"), doc("Diretrizes da chamada")]
        assert elect_main_document_index(docs, "Grupo desconhecido") == 1

    def test_ties_fall_back_to_dom_order(self):
        """Empate resolvido pela ordem no HTML mantém a escolha estável."""
        docs = [doc("Baixar", "a.pdf"), doc("Baixar", "b.pdf")]
        assert elect_main_document_index(docs, "Grupo desconhecido") == 0

    def test_empty_group_has_no_main(self):
        assert elect_main_document_index([], "Grupo") == -1

    def test_election_does_not_depend_on_document_order(self):
        """
        Mesma escolha independente da ordem de entrada: é isso que torna a
        identidade estável entre execuções.
        """
        edital = doc("Edital FAPES 17/2026 - Prêmio", "edital.pdf")
        anexo = doc("Anexo I - Modelo", "anexo.pdf")
        grupo = "Edital FAPES 17/2026 - Prêmio"
        assert elect_main_document_index([anexo, edital], grupo) == 1
        assert elect_main_document_index([edital, anexo], grupo) == 0

    def test_election_never_consults_an_llm(self):
        """Nenhum argumento de classificação: a decisão é só da página."""
        import inspect

        assinatura = inspect.signature(elect_main_document_index)
        assert list(assinatura.parameters) == ["docs", "group_title"]


class TestPontuacao:
    def test_url_also_counts_as_evidence(self):
        com_url = score_main_document("Baixar", "edital_04_2026.pdf", "Grupo")
        sem_url = score_main_document("Baixar", "arquivo.pdf", "Grupo")
        assert com_url > sem_url

    @pytest.mark.parametrize(
        "titulo", ["Edital 01", "Chamada Pública", "Diretrizes", "Regulamento"]
    )
    def test_main_hints_score_above_neutral(self, titulo):
        assert score_main_document(titulo, "x.pdf", "G") > score_main_document(
            "documento", "x.pdf", "G"
        )
