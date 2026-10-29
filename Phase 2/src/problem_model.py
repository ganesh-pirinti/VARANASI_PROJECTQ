"""Mathematical Model, QUBO Formulation, and Ising Cost Hamiltonian for PS-O1.

Problem Statement: PS-O1 — Quantum Optimization of Network Partitioning Using QAOA
Team: VARANASI

Mathematical Formulation:
Binary variables x_i in {0, 1} assign each vertex i to partition group S (x_i=1) or S_bar (x_i=0).
For edge (i, j) with weight w_ij, the cut contribution is:
  cut(i, j) = w_ij * (x_i + x_j - 2*x_i*x_j)
  
Total cut objective to MAXIMIZE:
  C(x) = sum_{(i,j) in E} w_ij * (x_i + x_j - 2*x_i*x_j)

QUBO formulation to MINIMIZE:
  min_x  -C(x) = x^T Q x
  
Ising spin mapping (x_i = (I - Z_i)/2):
  x_i + x_j - 2*x_i*x_j = 1/2 * (I - Z_i*Z_j)

Cost Hamiltonian:
  H_C = sum_{(i,j) in E} (w_ij / 2) * (I - Z_i*Z_j)
  
Since constant identity shifts do not affect the eigenstate ordering:
  H_C_diag = - sum_{(i,j) in E} (w_ij / 2) * Z_i*Z_j   (up to energy offset sum w_ij/2 = 13.5)
"""
from __future__ import annotations
import json
from typing import List, Tuple, Dict, Any
import numpy as np

# Locked PS-O1 instance constants
LOCKED_VERTICES = 6
LOCKED_EDGES = [
    [0, 2, 1],
    [0, 3, 4],
    [0, 4, 4],
    [1, 4, 3],
    [1, 5, 3],
    [2, 3, 5],
    [2, 4, 1],
    [3, 4, 4],
    [3, 5, 2],
]
LOCKED_TOTAL_WEIGHT = 27
LOCKED_MAX_CUT = 22

class NetworkPartitionModel:
    """Rigorous mathematical formulation and validation for PS-O1."""
    
    def __init__(self, weighted_edges: List[List[int]] = None, num_vertices: int = LOCKED_VERTICES):
        self.num_vertices = num_vertices
        self.weighted_edges = weighted_edges if weighted_edges is not None else LOCKED_EDGES
        self.total_weight = sum(w for _, _, w in self.weighted_edges)
        self.adjacency_matrix = self._build_adjacency_matrix()
        self.qubo_matrix = self._build_qubo_matrix()
        
    def _build_adjacency_matrix(self) -> np.ndarray:
        adj = np.zeros((self.num_vertices, self.num_vertices), dtype=int)
        for u, v, w in self.weighted_edges:
            adj[u, v] = w
            adj[v, u] = w
        return adj
        
    def _build_qubo_matrix(self) -> np.ndarray:
        """Build the n x n upper-triangular QUBO matrix Q such that min x^T Q x = min -C(x).
        
        -C(x) = sum_{(i,j)} -w_ij*(x_i + x_j - 2*x_i*x_j)
              = sum_{(i,j)} [-w_ij*x_i - w_ij*x_j + 2*w_ij*x_i*x_j]
              
        Diagonal terms: Q_ii = - deg_w(i) = - sum_{j: (i,j) in E} w_ij
        Off-diagonal terms (i < j): Q_ij = 2 * w_ij
        """
        Q = np.zeros((self.num_vertices, self.num_vertices), dtype=float)
        # Degree sum for diagonal
        for u, v, w in self.weighted_edges:
            Q[u, u] -= w
            Q[v, v] -= w
            if u < v:
                Q[u, v] += 2.0 * w
            else:
                Q[v, u] += 2.0 * w
        return Q

    def evaluate_cut(self, partition: List[int] | Tuple[int, ...]) -> int:
        """Evaluate cut weight for a given partition vector x in {0, 1}^n."""
        cut_w = 0
        for u, v, w in self.weighted_edges:
            if partition[u] != partition[v]:
                cut_w += w
        return cut_w

    def evaluate_qubo_energy(self, partition: List[int] | Tuple[int, ...]) -> float:
        """Evaluate x^T Q x, which equals -C(x)."""
        x = np.array(partition, dtype=float)
        return float(x.T @ self.qubo_matrix @ x)

    def get_hamiltonian_terms(self) -> List[Dict[str, Any]]:
        """Return human-readable term-by-term Pauli cost Hamiltonian components."""
        terms = []
        for u, v, w in self.weighted_edges:
            terms.append({
                "edge": [u, v],
                "weight": w,
                "pauli_term": f"Z_{u} * Z_{v}",
                "coefficient": -float(w) / 2.0,
                "constant_offset": float(w) / 2.0,
            })
        return terms

    def to_dict(self) -> Dict[str, Any]:
        """Export comprehensive model metadata."""
        return {
            "num_vertices": self.num_vertices,
            "weighted_edges": self.weighted_edges,
            "total_weight": self.total_weight,
            "max_cut_theoretical": LOCKED_MAX_CUT,
            "qubo_matrix": self.qubo_matrix.tolist(),
            "adjacency_matrix": self.adjacency_matrix.tolist(),
            "hamiltonian_terms": self.get_hamiltonian_terms(),
        }

if __name__ == "__main__":
    model = NetworkPartitionModel()
    print("QUBO Matrix Q:")
    print(model.qubo_matrix)
    print("\nSample optimal cut (1, 1, 0, 1, 0, 0):")
    p = [1, 1, 0, 1, 0, 0]
    cut = model.evaluate_cut(p)
    qubo_e = model.evaluate_qubo_energy(p)
    print(f"Cut weight: {cut}, QUBO energy: {qubo_e} (Check: cut == -energy: {cut == -qubo_e})")
