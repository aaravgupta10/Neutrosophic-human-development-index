"""
Unit and Verification Tests for Step 17 Deliverables
"""

import unittest
from pathlib import Path
import pandas as pd
import numpy as np

STEP17_DIR = Path(__file__).resolve().parent

class TestStep17(unittest.TestCase):
    def setUp(self):
        self.frame_path = STEP17_DIR / "Step17_Frame.csv"
        self.ladder_path = STEP17_DIR / "Step17_Ladder.csv"
        self.me_path = STEP17_DIR / "Step17_MarginalEffects.csv"
        self.results_path = STEP17_DIR / "Step17_Results.md"
        self.script_path = STEP17_DIR / "Step17_Estimation.py"

    def test_deliverable_files_exist(self):
        self.assertTrue(self.frame_path.exists(), "Step17_Frame.csv missing")
        self.assertTrue(self.ladder_path.exists(), "Step17_Ladder.csv missing")
        self.assertTrue(self.me_path.exists(), "Step17_MarginalEffects.csv missing")
        self.assertTrue(self.results_path.exists(), "Step17_Results.md missing")
        self.assertTrue(self.script_path.exists(), "Step17_Estimation.py missing")

    def test_frame_properties_and_gate_a(self):
        df = pd.read_csv(self.frame_path)
        self.assertEqual(len(df), 184, "Frame should have exactly 184 rows (Tier I economies)")
        
        # Constructed variables present
        for col in ["T", "F", "Phi", "T_svc", "Phi_svc", "inc"]:
            self.assertIn(col, df.columns, f"Constructed variable {col} missing in frame")

        # Recomputations
        phi_diff = (df["Phi_EGDI"] - (df["EGDI"] * (1 - df["p"]))).abs().max()
        self.assertLess(phi_diff, 1e-10, "Phi_EGDI recomputation exceeds 1e-10 threshold")

        phi_svc_diff = (df["Phi_OSI"] - (df["OSI"] * (1 - df["p"]))).abs().max()
        self.assertLess(phi_svc_diff, 1e-10, "Phi_OSI recomputation exceeds 1e-10 threshold")

        # Gate A Counts
        gov_valid = df.dropna(subset=["GovPay_Pct", "inc", "T", "F", "Phi"])
        self.assertEqual(len(gov_valid), 145, "Gate A failure on GovPay_Pct: expected 145")

        dig_valid = df.dropna(subset=["DigitalPay_Pct", "inc", "T", "F", "Phi"])
        self.assertEqual(len(dig_valid), 150, "Gate A failure on DigitalPay_Pct: expected 150")

        mob_valid = df.dropna(subset=["MobileAccess_Pct", "inc", "T", "F", "Phi"])
        self.assertEqual(len(mob_valid), 88, "Gate A failure on MobileAccess_Pct: expected 88")

        # Monaco check
        mco = df[df["ISO3"] == "MCO"]
        self.assertTrue(pd.isna(mco["inc"].values[0]), "Monaco should have NaN income")

    def test_ladder_estimates_and_m2_reproduction(self):
        ladder = pd.read_csv(self.ladder_path)
        self.assertGreater(len(ladder), 0)

        # Confirm all 6 models are present
        models = set(ladder["Model"])
        expected_models = {"M0", "M1", "M2", "M3", "M3b", "M5"}
        self.assertEqual(models, expected_models)

        # Confirm M2 on GovPay_Pct reproduces published -0.4624
        m2_row = ladder[(ladder["Model"] == "M2") & (ladder["Outcome"] == "GovPay_Pct") & (ladder["Regressor"] == "Phi")]
        self.assertEqual(len(m2_row), 1)
        phi_coef = float(m2_row["Coef"].values[0])
        self.assertAlmostEqual(phi_coef, -0.4624, places=4, msg="M2 did not reproduce published -0.4624")

    def test_marginal_effects_grid(self):
        me = pd.read_csv(self.me_path)
        self.assertEqual(len(me), 10, "Marginal effects table should have 10 rows (5 T values x 2 outcomes)")
        
        expected_t = [0.2, 0.4, 0.6, 0.8, 0.95]
        for outcome in ["GovPay_Pct", "DigitalPay_Pct"]:
            sub = me[me["Outcome"] == outcome]
            t_vals = sorted(sub["T_val"].tolist())
            np.testing.assert_allclose(t_vals, expected_t, rtol=1e-5)

    def test_results_markdown_content(self):
        content = self.results_path.read_text(encoding="utf-8")
        self.assertIn("Gate A Verification", content)
        self.assertIn("Centring-Invariance Demonstration", content)
        self.assertIn("Fractional Logit Model", content)
        self.assertIn("Robustness Re-estimations", content)
        self.assertIn("Findex Coverage Comparison", content)
        self.assertIn("Cook's D", content)
        self.assertIn("-0.4624", content)

if __name__ == "__main__":
    unittest.main()
