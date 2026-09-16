"""
Step 4 of the pipeline: emit Tables 1-3 and Table 5 as CSV.

Per the audit procedure: "never hand-type numbers into the manuscript".
Every value in these tables is regenerated from data/raw/ on each run.

Table layout follows the Phase 3 specification:
  Table 1  - Raw Digital Metrics
  Table 2  - EGDI Neutrosophic Gap (T = raw EGDI, F = non-penetration, T adjusted)
  Table 3  - Composite Digital Dimension (sub-scores + I_digital, ranked)
  Table 5  - Neutrosophic Disparity Scores (T_x, I_x, S_bal, S_int, ranked by S_int)

Table 4 is not defined in the Phase 3 spec supplied and is intentionally not
emitted here. When its layout is finalised, add a table_4 block below.
"""
import sys
import pandas as pd
from config import PROCESSED_DIR, OUTPUT_DIR


def generate_tables():
    # Load the computed data
    df_digital = pd.read_csv(PROCESSED_DIR / "computed_digital.csv")
    df_disparity = pd.read_csv(PROCESSED_DIR / "computed_disparity.csv")

    # Table 1: Raw Digital Metrics.
    # Includes Audit_Notes (year-used / carry-forward / missing flags) so the
    # published table is self-documenting per audit §1.2-1.3 -- a reviewer can
    # see which cells are 2023 vs. carried-forward without opening interim files.
    table_1 = df_digital[["Country", "Region", "Internet_Pen_2023_Pct",
                          "Fixed_Broadband_2023_per100", "EGDI_2024",
                          "HiTech_Exports_Pct", "Audit_Notes"]]
    table_1.to_csv(OUTPUT_DIR / "Table_1_Raw_Digital.csv", index=False)

    # Table 2: EGDI Neutrosophic Gap
    table_2 = df_digital[["Country", "EGDI_2024", "F_egov", "T_egov_adjusted"]]
    table_2 = table_2.rename(columns={
        "EGDI_2024": "Raw EGDI (T)",
        "F_egov": "Non-Penetration (F)",
    })
    table_2.to_csv(OUTPUT_DIR / "Table_2_EGDI_Neutrosophic.csv", index=False)

    # Table 3: Composite Digital Dimension (I_digital), ranked
    table_3 = df_digital[["Country", "I_penetration", "I_broadband",
                          "T_egov_adjusted", "I_hitech", "I_digital"]]
    table_3 = table_3.sort_values(by="I_digital", ascending=False)
    table_3.to_csv(OUTPUT_DIR / "Table_3_Composite_Digital.csv", index=False)

    # Table 4: HDI-FN Preview (Part 6 layout)
    hdi_fn_path = PROCESSED_DIR / "computed_hdi_fn.csv"
    table_4_cols = [
        "Country", "Region", "I_health", "I_education", "I_income_adj (approx.)",
        "I_digital", "HDI_FN Score", "HDI_FN Rank",
        "Standard HDI Score", "Standard HDI Rank", "Rank Change (±)",
        "Excluded (reason)",
    ]
    if hdi_fn_path.exists():
        df_hdi_fn = pd.read_csv(hdi_fn_path)
        df_hdi_fn["Excluded (reason)"] = df_hdi_fn["HDI_FN"].apply(
            lambda v: "" if pd.notna(v) else
            "Hi-Tech Exports missing in 2020-2023 SWIID/WDI window (Step 1.3); "
            "I_digital and HDI_FN not computed for this country, not silently blank"
        )
        # Within-sample ranks (1 = highest score); NaN scores get NaN ranks
        df_hdi_fn["HDI_FN Rank"] = df_hdi_fn["HDI_FN"].rank(
            ascending=False, method="min"
        ).astype("Int64")
        df_hdi_fn["Standard HDI Rank"] = df_hdi_fn["standard_hdi_score"].rank(
            ascending=False, method="min"
        ).astype("Int64")
        # Positive Rank Change = climbed vs. standard HDI (better under HDI-FN)
        df_hdi_fn["Rank Change (±)"] = (
            df_hdi_fn["Standard HDI Rank"] - df_hdi_fn["HDI_FN Rank"]
        )
        table_4 = df_hdi_fn.rename(columns={
            "I_income_adj": "I_income_adj (approx.)",
            "HDI_FN": "HDI_FN Score",
            "standard_hdi_score": "Standard HDI Score",
        })[table_4_cols].sort_values(by="HDI_FN Rank")
        table_4.to_csv(OUTPUT_DIR / "Table_4_HDI_FN_Preview.csv", index=False)
        print(f"[04_tables] Table 4 emitted with "
              f"{table_4['HDI_FN Score'].notna().sum()}/{len(table_4)} scored countries.")
    else:
        pd.DataFrame(columns=table_4_cols).to_csv(
            OUTPUT_DIR / "Table_4_HDI_FN_Preview.csv", index=False
        )
        print("[04_tables] WARNING: computed_hdi_fn.csv absent; Table 4 emitted "
              "with headers only. Add data/raw/undp_hdi_2023.csv and re-run.")

    # Table 5: Neutrosophic Disparity Score Table (S_int and S_bal)
    if df_disparity.empty:
        # Preserve the schema so downstream consumers don't break, but flag it.
        table_5 = pd.DataFrame(columns=[
            "Country", "Formal Gini (T)", "Gini SE (reported, not modeled)",
            "Shadow Econ (I)", "S_bal", "S_int",
        ])
        print("[04_tables] WARNING: computed_disparity.csv is empty; "
              "Table 5 emitted with headers only. Populate shadow_economy.csv "
              "with primary-source MIMIC values and re-run.")
    else:
        table_5 = df_disparity[["Country", "T_x", "gini_se", "I_x", "S_bal", "S_int"]]
        table_5 = table_5.rename(columns={
            "T_x": "Formal Gini (T)",
            "gini_se": "Gini SE (reported, not modeled)",
            "I_x": "Shadow Econ (I)",
        })
        table_5 = table_5.sort_values(by="S_int", ascending=False)
    table_5.to_csv(OUTPUT_DIR / "Table_5_Disparity_Scores.csv", index=False)

    print(f"[04_tables] 04_tables.py executed successfully. "
          f"Tables 1-3 and Table 5 emitted to {OUTPUT_DIR}/.")


if __name__ == "__main__":
    sys.exit(generate_tables())
