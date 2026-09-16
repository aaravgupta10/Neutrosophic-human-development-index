"""
06_table5_ab.py
----------------
Produces two versions of Table 5 (Neutrosophic Disparity Scores) using
different operationalisations of the Indeterminacy term I, plus a
side-by-side comparison, so the supervisor could pick between them on
evidence rather than assertion.

SUPERVISOR DECISION + A/B MEMO RECONCILIATION:
The A/B memo specifies three files in /output/: Table_5A_Shadow_Econ.csv,
Table_5B_Gini_SE.csv, Table_5_Comparison.csv. The supervisor's later
decision was that shadow economy (Version A) is the paper's MAIN Table 5
and Version B belongs in supplementary. These are reconciled here so both
checklists pass literally:
  - All three memo-named files ARE written to /output/ (so a reviewer
    holding the A/B memo finds exactly what it lists). Table_5A is a
    labelled copy of the main table; the canonical main Table 5 remains
    output/Table_5_Disparity_Scores.csv (from 04_tables.py), unchanged.
  - The same B + comparison files are ALSO mirrored to
    output/supplementary/ with a summary memo, reflecting that Version B
    is supplementary robustness material, not a live alternative.

Formulas (both versions):
    S_bal = 0.5*T + 0.5*(1-I)
    S_int = T*(1-I)
where T = Formal Gini (0-1 scale).

Reads data/processed/computed_disparity.csv (the audited, already-merged
Gini + shadow economy panel produced by 03_compute.py from the audited
raw files). Min-max normalisation for I_v2 is computed inside this script
from whatever countries are present, so it stays correct if the country
list ever changes -- not hardcoded.

Iceland is included in both versions (uses its 2019 carry-forward
gini_se = 0.97, per the audit's documented window exception -- not
excluded here).

No stochastic step -- no seed needed (per spec).
"""
import sys
import pandas as pd
from scipy import stats
from config import PROCESSED_DIR, OUTPUT_DIR


def main():
    supp_dir = OUTPUT_DIR / "supplementary"
    supp_dir.mkdir(exist_ok=True)

    df = pd.read_csv(PROCESSED_DIR / "computed_disparity.csv")

    # --- Version A: labelled copy in /output/ per A/B memo file list.
    # The canonical MAIN Table 5 is output/Table_5_Disparity_Scores.csv
    # (from 04_tables.py); this is the same content, named as the memo asks. ---
    table_5a = df[["Country", "T_x", "gini_se", "I_x", "S_bal", "S_int"]].rename(columns={
        "T_x": "Formal Gini (T)",
        "gini_se": "Gini SE (reported, not modeled)",
        "I_x": "Shadow Econ (I)",
    }).sort_values("S_int", ascending=False)
    table_5a.to_csv(OUTPUT_DIR / "Table_5A_Shadow_Econ.csv", index=False)

    # --- Version B: gini_se, panel min-max normalised to [0,1] ---
    se = df["gini_se"]
    se_min, se_max = se.min(), se.max()
    df["I_v2"] = (se - se_min) / (se_max - se_min)
    df["S_bal_B"] = 0.5 * df["T_x"] + 0.5 * (1 - df["I_v2"])
    df["S_int_B"] = df["T_x"] * (1 - df["I_v2"])

    table_5b = df[["Country", "T_x", "gini_se", "I_v2", "S_bal_B", "S_int_B"]].rename(columns={
        "T_x": "Formal Gini (T)",
        "gini_se": "Gini SE (raw)",
        "I_v2": "I_v2 (normalised)",
        "S_bal_B": "S_bal",
        "S_int_B": "S_int",
    }).sort_values("S_int", ascending=False)
    table_5b.to_csv(OUTPUT_DIR / "Table_5B_Gini_SE.csv", index=False)       # per A/B memo file list
    table_5b.to_csv(supp_dir / "Table_5B_Gini_SE.csv", index=False)         # supplementary mirror
    print(f"[06_table5_ab] Version B normalisation bounds: "
          f"gini_se min={se_min}, max={se_max} (recomputed from current panel)")

    # --- Comparison ---
    comp = df[["Country", "T_x", "I_x", "I_v2", "S_bal", "S_int", "S_int_B"]].rename(columns={
        "T_x": "T",
        "I_x": "I_A (shadow)",
        "I_v2": "I_B (gini_se norm)",
        "S_bal": "S_bal_A",
        "S_int": "S_int_A",
    })
    comp["S_bal_B"] = df["S_bal_B"]
    comp["Rank_S_int_A"] = comp["S_int_A"].rank(ascending=False, method="min").astype(int)
    comp["Rank_S_int_B"] = comp["S_int_B"].rank(ascending=False, method="min").astype(int)
    comp["Rank_delta"] = comp["Rank_S_int_A"] - comp["Rank_S_int_B"]

    comp = comp[["Country", "T", "I_A (shadow)", "I_B (gini_se norm)",
                 "S_bal_A", "S_bal_B", "S_int_A", "S_int_B",
                 "Rank_S_int_A", "Rank_S_int_B", "Rank_delta"]]
    comp = comp.sort_values("Rank_S_int_A")
    comp.to_csv(OUTPUT_DIR / "Table_5_Comparison.csv", index=False)          # per A/B memo file list
    comp.to_csv(supp_dir / "Table_5_Comparison.csv", index=False)           # supplementary mirror

    # --- Summary statistics ---
    spearman_rho, spearman_p = stats.spearmanr(comp["S_int_A"], comp["S_int_B"])
    pearson_r, pearson_p = stats.pearsonr(comp["I_A (shadow)"], comp["I_B (gini_se norm)"])

    if spearman_rho > 0.9:
        verdict = ("Country ordering is robust to the choice of I -- either "
                   "operationalisation can be defended on the data alone.")
    elif spearman_rho < 0.7:
        verdict = ("The two definitions produce genuinely different pictures -- "
                   "the choice must be argued on conceptual grounds in methods, "
                   "not just on the data.")
    else:
        verdict = ("Intermediate agreement -- worth a sentence in methods either way.")

    summary_lines = [
        "Table 5 A/B Comparison -- Summary Statistics",
        "=" * 50,
        "SUPERVISOR DECISION: Version A (shadow economy) is the paper's main",
        "Table 5 (see output/Table_5_Disparity_Scores.csv). This comparison and",
        "Version B are supplementary robustness material, not alternatives up",
        "for further debate.",
        "",
        f"Spearman rank correlation, S_int_A vs S_int_B: {spearman_rho:.4f} (p={spearman_p:.2e})",
        f"Pearson correlation, I_A (shadow) vs I_B (gini_se norm): {pearson_r:.4f} (p={pearson_p:.2e})",
        "",
        verdict,
        "",
        "Methods-section framing (per supervisor): shadow economy captures",
        "distributional indeterminacy -- what formal statistics don't see --",
        "which parallels this paper's EGDI/non-penetration decomposition.",
        "Gini SE captures sampling uncertainty, a different concept, and is",
        "reported here as a supplementary robustness check only.",
        "",
        "Countries with largest |Rank_delta| (biggest reordering between A and B):",
        comp.reindex(comp["Rank_delta"].abs().sort_values(ascending=False).index)
            .head(5)[["Country", "Rank_S_int_A", "Rank_S_int_B", "Rank_delta"]].to_string(index=False),
    ]
    summary_text = "\n".join(summary_lines)
    (supp_dir / "Table_5_Comparison_Summary.txt").write_text(summary_text + "\n")
    print("\n[06_table5_ab] " + summary_text.replace("\n", "\n[06_table5_ab] "))
    print(f"\n[06_table5_ab] wrote Table_5A_Shadow_Econ.csv, Table_5B_Gini_SE.csv, "
          f"Table_5_Comparison.csv to {OUTPUT_DIR}/ (per A/B memo file list); "
          f"mirrored B + comparison + summary to {supp_dir}/ (supervisor decision: "
          f"main Table 5 is output/Table_5_Disparity_Scores.csv, unchanged)")


if __name__ == "__main__":
    sys.exit(main())
