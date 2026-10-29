"""
QAOA circuit generation, classical parameter optimization, and evaluation.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
import time


def build_qaoa_circuit(
    edges: List[Dict[str, Any]],
    num_nodes: int,
    gamma: List[float],
    beta: List[float],
    p: int = 1,
    measure: bool = False
) -> QuantumCircuit:
    """
    Construct a p-layer QAOA circuit for Max-Cut.
    
    Ansatz:
      |psi(gamma, beta)> = prod_{k=1}^p [ U(M, beta_k) U(C, gamma_k) ] |+>^n
    where:
      U(C, gamma) applies RZZ(2 * gamma * weight) for each graph edge.
      U(M, beta) applies RX(2 * beta) for each vertex.
    """
    qc = QuantumCircuit(num_nodes)
    
    # Initial state: Uniform superposition
    qc.h(range(num_nodes))
    qc.barrier()
    
    for layer in range(p):
        g = gamma[layer]
        b = beta[layer]
        
        # Phase separation (Cost unitary)
        for edge in edges:
            u = edge["source"]
            v = edge["target"]
            w = edge["weight"]
            # RZZ(theta) = exp(-i * theta/2 * Z \otimes Z)
            # Setting theta = 2 * g * w
            qc.rzz(2 * g * w, u, v)
        qc.barrier()
        
        # Mixer unitary
        for u in range(num_nodes):
            qc.rx(2 * b, u)
        qc.barrier()
        
    if measure:
        qc.measure_all()
        
    return qc


def compute_expected_cut_from_statevector(
    circuit: QuantumCircuit,
    edges: List[Dict[str, Any]],
    num_nodes: int
) -> Tuple[float, Dict[str, float]]:
    """
    Compute the exact expectation value of the cut function from the circuit statevector:
      <C> = sum_{x} P(x) * C(x)
    """
    # Remove measurements if any for statevector simulation
    circ_no_meas = circuit.remove_final_measurements(inplace=False) if circuit.cregs else circuit
    sv = Statevector.from_instruction(circ_no_meas)
    probs_dict = sv.probabilities_dict()
    
    expected_cut = 0.0
    bitstring_probs = {}
    
    for bstr_little_endian, prob in probs_dict.items():
        # Qiskit bitstring order: qubit 0 is the rightmost character
        # Convert to normal node-indexed string: index 0 is node 0
        normal_bstr = bstr_little_endian[::-1]
        bitstring_probs[normal_bstr] = prob
        
        # Calculate cut for this bitstring
        cut = 0.0
        for edge in edges:
            u = edge["source"]
            v = edge["target"]
            w = edge["weight"]
            if normal_bstr[u] != normal_bstr[v]:
                cut += w
        expected_cut += prob * cut
        
    return expected_cut, bitstring_probs


def optimize_qaoa(
    edges: List[Dict[str, Any]],
    num_nodes: int,
    p: int = 1,
    initial_params: Optional[List[float]] = None,
    maxiter: int = 100,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Optimize QAOA variational parameters (gamma, beta) using COBYLA.
    Maximizes the expected cut value.
    """
    np.random.seed(seed)
    if initial_params is None:
        # Standard initial heuristic angles: gamma ~ 0.5, beta ~ 0.5
        initial_params = [0.5] * p + [0.5] * p
        
    eval_history = []
    
    def objective_fn(params):
        gamma = params[:p]
        beta = params[p:]
        circ = build_qaoa_circuit(edges, num_nodes, gamma, beta, p=p, measure=False)
        exp_cut, _ = compute_expected_cut_from_statevector(circ, edges, num_nodes)
        eval_history.append(exp_cut)
        # Minimize negative expected cut to maximize cut
        return -exp_cut

    start_time = time.time()
    res = minimize(
        objective_fn,
        initial_params,
        method="COBYLA",
        options={"maxiter": maxiter, "disp": False}
    )
    opt_time = time.time() - start_time
    
    opt_gamma = res.x[:p].tolist()
    opt_beta = res.x[p:].tolist()
    opt_cut = -float(res.fun)
    
    # Build optimal circuit
    opt_circuit = build_qaoa_circuit(edges, num_nodes, opt_gamma, opt_beta, p=p, measure=False)
    _, bitstring_probs = compute_expected_cut_from_statevector(opt_circuit, edges, num_nodes)
    
    return {
        "p": p,
        "optimal_gamma": opt_gamma,
        "optimal_beta": opt_beta,
        "expected_cut": opt_cut,
        "optimization_time_sec": opt_time,
        "num_evaluations": len(eval_history),
        "history": eval_history,
        "optimal_circuit": opt_circuit,
        "bitstring_probs": bitstring_probs
    }


def sample_qaoa_shots(
    circuit: QuantumCircuit,
    shots: int = 4096,
    seed: int = 42
) -> Dict[str, int]:
    """
    Run shot-based sampling using AerSimulator.
    Returns counts dictionary with node-0-indexed bitstrings.
    """
    meas_circ = circuit.copy()
    if not meas_circ.cregs:
        meas_circ.measure_all()
        
    sim = AerSimulator()
    job = sim.run(meas_circ, shots=shots, seed_simulator=seed)
    result = job.result()
    counts = result.get_counts()
    
    # Reverse bitstrings to node-order (index 0 is node 0)
    reordered_counts = {k[::-1]: v for k, v in counts.items()}
    return reordered_counts
