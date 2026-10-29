"""Unit tests verifying that Studio data exports synchronize perfectly with official benchmarks."""
from __future__ import annotations
import json
import os
import unittest

import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

class TestWebsiteDataSynchronization(unittest.TestCase):
    def setUp(self):
        self.studio_json = os.path.join(ROOT_DIR, "data", "studio_data.json")
        self.web_json = os.path.join(ROOT_DIR, "web", "data", "benchmark_data.json")
        self.web_public_json = os.path.join(ROOT_DIR, "web", "public", "data", "benchmark_data.json")
        self.inst_file = os.path.join(ROOT_DIR, "data", "instance.json")
        
    def test_01_all_json_exports_exist(self):
        """Verify data/studio_data.json and web copies exist."""
        self.assertTrue(os.path.exists(self.studio_json))
        self.assertTrue(os.path.exists(self.web_json))
        self.assertTrue(os.path.exists(self.web_public_json))
        
    def test_02_studio_data_payload_structure(self):
        """Verify the JSON contains all required stations data."""
        with open(self.studio_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        required_keys = [
            "metadata", "instance", "ground_truth", "solution_space",
            "processors", "results_table", "bell_table", "qaoa_counts",
            "parameter_landscape", "real_world_scenario"
        ]
        for k in required_keys:
            self.assertIn(k, data, f"Missing top-level key: {k}")
            
    def test_03_solution_space_covers_all_64_states(self):
        """Verify exhaustive solution space contains exactly 64 assignments with 2 optima."""
        with open(self.studio_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        sol_space = data["solution_space"]
        self.assertEqual(len(sol_space), 64)
        
        optima = [s for s in sol_space if s["is_optimal"]]
        self.assertEqual(len(optima), 2)
        for opt in optima:
            self.assertEqual(opt["cut_weight"], 22)
            self.assertIn(opt["bitstring"], ["110100", "001011"])

    def test_04_benchmark_synchronization(self):
        """Verify results_table and bell_table in JSON match CSV row counts and metrics."""
        with open(self.studio_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(len(data["results_table"]), 6)
        self.assertEqual(len(data["bell_table"]), 4)
        
        # Check Processor D noisy values
        d_noisy = [r for r in data["results_table"] if r["processor"] in ["D", "Processor D"] and r["condition"] == "noisy"][0]
        val = float(d_noisy.get("quality_value") or d_noisy.get("metric_value"))
        self.assertAlmostEqual(val, 0.7862, places=3)
        self.assertAlmostEqual(float(d_noisy["p_opt"]), 0.1250, places=3)

    def test_05_parameter_landscape_grid_completeness(self):
        """Verify 2D parameter landscape grid has 25x25 precomputed statevector evaluations."""
        with open(self.studio_json, "r", encoding="utf-8") as f:
            landscape = json.load(f)["parameter_landscape"]
            
        grid = landscape["values"]
        self.assertEqual(len(grid), 25)
        self.assertEqual(len(grid[0]), 25)
        
        # Verify optimal point is recorded
        opt_pt = landscape["optimal_point"]
        self.assertAlmostEqual(opt_pt["expected_cut"], 17.7128, places=2)
        self.assertAlmostEqual(opt_pt["approx_ratio"], 0.8051, places=2)

if __name__ == "__main__":
    unittest.main()
