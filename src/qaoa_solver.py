"""QAOA Implementation, Parameter Optimization, and Sampling for PS-O1.

Supports depth p=1 (required) and p=2 (optional), classical optimizer with
multiple restart seeds, circuit construction adhering to official basis gates,
and sampling on ideal and noisy backends.
"""
from __future__ import annotations
import json
from typing import List, Tuple, Dict, Any
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
    circuit_metrics,
)
from src.exact_solver import compute_cut_weight

def construct_qaoa_circuit(
    weighted_edges: List[List[int]],
    gamma: List[float] | float,
    beta: List[float] | float,
    num_qubits: int = 6,
    add_measurements: bool = True,
) -> QuantumCircuit:
    """Construct QAOA circuit for Max-Cut with depth p.
    
    Unitary operators:
    - Initial state: |+>^{\\otimes n} via Hadamard gates
    - Cost Hamiltonian evolution: e^{-i \\gamma_k H_C} where H_C = sum_{(u,v)} w_{uv} (I - Z_u Z_v)/2
      Implemented via CX(u, v) -> Rz(gamma_k * w_{uv}) -> CX(u, v)
    - Mixer Hamiltonian evolution: e^{-i \\beta_k H_M} where H_M = sum_i X_i
      Implemented via Rx(2 * beta_k) on each qubit
    """
    if isinstance(gamma, (int, float)):
        gamma = [float(gamma)]
    if isinstance(beta, (int, float)):
        beta = [float(beta)]
        
    p = len(gamma)
    assert len(beta) == p, f"gamma and beta must have same depth, got {len(gamma)} vs {len(beta)}"
    
    qc = QuantumCircuit(num_qubits, num_qubits if add_measurements else 0)
    qc.h(range(num_qubits))
    
    for layer in range(p):
        g = float(gamma[layer])
        b = float(beta[layer])
        
        # Cost layer
        for u, v, w in weighted_edges:
            angle = float(g * w)
            qc.cx(u, v)
            qc.rz(angle, v)
            qc.cx(u, v)
            
        # Mixer layer
        for i in range(num_qubits):
            qc.rx(float(2.0 * b), i)
            
    if add_measurements:
        qc.measure(range(num_qubits), range(num_qubits))
        
    return qc

class QAOASolver:
    """QAOA Solver and optimizer for the PS-O1 instance."""
    
    def __init__(self, weighted_edges: List[List[int]], num_qubits: int = 6):
        self.weighted_edges = weighted_edges
        self.num_qubits = num_qubits
        self.sv_sim = AerSimulator(method="statevector", seed_simulator=SEED)
        
    def evaluate_statevector_expectation(self, gamma: List[float], beta: List[float]) -> float:
        """Compute the exact theoretical expectation value <C> of cut weight."""
        qc = construct_qaoa_circuit(
            self.weighted_edges,
            gamma=gamma,
            beta=beta,
            num_qubits=self.num_qubits,
            add_measurements=False,
        )
        qc.save_statevector()
        result = self.sv_sim.run(qc).result()
        sv = np.asarray(result.get_statevector())
        probabilities = np.abs(sv) ** 2
        
        exp_cut = 0.0
        for state_idx, prob in enumerate(probabilities):
            x = tuple((state_idx >> bit) & 1 for bit in range(self.num_qubits))
            exp_cut += prob * compute_cut_weight(x, self.weighted_edges)
        return float(exp_cut)

    def optimize_parameters(
        self,
        seeds: List[int],
        p: int = 1,
        maxiter: int = 80,
        c_star: float = 22.0,
    ) -> Dict[str, Any]:
        """Run classical optimizer across multiple initialization seeds.
        
        Each initial parameter is drawn uniformly from [0, pi] as required.
        """
        seed_results = []
        
        for seed in seeds:
            rng = np.random.default_rng(seed)
            init_gamma = rng.uniform(0, np.pi, size=p).tolist()
            init_beta = rng.uniform(0, np.pi, size=p).tolist()
            init_params = np.array(init_gamma + init_beta)
            
            def loss_func(params):
                g = params[:p]
                b = params[p:]
                return -self.evaluate_statevector_expectation(g, b)
                
            res = minimize(
                loss_func,
                init_params,
                method="COBYLA",
                options={"maxiter": maxiter},
            )
            
            opt_gamma = res.x[:p].tolist()
            opt_beta = res.x[p:].tolist()
            exp_cut = -float(res.fun)
            approx_ratio = exp_cut / c_star
            
            seed_results.append({
                "seed": seed,
                "initial_gamma": init_gamma,
                "initial_beta": init_beta,
                "optimized_gamma": opt_gamma,
                "optimized_beta": opt_beta,
                "expected_cut": exp_cut,
                "approx_ratio": approx_ratio,
                "optimizer_success": res.success,
                "iterations": res.nfev,
            })
            
        # Find best parameter set
        best_run = max(seed_results, key=lambda item: item["expected_cut"])
        ratios = [item["approx_ratio"] for item in seed_results]
        
        return {
            "p": p,
            "seed_results": seed_results,
            "best_run": best_run,
            "mean_approx_ratio": float(np.mean(ratios)),
            "std_approx_ratio": float(np.std(ratios)),
            "best_gamma": best_run["optimized_gamma"],
            "best_beta": best_run["optimized_beta"],
        }

    def sample_processor(
        self,
        processor: dict,
        gamma: List[float],
        beta: List[float],
        noisy: bool,
        shots: int = SHOTS,
        c_star: int = 22,
        optimal_partitions: Set[Tuple[int, ...]] | None = None,
    ) -> Dict[str, Any]:
        """Transpile and sample bound QAOA circuit on the specified processor."""
        if optimal_partitions is None:
            optimal_partitions = {(1, 1, 0, 1, 0, 0), (0, 0, 1, 0, 1, 1)}
            
        qc = construct_qaoa_circuit(
            self.weighted_edges,
            gamma=gamma,
            beta=beta,
            num_qubits=self.num_qubits,
            add_measurements=True,
        )
        
        # Check capacity
        if qc.num_qubits > processor["num_qubits"]:
            return {
                "processor": processor["name"],
                "noisy": noisy,
                "executable": False,
                "reason": f"needs {qc.num_qubits} qubits > {processor['num_qubits']}",
            }
            
        tqc = transpile_for(qc, processor)
        metrics = circuit_metrics(qc, processor)
        sim = simulator(noisy=noisy, processor=processor)
        counts = sim.run(tqc, shots=shots).result().get_counts()
        
        total_shots = sum(counts.values())
        total_cut_weight = 0.0
        best_cut_weight = 0
        optimal_shots = 0
        sampled_distribution: Dict[int, int] = {}
        
        for bitstring, count in counts.items():
            x = counts_to_x(bitstring)
            c = compute_cut_weight(x, self.weighted_edges)
            total_cut_weight += c * count
            sampled_distribution[c] = sampled_distribution.get(c, 0) + count
            if c > best_cut_weight:
                best_cut_weight = c
            if x in optimal_partitions:
                optimal_shots += count
                
        mean_cut = total_cut_weight / float(total_shots)
        approx_ratio = mean_cut / float(c_star)
        r_best = best_cut_weight / float(c_star)
        p_opt = optimal_shots / float(total_shots)
        
        return {
            "processor": processor["name"],
            "noisy": noisy,
            "executable": True,
            "shots": total_shots,
            "metrics": metrics,
            "mean_cut": mean_cut,
            "best_cut": best_cut_weight,
            "approx_ratio": approx_ratio,
            "r_best": r_best,
            "p_opt": p_opt,
            "optimal_shots": optimal_shots,
            "sampled_distribution": sampled_distribution,
            "counts": counts,
        }
