import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from dotenv import load_dotenv

from src.config import get_reference_year
from src.core.interfaces import ISource, ITransform, ISink
from src.components.sources.finep_source import FinepSource
from src.components.transforms.edital_normalizer import EditalNormalizer
from src.components.sinks.json_sink import LocalJSONSink
from src.domain.models import RawEdital, EditalDomain

load_dotenv()

logger = logging.getLogger(__name__)


def run_pipeline(
    source: Optional[ISource[RawEdital]] = None,
    transform: Optional[ITransform[RawEdital, EditalDomain]] = None,
    sink: Optional[ISink[EditalDomain]] = None,
    reference_year: Optional[int] = None,
    max_pages: Optional[int] = None,
) -> None:
    """
    Orquestra o ETL de chamadas públicas FINEP (extract → transform → sink).
    Por padrão usa FinepSource com ano de referência do ambiente (REFERENCE_YEAR)
    ou ano atual. Opcionalmente limita à primeira página com max_pages=1.
    """
    source = source or FinepSource(
        reference_year=reference_year or get_reference_year(),
        max_pages=max_pages,
    )
    transform = transform or EditalNormalizer()
    sink = sink or LocalJSONSink()

    logger.info("Starting FINEP Chamadas Públicas Pipeline...")

    # 1. Extract
    logger.info("Phase 1: Extraction")
    raw_data_list = source.read()

    if not raw_data_list:
        logger.warning("Extraction returned empty. Halting pipeline.")
        return

    logger.info("Extracted %s raw records.", len(raw_data_list))

    # 2. Transform
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
            except Exception as e:
                logger.error("Failed to transform item %s: %s", raw_item.title, e)

    logger.info(
        "Successfully transformed %s out of %s records.",
        len(valid_domains),
        len(raw_data_list),
    )

    # 3. Load
    logger.info("Phase 3: Load/Sink")
    if valid_domains:
        sink.write(valid_domains)
        logger.info("Pipeline completed successfully.")
    else:
        logger.warning("No valid domains to sink. Pipeline finished with warnings.")


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    # Por padrão roda só a primeira página (teste). Use --all para todas as páginas.
    run_pipeline(max_pages=1 if "--all" not in sys.argv else None)
