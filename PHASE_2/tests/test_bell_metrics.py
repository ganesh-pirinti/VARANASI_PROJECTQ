"""
tests/test_bell_metrics.py — Tests for Bell State Tomography & Uncertainty Calculations
"""
import pytest
from qff_phase2 import (
    bell_circuit,
    parity_expectation,
    bell_experiment,
    load_processor,
)


def test_bell_circuit_dimensions():
    for b in ("XX", "YY", "ZZ"):
        qc = bell_circuit(b)
        assert qc.num_qubits == 2
        assert qc.num_clbits == 2


def test_parity_formula():
    counts = {"00": 2048, "11": 2048}
    e, se = parity_expectation(counts)
    assert e == 1.0
    assert se == 0.0


def test_bell_experiment_on_d():
    p_d = load_processor("processors/processor_D.json")
    res = bell_experiment(p_d, physical_pair=(0, 2), noisy=False, shots=1024)
    assert res["fidelity"] == 1.0
    assert res["fidelity_se"] == 0.0
