"""
Testes do mapeamento de seção da FAPES para categoria.

A categoria saía do slug da URL e só era corrigida por uma cadeia de `if`. Em
`chamadas-internacionais` nenhuma condição casava — a URL termina em
"internacionais", que **não contém** "internacional" —, então o slug cru
`chamadas` vazava como categoria. Foram 23 editais afetados.
"""

import pytest

from src.components.sources.fapes_source import (
    FAPES_FALLBACK_CATEGORY,
    category_for_url,
)


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://fapes.es.gov.br/editais-abertos-pesquisa-4", "pesquisa"),
        ("https://fapes.es.gov.br/editais-abertos-extensao-2", "extensão"),
        ("https://fapes.es.gov.br/inovacao", "inovação"),
        ("https://fapes.es.gov.br/difusao-do-conhecimento", "divulgação de conhecimento"),
    ],
)
def test_known_sections_map_to_their_category(url, expected):
    assert category_for_url(url) == expected


def test_international_section_is_research_not_the_url_slug():
    """Era este o caso que vazava `chamadas`."""
    assert category_for_url("https://fapes.es.gov.br/chamadas-internacionais") == "pesquisa"


def test_the_failing_substring_check_is_documented_by_this_case():
    """Guarda a causa raiz: o plural não contém o singular."""
    assert "internacional" not in "chamadas-internacionais"


def test_unmapped_section_never_leaks_part_of_the_url():
    assert category_for_url("https://fapes.es.gov.br/secao-inedita") == FAPES_FALLBACK_CATEGORY
    assert category_for_url("") == FAPES_FALLBACK_CATEGORY
