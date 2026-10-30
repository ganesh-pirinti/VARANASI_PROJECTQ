"""
tests/test_processor_configs.py — Tests for Processors A, B, and D Rules
"""
import pytest
from qff_phase2 import (
    PROCESSOR_A,
    PROCESSOR_B,
    load_processor,
    validate_processor_d,
    BASIS_GATES,
    P1_DEPOL,
    P2_DEPOL,
    P_READOUT,
)


def test_processor_a_capacity():
    assert PROCESSOR_A["num_qubits"] == 5
    assert len(PROCESSOR_A["edges"]) == 4


def test_processor_b_topology():
    assert PROCESSOR_B["num_qubits"] == 9
    assert len(PROCESSOR_B["edges"]) == 12


def test_processor_d_rules():
    p_d = load_processor("processors/processor_D.json")
    errs = validate_processor_d(p_d, required_qubits=6)
    assert errs == [], f"Processor D rule check failed: {errs}"
    assert 6 <= p_d["num_qubits"] <= 12
    assert set(p_d["basis_gates"]) == set(BASIS_GATES)

    # Max degree <= 4
    deg = {}
    for u, v in p_d["edges"]:
        deg[u] = deg.get(u, 0) + 1
        deg[v] = deg.get(v, 0) + 1
    for q, d in deg.items():
        assert d <= 4, f"Qubit {q} degree {d} > 4"

    # Noise >= official
    nz = p_d["noise"]
    assert nz["p1"] >= P1_DEPOL
    assert nz["p2"] >= P2_DEPOL
    assert nz["p_readout"] >= P_READOUT
