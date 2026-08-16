import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from dotenv import load_dotenv

from src.components.sinks.json_sink import LocalJSONSink
from src.components.sources.confap_source import ConfapSource
from src.components.transforms.edital_normalizer import EditalNormalizer
from src.core.interfaces import ISink, ISource, ITransform
from src.domain.models import EditalDomain, RawEdital
from src.flow_health import emit_flow_stats
from src import rejection_store
from src.processed_store import DEFAULT_PATH, add_many, get_keys_set
from src.components.transforms.mistral_client import MistralUnavailableError
from src.components.transforms.extraction_contract import ExtractionUnavailableError

load_dotenv()

logger = logging.getLogger(__name__)


def run_pipeline(
    source: Optional[ISource[RawEdital]] = None,
    transform: Optional[ITransform[RawEdital, EditalDomain]] = None,
    sink: Optional[ISink[EditalDomain]] = None,
    processed_index_path: str = DEFAULT_PATH,
) -> None:
    """
    Orquestra o ETL das chamadas de cooperação internacional do CONFAP.

    Deduplicação pela URL da página de detalhe, que é estável (id + slug).
    """
    processed_urls = get_keys_set("confap", path=processed_index_path)
    # Recusas ainda válidas contam como já vistas: sem isso, um edital
    # que o portão rejeitou volta como novo em toda execução, com PDF
    # baixado e OCR refeito só para ser rejeitado de novo.
    processed_urls = processed_urls | rejection_store.get_active_keys("confap")
    source = source or ConfapSource(processed_urls=processed_urls)
    transform = transform or EditalNormalizer()
    sink = sink or LocalJSONSink()

    logger.info("Starting CONFAP Pipeline...")
    logger.info("Phase 1: Extraction")
    raw_data_list = source.read()

    # Quantas chamadas a origem devolveu antes da deduplicação: é o que permite
    # ao runner distinguir "portal sem novidade" de "source quebrado".
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
            except ExtractionUnavailableError:
                # Conta Mistral recusada mata a extração inteira, não um item.
                # Engolir aqui fazia o fluxo terminar verde sem edital algum.
                raise
            except Exception as exc:
                logger.error("Failed to transform item %s: %s", raw_item.title, exc)

    logger.info(
        "Successfully transformed %s out of %s records.",
        len(valid_domains),
        len(raw_data_list),
    )

    logger.info("Phase 3: Load/Sink")
    emit_flow_stats(raw_count=listing_count, new_count=len(valid_domains))
    rejection_store.record("confap", getattr(transform, "rejections", {}))

    if valid_domains:
        persisted = sink.write(valid_domains)
        add_many(
            "confap",
            [d.link for d in persisted.values()],
            path=processed_index_path,
        )
        logger.info("Pipeline completed successfully.")
    else:
        logger.warning("No valid domains to sink. Pipeline finished with warnings.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()
