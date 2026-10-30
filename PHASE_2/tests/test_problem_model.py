"""
tests/test_problem_model.py — Unit Tests for Locked Problem Graph & QUBO
"""
import pytest
from src.problem_model import (
    NUM_VERTICES,
    NUM_EDGES,
    TOTAL_WEIGHT,
    LOCKED_EDGES,
    compute_cut_weight,
    construct_qubo_matrix,
    evaluate_qubo,
)


def test_vertex_and_edge_counts():
    vertices = set()
    for u, v, _ in LOCKED_EDGES:
        vertices.add(u)
        vertices.add(v)
    assert len(vertices) == NUM_VERTICES == 6
    assert len(LOCKED_EDGES) == NUM_EDGES == 9


def test_total_graph_weight():
    assert sum(w for _, _, w in LOCKED_EDGES) == TOTAL_WEIGHT == 27


def test_qubo_equivalence_all_64_states():
    """Verify QUBO(x) == -C(x) exactly for all 64 bitstrings."""
    Q, const = construct_qubo_matrix(LOCKED_EDGES)
    for idx in range(64):
        x = tuple((idx >> b) & 1 for b in range(6))
        cut = compute_cut_weight(x, LOCKED_EDGES)
        qubo_val = evaluate_qubo(x, Q, const)
        assert abs(qubo_val - (-float(cut))) < 1e-9, f"QUBO mismatch at {x}"
