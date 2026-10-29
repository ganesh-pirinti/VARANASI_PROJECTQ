"""Unit tests for PS-O1 locked instance and exact classical ground truth."""
from __future__ import annotations
import json
import os
import unittest
import numpy as np

# Ensure root import
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.problem_model import (
    NetworkPartitionModel,
    LOCKED_VERTICES,
    LOCKED_EDGES,
    LOCKED_TOTAL_WEIGHT,
    LOCKED_MAX_CUT,
)
from src.classical_baselines import get_uniform_random_baseline, solve_greedy_heuristic
from src.exact_solver import solve_exact_maxcut, compute_cut_weight

class TestInstanceAndClassicalBaselines(unittest.TestCase):
    def setUp(self):
        inst_path = os.path.join(ROOT_DIR, "data", "instance.json")
        with open(inst_path, "r", encoding="utf-8") as f:
            self.instance_data = json.load(f)
            
    def test_01_locked_instance_structure(self):
        """Verify vertex count, edge list, and total edge weight."""
        self.assertEqual(self.instance_data["num_vertices"], LOCKED_VERTICES)
        self.assertEqual(len(self.instance_data["weighted_edges"]), 9)
        self.assertEqual(self.instance_data["weighted_edges"], LOCKED_EDGES)
        
        total_w = sum(w for _, _, w in self.instance_data["weighted_edges"])
        self.assertEqual(total_w, LOCKED_TOTAL_WEIGHT)
        
    def test_02_graph_connectivity(self):
        """Verify the 6-vertex graph is fully connected (no disconnected components)."""
        adj = {i: [] for i in range(LOCKED_VERTICES)}
        for u, v, _ in LOCKED_EDGES:
            adj[u].append(v)
            adj[v].append(u)
            
        visited = set()
        def dfs(node):
            visited.add(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    dfs(neighbor)
        dfs(0)
        self.assertEqual(len(visited), LOCKED_VERTICES, "Graph must be connected.")

    def test_03_exact_maxcut_optimum(self):
        """Verify exhaustive 64-state search yields C* = 22 with exactly two complementary partitions."""
        gt = solve_exact_maxcut(LOCKED_EDGES, LOCKED_VERTICES)
        self.assertEqual(gt["max_cut_weight"], LOCKED_MAX_CUT)
        self.assertEqual(gt["optimal_solution_count"], 2)
        
        optima = gt["optimal_partitions"]
        # Both must achieve cut 22
        for p in optima:
            self.assertEqual(compute_cut_weight(list(p), LOCKED_EDGES), LOCKED_MAX_CUT)
            
        # Verify complementarity: p1_i + p2_i == 1 for all vertices i
        p1, p2 = optima[0], optima[1]
        for b1, b2 in zip(p1, p2):
            self.assertEqual(b1 + b2, 1, "Optimal assignments must be bitwise complements.")

    def test_04_uniform_random_baseline(self):
        """Verify uniform random expectation E[C] = 13.5, r = 0.6136, P_opt = 3.125%."""
        rand = get_uniform_random_baseline(LOCKED_EDGES, LOCKED_MAX_CUT)
        self.assertAlmostEqual(rand["expected_cut"], 13.5, places=5)
        self.assertAlmostEqual(rand["approximation_ratio"], 13.5 / 22.0, places=5)
        self.assertAlmostEqual(rand["p_opt"], 2.0 / 64.0, places=5)
        self.assertAlmostEqual(rand["p_opt_pct"], 3.125, places=3)

    def test_05_qubo_and_hamiltonian_consistency(self):
        """Verify QUBO energy matches -C(x) and Hamiltonian terms match edge weights."""
        model = NetworkPartitionModel(LOCKED_EDGES, LOCKED_VERTICES)
        self.assertEqual(model.total_weight, LOCKED_TOTAL_WEIGHT)
        
        # Test across sample partitions
        test_partitions = [
            (0, 0, 0, 0, 0, 0),
            (1, 1, 0, 1, 0, 0),
            (0, 0, 1, 0, 1, 1),
            (1, 0, 1, 0, 1, 0),
        ]
        for p in test_partitions:
            cut = model.evaluate_cut(p)
            qubo_e = model.evaluate_qubo_energy(p)
            self.assertEqual(cut, -int(round(qubo_e)), "QUBO energy must strictly equal -C(x).")

if __name__ == "__main__":
    unittest.main()
