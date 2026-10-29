"""Classical Baselines and Exact Ground-Truth Enumeration for PS-O1.

Provides exhaustive 64-state Max-Cut enumeration, greedy heuristic baseline,
uniform random expectation baseline, and validation against the locked 6-vertex graph.
"""
from __future__ import annotations
from typing import List, Tuple, Dict, Any
import numpy as np

# Re-export from existing exact_solver for full backward compatibility
from src.exact_solver import compute_cut_weight, solve_exact_maxcut

def get_uniform_random_baseline(weighted_edges: List[List[int]], c_star: float = 22.0) -> Dict[str, float]:
    """Calculate the theoretical uniform random baseline for the locked graph.
    
    Total weight W = 27.
    Expected cut for any edge is w_ij / 2.
    Expected total cut = W / 2 = 13.5.
    Approximation ratio r_rand = 13.5 / 22 = 0.613636...
    Probability of sampling either optimal state = 2 / 2^6 = 2 / 64 = 0.03125 (3.125%).
    """
    total_w = sum(w for _, _, w in weighted_edges)
    exp_cut = total_w / 2.0
    r_rand = exp_cut / c_star
    p_opt_rand = 2.0 / 64.0
    return {
        "total_edge_weight": total_w,
        "expected_cut": exp_cut,
        "approximation_ratio": r_rand,
        "p_opt": p_opt_rand,
        "p_opt_pct": p_opt_rand * 100.0,
    }

def solve_greedy_heuristic(weighted_edges: List[List[int]], num_vertices: int = 6) -> Dict[str, Any]:
    """Simple deterministic greedy 2-partition heuristic for educational comparison.
    
    Places each vertex sequentially into partition S or not S to maximize partial cut.
    """
    partition = [0] * num_vertices
    # Fix vertex 0 in partition 0
    for v in range(1, num_vertices):
        # Score if v=0
        partition[v] = 0
        w0 = compute_cut_weight(partition, weighted_edges)
        # Score if v=1
        partition[v] = 1
        w1 = compute_cut_weight(partition, weighted_edges)
        if w0 > w1:
            partition[v] = 0
        else:
            partition[v] = 1
            
    cut_w = compute_cut_weight(partition, weighted_edges)
    return {
        "partition": partition,
        "bitstring": "".join(str(b) for b in partition),
        "cut_weight": cut_w,
        "approximation_ratio": cut_w / 22.0,
    }

if __name__ == "__main__":
    # Self-test
    edges = [[0, 2, 1], [0, 3, 4], [0, 4, 4], [1, 4, 3], [1, 5, 3], [2, 3, 5], [2, 4, 1], [3, 4, 4], [3, 5, 2]]
    gt = solve_exact_maxcut(edges, 6)
    print(f"Classical Ground Truth: C* = {gt['max_cut_weight']}, Optima = {gt['optimal_partitions']}")
    rand = get_uniform_random_baseline(edges, gt['max_cut_weight'])
    print(f"Random Baseline: E[C] = {rand['expected_cut']}, r = {rand['approximation_ratio']:.4f}, P_opt = {rand['p_opt_pct']:.2f}%")
    greedy = solve_greedy_heuristic(edges, 6)
    print(f"Greedy Baseline: C = {greedy['cut_weight']}, r = {greedy['approximation_ratio']:.4f}")
