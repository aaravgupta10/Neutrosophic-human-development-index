"""
00_build_gini.py
----------------
Regenerates gini_clean_2023.csv from SWIID 9.x for the HDI-FN 20-country
panel, every run, from the raw SWIID download -- this is Phase 2's updated
Gini source superseding the earlier hand-delivered gini_clean_2023_updated.csv.

Adapted from build_gini_clean_2023.py (teacher-supplied), same logic,
re-pointed at this repo's data/raw and data/interim directories so it
runs as step 0 of run_all.sh instead of a standalone script. A verbatim
copy of the original is kept at docs/build_gini_clean_2023_reference.py.

Reference year: 2023.
Missing-value rule (Step 1.3 of the audit procedure): carry the most
recent value within a strict 2020-2023 window. Anything outside that
window is left missing and flagged -- EXCEPT Iceland, which has a
faculty-approved, documented one-year exception (see WINDOW_EXCEPTIONS
below and the README "Phase 2 update: Gini data" section).

Measure: gini_disp (disposable-income Gini, post-tax post-transfer).

Citation:
  Solt, F. (2020). The Standardized World Income Inequality Database,
  Versions 8-9. Social Science Quarterly 101(3): 1183-1199.
"""
import sys
import pandas as pd
from config import RAW_DIR, INTERIM_DIR

WINDOW = range(2020, 2024)     # 2020, 2021, 2022, 2023 -- per Step 1.3
MEASURE = "gini_disp"

# --- Documented exception (faculty-approved, see README "Phase 2 update:
#     Gini data" section) ---
# Iceland has no SWIID gini_disp observation in the strict 2020-2023
# window. The 2019 gini_disp value (25.3) is used as a one-year carry-
# forward beyond the stated window, confirmed correct against SWIID
# directly (gini_disp=25.3, gini_mkt=36.8 for Iceland/2019 -- the earlier
# 36.8 in a prior draft was a gini_mkt/gini_disp column mix-up, not a
# valid disposable-income figure). Every other country in the panel has
# a match inside the strict window and needs no such exception.
WINDOW_EXCEPTIONS = {
    "Iceland": range(2019, 2024),  # widened by one year, this country only
}

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


def main():
    sw_all = pd.read_csv(RAW_DIR / "swiid_summary.csv")
    sw_all = sw_all[sw_all["country"].isin(PANEL["swiid_name"])]

    frames = []
    for name in PANEL["swiid_name"]:
        window = WINDOW_EXCEPTIONS.get(name, WINDOW)
        sub = sw_all[(sw_all["country"] == name) & (sw_all["year"].isin(window))]
        if not sub.empty:
            frames.append(sub.sort_values("year", ascending=False).head(1))

    sw = pd.concat(frames, ignore_index=True) if frames else sw_all.iloc[0:0]
    sw = sw[["country", "year", MEASURE, f"{MEASURE}_se"]]
    sw.columns = ["swiid_name", "year_used", "gini", "gini_se"]

    df = PANEL.merge(sw, on="swiid_name", how="left")
    df["source"] = f"SWIID 9.x ({MEASURE}), Solt (2020)"
    df["gini"] = df["gini"].round(2)
    df["gini_se"] = df["gini_se"].round(2)
    df["year_used"] = df["year_used"].astype("Int64")

    missing = df[df["gini"].isna()]
    if not missing.empty:
        print("[00_build_gini] WARNING: no SWIID match (incl. any documented "
              "per-country window exception) for:")
        print(missing[["iso3", "country", "swiid_name"]].to_string(index=False))

    if "Iceland" in WINDOW_EXCEPTIONS:
        icl = df[df["country"] == "Iceland"]
        if not icl.empty and pd.notna(icl.iloc[0]["gini"]):
            print(f"[00_build_gini] NOTE: Iceland uses a documented one-year "
                  f"carry-forward exception (year={icl.iloc[0]['year_used']}, "
                  f"gini_disp={icl.iloc[0]['gini']}), faculty-confirmed against "
                  f"raw SWIID (gini_mkt=36.8 for the same row is NOT used -- "
                  f"an earlier draft mixed these up). See README.")

    cols = ["iso3", "country", "region", "year_used", "gini", "gini_se", "source"]
    out_path = INTERIM_DIR / "gini_clean_2023_built.csv"
    df[cols].to_csv(out_path, index=False)
    print(f"[00_build_gini] wrote {out_path}")
    print(df[cols].to_string(index=False))


if __name__ == "__main__":
    sys.exit(main())
