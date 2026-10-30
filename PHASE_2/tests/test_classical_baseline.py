"""
tests/test_classical_baseline.py — Unit Tests for Classical Ground Truth & Baselines
"""
import pytest
from src.classical_baseline import solve_exhaustive, assignment_to_bitstring
from qff_phase2 import counts_to_x


def test_classical_optimum():
    res = solve_exhaustive()
    assert res["max_cut"] == 22
    assert res["optimal_count"] == 2


def test_complementary_optimal_partitions():
    res = solve_exhaustive()
    assert (1, 1, 0, 1, 0, 0) in res["optimal_assignments"]
    assert (0, 0, 1, 0, 1, 1) in res["optimal_assignments"]


def test_qiskit_little_endian_mapping():
    res = solve_exhaustive()
    assert "001011" in res["optimal_bitstrings"]
    assert "110100" in res["optimal_bitstrings"]


def test_counts_to_x_roundtrip():
    for idx in range(64):
        x = tuple((idx >> b) & 1 for b in range(6))
        bs = assignment_to_bitstring(x)
        assert counts_to_x(bs) == x


def test_uniform_random_baseline():
    res = solve_exhaustive()
    assert abs(res["random_mean_cut"] - 13.5) < 1e-9
    assert abs(res["random_approx_ratio"] - (13.5 / 22.0)) < 1e-9
    assert abs(res["random_p_opt"] - (2.0 / 64.0)) < 1e-9
