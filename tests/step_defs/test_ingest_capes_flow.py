from src.domain.models import EditalDomain, RawEdital
from src.flows.ingest_capes_flow import run_pipeline


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
            orgão_fomento="CAPES",
            categoria="pesquisa",
            status="aberto",
            data_abertura="2026-03-22",
            data_encerramento="",
            link=raw_item.url,
            cronograma=[],
            tags=["capes"],
            anexos=[],
        )


class SpySink:
    def __init__(self):
        self.written_items = []

    def write(self, items):
        self.written_items.extend(items)


def test_ingest_capes_flow_persists_items_and_updates_registry(tmp_path):
    registry_path = tmp_path / "processed_editais.json"
    sink = SpySink()
    source = StubSource(
        [
            RawEdital(
                title="Edital CAPES A",
                url="https://www.gov.br/capes/pt-br/assuntos/edital-a",
                raw_agency="CAPES",
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
    assert "edital-a" in registry_path.read_text(encoding="utf-8")
