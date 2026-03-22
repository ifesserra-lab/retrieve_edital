from src.domain.models import EditalDomain, RawEdital
from src.flows.ingest_cnpq_flow import run_pipeline


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
            orgão_fomento="CNPq",
            categoria="pesquisa",
            status="aberto",
            data_abertura="2026-03-22",
            data_encerramento="",
            link=raw_item.url,
            cronograma=[],
            tags=["cnpq"],
            anexos=[],
        )


class SpySink:
    def __init__(self):
        self.written_items = []

    def write(self, items):
        self.written_items.extend(items)


def test_ingest_cnpq_flow_persists_items_and_updates_registry(tmp_path):
    registry_path = tmp_path / "processed_editais.json"
    sink = SpySink()
    source = StubSource(
        [
            RawEdital(
                title="Chamada CNPq A",
                url="http://memoria2.cnpq.br/web/guest/chamadas-publicas?idDivulgacao=1",
                raw_agency="CNPq",
                raw_description="Descricao da chamada",
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
    assert "idDivulgacao=1" in registry_path.read_text(encoding="utf-8")
