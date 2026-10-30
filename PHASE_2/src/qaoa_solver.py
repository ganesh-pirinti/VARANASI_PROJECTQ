"""
src/qaoa_solver.py — QAOA Circuit Construction & Multi-Restart Optimization
===========================================================================

Builds QAOA (p=1) circuits conforming to official basis gates (rz, sx, x, cx),
evaluates exact statevector expectation, executes multi-start classical optimization
using numpy.random.default_rng(seed) across mandatory seeds [0, 1, 2, 3, 4],
and samples transpiled circuits under ideal and noisy conditions.
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Any
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from qff_phase2 import (
    counts_to_x,
    transpile_for,
    simulator,
    SHOTS,
    SEED,
)
from src.problem_model import LOCKED_EDGES, NUM_VERTICES, compute_cut_weight


def build_qaoa_circuit(
    gamma: float | List[float],
    beta: float | List[float],
    edges: List[Tuple[int, int, int]] = LOCKED_EDGES,
    num_qubits: int = NUM_VERTICES,
    measure: bool = True,
) -> QuantumCircuit:
    """
    Construct QAOA p=1 circuit:
      1. Uniform superposition: H on all qubits
      2. Cost layer: CX(u, v) -> Rz(gamma * w) -> CX(u, v) for each edge
      3. Mixer layer: Rx(2 * beta) on all qubits
      4. Measurement on all qubits
    """
    if isinstance(gamma, (int, float)):
        gammas = [float(gamma)]
    else:
        gammas = [float(g) for g in gamma]

    if isinstance(beta, (int, float)):
        betas = [float(beta)]
    else:
        betas = [float(b) for b in beta]

    p = len(gammas)
    qc = QuantumCircuit(num_qubits, num_qubits if measure else 0)

    # Initial state |+>^n
    qc.h(range(num_qubits))

    for layer in range(p):
        g = gammas[layer]
        b = betas[layer]

        # Cost layer
        for u, v, w in edges:
            qc.cx(u, v)
            qc.rz(g * float(w), v)
            qc.cx(u, v)

        # Mixer layer
        for q in range(num_qubits):
            qc.rx(2.0 * b, q)

    if measure:
        qc.measure(range(num_qubits), range(num_qubits))

    return qc


def evaluate_statevector_expectation(
    gamma: float,
    beta: float,
    edges: List[Tuple[int, int, int]] = LOCKED_EDGES,
    num_qubits: int = NUM_VERTICES,
) -> float:
    """
    Compute exact expectation value <psi(gamma, beta)| C |psi(gamma, beta)>
    via statevector simulation without shot noise.
    """
    qc = build_qaoa_circuit(gamma, beta, edges, num_qubits, measure=False)
    qc.save_statevector()
    sim = AerSimulator(method="statevector", seed_simulator=SEED)
    sv = sim.run(qc).result().get_statevector()
    probs = np.abs(sv.data) ** 2

    exp_cut = 0.0
    for idx in range(1 << num_qubits):
        x = tuple((idx >> b) & 1 for b in range(num_qubits))
        cut = compute_cut_weight(x, edges)
        exp_cut += probs[idx] * cut

    return float(exp_cut)


class QAOASolver:
    """Manages parameter optimization and multi-start execution."""

    def __init__(self, edges: List[Tuple[int, int, int]] = LOCKED_EDGES, num_qubits: int = NUM_VERTICES):
        self.edges = edges
        self.num_qubits = num_qubits

    def optimize_multi_start(
        self,
        seeds: List[int] = [0, 1, 2, 3, 4],
        maxiter: int = 80,
        c_star: float = 22.0,
    ) -> Dict[str, Any]:
        """
        Execute mandatory multi-start classical optimization protocol:
          - numpy.random.default_rng(seed)
          - Initial gamma, beta in [0, pi]
          - COBYLA optimizer minimizing -<C>
        """
        seed_results = []
        best_run = None
        best_exp = -1.0

        for s in seeds:
            rng = np.random.default_rng(s)
            init_gamma, init_beta = [float(v) for v in rng.uniform(0.0, np.pi, size=2)]

            def loss(params):
                g, b = params
                return -evaluate_statevector_expectation(g, b, self.edges, self.num_qubits)

            res = minimize(
                loss,
                [init_gamma, init_beta],
                method="COBYLA",
                options={"maxiter": maxiter},
            )

            opt_g = float(res.x[0])
            opt_b = float(res.x[1])
            exp_c = -float(res.fun)
            ar = exp_c / c_star

            record = {
                "seed": s,
                "initial_gamma": [init_gamma],
                "initial_beta": [init_beta],
                "optimized_gamma": [opt_g],
                "optimized_beta": [opt_b],
                "expected_cut": exp_c,
                "approx_ratio": ar,
                "iterations": int(res.nfev),
                "optimizer_success": bool(res.success),
            }
            seed_results.append(record)

            if exp_c > best_exp:
                best_exp = exp_c
                best_run = record

        approx_ratios = [r["approx_ratio"] for r in seed_results]
        return {
            "p": 1,
            "seed_results": seed_results,
            "best_run": best_run,
            "best_gamma": best_run["optimized_gamma"],
            "best_beta": best_run["optimized_beta"],
            "mean_approx_ratio": float(np.mean(approx_ratios)),
            "std_approx_ratio": float(np.std(approx_ratios)),
        }
