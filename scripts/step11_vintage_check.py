"""
Step 11 verification script — Pakistan penetration-vintage sensitivity.
Run against the AUDITED data files (adjust DATA_DIR to your local copies).
Reproduces the three trial findings reported in the Step 11 memo:
  (1) nowcast facade quantities  (2) intersection-criterion survival
  (3) HDI-N rank invariance
Replace PEN_NOWCAST with the exact ITU 2024 value you verify in Task 3.
"""
import pandas as pd

DATA_DIR   = "."            # directory holding the audited CSVs
PEN_NOWCAST = 0.57          # ITU 2024 release value — VERIFY AND REPLACE (Task 3)

t2 = pd.read_csv(f"{DATA_DIR}/Table_2_EGDI_Neutrosophic.csv")
t3 = pd.read_csv(f"{DATA_DIR}/Table_3_Composite_Digital.csv")
t4 = pd.read_csv(f"{DATA_DIR}/Table_4_HDI_FN_Preview.csv")

# (1) Nowcast facade quantities
egdi = t2.loc[t2.Country == "Pakistan", "Raw EGDI (T)"].iloc[0]
R_now, Phi_now = 1 / PEN_NOWCAST, egdi * (1 - PEN_NOWCAST)
print(f"(1) Pakistan nowcast: R_facade = {R_now:.3f}   Phi = {Phi_now:.4f}")
print(f"    Expected (trial): R_facade = 1.754        Phi = 0.2189\n")

# (2) Intersection criterion at BOTH interval ends
for label, pen_pk in [("upper bound (carry-forward 0.189)", None),
                      (f"lower bound (nowcast {PEN_NOWCAST})", PEN_NOWCAST)]:
    d = t2.copy()
    d["pen"] = 1 - d["Non-Penetration (F)"]
    if pen_pk is not None:
        d.loc[d.Country == "Pakistan", "pen"] = pen_pk
    d["R"], d["Phi"] = 1 / d["pen"], d["Raw EGDI (T)"] * (1 - d["pen"])
    inter = sorted(set(d.nlargest(4, "R").Country) & set(d.nlargest(4, "Phi").Country))
    print(f"(2) Intersection, {label}: {inter}")
    if pen_pk is not None:
        gap = (d.set_index("Country").loc["Pakistan", "Phi"]
               - d.set_index("Country").loc["Burkina Faso", "Phi"])
        print(f"    Phi margin Pakistan over Burkina Faso at lower bound: {gap:.4f} (expected 0.003)")
print("    Expected: ['Bangladesh', 'Nepal', 'Pakistan'] at both ends\n")

# (3) HDI-N invariance under the nowcast
r3   = t3.loc[t3.Country == "Pakistan"].iloc[0]
Tadj = egdi * PEN_NOWCAST
Idig = (PEN_NOWCAST * r3["I_broadband"] * Tadj * r3["I_hitech"]) ** 0.25
r4   = t4.loc[t4.Country == "Pakistan"].iloc[0]
hdin = (r4["I_health"] * r4["I_education"] * r4["I_income_adj (approx.)"] * Idig) ** 0.25
nb   = t4[t4.Country.isin(["Nepal", "Burkina Faso"])].set_index("Country")["HDI_FN Score"]
print(f"(3) Pakistan HDI-N under nowcast = {hdin:.3f} (expected 0.363)")
print(f"    Nepal = {nb['Nepal']:.3f}  >  Pakistan  >  Burkina Faso = {nb['Burkina Faso']:.3f}"
      f"   ->  rank 18 {'INVARIANT' if nb['Burkina Faso'] < hdin < nb['Nepal'] else 'CHANGED — REPORT'}")
