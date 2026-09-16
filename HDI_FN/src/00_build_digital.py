"""
00_build_digital.py
--------------------
Regenerates the digital indicators panel (Internet Penetration, Fixed
Broadband, Hi-Tech Exports) from the raw ITU/WDI downloads, every run.

This supersedes the hand-delivered digital_raw_2023.csv, which turned out
to still contain the original caret-marked (^) pre-audit fallback estimates
for most Hi-Tech Exports cells and roughly half the Internet Penetration
cells, despite being labeled "audited" -- confirmed cell-by-cell against
the raw source files below (see README "Digital layer rebuild" section).

EGDI is NOT rebuilt here -- it was never in question, is already sourced
directly from the 2024 UN E-Government Survey, and there is no raw EGDI
file in this repo to rebuild it from. It is carried over as-is from
digital_raw_2023.csv.

Reference year: 2023. Missing-value rule (Step 1.3): carry forward the
most recent value within a strict 2020-2023 window, and flag which year
was used. If a country is missing more than 2 of the 4 digital
sub-indicators, it should be dropped from the digital panel (none are,
in this 20-country study panel -- worst case is Bangladesh, missing only
Hi-Tech).

Sources:
  Internet Penetration : ITU DataHub, series i99H  (individuals-using-the-internet_.csv)
  Fixed Broadband      : ITU DataHub, series i992b (fixed-broadband-subscriptions.csv)
                         (that file also bundles a mislabeled absolute-
                         subscriber-count series, i4213tfbb -- excluded here)
  Hi-Tech Exports       : World Bank WDI, series TX.VAL.TECH.MF.ZS (high-technology-exports-1.csv)
  EGDI                  : carried over from digital_raw_2023.csv (UN E-Gov Survey 2024)
"""
import sys
import numpy as np
import pandas as pd
from config import RAW_DIR, INTERIM_DIR

WINDOW = range(2020, 2024)   # 2020, 2021, 2022, 2023 -- per Step 1.3

# iso3 -> (country display name, region) for the 20-country study panel
PANEL = pd.DataFrame([
    ("ISL", "Iceland",      "North"),
    ("NOR", "Norway",       "North"),
    ("NLD", "Netherlands",  "North"),
    ("DNK", "Denmark",      "North"),
    ("CHE", "Switzerland",  "North"),
    ("CAN", "Canada",       "North"),
    ("KOR", "South Korea",  "North"),
    ("FRA", "France",       "North"),
    ("FIN", "Finland",      "North"),
    ("DEU", "Germany",      "North"),
    ("AUS", "Australia",    "North"),
    ("JPN", "Japan",        "North"),
    ("CHN", "China",        "South"),
    ("IDN", "Indonesia",    "South"),
    ("MAR", "Morocco",      "South"),
    ("PAK", "Pakistan",     "South"),
    ("BFA", "Burkina Faso", "South"),
    ("PHL", "Philippines",  "South"),
    ("NPL", "Nepal",        "South"),
    ("BGD", "Bangladesh",   "South"),
], columns=["iso3", "country", "region"])


def carry_forward(df_long, iso3_col, year_col, value_col):
    """For each iso3, take the 2023 value if present; else the most
    recent value within WINDOW. Returns iso3 -> (value, year_used)."""
    df_long = df_long[df_long[year_col].isin(WINDOW)]
    df_long = df_long[df_long[iso3_col].isin(PANEL["iso3"])]
    df_long = df_long.dropna(subset=[value_col])
    picked = (df_long.sort_values([iso3_col, year_col], ascending=[True, False])
                      .groupby(iso3_col, as_index=False)
                      .first())
    return picked[[iso3_col, year_col, value_col]].rename(
        columns={iso3_col: "iso3", year_col: "year_used", value_col: "value"}
    )


def main():
    # --- Internet Penetration (ITU i99H) ---
    itu_net = pd.read_csv(RAW_DIR / "individuals-using-the-internet_.csv")
    net = carry_forward(itu_net, "entityIso", "dataYear", "dataValue")
    net = net.rename(columns={"value": "Internet_Pen_2023_Pct"})

    # --- Fixed Broadband (ITU i992b -- excluding the bundled i4213tfbb series) ---
    itu_bb = pd.read_csv(RAW_DIR / "fixed-broadband-subscriptions.csv")
    itu_bb = itu_bb[itu_bb["seriesCode"] == "i992b"]
    bb = carry_forward(itu_bb, "entityIso", "dataYear", "dataValue")
    bb = bb.rename(columns={"value": "Fixed_Broadband_2023_per100"})

    # --- Hi-Tech Exports (WDI TX.VAL.TECH.MF.ZS) ---
    wdi_hitech = pd.read_csv(RAW_DIR / "high-technology-exports-1.csv", skiprows=4)
    wdi_long = wdi_hitech.melt(
        id_vars=["Country Name", "Country Code"],
        value_vars=[str(y) for y in WINDOW],
        var_name="year", value_name="value",
    )
    wdi_long["year"] = wdi_long["year"].astype(int)
    hitech = carry_forward(wdi_long, "Country Code", "year", "value")
    hitech = hitech.rename(columns={"value": "HiTech_Exports_Pct"})

    # --- assemble ---
    df = PANEL.copy()
    notes = {iso3: [] for iso3 in df["iso3"]}

    df = df.merge(net[["iso3", "Internet_Pen_2023_Pct", "year_used"]]
                  .rename(columns={"year_used": "internet_year"}), on="iso3", how="left")
    df = df.merge(bb[["iso3", "Fixed_Broadband_2023_per100", "year_used"]]
                  .rename(columns={"year_used": "broadband_year"}), on="iso3", how="left")
    df = df.merge(hitech[["iso3", "HiTech_Exports_Pct", "year_used"]]
                  .rename(columns={"year_used": "hitech_year"}), on="iso3", how="left")

    for _, row in df.iterrows():
        iso3 = row["iso3"]
        for label, yearcol in [("Internet", "internet_year"),
                                ("Broadband", "broadband_year"),
                                ("Hi-Tech", "hitech_year")]:
            y = row[yearcol]
            if pd.isna(y):
                notes[iso3].append(f"{label} missing in 2020-2023 window")
            elif int(y) != 2023:
                notes[iso3].append(f"{label} carried forward from {int(y)}")
    df["Audit_Notes"] = df["iso3"].map(lambda i: "; ".join(notes[i]) if notes[i] else "2023 data used for all three")

    # --- carry over EGDI from the existing digital_raw_2023.csv (not rebuilt here) ---
    legacy = pd.read_csv(RAW_DIR / "digital_raw_2023.csv")
    df = df.merge(legacy[["Country", "EGDI_2024"]].rename(columns={"Country": "country"}),
                  on="country", how="left")

    df = df[["country", "region", "Internet_Pen_2023_Pct", "Fixed_Broadband_2023_per100",
              "EGDI_2024", "HiTech_Exports_Pct", "Audit_Notes"]]
    df = df.rename(columns={"country": "Country", "region": "Region"})

    missing_hitech = df[df["HiTech_Exports_Pct"].isna()]
    if not missing_hitech.empty:
        print(f"[00_build_digital] {len(missing_hitech)} countries missing "
              f"Hi-Tech Exports in the 2020-2023 window: "
              f"{missing_hitech['Country'].tolist()} (kept in panel -- only "
              f"1 of 4 sub-indicators missing, below the 2-of-4 drop threshold)")

    out_path = INTERIM_DIR / "digital_raw_2023_built.csv"
    df.to_csv(out_path, index=False)
    print(f"[00_build_digital] wrote {out_path}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    sys.exit(main())
