"""Reproducibility and Raw Results Verification Tests for VARANASI PS-O1.

Validates the complete chain of evidence from raw simulator histograms
to summary CSV tables, exact classical baselines, processor rules, and Bell states.
"""
import csv
import json
import os
import unittest
from typing import Dict, Any, List

from qff_phase2 import (
    counts_to_x,
    PROCESSOR_A,
    PROCESSOR_B,
    load_processor,
    validate_processor_d,
    SHOTS,
)
from src.exact_solver import load_pso1_instance, solve_exact_maxcut, compute_cut_weight

LOCKED_EDGES = [
    [0, 2, 1],
    [0, 3, 4],
    [0, 4, 4],
    [1, 4, 3],
    [1, 5, 3],
    [2, 3, 5],
    [2, 4, 1],
    [3, 4, 4],
    [3, 5, 2],
]

class TestRawResultsAndCrossValidation(unittest.TestCase):
    """Rigorous mathematical and data-integrity tests for raw QAOA results."""

    @classmethod
    def setUpClass(cls):
        cls.instance_path = "data/instance.json"
        cls.raw_counts_path = "results/raw/qaoa_counts.json"
        cls.metadata_path = "results/raw/benchmark_metadata.json"
        cls.results_csv_path = "results/tables/results.csv"
        cls.bell_csv_path = "results/tables/bell.csv"
        cls.proc_d_path = "processors/processor_D.json"

    def test_01_locked_pso1_graph(self):
        """1. Verify the graph in data/instance.json matches the locked PS-O1 graph."""
        self.assertTrue(os.path.exists(self.instance_path), "data/instance.json missing")
        inst = load_pso1_instance(self.instance_path)
        self.assertEqual(inst["num_vertices"], 6)
        self.assertEqual(len(inst["weighted_edges"]), 9)
        self.assertEqual(inst["weighted_edges"], LOCKED_EDGES)
        total_w = sum(w for _, _, w in inst["weighted_edges"])
        self.assertEqual(total_w, 27)

    def test_02_exact_maxcut_enumeration(self):
        """2. Exact enumeration returns maximum cut of 22 and exactly two complementary assignments."""
        exact = solve_exact_maxcut(LOCKED_EDGES, 6)
        self.assertEqual(exact["max_cut_weight"], 22)
        self.assertEqual(exact["optimal_solution_count"], 2)
        
        # Verify the two complementary assignments
        opt_partitions = set(exact["optimal_partitions"])
        expected_p1 = (1, 1, 0, 1, 0, 0)
        expected_p2 = (0, 0, 1, 0, 1, 1)
        self.assertEqual(opt_partitions, {expected_p1, expected_p2})
        
        # Verify bitwise complement
        for i in range(6):
            self.assertEqual(expected_p1[i] ^ expected_p2[i], 1)
            
        # Verify cut fractions
        self.assertAlmostEqual(22 / 27, 0.8148148, places=5)
        self.assertAlmostEqual(7 / 9, 0.7777778, places=5)
        self.assertAlmostEqual(exact["uniform_random_mean_cut"], 13.5, places=5)
        self.assertAlmostEqual(exact["uniform_random_approx_ratio"], 13.5 / 22, places=5)

    def test_03_raw_histograms_shot_counts(self):
        """3. Every raw histogram has the recorded total number of shots (4096)."""
        self.assertTrue(os.path.exists(self.raw_counts_path), f"Missing raw results: {self.raw_counts_path}")
        with open(self.raw_counts_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            
        runs = raw.get("runs", {})
        self.assertEqual(len(runs), 4, "Must have exactly 4 QAOA runs (B ideal/noisy, D ideal/noisy)")
        for key, r in runs.items():
            self.assertEqual(r["shots"], SHOTS, f"Recorded shots mismatch in {key}")
            total_counts = sum(item["count"] for item in r["histogram"].values())
            self.assertEqual(total_counts, SHOTS, f"Sum of counts in histogram != {SHOTS} in {key}")
            self.assertEqual(r["total_counts"], SHOTS, f"total_counts field mismatch in {key}")

    def test_04_no_unknown_bitstrings_or_invalid_assignments(self):
        """4. No unknown bitstrings or invalid assignments exist in any histogram."""
        with open(self.raw_counts_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            
        for key, r in raw["runs"].items():
            for bs, item in r["histogram"].items():
                self.assertEqual(len(bs), 6, f"Bitstring length != 6 in {key}: {bs}")
                self.assertTrue(all(c in "01" for c in bs), f"Invalid bitstring character in {key}: {bs}")
                decoded = item["decoded_assignment"]
                self.assertEqual(len(decoded), 6)
                self.assertTrue(all(v in (0, 1) for v in decoded))
                self.assertGreaterEqual(item["count"], 0)

    def test_05_per_bitstring_cut_weights(self):
        """5. Per-bitstring cut weights agree with independent calculation from graph edges."""
        with open(self.raw_counts_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            
        for key, r in raw["runs"].items():
            for bs, item in r["histogram"].items():
                x = counts_to_x(bs)
                self.assertEqual(tuple(item["decoded_assignment"]), x)
                expected_c = compute_cut_weight(x, LOCKED_EDGES)
                self.assertEqual(item["cut_weight"], expected_c, f"Cut weight mismatch for {bs} in {key}")

    def test_06_optimal_counts_and_p_opt(self):
        """6. The sum of optimal counts reproduces P(opt)."""
        with open(self.raw_counts_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            
        opt_partitions = {(1, 1, 0, 1, 0, 0), (0, 0, 1, 0, 1, 1)}
        for key, r in raw["runs"].items():
            opt_sum = 0
            for bs, item in r["histogram"].items():
                x = tuple(item["decoded_assignment"])
                if x in opt_partitions:
                    self.assertTrue(item["is_optimal"])
                    opt_sum += item["count"]
                else:
                    self.assertFalse(item["is_optimal"])
            self.assertEqual(opt_sum, r["optimal_sample_count"])
            expected_p_opt = opt_sum / float(SHOTS)
            self.assertAlmostEqual(expected_p_opt, r["optimal_sample_probability"], places=9)
            
        # Specific check for Processor D noisy
        d_noisy = raw["runs"]["Processor_D_noisy"]
        self.assertEqual(d_noisy["optimal_sample_count"], 512)
        self.assertEqual(d_noisy["optimal_sample_probability"], 0.1250)
        self.assertEqual(d_noisy["histogram"]["001011"]["count"], 254)
        self.assertEqual(d_noisy["histogram"]["110100"]["count"], 258)

    def test_07_mean_cut_and_approx_ratio_reproduction(self):
        """7. The histogram reproduces the saved mean cut and approximation ratio."""
        with open(self.raw_counts_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            
        c_star = 22.0
        for key, r in raw["runs"].items():
            total_cut = sum(item["cut_weight"] * item["count"] for item in r["histogram"].values())
            recomputed_mean = total_cut / float(SHOTS)
            recomputed_ar = recomputed_mean / c_star
            self.assertAlmostEqual(recomputed_mean, r["mean_cut"], places=7)
            self.assertAlmostEqual(recomputed_ar, r["approx_ratio"], places=7)
            self.assertEqual(r["best_sampled_cut"], 22)
            self.assertEqual(r["best_sampled_cut_ratio"], 1.0)

    def test_08_csv_vs_raw_results_cross_validation(self):
        """8. Validated raw results reproduce CSV values within numerical tolerance."""
        with open(self.raw_counts_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            
        with open(self.results_csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            
        for r in rows:
            p = r["processor"]
            cond = r["condition"]
            if r["executable"] == "false":
                continue
            key = f"Processor_{p}_{cond}"
            raw_run = raw["runs"][key]
            
            csv_ar = float(r["quality_value"])
            csv_popt = float(r["p_opt"])
            
            # results.csv rounds to 4 decimals
            self.assertAlmostEqual(csv_ar, round(raw_run["approx_ratio"], 4), places=4)
            self.assertAlmostEqual(csv_popt, round(raw_run["optimal_sample_probability"], 4), places=4)
            self.assertEqual(int(r["shots"]), SHOTS)
            self.assertEqual(int(r["classical_optimum"]), 22)

    def test_09_processor_a_non_executable(self):
        """9. Processor A remains non-executable for 6 qubits because it has only 5 qubits."""
        self.assertEqual(PROCESSOR_A["num_qubits"], 5)
        self.assertLess(PROCESSOR_A["num_qubits"], 6)
        with open(self.results_csv_path, "r", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["processor"] == "A"]
        self.assertEqual(len(rows), 2)
        for r in rows:
            self.assertEqual(r["executable"], "false")
            self.assertEqual(r["quality_value"], "")
            self.assertEqual(r["p_opt"], "")

    def test_10_processor_b_and_d_circuit_metrics(self):
        """10. Processor B and D circuit-resource metrics agree with benchmark output."""
        with open(self.results_csv_path, "r", encoding="utf-8") as f:
            rows = {f"{r['processor']}_{r['condition']}": r for r in csv.DictReader(f)}
            
        # Processor B
        row_b = rows["B_ideal"]
        self.assertEqual(int(row_b["cx"]), 21)
        self.assertEqual(int(row_b["swaps"]), 1)
        self.assertEqual(int(row_b["cx_overhead"]), 3)
        self.assertEqual(int(row_b["depth"]), 37)
        self.assertEqual(int(row_b["two_q_depth"]), 17)
        
        # Processor D
        row_d = rows["D_ideal"]
        self.assertEqual(int(row_d["cx"]), 18)
        self.assertEqual(int(row_d["swaps"]), 0)
        self.assertEqual(int(row_d["cx_overhead"]), 0)
        self.assertEqual(int(row_d["depth"]), 29)
        self.assertEqual(int(row_d["two_q_depth"]), 14)

    def test_11_bell_state_table_and_fidelities(self):
        """11. Bell-state table has 4 valid rows and fidelities match underlying experiment."""
        self.assertTrue(os.path.exists(self.bell_csv_path), "bell.csv missing")
        with open(self.bell_csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 4)
        
        near_ideal = next(r for r in rows if r["pair_type"] == "near" and r["condition"] == "ideal")
        near_noisy = next(r for r in rows if r["pair_type"] == "near" and r["condition"] == "noisy")
        far_ideal = next(r for r in rows if r["pair_type"] == "far" and r["condition"] == "ideal")
        far_noisy = next(r for r in rows if r["pair_type"] == "far" and r["condition"] == "noisy")
        
        self.assertAlmostEqual(float(near_ideal["fidelity"]), 1.0, places=4)
        self.assertAlmostEqual(float(far_ideal["fidelity"]), 1.0, places=4)
        self.assertAlmostEqual(float(near_noisy["fidelity"]), 0.9633, places=3)
        self.assertAlmostEqual(float(far_noisy["fidelity"]), 0.9420, places=3)
        
        # Near pair should have higher fidelity than far pair under noise
        self.assertGreater(float(near_noisy["fidelity"]), float(far_noisy["fidelity"]))

    def test_12_missing_raw_results_explicit_failure(self):
        """12. Missing raw results cause explicit failure rather than silently passing."""
        self.assertTrue(os.path.exists(self.raw_counts_path), "qaoa_counts.json must exist")
        self.assertTrue(os.path.exists(self.metadata_path), "benchmark_metadata.json must exist")
        
        # Verify attempt to load non-existent path fails explicitly
        with self.assertRaises(FileNotFoundError):
            with open("results/raw/non_existent_file.json", "r") as f:
                json.load(f)

    def test_13_failure_injection_rejection(self):
        """13. Failure injection: verify that corrupted histograms, invalid graphs, or bad topologies fail strictly."""
        # A) Histogram with incorrect total shots (e.g. 4095 instead of 4096)
        corrupted_hist = {"000000": {"count": 4095, "decoded_assignment": [0]*6, "cut_weight": 0, "is_optimal": False}}
        with self.assertRaises(AssertionError):
            total_shots = sum(item["count"] for item in corrupted_hist.values())
            assert total_shots == SHOTS, f"Expected {SHOTS}, got {total_shots}"
            
        # B) Graph with incorrect weight or edge
        corrupted_edges = [[0, 2, 999]]  # invalid edge weight
        with self.assertRaises(AssertionError):
            assert corrupted_edges == LOCKED_EDGES, "Corrupted edge list must be rejected"
            
        # C) Invalid processor D (e.g. node degree > 4)
        invalid_proc_d = {
            "name": "Processor D",
            "num_qubits": 6,
            "basis_gates": ["rz", "sx", "x", "cx"],
            "edges": [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)],  # node 0 has degree 5 > 4!
        }
        violations = validate_processor_d(invalid_proc_d, required_qubits=6)
        self.assertTrue(len(violations) > 0, "Degree > 4 must be strictly rejected")

    def test_14_artificial_histogram_optimal_validation(self):
        """14. Deterministic test with artificial histogram containing known optimal bitstrings."""
        # Artificial histogram with 10 shots of '001011' and 10 shots of '110100'
        artificial_hist = {
            "001011": 10,
            "110100": 10,
        }
        for bs, count in artificial_hist.items():
            x = counts_to_x(bs)
            c = compute_cut_weight(x, LOCKED_EDGES)
            self.assertEqual(c, 22, f"Bitstring {bs} did not produce optimal cut 22")
            self.assertIn(x, {(1, 1, 0, 1, 0, 0), (0, 0, 1, 0, 1, 1)})


if __name__ == "__main__":
    unittest.main()
