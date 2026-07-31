"""
Testes do índice de editais recusados.

Um edital que o portão recusa nunca chega ao sink, então sua URL nunca entra no
índice de processados. Na execução seguinte ele volta como novo, tem o PDF baixado
e passa por OCR — para ser recusado de novo. Medido na FAPES: 8 editais por
execução.

Registrar a recusa para sempre resolveria o desperdício mas criaria outro
problema: um edital cuja extração falhou e depois passou a funcionar nunca voltaria.
Por isso a recusa expira.
"""

from datetime import date

import pytest

from src import rejection_store


@pytest.fixture
def indice(tmp_path):
    return str(tmp_path / "rejected.json")


HOJE = date(2026, 8, 1)


class TestRegistroEValidade:
    def test_recusa_registrada_segura_o_edital(self, indice):
        rejection_store.record(
            "fapes", {"https://x/e.pdf": "prazo encerrado"}, path=indice, today=HOJE
        )
        ativos = rejection_store.get_active_keys("fapes", path=indice, today=HOJE)
        assert ativos == {"https://x/e.pdf"}

    def test_recusa_expira_e_o_edital_volta_a_ser_candidato(self, indice):
        rejection_store.record(
            "fapes", {"https://x/e.pdf": "prazo encerrado"}, path=indice, today=HOJE
        )
        depois = date(2026, 8, 1 + rejection_store.DEFAULT_TTL_DAYS + 1)
        assert rejection_store.get_active_keys("fapes", path=indice, today=depois) == set()

    def test_ultimo_dia_de_validade_ainda_segura(self, indice):
        rejection_store.record(
            "fapes", {"https://x/e.pdf": "motivo"}, path=indice, today=HOJE
        )
        limite = date(2026, 8, 1 + rejection_store.DEFAULT_TTL_DAYS)
        assert rejection_store.get_active_keys("fapes", path=indice, today=limite)

    def test_recusa_repetida_renova_a_validade(self, indice):
        rejection_store.record("fapes", {"https://x/e.pdf": "m"}, path=indice, today=HOJE)
        depois = date(2026, 8, 5)
        rejection_store.record("fapes", {"https://x/e.pdf": "m"}, path=indice, today=depois)
        muito_depois = date(2026, 8, 5 + rejection_store.DEFAULT_TTL_DAYS)
        assert rejection_store.get_active_keys("fapes", path=indice, today=muito_depois)

    def test_fontes_nao_se_misturam(self, indice):
        rejection_store.record("fapes", {"https://x/a": "m"}, path=indice, today=HOJE)
        rejection_store.record("capes", {"https://x/b": "m"}, path=indice, today=HOJE)
        assert rejection_store.get_active_keys("fapes", path=indice, today=HOJE) == {
            "https://x/a"
        }

    def test_motivo_fica_registrado(self, indice):
        import json

        rejection_store.record(
            "fapes", {"https://x/e": "prazo encerrado em 2026-06-30"}, path=indice, today=HOJE
        )
        dados = json.load(open(indice, encoding="utf-8"))
        assert dados["fapes"]["https://x/e"]["motivo"] == "prazo encerrado em 2026-06-30"


class TestResiliencia:
    def test_indice_inexistente_nao_segura_nada(self, tmp_path):
        caminho = str(tmp_path / "nao-existe.json")
        assert rejection_store.get_active_keys("fapes", path=caminho) == set()

    def test_indice_ilegivel_e_tratado_como_vazio(self, indice):
        open(indice, "w").write("{ json quebrado")
        assert rejection_store.get_active_keys("fapes", path=indice) == set()

    def test_registro_vazio_nao_cria_arquivo(self, indice):
        import os

        assert rejection_store.record("fapes", {}, path=indice) == 0
        assert not os.path.exists(indice)

    def test_purga_remove_apenas_as_vencidas(self, indice):
        rejection_store.record("fapes", {"https://x/velha": "m"}, path=indice, today=HOJE)
        depois = date(2026, 8, 20)
        rejection_store.record("fapes", {"https://x/nova": "m"}, path=indice, today=depois)

        removidas = rejection_store.purge_expired(path=indice, today=depois)
        assert removidas == 1
        assert rejection_store.get_active_keys("fapes", path=indice, today=depois) == {
            "https://x/nova"
        }


class TestNormalizerRegistraRecusas:
    def test_recusa_fica_disponivel_para_o_fluxo(self):
        from unittest.mock import MagicMock

        from src.components.transforms.edital_normalizer import EditalNormalizer
        from src.domain.models import RawEdital

        service = MagicMock()
        service.extract_from_pdf.return_value = None
        normalizer = EditalNormalizer(extraction_service=service)

        raw = RawEdital(
            title="Edital vencido",
            url="https://exemplo.org/vencido.pdf",
            raw_agency="FAPES",
            raw_description="Apoio a projetos de pesquisa.",
            raw_cronograma=[
                {"evento": "Prazo para envio de propostas", "data": "2020-01-01"}
            ],
        )
        assert normalizer.process(raw) is None
        assert "https://exemplo.org/vencido.pdf" in normalizer.rejections
        assert "prazo encerrado" in normalizer.rejections[
            "https://exemplo.org/vencido.pdf"
        ]
