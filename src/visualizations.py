"""Plotting and visualization utilities for VARANASI Phase 2 PS-O1.

Generates high-resolution PNG figures:
1. network_partitioning_graph.png - Locked 6-node graph with optimal partition colored
2. processor_topologies.png - Topologies of Processors A, B, and D side-by-side
3. bell_fidelity_comparison.png - Bell state fidelity on Processor D (near vs far, ideal vs noisy)
4. qaoa_cut_distribution.png - Sampled cut distribution vs uniform random baseline
5. processor_resource_comparison.png - Transpilation metrics (CX, depth, SWAPs)
"""
from __future__ import annotations
import os
from typing import List, Tuple, Dict, Any
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def plot_network_partitioning_graph(
    weighted_edges: List[List[int]],
    optimal_partition: Tuple[int, ...] = (1, 1, 0, 1, 0, 0),
    output_path: str = "results/figures/network_partitioning_graph.png",
):
    """Plot the locked 6-vertex PS-O1 graph with optimal partition coloring."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    G = nx.Graph()
    for u, v, w in weighted_edges:
        G.add_edge(u, v, weight=w)
        
    pos = {
        0: np.array([-1.0, 0.5]),
        1: np.array([1.0, 0.5]),
        2: np.array([-1.0, -0.5]),
        3: np.array([0.0, 1.0]),
        4: np.array([0.0, -1.0]),
        5: np.array([1.0, -0.5]),
    }
    
    # Identify cut and uncut edges
    cut_edges = []
    uncut_edges = []
    for u, v, d in G.edges(data=True):
        if optimal_partition[u] != optimal_partition[v]:
            cut_edges.append((u, v))
        else:
            uncut_edges.append((u, v))
            
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    
    # Node colors based on partition
    # Group S (value 1) vs Group S_bar (value 0)
    node_colors = ["#2b5c8f" if optimal_partition[i] == 1 else "#d95f02" for i in range(6)]
    
    # Draw uncut edges
    nx.draw_networkx_edges(
        G, pos, edgelist=uncut_edges, width=2.0, alpha=0.5,
        edge_color="#888888", style="solid", ax=ax
    )
    # Draw cut edges
    nx.draw_networkx_edges(
        G, pos, edgelist=cut_edges, width=3.5, alpha=0.95,
        edge_color="#e41a1c", style="dashed", ax=ax
    )
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, node_color=node_colors, node_size=1100,
        edgecolors="#222222", linewidths=2.0, ax=ax
    )
    nx.draw_networkx_labels(
        G, pos, font_size=13, font_family="sans-serif",
        font_weight="bold", font_color="white", ax=ax
    )
    
    # Edge labels (weights)
    edge_labels = {(u, v): f"w={d['weight']}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_size=10,
        font_color="#111111", font_weight="bold", ax=ax
    )
    
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Group S (x=1) {0, 1, 3}',
               markerfacecolor='#2b5c8f', markersize=12),
        Line2D([0], [0], marker='o', color='w', label=r'Group $\bar{S}$ (x=0) {2, 4, 5}',
               markerfacecolor='#d95f02', markersize=12),
        Line2D([0], [0], color='#e41a1c', lw=3, linestyle='--',
               label='Cut Edges (Weight = 22)'),
        Line2D([0], [0], color='#888888', lw=2, linestyle='-',
               label='Internal Edges (Weight = 5)'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.95, fontsize=10)
    ax.set_title(
        "PS-O1 Network Partitioning: Locked 6-Vertex Graph\nOptimal Cut Partition ($C^* = 22 / 27$)",
        fontsize=13, fontweight="bold", pad=12
    )
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_processor_topologies(
    proc_a: dict,
    proc_b: dict,
    proc_d: dict,
    output_path: str = "results/figures/processor_topologies.png",
):
    """Plot Processor A, B, and D coupling maps side-by-side."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)
    
    # Processor A
    GA = nx.Graph()
    GA.add_nodes_from(range(proc_a["num_qubits"]))
    GA.add_edges_from(proc_a["edges"])
    pos_A = nx.spring_layout(GA, seed=42)
    nx.draw_networkx(
        GA, pos_A, ax=axes[0], node_color="#d95f02", node_size=800,
        font_color="white", font_weight="bold", edge_color="#444444", width=2.0
    )
    axes[0].set_title(
        f"Processor A (5 Qubits)\nCapacity Bottleneck: INFEASIBLE for PS-O1\n(Needs 6 qubits > 5 available)",
        fontsize=11, fontweight="bold", pad=10
    )
    axes[0].axis("off")
    
    # Processor B
    GB = nx.Graph()
    GB.add_nodes_from(range(proc_b["num_qubits"]))
    GB.add_edges_from(proc_b["edges"])
    pos_B = nx.spring_layout(GB, seed=42)
    nx.draw_networkx(
        GB, pos_B, ax=axes[1], node_color="#7570b3", node_size=800,
        font_color="white", font_weight="bold", edge_color="#444444", width=2.0
    )
    axes[1].set_title(
        f"Processor B (9 Qubits)\nRouting Bottleneck: 1 SWAP (+3 CX)\nCX Count = 21, Depth = 37",
        fontsize=11, fontweight="bold", pad=10
    )
    axes[1].axis("off")
    
    # Processor D
    GD = nx.Graph()
    GD.add_nodes_from(range(proc_d["num_qubits"]))
    GD.add_edges_from(proc_d["edges"])
    # Circular or spring layout
    pos_D = {
        0: np.array([-0.8, 0.4]),
        1: np.array([0.8, 0.4]),
        2: np.array([-0.8, -0.4]),
        3: np.array([0.0, 0.7]),
        4: np.array([0.0, -0.7]),
        5: np.array([0.8, -0.4]),
        6: np.array([1.4, -0.7]),
        7: np.array([1.8, 0.0]),
        8: np.array([1.4, 0.7]),
    }
    # Color active problem qubits (0..5) green, ancillary ring qubits (6..8) blue
    d_colors = ["#1b9e77" if i < 6 else "#386cb0" for i in range(proc_d["num_qubits"])]
    nx.draw_networkx(
        GD, pos_D, ax=axes[2], node_color=d_colors, node_size=800,
        font_color="white", font_weight="bold", edge_color="#222222", width=2.0
    )
    axes[2].set_title(
        f"Processor D: VARANASI Co-Design (9 Qubits)\nProblem-Matched: ZERO SWAPs (0 CX Overhead)\nCX Count = 18, Depth = 29, Max Degree = 4",
        fontsize=11, fontweight="bold", pad=10
    )
    axes[2].axis("off")
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_bell_fidelity_comparison(
    bell_rows: List[Dict[str, Any]],
    output_path: str = "results/figures/bell_fidelity_comparison.png",
):
    """Plot Bell state fidelity on Processor D comparing near vs far pair under ideal and noisy."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    labels = []
    fidelities = []
    errors = []
    colors = []
    
    for r in bell_rows:
        label = f"{r['pair_type'].capitalize()}\n{r['qubit_pair']} (dist {r['pair_distance']})\n[{r['condition']}]"
        labels.append(label)
        fidelities.append(r["fidelity"])
        errors.append(r["fidelity_se"])
        if r["condition"] == "ideal":
            colors.append("#2ca25f")
        else:
            colors.append("#e6550d" if r["pair_type"] == "near" else "#de2d26")
            
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    x = np.arange(len(labels))
    bars = ax.bar(x, fidelities, yerr=errors, capsize=6, color=colors, edgecolor="#222222", width=0.55)
    
    ax.set_ylabel("Bell State Fidelity $F(|\\Phi^+\\rangle)$", fontsize=12, fontweight="bold")
    ax.set_title("Processor D Objective 1: Bell State Verification ($4096$ shots per basis)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_ylim([0.88, 1.04])
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    
    for bar, f, se in zip(bars, fidelities, errors):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0, height + 0.008,
            f"{f:.4f} \u00b1 {se:.4f}", ha="center", va="bottom",
            fontsize=9.5, fontweight="bold"
        )
        
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_qaoa_cut_distribution(
    sampled_counts_b_noisy: Dict[int, int],
    sampled_counts_d_noisy: Dict[int, int],
    exact_cut_distribution: Dict[int, int],
    total_shots: int = 4096,
    output_path: str = "results/figures/qaoa_cut_distribution.png",
):
    """Plot probability distribution of sampled cut weights vs uniform random baseline."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    all_possible_cuts = sorted(exact_cut_distribution.keys())
    
    prob_uniform = [exact_cut_distribution[c] / 64.0 for c in all_possible_cuts]
    prob_b = [sampled_counts_b_noisy.get(c, 0) / float(total_shots) for c in all_possible_cuts]
    prob_d = [sampled_counts_d_noisy.get(c, 0) / float(total_shots) for c in all_possible_cuts]
    
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    width = 0.25
    x = np.arange(len(all_possible_cuts))
    
    ax.bar(x - width, prob_uniform, width=width, label="Uniform Random Baseline (Exact)", color="#999999", edgecolor="#222")
    ax.bar(x, prob_b, width=width, label="QAOA p=1 on Processor B (Noisy)", color="#7570b3", edgecolor="#222")
    ax.bar(x + width, prob_d, width=width, label="QAOA p=1 on Processor D (Noisy)", color="#1b9e77", edgecolor="#222")
    
    ax.set_xlabel("Cut Weight $C(x)$", fontsize=12, fontweight="bold")
    ax.set_ylabel("Sampling Probability", fontsize=12, fontweight="bold")
    ax.set_title("Cut Weight Distribution: QAOA ($p=1$) vs Uniform Random Baseline\nHighlighting Optimal Cut $C^* = 22$", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels([str(c) for c in all_possible_cuts], fontsize=10, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    
    # Highlight C* = 22
    max_idx = all_possible_cuts.index(22)
    ax.annotate(
        "Optimal $C^* = 22$\n$P_{opt} \\approx 12.5\\%$ vs $3.1\\%$ (Random)",
        xy=(max_idx + width, prob_d[max_idx]),
        xytext=(max_idx - 1.5, max_idx * 0.01 + 0.12),
        arrowprops=dict(facecolor="#e41a1c", shrink=0.08, width=2, headwidth=8),
        fontsize=10.5, fontweight="bold", color="#e41a1c",
        bbox=dict(boxstyle="round,pad=0.4", fc="#fff", ec="#e41a1c", lw=1.5)
    )
    
    ax.legend(framealpha=0.95, fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_processor_resource_comparison(
    metrics_a: dict,
    metrics_b: dict,
    metrics_d: dict,
    output_path: str = "results/figures/processor_resource_comparison.png",
):
    """Plot resource metrics (CX count, total depth, 2Q depth, SWAPs) across processors."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    categories = ["CX Count", "Circuit Depth", "Two-Qubit Depth", "SWAPs Inserted"]
    
    # Processor A is not executable (0 across gates)
    val_b = [metrics_b["cx"], metrics_b["depth"], metrics_b["two_q_depth"], metrics_b["swaps"]]
    val_d = [metrics_d["cx"], metrics_d["depth"], metrics_d["two_q_depth"], metrics_d["swaps"]]
    
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    x = np.arange(len(categories))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, val_b, width, label="Processor B (9 Qubits, Generic)", color="#7570b3", edgecolor="#222")
    rects2 = ax.bar(x + width/2, val_d, width, label="Processor D (9 Qubits, VARANASI Co-Design)", color="#1b9e77", edgecolor="#222")
    
    ax.set_ylabel("Metric Value", fontsize=12, fontweight="bold")
    ax.set_title("Transpilation Resource Comparison for PS-O1 QAOA Circuit\n(Processor A: Infeasible due to 5-Qubit Capacity Limit)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10.5, fontweight="bold")
    ax.legend(framealpha=0.95, fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    
    for rects in [rects1, rects2]:
        for bar in rects:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.4,
                    f"{int(height)}", ha="center", va="bottom", fontsize=10, fontweight="bold")
                    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
