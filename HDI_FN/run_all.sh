#!/usr/bin/env bash
# Reproduces every numerical table in the paper from data/raw/ on a clean
# checkout. Per Step 3.2 of the audit procedure: no manual steps required.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if python3 -c "import sys" >/dev/null 2>&1; then
    PYTHON=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -c "import sys" >/dev/null 2>&1; then
    # Windows Python launcher support. This also avoids the Microsoft Store
    # python3 placeholder, which can exist on PATH without an interpreter.
    PYTHON=(py -3)
elif python -c "import sys" >/dev/null 2>&1; then
    PYTHON=(python)
else
    echo "ERROR: Python 3 is required. Install Python 3.10+ and ensure python3, py -3, or python is usable." >&2
    exit 1
fi

required_raw=(
    "data/raw/swiid_summary.csv"
    "data/raw/individuals-using-the-internet_.csv"
    "data/raw/fixed-broadband-subscriptions.csv"
    "data/raw/high-technology-exports-1.csv"
    "data/raw/shadow_economy.csv"
    "data/raw/undp_hdi_2023.csv"
    "data/raw/digital_raw_2023.csv"
)
for file in "${required_raw[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "ERROR: Required tracked raw input is missing: $file" >&2
        exit 1
    fi
done

# Install pinned deps. Skip if they're already importable; don't halt
# the pipeline on install errors (e.g. PEP 668 externally-managed envs) --
# if imports subsequently fail, the script errors on its own with a clear
# traceback pointing at requirements.txt.
if ! "${PYTHON[@]}" -c "import pandas, numpy" 2>/dev/null; then
    "${PYTHON[@]}" -m pip install -q -r requirements.txt || \
        "${PYTHON[@]}" -m pip install -q --user -r requirements.txt || \
        echo "WARN: pip install failed; assuming deps are already installed."
fi

cd src
"${PYTHON[@]}" 00_build_gini.py
"${PYTHON[@]}" 00_build_digital.py
"${PYTHON[@]}" 01_ingest.py
"${PYTHON[@]}" 02_clean.py
"${PYTHON[@]}" 03_compute.py
"${PYTHON[@]}" 04_tables.py
"${PYTHON[@]}" 05_robustness.py
"${PYTHON[@]}" 06_table5_ab.py
"${PYTHON[@]}" 07_tiva_subset.py

echo ""
echo "Done. Tables 1, 2, 3, 4, 5 written to output/."
