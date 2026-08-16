"""
Testes da precedência entre fontes: a original vence o agregador.

Caso concreto que motivou a regra: a Chamada CONFAP & CDTI 2026-2027 chegou pela
FAPES — que hospeda as diretrizes, recebe a submissão capixaba e responde pelo
edital — e também pelo CONFAP, que a republica como cooperação internacional.
Os dois viraram arquivo em `data/output/`.
"""

import json

import pytest

from src.components.sinks.json_sink import LocalJSONSink
from src.components.transforms import cross_source_dedup as dedup
from src.domain.models import EditalDomain


def edital(nome, fonte, encerramento="2026-10-08", link="https://x/1"):
    return EditalDomain(
        nome=nome,
        descrição="d",
        orgão_fomento=fonte.upper(),
        categoria="pesquisa",
        status="aberto",
        data_abertura="2026-07-13",
        data_encerramento=encerramento,
        link=link,
        cronograma=[],
        tags=[],
        fonte_key=fonte,
    )


def grava(diretorio, item, nome_arquivo=None):
    from dataclasses import asdict

    caminho = diretorio / (nome_arquivo or f"{item.fonte_key}.json")
    caminho.write_text(json.dumps(asdict(item), ensure_ascii=False), encoding="utf-8")
    return caminho


class TestChaveCanonica:
    def test_ignora_acento_caixa_e_pontuacao(self):
        a = dedup.canonical_key("Chamada CONFAP & CDTI 2026-2027", "2026-10-08")
        b = dedup.canonical_key("CHAMADA CONFAP  CDTI 2026 2027", "2026-10-08")
        assert a == b

    def test_prazo_diferente_e_edital_diferente(self):
        a = dedup.canonical_key("Chamada X", "2026-10-08")
        b = dedup.canonical_key("Chamada X", "2027-10-08")
        assert a != b

    @pytest.mark.parametrize("nome, prazo", [("", "2026-10-08"), ("Chamada X", "")])
    def test_sem_titulo_ou_sem_prazo_nao_ha_chave(self, nome, prazo):
        """
        Sem prazo não dá para afirmar que dois títulos parecidos são o mesmo
        edital, e deduplicar errado apaga oportunidade real.
        """
        assert dedup.canonical_key(nome, prazo) == ""


class TestClassificacaoDeFonte:
    def test_confap_e_agregador(self):
        assert dedup.is_aggregator("confap") is True

    @pytest.mark.parametrize("fonte", ["fapes", "finep", "capes", "horizon", ""])
    def test_demais_sao_primarias(self, fonte):
        assert dedup.is_aggregator(fonte) is False


class TestPrecedencia:
    def test_agregador_e_descartado_quando_a_original_ja_publicou(self, tmp_path):
        grava(tmp_path, edital("Chamada CONFAP & CDTI 2026-2027", "fapes"))
        novos, remover = dedup.filter_superseded(
            [edital("Chamada CONFAP & CDTI 2026-2027", "confap")], str(tmp_path)
        )
        assert novos == []
        assert remover == []

    def test_original_substitui_o_registro_do_agregador(self, tmp_path):
        caminho = grava(tmp_path, edital("Chamada CONFAP & CDTI 2026-2027", "confap"))
        novos, remover = dedup.filter_superseded(
            [edital("Chamada CONFAP & CDTI 2026-2027", "fapes")], str(tmp_path)
        )
        assert len(novos) == 1 and novos[0].fonte_key == "fapes"
        assert remover == [str(caminho)]

    def test_duas_primarias_nao_se_eliminam(self, tmp_path):
        """
        Entre duas fontes primárias não há vencedor definido. Escolher uma
        arbitrariamente apagaria dado sem critério; melhor manter as duas.
        """
        grava(tmp_path, edital("Chamada Conjunta", "finep"))
        novos, remover = dedup.filter_superseded(
            [edital("Chamada Conjunta", "capes")], str(tmp_path)
        )
        assert len(novos) == 1
        assert remover == []

    def test_edital_inedito_passa(self, tmp_path):
        novos, remover = dedup.filter_superseded(
            [edital("Chamada Nova", "confap")], str(tmp_path)
        )
        assert len(novos) == 1 and remover == []

    def test_prazos_diferentes_nao_colidem(self, tmp_path):
        grava(tmp_path, edital("Chamada Anual", "fapes", encerramento="2025-10-08"))
        novos, _ = dedup.filter_superseded(
            [edital("Chamada Anual", "confap", encerramento="2026-10-08")],
            str(tmp_path),
        )
        assert len(novos) == 1, "edição de outro ano é outro edital"

    def test_indice_prefere_a_primaria_quando_ja_ha_duas(self, tmp_path):
        """
        Estado herdado: os dois arquivos já existem. O índice precisa apontar
        para a fonte original, senão o agregador que chegar depois é mantido.
        """
        grava(tmp_path, edital("Chamada X", "confap"), "a_confap.json")
        grava(tmp_path, edital("Chamada X", "fapes"), "b_fapes.json")
        indice = dedup.index_published(str(tmp_path))
        chave = dedup.canonical_key("Chamada X", "2026-10-08")
        assert indice[chave][0] == "fapes"


class TestSinkRemoveOArquivoDoAgregador:
    def test_arquivo_do_agregador_some_quando_a_original_grava(self, tmp_path):
        antigo = grava(tmp_path, edital("Chamada CONFAP & CDTI 2026-2027", "confap"))
        sink = LocalJSONSink(output_dir=str(tmp_path))

        sink.write([edital("Chamada CONFAP & CDTI 2026-2027", "fapes")])

        assert not antigo.exists(), "o registro do agregador deveria ter saído"
        restantes = [
            json.loads(p.read_text(encoding="utf-8")) for p in tmp_path.glob("*.json")
        ]
        assert [d["fonte_key"] for d in restantes] == ["fapes"]

    def test_gravacao_normal_nao_e_afetada(self, tmp_path):
        sink = LocalJSONSink(output_dir=str(tmp_path))
        persistidos = sink.write([edital("Chamada Isolada", "finep")])
        assert len(persistidos) == 1
        assert len(list(tmp_path.glob("*.json"))) == 1


class TestNormalizadorRecusaOAgregador:
    """
    A recusa acontece no normalizador, não no sink, porque só ali ela entra em
    `rejections` — e daí no índice com validade. Descartada no sink, a chamada
    voltaria como nova toda noite e pagaria coleta para ser jogada fora.
    """

    def _normalizer(self, tmp_path):
        from unittest.mock import MagicMock

        from src.components.transforms.edital_normalizer import EditalNormalizer

        return EditalNormalizer(
            extraction_service=MagicMock(), output_dir=str(tmp_path)
        )

    def test_recusa_entra_em_rejections_para_ganhar_validade(self, tmp_path):
        from src.domain.models import RawEdital

        grava(tmp_path, edital("Chamada CONFAP & CDTI 2026-2027", "fapes"))
        normalizer = self._normalizer(tmp_path)
        alvo = edital(
            "Chamada CONFAP & CDTI 2026-2027",
            "confap",
            link="https://confap.org.br/pt/editais/114/x",
        )
        raw = RawEdital(title=alvo.nome, url=alvo.link, raw_agency="CONFAP")

        resultado = normalizer._publish_or_discard(alvo, raw)

        assert resultado is None
        assert raw.url in normalizer.rejections
        assert "fonte original" in normalizer.rejections[raw.url]

    def test_edital_sem_duplicata_e_publicado(self, tmp_path):
        from src.domain.models import RawEdital

        normalizer = self._normalizer(tmp_path)
        alvo = edital("Chamada Inédita", "confap")
        raw = RawEdital(title=alvo.nome, url=alvo.link, raw_agency="CONFAP")

        assert normalizer._publish_or_discard(alvo, raw) is not None
        assert normalizer.rejections == {}
