"""
Comprehensive Automated Test Suite for Qiskit Fall Fest 2026 PS-O1.
Validates graph models, baselines, QAOA objectives, hardware topologies,
transpilation constraints, routing pass identification, comparable baselines,
numerical overhead formulas, and artifact consistency.
"""

import os
import sys
import json
import unittest
import pandas as pd
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
from src.graph_utils import load_graph_data, classical_exact_max_cut, compute_cut_value
from src.qaoa_solver import (
    build_qaoa_circuit,
    optimize_qaoa,
    compute_expected_cut_from_statevector
)
from src.transpiler_benchmark import (
    load_processor_config,
    validate_processor_config,
    benchmark_processor_transpilation,
    RoutingStageInstrumenter
)


class TestGraphAndBaselines(unittest.TestCase):
    """Test graph loading, weights, and classical exact Max-Cut baselines."""

    def setUp(self):
        self.g6_path = os.path.join(PROJECT_ROOT, "data", "benchmark_graph_6node.json")
        self.g5_path = os.path.join(PROJECT_ROOT, "data", "benchmark_graph_5node.json")

    def test_6node_graph_validity(self):
        data = load_graph_data(self.g6_path)
        self.assertEqual(data["num_nodes"], 6)
        self.assertEqual(len(data["edges"]), 9)
        total_w = sum(e["weight"] for e in data["edges"])
        self.assertEqual(total_w, 23)
        self.assertEqual(data["total_weight"], 23)

        # Brute force verification
        res = classical_exact_max_cut(data["edges"], 6)
        self.assertEqual(res["max_cut_value"], 17.0)
        self.assertEqual(res["random_baseline_expectation"], 11.5)
        self.assertEqual(len(res["optimal_bitstrings"]), 6)
        for bstr in res["optimal_bitstrings"]:
            self.assertEqual(compute_cut_value(bstr, data["edges"]), 17.0)

        # Ensure JSON-stored values match brute-force calculations strictly
        self.assertEqual(data["classical_exact_max_cut"], 17)
        self.assertEqual(set(data["classical_optimal_partitions"]), set(res["optimal_bitstrings"]))
        self.assertEqual(data["random_cut_expectation"], 11.5)

    def test_5node_graph_validity(self):
        data = load_graph_data(self.g5_path)
        self.assertEqual(data["num_nodes"], 5)
        self.assertEqual(len(data["edges"]), 7)
        total_w = sum(e["weight"] for e in data["edges"])
        self.assertEqual(total_w, 18)
        self.assertEqual(data["total_weight"], 18)

        # Brute force verification
        res = classical_exact_max_cut(data["edges"], 5)
        self.assertEqual(res["max_cut_value"], 14.0)
        self.assertEqual(res["random_baseline_expectation"], 9.0)
        expected_opts = {"00101", "01001", "10110", "11010"}
        self.assertEqual(set(res["optimal_bitstrings"]), expected_opts)
        for bstr in res["optimal_bitstrings"]:
            self.assertEqual(compute_cut_value(bstr, data["edges"]), 14.0)

        # Ensure JSON-stored values match brute-force calculations strictly
        self.assertEqual(data["classical_exact_max_cut"], 14)
        self.assertEqual(set(data["classical_optimal_partitions"]), expected_opts)
        self.assertEqual(data["random_cut_expectation"], 9.0)

    def test_5node_regression_against_erroneous_partitions(self):
        """Regression test: verify that previously miscalculated bitstrings are strictly rejected."""
        data = load_graph_data(self.g5_path)
        erroneous_bitstrings = ["01011", "01101", "10010", "10100"]
        stored_opts = set(data["classical_optimal_partitions"])
        for bstr in erroneous_bitstrings:
            self.assertNotIn(bstr, stored_opts, f"Erroneous bitstring {bstr} must not be in stored optimal partitions.")
            val = compute_cut_value(bstr, data["edges"])
            self.assertLess(val, 14.0, f"Erroneous bitstring {bstr} must have cut < 14.0, got {val}.")

    def test_canonical_graph_file_alias_consistency(self):
        """Verify that data/benchmark_graph.json matches data/benchmark_graph_6node.json exactly."""
        alias_path = os.path.join(PROJECT_ROOT, "data", "benchmark_graph.json")
        data_alias = load_graph_data(alias_path)
        data_6 = load_graph_data(self.g6_path)
        self.assertEqual(data_alias["num_nodes"], data_6["num_nodes"])
        self.assertEqual(data_alias["edges"], data_6["edges"])
        self.assertEqual(data_alias["total_weight"], data_6["total_weight"])
        self.assertEqual(data_alias["classical_exact_max_cut"], data_6["classical_exact_max_cut"])
        self.assertEqual(data_alias["classical_optimal_partitions"], data_6["classical_optimal_partitions"])


class TestQAOACircuitAndObjective(unittest.TestCase):
    """Test QAOA ansatz construction and objective consistency."""

    def setUp(self):
        self.g5_path = os.path.join(PROJECT_ROOT, "data", "benchmark_graph_5node.json")
        self.g5 = load_graph_data(self.g5_path)

    def test_qaoa_circuit_structure(self):
        qc = build_qaoa_circuit(self.g5["edges"], 5, gamma=[0.5], beta=[0.5], p=1)
        self.assertEqual(qc.num_qubits, 5)
        # 5 H gates + 7 RZZ gates + 5 RX gates
        ops = qc.count_ops()
        self.assertEqual(ops.get("h", 0), 5)
        self.assertEqual(ops.get("rzz", 0), 7)
        self.assertEqual(ops.get("rx", 0), 5)

    def test_qaoa_optimization_bound(self):
        res = optimize_qaoa(self.g5["edges"], 5, p=1, seed=42)
        exp_cut = res["expected_cut"]
        approx_ratio = exp_cut / 14.0
        self.assertLessEqual(approx_ratio, 1.000001)
        # Must beat random expectation of 9.0
        self.assertGreater(exp_cut, 9.0)


class TestProcessorTopologiesAndTranspilation(unittest.TestCase):
    """Test official processor topologies, validation, and compilation constraints."""

    def setUp(self):
        self.pa_path = os.path.join(PROJECT_ROOT, "processors", "processor_a.json")
        self.pb_path = os.path.join(PROJECT_ROOT, "processors", "processor_b.json")
        self.pa = load_processor_config(self.pa_path)
        self.pb = load_processor_config(self.pb_path)
        self.g6 = load_graph_data(os.path.join(PROJECT_ROOT, "data", "benchmark_graph_6node.json"))
        self.g5 = load_graph_data(os.path.join(PROJECT_ROOT, "data", "benchmark_graph_5node.json"))

    def test_processor_validation_catches_invalid_configs(self):
        """Verify that validate_processor_config strictly rejects invalid configurations."""
        # Missing required field
        with self.assertRaises(ValueError):
            validate_processor_config({"processor_id": "P", "num_qubits": 2, "basis_gates": ["cx"]})
        # Invalid qubit count
        with self.assertRaises(ValueError):
            validate_processor_config({"processor_id": "P", "num_qubits": 0, "basis_gates": ["cx"], "coupling_map": []})
        # Self-loop
        with self.assertRaises(ValueError):
            validate_processor_config({"processor_id": "P", "num_qubits": 2, "basis_gates": ["cx"], "coupling_map": [[0, 0]]})
        # Out of bounds
        with self.assertRaises(ValueError):
            validate_processor_config({"processor_id": "P", "num_qubits": 2, "basis_gates": ["cx"], "coupling_map": [[0, 2], [2, 0]]})
        # Asymmetric
        with self.assertRaises(ValueError):
            validate_processor_config({"processor_id": "P", "num_qubits": 2, "basis_gates": ["cx"], "coupling_map": [[0, 1]]})

    def test_processor_topologies(self):
        self.assertEqual(self.pa["num_qubits"], 5)
        self.assertEqual(len(self.pa["coupling_edges_undirected"]), 4)
        self.assertEqual(self.pb["num_qubits"], 9)
        self.assertEqual(len(self.pb["coupling_edges_undirected"]), 12)

    def test_processor_a_6qubit_infeasibility(self):
        qc6 = build_qaoa_circuit(self.g6["edges"], 6, [0.5], [0.5], p=1)
        res = benchmark_processor_transpilation(qc6, self.pa, instance_name="6-Node", optimization_levels=[1, 2, 3])
        self.assertEqual(len(res), 3)
        for r in res:
            self.assertEqual(r["status"], "INFEASIBLE_CAPACITY_EXCEEDED")
            self.assertIsNone(r["physical_cx"])
            self.assertIsNone(r["physical_depth"])
            self.assertIsNone(r["routing_pass"])

    def test_processor_b_6qubit_compilation(self):
        qc6 = build_qaoa_circuit(self.g6["edges"], 6, [0.4856], [0.3875], p=1)
        res = benchmark_processor_transpilation(qc6, self.pb, instance_name="6-Node", optimization_levels=[1, 2, 3], seed=42)
        self.assertEqual(len(res), 3)
        for r in res:
            self.assertEqual(r["status"], "COMPILED_SUCCESSFULLY")
            self.assertEqual(r["logical_cx"], 18)  # 9 edges * 2
            self.assertGreaterEqual(r["physical_cx"], 18)
            self.assertEqual(r["cx_overhead"], r["physical_cx"] - r["logical_cx"])
            self.assertAlmostEqual(r["routing_overhead_ratio"], r["cx_overhead"] / 18.0)
            self.assertIsNotNone(r["circuit_routed_physical"])
            self.assertIsNotNone(r["circuit_routed_with_swaps"])

    def test_both_processors_5qubit_compilation(self):
        qc5 = build_qaoa_circuit(self.g5["edges"], 5, [0.4308], [0.9041], p=1)
        res_a = benchmark_processor_transpilation(qc5, self.pa, instance_name="5-Node", optimization_levels=[1, 2, 3], seed=42)
        res_b = benchmark_processor_transpilation(qc5, self.pb, instance_name="5-Node", optimization_levels=[1, 2, 3], seed=42)

        # Processor A (Tree): 2 SWAPs, 20 physical CX (14 logical + 6 from 2 SWAPs)
        for r in res_a:
            self.assertEqual(r["status"], "COMPILED_SUCCESSFULLY")
            self.assertEqual(r["logical_cx"], 14)
            self.assertEqual(r["routing_swaps"], 2)
            self.assertEqual(r["physical_cx"], 20)
            self.assertEqual(r["cx_overhead"], 6)
            self.assertAlmostEqual(r["routing_overhead_ratio"], 6 / 14.0)

        # Processor B (Heavy-Hex): 1 SWAP, 17 physical CX (14 logical + 3 from 1 SWAP)
        for r in res_b:
            self.assertEqual(r["status"], "COMPILED_SUCCESSFULLY")
            self.assertEqual(r["logical_cx"], 14)
            self.assertEqual(r["routing_swaps"], 1)
            self.assertEqual(r["physical_cx"], 17)
            self.assertEqual(r["cx_overhead"], 3)
            self.assertAlmostEqual(r["routing_overhead_ratio"], 3 / 14.0)

    def test_routing_pass_identification_and_boundary(self):
        """Verify that RoutingStageInstrumenter correctly identifies a recognized routing pass and captures real routing output."""
        qc6 = build_qaoa_circuit(self.g6["edges"], 6, [0.4856], [0.3875], p=1)
        res_b = benchmark_processor_transpilation(qc6, self.pb, instance_name="6-Node", optimization_levels=[1, 2, 3], seed=42)
        for r in res_b:
            # 1. Routing pass must be an intended, recognized routing algorithm
            self.assertIn(r["routing_pass"], RoutingStageInstrumenter.ROUTING_PASS_NAMES)

            # 2. Intermediate circuit captured at the routing boundary must be a valid QuantumCircuit
            routed_circ = r["circuit_routed_with_swaps"]
            self.assertIsInstance(routed_circ, QuantumCircuit)
            self.assertEqual(routed_circ.num_qubits, self.pb["num_qubits"])

            # 3. Intermediate circuit must contain explicit SWAP gates matching recorded routing_swaps
            swaps_in_intermediate = routed_circ.count_ops().get("swap", 0)
            self.assertEqual(swaps_in_intermediate, r["routing_swaps"])
            self.assertGreater(swaps_in_intermediate, 0)

            # 4. Final physical circuit must have 0 SWAP gates (all decomposed into CXs)
            physical_circ = r["circuit_routed_physical"]
            self.assertIsInstance(physical_circ, QuantumCircuit)
            self.assertEqual(physical_circ.count_ops().get("swap", 0), 0)
            self.assertEqual(physical_circ.count_ops().get("cx", 0), r["physical_cx"])

            # 5. All gates in final physical circuit must be in native basis
            allowed_gates = set(self.pb["basis_gates"] + ["barrier"])
            for op in physical_circ.count_ops().keys():
                self.assertIn(op, allowed_gates)

    def test_comparable_baseline_optimization_levels(self):
        """Verify that logical baselines are matched per optimization level."""
        qc6 = build_qaoa_circuit(self.g6["edges"], 6, [0.4856], [0.3875], p=1)
        res_b = benchmark_processor_transpilation(qc6, self.pb, instance_name="6-Node", optimization_levels=[1, 2, 3], seed=42)
        for r in res_b:
            # Baseline CX and depth must be non-zero and match level
            self.assertEqual(r["logical_cx"], 18)
            self.assertEqual(r["logical_depth"], 35)
            self.assertEqual(r["cx_overhead"], r["physical_cx"] - r["logical_cx"])
            self.assertEqual(r["depth_overhead"], r["physical_depth"] - r["logical_depth"])
            self.assertAlmostEqual(r["routing_overhead_ratio"], r["cx_overhead"] / r["logical_cx"])

    def test_routing_instrumenter_negative_non_routing_passes_only(self):
        """Negative test: verify that validate() strictly fails if only non-routing passes call back."""
        inst = RoutingStageInstrumenter()
        qc = QuantumCircuit(2)
        qc.cx(0, 1)
        dag = circuit_to_dag(qc)

        class MockPass:
            def __init__(self, name):
                self._name = name
            def name(self):
                return self._name

        # Simulate callbacks from non-routing passes only (e.g. SetLayout, CheckMap, ApplyLayout, BasisTranslator)
        non_routing_passes = [
            "SetLayout", "VF2PostLayout", "CheckMap", "ApplyLayout",
            "BasisTranslator", "Optimize1qGatesDecomposition"
        ]
        for p_name in non_routing_passes:
            inst(MockPass(p_name), dag, time=0.01, property_set={})

        self.assertTrue(inst.instrumentation_ran)
        self.assertIsNone(inst.routing_pass_name)
        self.assertIsNone(inst.routed_circuit)
        with self.assertRaises(RuntimeError) as ctx:
            inst.validate()
        self.assertIn("failed to observe an intended routing pass", str(ctx.exception))

    def test_routing_instrumenter_validation_failure_when_unexecuted(self):
        """Verify that RoutingStageInstrumenter.validate() raises if no passes ran at all."""
        inst = RoutingStageInstrumenter()
        with self.assertRaises(RuntimeError) as ctx:
            inst.validate()
        self.assertIn("no compiler passes were intercepted", str(ctx.exception))


class TestOutputConsistency(unittest.TestCase):
    """Test consistency across generated CSV, JSON, and Markdown tables."""

    def setUp(self):
        self.results_dir = os.path.join(PROJECT_ROOT, "results")
        self.csv_file = os.path.join(self.results_dir, "benchmark_metrics.csv")
        self.json_file = os.path.join(self.results_dir, "qaoa_summary.json")
        self.md_file = os.path.join(self.results_dir, "metrics_table.md")

    def test_results_files_exist_and_non_empty(self):
        self.assertTrue(os.path.exists(self.csv_file), "benchmark_metrics.csv missing")
        self.assertTrue(os.path.exists(self.json_file), "qaoa_summary.json missing")
        self.assertTrue(os.path.exists(self.md_file), "metrics_table.md missing")
        self.assertGreater(os.path.getsize(self.csv_file), 0)
        self.assertGreater(os.path.getsize(self.json_file), 0)
        self.assertGreater(os.path.getsize(self.md_file), 0)

    def test_json_and_csv_metric_consistency(self):
        """Verify that every record in CSV strictly matches the record in JSON summary."""
        with open(self.json_file, "r", encoding="utf-8") as f:
            summary = json.load(f)
        df = pd.read_csv(self.csv_file)
        json_records = summary["benchmark_records"]
        self.assertEqual(len(df), len(json_records))

        for idx, row in df.iterrows():
            rec = json_records[idx]
            self.assertEqual(row["instance"], rec["instance"])
            self.assertEqual(row["processor_id"], rec["processor_id"])
            self.assertEqual(int(row["opt_level"]), int(rec["opt_level"]))
            self.assertEqual(row["status"], rec["status"])

            if row["status"] == "COMPILED_SUCCESSFULLY":
                self.assertEqual(int(row["physical_depth"]), int(rec["physical_depth"]))
                self.assertEqual(int(row["routing_swaps"]), int(rec["routing_swaps"]))
                self.assertEqual(str(row["routing_pass"]), str(rec["routing_pass"]))
                self.assertEqual(int(row["physical_cx"]), int(rec["physical_cx"]))
                self.assertEqual(int(row["cx_overhead"]), int(rec["cx_overhead"]))
                self.assertAlmostEqual(float(row["routing_overhead_ratio"]), float(rec["routing_overhead_ratio"]), places=5)
                self.assertEqual(int(row["total_gates"]), int(rec["total_gates"]))

                # Verify numerical overhead identities
                logical_cx = int(rec["logical_cx"])
                physical_cx = int(rec["physical_cx"])
                cx_overhead = int(rec["cx_overhead"])
                self.assertEqual(cx_overhead, physical_cx - logical_cx)
                self.assertAlmostEqual(rec["routing_overhead_ratio"], cx_overhead / logical_cx, places=5)
                self.assertEqual(rec["depth_overhead"], rec["physical_depth"] - rec["logical_depth"])
                self.assertEqual(rec["total_gates"], rec["single_qubit_gates"] + rec["two_qubit_gates"])
                self.assertEqual(rec["two_qubit_gates"], rec["physical_cx"] + rec["physical_swaps"])
                self.assertEqual(rec["physical_swaps"], 0)

    def test_json_summary_baselines(self):
        with open(self.json_file, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertEqual(summary["canonical_6node"]["classical_optimal_cut"], 17.0)
        self.assertEqual(summary["canonical_6node"]["random_baseline"], 11.5)
        self.assertGreater(summary["canonical_6node"]["qaoa_expected_cut"], 11.5)
        self.assertLessEqual(summary["canonical_6node"]["approximation_ratio"], 1.0)

        self.assertEqual(summary["codesign_5node"]["classical_optimal_cut"], 14.0)
        self.assertEqual(summary["codesign_5node"]["random_baseline"], 9.0)
        self.assertGreater(summary["codesign_5node"]["qaoa_expected_cut"], 9.0)
        self.assertLessEqual(summary["codesign_5node"]["approximation_ratio"], 1.0)

        # Team metadata assertions
        meta = summary.get("team_metadata", {})
        self.assertEqual(meta.get("team_name"), "YOUR_ACTUAL_REGISTERED_TEAM_NAME")
        self.assertEqual(meta.get("team_id"), "YOUR_ACTUAL_REGISTERED_PARTICIPANT_OR_TEAM_ID")
        self.assertEqual(meta.get("team_leader", {}).get("name"), "Ganesh Pirinti")
        self.assertEqual(len(meta.get("team_members", [])), 2)
        self.assertEqual(meta.get("team_members", [])[1]["name"], "Mohammed Sadiq")


if __name__ == "__main__":
    unittest.main()
