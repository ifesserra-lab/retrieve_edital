import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from dotenv import load_dotenv

from src.components.sinks.json_sink import LocalJSONSink
from src.components.sources.prppg_ifes_source import PrppgIfesSource
from src.components.transforms.edital_normalizer import EditalNormalizer
from src.core.interfaces import ISink, ISource, ITransform
from src.domain.models import EditalDomain, RawEdital
from src.processed_store import DEFAULT_PATH, add_many, get_keys_set

load_dotenv()

logger = logging.getLogger(__name__)


def run_pipeline(
    source: Optional[ISource[RawEdital]] = None,
    transform: Optional[ITransform[RawEdital, EditalDomain]] = None,
    sink: Optional[ISink[EditalDomain]] = None,
    current_year: Optional[int] = None,
    processed_index_path: str = DEFAULT_PATH,
) -> None:
    """
    Orquestra o ETL de editais PRPPG/IFES usando deduplicação pela URL
    estável da página de detalhe (`Editais.aspx?cod=...`).
    """
    processed_urls = get_keys_set("prppg_ifes", path=processed_index_path)
    source = source or PrppgIfesSource(
        current_year=current_year,
        processed_urls=processed_urls,
    )
    transform = transform or EditalNormalizer()
    sink = sink or LocalJSONSink()

    logger.info("Starting PRPPG/IFES Editais Pipeline...")
    logger.info("Phase 1: Extraction")
    raw_data_list = source.read()

    if not raw_data_list:
        logger.warning("Extraction returned empty. Halting pipeline.")
        return

    logger.info("Extracted %s raw records.", len(raw_data_list))
    logger.info("Phase 2: Transformation (Parallel)")
    valid_domains = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_item = {
            executor.submit(transform.process, item): item
            for item in raw_data_list
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
    if valid_domains:
        sink.write(valid_domains)
        add_many(
            "prppg_ifes",
            [domain.link for domain in valid_domains],
            path=processed_index_path,
        )
        logger.info("Pipeline completed successfully.")
    else:
        logger.warning("No valid domains to sink. Pipeline finished with warnings.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()
