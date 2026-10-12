"""
Visualizations for official QFF 2026 Processors A & B and QAOA Max-Cut Benchmarks.
"""

import os
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


def plot_graph_and_topologies(
    graph_data: Dict[str, Any],
    proc_a: Dict[str, Any],
    proc_b: Dict[str, Any],
    output_path: str
) -> None:
    """Side-by-side plot of the problem graph and official Processor A & B topologies."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    
    # 1. Problem Graph (6-node)
    G_prob = nx.Graph()
    for e in graph_data["edges"]:
        G_prob.add_edge(e["source"], e["target"], weight=e["weight"])
    pos_prob = nx.circular_layout(G_prob)
    ax = axes[0]
    nx.draw_networkx_nodes(G_prob, pos_prob, ax=ax, node_color="#4C72B0", node_size=700)
    nx.draw_networkx_labels(G_prob, pos_prob, ax=ax, font_color="white", font_weight="bold")
    weights = nx.get_edge_attributes(G_prob, "weight")
    nx.draw_networkx_edges(G_prob, pos_prob, ax=ax, width=2.0, edge_color="#333333")
    nx.draw_networkx_edge_labels(G_prob, pos_prob, edge_labels=weights, ax=ax, font_size=9)
    ax.set_title(
        f"Problem Graph (PS-O1 6-Node)\nTotal Weight: {graph_data['total_weight']} | Max Cut: {graph_data.get('classical_exact_max_cut', 'N/A')}",
        fontsize=11, fontweight="bold"
    )
    ax.axis("off")
    
    # 2. Official Processor A (5 qubits: T-shaped tree)
    G_a = nx.Graph()
    for u, v in proc_a["coupling_edges_undirected"]:
        G_a.add_edge(u, v)
    pos_a = {
        0: (0, 1),
        1: (1, 1),   # central node
        2: (2, 1),
        3: (1, 0),
        4: (1, -1)
    }
    ax = axes[1]
    nx.draw_networkx_nodes(G_a, pos_a, ax=ax, node_color="#C44E52", node_size=700)
    nx.draw_networkx_labels(G_a, pos_a, ax=ax, font_color="white", font_weight="bold")
    nx.draw_networkx_edges(G_a, pos_a, ax=ax, width=2.5, edge_color="#C44E52")
    ax.set_title(
        "Official Processor A (5 Qubits)\nT-Tree Topology | Edges: (0,1),(1,2),(1,3),(3,4)\n[Cannot fit 6-qubit circuit directly]",
        fontsize=11, fontweight="bold"
    )
    ax.axis("off")
    
    # 3. Official Processor B (9 qubits: heavy-hex lattice)
    G_b = nx.Graph()
    for u, v in proc_b["coupling_edges_undirected"]:
        G_b.add_edge(u, v)
    pos_b = {
        0: (0, 2),
        1: (1, 2),
        2: (2, 2),
        3: (2, 1),
        4: (2, 0),
        5: (1, 0),
        6: (1, 1),   # high-degree hub
        7: (0, 1),
        8: (0, 0)
    }
    ax = axes[2]
    nx.draw_networkx_nodes(G_b, pos_b, ax=ax, node_color="#55A868", node_size=700)
    nx.draw_networkx_labels(G_b, pos_b, ax=ax, font_color="white", font_weight="bold")
    nx.draw_networkx_edges(G_b, pos_b, ax=ax, width=2.0, edge_color="#55A868")
    ax.set_title(
        "Official Processor B (9 Qubits)\nHeavy-Hex Inspired Mesh | 12 Undirected Edges\n[Accommodates 6-qubit circuits with routing paths]",
        fontsize=11, fontweight="bold"
    )
    ax.axis("off")
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_cut_distribution(
    bitstring_probs: Dict[str, float],
    edges: List[Dict[str, Any]],
    classical_res: Dict[str, Any],
    expected_cut: float,
    output_path: str
) -> None:
    """Plot probability distribution of QAOA sampled bitstrings sorted by cut value."""
    data = []
    for bstr, prob in bitstring_probs.items():
        cut = sum(e["weight"] for e in edges if bstr[e["source"]] != bstr[e["target"]])
        is_opt = bstr in classical_res["optimal_bitstrings"]
        data.append({"bitstring": bstr, "cut": cut, "probability": prob, "is_opt": is_opt})
        
    df = pd.DataFrame(data).sort_values(by="cut")
    
    plt.figure(figsize=(13, 6))
    colors = ["#C44E52" if row["is_opt"] else "#4C72B0" for _, row in df.iterrows()]
    plt.bar(range(len(df)), df["probability"], color=colors, width=0.8, alpha=0.85)
    
    max_cut = classical_res["max_cut_value"]
    random_cut = classical_res["random_baseline_expectation"]
    
    plt.title(
        f"QAOA Sampling Distribution on Canonical 6-Node Graph\n"
        f"Expected Cut: {expected_cut:.4f} | Classical Max Cut: {max_cut:.1f} | Random Baseline: {random_cut:.1f}",
        fontsize=12, fontweight="bold"
    )
    plt.xlabel("Sampled Bitstring Index (Sorted by Ascending Cut Value)", fontsize=11)
    plt.ylabel("Measurement Probability", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    
    # Annotate top optimal state
    opt_indices = [idx for idx, (_, row) in enumerate(df.iterrows()) if row["is_opt"]]
    if opt_indices:
        idx = opt_indices[-1]
        p = df.iloc[idx]["probability"]
        plt.annotate(
            f"Global Optima\nCut = {max_cut:.1f}",
            xy=(idx, p),
            xytext=(idx - 12, p + 0.005),
            arrowprops=dict(facecolor="#C44E52", shrink=0.05, width=1, headwidth=6),
            fontsize=9, fontweight="bold", color="#C44E52"
        )
        
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_swap_and_depth_comparison(
    benchmark_df: pd.DataFrame,
    output_path: str
) -> None:
    """Plot grouped bar charts of Depth, CX Count, and SWAP overhead across configurations."""
    # Filter only successfully compiled records
    comp_df = benchmark_df[benchmark_df["status"] == "COMPILED_SUCCESSFULLY"].copy()
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # We plot the 5-node co-design benchmark comparing Processor A vs Processor B head-to-head
    sub5 = comp_df[comp_df["instance"] == "5-Node_Subgraph"].copy()
    if sub5.empty:
        sub5 = comp_df
        
    opt_levels = sorted(sub5["opt_level"].unique())
    x = np.arange(len(opt_levels))
    bar_width = 0.35
    
    # Processor A data
    df_a = sub5[sub5["processor_id"] == "Processor_A"].sort_values("opt_level")
    # Processor B data
    df_b = sub5[sub5["processor_id"] == "Processor_B"].sort_values("opt_level")
    
    # 1. SWAP Count
    swaps_col = "routing_swaps" if "routing_swaps" in sub5.columns else "swap_count"
    depth_col = "physical_depth" if "physical_depth" in sub5.columns else "circuit_depth"

    ax = axes[0]
    ax.bar(x - bar_width/2, df_a[swaps_col], width=bar_width, label="Processor A (5Q Tree)", color="#C44E52")
    ax.bar(x + bar_width/2, df_b[swaps_col], width=bar_width, label="Processor B (9Q Mesh)", color="#55A868")
    ax.set_title("Routing SWAP Gate Overhead\n(5-Node Co-Design Benchmark)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Transpiler Optimization Level", fontsize=10)
    ax.set_ylabel("SWAP Gate Count", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Level {lvl}" for lvl in opt_levels])
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()
    
    # 2. Total CX Count
    ax = axes[1]
    ax.bar(x - bar_width/2, df_a["physical_cx"], width=bar_width, label="Processor A (5Q Tree)", color="#C44E52")
    ax.bar(x + bar_width/2, df_b["physical_cx"], width=bar_width, label="Processor B (9Q Mesh)", color="#55A868")
    ax.set_title("Physical CX Gate Count\n(5-Node Co-Design Benchmark)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Transpiler Optimization Level", fontsize=10)
    ax.set_ylabel("Total CX Gates", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Level {lvl}" for lvl in opt_levels])
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()
    
    # 3. Circuit Depth
    ax = axes[2]
    ax.bar(x - bar_width/2, df_a[depth_col], width=bar_width, label="Processor A (5Q Tree)", color="#C44E52")
    ax.bar(x + bar_width/2, df_b[depth_col], width=bar_width, label="Processor B (9Q Mesh)", color="#55A868")
    ax.set_title("Transpiled Circuit Depth\n(5-Node Co-Design Benchmark)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Transpiler Optimization Level", fontsize=10)
    ax.set_ylabel("Circuit Depth", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Level {lvl}" for lvl in opt_levels])
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
