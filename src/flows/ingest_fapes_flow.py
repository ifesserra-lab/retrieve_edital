import logging
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from src.core.interfaces import ISource, ITransform, ISink
from src.components.sources.fapes_source import FapesSource
from src.components.transforms.edital_normalizer import EditalNormalizer
from src.components.sinks.json_sink import LocalJSONSink
from src.domain.models import RawEdital, EditalDomain
from src.flow_health import emit_flow_stats
from src.processed_store import get_keys_set, add_many, DEFAULT_PATH

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def _processed_keys(editais) -> list:
    """
    Registra a URL do edital **e** as dos seus anexos.

    O FapesSource agrupa os documentos de um edital e elege um como principal
    conforme a classificação do Mistral, que varia entre execuções. Registrar só
    a URL do principal fazia a chave mudar de uma rodada para a outra: o mesmo
    edital voltava como novo, era reprocessado por OCR e sobrescrevia o arquivo
    anterior. Guardando todas as URLs do grupo, qualquer documento que reapareça
    identifica o edital já coletado.
    """
    keys: list = []
    for edital in editais:
        if edital.link:
            keys.append(edital.link)
        for anexo in edital.anexos or []:
            link = (anexo.get("link") or "").strip()
            if link:
                keys.append(link)
    return keys


def run_pipeline(
    source: ISource[RawEdital] = None,
    transform: ITransform[RawEdital, EditalDomain] = None,
    sink: ISink[EditalDomain] = None,
    processed_index_path: str = DEFAULT_PATH,
) -> None:
    """
    Orchestrates the ETL execution injecting dependencies.
    Uses processed_editais.json to skip already-processed editais.
    """
    # A FAPES deduplica por URL do documento, como as demais fontes. Antes a
    # chave era o nome do arquivo, que vem do nome reescrito pelo Mistral e não
    # do título da página — as duas chaves não fechavam, e os mesmos editais
    # voltavam a cada execução consumindo OCR.
    processed_urls = get_keys_set("fapes", path=processed_index_path)
    source = source or FapesSource(processed_urls=processed_urls)
    transform = transform or EditalNormalizer()
    sink = sink or LocalJSONSink()
    
    logger.info("Starting Retrieve Edital Pipeline...")
    
    # 1. Extract
    logger.info("Phase 1: Extraction")
    raw_data_list = source.read()

    # Quantos itens a origem devolveu antes da deduplicação: é o que
    # permite ao runner separar "portal sem novidade" de "source quebrado".
    listing_count = getattr(source, "last_listing_count", len(raw_data_list))
    
    if not raw_data_list:
        emit_flow_stats(raw_count=listing_count, new_count=0)
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
    # Emitido antes do sink, e fora do `if`: quando a origem responde mas todos
    # os itens são rejeitados pelas regras de publicação, o runner precisa saber
    # que a origem respondeu. Dentro do `if`, esse caso não emitia nada e o
    # runner caía no proxy de sequência — o falso alarme que as estatísticas
    # existem para evitar.
    emit_flow_stats(raw_count=listing_count, new_count=len(valid_domains))
    if valid_domains:
        persisted = sink.write(valid_domains)
        add_many(
            "fapes",
            _processed_keys(persisted.values()),
            path=processed_index_path,
        )
        logger.info("Pipeline completed successfully.")
    else:
        logger.warning("No valid domains to sink. Pipeline finished with warnings.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()
