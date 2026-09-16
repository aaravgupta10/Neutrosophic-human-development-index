"""
Step 1 of the pipeline: read raw, write interim.

Reads the audited indicator files (data/raw/digital_raw_2023.csv,
data/raw/gini_clean_2023_updated.csv) plus the supporting primary-source
downloads (WDI high-tech exports, ITU internet penetration, WB country
metadata) that back those audited values.

Never edits data/raw/. Writes one interim file per source to data/interim/.
"""
import sys
import pandas as pd
from config import RAW_DIR, INTERIM_DIR

MISSING_TOKENS = {"Missing", "missing", "", "NA", "N/A"}


def load_digital_raw() -> pd.DataFrame:
    """Prefer the freshly-built digital panel (00_build_digital.py, run
    from raw ITU/WDI downloads) over the hand-delivered CSV -- confirmed
    cell-by-cell that digital_raw_2023.csv still carried pre-audit ^
    fallback estimates for most Hi-Tech and about half the Internet cells."""
    built_path = INTERIM_DIR / "digital_raw_2023_built.csv"
    if built_path.exists():
        path = built_path
        print(f"[01_ingest] using freshly-built {path.name} (from ITU/WDI raw downloads)")
    else:
        path = RAW_DIR / "digital_raw_2023.csv"
        print(f"[01_ingest] WARNING: {built_path.name} not found -- "
              f"falling back to hand-delivered {path.name}. "
              f"Run 00_build_digital.py first for full reproducibility.")
    df = pd.read_csv(path)
    for col in ["Internet_Pen_2023_Pct", "Fixed_Broadband_2023_per100",
                "EGDI_2024", "HiTech_Exports_Pct"]:
        df[col] = df[col].replace(list(MISSING_TOKENS), pd.NA)
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_gini_clean() -> pd.DataFrame:
    """Prefer the freshly-built Gini file (00_build_gini.py, run from the
    raw SWIID download) over the hand-delivered CSV -- Phase 2 update:
    the raw SWIID file supersedes the earlier standalone deliverable."""
    built_path = INTERIM_DIR / "gini_clean_2023_built.csv"
    if built_path.exists():
        path = built_path
        print(f"[01_ingest] using freshly-built {path.name} (from swiid_summary.csv)")
    else:
        path = RAW_DIR / "gini_clean_2023_updated.csv"
        print(f"[01_ingest] WARNING: {built_path.name} not found -- "
              f"falling back to hand-delivered {path.name}. "
              f"Run 00_build_gini.py first for full reproducibility.")
    df = pd.read_csv(path)
    df["gini"] = pd.to_numeric(df["gini"], errors="coerce")
    df["gini_se"] = pd.to_numeric(df["gini_se"], errors="coerce")
    df["year_used"] = pd.to_numeric(df["year_used"], errors="coerce").astype("Int64")
    return df


def load_country_metadata() -> pd.DataFrame:
    path = RAW_DIR / "metadata-country.csv"
    df = pd.read_csv(path)
    df = df.rename(columns={
        "Country Code": "iso3",
        "Region": "wb_region",
        "IncomeGroup": "wb_income_group",
        "TableName": "wb_country_name",
    })
    return df[["iso3", "wb_region", "wb_income_group", "wb_country_name"]]


def load_wdi_hitech_raw() -> pd.DataFrame:
    """WDI wide-format export, header starts on row 5 (0-indexed row 4)."""
    path = RAW_DIR / "high-technology-exports-1.csv"
    df = pd.read_csv(path, skiprows=4)
    return df


def load_itu_internet_raw() -> pd.DataFrame:
    """ITU DataHub long-format panel (seriesID, entityIso, dataValue, dataYear, ...)."""
    path = RAW_DIR / "individuals-using-the-internet_.csv"
    df = pd.read_csv(path)
    return df


def main():
    digital = load_digital_raw()
    gini = load_gini_clean()
    country_meta = load_country_metadata()
    wdi_hitech = load_wdi_hitech_raw()
    itu_internet = load_itu_internet_raw()

    digital.to_csv(INTERIM_DIR / "digital_interim.csv", index=False)
    gini.to_csv(INTERIM_DIR / "gini_interim.csv", index=False)
    country_meta.to_csv(INTERIM_DIR / "country_meta_interim.csv", index=False)
    # Keep the raw provenance panels around in interim, trimmed to columns
    # actually needed downstream, so 02_clean.py doesn't re-parse the
    # full multi-decade WDI/ITU panels.
    wdi_hitech.to_csv(INTERIM_DIR / "wdi_hitech_interim.csv", index=False)
    itu_internet.to_csv(INTERIM_DIR / "itu_internet_interim.csv", index=False)

    print(f"[01_ingest] digital_raw_2023.csv:        {len(digital)} rows")
    print(f"[01_ingest] gini_clean_2023_updated.csv:  {len(gini)} rows")
    print(f"[01_ingest] metadata-country.csv:         {len(country_meta)} rows")
    print(f"[01_ingest] WDI hi-tech exports (raw):    {len(wdi_hitech)} rows")
    print(f"[01_ingest] ITU internet panel (raw):     {len(itu_internet)} rows")

    missing_digital = digital.isna().sum()
    flagged = missing_digital[missing_digital > 0]
    if not flagged.empty:
        print("[01_ingest] NOTE: missing cells detected in digital_raw_2023.csv "
              "(expected, per audit notes column):")
        print(flagged.to_string())


if __name__ == "__main__":
    sys.exit(main())
