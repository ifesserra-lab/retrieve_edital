"""
Testes da resolução de colisão de nome de arquivo no LocalJSONSink.

Contexto: dois editais com o mesmo título produzem o mesmo slug de arquivo. O
sink sobrescrevia um com o outro em silêncio e o flow registrava as duas chaves
no índice — o edital perdido nunca voltava, porque a chave dele já constava como
processada. Caso real: as duas chamadas `Programa de Investimento em Startups
Inovadoras 2ª Rodada` da FINEP (ids 721708 e 721681).
"""

import json
import os

import pytest

from src.components.sinks.json_sink import LocalJSONSink
from src.domain.models import EditalDomain


def build_edital(nome: str, link: str, descricao: str = "Descrição") -> EditalDomain:
    return EditalDomain(
        nome=nome,
        descrição=descricao,
        orgão_fomento="FINEP",
        categoria="inovação",
        status="aberta",
        data_abertura="2026-01-01",
        data_encerramento="2026-12-31",
        link=link,
        cronograma=[],
        tags=[],
        anexos=[],
    )


@pytest.fixture
def sink(tmp_path):
    return LocalJSONSink(output_dir=str(tmp_path / "output"))


class TestCollisionBetweenDistinctEditais:
    def test_same_title_different_links_produce_two_files(self, sink):
        editais = [
            build_edital("Programa de Investimento em Startups", ".../721708"),
            build_edital("Programa de Investimento em Startups", ".../721681"),
        ]
        persisted = sink.write(editais)

        assert len(persisted) == 2
        assert len(os.listdir(sink.output_dir)) == 2

    def test_first_edital_keeps_the_unsuffixed_name(self, sink):
        """Nomes já existentes não podem mudar: as chaves FAPES são nomes de arquivo."""
        editais = [
            build_edital("Edital Repetido", ".../aaa"),
            build_edital("Edital Repetido", ".../bbb"),
        ]
        basenames = list(sink.write(editais).keys())

        assert basenames[0] == "edital_repetido"
        assert basenames[1].startswith("edital_repetido_")

    def test_neither_edital_loses_its_content(self, sink):
        sink.write(
            [
                build_edital("Edital Repetido", ".../aaa", descricao="PRIMEIRO"),
                build_edital("Edital Repetido", ".../bbb", descricao="SEGUNDO"),
            ]
        )

        descricoes = set()
        for filename in os.listdir(sink.output_dir):
            with open(os.path.join(sink.output_dir, filename), encoding="utf-8") as f:
                descricoes.add(json.load(f)["descrição"])
        assert descricoes == {"PRIMEIRO", "SEGUNDO"}

    def test_collision_across_separate_runs_is_also_handled(self, sink):
        sink.write([build_edital("Edital Repetido", ".../aaa")])
        sink.write([build_edital("Edital Repetido", ".../bbb")])
        assert len(os.listdir(sink.output_dir)) == 2

    def test_suffix_is_stable_so_reruns_do_not_multiply_files(self, sink):
        """O sufixo vem do link, não de contador: reexecutar não gera arquivo novo."""
        editais = [
            build_edital("Edital Repetido", ".../aaa"),
            build_edital("Edital Repetido", ".../bbb"),
        ]
        first = sink.write(editais)
        second = sink.write(editais)

        assert list(first.keys()) == list(second.keys())
        assert len(os.listdir(sink.output_dir)) == 2


class TestUpdateOfTheSameEdital:
    def test_same_link_overwrites_instead_of_forking(self, sink):
        """Recoletar o mesmo edital é atualização, não colisão."""
        sink.write([build_edital("Edital X", ".../aaa", descricao="VELHA")])
        sink.write([build_edital("Edital X", ".../aaa", descricao="NOVA")])

        files = os.listdir(sink.output_dir)
        assert files == ["edital_x.json"]
        with open(os.path.join(sink.output_dir, files[0]), encoding="utf-8") as f:
            assert json.load(f)["descrição"] == "NOVA"

    def test_legacy_file_without_link_is_overwritten_not_forked(self, sink):
        """Arquivo legado sem `link` não pode multiplicar a cada execução."""
        os.makedirs(sink.output_dir, exist_ok=True)
        legacy_path = os.path.join(sink.output_dir, "edital_x.json")
        with open(legacy_path, "w", encoding="utf-8") as f:
            json.dump({"nome": "Edital X", "descrição": "LEGADO"}, f)

        sink.write([build_edital("Edital X", ".../aaa")])
        assert os.listdir(sink.output_dir) == ["edital_x.json"]

    def test_unreadable_existing_file_is_treated_as_collision(self, sink):
        """Na dúvida, preserva o arquivo existente em vez de sobrescrever."""
        os.makedirs(sink.output_dir, exist_ok=True)
        with open(
            os.path.join(sink.output_dir, "edital_x.json"), "w", encoding="utf-8"
        ) as f:
            f.write("{ json quebrado")

        sink.write([build_edital("Edital X", ".../aaa")])
        assert len(os.listdir(sink.output_dir)) == 2


class TestWriteReportsWhatReachedDisk:
    def test_returns_persisted_items_keyed_by_basename(self, sink):
        edital = build_edital("Edital X", ".../aaa")
        persisted = sink.write([edital])
        assert persisted == {"edital_x": edital}

    def test_empty_batch_returns_empty_mapping(self, sink):
        assert sink.write([]) == {}

    def test_failed_write_is_left_out_of_the_result(self, sink, monkeypatch):
        """
        Registrar um edital cuja gravação falhou o marcaria como processado sem
        arquivo correspondente, e ele nunca seria recoletado.
        """
        good = build_edital("Edital Bom", ".../aaa")
        bad = build_edital("Edital Ruim", ".../bbb")
        real_open = open

        def open_failing_on_bad(path, *args, **kwargs):
            if "edital_ruim" in str(path) and "w" in str(args[0] if args else ""):
                raise OSError("disco cheio")
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr("builtins.open", open_failing_on_bad)
        persisted = sink.write([good, bad])

        assert list(persisted.keys()) == ["edital_bom"]
