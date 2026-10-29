"""Standardized Quantum and Classical Metrics for PS-O1.

Implements official definitions from QFF 2026 Optimization Challenge Kit:
- Section 3: Official circuit resource metrics (logical CX, physical CX, depth, two-qubit depth, SWAPs, CX overhead).
- Section 4: Bell state expectation values, fidelity equation, and propagated standard errors.
- Section 9: Quality metrics (approximation ratio, best-sampled ratio, P_opt).
- Section 11: Official scoring rubric diagnostic formula calculator.
"""
from __future__ import annotations
import math
from typing import Dict, Any, List, Tuple
import numpy as np
from qff_phase2 import circuit_metrics, counts_to_x
from src.exact_solver import compute_cut_weight

def compute_histogram_metrics(
    counts: Dict[str, int],
    weighted_edges: List[List[int]],
    c_star: float = 22.0,
    optimal_assignments: List[Tuple[int, ...]] = None,
) -> Dict[str, Any]:
    """Compute all required quality metrics from a raw measurement histogram."""
    if optimal_assignments is None:
        optimal_assignments = [(1, 1, 0, 1, 0, 0), (0, 0, 1, 0, 1, 1)]
        
    total_shots = sum(counts.values())
    if total_shots == 0:
        raise ValueError("Cannot compute metrics from empty counts dictionary.")
        
    cut_counts = {}
    total_weighted_cut = 0.0
    max_cut_sampled = 0
    optimal_shots = 0
    
    per_bitstring_records = []
    
    for key, count in counts.items():
        x = counts_to_x(key)
        cut = compute_cut_weight(list(x), weighted_edges)
        total_weighted_cut += cut * count
        cut_counts[cut] = cut_counts.get(cut, 0) + count
        
        if cut > max_cut_sampled:
            max_cut_sampled = cut
            
        is_opt = (x in optimal_assignments)
        if is_opt:
            optimal_shots += count
            
        per_bitstring_records.append({
            "key": key,
            "x": list(x),
            "cut": cut,
            "count": count,
            "probability": count / total_shots,
            "is_optimal": is_opt,
        })
        
    mean_cut = total_weighted_cut / total_shots
    approx_ratio = mean_cut / c_star
    best_approx_ratio = max_cut_sampled / c_star
    p_opt = optimal_shots / total_shots
    
    # Compute standard error of the mean cut
    variance = sum(((rec["cut"] - mean_cut) ** 2) * rec["count"] for rec in per_bitstring_records) / total_shots
    std_dev_cut = math.sqrt(variance)
    std_err_approx_ratio = (std_dev_cut / math.sqrt(total_shots)) / c_star
    
    return {
        "shots": total_shots,
        "mean_cut": mean_cut,
        "std_dev_cut": std_dev_cut,
        "approx_ratio": approx_ratio,
        "std_err_approx_ratio": std_err_approx_ratio,
        "max_cut_sampled": max_cut_sampled,
        "best_approx_ratio": best_approx_ratio,
        "optimal_shots": optimal_shots,
        "p_opt": p_opt,
        "p_opt_pct": p_opt * 100.0,
        "cut_distribution": cut_counts,
        "bitstrings": per_bitstring_records,
    }

def calculate_bell_fidelity(
    exp_xx: float,
    exp_yy: float,
    exp_zz: float,
    se_xx: float,
    se_yy: float,
    se_zz: float,
) -> Tuple[float, float]:
    """Calculate Bell state fidelity and uncertainty via official formula.
    
    Target: |Phi+> = (|00> + |11>) / sqrt(2)
    F = (1 + <XX> - <YY> + <ZZ>) / 4
    SE(F) = 1/4 * sqrt(SE_XX^2 + SE_YY^2 + SE_ZZ^2)
    """
    fidelity = (1.0 + exp_xx - exp_yy + exp_zz) / 4.0
    se_fidelity = 0.25 * math.sqrt(se_xx**2 + se_yy**2 + se_zz**2)
    return fidelity, se_fidelity

def calculate_official_score_diagnostic(
    noisy_approx_ratio: float,
    noisy_p_opt: float,
    # Official PS-O1 reference values
    r_rand: float = 0.614,
    r_ref: float = 0.785,
    p_rand: float = 0.031,
    p_ref: float = 0.123,
) -> Dict[str, Any]:
    """Calculate diagnostic objective formula points per Section 11 of Challenge Kit.
    
    s(x) = clip((x - x_rand) / (x_ref - x_rand), 0, 1)
    Quality points = 15 * [0.5 * s(r) + 0.5 * s(P_opt)]
    """
    s_r = max(0.0, min(1.0, (noisy_approx_ratio - r_rand) / (r_ref - r_rand)))
    s_p = max(0.0, min(1.0, (noisy_p_opt - p_rand) / (p_ref - p_rand)))
    quality_fraction = 0.5 * s_r + 0.5 * s_p
    quality_points = 15.0 * quality_fraction
    return {
        "s_r": s_r,
        "s_p_opt": s_p,
        "quality_fraction": quality_fraction,
        "quality_points": quality_points,
        "max_quality_points": 15.0,
    }
