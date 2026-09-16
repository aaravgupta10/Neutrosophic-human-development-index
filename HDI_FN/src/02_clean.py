"""
Step 2 of the pipeline: harmonise iso3, units, years; merge the digital
and Gini interim files into a single country-level analysis panel.

- Standardises on ISO-3 throughout (Step 4.2 pitfall: don't mix ISO-2/ISO-3).
  digital_interim.csv carries no iso3 column, so it is joined to
  gini_interim.csv on the country name (both files share identical name
  strings), which does carry iso3.
- Keeps raw units (percentages, per-100 subscriptions) untouched here;
  no rescaling happens in this script (Step 4.2 pitfall) — that is
  03_compute.py's job.
"""
import sys
import pandas as pd
from config import INTERIM_DIR, PROCESSED_DIR, RAW_DIR

DIGITAL_YEAR_DEFAULT = 2023
EGDI_YEAR = 2024


def main():
    digital = pd.read_csv(INTERIM_DIR / "digital_interim.csv")
    gini = pd.read_csv(INTERIM_DIR / "gini_interim.csv")
    country_meta = pd.read_csv(INTERIM_DIR / "country_meta_interim.csv")

    # --- join digital <-> gini on country name to recover iso3 ---
    merged = digital.merge(
        gini[["iso3", "country", "year_used", "gini", "gini_se", "source"]],
        left_on="Country",
        right_on="country",
        how="left",
        validate="one_to_one",
    )

    unmatched = merged[merged["iso3"].isna()]["Country"].tolist()
    if unmatched:
        print(f"[02_clean] WARNING: {len(unmatched)} countries could not be "
              f"matched to an iso3 code via the Gini file: {unmatched}")

    merged = merged.drop(columns=["country"]).rename(columns={
        "Country": "country",
        "Region": "region",
        "Internet_Pen_2023_Pct": "internet_pen",
        "Fixed_Broadband_2023_per100": "broadband_per100",
        "EGDI_2024": "egdi_2024",
        "HiTech_Exports_Pct": "hitech_exports_pct",
        "Audit_Notes": "digital_audit_notes",
        "year_used": "gini_year",
        "source": "gini_source",
    })

    # Documented exceptions to the 2023 reference year (Step 1.2): rows
    # whose own audit note says a later year was substituted.
    merged["digital_year_used"] = DIGITAL_YEAR_DEFAULT
    later_year_mask = merged["digital_audit_notes"].str.contains(
        "2024 data", case=False, na=False
    )
    merged.loc[later_year_mask, "digital_year_used"] = 2024

    # --- attach WB income group / region for reference (not used in scoring) ---
    merged = merged.merge(
        country_meta[["iso3", "wb_income_group"]], on="iso3", how="left"
    )

    ordered_cols = [
        "iso3", "country", "region", "wb_income_group",
        "digital_year_used", "internet_pen", "broadband_per100",
        "egdi_2024", "hitech_exports_pct", "digital_audit_notes",
        "gini_year", "gini", "gini_se", "gini_source",
    ]
    merged = merged[ordered_cols]

    n_missing_hitech = merged["hitech_exports_pct"].isna().sum()
    n_countries = len(merged)
    print(f"[02_clean] merged panel: {n_countries} countries, "
          f"{n_missing_hitech} with missing hitech_exports_pct")

    out_path = PROCESSED_DIR / "hdi_fn_panel_2023.csv"
    merged.to_csv(out_path, index=False)
    print(f"[02_clean] wrote {out_path}")

    # Also emit the audited files as analysis-ready processed files
    # (numeric types coerced, "Missing" -> NaN). 03_compute.py reads
    # these two paths verbatim, per the Phase 3 specification.
    digital_processed = pd.read_csv(INTERIM_DIR / "digital_interim.csv")
    digital_processed.to_csv(PROCESSED_DIR / "digital_raw_2023.csv", index=False)
    gini_processed = pd.read_csv(INTERIM_DIR / "gini_interim.csv")
    gini_processed.to_csv(PROCESSED_DIR / "gini_clean_2023_updated.csv", index=False)
    print(f"[02_clean] wrote {PROCESSED_DIR / 'digital_raw_2023.csv'}")
    print(f"[02_clean] wrote {PROCESSED_DIR / 'gini_clean_2023_updated.csv'}")

    # --- Clean shadow_economy.csv (raw file has flag emoji prefixes,
    #     a sub-header row, and 131 countries; we need clean names and
    #     just the 20 relevant to this study). ---
    shadow_raw_path = RAW_DIR / "shadow_economy.csv"
    if shadow_raw_path.exists():
        shadow = pd.read_csv(shadow_raw_path, skiprows=[1])  # skip units sub-header
        # Strip flag emoji + surrounding whitespace from Country
        shadow["Country"] = (
            shadow["Country"]
            .astype(str)
            .str.replace(r"^[^\w]+", "", regex=True)   # leading non-word chars (emoji)
            .str.strip()
        )
        # Reconcile naming with the digital/Gini panels
        shadow["Country"] = shadow["Country"].replace({"Korea": "South Korea"})
        shadow = shadow[["Country", "Shadow Economy"]]
        shadow["Shadow Economy"] = pd.to_numeric(shadow["Shadow Economy"], errors="coerce")

        study_countries = digital_processed["Country"].tolist()
        shadow_study = shadow[shadow["Country"].isin(study_countries)]
        missing = set(study_countries) - set(shadow_study["Country"])
        if missing:
            print(f"[02_clean] WARNING: shadow_economy.csv missing rows for: {sorted(missing)}")
        shadow_study.to_csv(PROCESSED_DIR / "shadow_economy.csv", index=False)
        print(f"[02_clean] wrote {PROCESSED_DIR / 'shadow_economy.csv'} "
              f"({len(shadow_study)}/{len(study_countries)} study countries matched)")

    # --- Pass through undp_hdi_2023.csv if present (used by Table 4) ---
    undp_raw_path = RAW_DIR / "undp_hdi_2023.csv"
    if undp_raw_path.exists():
        undp = pd.read_csv(undp_raw_path)
        undp.to_csv(PROCESSED_DIR / "undp_hdi_2023.csv", index=False)
        print(f"[02_clean] wrote {PROCESSED_DIR / 'undp_hdi_2023.csv'}")
    else:
        print(f"[02_clean] NOTE: data/raw/undp_hdi_2023.csv not present; "
              f"Table 4 will be emitted as headers-only until it is added.")


if __name__ == "__main__":
    sys.exit(main())
