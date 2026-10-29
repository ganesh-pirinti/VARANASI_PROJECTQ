"""Unit tests for Processors A, B, and D architectural compliance and rules."""
from __future__ import annotations
import json
import os
import unittest

import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from qff_phase2 import load_processor, validate_processor_d, transpile_for, circuit_metrics
from src.qaoa_solver import construct_qaoa_circuit

class TestProcessorsCompliance(unittest.TestCase):
    def setUp(self):
        self.proc_a_file = os.path.join(ROOT_DIR, "processors", "processor_A.json")
        self.proc_b_file = os.path.join(ROOT_DIR, "processors", "processor_B.json")
        self.proc_d_file = os.path.join(ROOT_DIR, "processors", "processor_D.json")
        
        self.proc_a = load_processor(self.proc_a_file)
        self.proc_b = load_processor(self.proc_b_file)
        self.proc_d = load_processor(self.proc_d_file)

    def test_01_processor_a_specs(self):
        """Verify Processor A has 5 qubits and official basis gates."""
        self.assertEqual(self.proc_a["num_qubits"], 5)
        self.assertEqual(self.proc_a["basis_gates"], ["rz", "sx", "x", "cx"])

    def test_02_processor_b_specs(self):
        """Verify Processor B has 9 qubits, official coupling, and basis gates."""
        self.assertEqual(self.proc_b["num_qubits"], 9)
        self.assertEqual(self.proc_b["basis_gates"], ["rz", "sx", "x", "cx"])

    def test_03_processor_d_official_validation(self):
        """Verify Processor D passes validate_processor_d with 0 violations for PS-O1 (6 qubits)."""
        violations = validate_processor_d(self.proc_d, required_qubits=6)
        self.assertEqual(len(violations), 0, f"Processor D had rule violations: {violations}")

    def test_04_processor_d_architectural_constraints(self):
        """Verify Processor D constraints: qubits in [6, 12], max degree <= 4, gate set, noise rates."""
        # 1. Qubit range
        n_q = self.proc_d["num_qubits"]
        self.assertGreaterEqual(n_q, 6)
        self.assertLessEqual(n_q, 12)
        self.assertEqual(n_q, 9)
        
        # 2. Maximum degree <= 4
        degree = {i: 0 for i in range(n_q)}
        for u, v in self.proc_d["edges"]:
            degree[u] += 1
            degree[v] += 1
        for node, deg in degree.items():
            self.assertLessEqual(deg, 4, f"Node {node} exceeds maximum allowed degree of 4 (deg={deg})")
            
        # 3. Gate set
        self.assertEqual(self.proc_d["basis_gates"], ["rz", "sx", "x", "cx"])
        
        # 4. Noise rates >= official reference rates
        noise = self.proc_d["noise"]
        self.assertGreaterEqual(noise.get("p1", 0.0), 0.001)
        self.assertGreaterEqual(noise.get("p2", 0.0), 0.005)
        self.assertGreaterEqual(noise.get("p_readout", 0.0), 0.01)

    def test_05_processor_d_swap_elimination(self):
        """Verify that transpiling PS-O1 QAOA on Processor D completely eliminates SWAPs (0 SWAPs)."""
        inst_path = os.path.join(ROOT_DIR, "data", "instance.json")
        with open(inst_path, "r", encoding="utf-8") as f:
            edges = json.load(f)["weighted_edges"]
            
        qc = construct_qaoa_circuit(edges, gamma=0.5, beta=0.5, num_qubits=6, add_measurements=True)
        
        # Evaluate circuit metrics on B and D directly from the virtual QAOA circuit
        m_b = circuit_metrics(qc, self.proc_b)
        m_d = circuit_metrics(qc, self.proc_d)
        
        self.assertEqual(m_b["swaps"], 1, "Processor B must require 1 SWAP on PS-O1 circuit.")
        self.assertEqual(m_d["swaps"], 0, "Processor D must achieve 0 SWAPs on PS-O1 circuit.")
        self.assertEqual(m_d["cx_overhead"], 0, "Processor D must have 0 CX overhead.")
        self.assertEqual(m_b["cx_overhead"], 3, "Processor B must have +3 CX overhead.")
        self.assertLess(m_d["cx"], m_b["cx"], "Processor D must require fewer CX gates than Processor B.")
        self.assertLess(m_d["depth"], m_b["depth"], "Processor D must achieve lower total depth than Processor B.")
        self.assertLess(m_d["two_q_depth"], m_b["two_q_depth"], "Processor D must achieve lower two-qubit depth.")

if __name__ == "__main__":
    unittest.main()
