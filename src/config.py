"""
Configuration used by sources and pipeline.
Centralizes environment-based variables (e.g. reference year for deadline filtering).
"""

import os
from datetime import datetime
from typing import Optional


def get_reference_year(override: Optional[int] = None) -> int:
    """
    Returns the reference year used to filter editais by deadline.
    Only chamadas whose "Prazo para envio de propostas" ends in this year
    or in the next year are included.

    Priority:
        1. override (e.g. passed to FinepSource)
        2. REFERENCE_YEAR env var (integer)
        3. Current calendar year

    Returns:
        Reference year (e.g. 2026).
    """
    if override is not None:
        return override
    raw = os.getenv("REFERENCE_YEAR", "").strip()
    if raw:
        try:
            return int(raw)
        except ValueError:
            pass
    return datetime.now().year
