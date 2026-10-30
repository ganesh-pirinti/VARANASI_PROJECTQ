"""
src/benchmarking.py — Cross-Processor QAOA Benchmarking Engine
==============================================================

Executes multi-restart parameter optimization across seeds [0, 1, 2, 3, 4],
evaluates circuit metrics on Processors A, B, and D, samples 4096 shots under ideal
and official noisy simulation, and exports:
  - results/tables/results.csv (Official Section 9 Schema)
  - results/tables/optimization_runs.csv
  - results/tables/processor_metrics.csv
  - results/raw/qaoa_counts.json
"""

from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

from qff_phase2 import (
    PROCESSOR_A,
    PROCESSOR_B,
    load_processor,
    circuit_metrics,
    transpile_for,
    simulator,
    counts_to_x,
    SHOTS,
)
from src.problem_model import LOCKED_EDGES, compute_cut_weight
from src.classical_baseline import solve_exhaustive
from src.qaoa_solver import build_qaoa_circuit, QAOASolver


def run_benchmarks(
    processor_d_path: str = "processors/processor_D.json",
    results_csv_path: str = "results/tables/results.csv",
    opt_runs_csv_path: str = "results/tables/optimization_runs.csv",
    proc_metrics_csv_path: str = "results/tables/processor_metrics.csv",
    raw_counts_path: str = "results/raw/qaoa_counts.json",
) -> Dict[str, Any]:
    """Execute complete benchmarking workflow across A, B, and D."""
    Path(results_csv_path).parent.mkdir(parents=True, exist_ok=True)
    Path(raw_counts_path).parent.mkdir(parents=True, exist_ok=True)

    # 1. Classical ground truth
    classical = solve_exhaustive()
    c_star = classical["max_cut"]
    r_rand = classical["random_approx_ratio"]
    opt_set = set(classical["optimal_assignments"])

    # 2. Multi-start QAOA parameter optimization
    solver = QAOASolver(edges=LOCKED_EDGES, num_qubits=6)
    opt_results = solver.optimize_multi_start(seeds=[0, 1, 2, 3, 4], maxiter=80, c_star=float(c_star))
    best_run = opt_results["best_run"]
    opt_gamma = best_run["optimized_gamma"]
    opt_beta = best_run["optimized_beta"]

    # Export optimization runs table
    with open(opt_runs_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["seed", "initial_gamma", "initial_beta", "final_gamma", "final_beta", "cost_expectation", "approx_ratio", "iterations", "success"])
        for r in opt_results["seed_results"]:
            writer.writerow([
                r["seed"],
                f"{r['initial_gamma'][0]:.6f}",
                f"{r['initial_beta'][0]:.6f}",
                f"{r['optimized_gamma'][0]:.6f}",
                f"{r['optimized_beta'][0]:.6f}",
                f"{r['expected_cut']:.6f}",
                f"{r['approx_ratio']:.6f}",
                r["iterations"],
                r["optimizer_success"],
            ])

    # 3. Construct optimal QAOA circuit
    qc = build_qaoa_circuit(opt_gamma, opt_beta, LOCKED_EDGES, 6, measure=True)

    # Load processor configurations
    proc_d = load_processor(processor_d_path)
    procs = [
        ("A", PROCESSOR_A),
        ("B", PROCESSOR_B),
        ("D", proc_d),
    ]

    metrics = {}
    for pid, p in procs:
        metrics[pid] = circuit_metrics(qc, p)

    # Export processor metrics table
    with open(proc_metrics_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["processor", "executable", "logical_qubits", "physical_qubits", "logical_cx", "cx", "depth", "two_q_depth", "swaps", "cx_overhead", "reason"])
        for pid, m in metrics.items():
            if not m.get("executable", True):
                writer.writerow([pid, False, 6, m.get("physical_qubits", 5), "", "", "", "", "", "", m.get("reason", "")])
            else:
                writer.writerow([pid, True, m["logical_qubits"], m["physical_qubits"], m["logical_cx"], m["cx"], m["depth"], m["two_q_depth"], m["swaps"], m["cx_overhead"], ""])

    # 4. Sampling execution
    results_rows = []
    raw_counts = {}

    for pid, p in procs:
        m = metrics[pid]
        if not m.get("executable", True):
            for cond in ["ideal", "noisy"]:
                results_rows.append({
                    "problem_id": "PS-O1",
                    "processor": pid,
                    "condition": cond,
                    "executable": "false",
                    "logical_qubits": 6,
                    "physical_qubits": p["num_qubits"],
                    "logical_cx": "",
                    "cx": "",
                    "depth": "",
                    "two_q_depth": "",
                    "swaps": "",
                    "cx_overhead": "",
                    "shots": "",
                    "quality_metric": "approx_ratio",
                    "quality_value": "",
                    "p_opt": "",
                    "classical_optimum": c_star,
                    "random_baseline": f"{r_rand:.4f}",
                })
            continue

        tqc = transpile_for(qc, p)
        for cond, noisy in [("ideal", False), ("noisy", True)]:
            sim = simulator(noisy=noisy, processor=p)
            counts = sim.run(tqc, shots=SHOTS).result().get_counts()
            raw_counts[f"{pid}_{cond}"] = counts

            total_score = 0.0
            opt_shots = 0
            for k, cnt in counts.items():
                x = counts_to_x(k)
                score = compute_cut_weight(x, LOCKED_EDGES)
                total_score += score * cnt
                if x in opt_set:
                    opt_shots += cnt

            mean_score = total_score / SHOTS
            ar = mean_score / c_star
            p_opt = opt_shots / SHOTS

            results_rows.append({
                "problem_id": "PS-O1",
                "processor": pid,
                "condition": cond,
                "executable": "true",
                "logical_qubits": 6,
                "physical_qubits": p["num_qubits"],
                "logical_cx": m["logical_cx"],
                "cx": m["cx"],
                "depth": m["depth"],
                "two_q_depth": m["two_q_depth"],
                "swaps": m["swaps"],
                "cx_overhead": m["cx_overhead"],
                "shots": SHOTS,
                "quality_metric": "approx_ratio",
                "quality_value": f"{ar:.4f}",
                "p_opt": f"{p_opt:.4f}",
                "classical_optimum": c_star,
                "random_baseline": f"{r_rand:.4f}",
            })

    # Export results.csv (Official Contract Schema)
    with open(results_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "problem_id", "processor", "condition", "executable",
            "logical_qubits", "physical_qubits", "logical_cx", "cx",
            "depth", "two_q_depth", "swaps", "cx_overhead", "shots",
            "quality_metric", "quality_value", "p_opt", "classical_optimum",
            "random_baseline",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results_rows:
            writer.writerow(row)

    # Save raw histograms
    with open(raw_counts_path, "w", encoding="utf-8") as f:
        json.dump(raw_counts, f, indent=2)

    return {
        "results_rows": results_rows,
        "metrics": metrics,
        "opt_results": opt_results,
        "raw_counts": raw_counts,
    }
