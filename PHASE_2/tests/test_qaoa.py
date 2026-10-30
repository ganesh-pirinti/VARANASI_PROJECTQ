"""
tests/test_qaoa.py — Tests for QAOA Circuit & Multi-Start Parameter Optimization
"""
import pytest
from src.problem_model import LOCKED_EDGES
from src.qaoa_solver import build_qaoa_circuit, QAOASolver


def test_qaoa_circuit_structure():
    qc = build_qaoa_circuit([0.3], [0.4], LOCKED_EDGES, 6, measure=True)
    assert qc.num_qubits == 6
    ops = qc.count_ops()
    assert ops.get("h", 0) == 6
    assert ops.get("cx", 0) == 18  # 2 CX per edge * 9 edges
    assert ops.get("measure", 0) == 6


def test_qaoa_optimization_seeds():
    import numpy as np
    solver = QAOASolver(edges=LOCKED_EDGES, num_qubits=6)
    opt = solver.optimize_multi_start(seeds=[0, 1, 2, 3, 4], maxiter=60)
    assert len(opt["seed_results"]) == 5
    for r in opt["seed_results"]:
        s = r["seed"]
        expected_init = np.random.default_rng(s).uniform(0.0, np.pi, size=2)
        assert abs(r["initial_gamma"][0] - expected_init[0]) < 1e-9
        assert abs(r["initial_beta"][0] - expected_init[1]) < 1e-9
    best = opt["best_run"]
    assert best["seed"] == 3
    assert best["approx_ratio"] > 0.75, f"Approximation ratio {best['approx_ratio']} too low"
