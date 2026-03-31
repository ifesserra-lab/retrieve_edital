from src.domain.models import EditalDomain, RawEdital
from src.flows.ingest_proex_ifes_flow import run_pipeline


class StubSource:
    def __init__(self, items):
        self.items = items

    def read(self):
        return self.items


class StubTransform:
    def process(self, raw_item):
        return EditalDomain(
            nome=raw_item.title,
            descrição=raw_item.raw_description or "descricao",
            orgão_fomento="PROEX/IFES",
            categoria="extensão",
            status="aberto",
            data_abertura="2026-01-01",
            data_encerramento="",
            link=raw_item.url,
            cronograma=[],
            tags=["proex", "ifes"],
            anexos=[],
        )


class SpySink:
    def __init__(self):
        self.written_items = []

    def write(self, items):
        self.written_items.extend(items)


def test_ingest_proex_ifes_flow_persists_items_and_updates_registry(tmp_path):
    registry_path = tmp_path / "processed_editais.json"
    sink = SpySink()
    source = StubSource(
        [
            RawEdital(
                title="EDITAL Nº 05/2026 - Prêmio Assistec Inova",
                url="https://proex.ifes.edu.br/images/editais/2026/05/edital-05.pdf",
                raw_agency="PROEX/IFES",
                raw_description="Descricao do edital",
            )
        ]
    )

    run_pipeline(
        source=source,
        transform=StubTransform(),
        sink=sink,
        processed_index_path=str(registry_path),
    )

    assert len(sink.written_items) == 1
    assert registry_path.exists()
    assert "edital-05.pdf" in registry_path.read_text(encoding="utf-8")
