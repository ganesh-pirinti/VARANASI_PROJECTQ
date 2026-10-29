"""Automated unit test suite for VARANASI Phase 2 PS-O1."""
import unittest
import json
import os
import csv
from qiskit import QuantumCircuit

import qff_phase2
from qff_phase2 import (
    load_processor,
    validate_processor_d,
    PROCESSOR_A,
    PROCESSOR_B,
    circuit_metrics,
    BASIS_GATES,
)
from src.exact_solver import load_pso1_instance, solve_exact_maxcut
from src.qaoa_solver import construct_qaoa_circuit

class TestPhase2Validation(unittest.TestCase):
    
    def test_processor_d_compliance(self):
        """Verify Processor D passes all official rules without violation."""
        proc_d = load_processor("processors/processor_D.json")
        self.assertEqual(proc_d["name"], "Processor D")
        self.assertEqual(proc_d["team"], "VARANASI")
        self.assertEqual(proc_d["problem_statement"], "PS-O1")
        self.assertEqual(proc_d["num_qubits"], 9)
        self.assertLessEqual(proc_d["num_qubits"], 12)
        self.assertGreaterEqual(proc_d["num_qubits"], 6)
        
        # Max degree check
        deg = {}
        for u, v in proc_d["edges"]:
            deg[u] = deg.get(u, 0) + 1
            deg[v] = deg.get(v, 0) + 1
        for q, d in deg.items():
            self.assertLessEqual(d, 4, f"Qubit {q} degree {d} exceeds max degree 4")
            
        # Official validator
        errs = validate_processor_d(proc_d, required_qubits=6)
        self.assertEqual(errs, [], f"Processor D rule check failed: {errs}")

    def test_instance_integrity(self):
        """Verify locked instance file matches instances.json."""
        inst = load_pso1_instance("data/instance.json")
        with open("instances.json") as f:
            full = json.load(f)["PS-O1"]
        self.assertEqual(inst["num_vertices"], 6)
        self.assertEqual(len(inst["weighted_edges"]), 9)
        self.assertEqual(inst["weighted_edges"], full["weighted_edges"])
        self.assertEqual(sum(w for _, _, w in inst["weighted_edges"]), 27)

    def test_exact_classical_optimum(self):
        """Verify exact ground truth C* = 22 and random baseline."""
        inst = load_pso1_instance("data/instance.json")
        res = solve_exact_maxcut(inst["weighted_edges"], 6)
        self.assertEqual(res["max_cut_weight"], 22)
        self.assertEqual(res["optimal_solution_count"], 2)
        self.assertAlmostEqual(res["uniform_random_mean_cut"], 13.5, places=4)
        self.assertAlmostEqual(res["uniform_random_approx_ratio"], 13.5 / 22.0, places=4)
        self.assertAlmostEqual(res["uniform_random_p_opt"], 2.0 / 64.0, places=4)

    def test_processor_capacity_rules(self):
        """Verify Processor A is marked non-executable for 6 qubits."""
        qc = QuantumCircuit(6)
        m_a = circuit_metrics(qc, PROCESSOR_A)
        self.assertFalse(m_a["executable"])
        self.assertIn("needs 6 qubits > 5", m_a["reason"])

    def test_processor_d_swap_elimination(self):
        """Verify Processor D eliminates SWAPs on PS-O1 QAOA circuit."""
        inst = load_pso1_instance("data/instance.json")
        qc = construct_qaoa_circuit(inst["weighted_edges"], gamma=0.5, beta=0.5, num_qubits=6)
        proc_d = load_processor("processors/processor_D.json")
        m_d = circuit_metrics(qc, proc_d)
        self.assertTrue(m_d["executable"])
        self.assertEqual(m_d["logical_cx"], 18)
        self.assertEqual(m_d["cx"], 18)
        self.assertEqual(m_d["swaps"], 0)
        self.assertEqual(m_d["cx_overhead"], 0)

    def test_results_csv_schema(self):
        """Verify results.csv exists and has correct columns."""
        path = "results/tables/results.csv"
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
        expected_cols = [
            "problem_id", "processor", "condition", "executable", "logical_qubits",
            "physical_qubits", "logical_cx", "cx", "depth", "two_q_depth",
            "swaps", "cx_overhead", "shots", "quality_metric", "quality_value",
            "p_opt", "classical_optimum", "random_baseline"
        ]
        self.assertEqual(header, expected_cols)

    def test_bell_csv_schema(self):
        """Verify bell.csv exists and contains 4 rows."""
        path = "results/tables/bell.csv"
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        self.assertEqual(len(rows), 4)

    def test_figures_exist(self):
        """Verify all generated figures exist and are non-empty."""
        expected_figs = [
            "network_partitioning_graph.png",
            "processor_topologies.png",
            "bell_fidelity_comparison.png",
            "qaoa_cut_distribution.png",
            "processor_resource_comparison.png",
        ]
        for fig in expected_figs:
            path = os.path.join("results/figures", fig)
            self.assertTrue(os.path.exists(path), f"Missing figure: {path}")
            self.assertGreater(os.path.getsize(path), 1000, f"Empty figure: {path}")

if __name__ == "__main__":
    unittest.main()
