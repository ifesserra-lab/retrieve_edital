from src.domain.models import EditalDomain, RawEdital
from src.flows.ingest_prppg_ifes_flow import run_pipeline


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
            orgão_fomento="PRPPG/IFES",
            categoria="pesquisa",
            status="encerrado",
            data_abertura="2026-03-30",
            data_encerramento="2026-11-01",
            link=raw_item.url,
            cronograma=[],
            tags=["prppg", "ifes"],
            anexos=[],
        )


class SpySink:
    def __init__(self):
        self.written_items = []

    def write(self, items):
        self.written_items.extend(items)


def test_ingest_prppg_ifes_flow_persists_items_and_updates_registry(tmp_path):
    registry_path = tmp_path / "processed_editais.json"
    sink = SpySink()
    source = StubSource(
        [
            RawEdital(
                title="Edital 04/2026 - Propop-Ciência",
                url="https://sigpesq.ifes.edu.br/publico/Editais.aspx?cod=290",
                raw_agency="PRPPG/IFES",
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
    assert "cod=290" in registry_path.read_text(encoding="utf-8")
