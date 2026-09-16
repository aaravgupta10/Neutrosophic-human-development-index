"""
build_digital_raw_2023.py
-------------------------
Rebuild digital_raw_2023.csv from primary-source CSVs.

Reference year: 2023.
Missing-value rule: carry the most recent value within 2020-2023; if still
missing, leave blank and record the reason in `source_note`.

Inputs (place in ./data/raw/):
  individualsusingtheinternet_.csv   (ITU DataHub, series i99H)
  fixedbroadbandsubscriptions_.csv   (ITU DataHub, series i992b only)
  hightechnologyexports1.csv         (World Bank WDI, TX.VAL.TECH.MF.ZS)
  EGOV_DATA_2024.csv                 (UN E-Government Survey 2024)

Output: digital_raw_2023.csv
"""
import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
REF_YEAR = 2023
WINDOW = range(2020, 2024)   # 2020, 2021, 2022, 2023

# Master country table — join everything on ISO-3.
# (Add columns for any name variants encountered in the sources.)
COUNTRIES = pd.DataFrame([
    ("ISL", "Iceland",      "North", "Iceland"),
    ("NOR", "Norway",       "North", "Norway"),
    ("NLD", "Netherlands",  "North", "Netherlands"),
    ("DNK", "Denmark",      "North", "Denmark"),
    ("CHE", "Switzerland",  "North", "Switzerland"),
    ("CAN", "Canada",       "North", "Canada"),
    ("KOR", "South Korea",  "North", "Republic of Korea"),   # EGOV name
    ("FRA", "France",       "North", "France"),
    ("FIN", "Finland",      "North", "Finland"),
    ("DEU", "Germany",      "North", "Germany"),
    ("AUS", "Australia",    "North", "Australia"),
    ("JPN", "Japan",        "North", "Japan"),
    ("CHN", "China",        "South", "China"),
    ("IDN", "Indonesia",    "South", "Indonesia"),
    ("MAR", "Morocco",      "South", "Morocco"),
    ("PAK", "Pakistan",     "South", "Pakistan"),
    ("BFA", "Burkina Faso", "South", "Burkina Faso"),
    ("PHL", "Philippines",  "South", "Philippines"),
    ("NPL", "Nepal",        "South", "Nepal"),
    ("BGD", "Bangladesh",   "South", "Bangladesh"),
], columns=["iso3", "country", "region", "egov_name"])


def pull_itu(path, series_code, value_label):
    """Get the most recent ITU value in WINDOW per ISO-3."""
    df = pd.read_csv(path)
    df = df[df["seriesCode"] == series_code]
    df = df[df["dataYear"].isin(WINDOW)]
    df = df.sort_values(["entityIso", "dataYear"], ascending=[True, False])
    df = df.groupby("entityIso", as_index=False).first()
    return df[["entityIso", "dataValue", "dataYear"]].rename(
        columns={"entityIso": "iso3",
                 "dataValue": value_label,
                 "dataYear": f"{value_label}_year"})


def pull_wdi(path, value_label):
    """Get the most recent WDI value in WINDOW per ISO-3 (wide-format file)."""
    df = pd.read_csv(path, skiprows=4)
    years = [str(y) for y in WINDOW]
    out = []
    for _, row in df.iterrows():
        iso = row["Country Code"]
        latest_val, latest_year = None, None
        for y in sorted(years, reverse=True):     # newest first
            v = row.get(y)
            if pd.notna(v):
                latest_val, latest_year = float(v), int(y)
                break
        out.append((iso, latest_val, latest_year))
    return pd.DataFrame(out, columns=["iso3", value_label, f"{value_label}_year"])


def pull_egdi(path, name_map):
    """EGOV 2024 file — joined on country name (no ISO column)."""
    df = pd.read_csv(path)
    df["Country Name"] = df["Country Name"].str.strip()
    out = name_map.merge(df, left_on="egov_name", right_on="Country Name", how="left")
    return out[["iso3", "E-Government Index"]].rename(
        columns={"E-Government Index": "egdi_2024"})


# ---- assemble ------------------------------------------------------------
df = COUNTRIES.copy()
df = df.merge(pull_itu(RAW / "individualsusingtheinternet_.csv",
                       "i99H", "internet_pen"), on="iso3", how="left")
df = df.merge(pull_itu(RAW / "fixedbroadbandsubscriptions_.csv",
                       "i992b", "broadband_per100"), on="iso3", how="left")
df = df.merge(pull_wdi(RAW / "hightechnologyexports1.csv",
                       "hitech_exports_pct"), on="iso3", how="left")
df = df.merge(pull_egdi(RAW / "EGOV_DATA_2024.csv", COUNTRIES[["iso3","egov_name"]]),
              on="iso3", how="left")

# Round to 2 dp for the panel; keep year-used columns for the audit trail.
for col in ["internet_pen", "broadband_per100", "hitech_exports_pct", "egdi_2024"]:
    df[col] = df[col].round(3 if col == "egdi_2024" else 2)

cols = ["iso3", "country", "region",
        "internet_pen", "internet_pen_year",
        "broadband_per100", "broadband_per100_year",
        "hitech_exports_pct", "hitech_exports_pct_year",
        "egdi_2024"]
df[cols].to_csv("digital_raw_2023.csv", index=False)
print(df[cols].to_string(index=False))
