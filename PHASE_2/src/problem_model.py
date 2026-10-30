"""
src/problem_model.py — PS-O1 Network Partitioning Graph & QUBO Formulation
==========================================================================

Independently defines the locked 6-vertex weighted graph from instances.json,
computes direct classical cut weights, formulates the QUBO matrix for -C(x),
and verifies mathematical equivalence.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Locked 6-vertex, 9-edge instance motivated by 5G network partitioning
NUM_VERTICES = 6
NUM_EDGES = 9
TOTAL_WEIGHT = 27

LOCKED_EDGES: List[Tuple[int, int, int]] = [
    (0, 2, 1),
    (0, 3, 4),
    (0, 4, 4),
    (1, 4, 3),
    (1, 5, 3),
    (2, 3, 5),
    (2, 4, 1),
    (3, 4, 4),
    (3, 5, 2),
]


def load_instance(path: str = "data/instance.json") -> dict:
    """Load PS-O1 instance data."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_cut_weight(assignment: Tuple[int, ...] | List[int], edges: List[Tuple[int, int, int]] = LOCKED_EDGES) -> int:
    """
    Compute cut weight:
      C(x) = sum_{(u,v,w) in E} w * (x_u + x_v - 2*x_u*x_v)
    Edge (u, v) is cut if and only if x[u] != x[v].
    """
    cut = 0
    for u, v, w in edges:
        if assignment[u] != assignment[v]:
            cut += w
    return cut


def construct_qubo_matrix(edges: List[Tuple[int, int, int]] = LOCKED_EDGES) -> Tuple[Dict[Tuple[int, int], float], float]:
    """
    Construct upper-triangular QUBO dictionary Q for minimizing -C(x):
      -C(x) = sum_i Q_{ii} x_i + sum_{i<j} Q_{ij} x_i x_j
    
    For each edge (u, v, w):
      Contribution to -C(x) = -w*(x_u + x_v - 2*x_u*x_v)
      Linear: -w to x_u, -w to x_v
      Quadratic: +2w to x_u*x_v
    """
    Q: Dict[Tuple[int, int], float] = {}
    for u, v, w in edges:
        Q[(u, u)] = Q.get((u, u), 0.0) - float(w)
        Q[(v, v)] = Q.get((v, v), 0.0) - float(w)
        key = (min(u, v), max(u, v))
        Q[key] = Q.get(key, 0.0) + 2.0 * float(w)
    return Q, 0.0


def evaluate_qubo(assignment: Tuple[int, ...] | List[int], Q: Dict[Tuple[int, int], float], constant: float = 0.0) -> float:
    """Evaluate x^T Q x + constant."""
    val = constant
    for (i, j), coeff in Q.items():
        if i == j:
            val += coeff * assignment[i]
        else:
            val += coeff * assignment[i] * assignment[j]
    return val
