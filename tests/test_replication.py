"""
Comprehensive Unit & Replication Tests for the Neutrosophic Human Development Index (HDI-N) Project.
Verifies dataset integrity, mathematical consistency, Gate A sample sizes,
and econometric model reproduction.
"""

import unittest
from pathlib import Path
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent

class TestReplication(unittest.TestCase):
    def setUp(self):
        self.canonical_v1 = REPO_ROOT / "data" / "canonical" / "HDIN_Canonical_v1.csv"
        self.canonical_v2 = REPO_ROOT / "data" / "canonical" / "HDIN_Canonical_v2.csv"
        self.findex_raw = REPO_ROOT / "data" / "validation" / "Step15_Findex_Raw.csv"
        self.step17_frame = REPO_ROOT / "results" / "Step17_Frame.csv"
        self.step17_ladder = REPO_ROOT / "results" / "Step17_Ladder.csv"
        self.step17_me = REPO_ROOT / "results" / "Step17_MarginalEffects.csv"
        self.step17_results = REPO_ROOT / "results" / "Step17_Results.md"

    def test_canonical_panel_properties(self):
        self.assertTrue(self.canonical_v2.exists(), "HDIN_Canonical_v2.csv missing")
        df = pd.read_csv(self.canonical_v2)
        self.assertEqual(len(df), 184, "Canonical v2 should have exactly 184 economies")
        
        # Check presence of key neutrosophic components
        required_cols = [
            "ISO3", "Country", "EGDI", "OSI", "TII", "HCI",
            "p", "T_adj_EGDI", "T_adj_OSI", "Phi_EGDI", "Phi_OSI",
            "I_egov", "Signed_Div", "I_income", "HDI_Standard"
        ]
        for col in required_cols:
            self.assertIn(col, df.columns, f"Column {col} missing in HDIN_Canonical_v2")

        # Mathematical recomputation identity check: Phi = EGDI * (1 - p)
        phi_diff = (df["Phi_EGDI"] - (df["EGDI"] * (1 - df["p"]))).abs().max()
        self.assertLess(phi_diff, 1e-10, "Discrepancy in Phi_EGDI exceeds 1e-10")

        # Service-level recomputation: Phi_svc = OSI * (1 - p)
        phi_svc_diff = (df["Phi_OSI"] - (df["OSI"] * (1 - df["p"]))).abs().max()
        self.assertLess(phi_svc_diff, 1e-10, "Discrepancy in Phi_OSI exceeds 1e-10")

    def test_gate_a_verification(self):
        self.assertTrue(self.step17_frame.exists(), "Step17_Frame.csv missing")
        frame = pd.read_csv(self.step17_frame)
        self.assertEqual(len(frame), 184, "Frame should contain 184 Tier I economies")

        # Gate A sample sizes
        gov_valid = frame.dropna(subset=["GovPay_Pct", "inc", "T", "F", "Phi"])
        self.assertEqual(len(gov_valid), 145, "Gate A failure on GovPay_Pct: expected 145 rows")

        dig_valid = frame.dropna(subset=["DigitalPay_Pct", "inc", "T", "F", "Phi"])
        self.assertEqual(len(dig_valid), 150, "Gate A failure on DigitalPay_Pct: expected 150 rows")

        mob_valid = frame.dropna(subset=["MobileAccess_Pct", "inc", "T", "F", "Phi"])
        self.assertEqual(len(mob_valid), 88, "Gate A failure on MobileAccess_Pct: expected 88 rows")

        # Monaco check
        mco = frame[frame["ISO3"] == "MCO"]
        self.assertTrue(pd.isna(mco["inc"].values[0]), "Monaco should have NaN income sub-index")

    def test_econometric_ladder_estimates(self):
        self.assertTrue(self.step17_ladder.exists(), "Step17_Ladder.csv missing")
        ladder = pd.read_csv(self.step17_ladder)

        # Confirm Model 2 reproduction (-0.4624) on GovPay_Pct
        m2_row = ladder[
            (ladder["Outcome"] == "GovPay_Pct") & 
            (ladder["Model"] == "M2") & 
            (ladder["Regressor"] == "Phi")
        ]
        self.assertEqual(len(m2_row), 1)
        m2_coef = float(m2_row["Coef"].values[0])
        self.assertAlmostEqual(m2_coef, -0.4624, places=4, msg="M2 GovPay_Pct Phi coef mismatch")

        # Confirm Model 3 horse race (-0.8698, p < 0.0001) on GovPay_Pct
        m3_row = ladder[
            (ladder["Outcome"] == "GovPay_Pct") & 
            (ladder["Model"] == "M3") & 
            (ladder["Regressor"] == "Phi")
        ]
        self.assertEqual(len(m3_row), 1)
        m3_coef = float(m3_row["Coef"].values[0])
        self.assertAlmostEqual(m3_coef, -0.8698, places=4, msg="M3 GovPay_Pct Phi coef mismatch")
        m3_p = float(m3_row["p_value"].values[0])
        self.assertLess(m3_p, 0.0001, "M3 GovPay_Pct Phi p-value should be < 0.0001")

        # Confirm Model 3b (without Phi, F is insignificant)
        m3b_f_row = ladder[
            (ladder["Outcome"] == "GovPay_Pct") & 
            (ladder["Model"] == "M3b") & 
            (ladder["Regressor"] == "F")
        ]
        self.assertEqual(len(m3b_f_row), 1)
        m3b_f_p = float(m3b_f_row["p_value"].values[0])
        self.assertGreater(m3b_f_p, 0.05, "In M3b on GovPay_Pct, F should not be significant (p > 0.05)")

if __name__ == "__main__":
    unittest.main()
