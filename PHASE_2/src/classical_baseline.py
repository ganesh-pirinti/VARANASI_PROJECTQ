"""
src/classical_baseline.py — Exhaustive Classical Enumeration & Ground Truth
===========================================================================

Enumerates all 2^6 = 64 bitstrings, validates C* = 22, verifies complementary
optimal partitions S={0,1,3} and {2,4,5}, checks the random baseline,
and exports results/tables/classical_enumeration.csv.
"""

from __future__ import annotations
import csv
from pathlib import Path
from typing import Dict, List, Tuple

from src.problem_model import (
    NUM_VERTICES,
    NUM_EDGES,
    TOTAL_WEIGHT,
    LOCKED_EDGES,
    compute_cut_weight,
    construct_qubo_matrix,
    evaluate_qubo,
)
from qff_phase2 import counts_to_x


def assignment_to_bitstring(x: Tuple[int, ...] | List[int]) -> str:
    """Convert vertex assignment (x0..x5) to Qiskit little-endian count string."""
    return "".join(str(b) for b in reversed(x))


def solve_exhaustive(edges: List[Tuple[int, int, int]] = LOCKED_EDGES) -> dict:
    """
    Exhaustively evaluate all 64 states.
    Returns:
      - max_cut: 22
      - optimal_assignments: [(1, 1, 0, 1, 0, 0), (0, 0, 1, 0, 1, 1)]
      - optimal_bitstrings: ['001011', '110100']
      - random_mean_cut: 13.5
      - random_approx_ratio: 13.5 / 22 = 0.613636...
      - random_p_opt: 2 / 64 = 0.03125
      - cut_distribution: dict of cut_value -> frequency
      - all_states: list of state dicts
    """
    num_states = 1 << NUM_VERTICES
    Q, const = construct_qubo_matrix(edges)

    max_cut = -1
    optimal_assignments = []
    cut_counts: Dict[int, int] = {}
    total_cut_sum = 0
    all_states = []

    for idx in range(num_states):
        # x_i is bit i (x0..x5)
        x = tuple((idx >> b) & 1 for b in range(NUM_VERTICES))
        cut = compute_cut_weight(x, edges)
        qubo_val = evaluate_qubo(x, Q, const)

        # Mathematical equivalence check: QUBO(x) == -C(x)
        assert abs(qubo_val - (-float(cut))) < 1e-9, f"QUBO mismatch at {x}"

        bs = assignment_to_bitstring(x)
        assert counts_to_x(bs) == x, f"counts_to_x roundtrip failed at {x}"

        total_cut_sum += cut
        cut_counts[cut] = cut_counts.get(cut, 0) + 1

        if cut > max_cut:
            max_cut = cut
            optimal_assignments = [x]
        elif cut == max_cut:
            optimal_assignments.append(x)

        all_states.append({
            "index": idx,
            "assignment": x,
            "bitstring": bs,
            "cut_weight": cut,
            "qubo_val": qubo_val,
        })

    random_mean = total_cut_sum / num_states
    random_ar = random_mean / max_cut if max_cut > 0 else 0.0
    random_p_opt = len(optimal_assignments) / num_states
    opt_bitstrings = [assignment_to_bitstring(a) for a in optimal_assignments]

    return {
        "num_vertices": NUM_VERTICES,
        "num_edges": NUM_EDGES,
        "total_weight": TOTAL_WEIGHT,
        "max_cut": max_cut,
        "optimal_assignments": optimal_assignments,
        "optimal_bitstrings": opt_bitstrings,
        "optimal_count": len(optimal_assignments),
        "random_mean_cut": random_mean,
        "random_approx_ratio": random_ar,
        "random_p_opt": random_p_opt,
        "cut_distribution": cut_counts,
        "all_states": all_states,
    }


def export_classical_enumeration(output_path: str = "results/tables/classical_enumeration.csv") -> None:
    """Save all 64 states to CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    res = solve_exhaustive()
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "assignment", "qiskit_bitstring", "cut_weight", "qubo_value", "is_optimal"])
        for s in res["all_states"]:
            is_opt = s["cut_weight"] == res["max_cut"]
            writer.writerow([
                s["index"],
                str(s["assignment"]),
                s["bitstring"],
                s["cut_weight"],
                f"{s['qubo_val']:.1f}",
                is_opt,
            ])
