import logging
import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from src.core.interfaces import ISource, ITransform, ISink
from src.components.sources.fapes_source import FapesSource
from src.components.transforms.edital_normalizer import EditalNormalizer
from src.components.sinks.json_sink import LocalJSONSink
from src.domain.models import RawEdital, EditalDomain

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def run_pipeline(
    source: ISource[RawEdital] = None,
    transform: ITransform[RawEdital, EditalDomain] = None,
    sink: ISink[EditalDomain] = None
) -> None:
    """
    Orchestrates the ETL execution injecting dependencies.
    """
    processed_titles = set()
    output_dir = "data/output"
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith(".json"):
                processed_titles.add(file.replace(".json", ""))

    source = source or FapesSource(processed_titles=processed_titles)
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
    logger.info("Phase 2: Transformation (Parallel)")
    valid_domains = []
    
    # Use ThreadPoolExecutor to parallelize Mistral API calls
    # max_workers=2 is a safe default to avoid aggressive rate limiting
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Map transform.process to the list of raw items
        future_to_item = {executor.submit(transform.process, item): item for item in raw_data_list}
        
        for future in future_to_item:
            raw_item = future_to_item[future]
            try:
                domain_item = future.result()
                if domain_item:
                    valid_domains.append(domain_item)
            except Exception as e:
                logger.error(f"Failed to transform item {raw_item.title}: {e}")
            
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
