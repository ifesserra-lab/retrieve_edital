"""
Tests for FINEP source: stop pagination when no editais have deadline >= current year.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.components.sources.finep_source import (
    FinepSource,
    _deadline_in_range,
    _parse_deadline_year,
)


class TestFinepDeadlineHelpers:
    """Valida funções auxiliares de prazo."""

    def test_parse_deadline_year(self):
        text = "Prazo para envio de propostas até: 15/09/2026"
        assert _parse_deadline_year(text) == 2026
        assert _parse_deadline_year("Prazo para envio de propostas até: 01/01/2025") == 2025
        assert _parse_deadline_year("sem data") is None

    def test_deadline_in_range(self):
        ref = 2026
        assert _deadline_in_range(2026, ref) is True
        assert _deadline_in_range(2027, ref) is True
        assert _deadline_in_range(2025, ref) is False
        assert _deadline_in_range(2028, ref) is False
        assert _deadline_in_range(None, ref) is False


class TestFinepSourceStopWhenNoCurrentYearEditais:
    """
    Valida que o FinepSource para de navegar quando todos os editais da página
    têm prazo para envio de propostas até em ano anterior ao de referência.
    """

    def test_stops_pagination_when_all_deadlines_are_previous_year(self):
        # reference_year=2027: só interessam prazos em 2027 ou 2028
        # Na página simulada todos têm "Prazo até 01/01/2026" -> ano anterior
        source = FinepSource(reference_year=2027, max_pages=None)

        def make_link_mock(href: str, block_text: str):
            link = MagicMock()
            link.get_attribute.return_value = href
            link.inner_text.return_value = "Chamada FINEP Teste"
            parent = MagicMock()
            parent.inner_text.return_value = block_text
            parent.locator.return_value = parent
            link.locator.return_value = parent
            return link

        # Uma página com 2 links, ambos com prazo em 2026 (ano anterior a 2027)
        link_els = [
            make_link_mock(
                "/chamadas-publicas/chamadapublica/771",
                "Prazo para envio de propostas até: 15/06/2026",
            ),
            make_link_mock(
                "/chamadas-publicas/chamadapublica/772",
                "Prazo para envio de propostas até: 01/12/2026",
            ),
        ]

        with patch("src.components.sources.finep_source.sync_playwright") as mock_pw:
            mock_page = MagicMock()
            mock_page.goto.return_value = None
            mock_page.wait_for_load_state.return_value = None
            mock_page.wait_for_selector.return_value = None
            # Primeira chamada: links da listagem; segunda: botão "Próxima" (vazio = para)
            locator_listagem = MagicMock()
            locator_listagem.all.return_value = link_els
            locator_next = MagicMock()
            locator_next.all.return_value = []
            mock_page.locator.side_effect = [locator_listagem, locator_next]

            mock_browser = MagicMock()
            mock_browser.new_page.return_value = mock_page
            mock_browser.close.return_value = None

            mock_pw_context = MagicMock()
            mock_pw_context.chromium.launch.return_value = mock_browser

            mock_pw.return_value.__enter__.return_value = mock_pw_context
            mock_pw.return_value.__exit__.return_value = None

            result = source.read()

        # Nenhum edital no ano de referência (2027/2028) -> lista vazia
        assert result == []
        # Navegou só uma vez (página 1); não foi para página 2
        assert mock_page.goto.call_count == 1
