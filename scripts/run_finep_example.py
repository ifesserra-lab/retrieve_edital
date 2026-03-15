#!/usr/bin/env python3
"""
Exemplo: roda o pipeline ETL usando FinepSource (primeira página da listagem).
Uso (com dependências instaladas):
  python scripts/run_finep_example.py
  ou, da raiz do projeto: python -m scripts.run_finep_example
"""
import logging
import sys

# Garante que src está no path
sys.path.insert(0, ".")

from src.components.sources.finep_source import FinepSource
from src.flows.ingest_fapes_flow import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

if __name__ == "__main__":
    run_pipeline(source=FinepSource(reference_year=2026, max_pages=1))
