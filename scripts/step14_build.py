from __future__ import annotations

import csv
import math
from collections import Counter
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path


getcontext().prec = 50

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUTS_DIR = REPO_ROOT / "data" / "inputs"
CANONICAL_DIR = REPO_ROOT / "data" / "canonical"
ROOT = INPUTS_DIR

CANONICAL_COLUMNS = [
    "ISO3", "Country", "M49_Region", "M49_Subregion", "WB_Region", "EGDI", "OSI", "TII", "HCI",
    "Penetration_Pct", "Penetration_Year", "p", "Broadband_per100", "Broadband_Year", "HiTech_Pct",
    "HiTech_Year", "I_pen", "I_bb", "I_ht", "T_adj_EGDI", "T_adj_OSI", "Phi_EGDI", "Phi_OSI",
    "R_facade", "I_egov", "Signed_Div", "I_health", "I_education", "I_income", "HDI_Standard",
    "Rank_Standard", "Tier_I", "Tier_II", "Tier_III", "Exclusion_Reason", "I_bb_T2", "I_digital_T2",
    "HDIN_T2", "Rank_T2", "I_digital_A", "HDIN_A", "Rank_A", "I_digital_B", "HDIN_B", "Rank_B",
    "I_digital_C", "HDIN_C", "Rank_C",
]


def read_csv(name: str) -> list[dict[str, str]]:
    p = ROOT / name
    if not p.exists():
        p = REPO_ROOT / name
    if not p.exists():
        p = REPO_ROOT / "results" / "tables" / Path(name).name
    if not p.exists():
        p = REPO_ROOT / "data" / "inputs" / Path(name).name
    with p.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["ISO3"]: row for row in rows if row.get("ISO3")}


def decimal(value: str | None) -> Decimal | None:
    if value is None or not str(value).strip():
        return None
    try:
        return Decimal(str(value).strip())
    except InvalidOperation:
        return None


def present_positive(value: str | None) -> bool:
    number = decimal(value)
    return number is not None and number > 0


def floating(value: float) -> str:
    return format(value, ".17g")


def ranked_min(rows: list[dict[str, str]], field: str, rank_field: str) -> None:
    ordered = sorted(rows, key=lambda row: float(row[field]), reverse=True)
    previous = None
    rank = 0
    for position, row in enumerate(ordered, start=1):
        value = float(row[field])
        if previous is None or value != previous:
            rank = position
            previous = value
        row[rank_field] = str(rank)


def write_csv(name: str, rows: list[dict[str, str]], columns: list[str]) -> None:
    out_dir = CANONICAL_DIR if "Canonical" in name else ROOT
    with (out_dir / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(name: str, lines: list[str]) -> None:
    out_dir = CANONICAL_DIR if "List" in name or "Provenance" in name else (REPO_ROOT / "results")
    (out_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_canonical() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    facade = [row for row in read_csv("Step12_Facade_Full_Population.csv") if decimal(row["Phi_EGDI"]) is not None]
    egdi_full = index(read_csv("Step12_EGDI_2024_Full.csv"))
    regions = index(read_csv("Step13_Region_Lookup.csv"))
    hdr = index(read_csv("Step13_HDR_Dimensions_Full.csv"))
    broadband = index(read_csv("Step13_ITU_Broadband_Full.csv"))
    hitech = index(read_csv("Step13_WDI_HiTech_Full.csv"))
    master = index(read_csv("Step13_Master_Inputs.csv"))
    operators = index(read_csv("Step13_HDIN_Operators.csv"))

    rows: list[dict[str, str]] = []
    for source in facade:
        iso3 = source["ISO3"]
        region = regions.get(iso3, {})
        egdi_source = egdi_full.get(iso3, {})
        hdi = hdr.get(iso3, {})
        bb = broadband.get(iso3, {})
        ht = hitech.get(iso3, {})
        legacy_master = master.get(iso3, {})
        operator = operators.get(iso3, {})
        row = {
            "ISO3": iso3,
            "Country": source["Country"],
            "M49_Region": region.get("M49_Region", ""),
            "M49_Subregion": region.get("M49_Subregion", ""),
            "WB_Region": region.get("WB_Region", ""),
            "EGDI": egdi_source.get("EGDI", source["EGDI"]), "OSI": egdi_source.get("OSI", source["OSI"]),
            "TII": egdi_source.get("TII", source["TII"]), "HCI": egdi_source.get("HCI", source["HCI"]),
            "Penetration_Pct": source["Penetration_Pct"], "Penetration_Year": source["Year_Used"], "p": source["p"],
            "Broadband_per100": bb.get("Broadband_per100", ""), "Broadband_Year": bb.get("Year_Used", ""),
            "HiTech_Pct": ht.get("HiTech_Pct", ""), "HiTech_Year": ht.get("Year_Used", ""),
            "I_pen": source["p"], "I_bb": legacy_master.get("I_bb", ""), "I_ht": legacy_master.get("I_ht", ""),
            "T_adj_EGDI": source["T_adj_EGDI"], "T_adj_OSI": source["T_adj_OSI"], "Phi_EGDI": source["Phi_EGDI"],
            "Phi_OSI": source["Phi_OSI"], "R_facade": source["R_facade"], "I_egov": source["I_egov"],
            "Signed_Div": source["Signed_Div"], "I_health": hdi.get("I_health", ""),
            "I_education": hdi.get("I_education", ""), "I_income": hdi.get("I_income", ""),
            "HDI_Standard": hdi.get("HDI_Standard", ""), "Rank_Standard": hdi.get("HDI_Rank_Standard", ""),
            "Tier_I": "1", "Tier_II": "0", "Tier_III": "0", "Exclusion_Reason": "",
            "I_bb_T2": "", "I_digital_T2": "", "HDIN_T2": "", "Rank_T2": "",
            "I_digital_A": operator.get("I_digital_A", ""), "HDIN_A": operator.get("HDIN_A", ""), "Rank_A": operator.get("Rank_A", ""),
            "I_digital_B": operator.get("I_digital_B", ""), "HDIN_B": operator.get("HDIN_B", ""), "Rank_B": operator.get("Rank_B", ""),
            "I_digital_C": operator.get("I_digital_C", ""), "HDIN_C": operator.get("HDIN_C", ""), "Rank_C": operator.get("Rank_C", ""),
        }
        hdi_fields = ["I_health", "I_education", "I_income"]
        tier2 = present_positive(row["Broadband_per100"]) and all(decimal(row[field]) is not None for field in hdi_fields)
        row["Tier_II"] = "1" if tier2 else "0"
        tier3 = tier2 and present_positive(row["HiTech_Pct"])
        row["Tier_III"] = "1" if tier3 else "0"
        if not tier3:
            if not present_positive(row["Broadband_per100"]):
                row["Exclusion_Reason"] = "Broadband_per100 missing or non-positive"
            elif decimal(row["I_health"]) is None:
                row["Exclusion_Reason"] = "I_health missing"
            elif decimal(row["I_education"]) is None:
                row["Exclusion_Reason"] = "I_education missing"
            elif decimal(row["I_income"]) is None:
                row["Exclusion_Reason"] = "I_income missing"
            else:
                row["Exclusion_Reason"] = "HiTech_Pct missing or non-positive"
        rows.append(row)

    tier2_rows = [row for row in rows if row["Tier_II"] == "1"]
    broadband_max = max(decimal(row["Broadband_per100"]) for row in tier2_rows)
    for row in tier2_rows:
        i_bb = float(decimal(row["Broadband_per100"]) / broadband_max)
        digital = (float(decimal(row["I_pen"])) * i_bb * float(decimal(row["T_adj_EGDI"]))) ** (1 / 3)
        hdin = (float(decimal(row["I_health"])) * float(decimal(row["I_education"])) * float(decimal(row["I_income"])) * digital) ** 0.25
        row["I_bb_T2"] = floating(i_bb)
        row["I_digital_T2"] = floating(digital)
        row["HDIN_T2"] = floating(hdin)
    ranked_min(tier2_rows, "HDIN_T2", "Rank_T2")
    rows.sort(key=lambda row: decimal(row["Phi_EGDI"]), reverse=True)
    write_csv("HDIN_Canonical_v1.csv", rows, CANONICAL_COLUMNS)
    return rows, facade


def gate_report(canonical: list[dict[str, str]], facade: list[dict[str, str]]) -> None:
    source = index(facade)
    deviations = {key: Decimal(0) for key in ["Phi_EGDI", "Phi_OSI", "R_facade", "I_egov", "Signed_Div"]}
    for row in canonical:
        egdi, osi, tii, p = (decimal(row[key]) for key in ["EGDI", "OSI", "TII", "p"])
        recomputed = {
            "Phi_EGDI": egdi * (Decimal(1) - p),
            "Phi_OSI": osi * (Decimal(1) - p),
            "R_facade": Decimal(1) / p,
            "I_egov": abs(osi - tii),
            "Signed_Div": osi - tii,
        }
        for key, value in recomputed.items():
            deviations[key] = max(deviations[key], abs(value - decimal(source[row["ISO3"]][key])))
    lines = ["# Step 14 Task 1 Reproduction Gate", "", f"Canonical rows with computable Phi_EGDI: {len(canonical)}.", "", "| Quantity | Maximum absolute deviation | Gate |", "|---|---:|---|"]
    for key, value in deviations.items():
        lines.append(f"| {key} | {value} | {'PASS' if value <= Decimal('1e-9') else 'FAIL'} |")
    lines.extend(["", "All five values were recomputed solely from EGDI, OSI, TII, and p, then compared against Step12_Facade_Full_Population.csv."])
    write_markdown("Step14_Task1_Reproduction_Gate.md", lines)


def tier_report(rows: list[dict[str, str]]) -> None:
    tier1 = rows
    tier2 = [row for row in rows if row["Tier_II"] == "1"]
    tier3 = [row for row in rows if row["Tier_III"] == "1"]
    max_row = max(tier2, key=lambda row: decimal(row["Broadband_per100"]))
    loss_t2 = [row for row in tier1 if row["Tier_II"] == "0"]
    loss_t3 = [row for row in tier2 if row["Tier_III"] == "0"]
    lines = ["# Step 14 Tier Counts", "", "| Tier | Count | Economies lost against preceding tier |", "|---|---:|---:|", f"| Tier I | {len(tier1)} | 0 |", f"| Tier II | {len(tier2)} | {len(loss_t2)} |", f"| Tier III | {len(tier3)} | {len(loss_t3)} |", "", f"Tier II broadband normalisation maximum: `{max_row['Broadband_per100']}` per 100 people ({max_row['Country']}, {max_row['ISO3']}).", ""]
    for title, losses in [("Lost from Tier I to Tier II", loss_t2), ("Lost from Tier II to Tier III", loss_t3)]:
        counts = Counter(row["Exclusion_Reason"] for row in losses)
        lines.extend([f"## {title}", "", "| Reason | Count | Economies |", "|---|---:|---|"])
        for reason, count in sorted(counts.items()):
            economies = "; ".join(f"{row['Country']} ({row['ISO3']})" for row in losses if row["Exclusion_Reason"] == reason)
            lines.append(f"| {reason} | {count} | {economies} |")
        lines.append("")
    write_markdown("Step14_Tier_Counts.md", lines)


def norm_country(value: str) -> str:
    aliases = {"South Korea": "Republic of Korea", "United States": "United States of America"}
    return aliases.get(value.strip(), value.strip())


def reconciliation(rows: list[dict[str, str]]) -> None:
    canonical = {norm_country(row["Country"]): row for row in rows}
    table2 = read_csv("HDI_FN/output/Table_2_EGDI_Neutrosophic.csv")
    table1 = read_csv("HDI_FN/output/Table_1_Raw_Digital.csv")
    legacy = {norm_country(row["Country"]): {"table2": row} for row in table2}
    for row in table1:
        legacy.setdefault(norm_country(row["Country"]), {})["table1"] = row
    differences: list[tuple[str, str, str, str, Decimal, str]] = []
    missing: list[str] = []
    for country, sources in legacy.items():
        current = canonical.get(country)
        if not current:
            missing.append(country)
            continue
        t1, t2 = sources.get("table1", {}), sources.get("table2", {})
        checks = [
            ("EGDI", current["EGDI"], t2.get("Raw EGDI (T)", ""), "Phi_EGDI"),
            ("Penetration_Pct", current["Penetration_Pct"], t1.get("Internet_Pen_2023_Pct", ""), "Phi_EGDI; R_facade"),
            ("Phi_EGDI", current["Phi_EGDI"], t2.get("Non-Penetration (F)", ""), "none"),
        ]
        if t1.get("Internet_Pen_2023_Pct"):
            legacy_r = Decimal(100) / decimal(t1["Internet_Pen_2023_Pct"])
            checks.append(("R_facade", current["R_facade"], str(legacy_r), "none"))
        for metric, current_value, legacy_value, affected in checks:
            if decimal(current_value) is None or decimal(legacy_value) is None:
                continue
            difference = abs(decimal(current_value) - decimal(legacy_value))
            if difference > Decimal("1e-12"):
                differences.append((country, metric, current_value, legacy_value, difference, affected))
    lines = ["# Step 14 Legacy Reconciliation", "", "Legacy sources: `HDI_FN/output/Table_2_EGDI_Neutrosophic.csv` and `HDI_FN/output/Table_1_Raw_Digital.csv`.", "", "| Country | Cell | Canonical value | Legacy value | Absolute difference | Downstream quantity affected |", "|---|---|---:|---:|---:|---|"]
    for country, metric, current_value, legacy_value, difference, affected in differences:
        lines.append(f"| {country} | {metric} | {current_value} | {legacy_value} | {difference} | {affected} |")
    lines.extend(["", f"Cells differing above 1e-12: {len(differences)}.", f"Legacy economies without a canonical country-name match: {', '.join(missing) if missing else 'none'}.", "", "Bangladesh is retained as an audit discrepancy: canonical EGDI is 0.6570, while the legacy file reports 0.656. No source or legacy value was modified."])
    write_markdown("Step14_Legacy_Reconciliation.md", lines)


def main() -> None:
    rows, facade = build_canonical()
    gate_report(rows, facade)
    tier_report(rows)
    reconciliation(rows)
    print(f"Built {len(rows)} canonical rows in {ROOT}")


if __name__ == "__main__":
    main()
