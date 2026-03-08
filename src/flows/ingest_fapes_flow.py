import logging
from src.core.interfaces import ISource, ITransform, ISink
from src.components.sources.fapes_source import FapesSource
from src.components.transforms.edital_normalizer import EditalNormalizer
from src.components.sinks.json_sink import LocalJSONSink
from src.domain.models import RawEdital, EditalDomain

logger = logging.getLogger(__name__)

def run_pipeline(
    source: ISource[RawEdital] = None,
    transform: ITransform[RawEdital, EditalDomain] = None,
    sink: ISink[EditalDomain] = None
) -> None:
    """
    Orchestrates the ETL execution injecting dependencies.
    """
    source = source or FapesSource()
    transform = transform or EditalNormalizer()
    sink = sink or LocalJSONSink()
    
    logger.info("Starting Retrieve Edital Pipeline...")
    
    # 1. Extract
    logger.info("Phase 1: Extraction")
    raw_data_list = source.read()
    
    if not raw_data_list:
        logger.warning("Extraction returned empty. Halting pipeline.")
        return
        
    logger.info(f"Extracted {len(raw_data_list)} raw records.")

    # 2. Transform
    logger.info("Phase 2: Transformation")
    valid_domains = []
    for count, raw_item in enumerate(raw_data_list, start=1):
        try:
            domain_item = transform.process(raw_item)
            valid_domains.append(domain_item)
        except Exception as e:
            logger.error(f"Failed to transform item {count} ({raw_item.title}): {e}")
            
    logger.info(f"Successfully transformed {len(valid_domains)} out of {len(raw_data_list)} records.")

    # 3. Load
    logger.info("Phase 3: Load/Sink")
    if valid_domains:
        sink.write(valid_domains)
        logger.info("Pipeline completed successfully.")
    else:
        logger.warning("No valid domains to sink. Pipeline finished with warnings.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()
