"""
Graph utilities and classical Max-Cut baseline algorithms.
"""

import json
from typing import Dict, List, Tuple, Any
import numpy as np


def load_graph_data(filepath: str) -> Dict[str, Any]:
    """Load benchmark graph specification from JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def compute_cut_value(bitstring: str, edges: List[Dict[str, Any]]) -> float:
    """
    Compute cut value for a binary partition bitstring.
    Bitstring index convention: node i corresponds to bitstring[i].
    """
    cut = 0.0
    for edge in edges:
        u = edge["source"]
        v = edge["target"]
        w = edge["weight"]
        if bitstring[u] != bitstring[v]:
            cut += w
    return cut


def classical_exact_max_cut(edges: List[Dict[str, Any]], num_nodes: int) -> Dict[str, Any]:
    """
    Exhaustively evaluate all 2^N configurations to determine the global optimum.
    Returns optimal cut value, optimal partitions, and distribution over all cuts.
    """
    total_states = 1 << num_nodes
    max_cut_val = -float("inf")
    optimal_bitstrings = []
    cut_distribution: Dict[float, int] = {}

    for i in range(total_states):
        # Format as binary string of length num_nodes
        bstr = format(i, f"0{num_nodes}b")
        val = compute_cut_value(bstr, edges)
        cut_distribution[val] = cut_distribution.get(val, 0) + 1

        if val > max_cut_val:
            max_cut_val = val
            optimal_bitstrings = [bstr]
        elif np.isclose(val, max_cut_val):
            optimal_bitstrings.append(bstr)

    total_weight = sum(e["weight"] for e in edges)
    random_expectation = 0.5 * total_weight

    return {
        "max_cut_value": max_cut_val,
        "optimal_bitstrings": optimal_bitstrings,
        "total_weight": total_weight,
        "random_baseline_expectation": random_expectation,
        "cut_distribution": cut_distribution,
        "num_evaluated_states": total_states
    }
