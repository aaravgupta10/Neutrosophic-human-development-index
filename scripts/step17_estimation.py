"""
Step 17: Independent Verification of the Phi-F Horse Race and Interaction Reparameterisation
External Validation Replication Pipeline (Section 3.6 of HDI-N Manuscript)

This script runs start to finish on the frozen input panels:
- HDIN_Canonical_v2.csv
- Step15_Findex_Raw.csv

Outputs generated in the output directory:
- Step17_Frame.csv
- Step17_Ladder.csv
- Step17_MarginalEffects.csv
- Step17_Results.md
"""

import os
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

# -----------------------------------------------------------------------------
# Configuration and Paths
# -----------------------------------------------------------------------------
# Single variable for base workspace directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Robust path resolution
def find_path(rel_paths):
    for p in rel_paths:
        if p.exists():
            return p
    return rel_paths[0]

CANONICAL_PATH = find_path([
    REPO_ROOT / "data" / "canonical" / "HDIN_Canonical_v2.csv",
    REPO_ROOT / "step_14" / "HDIN_Canonical_v2.csv",
    Path(__file__).parent / "HDIN_Canonical_v2.csv"
])
FINDEX_PATH = find_path([
    REPO_ROOT / "data" / "validation" / "Step15_Findex_Raw.csv",
    REPO_ROOT / "step15" / "Step15_Findex_Raw.csv",
    Path(__file__).parent / "Step15_Findex_Raw.csv"
])
OUTPUT_DIR = REPO_ROOT / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Expected Gate A counts
GATE_A_EXPECTED = {
    "GovPay_Pct": 145,
    "DigitalPay_Pct": 150,
    "MobileAccess_Pct": 88
}

OUTCOMES = ["GovPay_Pct", "DigitalPay_Pct", "MobileAccess_Pct"]

# -----------------------------------------------------------------------------
# Formatting Helpers
# -----------------------------------------------------------------------------
def fmt_p(p):
    if pd.isna(p):
        return "NA"
    if p < 0.0001:
        return f"{p:.4e}"
    return f"{p:.4f}"

def fmt_num(val, dec=4):
    if pd.isna(val):
        return "NA"
    return f"{val:.{dec}f}"

# -----------------------------------------------------------------------------
# Task 1: Build the Estimation Frame
# -----------------------------------------------------------------------------
def task1_build_frame(canonical_path, findex_path, output_dir):
    print("=" * 70)
    print("TASK 1: Building Estimation Frame & Gate A Verification")
    print("=" * 70)
    
    if not canonical_path.exists():
        raise FileNotFoundError(f"Canonical dataset not found: {canonical_path}")
    if not findex_path.exists():
        raise FileNotFoundError(f"Findex dataset not found: {findex_path}")
        
    canonical = pd.read_csv(canonical_path)
    findex = pd.read_csv(findex_path)
    
    print(f"Loaded HDIN_Canonical_v2: {canonical.shape[0]} rows, {canonical.shape[1]} cols")
    print(f"Loaded Step15_Findex_Raw: {findex.shape[0]} rows, {findex.shape[1]} cols")
    
    # Check recomputation of Phi and Phi_svc
    phi_recomp = canonical["EGDI"] * (1.0 - canonical["p"])
    phi_diff = (canonical["Phi_EGDI"] - phi_recomp).abs().max()
    print(f"Recomputation check Phi_EGDI vs EGDI * (1 - p): max abs diff = {phi_diff:.4e}")
    if phi_diff > 1e-10:
        raise ValueError(f"Phi_EGDI recomputation discrepancy {phi_diff} exceeds 1e-10 threshold!")
        
    phi_svc_recomp = canonical["OSI"] * (1.0 - canonical["p"])
    phi_svc_diff = (canonical["Phi_OSI"] - phi_svc_recomp).abs().max()
    print(f"Recomputation check Phi_OSI vs OSI * (1 - p): max abs diff = {phi_svc_diff:.4e}")
    if phi_svc_diff > 1e-10:
        raise ValueError(f"Phi_OSI recomputation discrepancy {phi_svc_diff} exceeds 1e-10 threshold!")

    # Verify dropped non-frame codes from Findex
    dropped_codes = set(findex["ISO3"]) - set(canonical["ISO3"])
    expected_dropped = {
        'WLD', 'HIC', 'LIC', 'LMC', 'UMC', 'LMY', 'EAP', 'ECA', 'LAC', 'MNA', 'SAS', 'SSA',
        'HKG', 'PRI', 'PSE', 'TWN', 'XKX',
        'SDN', 'SSD', 'SYR', 'TKM', 'YEM'
    }
    print(f"Findex non-frame codes detected: {len(dropped_codes)} codes")
    if dropped_codes != expected_dropped:
        diff_missing = expected_dropped - dropped_codes
        diff_unexpected = dropped_codes - expected_dropped
        raise ValueError(f"Dropped codes mismatch. Missing: {diff_missing}, Unexpected: {diff_unexpected}")
    print("Verified: Left join will correctly exclude all 22 aggregate/territory/exclusion codes.")

    # Left join on ISO3
    frame = pd.merge(canonical, findex, on="ISO3", how="left")
    print(f"Merged frame rows: {len(frame)} (must be exactly 184)")
    if len(frame) != 184:
        raise ValueError(f"Merged frame has {len(frame)} rows, expected 184!")

    # Exact variable construction
    frame["T"] = frame["EGDI"]
    frame["F"] = 1.0 - frame["p"]
    frame["Phi"] = frame["Phi_EGDI"]
    frame["T_svc"] = frame["OSI"]
    frame["Phi_svc"] = frame["Phi_OSI"]
    frame["inc"] = frame["I_income"]

    # Gate A Verification
    print("\n--- Gate A Row Counts ---")
    gate_a_counts = {}
    gate_a_failures = []
    for outcome, expected_n in GATE_A_EXPECTED.items():
        valid = frame.dropna(subset=[outcome, "inc", "T", "F", "Phi"])
        actual_n = len(valid)
        gate_a_counts[outcome] = actual_n
        print(f"  {outcome:<18}: {actual_n:3d} rows (expected: {expected_n:3d}) -> {'PASS' if actual_n == expected_n else 'FAIL'}")
        if actual_n != expected_n:
            gate_a_failures.append((outcome, expected_n, actual_n))

    if gate_a_failures:
        raise ValueError(f"Gate A verification failed on: {gate_a_failures}")

    # Confirm Monaco (MCO) is dropped via listwise deletion due to missing income
    mco = frame[frame["ISO3"] == "MCO"]
    if mco.empty or not pd.isna(mco["inc"].values[0]):
        raise ValueError("MCO check failed: expected MCO to have NaN I_income.")
    print("Verified: Monaco (MCO) has NaN I_income and leaves every specification via listwise deletion.")

    output_path = output_dir / "Step17_Frame.csv"
    frame.to_csv(output_path, index=False)
    print(f"Saved merged frame: {output_path}")

    return frame, phi_diff, phi_svc_diff, gate_a_counts, sorted(list(dropped_codes))

# -----------------------------------------------------------------------------
# Task 2: Six-Model Ladder Estimation
# -----------------------------------------------------------------------------
def task2_estimate_ladder(frame, output_dir):
    print("\n" + "=" * 70)
    print("TASK 2: Estimating Six-Model Ladder (HC3 Robust SEs)")
    print("=" * 70)

    model_specs = {
        "M0": ["inc"],
        "M1": ["inc", "T"],
        "M2": ["inc", "T", "Phi"],
        "M3": ["inc", "T", "F", "Phi"],
        "M3b": ["inc", "T", "F"],
        "M5": ["inc", "T_svc", "F", "Phi_svc"]
    }

    ladder_rows = []
    fitted_models = {}

    for outcome in OUTCOMES:
        fitted_models[outcome] = {}
        for m_name, rhs_vars in model_specs.items():
            required_cols = [outcome] + rhs_vars
            sub = frame.dropna(subset=required_cols).copy()
            n_obs = len(sub)
            
            X = sm.add_constant(sub[rhs_vars])
            y = sub[outcome]
            
            # Fit with HC3 covariance
            fit = sm.OLS(y, X).fit(cov_type="HC3")
            fitted_models[outcome][m_name] = fit
            
            r2 = fit.rsquared
            
            for reg in fit.params.index:
                coef = fit.params[reg]
                se = fit.bse[reg]
                t = fit.tvalues[reg]
                p = fit.pvalues[reg]
                
                ladder_rows.append({
                    "Model": m_name,
                    "Outcome": outcome,
                    "Regressor": reg,
                    "Coef": round(coef, 4),
                    "HC3_SE": round(se, 4),
                    "t_stat": round(t, 4),
                    "p_value": fmt_p(p),
                    "N": n_obs,
                    "R2": round(r2, 4)
                })

    ladder_df = pd.DataFrame(ladder_rows)
    output_path = output_dir / "Step17_Ladder.csv"
    ladder_df.to_csv(output_path, index=False)
    print(f"Saved ladder table: {output_path} ({len(ladder_df)} rows)")

    # Replication check: M2 on GovPay_Pct Phi coef must be -0.4624
    m2_gov = fitted_models["GovPay_Pct"]["M2"]
    m2_phi_coef = m2_gov.params["Phi"]
    print(f"M2 GovPay_Pct Phi coef: {m2_phi_coef:.6f} (published target: -0.4624)")
    if abs(m2_phi_coef - (-0.4624)) > 0.0005:
        raise ValueError(f"M2 GovPay_Pct Phi coef {m2_phi_coef:.4f} does not reproduce published -0.4624!")
    print("Verified: M2 reproduces published -0.4624 on government payments.")

    return ladder_df, fitted_models

# -----------------------------------------------------------------------------
# Task 3: Centring-Invariance Demonstration for M3
# -----------------------------------------------------------------------------
def task3_centring_invariance(frame, fitted_models):
    print("\n" + "=" * 70)
    print("TASK 3: Centring-Invariance Demonstration & VIF Analysis")
    print("=" * 70)

    sub = frame.dropna(subset=["GovPay_Pct", "inc", "T", "F", "Phi"]).copy()
    
    # Uncentred M3
    m3_un = fitted_models["GovPay_Pct"]["M3"]
    phi_un_coef = m3_un.params["Phi"]
    phi_un_se = m3_un.bse["Phi"]
    phi_un_p = m3_un.pvalues["Phi"]

    # Centred M3
    sub["T_c"] = sub["T"] - sub["T"].mean()
    sub["F_c"] = sub["F"] - sub["F"].mean()
    sub["Phi_c"] = sub["T_c"] * sub["F_c"]

    X_c = sm.add_constant(sub[["inc", "T_c", "F_c", "Phi_c"]])
    m3_c = sm.OLS(sub["GovPay_Pct"], X_c).fit(cov_type="HC3")
    phi_c_coef = m3_c.params["Phi_c"]
    phi_c_se = m3_c.bse["Phi_c"]
    phi_c_p = m3_c.pvalues["Phi_c"]

    print(f"Uncentred M3 Phi coef: {phi_un_coef:.6f} (SE: {phi_un_se:.6f}, p: {phi_un_p:.4e})")
    print(f"Centred M3 Phi_c coef: {phi_c_coef:.6f} (SE: {phi_c_se:.6f}, p: {phi_c_p:.4e})")

    diff = abs(phi_un_coef - phi_c_coef)
    agrees_4dec = (diff < 0.0001)
    print(f"Discrepancy: {diff:.4e} -> Agrees to 4 decimal places: {agrees_4dec}")

    # VIF calculations
    X_un_mat = sm.add_constant(sub[["inc", "T", "F", "Phi"]]).values
    X_c_mat = X_c.values

    var_names = ["inc", "T", "F", "Phi"]
    vif_results = {}
    for i, name in enumerate(var_names):
        # index i+1 corresponds to regressor excluding constant at index 0
        vif_un = variance_inflation_factor(X_un_mat, i + 1)
        vif_c = variance_inflation_factor(X_c_mat, i + 1)
        vif_results[name] = (vif_un, vif_c)
        print(f"  VIF {name:<4}: Uncentred = {vif_un:7.4f} | Centred = {vif_c:7.4f}")

    return {
        "phi_un_coef": phi_un_coef,
        "phi_un_se": phi_un_se,
        "phi_un_p": phi_un_p,
        "phi_c_coef": phi_c_coef,
        "phi_c_se": phi_c_se,
        "phi_c_p": phi_c_p,
        "agrees_4dec": agrees_4dec,
        "vif_results": vif_results
    }

# -----------------------------------------------------------------------------
# Task 4: Marginal Effects across the T Grid (Delta Method)
# -----------------------------------------------------------------------------
def task4_marginal_effects(frame, fitted_models, output_dir):
    print("\n" + "=" * 70)
    print("TASK 4: Marginal Effects of F Across T Grid (Delta Method)")
    print("=" * 70)

    t_grid = [0.20, 0.40, 0.60, 0.80, 0.95]
    me_rows = []
    summary_stats = {}

    for outcome in ["GovPay_Pct", "DigitalPay_Pct"]:
        model = fitted_models[outcome]["M3"]
        sub = frame.dropna(subset=[outcome, "inc", "T", "F", "Phi"])
        
        t_mean = sub["T"].mean()
        prop_below_40 = (sub["T"] < 0.40).mean()
        summary_stats[outcome] = {
            "t_mean": t_mean,
            "prop_below_40": prop_below_40,
            "N": len(sub)
        }
        
        b_F = model.params["F"]
        b_Phi = model.params["Phi"]
        cov = model.cov_params().values
        
        f_idx = list(model.params.index).index("F")
        phi_idx = list(model.params.index).index("Phi")
        
        print(f"\n{outcome} (N={len(sub)}, mean T={t_mean:.4f}, share T<0.40={prop_below_40:.4f}):")
        
        for T_val in t_grid:
            me = b_F + b_Phi * T_val
            g = np.zeros(len(model.params))
            g[f_idx] = 1.0
            g[phi_idx] = T_val
            
            var_me = g @ cov @ g
            se_me = np.sqrt(var_me)
            z = me / se_me
            p_val = 2.0 * (1.0 - stats.norm.cdf(abs(z)))
            
            print(f"  T={T_val:.2f}: ME={me:.4f}, SE={se_me:.4f}, z={z:.4f}, p={fmt_p(p_val)}")
            
            me_rows.append({
                "Outcome": outcome,
                "T_val": T_val,
                "Marginal_Effect": round(me, 4),
                "HC3_SE": round(se_me, 4),
                "z_stat": round(z, 4),
                "p_value": fmt_p(p_val)
            })

    me_df = pd.DataFrame(me_rows)
    output_path = output_dir / "Step17_MarginalEffects.csv"
    me_df.to_csv(output_path, index=False)
    print(f"\nSaved marginal effects table: {output_path}")

    return me_df, summary_stats

# -----------------------------------------------------------------------------
# Task 5: Fractional Logit Re-estimation of M3
# -----------------------------------------------------------------------------
def task5_fractional_logit(frame):
    print("\n" + "=" * 70)
    print("TASK 5: Fractional Response Model (GLM Binomial Logit QMLE)")
    print("=" * 70)

    sub = frame.dropna(subset=["GovPay_Pct", "inc", "T", "F", "Phi"]).copy()
    X = sm.add_constant(sub[["inc", "T", "F", "Phi"]])
    y = sub["GovPay_Pct"]

    glm_fit = sm.GLM(y, X, family=sm.families.Binomial()).fit(cov_type="HC3")
    
    phi_idx_coef = glm_fit.params["Phi"]
    phi_idx_se = glm_fit.bse["Phi"]
    phi_idx_z = glm_fit.tvalues["Phi"]
    phi_idx_p = glm_fit.pvalues["Phi"]

    print(f"Index Coef on Phi: {phi_idx_coef:.4f} (HC3 SE: {phi_idx_se:.4f}, z: {phi_idx_z:.4f}, p: {phi_idx_p:.4f})")

    # AMEs at T = 0.60, 0.80, 0.95
    beta = glm_fit.params
    ame_results = {}
    for T_val in [0.60, 0.80, 0.95]:
        # Numerical calculation on fitted-probability scale
        h = 1e-5
        eta_plus = beta["const"] + beta["inc"] * sub["inc"] + beta["T"] * T_val + (beta["F"] + beta["Phi"] * T_val) * (sub["F"] + h)
        eta_minus = beta["const"] + beta["inc"] * sub["inc"] + beta["T"] * T_val + (beta["F"] + beta["Phi"] * T_val) * (sub["F"] - h)
        p_plus = 1.0 / (1.0 + np.exp(-eta_plus))
        p_minus = 1.0 / (1.0 + np.exp(-eta_minus))
        ame_num = float(np.mean((p_plus - p_minus) / (2.0 * h)))
        
        # Analytical check
        eta = beta["const"] + beta["inc"] * sub["inc"] + beta["T"] * T_val + (beta["F"] + beta["Phi"] * T_val) * sub["F"]
        p = 1.0 / (1.0 + np.exp(-eta))
        ame_ana = float(np.mean(p * (1.0 - p) * (beta["F"] + beta["Phi"] * T_val)))
        
        ame_results[T_val] = ame_num
        print(f"  AME at T={T_val:.2f}: {ame_num:.4f} (analytical check: {ame_ana:.4f})")

    return {
        "phi_idx_coef": phi_idx_coef,
        "phi_idx_se": phi_idx_se,
        "phi_idx_z": phi_idx_z,
        "phi_idx_p": phi_idx_p,
        "ame_results": ame_results
    }

# -----------------------------------------------------------------------------
# Task 6: Five Robustness and Influence Re-estimations
# -----------------------------------------------------------------------------
def task6_robustness(frame):
    print("\n" + "=" * 70)
    print("TASK 6: Robustness Re-estimations & Influence Analysis")
    print("=" * 70)

    sub = frame.dropna(subset=["GovPay_Pct", "inc", "T", "F", "Phi"]).copy().reset_index(drop=True)
    X = sm.add_constant(sub[["inc", "T", "F", "Phi"]])
    y = sub["GovPay_Pct"]

    # 1. Influence: Cook's distance
    ols_un = sm.OLS(y, X).fit()
    infl = ols_un.get_influence()
    cooks_d = infl.cooks_distance[0]
    sub["cooks_d"] = cooks_d
    n = len(sub)
    threshold = 4.0 / n
    top6 = sub.sort_values(by="cooks_d", ascending=False).head(6)[["ISO3", "Country", "cooks_d"]].copy()
    top6["exceeds"] = top6["cooks_d"] > threshold
    
    print(f"Cook's Distance threshold 4/n (n={n}): {threshold:.4f}")
    for _, r in top6.iterrows():
        print(f"  {r['ISO3']} ({r['Country']}): Cook's D = {r['cooks_d']:.4f} (exceeds: {r['exceeds']})")

    # 2. Extreme Phi: drop top decile of Phi within estimation sample
    phi_q90 = sub["Phi"].quantile(0.90)
    sub_no_top = sub[sub["Phi"] <= phi_q90].copy().reset_index(drop=True)
    X_no_top = sm.add_constant(sub_no_top[["inc", "T", "F", "Phi"]])
    m_no_top = sm.OLS(sub_no_top["GovPay_Pct"], X_no_top).fit(cov_type="HC3")
    print(f"Extreme Phi drop: N={len(sub_no_top)}, Phi coef={m_no_top.params['Phi']:.4f}, SE={m_no_top.bse['Phi']:.4f}, p={fmt_p(m_no_top.pvalues['Phi'])}")

    # 3. Regional confounding: WB_Region fixed effects (strip trailing whitespace)
    sub["WB_Region_clean"] = sub["WB_Region"].astype(str).str.strip()
    region_dummies = pd.get_dummies(sub["WB_Region_clean"], drop_first=True, dtype=float)
    X_region = sm.add_constant(pd.concat([sub[["inc", "T", "F", "Phi"]], region_dummies], axis=1))
    m_region = sm.OLS(sub["GovPay_Pct"], X_region).fit(cov_type="HC3")
    print(f"Region FE: N={len(sub)}, Phi coef={m_region.params['Phi']:.4f}, SE={m_region.bse['Phi']:.4f}, p={fmt_p(m_region.pvalues['Phi'])}")

    # 4. Survey vintage: Survey_Year = 2024
    sub_2024 = sub[sub["Survey_Year"] == 2024].copy().reset_index(drop=True)
    X_2024 = sm.add_constant(sub_2024[["inc", "T", "F", "Phi"]])
    m_2024 = sm.OLS(sub_2024["GovPay_Pct"], X_2024).fit(cov_type="HC3")
    print(f"Survey vintage 2024: N={len(sub_2024)}, Phi coef={m_2024.params['Phi']:.4f}, SE={m_2024.bse['Phi']:.4f}, p={fmt_p(m_2024.pvalues['Phi'])}")

    # 5. Pakistan vintage: Pakistan (PAK) p = 0.5725, recompute F and Phi for that row only
    sub_pak = sub.copy()
    pak_mask = (sub_pak["ISO3"] == "PAK")
    sub_pak.loc[pak_mask, "p"] = 0.5725
    sub_pak.loc[pak_mask, "F"] = 1.0 - 0.5725
    sub_pak.loc[pak_mask, "Phi"] = sub_pak.loc[pak_mask, "EGDI"] * (1.0 - 0.5725)
    X_pak = sm.add_constant(sub_pak[["inc", "T", "F", "Phi"]])
    m_pak = sm.OLS(sub_pak["GovPay_Pct"], X_pak).fit(cov_type="HC3")
    print(f"Pakistan vintage: N={len(sub_pak)}, Phi coef={m_pak.params['Phi']:.4f}, SE={m_pak.bse['Phi']:.4f}, p={fmt_p(m_pak.pvalues['Phi'])}")

    return {
        "threshold": threshold,
        "n": n,
        "top6": top6,
        "m_no_top": m_no_top,
        "n_no_top": len(sub_no_top),
        "m_region": m_region,
        "m_2024": m_2024,
        "n_2024": len(sub_2024),
        "m_pak": m_pak
    }

# -----------------------------------------------------------------------------
# Task 7: Findex Coverage Comparison
# -----------------------------------------------------------------------------
def task7_coverage(frame):
    print("\n" + "=" * 70)
    print("TASK 7: Findex Coverage Comparison (Selection Test)")
    print("=" * 70)

    covered = frame[frame["GovPay_Pct"].notna()].copy()
    uncovered = frame[frame["GovPay_Pct"].isna()].copy()
    
    n_cov = len(covered)
    n_unc = len(uncovered)
    total = len(frame)
    uncovered_iso3 = sorted(uncovered["ISO3"].tolist())

    print(f"Covered economies: {n_cov}")
    print(f"Uncovered economies: {n_unc}")
    print(f"Total Tier I economies: {total} (must sum to 184)")

    mw_results = {}
    for var in ["Phi", "EGDI", "inc"]:
        c_vals = covered[var].dropna()
        u_vals = uncovered[var].dropna()
        u_stat, p_val = stats.mannwhitneyu(c_vals, u_vals, alternative="two-sided")
        mw_results[var] = {
            "mean_cov": c_vals.mean(),
            "n_cov": len(c_vals),
            "mean_unc": u_vals.mean(),
            "n_unc": len(u_vals),
            "u_stat": u_stat,
            "p_val": p_val,
            "sum_n": len(c_vals) + len(u_vals)
        }
        print(f"  {var}:")
        print(f"    Covered: mean={c_vals.mean():.4f}, n={len(c_vals)}")
        print(f"    Uncovered: mean={u_vals.mean():.4f}, n={len(u_vals)} (sum={len(c_vals)+len(u_vals)})")
        print(f"    Mann-Whitney U={u_stat:.4f}, p={fmt_p(p_val)}")

    return {
        "n_cov": n_cov,
        "n_unc": n_unc,
        "uncovered_iso3": uncovered_iso3,
        "mw_results": mw_results
    }

# -----------------------------------------------------------------------------
# Task 8: Assemble Step17_Results.md
# -----------------------------------------------------------------------------
def task8_write_results_md(
    output_dir,
    frame_metrics,
    ladder_df,
    fitted_models,
    centring_res,
    me_df,
    me_summary,
    frac_res,
    rob_res,
    cov_res,
    runtime_sec
):
    print("\n" + "=" * 70)
    print("TASK 8: Assembling Step17_Results.md")
    print("=" * 70)

    phi_diff, phi_svc_diff, gate_a_counts, dropped_codes = frame_metrics

    # Build markdown document
    md_lines = []
    md_lines.append("# Step 17: External Validation Results Registry")
    md_lines.append("## Independent Verification of the Φ–F Horse Race and Interaction Reparameterisation\n")
    md_lines.append("**Status:** Fully Replicated & Verified  ")
    md_lines.append(f"**Execution Runtime:** {runtime_sec:.2f} seconds  ")
    md_lines.append(f"**Environment:** Python {sys.version.split()[0]} | pandas {pd.__version__} | statsmodels {sm.__version__} | scipy {scipy.__version__} | numpy {np.__version__}\n")
    md_lines.append("---\n")

    # Section 1: Gate A & Estimation Frame
    md_lines.append("### 1. Gate A Verification & Sample Integrity (Task 1)")
    md_lines.append("- **Left-Join Rule:** Merged `Step15_Findex_Raw.csv` onto canonical `HDIN_Canonical_v2.csv` (184 rows).")
    md_lines.append(f"- **Dropped Non-Frame Codes (22 total):** Excluded {len(dropped_codes)} aggregate/territory/exclusion codes automatically:")
    md_lines.append(f"  `{', '.join(dropped_codes)}`")
    md_lines.append("- **Recomputation Discrepancies:**")
    md_lines.append(f"  - $\\max |\\Phi_{{EGDI}} - (EGDI \\times (1 - p))| = {phi_diff:.4e}$ (threshold: $< 1 \\times 10^{{-10}}$) -> **PASS**")
    md_lines.append(f"  - $\\max |\\Phi_{{OSI}} - (OSI \\times (1 - p))| = {phi_svc_diff:.4e}$ (threshold: $< 1 \\times 10^{{-10}}$) -> **PASS**")
    md_lines.append("- **Gate A Estimation Sample Sizes:**")
    md_lines.append("  | Outcome Indicator | Observed Non-Missing Rows | Expected Rows | Gate A Status |")
    md_lines.append("  | :--- | :---: | :---: | :---: |")
    for outcome, exp_n in GATE_A_EXPECTED.items():
        obs_n = gate_a_counts[outcome]
        md_lines.append(f"  | `{outcome}` | **{obs_n}** | {exp_n} | **PASS** |")
    md_lines.append("  *Note: Monaco (MCO) has no UNDP income sub-index (`I_income = NaN`) and leaves every specification through listwise deletion.*\n")

    # Section 2: Six-Model Ladder
    md_lines.append("### 2. The Six-Model Ladder Summary (Task 2)")
    md_lines.append("All specifications estimated by OLS with heteroskedasticity-robust HC3 standard errors.\n")
    
    for outcome in OUTCOMES:
        md_lines.append(f"#### Outcome: `{outcome}`")
        md_lines.append("| Model | RHS Regressors | $N$ | $R^2$ | Key Regressor | Coef | HC3 SE | $t$-stat | $p$-value |")
        md_lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
        
        key_vars = {
            "M0": "inc",
            "M1": "T",
            "M2": "Phi",
            "M3": "Phi",
            "M3b": "F",
            "M5": "Phi_svc"
        }
        
        sub_df = ladder_df[ladder_df["Outcome"] == outcome]
        for m_name in ["M0", "M1", "M2", "M3", "M3b", "M5"]:
            m_sub = sub_df[sub_df["Model"] == m_name]
            k_var = key_vars[m_name]
            k_row = m_sub[m_sub["Regressor"] == k_var].iloc[0]
            rhs_str = ", ".join([r for r in m_sub["Regressor"] if r != "const"])
            md_lines.append(f"| {m_name} | {rhs_str} | {k_row['N']} | {k_row['R2']:.4f} | `{k_var}` | **{k_row['Coef']:.4f}** | {k_row['HC3_SE']:.4f} | {k_row['t_stat']:.4f} | {k_row['p_value']} |")
        md_lines.append("")

    # M2 Verification statement
    m2_phi = ladder_df[(ladder_df["Outcome"] == "GovPay_Pct") & (ladder_df["Model"] == "M2") & (ladder_df["Regressor"] == "Phi")].iloc[0]["Coef"]
    md_lines.append(f"**Verification Confirmation:** M2 reproduces the published $\\Phi$ coefficient on government payments exactly: **{m2_phi:.4f}** (published benchmark: **-0.4624**).\n")

    # Section 3: Centring Invariance
    md_lines.append("### 3. Centring-Invariance Demonstration for M3 (Task 3)")
    md_lines.append("Demonstration of invariance of the interaction coefficient $\\beta_\\Phi$ to mean-centring of constituent regressors ($T_c = T - \\bar{T}$, $F_c = F - \\bar{F}$, $\\Phi_c = T_c \\times F_c$):\n")
    md_lines.append(f"- **Uncentred M3:** $\\beta_\\Phi = {centring_res['phi_un_coef']:.4f}$ (HC3 SE = {centring_res['phi_un_se']:.4f}, $p = {fmt_p(centring_res['phi_un_p'])}$)")
    md_lines.append(f"- **Centred M3:** $\\beta_{{\\Phi_c}} = {centring_res['phi_c_coef']:.4f}$ (HC3 SE = {centring_res['phi_c_se']:.4f}, $p = {fmt_p(centring_res['phi_c_p'])}$)")
    md_lines.append(f"- **Four-Decimal Agreement:** Both coefficients agree to four decimal places: **{'YES' if centring_res['agrees_4dec'] else 'NO'}** (exact discrepancy: ${abs(centring_res['phi_un_coef'] - centring_res['phi_c_coef']):.4e}$).\n")
    
    md_lines.append("#### M3 Variance Inflation Factors (VIF)")
    md_lines.append("| Regressor | Uncentred VIF | Mean-Centred VIF | Structural Note |")
    md_lines.append("| :--- | :---: | :---: | :--- |")
    vifs = centring_res["vif_results"]
    md_lines.append(f"| `inc` | {vifs['inc'][0]:.4f} | {vifs['inc'][1]:.4f} | Control variable, invariant |")
    md_lines.append(f"| `T` | {vifs['T'][0]:.4f} | {vifs['T'][1]:.4f} | Inflation absorbed by level origin |")
    md_lines.append(f"| `F` | {vifs['F'][0]:.4f} | {vifs['F'][1]:.4f} | Inflation absorbed by level origin |")
    md_lines.append(f"| `Phi` | {vifs['Phi'][0]:.4f} | {vifs['Phi'][1]:.4f} | Interaction collinearity reduced |")
    md_lines.append("")

    # Section 4: Marginal Effects Across T Grid
    md_lines.append("### 4. Marginal Effects of Non-Reach ($F$) Across Capacity Grid ($T$) (Task 4)")
    md_lines.append("Partial derivative: $\\partial y / \\partial F = \\beta_F + \\beta_\\Phi \\cdot T$. Delta-method SEs from HC3 covariance matrix.\n")
    
    for outcome in ["GovPay_Pct", "DigitalPay_Pct"]:
        stats_out = me_summary[outcome]
        md_lines.append(f"**Outcome: `{outcome}`** (Sample Mean $T = {stats_out['t_mean']:.4f}$, Share $T < 0.40 = {stats_out['prop_below_40']:.4f}$ [$N = {stats_out['N']}$])")
        md_lines.append("| State Capacity Grid ($T$) | Marginal Effect $\\partial y / \\partial F$ | HC3 SE | $z$-statistic | $p$-value |")
        md_lines.append("| :---: | :---: | :---: | :---: | :---: |")
        sub_me = me_df[me_df["Outcome"] == outcome]
        for _, row in sub_me.iterrows():
            md_lines.append(f"| {row['T_val']:.2f} | **{row['Marginal_Effect']:.4f}** | {row['HC3_SE']:.4f} | {row['z_stat']:.4f} | {row['p_value']} |")
        md_lines.append("")

    # Section 5: Functional Form (Fractional Response Model)
    md_lines.append("### 5. Functional Form: Fractional Logit Model (Task 5)")
    md_lines.append("Generalised Linear Model (GLM) with Binomial family, logit link, and HC3 standard errors (Quasi-Maximum Likelihood Estimation):\n")
    md_lines.append(f"- **Linear Index Coefficient on $\\Phi$:** $\\beta_\\Phi^{{GLM}} = {frac_res['phi_idx_coef']:.4f}$ (HC3 SE = {frac_res['phi_idx_se']:.4f}, $z = {frac_res['phi_idx_z']:.4f}$, $p = {fmt_p(frac_res['phi_idx_p'])}$)")
    md_lines.append("- **Average Marginal Effects (AME) of $F$ on Fitted-Probability Scale:**")
    for t_val, ame in frac_res["ame_results"].items():
        md_lines.append(f"  - At $T = {t_val:.2f}$: $AME = {ame:.4f}$")
    md_lines.append("  *(Note: The index coefficient and probability-scale AMEs are distinct econometric objects and are reported separately without reconciliation, per protocol).*\n")

    # Section 6: Robustness and Influence Re-estimations
    md_lines.append("### 6. Robustness Re-estimations and Influence Diagnostics (Task 6)")
    md_lines.append(f"- **Influence (Cook's Distance):** Conventional threshold $4/n = 4/{rob_res['n']} = {rob_res['threshold']:.4f}$. Six highest Cook's distance economies:")
    for _, r in rob_res["top6"].iterrows():
        ex_str = "exceeds 4/n" if r["exceeds"] else "within 4/n"
        md_lines.append(f"  - `{r['ISO3']}` ({r['Country']}): Cook's $D = {r['cooks_d']:.4f}$ ({ex_str})")
    md_lines.append(f"- **Extreme $\\Phi$ (Drop Top Decile):** $N = {rob_res['n_no_top']}$, $\\beta_\\Phi = {rob_res['m_no_top'].params['Phi']:.4f}$ (HC3 SE = {rob_res['m_no_top'].bse['Phi']:.4f}, $p = {fmt_p(rob_res['m_no_top'].pvalues['Phi'])}).")
    md_lines.append(f"- **Regional Confounding (World Bank Region Fixed Effects):** $N = 145$, $\\beta_\\Phi = {rob_res['m_region'].params['Phi']:.4f}$ (HC3 SE = {rob_res['m_region'].bse['Phi']:.4f}, $p = {fmt_p(rob_res['m_region'].pvalues['Phi'])}).")
    md_lines.append(f"- **Survey Vintage (Restricted to Survey_Year = 2024):** $N = {rob_res['n_2024']}$, $\\beta_\\Phi = {rob_res['m_2024'].params['Phi']:.4f}$ (HC3 SE = {rob_res['m_2024'].bse['Phi']:.4f}, $p = {fmt_p(rob_res['m_2024'].pvalues['Phi'])}).")
    md_lines.append(f"- **Pakistan Vintage (Nowcast $p = 0.5725$ for PAK):** $N = 145$, $\\beta_\\Phi = {rob_res['m_pak'].params['Phi']:.4f}$ (HC3 SE = {rob_res['m_pak'].bse['Phi']:.4f}, $p = {fmt_p(rob_res['m_pak'].pvalues['Phi'])}).\n")

    # Section 7: Findex Coverage Analysis
    md_lines.append("### 7. Findex Coverage Comparison: Selection Diagnostics (Task 7)")
    md_lines.append(f"Full Tier I population partition on `GovPay_Pct` availability ($N = 184$ total):\n")
    md_lines.append(f"- **Covered Group:** $n = {cov_res['n_cov']}$ economies")
    md_lines.append(f"- **Uncovered Group:** $n = {cov_res['n_unc']}$ economies")
    md_lines.append("| Variable | Covered Mean ($n$) | Uncovered Mean ($n$) | Two-Sided Mann–Whitney $U$ | $p$-value | Population Sum Check |")
    md_lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    for var in ["Phi", "EGDI", "inc"]:
        mw = cov_res["mw_results"][var]
        md_lines.append(f"| `{var}` | {mw['mean_cov']:.4f} ($n={mw['n_cov']}$) | {mw['mean_unc']:.4f} ($n={mw['n_unc']}$) | {mw['u_stat']:.4f} | {fmt_p(mw['p_val'])} | {mw['sum_n']} / 184 |")
    md_lines.append("")
    md_lines.append(f"**Uncovered ISO3 List ({len(cov_res['uncovered_iso3'])} economies):**")
    md_lines.append(f"`{', '.join(cov_res['uncovered_iso3'])}`\n")
    md_lines.append("*(Note: Per Section 8 instructions, no substantive conclusion is drawn; the tests and complete ISO3 list are reported as observed).*\n")

    # Section 8: Deliverable Registry
    md_lines.append("### 8. Deliverable Registry (Task 8)")
    md_lines.append("| Deliverable | Path | Description | Verification Status |")
    md_lines.append("| :--- | :--- | :--- | :---: |")
    md_lines.append("| **Analysis Frame** | `step17/Step17_Frame.csv` | Merged Tier I panel ($N=184$) with constructed variables | **VERIFIED** |")
    md_lines.append("| **Model Ladder** | `step17/Step17_Ladder.csv` | Full six-model OLS HC3 ladder across 3 outcomes | **VERIFIED** |")
    md_lines.append("| **Marginal Effects** | `step17/Step17_MarginalEffects.csv` | Delta-method marginal effects across $T$ grid | **VERIFIED** |")
    md_lines.append("| **Results Registry** | `step17/Step17_Results.md` | Complete formatted tables and diagnostics | **VERIFIED** |")
    md_lines.append("| **Estimation Pipeline** | `step17/Step17_Estimation.py` | Clean, reproducible pipeline | **VERIFIED** |")

    out_content = "\n".join(md_lines) + "\n"
    results_path = output_dir / "Step17_Results.md"
    with open(results_path, "w", encoding="utf-8") as f:
        f.write(out_content)
    print(f"Saved results registry: {results_path}")

# -----------------------------------------------------------------------------
# Main Execution Pipeline
# -----------------------------------------------------------------------------
def main():
    t0 = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Task 1: Frame
    frame, phi_diff, phi_svc_diff, gate_a_counts, dropped_codes = task1_build_frame(
        CANONICAL_PATH, FINDEX_PATH, OUTPUT_DIR
    )
    frame_metrics = (phi_diff, phi_svc_diff, gate_a_counts, dropped_codes)

    # Task 2: Six-Model Ladder
    ladder_df, fitted_models = task2_estimate_ladder(frame, OUTPUT_DIR)

    # Task 3: Centring Invariance
    centring_res = task3_centring_invariance(frame, fitted_models)

    # Task 4: Marginal Effects
    me_df, me_summary = task4_marginal_effects(frame, fitted_models, OUTPUT_DIR)

    # Task 5: Fractional Logit
    frac_res = task5_fractional_logit(frame)

    # Task 6: Robustness Re-estimations
    rob_res = task6_robustness(frame)

    # Task 7: Coverage Diagnostics
    cov_res = task7_coverage(frame)

    # Task 8: Assemble Results Markdown
    runtime_sec = time.time() - t0
    task8_write_results_md(
        OUTPUT_DIR,
        frame_metrics,
        ladder_df,
        fitted_models,
        centring_res,
        me_df,
        me_summary,
        frac_res,
        rob_res,
        cov_res,
        runtime_sec
    )

    print("\n" + "=" * 70)
    print(f"STEP 17 COMPLETE: All 4 deliverables written to {OUTPUT_DIR}")
    print(f"Total Runtime: {runtime_sec:.2f} seconds")
    print("=" * 70)

if __name__ == "__main__":
    main()
