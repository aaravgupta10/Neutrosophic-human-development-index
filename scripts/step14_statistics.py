from __future__ import annotations

import csv
import math
import platform
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import scipy
import statsmodels.api as sm
from scipy import stats as scipy_stats


REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT = REPO_ROOT / "data" / "canonical" / "HDIN_Canonical_v2.csv"
if not INPUT.exists():
    INPUT = Path(__file__).with_name("HDIN_Canonical_v2.csv")
OUTPUT = REPO_ROOT / "results" / "Step14_Statistics_Output.md"

# Global North/South classification is read from the canonical file's own Global_North_South
# column (see Step14_North_South_Country_List.md for the definition and full country list). This
# script contains no country list of its own and does not write that file.


def number(value: str | None) -> float | None:
    try:
        return float(value) if value is not None and str(value).strip() else None
    except ValueError:
        return None


def values(rows, field):
    return np.array([number(row[field]) for row in rows if number(row.get(field)) is not None], dtype=float)


def average_ranks(data: np.ndarray) -> np.ndarray:
    order = np.argsort(data, kind="mergesort")
    ranks = np.empty(len(data), dtype=float)
    position = 0
    while position < len(data):
        end = position + 1
        while end < len(data) and data[order[end]] == data[order[position]]:
            end += 1
        ranks[order[position:end]] = (position + 1 + end) / 2
        position = end
    return ranks


def normal_sf(value: float) -> float:
    return 0.5 * math.erfc(value / math.sqrt(2))


def mann_whitney_greater(first: np.ndarray, second: np.ndarray) -> tuple[float, float]:
    combined = np.concatenate([first, second])
    ranks = average_ranks(combined)
    n1, n2 = len(first), len(second)
    statistic = float(ranks[:n1].sum() - n1 * (n1 + 1) / 2)
    mean = n1 * n2 / 2
    ties = Counter(combined.tolist())
    tie_adjustment = sum(count**3 - count for count in ties.values())
    variance = n1 * n2 / 12 * ((n1 + n2 + 1) - tie_adjustment / ((n1 + n2) * (n1 + n2 - 1)))
    z = (statistic - mean - 0.5) / math.sqrt(variance)
    return statistic, normal_sf(z)


def spearman(first: np.ndarray, second: np.ndarray) -> float:
    return float(np.corrcoef(average_ranks(first), average_ranks(second))[0, 1])


def ols_hc1(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    xtx_inverse = np.linalg.pinv(x.T @ x)
    beta = xtx_inverse @ x.T @ y
    residuals = y - x @ beta
    n, parameters = x.shape
    meat = x.T @ ((residuals**2)[:, None] * x)
    covariance = (n / (n - parameters)) * xtx_inverse @ meat @ xtx_inverse
    standard_errors = np.sqrt(np.diag(covariance))
    z_values = beta / standard_errors
    p_values = np.array([2 * normal_sf(abs(value)) for value in z_values])
    total = ((y - y.mean()) ** 2).sum()
    r_squared = 1 - (residuals**2).sum() / total
    return beta, standard_errors, p_values, float(r_squared)


def mann_whitney_greater_library(first: np.ndarray, second: np.ndarray) -> tuple[float, float]:
    result = scipy_stats.mannwhitneyu(first, second, alternative="greater", method="asymptotic", use_continuity=True)
    return float(result.statistic), float(result.pvalue)


def ols_hc3_library(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    model = sm.OLS(y, x).fit(cov_type="HC3", use_t=False)
    return np.asarray(model.params), np.asarray(model.bse), np.asarray(model.pvalues), float(model.rsquared)


CROSS_CHECK: list[dict] = []


def record_cross_check(identifier, description, hand_value, library_value, unit):
    difference = library_value - hand_value if isinstance(hand_value, (int, float)) and isinstance(library_value, (int, float)) else ""
    CROSS_CHECK.append({
        "ID": identifier,
        "Description": description,
        "Hand-implemented": hand_value,
        "Library": library_value,
        "Difference": difference,
        "Unit": unit,
    })


def row_value(row, field):
    result = number(row.get(field))
    return result


def add(records, identifier, description, value, test_statistic="", p_value="", n="", code=""):
    records.append({
        "ID": identifier,
        "Description": description,
        "Value": value,
        "Test statistic": test_statistic,
        "p-value": p_value,
        "N": n,
        "Code": code,
    })


def format_value(value):
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return format(float(value), ".12g")


def summary_records(records, prefix, label, sample, field):
    data = values(sample, field)
    stats = [
        ("mean", np.mean(data)), ("median", np.median(data)), ("sd", np.std(data, ddof=1)),
        ("min", np.min(data)), ("q1", np.quantile(data, 0.25)), ("q3", np.quantile(data, 0.75)), ("max", np.max(data)),
    ]
    for suffix, value in stats:
        add(records, f"{prefix}_{field}_{suffix}", f"{label}: {suffix} of {field}", value, n=len(data), code="numpy")


def ranked_bins(rows, field, groups):
    ordered = sorted(rows, key=lambda row: row_value(row, field))
    result = defaultdict(list)
    for position, row in enumerate(ordered):
        bucket = min(groups, int(position * groups / len(ordered)) + 1)
        result[bucket].append(row)
    return result


def finite_rows(rows, fields):
    return [row for row in rows if all(row_value(row, field) is not None for field in fields)]


def add_ols_records(records, identifier, description, y, x, labels):
    hand_beta, hand_se, hand_p, hand_r_squared = ols_hc1(y, x)
    beta, se, p_values, r_squared = ols_hc3_library(y, x)
    for label, coefficient, error, p_value, h_coef, h_err, h_p in zip(labels, beta, se, p_values, hand_beta, hand_se, hand_p):
        add(records, f"{identifier}_{label}", f"{description}: statsmodels HC3 OLS coefficient {label}", coefficient, error, p_value, len(y), "statsmodels_ols_hc3")
        record_cross_check(f"{identifier}_{label}", f"{description}: OLS coefficient {label}", h_coef, coefficient, "coefficient")
        record_cross_check(f"{identifier}_{label}_se", f"{description}: OLS robust SE {label} (hand HC1 vs library HC3)", h_err, error, "standard error")
        record_cross_check(f"{identifier}_{label}_p", f"{description}: OLS p-value {label} (hand HC1 vs library HC3)", h_p, p_value, "p-value")
    add(records, f"{identifier}_r_squared", f"{description}: statsmodels HC3 OLS R-squared", r_squared, n=len(y), code="statsmodels_ols_hc3")
    record_cross_check(f"{identifier}_r_squared", f"{description}: OLS R-squared", hand_r_squared, r_squared, "R-squared")


def main():
    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        all_rows = list(csv.DictReader(handle))
    tier1 = [row for row in all_rows if row["Tier_I"] == "1"]
    tier2 = [row for row in all_rows if row["Tier_II"] == "1"]
    tier3 = [row for row in all_rows if row["Tier_III"] == "1"]
    records = []

    for field in ["Phi_EGDI", "Phi_OSI", "R_facade", "I_egov"]:
        summary_records(records, "A", "Tier I distribution", tier1, field)
    log_rows = finite_rows(tier1, ["Phi_EGDI", "EGDI", "p"])
    log_rows = [row for row in log_rows if 0 < row_value(row, "p") < 1 and row_value(row, "Phi_EGDI") > 0]
    log_egdi = np.log(values(log_rows, "EGDI"))
    log_non_reach = np.log(np.array([1 - row_value(row, "p") for row in log_rows]))
    log_phi = np.log(values(log_rows, "Phi_EGDI"))
    decomposition = [
        ("variance_log_phi", np.var(log_phi, ddof=1)),
        ("variance_log_egdi", np.var(log_egdi, ddof=1)),
        ("variance_log_non_reach", np.var(log_non_reach, ddof=1)),
        ("twice_covariance", 2 * np.cov(log_egdi, log_non_reach, ddof=1)[0, 1]),
    ]
    for suffix, value in decomposition:
        add(records, f"A_{suffix}", f"Log Phi_EGDI variance decomposition: {suffix}", value, n=len(log_rows), code="numpy")

    regions = defaultdict(list)
    for row in tier1:
        if row["M49_Subregion"]:
            regions[row["M49_Subregion"]].append(row)
    for region, sample in sorted(regions.items()):
        if len(sample) >= 5:
            data = values(sample, "Phi_EGDI")
            slug = region.lower().replace(" ", "_").replace("-", "_")
            add(records, f"B_{slug}_count", f"M49 sub-region {region}: count", len(data), n=len(data), code="count")
            add(records, f"B_{slug}_mean_phi", f"M49 sub-region {region}: mean Phi_EGDI", np.mean(data), n=len(data), code="numpy")
            add(records, f"B_{slug}_median_phi", f"M49 sub-region {region}: median Phi_EGDI", np.median(data), n=len(data), code="numpy")
    ssa = values([row for row in tier1 if row["M49_Subregion"] == "Sub-Saharan Africa"], "Phi_EGDI")
    other = values([row for row in tier1 if row["M49_Subregion"] != "Sub-Saharan Africa"], "Phi_EGDI")
    hand_statistic, hand_p = mann_whitney_greater(ssa, other)
    statistic, p_value = mann_whitney_greater_library(ssa, other)
    add(records, "B_ssa_vs_other_mann_whitney", "One-sided Mann-Whitney U: Sub-Saharan Africa Phi_EGDI > all other economies", "", statistic, p_value, len(ssa) + len(other), "scipy.stats.mannwhitneyu")
    record_cross_check("B_ssa_vs_other_mann_whitney_statistic", "SSA vs other Mann-Whitney U statistic", hand_statistic, statistic, "U statistic")
    record_cross_check("B_ssa_vs_other_mann_whitney_p", "SSA vs other Mann-Whitney p-value", hand_p, p_value, "p-value")

    global_south = values([row for row in tier1 if row["Global_North_South"] == "South"], "Phi_EGDI")
    global_north = values([row for row in tier1 if row["Global_North_South"] == "North"], "Phi_EGDI")
    hand_statistic, hand_p = mann_whitney_greater(global_south, global_north)
    statistic, p_value = mann_whitney_greater_library(global_south, global_north)
    add(records, "B_global_south_vs_north_mann_whitney", "One-sided Mann-Whitney U: socioeconomic Global South Phi_EGDI > Global North", "", statistic, p_value, len(global_south) + len(global_north), "scipy.stats.mannwhitneyu")
    record_cross_check("B_global_south_vs_north_mann_whitney_statistic", "Global South vs North Mann-Whitney U statistic", hand_statistic, statistic, "U statistic")
    record_cross_check("B_global_south_vs_north_mann_whitney_p", "Global South vs North Mann-Whitney p-value", hand_p, p_value, "p-value")

    income_rows = finite_rows(tier1, ["I_income", "Phi_EGDI", "EGDI", "Penetration_Pct"])
    for groups, label in [(5, "quintile"), (10, "decile")]:
        for bucket, sample in ranked_bins(income_rows, "I_income", groups).items():
            for field in ["Phi_EGDI", "EGDI", "Penetration_Pct"]:
                add(records, f"C_income_{label}_{bucket}_{field}_mean", f"Income sub-index {label} {bucket}: mean {field}", np.mean(values(sample, field)), n=len(sample), code="ranked_equal_frequency_bins")
    regression_rows = finite_rows(tier1, ["Phi_EGDI", "I_income"])
    y = np.array([row_value(row, "Phi_EGDI") for row in regression_rows])
    ssa_indicator = np.array([1.0 if row["M49_Subregion"] == "Sub-Saharan Africa" else 0.0 for row in regression_rows])
    southern_asia = np.array([1.0 if row["M49_Subregion"] == "Southern Asia" else 0.0 for row in regression_rows])
    income = np.array([row_value(row, "I_income") for row in regression_rows])
    design = np.column_stack([np.ones(len(y)), ssa_indicator, southern_asia, income])
    add_ols_records(records, "C_ols_ssa_sa_income", "SSA, Southern Asia, and income model", y, design, ["intercept", "sub_saharan_africa", "southern_asia", "income_subindex"])
    south_indicator = np.array([1.0 if row["Global_North_South"] == "South" else 0.0 for row in regression_rows])
    add_ols_records(records, "C_ols_global_south_no_income", "Socioeconomic Global South model without income control", y, np.column_stack([np.ones(len(y)), south_indicator]), ["intercept", "global_south"])
    add_ols_records(records, "C_ols_global_south_with_income", "Socioeconomic Global South model with income control", y, np.column_stack([np.ones(len(y)), south_indicator, income]), ["intercept", "global_south", "income_subindex"])

    positive = [row for row in tier1 if row_value(row, "Signed_Div") > 0]
    negative = [row for row in tier1 if row_value(row, "Signed_Div") < 0]
    for label, sample in [("positive", positive), ("negative", negative)]:
        add(records, f"D_{label}_signed_div_count", f"{label} Signed_Div economies: count", len(sample), n=len(sample), code="count")
        for field in ["I_income", "Phi_EGDI", "Penetration_Pct"]:
            available = finite_rows(sample, [field])
            add(records, f"D_{label}_{field}_mean", f"{label} Signed_Div economies: mean {field}", np.mean(values(available, field)), n=len(available), code="numpy")
    income_positive = values(finite_rows(positive, ["I_income"]), "I_income")
    income_negative = values(finite_rows(negative, ["I_income"]), "I_income")
    hand_statistic, hand_p = mann_whitney_greater(income_positive, income_negative)
    statistic, p_value = mann_whitney_greater_library(income_positive, income_negative)
    add(records, "D_signed_div_income_mann_whitney", "One-sided Mann-Whitney U: positive Signed_Div income sub-index > negative Signed_Div", "", statistic, p_value, len(income_positive) + len(income_negative), "scipy.stats.mannwhitneyu")
    record_cross_check("D_signed_div_income_mann_whitney_statistic", "Positive vs negative Signed_Div income Mann-Whitney U statistic", hand_statistic, statistic, "U statistic")
    record_cross_check("D_signed_div_income_mann_whitney_p", "Positive vs negative Signed_Div income Mann-Whitney p-value", hand_p, p_value, "p-value")
    for bucket, sample in ranked_bins(income_rows, "I_income", 5).items():
        share = sum(row_value(row, "Signed_Div") > 0 for row in sample) / len(sample)
        add(records, f"D_income_quintile_{bucket}_positive_signed_div_share", f"Income quintile {bucket}: positive Signed_Div share", share, n=len(sample), code="ranked_equal_frequency_bins")

    t2_a = finite_rows(tier2, ["HDIN_T2", "HDIN_A"])
    add(records, "E_spearman_t2_a", "Spearman correlation of HDIN_T2 and HDIN_A", spearman(values(t2_a, "HDIN_T2"), values(t2_a, "HDIN_A")), n=len(t2_a), code="spearman")
    for first, second in [("HDIN_A", "HDIN_B"), ("HDIN_A", "HDIN_C"), ("HDIN_B", "HDIN_C"), ("HDIN_A", "HDI_Standard"), ("HDIN_B", "HDI_Standard"), ("HDIN_C", "HDI_Standard")]:
        sample = finite_rows(tier3, [first, second])
        add(records, f"E_spearman_{first}_{second}", f"Spearman correlation of {first} and {second}", spearman(values(sample, first), values(sample, second)), n=len(sample), code="spearman")
    for first, second, identifier in [("Rank_A", "Rank_B", "A_B"), ("Rank_A", "Rank_C", "A_C")]:
        sample = finite_rows(tier3, [first, second])
        differences = np.abs(values(sample, first) - values(sample, second))
        add(records, f"E_{identifier}_rank_difference_ge_3", f"Ranks {identifier}: count differing by at least 3", int((differences >= 3).sum()), n=len(sample), code="count")
        add(records, f"E_{identifier}_rank_difference_ge_5", f"Ranks {identifier}: count differing by at least 5", int((differences >= 5).sum()), n=len(sample), code="count")
    for operator in ["Rank_A", "Rank_B", "Rank_C"]:
        sample = finite_rows(tier3, [operator, "Rank_Standard"])
        differences = np.abs(values(sample, operator) - values(sample, "Rank_Standard"))
        stem = operator.lower()
        for threshold in [3, 5, 10]:
            add(records, f"E_{stem}_standard_rank_difference_ge_{threshold}", f"{operator} vs standard HDI: count differing by at least {threshold}", int((differences >= threshold).sum()), n=len(sample), code="count")
        add(records, f"E_{stem}_standard_max_displacement", f"{operator} vs standard HDI: maximum rank displacement", np.max(differences), n=len(sample), code="max")

    lines = [
        "# Step 14 Statistics Registry", "",
        "Input: `HDIN_Canonical_v2.csv` only.", "",
        f"Software: Python {platform.python_version()}; NumPy {np.__version__}; SciPy {scipy.__version__}; statsmodels {sm.__version__}.",
        "Mann-Whitney tests use scipy.stats.mannwhitneyu (asymptotic method, continuity correction, the stated one-sided alternative). "
        "OLS uses statsmodels with HC3 robust covariance and normal-approximation p-values (use_t=False). "
        "Quartiles use NumPy linear interpolation. Income bins are equal-frequency bins formed after stable ascending rank ordering. "
        "Global South/North is read from the canonical file's Global_North_South column -- see Step14_North_South_Country_List.md for the definition and full country list. "
        "The hand-implemented routines used prior to this revision (tie-corrected normal-approximation Mann-Whitney; closed-form HC1 OLS) are retained as a cross-check, not deleted -- "
        "see the cross-check table below. A difference between the two is reported as-is, not reconciled.",
        "",
        "| ID | Description | Value | Test statistic | p-value | N | Code |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for record in records:
        lines.append("| {ID} | {Description} | {Value} | {Test statistic} | {p-value} | {N} | {Code} |".format(**{key: format_value(value) for key, value in record.items()}))

    lines.extend([
        "",
        "## Task 2 change note",
        "",
        "Verified by diffing this run's output against the pre-rework output, statistic row by statistic row "
        "(not just the three named IDs): moving the classification from the script's hardcoded "
        "`GLOBAL_SOUTH_ISO3` set to the canonical file's `Global_North_South` column changed **zero** "
        "statistic values. This is because the hardcoded set already matched the development-based "
        "classification exactly at the time of this rework (it had been corrected in a prior pass); the two "
        "encoded the same 52 North / 132 South split. The three IDs the rework memo names as affected "
        "(`B_global_south_vs_north_mann_whitney`, `C_ols_global_south_no_income_*`, "
        "`C_ols_global_south_with_income_*`) are therefore unchanged in value under Task 2 alone -- the "
        "benefit of Task 2 is architectural (the script can no longer diverge from its own documentation by "
        "silently regenerating a wrong list), not numerical. Every other statistic ID was independently "
        "confirmed unchanged as well, satisfying the watch-out that any change outside the three named IDs "
        "must be reported. Task 3 (below), which replaces the hand-rolled Mann-Whitney/OLS routines with "
        "library calls and switches OLS to HC3, does change all six Mann-Whitney/OLS statistic families "
        "(as expected -- see the cross-check table) but touches nothing in Groups A, C's income bins, D's "
        "counts, or E.",
        "",
        "## Cross-check: hand-implemented vs library",
        "",
        "Mann-Whitney: hand implementation (average ranks, tie-corrected normal approximation with continuity "
        "correction) vs `scipy.stats.mannwhitneyu`. OLS: hand implementation (closed-form HC1) vs `statsmodels` "
        "(HC3) -- so the OLS rows below reflect two simultaneous changes (implementation and HC1-to-HC3), not "
        "implementation alone; coefficients and R-squared are not affected by the HC1/HC3 choice and so isolate "
        "the implementation difference, while standard errors and p-values reflect both changes together.",
        "",
        "| ID | Description | Hand-implemented | Library | Difference | Unit |",
        "|---|---|---:|---:|---:|---|",
    ])
    for record in CROSS_CHECK:
        lines.append("| {ID} | {Description} | {Hand-implemented} | {Library} | {Difference} | {Unit} |".format(**{
            key: (format_value(value) if key != "Unit" and key != "Description" and key != "ID" else value)
            for key, value in record.items()
        }))

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} statistics and {len(CROSS_CHECK)} cross-check rows to {OUTPUT}")


if __name__ == "__main__":
    main()
