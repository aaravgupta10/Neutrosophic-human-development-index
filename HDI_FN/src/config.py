"""
Shared configuration for the HDI_FN replication pipeline.
Per the audit procedure (Step 3.2): a single fixed seed, declared once,
used by every script that touches any stochastic procedure.
"""
from pathlib import Path

SEED = 20260101

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
INTERIM_DIR = ROOT / "data" / "interim"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "output"
DOCS_DIR = ROOT / "docs"

REFERENCE_YEAR = 2023          # all digital indicators, per Step 1.2
EGDI_YEAR = 2024                # documented exception, biennial release cycle
CARRY_FORWARD_WINDOW = (2020, 2023)  # Step 1.3

for d in (INTERIM_DIR, PROCESSED_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)
