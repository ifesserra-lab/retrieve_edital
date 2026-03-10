import json
import os
import logging
from typing import List
from dataclasses import asdict
from src.core.interfaces import ISink
from src.domain.models import EditalDomain

logger = logging.getLogger(__name__)

class LocalJSONSink(ISink[EditalDomain]):
    """
    Persists valid editais into JSON files in the local filesystem.
    """
    
    def __init__(self, output_dir: str = "data/output"):
        self.output_dir = output_dir
        
    def _sanitize_filename(self, filename: str) -> str:
        """Removes invalid characters from a string to build a safe filename."""
        keepcharacters = (' ', '.', '_', '-')
        return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

    def write(self, items: List[EditalDomain]) -> None:
        if not items:
            logger.warning("No items to persist.")
            return
            
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        for idx, item in enumerate(items, start=1):
            base_name = self._sanitize_filename(item.nome)
            if not base_name:
                base_name = f"edital_anonimo_{idx}"
            
            # Truncate and add hash if too long to avoid collisions and FS errors
            if len(base_name) > 150:
                import hashlib
                name_hash = hashlib.md5(item.nome.encode()).hexdigest()[:6]
                base_name = f"{base_name[:140]}_{name_hash}"
            
            # Use lower-case robust naming
            filename = f"{base_name.replace(' ', '_').lower()}.json"
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
