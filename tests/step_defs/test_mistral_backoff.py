"""
Testes do teto de espera do backoff do Mistral.

Contar tentativas não limita duração: dez retentativas dobrando a partir de 60s
somavam mais de 17 horas numa única chamada, muito além de qualquer janela de job.
O corte passou a ser por tempo acumulado.
"""

import pytest

from src.components.transforms import mistral_client
from src.components.transforms.mistral_client import (
    RATE_LIMIT_MAX_TOTAL_WAIT_SEC,
    _call_with_rate_limit_retry,
    _is_rate_limit_error,
)


@pytest.fixture
def esperas(monkeypatch):
    """Captura as esperas sem realmente dormir."""
    registradas = []
    monkeypatch.setattr(mistral_client.time, "sleep", registradas.append)
    return registradas


class TestRateLimitDetection:
    @pytest.mark.parametrize(
        "mensagem",
        ["Status 429", "rate_limited", "Rate limit exceeded"],
    )
    def test_recognises_rate_limit_errors(self, mensagem):
        assert _is_rate_limit_error(RuntimeError(mensagem)) is True

    def test_other_errors_are_not_rate_limits(self):
        assert _is_rate_limit_error(RuntimeError("Status 401 Unauthorized")) is False


class TestCumulativeWaitCap:
    def test_total_wait_never_exceeds_the_cap(self, esperas):
        def sempre_429():
            raise RuntimeError("Status 429 rate_limited")

        with pytest.raises(RuntimeError):
            _call_with_rate_limit_retry(sempre_429, context="teste")

        assert sum(esperas) <= RATE_LIMIT_MAX_TOTAL_WAIT_SEC
        # Sem o teto, dez tentativas dobrando de 60s passariam de 17 horas.
        assert sum(esperas) < 17 * 3600

    def test_last_wait_is_shortened_to_fit_the_cap(self, esperas):
        def sempre_429():
            raise RuntimeError("Status 429")

        with pytest.raises(RuntimeError):
            _call_with_rate_limit_retry(sempre_429)

        # A soma encosta no teto sem passar: a última espera foi encurtada.
        assert sum(esperas) == pytest.approx(RATE_LIMIT_MAX_TOTAL_WAIT_SEC)

    def test_success_after_a_retry_does_not_raise(self, esperas):
        tentativas = {"n": 0}

        def falha_uma_vez():
            tentativas["n"] += 1
            if tentativas["n"] == 1:
                raise RuntimeError("Status 429")
            return "ok"

        assert _call_with_rate_limit_retry(falha_uma_vez) == "ok"
        assert esperas == [60]

    def test_non_rate_limit_error_is_raised_without_waiting(self, esperas):
        def falha_401():
            raise RuntimeError("Status 401 Unauthorized")

        with pytest.raises(RuntimeError, match="401"):
            _call_with_rate_limit_retry(falha_401)
        assert esperas == []
