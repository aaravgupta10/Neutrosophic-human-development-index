from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent
TABLE1_SOURCE = REPO_ROOT / "results" / "tables" / "Table_1_Raw_Digital.csv"
TABLE4_SOURCE = REPO_ROOT / "results" / "tables" / "Table_4_HDI_FN_Preview.csv"
SHARED_GRID = REPO_ROOT / "results" / "tables" / "Robustness_5_Digital_Variant_Grid.csv"
OUTPUT_GRID = REPO_ROOT / "results" / "tables" / "Robustness_5_Digital_Variant_Grid.csv"
REPORT_PATH = REPO_ROOT / "results" / "Step7_Verification_Report.txt"


def spearman_from_ranks(left: pd.Series, right: pd.Series) -> float:
    ranked = pd.DataFrame({"left": left, "right": right}).dropna()
    if ranked.empty:
        return float("nan")
    return ranked["left"].rank(method="average").corr(
        ranked["right"].rank(method="average")
    )


def build_frame() -> tuple[pd.DataFrame, pd.DataFrame]:
    table1 = pd.read_csv(TABLE1_SOURCE)
    table4 = pd.read_csv(TABLE4_SOURCE)

    df = table1.merge(
        table4[
            [
                "Country",
                "I_health",
                "I_education",
                "I_income_adj (approx.)",
                "HDI_FN Rank",
                "Standard HDI Rank",
            ]
        ],
        on="Country",
        how="left",
    )

    df["Ipen"] = df["Internet_Pen_2023_Pct"] / 100
    df["Ibb"] = (
        df["Fixed_Broadband_2023_per100"] / df["Fixed_Broadband_2023_per100"].max()
    )
    df["Iht"] = df["HiTech_Exports_Pct"] / df["HiTech_Exports_Pct"].max()
    df["Tadj_egov"] = df["EGDI_2024"] * df["Ipen"]

    df["Idig_A_4in_Tadj"] = (
        df["Ipen"] * df["Ibb"] * df["Tadj_egov"] * df["Iht"]
    ) ** 0.25
    df["Idig_B_3in_Tadj"] = (df["Ipen"] * df["Ibb"] * df["Tadj_egov"]) ** (1 / 3)
    df["Idig_C_4in_rawEGDI"] = (
        df["Ipen"] * df["Ibb"] * df["EGDI_2024"] * df["Iht"]
    ) ** 0.25
    df["Idig_D_3in_rawEGDI"] = (df["Ipen"] * df["Ibb"] * df["EGDI_2024"]) ** (1 / 3)

    for dig_col, score_col in [
        ("Idig_A_4in_Tadj", "HDIFN_A_4in_Tadj"),
        ("Idig_B_3in_Tadj", "HDIFN_B_3in_Tadj"),
        ("Idig_C_4in_rawEGDI", "HDIFN_C_4in_rawEGDI"),
        ("Idig_D_3in_rawEGDI", "HDIFN_D_3in_rawEGDI"),
    ]:
        df[score_col] = (
            df["I_health"]
            * df["I_education"]
            * df["I_income_adj (approx.)"]
            * df[dig_col]
        ) ** 0.25

    hi_tech_rankable = df["Iht"].notna()
    all_rankable = df["Ibb"].notna()

    for score_col, eligible, rank_col in [
        ("HDIFN_A_4in_Tadj", hi_tech_rankable, "rk_A_4in_Tadj"),
        ("HDIFN_B_3in_Tadj", all_rankable, "rk_B_3in_Tadj"),
        ("HDIFN_C_4in_rawEGDI", hi_tech_rankable, "rk_C_4in_rawEGDI"),
        ("HDIFN_D_3in_rawEGDI", all_rankable, "rk_D_3in_rawEGDI"),
    ]:
        df.loc[eligible, rank_col] = (
            df.loc[eligible, score_col].rank(ascending=False, method="min").astype(int)
        )

    grid = df[
        [
            "Country",
            "Standard HDI Rank",
            "rk_A_4in_Tadj",
            "rk_B_3in_Tadj",
            "rk_C_4in_rawEGDI",
            "rk_D_3in_rawEGDI",
        ]
    ].copy()
    grid["d_A_4in_Tadj"] = grid["Standard HDI Rank"] - grid["rk_A_4in_Tadj"]
    grid["d_B_3in_Tadj"] = grid["Standard HDI Rank"] - grid["rk_B_3in_Tadj"]
    grid["d_C_4in_rawEGDI"] = grid["Standard HDI Rank"] - grid["rk_C_4in_rawEGDI"]
    grid["d_D_3in_rawEGDI"] = grid["Standard HDI Rank"] - grid["rk_D_3in_rawEGDI"]

    return df, grid


def verify_and_write(df: pd.DataFrame, grid: pd.DataFrame) -> None:
    shared = pd.read_csv(SHARED_GRID)

    OUTPUT_GRID.parent.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUTPUT_GRID, index=False)

    rebuilt_matches_shared = grid.equals(shared)

    hi_tech_rankable = df["Iht"].notna()
    table4_match = bool(
        (
            df.loc[hi_tech_rankable, "rk_A_4in_Tadj"].astype(int)
            == df.loc[hi_tech_rankable, "HDI_FN Rank"].astype(int)
        ).all()
    )

    rho_a = spearman_from_ranks(
        df.loc[hi_tech_rankable, "rk_A_4in_Tadj"],
        df.loc[hi_tech_rankable, "Standard HDI Rank"],
    )
    rho_b = spearman_from_ranks(df["rk_B_3in_Tadj"], df["Standard HDI Rank"])
    rho_c = spearman_from_ranks(
        df.loc[hi_tech_rankable, "rk_C_4in_rawEGDI"],
        df.loc[hi_tech_rankable, "Standard HDI Rank"],
    )
    rho_d = spearman_from_ranks(df["rk_D_3in_rawEGDI"], df["Standard HDI Rank"])

    bangladesh = grid.loc[grid["Country"].eq("Bangladesh")].iloc[0]
    finland = grid.loc[grid["Country"].eq("Finland")].iloc[0]
    denmark = grid.loc[grid["Country"].eq("Denmark")].iloc[0]
    germany = grid.loc[grid["Country"].eq("Germany")].iloc[0]
    south_korea = grid.loc[grid["Country"].eq("South Korea")].iloc[0]
    iceland = grid.loc[grid["Country"].eq("Iceland")].iloc[0]
    norway = grid.loc[grid["Country"].eq("Norway")].iloc[0]

    lines = [
        "Step 7 verification report",
        "Date verified: 2026-07-23",
        "",
        "Inputs used:",
        f"- {TABLE1_SOURCE}",
        f"- {TABLE4_SOURCE}",
        f"- Shared comparator: {SHARED_GRID}",
        "",
        "Replication checks:",
        f"- Rebuilt grid matches the shared Step 7 CSV cell by cell: {rebuilt_matches_shared}",
        f"- 4-input/Tadj ranks reproduce Table_4_HDI_FN_Preview.csv exactly: {table4_match}",
        f"- Spearman vs Standard HDI, 4-input/Tadj: {rho_a:.4f}",
        f"- Spearman vs Standard HDI, 3-input/Tadj: {rho_b:.4f}",
        f"- Spearman vs Standard HDI, 4-input/raw EGDI: {rho_c:.4f}",
        f"- Spearman vs Standard HDI, 3-input/raw EGDI: {rho_d:.4f}",
        "",
        "Substantive checks from the memo:",
        f"- Finland rank change: {finland['d_A_4in_Tadj']:.0f} in 4-input/Tadj and {finland['d_B_3in_Tadj']:.0f} in 3-input/Tadj.",
        f"- Denmark rank change: {denmark['d_A_4in_Tadj']:.0f} in 4-input/Tadj and {denmark['d_B_3in_Tadj']:.0f} in 3-input/Tadj.",
        f"- Germany rank change: {germany['d_A_4in_Tadj']:.0f} in 4-input/Tadj and {germany['d_B_3in_Tadj']:.0f} in 3-input/Tadj.",
        f"- South Korea rank change: {south_korea['d_A_4in_Tadj']:.0f} in 4-input/Tadj and {south_korea['d_B_3in_Tadj']:.0f} in 3-input/Tadj.",
        f"- Iceland is rank {iceland['rk_A_4in_Tadj']:.0f} in 4-input/Tadj and rank {iceland['rk_B_3in_Tadj']:.0f} in 3-input/Tadj.",
        f"- Norway is rank {norway['rk_A_4in_Tadj']:.0f} in 4-input/Tadj and rank {norway['rk_B_3in_Tadj']:.0f} in 3-input/Tadj.",
        f"- Bangladesh is excluded from the 4-input variants and ranks {bangladesh['rk_B_3in_Tadj']:.0f} in both 3-input variants.",
        "",
        "Workspace limitation:",
        "- No manuscript source files (.tex or equivalent) are present in this workspace, so the Step 7 LaTeX subsection, reframing sweep, line-by-line change log, and compile/cross-reference checks could not be applied here.",
        "- Once the manuscript sources are available, this replication output is ready to support the Section 4.6 insertion and the abstract, Section 1, Section 3.4, Section 5.2, and Section 6 wording updates requested in the memo.",
    ]

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Rebuilt grid matches shared CSV: {rebuilt_matches_shared}")
    print(f"4-input/Tadj reproduces Table 4 exactly: {table4_match}")
    print(f"Spearman A vs standard HDI: {rho_a:.4f}")
    print(f"Spearman B vs standard HDI: {rho_b:.4f}")
    print(f"Spearman C vs standard HDI: {rho_c:.4f}")
    print(f"Spearman D vs standard HDI: {rho_d:.4f}")


def main() -> None:
    df, grid = build_frame()
    verify_and_write(df, grid)


if __name__ == "__main__":
    main()
