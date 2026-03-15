import hashlib
import json
import os
import logging
from typing import List
from dataclasses import asdict
from src.core.interfaces import ISink
from src.domain.models import EditalDomain

logger = logging.getLogger(__name__)


def key_from_nome(nome: str, fallback: str = "edital_anonimo") -> str:
    """
    Same key used for the output filename base (no extension).
    Use this to build the processed index key for FAPES so source and sink stay in sync.
    """
    keepcharacters = (" ", ".", "_", "-")
    base = "".join(c for c in nome if c.isalnum() or c in keepcharacters).rstrip()
    if not base:
        return fallback
    if len(base) > 150:
        base = f"{base[:140]}_{hashlib.md5(nome.encode()).hexdigest()[:6]}"
    return base.replace(" ", "_").lower()


class LocalJSONSink(ISink[EditalDomain]):
    """
    Persists valid editais into JSON files in the local filesystem.
    """

    def __init__(self, output_dir: str = "data/output"):
        self.output_dir = output_dir

    def _sanitize_filename(self, filename: str) -> str:
        """Removes invalid characters from a string to build a safe filename."""
        keepcharacters = (" ", ".", "_", "-")
        return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

    def basename_for(self, item: EditalDomain, index: int = 1) -> str:
        """Base filename (no .json) for this item; same logic as write() for the processed index."""
        base_name = self._sanitize_filename(item.nome)
        if not base_name:
            base_name = f"edital_anonimo_{index}"
        if len(base_name) > 150:
            base_name = f"{base_name[:140]}_{hashlib.md5(item.nome.encode()).hexdigest()[:6]}"
        return base_name.replace(" ", "_").lower()

    def write(self, items: List[EditalDomain]) -> None:
        if not items:
            logger.warning("No items to persist.")
            return
            
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        for idx, item in enumerate(items, start=1):
            base_name = self.basename_for(item, index=idx)
            filename = f"{base_name}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(asdict(item), f, ensure_ascii=False, indent=4)
                logger.debug(f"Saved {filepath}")
            except Exception as e:
                logger.error(f"Failed to write {filepath}: {e}")
                # Continuing the loop per pipeline fault-tolerance
                continue
                
        logger.info(f"Successfully persisted {len(items)} editais to {self.output_dir}")
