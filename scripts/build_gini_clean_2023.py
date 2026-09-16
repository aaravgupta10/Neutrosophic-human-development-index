"""
build_gini_clean_2023.py
------------------------
Build gini_clean_2023.csv from SWIID 9.x for the HDI-FN 20-country panel.

Reference year: 2023.
Missing-value rule: carry the most recent value within 2020-2023.
Measure: gini_disp (disposable-income Gini, post-tax post-transfer) -- this is
the welfare-relevant measure for HDI-style analysis. Switch MEASURE to
"gini_mkt" if a market-income comparison is wanted later.

Citation:
  Solt, F. (2020). The Standardized World Income Inequality Database,
  Versions 8-9. Social Science Quarterly 101(3): 1183-1199.

Source file:
  Download swiid9_x.zip from https://fsolt.org/swiid/ and place
  swiid_summary.csv in ./data/raw/

Output: gini_clean_2023.csv
"""
import pandas as pd
from pathlib import Path

RAW     = Path("data/raw")
WINDOW  = range(2020, 2024)             # 2020, 2021, 2022, 2023
MEASURE = "gini_disp"                   # or "gini_mkt"
OUTPUT  = Path("gini_clean_2023.csv")

# Twenty-country panel.  swiid_name uses the spelling found in SWIID's
# `country` column; check against the actual file if a join misses.
PANEL = pd.DataFrame([
    ("ISL", "Iceland",      "North", "Iceland"),
    ("NOR", "Norway",       "North", "Norway"),
    ("NLD", "Netherlands",  "North", "Netherlands"),
    ("DNK", "Denmark",      "North", "Denmark"),
    ("CHE", "Switzerland",  "North", "Switzerland"),
    ("CAN", "Canada",       "North", "Canada"),
    ("KOR", "South Korea",  "North", "Korea"),
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
], columns=["iso3", "country", "region", "swiid_name"])

# ---- load, filter to window + panel, take most recent year ---------------
sw = pd.read_csv(RAW / "swiid_summary.csv")
sw = sw[sw["year"].isin(WINDOW)]
sw = sw[sw["country"].isin(PANEL["swiid_name"])]
sw = (sw.sort_values(["country", "year"], ascending=[True, False])
        .groupby("country", as_index=False)
        .first())
sw = sw[["country", "year", MEASURE, f"{MEASURE}_se"]]
sw.columns = ["swiid_name", "year_used", "gini", "gini_se"]

# ---- assemble ------------------------------------------------------------
df = PANEL.merge(sw, on="swiid_name", how="left")
df["source"] = f"SWIID 9.x ({MEASURE}), Solt (2020)"
df["gini"]    = df["gini"].round(2)
df["gini_se"] = df["gini_se"].round(2)
df["year_used"] = df["year_used"].astype("Int64")

# Warn loudly about any panel country that didn't get a hit
missing = df[df["gini"].isna()]
if not missing.empty:
    print("WARNING: no SWIID match within 2020-2023 for:")
    print(missing[["iso3","country","swiid_name"]].to_string(index=False))

# ---- write ---------------------------------------------------------------
cols = ["iso3","country","region","year_used","gini","gini_se","source"]
try:
    df[cols].to_csv(OUTPUT, index=False)
    output_path = OUTPUT
except PermissionError:
    output_path = OUTPUT.with_name(f"{OUTPUT.stem}_updated{OUTPUT.suffix}")
    df[cols].to_csv(output_path, index=False)
    print(f"\nNOTE: {OUTPUT} was locked, so output was written to {output_path} instead.")

print("\n", df[cols].to_string(index=False))
