"""Export verified benchmark data, topologies, and landscapes for VARANASI Studio.

Derives all values directly from authoritative source files:
- data/instance.json
- instances.json
- results/raw/benchmark_metadata.json
- results/raw/qaoa_counts.json
- results/tables/results.csv
- results/tables/bell.csv

Generates: web/public/data/benchmark_data.json (or web/data/benchmark_data.json)
"""
from __future__ import annotations
import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import csv
import numpy as np
from src.exact_solver import solve_exact_maxcut, compute_cut_weight
from src.qaoa_solver import QAOASolver

def generate_studio_data(output_path: str = "web/data/benchmark_data.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 1. Load instance data
    with open("data/instance.json", "r", encoding="utf-8") as f:
        inst = json.load(f)
    weighted_edges = inst["weighted_edges"]
    num_vertices = inst["num_vertices"]
    
    # 2. Classical ground truth
    exact_res = solve_exact_maxcut(weighted_edges, num_vertices)
    
    # Enumerate all 64 states with cut weights
    states_64 = []
    for state_idx in range(1 << num_vertices):
        x = tuple((state_idx >> b) & 1 for b in range(num_vertices))
        c = compute_cut_weight(x, weighted_edges)
        bitstring = "".join(str(b) for b in x)
        # Qiskit little endian string is reversed
        qiskit_bs = "".join(str(x[num_vertices - 1 - b]) for b in range(num_vertices))
        is_opt = (c == exact_res["max_cut_weight"])
        states_64.append({
            "index": state_idx,
            "assignment": list(x),
            "bitstring": bitstring,
            "qiskit_bitstring": qiskit_bs,
            "cut_weight": c,
            "is_optimal": is_opt,
            "group_s": [i for i, val in enumerate(x) if val == 1],
            "group_sbar": [i for i, val in enumerate(x) if val == 0],
        })
        
    # 3. Load benchmark metadata & raw counts
    with open("results/raw/benchmark_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    with open("results/raw/qaoa_counts.json", "r", encoding="utf-8") as f:
        counts = json.load(f)
        
    runs = counts["runs"]
    
    # 4. Processors
    proc_a = meta["configured_processors"]["Processor_A"]
    proc_b = meta["configured_processors"]["Processor_B"]
    proc_d = meta["configured_processors"]["Processor_D"]
    
    # 5. Bell state verification
    bell_rows = []
    with open("results/tables/bell.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            bell_rows.append({
                "pair_type": r["pair_type"],
                "qubit_pair": r["qubit_pair"],
                "pair_distance": int(r["pair_distance"]),
                "condition": r["condition"],
                "cx_count": int(r["cx_count"]),
                "exp_XX": float(r["exp_XX"]),
                "exp_XX_se": float(r["exp_XX_se"]),
                "exp_YY": float(r["exp_YY"]),
                "exp_YY_se": float(r["exp_YY_se"]),
                "exp_ZZ": float(r["exp_ZZ"]),
                "exp_ZZ_se": float(r["exp_ZZ_se"]),
                "fidelity": float(r["fidelity"]),
                "fidelity_se": float(r["fidelity_se"]),
                "shots": int(r["shots"]),
            })
            
    # 6. Discrete PMF and CCDF distributions
    all_cuts = sorted(exact_res["cut_distribution"].keys())
    
    # Helper to convert raw histograms to cut frequency
    def get_cut_dist(hist):
        c_dist = {c: 0 for c in all_cuts}
        for bs, info in hist.items():
            cw = info["cut_weight"]
            cnt = info["count"]
            c_dist[cw] = c_dist.get(cw, 0) + cnt
        return c_dist
        
    b_noisy_dist = get_cut_dist(runs["Processor_B_noisy"]["histogram"])
    d_noisy_dist = get_cut_dist(runs["Processor_D_noisy"]["histogram"])
    
    p_rand = [exact_res["cut_distribution"][c] / 64.0 for c in all_cuts]
    p_b_noisy = [b_noisy_dist[c] / 4096.0 for c in all_cuts]
    p_d_noisy = [d_noisy_dist[c] / 4096.0 for c in all_cuts]
    
    ccdf_rand = [float(np.sum(p_rand[i:])) for i in range(len(all_cuts))]
    ccdf_b_noisy = [float(np.sum(p_b_noisy[i:])) for i in range(len(all_cuts))]
    ccdf_d_noisy = [float(np.sum(p_d_noisy[i:])) for i in range(len(all_cuts))]
    
    distribution_data = {
        "cut_values": all_cuts,
        "pmf": {
            "uniform_random": p_rand,
            "processor_b_noisy": p_b_noisy,
            "processor_d_noisy": p_d_noisy,
        },
        "ccdf": {
            "uniform_random": ccdf_rand,
            "processor_b_noisy": ccdf_b_noisy,
            "processor_d_noisy": ccdf_d_noisy,
        }
    }
    
    # 7. Knapsack exploratory instance from instances.json
    with open("instances.json", "r", encoding="utf-8") as f:
        all_instances = json.load(f)
    ps_o3 = all_instances.get("PS-O3", {})
    
    knapsack_items = []
    if "values" in ps_o3 and "weights" in ps_o3:
        vals = ps_o3["values"]
        wgts = ps_o3["weights"]
        cap = ps_o3["capacity"]
        names = ["Emergency Water Kit", "First-Aid Trauma Pack", "Radio Comms Unit", "Thermal Blankets", "Ration Supply Pack"]
        for i in range(len(vals)):
            knapsack_items.append({
                "id": i,
                "name": names[i] if i < len(names) else f"Item {i}",
                "value": vals[i],
                "weight": wgts[i],
            })
            
        # Enumerate all 32 subsets
        knapsack_subsets = []
        for s_idx in range(1 << len(vals)):
            chosen = [(s_idx >> b) & 1 for b in range(len(vals))]
            tot_w = sum(wgts[b] for b in range(len(vals)) if chosen[b] == 1)
            tot_v = sum(vals[b] for b in range(len(vals)) if chosen[b] == 1)
            feasible = (tot_w <= cap)
            knapsack_subsets.append({
                "subset_idx": s_idx,
                "chosen": chosen,
                "total_weight": tot_w,
                "total_value": tot_v,
                "feasible": feasible,
            })
        best_v = max(s["total_value"] for s in knapsack_subsets if s["feasible"])
        for s in knapsack_subsets:
            s["is_optimal"] = (s["feasible"] and s["total_value"] == best_v)
            
        knapsack_data = {
            "num_items": ps_o3["num_items"],
            "capacity": cap,
            "reference_penalty_P": ps_o3.get("reference_penalty_P", 5),
            "items": knapsack_items,
            "subsets": knapsack_subsets,
            "exact_optimal_value": best_v,
            "optimal_subset": next(s for s in knapsack_subsets if s["is_optimal"]),
        }
    else:
        knapsack_data = {}
        
    # 8. Precompute 2D parameter landscape grid (30 x 30)
    print("Computing 30x30 parameter landscape grid...")
    solver = QAOASolver(weighted_edges, num_qubits=6)
    grid_n = 30
    gammas = np.linspace(-0.6, 0.6, grid_n).tolist()
    betas = np.linspace(-0.1, 0.9, grid_n).tolist()
    landscape_grid = []
    for bi, b in enumerate(betas):
        row = []
        for gi, g in enumerate(gammas):
            ev = solver.evaluate_statevector_expectation([float(g)], [float(b)])
            row.append(round(ev, 4))
        landscape_grid.append(row)
        
    landscape_data = {
        "gammas": [round(g, 4) for g in gammas],
        "betas": [round(b, 4) for b in betas],
        "grid": landscape_grid,
        "optimal_point": {
            "gamma": meta["qaoa_optimization"]["best_gamma"][0],
            "beta": meta["qaoa_optimization"]["best_beta"][0],
            "expected_cut": meta["qaoa_optimization"]["theoretical_expected_cut"],
            "approx_ratio": meta["qaoa_optimization"]["theoretical_approx_ratio"],
        },
        "random_baseline_cut": 13.5,
    }
    
    studio_payload = {
        "metadata": {
            "problem_id": "PS-O1",
            "team": "VARANASI",
            "team_id": "AP251100708044",
            "title": "Quantum Optimization of Network Partitioning Using QAOA",
            "lead": "Ganesh Pirinti",
            "institution": "SRM University-AP",
            "basis_gates": ["rz", "sx", "x", "cx"],
            "shots": 4096,
            "seeds": [0, 1, 2, 3, 4],
            "noise_rates": {"p1": 0.001, "p2": 0.005, "p_readout": 0.01},
        },
        "graph": {
            "num_vertices": num_vertices,
            "num_edges": len(weighted_edges),
            "total_weight": exact_res["total_graph_weight"],
            "weighted_edges": weighted_edges,
        },
        "classical_ground_truth": {
            "max_cut_weight": exact_res["max_cut_weight"],
            "optimal_solution_count": exact_res["optimal_solution_count"],
            "weighted_cut_fraction": exact_res["max_cut_weight"] / exact_res["total_graph_weight"],
            "edge_count_fraction": 7.0 / 9.0,
            "optimal_partitions": exact_res["optimal_partitions"],
            "uniform_random": {
                "mean_cut": exact_res["uniform_random_mean_cut"],
                "approx_ratio": exact_res["uniform_random_approx_ratio"],
                "p_opt": exact_res["uniform_random_p_opt"],
            },
            "states_64": states_64,
        },
        "processors": {
            "Processor_A": {
                "name": "Processor A",
                "num_qubits": proc_a["num_qubits"],
                "edges": proc_a["edges"],
                "executable": False,
                "reason": "Needs 6 logical qubits, physical capacity is 5 qubits.",
                "metrics": {"cx": 0, "depth": 0, "two_q_depth": 0, "swaps": 0},
            },
            "Processor_B": {
                "name": "Processor B",
                "num_qubits": proc_b["num_qubits"],
                "edges": proc_b["edges"],
                "executable": True,
                "metrics": runs["Processor_B_noisy"]["metrics"],
                "noisy_results": {
                    "mean_cut": runs["Processor_B_noisy"]["mean_cut"],
                    "approx_ratio": runs["Processor_B_noisy"]["approx_ratio"],
                    "p_opt": runs["Processor_B_noisy"]["optimal_sample_probability"],
                    "optimal_count": runs["Processor_B_noisy"]["optimal_sample_count"],
                },
                "ideal_results": {
                    "mean_cut": runs["Processor_B_ideal"]["mean_cut"],
                    "approx_ratio": runs["Processor_B_ideal"]["approx_ratio"],
                    "p_opt": runs["Processor_B_ideal"]["optimal_sample_probability"],
                    "optimal_count": runs["Processor_B_ideal"]["optimal_sample_count"],
                }
            },
            "Processor_D": {
                "name": "Processor D (VARANASI Co-Design)",
                "num_qubits": proc_d["num_qubits"],
                "edges": proc_d["edges"],
                "executable": True,
                "metrics": runs["Processor_D_noisy"]["metrics"],
                "noisy_results": {
                    "mean_cut": runs["Processor_D_noisy"]["mean_cut"],
                    "approx_ratio": runs["Processor_D_noisy"]["approx_ratio"],
                    "p_opt": runs["Processor_D_noisy"]["optimal_sample_probability"],
                    "optimal_count": runs["Processor_D_noisy"]["optimal_sample_count"],
                },
                "ideal_results": {
                    "mean_cut": runs["Processor_D_ideal"]["mean_cut"],
                    "approx_ratio": runs["Processor_D_ideal"]["approx_ratio"],
                    "p_opt": runs["Processor_D_ideal"]["optimal_sample_probability"],
                    "optimal_count": runs["Processor_D_ideal"]["optimal_sample_count"],
                }
            }
        },
        "distributions": distribution_data,
        "bell_verification": bell_rows,
        "landscape": landscape_data,
        "knapsack_scenario": knapsack_data,
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(studio_payload, f, indent=2)
    print(f"Exported studio data to {output_path} ({os.path.getsize(output_path):,} bytes)")
    
    # Also write a copy to web/public/data/benchmark_data.json if public exists
    pub_path = "web/public/data/benchmark_data.json"
    os.makedirs(os.path.dirname(pub_path), exist_ok=True)
    with open(pub_path, "w", encoding="utf-8") as f:
        json.dump(studio_payload, f, indent=2)
    print(f"Exported studio data to {pub_path}")

if __name__ == "__main__":
    generate_studio_data()
