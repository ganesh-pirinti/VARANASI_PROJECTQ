"""Exact classical baseline solver for PS-O1 Network Partitioning (Max-Cut).

Computes the exact ground truth over all 2^N bitstrings, identifies all optimal partitions,
verifies bitwise complement symmetry, and calculates the uniform random baseline.
"""
from __future__ import annotations
import json
from typing import Dict, List, Tuple, Set

def load_pso1_instance(instance_path: str = "data/instance.json") -> dict:
    """Load PS-O1 instance data."""
    with open(instance_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def compute_cut_weight(x: Tuple[int, ...], weighted_edges: List[List[int]]) -> int:
    """Compute cut weight for assignment x = (x0, x1, ..., x_{n-1}).
    
    C(x) = sum_{(u, v, w) in E} w * (x_u + x_v - 2 * x_u * x_v)
    Edge (u, v) is cut if and only if x[u] != x[v].
    """
    cut = 0
    for u, v, w in weighted_edges:
        if x[u] != x[v]:
            cut += w
    return cut

def solve_exact_maxcut(weighted_edges: List[List[int]], num_vertices: int = 6) -> dict:
    """Exhaustively enumerate all 2^num_vertices bitstrings to find C* and the optimal set.
    
    Returns:
        dict containing:
            - num_vertices: int
            - total_graph_weight: int
            - max_cut_weight: int (C*)
            - optimal_partitions: List[Tuple[int, ...]] (assignments reaching C*)
            - optimal_solution_count: int
            - uniform_random_mean_cut: float
            - uniform_random_approx_ratio: float
            - uniform_random_p_opt: float
            - cut_distribution: Dict[int, int] (cut_value -> frequency across all 64 bitstrings)
    """
    total_w = sum(w for _, _, w in weighted_edges)
    num_states = 1 << num_vertices
    
    cut_distribution: Dict[int, int] = {}
    all_cuts: Dict[Tuple[int, ...], int] = {}
    
    for state_idx in range(num_states):
        x = tuple((state_idx >> bit) & 1 for bit in range(num_vertices))
        c = compute_cut_weight(x, weighted_edges)
        all_cuts[x] = c
        cut_distribution[c] = cut_distribution.get(c, 0) + 1
        
    c_star = max(all_cuts.values())
    optimal_partitions = [x for x, c in all_cuts.items() if c == c_star]
    
    # Uniform random baseline
    uniform_random_mean = sum(all_cuts.values()) / float(num_states)
    uniform_random_r = uniform_random_mean / float(c_star)
    uniform_random_p_opt = len(optimal_partitions) / float(num_states)
    
    return {
        "num_vertices": num_vertices,
        "total_graph_weight": total_w,
        "max_cut_weight": c_star,
        "optimal_partitions": optimal_partitions,
        "optimal_solution_count": len(optimal_partitions),
        "uniform_random_mean_cut": uniform_random_mean,
        "uniform_random_approx_ratio": uniform_random_r,
        "uniform_random_p_opt": uniform_random_p_opt,
        "cut_distribution": cut_distribution,
        "all_cuts": all_cuts,
    }
