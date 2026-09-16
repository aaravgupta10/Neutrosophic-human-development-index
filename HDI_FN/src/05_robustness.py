"""
05_robustness.py
-----------------
Three robustness checks requested in the proctor feedback memo, run
against the final HDI-FN panel.

IMPORTANT SCOPING NOTE, read before interpreting the output:
None of I_health, I_education, I_income_adj, I_penetration, T_egov_adjusted,
or I_hitech have a published standard error anywhere in this project's raw
data. The only real measurement-uncertainty figure available anywhere in
the pipeline is gini_se (SWIID), and Gini/S_bal/S_int are NOT inputs to
HDI_FN (HDI_FN = geometric mean of I_health, I_education, I_income_adj,
I_digital -- disparity is a separate Part 5 output). This means a bootstrap
that "propagates measurement error into HDI_FN" cannot honestly be built
without inventing standard errors for four indicators that don't have any
-- which this project's own rules (Step 4.2: no LLM-invented values)
explicitly forbid.

What IS available and honestly computable: I_broadband and I_hitech are
MIN-MAX normalised against the sample's own maximum (Switzerland/France for
broadband, South Korea for hi-tech). That means their value for every
country depends on which country happens to set the ceiling -- a real,
data-driven source of rank instability. Check 1 below was originally implemented as a case-resampling bootstrap
(resample countries, recompute the normalisation ceiling). That approach
turned out to be uninformative: uniformly rescaling I_broadband/I_hitech
by a different sample maximum does not change their relative ordering
across countries, so every one of 1000 replicates produced identical
ranks -- a real result, but not a useful robustness check. Replaced with
a synthetic perturbation Monte Carlo instead: each of HDI_FN's four
components (I_health, I_education, I_income_adj, I_digital) is multiplied
by (1 + noise), noise ~ Normal(0, 0.03) independently per component per
replicate, 1000 replicates, ranks recomputed each time. The 3% figure is
an ASSUMED generic perturbation magnitude for sensitivity testing -- it is
explicitly NOT a calibrated measurement-uncertainty estimate, because none
exists in this project's data. What this checks: which rank orderings are
robust to small input noise (wide separation between neighbours) versus
which are fragile (countries close enough in score that noise reorders
them). That is a legitimate and standard question even without real SEs.

Check 2 (operator sensitivity) and Check 3 (rank correlation) do not have
this limitation and are computed directly.

SUPERVISOR REFINEMENT (received after initial submission):
(i) Where a real standard error exists (gini_se, for the Gini component),
    use it directly instead of an assumed noise figure. Since Gini is not
    an HDI_FN input, this is applied as a SEPARATE check (Check 4 below)
    against Table 5's S_int (Shadow Economy version, the paper's main
    table) -- Gini is perturbed using its real gini_se; shadow economy
    (I_x) is held fixed since it has no published SE of its own.
(ii) Where no real SE exists (I_health, I_education, I_income_adj,
    I_digital -- the HDI_FN inputs), sweep the assumed noise magnitude at
    1%, 3%, and 5% instead of reporting a single flat 3% figure, and
    confirm whether rankings hold across all three levels.
"""
import sys
import numpy as np
import pandas as pd
from scipy import stats
from config import PROCESSED_DIR, OUTPUT_DIR, SEED

np.random.seed(SEED)
N_BOOTSTRAP = 1000
PERTURBATION_LEVELS = [0.01, 0.03, 0.05]  # 1%, 3%, 5% sweep -- see supervisor refinement above


def geometric_mean_4(a, b, c, d):
    return (a * b * c * d) ** (1 / 4)


def arithmetic_mean_4(a, b, c, d):
    return (a + b + c + d) / 4


def ces_4(a, b, c, d, rho=-1.0):
    """Equal-weight CES aggregator. rho -> 1 approaches arithmetic mean;
    rho -> 0 approaches geometric mean; rho < 0 penalises imbalance across
    components more heavily than the geometric mean (used here: rho=-1,
    a moderately conservative choice -- other rho values would shift the
    absolute scores but Check 2 reports rank correlation, which is fairly
    robust to the exact rho chosen)."""
    parts = np.stack([a, b, c, d])
    return (np.mean(parts ** rho, axis=0)) ** (1 / rho)


def check_1_bootstrap(df_hdi):
    """Synthetic perturbation Monte Carlo, swept at 1%/3%/5% noise levels
    (see module docstring). For each level: multiply each of HDI_FN's four
    components by independent (1 + Normal(0, level)) noise, recompute
    HDI_FN and rank, repeat N_BOOTSTRAP times, report the 2.5/50/97.5
    percentile rank per country. Returns one combined long-format frame
    with a 'Noise Level' column."""
    d = df_hdi.dropna(subset=["I_health", "I_education", "I_income_adj", "I_digital"]).copy()
    countries = d["Country"].tolist()
    base = d.set_index("Country")[["I_health", "I_education", "I_income_adj", "I_digital"]]

    all_rows = []
    for level in PERTURBATION_LEVELS:
        rank_records = {c: [] for c in df_hdi["Country"]}
        for _ in range(N_BOOTSTRAP):
            noise = 1 + np.random.normal(0, level, size=base.shape)
            perturbed = (base.values * noise)
            hdi_fn = geometric_mean_4(perturbed[:, 0], perturbed[:, 1], perturbed[:, 2], perturbed[:, 3])
            ranked = pd.Series(hdi_fn, index=base.index).rank(ascending=False, method="min")
            for c in countries:
                rank_records[c].append(ranked[c])

        for c in df_hdi["Country"]:
            recs = rank_records[c]
            if not recs:
                all_rows.append({"Noise Level": f"{level*100:.0f}%", "Country": c,
                                 "Rank 2.5th pct": np.nan, "Rank Median": np.nan,
                                 "Rank 97.5th pct": np.nan, "N replicates scored": 0})
                continue
            recs = np.array(recs)
            all_rows.append({
                "Noise Level": f"{level*100:.0f}%",
                "Country": c,
                "Rank 2.5th pct": np.percentile(recs, 2.5),
                "Rank Median": np.percentile(recs, 50),
                "Rank 97.5th pct": np.percentile(recs, 97.5),
                "N replicates scored": len(recs),
            })
    out = pd.DataFrame(all_rows)
    return out.sort_values(["Noise Level", "Rank Median"])


def check_4_gini_se_bootstrap(df_disparity):
    """Table 5 (main, Shadow Economy version) S_int rank stability under
    REAL Gini measurement uncertainty. Gini is perturbed as
    Normal(gini, gini_se) per replicate (gini_se is SWIID's actual
    reported standard error -- not an assumed figure). Shadow economy
    (I_x) is held FIXED, since it has no published standard error in this
    project's data. S_int = T*(1-I) recomputed each replicate; reports
    2.5/50/97.5 percentile rank per country over N_BOOTSTRAP replicates."""
    d = df_disparity.dropna(subset=["gini", "gini_se", "I_x"]).copy()
    countries = d["Country"].tolist()
    gini = d.set_index("Country")["gini"]
    gini_se = d.set_index("Country")["gini_se"]
    i_x = d.set_index("Country")["I_x"]

    rank_records = {c: [] for c in countries}
    for _ in range(N_BOOTSTRAP):
        gini_draw = np.random.normal(gini.values, gini_se.values)
        gini_draw = np.clip(gini_draw, 0, 100)  # Gini is bounded [0,100]
        t_draw = gini_draw / 100
        s_int_draw = t_draw * (1 - i_x.values)
        ranked = pd.Series(s_int_draw, index=gini.index).rank(ascending=False, method="min")
        for c in countries:
            rank_records[c].append(ranked[c])

    rows = []
    for c in countries:
        recs = np.array(rank_records[c])
        rows.append({
            "Country": c,
            "gini_se used": gini_se[c],
            "Rank 2.5th pct": np.percentile(recs, 2.5),
            "Rank Median": np.percentile(recs, 50),
            "Rank 97.5th pct": np.percentile(recs, 97.5),
        })
    return pd.DataFrame(rows).sort_values("Rank Median")


def check_2_operator_sensitivity(df_digital, df_hdi):
    """Recompute I_digital and HDI_FN under arithmetic mean and CES(rho=-1)
    in addition to the geometric mean already used, and report rank
    correlation between operator variants."""
    d = df_digital.set_index("Country")
    h = df_hdi.set_index("Country")

    variants = {}
    for name, fn in [("geometric", geometric_mean_4), ("arithmetic", arithmetic_mean_4),
                      ("ces_rho-1", ces_4)]:
        i_digital_v = fn(d["I_penetration"].values, d["I_broadband"].values,
                          d["T_egov_adjusted"].values, d["I_hitech"].values)
        i_digital_v = pd.Series(i_digital_v, index=d.index)
        hdi_fn_v = pd.Series(
            fn(h["I_health"].reindex(d.index).values, h["I_education"].reindex(d.index).values,
               h["I_income_adj"].reindex(d.index).values, i_digital_v.values),
            index=d.index,
        )
        variants[name] = hdi_fn_v

    df_variants = pd.DataFrame(variants)
    ranks = df_variants.rank(ascending=False, method="min")
    ranks.columns = [f"{c}_rank" for c in ranks.columns]

    corr_rows = []
    names = list(variants.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            valid = ranks[[f"{a}_rank", f"{b}_rank"]].dropna()
            if len(valid) > 2:
                rho, _ = stats.spearmanr(valid[f"{a}_rank"], valid[f"{b}_rank"])
            else:
                rho = np.nan
            corr_rows.append({"Operator A": a, "Operator B": b, "Spearman rank corr.": rho})

    combined = pd.concat([df_variants.add_suffix("_score"), ranks], axis=1).reset_index()
    return combined, pd.DataFrame(corr_rows)


def check_3_correlation(df_hdi):
    """Pearson and Spearman correlation between HDI-FN rank and Standard
    HDI rank -- tests whether the digital augmentation reorders countries
    beyond noise."""
    valid = df_hdi.dropna(subset=["HDI_FN Rank", "Standard HDI Rank"])
    pearson_r, pearson_p = stats.pearsonr(valid["HDI_FN Rank"], valid["Standard HDI Rank"])
    spearman_r, spearman_p = stats.spearmanr(valid["HDI_FN Rank"], valid["Standard HDI Rank"])
    return pd.DataFrame([{
        "N countries": len(valid),
        "Pearson r (ranks)": pearson_r, "Pearson p-value": pearson_p,
        "Spearman rho": spearman_r, "Spearman p-value": spearman_p,
    }])


def main():
    df_digital = pd.read_csv(PROCESSED_DIR / "computed_digital.csv")
    df_hdi = pd.read_csv(PROCESSED_DIR / "computed_hdi_fn.csv")
    df_disparity = pd.read_csv(PROCESSED_DIR / "computed_disparity.csv")

    hdi_ranked_path = OUTPUT_DIR / "Table_4_HDI_FN_Preview.csv"
    if hdi_ranked_path.exists():
        df_hdi_ranked = pd.read_csv(hdi_ranked_path)
    else:
        df_hdi_ranked = df_hdi

    print(f"[05_robustness] Check 1: perturbation Monte Carlo, {N_BOOTSTRAP} replicates, "
          f"swept at {[f'{l*100:.0f}%' for l in PERTURBATION_LEVELS]} (no real SEs "
          f"available for these 4 indicators -- assumed sensitivity magnitudes)...")
    bootstrap_ci = check_1_bootstrap(df_hdi)
    bootstrap_ci.to_csv(OUTPUT_DIR / "Robustness_1_Bootstrap_Rank_CI.csv", index=False)
    print(bootstrap_ci.to_string(index=False))

    # Stability verdict: does the rank-1 country and bottom-3 stay the same across levels?
    top1_by_level = bootstrap_ci.sort_values("Rank Median").groupby("Noise Level").apply(
        lambda g: g.sort_values("Rank Median").iloc[0]["Country"], include_groups=False
    )
    print(f"\n[05_robustness] Top-ranked country by noise level: {top1_by_level.to_dict()}")

    print(f"\n[05_robustness] Check 2: aggregation operator sensitivity...")
    op_scores, op_corr = check_2_operator_sensitivity(df_digital, df_hdi)
    op_scores.to_csv(OUTPUT_DIR / "Robustness_2_Operator_Sensitivity_Scores.csv", index=False)
    op_corr.to_csv(OUTPUT_DIR / "Robustness_2_Operator_Sensitivity_Correlation.csv", index=False)
    print(op_corr.to_string(index=False))

    print(f"\n[05_robustness] Check 3: HDI-FN vs Standard HDI rank correlation...")
    corr = check_3_correlation(df_hdi_ranked)
    corr.to_csv(OUTPUT_DIR / "Robustness_3_Rank_Correlation.csv", index=False)
    print(corr.to_string(index=False))

    print(f"\n[05_robustness] Check 4: Table 5 (main) S_int rank stability under "
          f"REAL gini_se (SWIID reported standard errors, not assumed)...")
    gini_se_ci = check_4_gini_se_bootstrap(df_disparity)
    gini_se_ci.to_csv(OUTPUT_DIR / "Robustness_4_Table5_GiniSE_Bootstrap.csv", index=False)
    print(gini_se_ci.to_string(index=False))

    print(f"\n[05_robustness] wrote 4 robustness outputs to {OUTPUT_DIR}/")


if __name__ == "__main__":
    sys.exit(main())
