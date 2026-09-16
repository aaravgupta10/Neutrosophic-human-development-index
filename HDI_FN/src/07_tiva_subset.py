"""
07_tiva_subset.py
------------------
SUPERVISOR DECISION (received): keep the raw Philippines Hi-Tech Exports
figure (WDI TX.VAL.TECH.MF.ZS) in the main panel -- consistency across the
20-country panel matters more than country-specific accuracy. Discuss
re-export inflation as a limitation in methods, supported by a
supplementary table (Table Sx) comparing the raw gross-export figure
against OECD TiVA domestic value-added (EXGR_DVA).

This script builds Table_Sx_TiVA_Subset.csv from
data/raw/tiva_domestic_value_added.csv (OECD TiVA 2025 edition, EXGR_DVA,
% of gross exports). Two DVA columns are provided:
  - tiva_dva_hitech_C26_pct : domestic value-added share of exports in
    ISIC Rev.4 division C26 (Computer, electronic and optical products) --
    the TiVA activity that best matches WDI's "high-technology exports".
    This is the relevant figure for the re-export inflation discussion.
  - tiva_dva_total_pct : domestic value-added share of TOTAL exports, for
    context.

Coverage / year caveats (state these in the methods limitation):
  - TiVA covers 18 of the 20 panel countries. Nepal (NPL) and Burkina
    Faso (BFA) are NOT in the OECD ICIO/TiVA country set, so they have no
    row here. This is a genuine coverage gap, not an omission.
  - TiVA's latest year is 2022 (current 2025 edition, 1995-2022), whereas
    the main panel's Hi-Tech figure is 2023 WDI. This is a one-year
    mismatch analogous to the EGDI-2024 exception -- disclose it.

If data/raw/tiva_domestic_value_added.csv is absent, this step no-ops
cleanly so run_all.sh does not fail.
"""
import sys
import pandas as pd
from config import RAW_DIR, PROCESSED_DIR, OUTPUT_DIR

TIVA_FILENAME = "tiva_domestic_value_added.csv"


def main():
    tiva_path = RAW_DIR / TIVA_FILENAME
    if not tiva_path.exists():
        print(f"[07_tiva_subset] SKIP: {tiva_path} not found. Table Sx pending "
              f"-- download OECD TiVA EXGR_DVA and place it there, then re-run.")
        return 0

    tiva = pd.read_csv(tiva_path)
    digital = pd.read_csv(PROCESSED_DIR / "digital_raw_2023.csv")

    merged = digital[["Country", "HiTech_Exports_Pct"]].merge(
        tiva[["Country", "year", "tiva_dva_hitech_C26_pct", "tiva_dva_total_pct"]],
        on="Country", how="left",
    )
    merged = merged.rename(columns={
        "HiTech_Exports_Pct": "WDI_HiTech_Gross_Exports_Pct_2023",
        "year": "TiVA_year",
        "tiva_dva_hitech_C26_pct": "TiVA_DVA_HiTech_C26_Pct",
        "tiva_dva_total_pct": "TiVA_DVA_Total_Pct",
    })

    # Re-export inflation indicator: 100 minus the domestic value-added share
    # = the foreign / re-exported content share of C26 (high-tech) exports.
    merged["Foreign_Content_Share_C26_Pct"] = (
        100 - merged["TiVA_DVA_HiTech_C26_Pct"]
    ).round(2)

    # Flag countries whose high-tech exports are >40% foreign content
    # (i.e. where the raw WDI gross figure most overstates domestic capacity).
    merged["High_ReExport_Flag"] = merged["Foreign_Content_Share_C26_Pct"].apply(
        lambda v: "HIGH re-export/foreign content" if pd.notna(v) and v > 40 else ""
    )

    merged = merged.sort_values("Foreign_Content_Share_C26_Pct", ascending=False,
                                 na_position="last")

    supp_dir = OUTPUT_DIR / "supplementary"
    supp_dir.mkdir(exist_ok=True)
    merged.to_csv(supp_dir / "Table_Sx_TiVA_Subset.csv", index=False)

    n_cov = merged["TiVA_DVA_HiTech_C26_Pct"].notna().sum()
    missing = merged[merged["TiVA_DVA_HiTech_C26_Pct"].isna()]["Country"].tolist()
    print(f"[07_tiva_subset] wrote Table_Sx_TiVA_Subset.csv "
          f"({n_cov}/{len(merged)} countries with TiVA coverage; "
          f"no coverage: {missing}) to {supp_dir}/")

    phl = merged[merged["Country"] == "Philippines"]
    if not phl.empty:
        row = phl.iloc[0]
        print(f"[07_tiva_subset] Philippines: WDI gross hi-tech "
              f"{row['WDI_HiTech_Gross_Exports_Pct_2023']:.1f}% but only "
              f"{row['TiVA_DVA_HiTech_C26_Pct']:.1f}% domestic value-added "
              f"(C26, {int(row['TiVA_year'])}) -> "
              f"{row['Foreign_Content_Share_C26_Pct']:.1f}% foreign/re-export "
              f"content, the highest in the panel. This is the quantitative "
              f"support for the re-export limitation.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
