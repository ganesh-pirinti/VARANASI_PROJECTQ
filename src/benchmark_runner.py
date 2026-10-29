"""End-to-End Benchmark Runner for VARANASI Phase 2 PS-O1.

Executes all official benchmark runs:
1. Exact classical solver to compute C* and random baseline
2. Parameter optimization over initialization seeds [0, 1, 2, 3, 4]
3. Sampling on Processor A (not executable), Processor B (ideal, noisy), and Processor D (ideal, noisy)
4. Exports results to results/tables/results.csv in the strict Section 9 format
5. Executes Bell state verification and exports to results/tables/bell.csv
6. Generates all visualization figures in results/figures/
"""
from __future__ import annotations
import csv
import json
import os
from typing import Dict, Any, List

from qff_phase2 import (
    PROCESSOR_A,
    PROCESSOR_B,
    load_processor,
    SHOTS,
)
from src.exact_solver import load_pso1_instance, solve_exact_maxcut
from src.qaoa_solver import QAOASolver
from src.bell_evaluator import run_bell_verification
from src.visualizations import (
    plot_network_partitioning_graph,
    plot_processor_topologies,
    plot_bell_fidelity_comparison,
    plot_qaoa_cut_distribution,
    plot_processor_resource_comparison,
)

def run_all_benchmarks(
    instance_path: str = "data/instance.json",
    processor_d_path: str = "processors/processor_D.json",
    results_csv_path: str = "results/tables/results.csv",
    bell_csv_path: str = "results/tables/bell.csv",
) -> Dict[str, Any]:
    """Run full benchmark pipeline and produce all deliverables."""
    os.makedirs(os.path.dirname(results_csv_path), exist_ok=True)
    os.makedirs(os.path.dirname(bell_csv_path), exist_ok=True)
    
    # 1. Load instance and solve exact baseline
    inst = load_pso1_instance(instance_path)
    weighted_edges = inst["weighted_edges"]
    num_vertices = inst["num_vertices"]
    init_seeds = inst["initialization_seeds"]
    
    exact_res = solve_exact_maxcut(weighted_edges, num_vertices)
    c_star = exact_res["max_cut_weight"]
    r_random = exact_res["uniform_random_approx_ratio"]
    opt_partitions_set = set(exact_res["optimal_partitions"])
    
    # 2. Optimize QAOA parameters across 5 seeds
    solver = QAOASolver(weighted_edges, num_vertices)
    opt_summary = solver.optimize_parameters(seeds=init_seeds, p=1, c_star=c_star)
    best_gamma = opt_summary["best_gamma"]
    best_beta = opt_summary["best_beta"]
    
    # 3. Load Processors
    proc_d = load_processor(processor_d_path)
    
    # 4. Benchmark Processors A, B, D under Ideal and Noisy
    results_rows: List[Dict[str, Any]] = []
    
    # Processor A: Capacity limit exceeded (5 qubits < 6 required)
    for cond in ("ideal", "noisy"):
        results_rows.append({
            "problem_id": "PS-O1",
            "processor": "A",
            "condition": cond,
            "executable": "false",
            "logical_qubits": num_vertices,
            "physical_qubits": PROCESSOR_A["num_qubits"],
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
            "random_baseline": f"{r_random:.4f}",
        })
        
    sampled_runs = {}
    for p_obj, p_name in [(PROCESSOR_B, "B"), (proc_d, "D")]:
        sampled_runs[p_name] = {}
        for noisy, cond in [(False, "ideal"), (True, "noisy")]:
            run_res = solver.sample_processor(
                processor=p_obj,
                gamma=best_gamma,
                beta=best_beta,
                noisy=noisy,
                shots=SHOTS,
                c_star=c_star,
                optimal_partitions=opt_partitions_set,
            )
            sampled_runs[p_name][cond] = run_res
            m = run_res["metrics"]
            results_rows.append({
                "problem_id": "PS-O1",
                "processor": p_name,
                "condition": cond,
                "executable": "true",
                "logical_qubits": m["logical_qubits"],
                "physical_qubits": m["physical_qubits"],
                "logical_cx": m["logical_cx"],
                "cx": m["cx"],
                "depth": m["depth"],
                "two_q_depth": m["two_q_depth"],
                "swaps": m["swaps"],
                "cx_overhead": m["cx_overhead"],
                "shots": run_res["shots"],
                "quality_metric": "approx_ratio",
                "quality_value": f"{run_res['approx_ratio']:.4f}",
                "p_opt": f"{run_res['p_opt']:.4f}",
                "classical_optimum": c_star,
                "random_baseline": f"{r_random:.4f}",
            })
            
    # Write results.csv
    fieldnames = [
        "problem_id",
        "processor",
        "condition",
        "executable",
        "logical_qubits",
        "physical_qubits",
        "logical_cx",
        "cx",
        "depth",
        "two_q_depth",
        "swaps",
        "cx_overhead",
        "shots",
        "quality_metric",
        "quality_value",
        "p_opt",
        "classical_optimum",
        "random_baseline",
    ]
    with open(results_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results_rows:
            writer.writerow(r)
            
    # 5. Run Bell verification
    bell_rows = run_bell_verification(
        processor_path=processor_d_path,
        near_pair=(0, 2),
        output_csv_path=bell_csv_path,
    )
    
    # 6. Generate visualizations
    best_partition = exact_res["optimal_partitions"][0]
    plot_network_partitioning_graph(weighted_edges, best_partition)
    plot_processor_topologies(PROCESSOR_A, PROCESSOR_B, proc_d)
    plot_bell_fidelity_comparison(bell_rows)
    plot_qaoa_cut_distribution(
        sampled_runs["B"]["noisy"]["sampled_distribution"],
        sampled_runs["D"]["noisy"]["sampled_distribution"],
        exact_res["cut_distribution"],
    )
    plot_processor_resource_comparison(
        {"cx": 0, "depth": 0, "two_q_depth": 0, "swaps": 0},
        sampled_runs["B"]["ideal"]["metrics"],
        sampled_runs["D"]["ideal"]["metrics"],
    )
    
    return {
        "exact_results": exact_res,
        "optimization_summary": opt_summary,
        "results_rows": results_rows,
        "bell_rows": bell_rows,
        "sampled_runs": sampled_runs,
    }
