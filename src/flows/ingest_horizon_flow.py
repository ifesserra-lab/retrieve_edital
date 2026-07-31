import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Sequence

from dotenv import load_dotenv

from src.components.sinks.json_sink import LocalJSONSink
from src.components.sources.horizon_source import HorizonSource
from src.components.transforms.edital_normalizer import EditalNormalizer
from src.core.interfaces import ISink, ISource, ITransform
from src.domain.models import EditalDomain, RawEdital
from src.flow_health import emit_flow_stats
from src import rejection_store
from src.processed_store import DEFAULT_PATH, add_many, get_keys_set

load_dotenv()

logger = logging.getLogger(__name__)


def run_pipeline(
    source: Optional[ISource[RawEdital]] = None,
    transform: Optional[ITransform[RawEdital, EditalDomain]] = None,
    sink: Optional[ISink[EditalDomain]] = None,
    divisions: Optional[Sequence[str]] = None,
    processed_index_path: str = DEFAULT_PATH,
) -> None:
    """
    Orquestra o ETL das chamadas do Horizon Europe (extract → transform → sink).

    Cadência semanal: o dataset de origem tem ~126 MB e muda pouco de um dia para
    o outro. Ver `.github/workflows/run_horizon_weekly.yml`.
    """
    processed_urls = get_keys_set("horizon", path=processed_index_path)
    # Recusas ainda válidas contam como já vistas: sem isso, um edital
    # que o portão rejeitou volta como novo em toda execução, com PDF
    # baixado e OCR refeito só para ser rejeitado de novo.
    processed_urls = processed_urls | rejection_store.get_active_keys("horizon")
    source = source or HorizonSource(
        divisions=divisions, processed_urls=processed_urls
    )
    transform = transform or EditalNormalizer()
    sink = sink or LocalJSONSink()

    logger.info("Starting Horizon Europe Pipeline...")

    logger.info("Phase 1: Extraction")
    raw_data_list = source.read()

    # Quantas chamadas relevantes a origem devolveu antes da deduplicação: é o
    # que permite ao runner distinguir "nada novo" de "source quebrado".
    listing_count = getattr(source, "last_listing_count", len(raw_data_list))

    if not raw_data_list:
        emit_flow_stats(raw_count=listing_count, new_count=0)
        logger.warning("Extraction returned empty. Halting pipeline.")
        return

    logger.info("Extracted %s raw records.", len(raw_data_list))
    logger.info("Phase 2: Transformation (Parallel)")
    valid_domains = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_item = {
            executor.submit(transform.process, item): item for item in raw_data_list
        }
        for future in future_to_item:
            raw_item = future_to_item[future]
            try:
                domain_item = future.result()
                if domain_item:
                    valid_domains.append(domain_item)
            except Exception as exc:
                logger.error("Failed to transform item %s: %s", raw_item.title, exc)

    logger.info(
        "Successfully transformed %s out of %s records.",
        len(valid_domains),
        len(raw_data_list),
    )

    logger.info("Phase 3: Load/Sink")
    emit_flow_stats(raw_count=listing_count, new_count=len(valid_domains))
    rejection_store.record("horizon", getattr(transform, "rejections", {}))

    if valid_domains:
        persisted = sink.write(valid_domains)
        add_many(
            "horizon",
            [d.link for d in persisted.values()],
            path=processed_index_path,
        )
        logger.info("Pipeline completed successfully.")
    else:
        logger.warning("No valid domains to sink. Pipeline finished with warnings.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()
