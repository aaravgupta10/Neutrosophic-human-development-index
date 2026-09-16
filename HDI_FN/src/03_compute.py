"""
Step 3 of the pipeline: build I_digital, HDI-FN dimension score, and the
neutrosophic disparity scores S_bal and S_int.

Formulas (Phase 3 specification):

  Digital dimension
    I_penetration    = Internet_Pen_2023_Pct / 100
    I_broadband      = Fixed_Broadband_2023_per100 / max(Fixed_Broadband_2023_per100)
    F_egov           = 1 - I_penetration                  # citizen non-penetration
    T_egov_adjusted  = EGDI_2024 * (1 - F_egov)
    I_hitech         = HiTech_Exports_Pct / max(HiTech_Exports_Pct)
    I_digital        = (I_penetration * I_broadband * T_egov_adjusted * I_hitech) ** (1/4)
                       # geometric mean; 0-values floored at 0.001 to avoid collapse

  Neutrosophic disparity (Part 5)
    T_x    = gini / 100                    # formal-sector inequality (Truth)
    I_x    = Shadow Economy / 100          # informal-sector share (Indeterminacy)
    S_bal  = (T_x + (1 - I_x)) / 2         # balance term
    S_int  = T_x * (1 - I_x)               # interaction term
"""
import sys
import numpy as np
import pandas as pd
from config import PROCESSED_DIR, RAW_DIR, SEED

np.random.seed(SEED)


def compute_metrics():
    # 1. Load the clean datasets generated in Phase 1 & 2
    df_digital = pd.read_csv(PROCESSED_DIR / "digital_raw_2023.csv")
    df_gini = pd.read_csv(PROCESSED_DIR / "gini_clean_2023_updated.csv")
    df_shadow = pd.read_csv(PROCESSED_DIR / "shadow_economy.csv")  # cleaned in 02_clean.py

    # --- A. DIGITAL DIMENSION CALCULATIONS ---
    # Normalizing inputs to 0-1 scale
    df_digital["I_penetration"] = df_digital["Internet_Pen_2023_Pct"] / 100
    df_digital["I_broadband"] = (
        df_digital["Fixed_Broadband_2023_per100"]
        / df_digital["Fixed_Broadband_2023_per100"].max()
    )

    # EGDI Adjusted for Citizen Non-Penetration (F)
    df_digital["F_egov"] = 1 - df_digital["I_penetration"]
    df_digital["T_egov_adjusted"] = df_digital["EGDI_2024"] * (1 - df_digital["F_egov"])

    # Hi-Tech Normalization (Bangladesh HiTech_Exports_Pct is NaN per audit rules
    # -- dropped from the digital panel per Step 1.3 "insufficient coverage" rule
    # after propagating through this division.)
    df_digital["I_hitech"] = (
        df_digital["HiTech_Exports_Pct"] / df_digital["HiTech_Exports_Pct"].max()
    )

    # Composite Digital Dimension (I_digital) - Geometric Mean (4th root)
    # Adding a nominal floor (0.001) to prevent 0-value geometric mean collapse
    # (e.g., Burkina Faso, Nepal on I_hitech).
    df_digital["I_hitech"] = df_digital["I_hitech"].replace(0, 0.001)
    df_digital["I_broadband"] = df_digital["I_broadband"].replace(0, 0.001)

    df_digital["I_digital"] = (
        df_digital["I_penetration"]
        * df_digital["I_broadband"]
        * df_digital["T_egov_adjusted"]
        * df_digital["I_hitech"]
    ) ** (1 / 4)

    # --- B. NEUTROSOPHIC DISPARITY CALCULATIONS (Part 5) ---
    # Merge Gini (T) and Shadow Economy (I) on country name.
    df_disparity = pd.merge(
        df_gini, df_shadow, left_on="country", right_on="Country", how="inner"
    )

    if df_disparity.empty:
        print("[03_compute] WARNING: shadow_economy.csv contains no matching rows; "
              "disparity output will be empty. Fill in Shadow Economy values from a "
              "primary source (e.g. Medina & Schneider, IMF WP/18/17) and re-run.")

    # Convert to 0-1 Neutrosophic Truth (T) and Indeterminacy (I) scales
    df_disparity["T_x"] = df_disparity["gini"] / 100
    df_disparity["I_x"] = df_disparity["Shadow Economy"] / 100

    # Calculate Disparity Scores
    df_disparity["S_bal"] = (df_disparity["T_x"] + (1 - df_disparity["I_x"])) / 2
    df_disparity["S_int"] = df_disparity["T_x"] * (1 - df_disparity["I_x"])

    # Save processed files for the tables script
    df_digital.to_csv(PROCESSED_DIR / "computed_digital.csv", index=False)
    df_disparity.to_csv(PROCESSED_DIR / "computed_disparity.csv", index=False)
    print("[03_compute] 03_compute.py executed successfully. Computations saved.")
    print(f"[03_compute] digital rows: {len(df_digital)}, "
          f"disparity rows: {len(df_disparity)}")

    # --- C. HDI-FN PREVIEW (Part 6 / Table 4) ---
    # undp_hdi_2023.csv supplies the three UNDP sub-indices directly
    # (I_health, I_education, I_income_adj), extracted from the Part 6
    # Table 4 reference dataset. These are pre-normalised 0-1 values; no
    # goalpost recomputation is needed here.
    #
    # HDI_FN = (I_health * I_education * I_income_adj * I_digital) ** (1/4)
    undp_path = PROCESSED_DIR / "undp_hdi_2023.csv"
    if not undp_path.exists():
        print("[03_compute] SKIP HDI-FN: data/raw/undp_hdi_2023.csv not supplied "
              "(Table 4 will emit headers only).")
        return

    df_undp = pd.read_csv(undp_path)

    df_hdi_fn = df_digital[["Country", "Region", "I_digital"]].merge(
        df_undp, on="Country", how="left"
    )
    df_hdi_fn["HDI_FN"] = (
        df_hdi_fn["I_health"]
        * df_hdi_fn["I_education"]
        * df_hdi_fn["I_income_adj"]
        * df_hdi_fn["I_digital"]
    ) ** (1 / 4)

    df_hdi_fn.to_csv(PROCESSED_DIR / "computed_hdi_fn.csv", index=False)
    print(f"[03_compute] wrote {PROCESSED_DIR / 'computed_hdi_fn.csv'} "
          f"({df_hdi_fn['HDI_FN'].notna().sum()}/{len(df_hdi_fn)} countries scored)")


if __name__ == "__main__":
    sys.exit(compute_metrics())
