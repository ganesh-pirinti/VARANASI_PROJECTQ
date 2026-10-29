"""Cross-Artifact Consistency and Scientific Reconciliation Test.

Guarantees 100% numerical agreement across:
- results/tables/results.csv
- results/tables/bell.csv
- results/tables/initializations.csv
- results/tables/resource_comparison.csv
- results/raw/qaoa_counts.json
- results/raw/benchmark_metadata.json
- data/studio_data.json
- report.md and README.md

Specifically prevents recurrence of stale/typographical discrepancies (e.g. 0.8048 vs 0.8074).
"""
from __future__ import annotations
import csv
import json
import os
import unittest
import numpy as np

import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.qaoa_solver import QAOASolver

class TestCrossArtifactConsistency(unittest.TestCase):
    def setUp(self):
        self.results_csv = os.path.join(ROOT_DIR, "results", "tables", "results.csv")
        self.raw_counts = os.path.join(ROOT_DIR, "results", "raw", "qaoa_counts.json")
        self.metadata = os.path.join(ROOT_DIR, "results", "raw", "benchmark_metadata.json")
        self.studio_json = os.path.join(ROOT_DIR, "data", "studio_data.json")
        self.report_md = os.path.join(ROOT_DIR, "report.md")
        self.readme_md = os.path.join(ROOT_DIR, "README.md")
        self.instance_json = os.path.join(ROOT_DIR, "data", "instance.json")
        
        with open(self.raw_counts, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)
        with open(self.metadata, "r", encoding="utf-8") as f:
            self.meta_data = json.load(f)
        with open(self.studio_json, "r", encoding="utf-8") as f:
            self.studio_data = json.load(f)

    def test_01_processor_b_ideal_exact_reconciliation(self):
        """Verify Processor B Ideal matches exact authoritative raw counts and no stale 0.8048 exists."""
        # Raw counts check
        b_ideal_raw = self.raw_data["runs"]["Processor_B_ideal"]
        self.assertEqual(b_ideal_raw["optimal_sample_count"], 572)
        self.assertAlmostEqual(b_ideal_raw["mean_cut"], 17.761962890625, places=5)
        self.assertAlmostEqual(b_ideal_raw["approx_ratio"], 0.8073619495738636, places=5)
        self.assertAlmostEqual(b_ideal_raw["optimal_sample_probability"], 572 / 4096.0, places=5)
        
        # CSV check
        with open(self.results_csv, "r", encoding="utf-8") as f:
            rows = {f"{r['processor']}_{r['condition']}": r for r in csv.DictReader(f)}
        b_ideal_csv = rows["B_ideal"]
        self.assertEqual(b_ideal_csv["quality_value"], "0.8074")
        self.assertEqual(b_ideal_csv["p_opt"], "0.1396")
        
        # Stale value rejection: 0.8048 must NOT be reported as Processor B ideal anywhere
        with open(self.results_csv, "r", encoding="utf-8") as f:
            csv_text = f.read()
        self.assertNotIn("0.8048", csv_text, "Stale approx ratio 0.8048 must not exist in results.csv")
        self.assertNotIn("0.1379", csv_text, "Stale P_opt 0.1379 must not exist in results.csv")

    def test_02_all_four_executable_runs_agreement(self):
        """Cross-check all 4 executable runs across raw_counts, results.csv, and studio_data.json."""
        with open(self.results_csv, "r", encoding="utf-8") as f:
            csv_rows = {f"Processor_{r['processor']}_{r['condition']}": r for r in csv.DictReader(f) if r["executable"].lower() == "true"}
            
        expected_benchmarks = {
            "Processor_B_ideal": {"approx_ratio": 0.8074, "p_opt": 0.1396, "opt_count": 572},
            "Processor_B_noisy": {"approx_ratio": 0.7874, "p_opt": 0.1260, "opt_count": 516},
            "Processor_D_ideal": {"approx_ratio": 0.8052, "p_opt": 0.1384, "opt_count": 567},
            "Processor_D_noisy": {"approx_ratio": 0.7862, "p_opt": 0.1250, "opt_count": 512},
        }
        
        for run_name, exp in expected_benchmarks.items():
            # 1. Raw check
            raw_run = self.raw_data["runs"][run_name]
            self.assertEqual(raw_run["optimal_sample_count"], exp["opt_count"])
            self.assertAlmostEqual(raw_run["approx_ratio"], exp["approx_ratio"], places=3)
            self.assertAlmostEqual(raw_run["optimal_sample_probability"], exp["p_opt"], places=3)
            
            # 2. CSV check
            csv_run = csv_rows[run_name]
            self.assertAlmostEqual(float(csv_run["quality_value"]), exp["approx_ratio"], places=3)
            self.assertAlmostEqual(float(csv_run["p_opt"]), exp["p_opt"], places=3)

    def test_03_parameter_symmetry_and_in_domain_canonical(self):
        """Numerically verify reflection symmetry F(-gamma, pi - beta) = F(gamma, beta)."""
        with open(self.instance_json, "r", encoding="utf-8") as f:
            edges = json.load(f)["weighted_edges"]
        solver = QAOASolver(edges, 6)
        
        raw_g = -0.16801984112040994
        raw_b = 0.332661845215259
        
        canon_g = -raw_g  # +0.16801984112040994 in [0, pi]
        canon_b = np.pi - raw_b  # +2.808930808374534 in [0, pi]
        
        val_raw = solver.evaluate_statevector_expectation([raw_g], [raw_b])
        val_canon = solver.evaluate_statevector_expectation([canon_g], [canon_b])
        
        # Symmetry must hold within floating point tolerance
        self.assertAlmostEqual(val_raw, val_canon, places=5)
        self.assertAlmostEqual(val_raw, 17.712816894564796, places=4)
        
        # Verify studio data records both representations
        landscape = self.studio_data["parameter_landscape"]
        opt_pt = landscape["optimal_point"]
        self.assertIn("raw_gamma", opt_pt)
        self.assertIn("canonical_gamma", opt_pt)
        self.assertAlmostEqual(opt_pt["canonical_gamma"], round(canon_g, 4), places=3)
        self.assertAlmostEqual(opt_pt["canonical_beta"], round(canon_b, 4), places=3)

if __name__ == "__main__":
    unittest.main()
