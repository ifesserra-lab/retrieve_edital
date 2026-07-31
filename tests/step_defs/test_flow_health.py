"""
Testes dos sinais de saúde dos fluxos (INF-04).

O que está sendo protegido: a diferença entre "o portal não publicou nada" e
"o source parou de funcionar". As duas situações eram reportadas como
`Sucesso, delta 0`.
"""

from src.flow_health import (
    FLOW_STATS_PREFIX,
    FlowStats,
    emit_flow_stats,
    parse_flow_stats,
    warn_on_redirect,
)


class TestEmitAndParseFlowStats:
    def test_emit_prints_machine_readable_line(self, capsys):
        emit_flow_stats(raw_count=36, new_count=5)
        assert capsys.readouterr().out.strip() == f"{FLOW_STATS_PREFIX} raw=36 new=5"

    def test_emit_without_new_count(self, capsys):
        emit_flow_stats(raw_count=0)
        assert capsys.readouterr().out.strip() == f"{FLOW_STATS_PREFIX} raw=0"

    def test_parse_reads_counts_from_noisy_output(self):
        output = (
            "INFO Starting flow...\n"
            f"{FLOW_STATS_PREFIX} raw=36 new=5\n"
            "INFO Pipeline completed successfully.\n"
        )
        assert parse_flow_stats(output) == FlowStats(raw_count=36, new_count=5)

    def test_parse_keeps_the_last_occurrence(self):
        output = f"{FLOW_STATS_PREFIX} raw=0\n{FLOW_STATS_PREFIX} raw=36 new=5\n"
        assert parse_flow_stats(output) == FlowStats(raw_count=36, new_count=5)

    def test_parse_returns_none_for_uninstrumented_flow(self):
        assert parse_flow_stats("INFO nothing to report") is None
        assert parse_flow_stats("") is None

    def test_source_returned_nothing_flags_broken_scraper(self):
        assert FlowStats(raw_count=0, new_count=0).source_returned_nothing is True
        assert FlowStats(raw_count=36, new_count=0).source_returned_nothing is False


class TestWarnOnRedirect:
    def test_detects_the_finep_style_outage(self, caplog):
        redirected = warn_on_redirect(
            "http://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta",
            "https://www.finep.gov.br/oportunidades",
        )
        assert redirected is True
        assert "redirecionou" in caplog.text

    def test_ignores_cosmetic_differences(self):
        assert (
            warn_on_redirect(
                "http://www.gov.br/cnpq/pt-br/chamadas/",
                "https://gov.br/cnpq/pt-br/chamadas",
            )
            is False
        )

    def test_ignores_missing_urls(self):
        assert warn_on_redirect("", "https://example.org") is False
        assert warn_on_redirect("https://example.org", "") is False


class TestStatsEmittedWhenEverythingIsRejected:
    """
    O PROEX/IFES devolveu 7 itens e publicou 0 — todos com prazo encerrado — e não
    emitiu estatística alguma: `emit_flow_stats` estava dentro do
    `if valid_domains:`. Sem o sinal, o runner cai no proxy de sequência e pode
    acusar de quebrada uma origem que respondeu normalmente.
    """

    def test_every_flow_emits_outside_the_valid_domains_branch(self):
        import pathlib
        import re

        for caminho in sorted(pathlib.Path("src/flows").glob("ingest_*_flow.py")):
            fonte = caminho.read_text(encoding="utf-8")
            emissao = re.search(
                r"^(\s*)emit_flow_stats\(raw_count=listing_count, new_count=len\(",
                fonte,
                re.M,
            )
            assert emissao, f"{caminho.name} não emite estatísticas antes do sink"
            # Quatro espaços = corpo da função; oito = dentro de um `if`.
            assert len(emissao.group(1)) == 4, (
                f"{caminho.name} emite dentro de um bloco condicional: "
                "itens todos rejeitados não gerariam sinal"
            )
