from unittest.mock import MagicMock

from src.components.transforms.edital_normalizer import EditalNormalizer
from src.domain.models import RawEdital


def test_process_uses_raw_status_and_period_fallback_dates():
    mock_service = MagicMock()
    mock_service.extract_from_pdf.return_value = None
    normalizer = EditalNormalizer(extraction_service=mock_service)
    raw = RawEdital(
        title="Edital 04/2026 - Propop-Ciência",
        url="https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=290",
        raw_agency="PRPPG/IFES",
        raw_status="encerrado",
        raw_description="Fluxo contínuo para participação em feiras.",
        raw_cronograma=[
            {"evento": "início do período do edital", "data": "2026-03-30"},
            {"evento": "fim do período do edital", "data": "2026-11-01"},
            {"evento": "Inscrição no SIGPesq - fluxo contínuo", "data": "2026-03-30"},
        ],
        raw_tags=["prppg", "ifes", "2026"],
    )

    result = normalizer.process(raw)

    assert result.status == "encerrado"
    assert result.data_abertura == "2026-03-30"
    assert result.data_encerramento == "2026-11-01"
