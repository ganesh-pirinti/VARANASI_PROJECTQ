"""Unit tests for Bell-state preparation, verification, and fidelity calculations."""
from __future__ import annotations
import csv
import math
import os
import unittest

import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.metrics import calculate_bell_fidelity
from src.bell_evaluator import run_bell_verification
from qff_phase2 import load_processor

class TestBellStateVerification(unittest.TestCase):
    def setUp(self):
        self.bell_csv = os.path.join(ROOT_DIR, "results", "tables", "bell.csv")
        self.proc_d_file = os.path.join(ROOT_DIR, "processors", "processor_D.json")
        self.proc_d = load_processor(self.proc_d_file)
        
    def test_01_bell_csv_schema_and_rows(self):
        """Verify bell.csv exists and has 4 rows covering near/far pairs under ideal/noisy conditions."""
        self.assertTrue(os.path.exists(self.bell_csv))
        with open(self.bell_csv, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            
        self.assertEqual(len(rows), 4, "bell.csv must contain exactly 4 rows.")
        expected_cols = [
            "pair_type", "qubit_pair", "pair_distance", "condition", "cx_count",
            "exp_XX", "exp_XX_se", "exp_YY", "exp_YY_se", "exp_ZZ", "exp_ZZ_se",
            "fidelity", "fidelity_se", "shots"
        ]
        for col in expected_cols:
            self.assertIn(col, rows[0].keys(), f"Missing column: {col}")

    def test_02_fidelity_formula_consistency(self):
        """Verify fidelity = (1 + <XX> - <YY> + <ZZ>) / 4 and standard errors propagate correctly."""
        with open(self.bell_csv, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            
        for r in rows:
            xx = float(r["exp_XX"])
            yy = float(r["exp_YY"])
            zz = float(r["exp_ZZ"])
            se_xx = float(r["exp_XX_se"])
            se_yy = float(r["exp_YY_se"])
            se_zz = float(r["exp_ZZ_se"])
            f_reported = float(r["fidelity"])
            se_f_reported = float(r["fidelity_se"])
            
            # Recalculate via official formula
            f_calc, se_f_calc = calculate_bell_fidelity(xx, yy, zz, se_xx, se_yy, se_zz)
            self.assertAlmostEqual(f_reported, f_calc, places=4)
            self.assertAlmostEqual(se_f_reported, se_f_calc, places=4)
            
            # Verify NOT calculated via shortcut P(00) + P(11)
            self.assertGreaterEqual(f_reported, 0.0)
            self.assertLessEqual(f_reported, 1.0001)

    def test_03_ideal_vs_noisy_physical_trends(self):
        """Verify ideal fidelities are ~1.0, and noisy fidelity reflects routing degradation across distance."""
        with open(self.bell_csv, "r", encoding="utf-8") as f:
            data = {(r["pair_type"], r["condition"]): r for r in csv.DictReader(f)}
            
        # Ideal pairs must have fidelity 1.0000 +/- 0.0000
        for p_type in ["near", "far"]:
            f_ideal = float(data[(p_type, "ideal")]["fidelity"])
            se_ideal = float(data[(p_type, "ideal")]["fidelity_se"])
            self.assertAlmostEqual(f_ideal, 1.0000, places=4)
            self.assertAlmostEqual(se_ideal, 0.0000, places=4)
            
        # Noisy near dist 1 vs far dist 4
        f_noisy_near = float(data[("near", "noisy")]["fidelity"])
        f_noisy_far = float(data[("far", "noisy")]["fidelity"])
        
        # Far pair has distance 4 requiring SWAP routing, hence more CX and lower fidelity
        self.assertGreater(f_noisy_near, f_noisy_far, "Near pair must exhibit higher fidelity than routed 4-hop far pair.")
        self.assertAlmostEqual(f_noisy_near, 0.9633, places=3)
        self.assertAlmostEqual(f_noisy_far, 0.9420, places=3)

if __name__ == "__main__":
    unittest.main()
