"""Unit tests for PS-O1 benchmark results, CSV tables, and raw histogram integrity."""
from __future__ import annotations
import csv
import json
import os
import unittest
import math

import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from qff_phase2 import counts_to_x
from src.exact_solver import compute_cut_weight

class TestResultsAndCrossValidation(unittest.TestCase):
    def setUp(self):
        self.results_csv = os.path.join(ROOT_DIR, "results", "tables", "results.csv")
        self.raw_counts_file = os.path.join(ROOT_DIR, "results", "raw", "qaoa_counts.json")
        self.init_csv = os.path.join(ROOT_DIR, "results", "tables", "initializations.csv")
        self.resource_csv = os.path.join(ROOT_DIR, "results", "tables", "resource_comparison.csv")
        self.inst_file = os.path.join(ROOT_DIR, "data", "instance.json")
        
        with open(self.inst_file, "r", encoding="utf-8") as f:
            self.inst = json.load(f)
        with open(self.raw_counts_file, "r", encoding="utf-8") as f:
            self.raw_counts = json.load(f)

    def test_01_results_csv_schema_and_rows(self):
        """Verify results.csv exists, has 6 rows, and adheres to official schema."""
        self.assertTrue(os.path.exists(self.results_csv))
        with open(self.results_csv, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            
        self.assertEqual(len(rows), 6, "results.csv must contain exactly 6 rows (A, B, D x Ideal, Noisy).")
        expected_cols = [
            "problem_id", "processor", "condition", "executable", "logical_qubits",
            "physical_qubits", "logical_cx", "cx", "depth", "two_q_depth", "swaps", "cx_overhead",
            "shots", "quality_metric", "quality_value", "p_opt", "classical_optimum", "random_baseline"
        ]
        for col in expected_cols:
            self.assertIn(col, rows[0].keys(), f"Missing column: {col}")

    def test_02_processor_a_non_executable(self):
        """Verify Processor A is marked non-executable for PS-O1 (5 qubits < 6 required)."""
        with open(self.results_csv, "r", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["processor"] == "A"]
            
        self.assertEqual(len(rows), 2)
        for r in rows:
            self.assertEqual(r["executable"].lower(), "false")
            self.assertEqual(r["quality_metric"], "approx_ratio")
            self.assertEqual(r["quality_value"], "")

    def test_03_raw_histograms_4096_shots(self):
        """Verify all executable runs sample exactly 4096 shots over the 64 bitstring domain."""
        runs = self.raw_counts["runs"]
        for run_name, run_data in runs.items():
            hist = run_data["histogram"]
            total_shots = sum(item["count"] for item in hist.values())
            self.assertEqual(total_shots, 4096, f"Run {run_name} must have exactly 4096 shots.")
            self.assertEqual(len(hist), 64, f"Run {run_name} must contain all 64 bitstrings.")
            
            # Verify bitstring domain
            for k in hist.keys():
                self.assertEqual(len(k), 6, f"Invalid bitstring length {len(k)}: {k}")
                self.assertTrue(set(k).issubset({"0", "1"}))

    def test_04_cross_validation_csv_vs_raw_counts(self):
        """Verify CSV approximation ratios and P_opt reproduce independently from raw counts."""
        with open(self.results_csv, "r", encoding="utf-8") as f:
            csv_rows = {f"Processor_{r['processor']}_{r['condition']}": r for r in csv.DictReader(f) if r["executable"].lower() == "true"}
            
        optimal_states = [(1, 1, 0, 1, 0, 0), (0, 0, 1, 0, 1, 1)]
        edges = self.inst["weighted_edges"]
        runs = self.raw_counts["runs"]
        
        for run_key, csv_row in csv_rows.items():
            self.assertIn(run_key, runs, f"Run {run_key} missing from raw_counts.json")
            hist = runs[run_key]["histogram"]
            
            # Independent recalculation
            total_cut = 0
            opt_count = 0
            for k, item in hist.items():
                cnt = item["count"]
                x = counts_to_x(k)
                cut = compute_cut_weight(list(x), edges)
                total_cut += cut * cnt
                if x in optimal_states:
                    opt_count += cnt
                    
            calc_mean_cut = total_cut / 4096.0
            calc_r = calc_mean_cut / 22.0
            calc_p_opt = opt_count / 4096.0
            
            csv_r = float(csv_row["quality_value"])
            csv_p_opt = float(csv_row["p_opt"])
            
            self.assertAlmostEqual(calc_r, csv_r, places=4, msg=f"Approximation ratio mismatch for {run_key}")
            self.assertAlmostEqual(calc_p_opt, csv_p_opt, places=4, msg=f"P_opt mismatch for {run_key}")

    def test_05_initializations_table_integrity(self):
        """Verify initializations.csv exists, has 5 seeds [0, 1, 2, 3, 4], and identifies seed 3 as best."""
        self.assertTrue(os.path.exists(self.init_csv))
        with open(self.init_csv, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            
        self.assertEqual(len(rows), 5)
        seeds = [int(r["seed"]) for r in rows]
        self.assertEqual(seeds, [0, 1, 2, 3, 4])
        
        best_rows = [r for r in rows if r["is_best"].lower() == "true"]
        self.assertEqual(len(best_rows), 1)
        self.assertEqual(int(best_rows[0]["seed"]), 3)
        self.assertAlmostEqual(float(best_rows[0]["approx_ratio"]), 0.8051, places=3)

    def test_06_resource_comparison_table(self):
        """Verify resource_comparison.csv shows SWAP elimination on Processor D."""
        self.assertTrue(os.path.exists(self.resource_csv))
        with open(self.resource_csv, "r", encoding="utf-8") as f:
            rows = {r["processor"]: r for r in csv.DictReader(f)}
            
        self.assertIn("Processor B", rows)
        self.assertIn("Processor D", rows)
        
        self.assertEqual(int(rows["Processor B"]["swaps"]), 1)
        self.assertEqual(int(rows["Processor D"]["swaps"]), 0)
        self.assertEqual(int(rows["Processor D"]["physical_cx"]), 18)
        self.assertEqual(int(rows["Processor B"]["physical_cx"]), 21)

if __name__ == "__main__":
    unittest.main()
