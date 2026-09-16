"""
Step 15: External Validation Pipeline (Section 3.6 of HDI-N Manuscript)
Replicates the validation merge on HDIN_Canonical_v2.csv and Step15_Findex_Raw.csv,
computes OLS regressions, and outputs diagnostic plots and results.
"""
import os
import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
CANON_PATH = REPO_ROOT / "data" / "canonical" / "HDIN_Canonical_v2.csv"
FINDEX_RAW_PATH = REPO_ROOT / "data" / "validation" / "Step15_Findex_Raw.csv"
OUTPUT_DIR = REPO_ROOT / "results"
PLOTS_DIR = OUTPUT_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

def run_validation():
    print("=" * 70)
    print("STEP 15: External Validation Pipeline")
    print("=" * 70)
    
    df_canon = pd.read_csv(CANON_PATH)
    df_findex = pd.read_csv(FINDEX_RAW_PATH)
    print(f"Loaded Canonical v2: {len(df_canon)} rows")
    print(f"Loaded Findex Raw: {len(df_findex)} rows")
    
    # Merge onto canonical
    merged = pd.merge(df_canon, df_findex, on="ISO3", how="inner")
    print(f"Merged validation set: {len(merged)} economies")
    
    validation_csv = REPO_ROOT / "data" / "validation" / "Step15_Validation_Set.csv"
    merged.to_csv(validation_csv, index=False)
    print(f"Saved: {validation_csv}")
    
    indicators = {
        "GovPay_Pct": "Received government payments into an account (%, age 15+)",
        "DigitalPay_Pct": "Made or received a digital payment (%, age 15+)",
        "MobileAccess_Pct": "Used a mobile phone or internet to check account balance (%, age 15+)"
    }
    
    for outcome, desc in indicators.items():
        sub = merged.dropna(subset=["EGDI", "I_income", "Phi_EGDI", outcome]).copy()
        print(f"\n--- Indicator: {outcome} ({desc}) | N = {len(sub)} ---")
        
        # M1: EGDI + inc
        X1 = sm.add_constant(sub[["EGDI", "I_income"]])
        m1 = sm.OLS(sub[outcome], X1).fit(cov_type="HC3")
        
        # M2: EGDI + inc + Phi_EGDI
        X2 = sm.add_constant(sub[["EGDI", "I_income", "Phi_EGDI"]])
        m2 = sm.OLS(sub[outcome], X2).fit(cov_type="HC3")
        
        print(f"  M1 R2 = {m1.rsquared:.4f} | EGDI coef = {m1.params['EGDI']:.4f} (p={m1.pvalues['EGDI']:.4f})")
        print(f"  M2 R2 = {m2.rsquared:.4f} | Phi coef  = {m2.params['Phi_EGDI']:.4f} (p={m2.pvalues['Phi_EGDI']:.4f})")
        print(f"  Delta R2 = {m2.rsquared - m1.rsquared:.4f}")
        
    print("\nValidation pipeline successfully completed.")

if __name__ == "__main__":
    run_validation()
