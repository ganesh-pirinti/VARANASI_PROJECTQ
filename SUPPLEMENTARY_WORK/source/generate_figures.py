#!/usr/bin/env python3
"""
generate_figures.py — Supplementary Scientific Figures Generator for Project VARANASI
Generates 7 publication-grade figures in PNG (300 DPI) and vector SVG formats.
Follows a restrained, classic scientific paper aesthetic (warm white background,
charcoal/navy text, muted steel-blue and bronze accents).
"""

import os
import sys
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D

# Base directories
SCRIPT_DIR = Path(__file__).resolve().parent
SUPP_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SUPP_DIR.parent
PHASE2_DIR = PROJECT_ROOT / "PHASE_2"
FIGURES_DIR = SUPP_DIR / "figures"

# Ensure output directory exists
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Visual theme constants
BG_COLOR = "#FFFFFF"
TEXT_DARK = "#0F172A"       # Deep slate/charcoal
TEXT_MUTED = "#475569"      # Slate grey
STEEL_BLUE = "#2563EB"      # Muted steel blue
STEEL_BLUE_DARK = "#1E40AF"
BRONZE = "#B45309"          # Restrained bronze/amber
BRONZE_DARK = "#92400E"
BRONZE_LIGHT = "#FEF3C7"
BOX_BG = "#F8FAFC"          # Light cool grey
BOX_BORDER = "#CBD5E1"      # Slate border
SUCCESS_GREEN = "#15803D"
ERROR_RED = "#B91C1C"

# Configure global matplotlib style
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 13,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "figure.facecolor": BG_COLOR,
    "axes.facecolor": BG_COLOR,
    "savefig.facecolor": BG_COLOR,
})

def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Required source file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ==============================================================================
# Figure 01: Three-Dimensional Weighted Network Graph
# ==============================================================================
def generate_figure_01():
    print("Generating Figure 01: 3D Weighted Network...")
    instance_path = PHASE2_DIR / "instances.json"
    data = load_json(instance_path)
    edges_raw = data["PS-O1"]["weighted_edges"]  # [[u, v, w], ...]
    
    # Visual 3D coordinates for spatial separation between partitions:
    # S = {0, 1, 3} on top plane z = +0.55
    # S_bar = {2, 4, 5} on bottom plane z = -0.55
    coords = {
        0: np.array([-0.65, -0.45,  0.55]),
        1: np.array([ 0.00,  0.75,  0.55]),
        3: np.array([ 0.65, -0.45,  0.55]),
        2: np.array([-0.65,  0.45, -0.55]),
        4: np.array([ 0.65,  0.45, -0.55]),
        5: np.array([ 0.00, -0.75, -0.55]),
    }
    
    fig = plt.figure(figsize=(9, 7), facecolor=BG_COLOR)
    ax = fig.add_subplot(111, projection="3d", facecolor=BG_COLOR)
    
    # Draw edges
    cut_weight = 0
    uncut_weight = 0
    
    for u, v, w in edges_raw:
        p1 = coords[u]
        p2 = coords[v]
        # Check if cut edge (crosses between top and bottom planes)
        is_cut = (p1[2] * p2[2] < 0)
        
        if is_cut:
            cut_weight += w
            color = STEEL_BLUE
            linestyle = "-"
            linewidth = 1.2 + 0.35 * w
            alpha = 0.85
        else:
            uncut_weight += w
            color = BRONZE
            linestyle = "--"
            linewidth = 1.2 + 0.35 * w
            alpha = 0.95
            
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                color=color, linestyle=linestyle, linewidth=linewidth, alpha=alpha, zorder=2)
        
        # Edge weight label at midpoint with small displacement
        mid = (p1 + p2) / 2.0
        ax.text(mid[0], mid[1], mid[2] + 0.04, f"w={w}",
                color=TEXT_DARK, fontsize=8.5, weight="bold",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="#FFFFFF", edgecolor=color, alpha=0.9, lw=0.8),
                ha="center", va="center", zorder=4)

    # Draw nodes
    for node, pt in coords.items():
        is_cluster_s = (pt[2] > 0)
        color = STEEL_BLUE_DARK if is_cluster_s else BRONZE_DARK
        ax.scatter([pt[0]], [pt[1]], [pt[2]], s=360, color=color, edgecolors="#FFFFFF", linewidths=1.8, zorder=5)
        ax.text(pt[0], pt[1], pt[2], f"q{node}", color="#FFFFFF", fontsize=9.5, weight="bold",
                ha="center", va="center", zorder=6)

    # Titles & Annotations
    ax.set_title("Figure 01: Three-Dimensional Spatial Partitioning of the PS-O1 Network Graph\n"
                 f"Optimal Partition: $S = \\{{0, 1, 3\\}}$ (Blue) vs $\\bar{{S}} = \\{{2, 4, 5\\}}$ (Bronze) | Total Weight $W = 27$",
                 pad=12, fontsize=11, color=TEXT_DARK, weight="bold")
    
    # Turn off background grid/panes for clean paper style
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor("#E2E8F0")
    ax.yaxis.pane.set_edgecolor("#E2E8F0")
    ax.zaxis.pane.set_edgecolor("#E2E8F0")
    ax.grid(True, linestyle=":", color="#E2E8F0", alpha=0.7)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    
    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=STEEL_BLUE_DARK, markersize=10,
                   label=r"Partition $S = \{0, 1, 3\}$ (Upper Plane, $z=+0.55$)"),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=BRONZE_DARK, markersize=10,
                   label=r"Partition $\bar{S} = \{2, 4, 5\}$ (Lower Plane, $z=-0.55$)"),
        plt.Line2D([0], [0], color=STEEL_BLUE, lw=2.5, linestyle="-",
                   label=f"Cut Edges: 7 edges, Total Cut Weight $C^* = {cut_weight}$ (81.5%)"),
        plt.Line2D([0], [0], color=BRONZE, lw=2.5, linestyle="--",
                   label=f"Internal Uncut Edges: 2 edges $(0,3: 4), (2,4: 1)$, Weight = {uncut_weight} (18.5%)"),
    ]
    ax.legend(handles=legend_elements, loc="lower center", bbox_to_anchor=(0.5, -0.05),
              frameon=True, facecolor="#F8FAFC", edgecolor=BOX_BORDER, framealpha=0.95, fontsize=8.5)

    ax.view_init(elev=24, azim=40)
    plt.tight_layout()
    
    fig.savefig(FIGURES_DIR / "01_weighted_network_3d.png", dpi=300)
    fig.savefig(FIGURES_DIR / "01_weighted_network_3d.svg")
    plt.close(fig)

# ==============================================================================
# Figure 02: Classical Optimization Workflow
# ==============================================================================
def generate_figure_02():
    print("Generating Figure 02: Classical Optimization Workflow...")
    fig, ax = plt.subplots(figsize=(10, 6.2), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")
    
    # Title
    ax.text(0.5, 0.95, "Figure 02: Deterministic Classical Ground-Truth Optimization Pipeline\n"
                       "Exhaustive 64-State Enumeration Establishing Benchmark Baseline $C^* = 22$",
            ha="center", va="top", fontsize=12, weight="bold", color=TEXT_DARK)
    
    # Flowchart boxes definition: (x, y, w, h, title, content, border_color)
    boxes = [
        (0.04, 0.52, 0.26, 0.34, "1. Graph & QUBO Model",
         "• 6 vertices ($V$), 9 weighted edges ($E$)\n"
         "• Total link weight $W = 27$\n"
         "• Binary indicator variables $x_i \\in \\{0, 1\\}$\n"
         "• Cut metric for edge $(u, v)$:\n"
         "  $C_{uv} = x_u + x_v - 2x_u x_v$\n"
         "• Total cut objective:\n"
         "  $C(x) = \\sum_{(u,v)} w_{uv} C_{uv}$", STEEL_BLUE),
        
        (0.37, 0.52, 0.26, 0.34, "2. Exhaustive Enumeration",
         "• Full configuration space: $2^6 = 64$\n"
         "• Bitstrings from $000000_2$ to $111111_2$\n"
         "• Evaluated via exact brute force\n"
         "• Constant offset: $W/2 = 13.5$\n"
         "• Cost Hamiltonian mapping:\n"
         "  $\\hat{H}_C = \\sum \\frac{w_{uv}}{2} \\hat{Z}_u \\hat{Z}_v$\n"
         "  $\\langle C \\rangle = 13.5 - \\langle \\hat{H}_C \\rangle$", STEEL_BLUE),
        
        (0.70, 0.52, 0.26, 0.34, "3. Global Optimum ($C^*$)",
         "• Global Maximum Cut: $C^* = 22$\n"
         "• Cut fraction: $22 / 27 = 81.48\\%$\n"
         "• Exactly 2 symmetric states:\n"
         "  $x^*_1 = (1, 1, 0, 1, 0, 0) \\to S=\\{0,1,3\\}$\n"
         "  $x^*_2 = (0, 0, 1, 0, 1, 1) \\to \\bar{S}=\\{2,4,5\\}$\n"
         "• Optimal sampling probability:\n"
         "  $P_{\\text{opt, random}} = 2/64 = 3.125\\%$", BRONZE),
        
        (0.18, 0.08, 0.64, 0.32, "4. Baseline Comparison & Distinction from Quantum Heuristic",
         "• Uniform Random Baseline Expectation: $\\langle C \\rangle_{\\text{random}} = W / 2 = 13.5000$ (Approximation ratio $r_{\\text{random}} = 13.5 / 22 = 0.6136$)\n"
         "• Methodological Rigor: The exact classical solver establishes mathematical ground truth, not a quantum algorithm.\n"
         "• QAOA Objective: Quantum optimization seeks to efficiently sample from the near-optimal distribution without exhaustive search.\n"
         "• Benchmark Threshold: QAOA solution quality ($r$) is formally measured relative to this exact classical ground truth ($C^*=22$).", TEXT_MUTED),
    ]
    
    for x, y, w, h, title, text, border in boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015",
                                      facecolor=BOX_BG, edgecolor=border, linewidth=1.4)
        ax.add_patch(rect)
        ax.text(x + 0.02, y + h - 0.035, title, fontsize=9.5, weight="bold", color=border)
        ax.text(x + 0.02, y + h - 0.07, text, fontsize=8.2, color=TEXT_DARK, va="top", linespacing=1.35)

    # Draw horizontal arrows
    arrow_props = dict(arrowstyle="->", color=TEXT_MUTED, lw=1.6)
    ax.annotate("", xy=(0.37, 0.69), xytext=(0.30, 0.69), arrowprops=arrow_props)
    ax.annotate("", xy=(0.70, 0.69), xytext=(0.63, 0.69), arrowprops=arrow_props)
    
    # Downward connection to baseline comparison
    ax.annotate("", xy=(0.50, 0.40), xytext=(0.50, 0.52), arrowprops=arrow_props)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "02_classical_optimization_workflow.png", dpi=300)
    fig.savefig(FIGURES_DIR / "02_classical_optimization_workflow.svg")
    plt.close(fig)

# ==============================================================================
# Figure 03: Hybrid Classical-Quantum QAOA Architecture
# ==============================================================================
def generate_figure_03():
    print("Generating Figure 03: Hybrid QAOA Architecture...")
    fig, ax = plt.subplots(figsize=(10.5, 6.5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")
    
    # Title
    ax.text(0.5, 0.96, "Figure 03: Closed-Loop Hybrid Classical–Quantum QAOA Architecture (Depth $p=1$)\n"
                       "Iterative Variational Co-Optimization Loop Between COBYLA and Qiskit Aer Simulator",
            ha="center", va="top", fontsize=12, weight="bold", color=TEXT_DARK)

    # 4 Main Blocks
    # Block 1: Classical Optimizer (COBYLA)
    rect1 = patches.FancyBboxPatch((0.05, 0.52), 0.26, 0.34, boxstyle="round,pad=0.015",
                                  facecolor="#F1F5F9", edgecolor=BRONZE_DARK, linewidth=1.5)
    ax.add_patch(rect1)
    ax.text(0.07, 0.825, "Classical Parameter Optimizer", fontsize=9.5, weight="bold", color=BRONZE_DARK)
    ax.text(0.07, 0.79,
            "• COBYLA gradient-free algorithm\n"
            "• 5 Multi-Start Seeds: $s \\in \\{0, 1, 2, 3, 4\\}$\n"
            "• Uniform sampling: $\\gamma_0, \\beta_0 \\in [0, \\pi]$\n"
            "• MaxIter budget: 80 function calls\n"
            "• Parameter update:\n"
            "  $(\\gamma_{k+1}, \\beta_{k+1}) \\leftarrow \\arg\\max \\langle C \\rangle$",
            fontsize=8.2, color=TEXT_DARK, va="top", linespacing=1.35)

    # Block 2: Quantum Circuit Ansatz
    rect2 = patches.FancyBboxPatch((0.39, 0.52), 0.28, 0.34, boxstyle="round,pad=0.015",
                                  facecolor="#F8FAFC", edgecolor=STEEL_BLUE, linewidth=1.5)
    ax.add_patch(rect2)
    ax.text(0.41, 0.825, "Parameterized Quantum Ansatz ($p=1$)", fontsize=9.5, weight="bold", color=STEEL_BLUE_DARK)
    ax.text(0.41, 0.79,
            "• Uniform superposition: $|+\\rangle^{\\otimes 6} = H^{\otimes 6} |0\\rangle^{\\otimes 6}$\n"
            "• Problem Unitary ($R_{ZZ}$ rotations):\n"
            "  $U_C(\\gamma) = \\prod_{(u,v)\\in E} \\exp(-i \\frac{\\gamma w_{uv}}{2} Z_u Z_v)$\n"
            "• Mixer Unitary ($R_X$ transverse fields):\n"
            "  $U_M(\\beta) = \\prod_{j=0}^{5} \\exp(-i \\beta X_j)$\n"
            "• Logical Circuit: 18 CX, 6 $R_Z$, 6 $R_X$",
            fontsize=8.2, color=TEXT_DARK, va="top", linespacing=1.35)

    # Block 3: Simulation Backend
    rect3 = patches.FancyBboxPatch((0.74, 0.52), 0.22, 0.34, boxstyle="round,pad=0.015",
                                  facecolor="#F8FAFC", edgecolor=STEEL_BLUE, linewidth=1.5)
    ax.add_patch(rect3)
    ax.text(0.76, 0.825, "Execution Backend (Simulated)", fontsize=9.5, weight="bold", color=STEEL_BLUE_DARK)
    ax.text(0.76, 0.79,
            "• Qiskit Aer (`AerSimulator`)\n"
            "• Hardware noise floor:\n"
            "  - $p_1 = 0.001$ (1Q depolarizing)\n"
            "  - $p_2 = 0.005$ (2Q depolarizing)\n"
            "  - $p_{\\text{readout}} = 0.01$ (bitflip)\n"
            "• Shot count: 4096 shots\n"
            "• Target Topologies: A, B, D",
            fontsize=8.2, color=TEXT_DARK, va="top", linespacing=1.35)

    # Block 4: Classical Objective Evaluator & Results Summary
    rect4 = patches.FancyBboxPatch((0.20, 0.08), 0.60, 0.32, boxstyle="round,pad=0.015",
                                  facecolor="#FAF5FF", edgecolor="#7C3AED", linewidth=1.5)
    ax.add_patch(rect4)
    ax.text(0.22, 0.365, "Expectation Value Evaluation & Convergence Tracking", fontsize=9.5, weight="bold", color="#7C3AED")
    ax.text(0.22, 0.33,
            "• Sampled Bitstring Distribution: $\\{x: N(x)\\}$ for $x \\in \\{0, 1\\}^6$\n"
            "• Sampled Expected Cut: $\\langle C \\rangle = \\sum_x \\frac{N(x)}{N_{\\text{shots}}} C(x) \\quad \\to \\quad r = \\frac{\\langle C \\rangle}{C^*}$\n"
            "• Official Trajectory Outcomes: Seeds 0, 2, 4 hit suboptimal plateaus ($r \\approx 0.707$); Seed 1 hit MaxIter (80);\n"
            "  Seed 3 found global variational optimum at $(\\gamma^* = -0.1680, \\beta^* = 0.3327) \\to \\langle C \\rangle = 17.7128$ ($r = 0.8051$).",
            fontsize=8.2, color=TEXT_DARK, va="top", linespacing=1.35)

    # Forward arrows
    arrow_fwd = dict(arrowstyle="->", color=STEEL_BLUE_DARK, lw=1.8)
    ax.annotate("", xy=(0.39, 0.69), xytext=(0.31, 0.69), arrowprops=arrow_fwd)
    ax.text(0.35, 0.71, r"$(\gamma, \beta)$", fontsize=9, color=STEEL_BLUE_DARK, ha="center", weight="bold")

    ax.annotate("", xy=(0.74, 0.69), xytext=(0.67, 0.69), arrowprops=arrow_fwd)
    ax.text(0.705, 0.71, "Compiled\nCircuit", fontsize=7.8, color=STEEL_BLUE_DARK, ha="center")

    # Downward arrow from Simulator to Evaluator
    arrow_eval = dict(arrowstyle="->", color="#7C3AED", lw=1.8)
    ax.annotate("", xy=(0.80, 0.40), xytext=(0.80, 0.52), arrowprops=arrow_eval)
    ax.text(0.81, 0.46, "Counts $\\{x: N(x)\\}$", fontsize=8.2, color="#7C3AED", va="center")

    # Feedback Loop arrow from Evaluator back to Optimizer
    arrow_feedback = dict(arrowstyle="->", color=BRONZE_DARK, lw=2.0, linestyle="-")
    ax.plot([0.20, 0.12, 0.12], [0.24, 0.24, 0.52], color=BRONZE_DARK, lw=1.8, linestyle="-")
    ax.annotate("", xy=(0.12, 0.52), xytext=(0.12, 0.45), arrowprops=arrow_feedback)
    ax.text(0.13, 0.34, "Iterative Feedback\n$\\Delta \\langle C \\rangle \\to$ Update $(\\gamma, \\beta)$",
            fontsize=8.2, color=BRONZE_DARK, weight="bold")

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "03_hybrid_qaoa_architecture.png", dpi=300)
    fig.savefig(FIGURES_DIR / "03_hybrid_qaoa_architecture.svg")
    plt.close(fig)

# ==============================================================================
# Figure 04: Quantum Processor Topologies
# ==============================================================================
def generate_figure_04():
    print("Generating Figure 04: Quantum Processor Topologies...")
    proc_a = load_json(PHASE2_DIR / "processors" / "processor_A.json")
    proc_b = load_json(PHASE2_DIR / "processors" / "processor_B.json")
    proc_d = load_json(PHASE2_DIR / "processors" / "processor_D.json")
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4.8), facecolor=BG_COLOR)
    for ax in (ax1, ax2, ax3):
        ax.set_facecolor(BG_COLOR)
        ax.axis("off")
        
    fig.suptitle("Figure 04: Quantum Processor Coupling Topologies & Structural Constraints\n"
                 "Coupling Graphs of Official Reference Processors A and B vs. Proposed Co-Designed Processor D",
                 fontsize=12, weight="bold", color=TEXT_DARK, y=0.98)

    # --- Panel 1: Processor A (5 Qubits, T-tree) ---
    pos_a = {
        0: (0.15, 0.8),
        1: (0.50, 0.8),
        2: (0.85, 0.8),
        3: (0.50, 0.4),
        4: (0.50, 0.05),
    }
    ax1.set_title("Processor A (5 Qubits, 4 Edges)\nStatus: INFEASIBLE (Needs 6 Qubits > 5)",
                  fontsize=9.5, weight="bold", color=ERROR_RED, pad=10)
    for u, v in proc_a.get("edges", proc_a.get("coupling_map")):
        p1, p2 = pos_a[u], pos_a[v]
        ax1.plot([p1[0], p2[0]], [p1[1], p2[1]], color=TEXT_MUTED, lw=2.0, zorder=1)
    for n, p in pos_a.items():
        ax1.scatter(p[0], p[1], s=380, color="#E2E8F0", edgecolors=ERROR_RED, lw=2.0, zorder=3)
        ax1.text(p[0], p[1], f"q{n}", ha="center", va="center", fontsize=9, weight="bold", color=TEXT_DARK, zorder=4)
    ax1.text(0.5, -0.15, "• Branching T-Tree Topology\n• Max degree: 3 (Node 1)\n• Capacity exceeded for 6-node Max-Cut",
             ha="center", fontsize=8.2, color=TEXT_DARK, bbox=dict(boxstyle="round,pad=0.2", facecolor=BOX_BG, edgecolor=BOX_BORDER))

    # --- Panel 2: Processor B (9 Qubits, Heavy-Hex Cyclic Mesh) ---
    pos_b = {
        0: (0.2, 0.85), 1: (0.5, 0.85), 2: (0.8, 0.85),
        8: (0.2, 0.45), 6: (0.5, 0.45), 3: (0.8, 0.45),
        7: (0.2, 0.05), 5: (0.5, 0.05), 4: (0.8, 0.05),
    }
    ax2.set_title("Processor B (9 Qubits, 12 Edges)\nRequires 1 SWAP Gate (21 CX)",
                  fontsize=9.5, weight="bold", color=STEEL_BLUE_DARK, pad=10)
    for u, v in proc_b.get("edges", proc_b.get("coupling_map")):
        p1, p2 = pos_b[u], pos_b[v]
        ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], color=STEEL_BLUE, lw=1.8, zorder=1)
    for n, p in pos_b.items():
        ax2.scatter(p[0], p[1], s=380, color=BOX_BG, edgecolors=STEEL_BLUE, lw=1.8, zorder=3)
        ax2.text(p[0], p[1], f"q{n}", ha="center", va="center", fontsize=9, weight="bold", color=TEXT_DARK, zorder=4)
    ax2.text(0.5, -0.15, "• Heavy-Hex Cyclic Mesh\n• Max degree: 5 (Node 6)\n• Transpilation: 1 SWAP, depth 37",
             ha="center", fontsize=8.2, color=TEXT_DARK, bbox=dict(boxstyle="round,pad=0.2", facecolor=BOX_BG, edgecolor=BOX_BORDER))

    # --- Panel 3: Processor D (9 Qubits, Co-Designed Planar Transmon) ---
    # Computational core (0..5) + routing ring (6..8)
    pos_d = {
        0: (0.35, 0.85), 1: (0.65, 0.85),
        2: (0.20, 0.50), 3: (0.50, 0.50), 4: (0.80, 0.50),
        5: (0.35, 0.15),
        6: (0.15, 0.15), 7: (0.05, 0.50), 8: (0.15, 0.85),
    }
    ax3.set_title("Processor D (9 Qubits, 13 Edges)\n0 SWAPs (18 CX, Theoretical Minimum)",
                  fontsize=9.5, weight="bold", color=BRONZE_DARK, pad=10)
    for u, v in proc_d.get("edges", proc_d.get("coupling_map")):
        p1, p2 = pos_d[u], pos_d[v]
        is_core = (u < 6 and v < 6)
        color = BRONZE if is_core else TEXT_MUTED
        lw = 2.0 if is_core else 1.3
        ls = "-" if is_core else ":"
        ax3.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, linestyle=ls, zorder=1)
    for n, p in pos_d.items():
        is_core = (n < 6)
        color = BRONZE_DARK if is_core else TEXT_MUTED
        bg = BRONZE_LIGHT if is_core else "#F1F5F9"
        ax3.scatter(p[0], p[1], s=380, color=bg, edgecolors=color, lw=2.0, zorder=3)
        ax3.text(p[0], p[1], f"q{n}", ha="center", va="center", fontsize=9, weight="bold", color=TEXT_DARK, zorder=4)
    ax3.text(0.5, -0.15, "• Co-Designed Planar Transmon\n• Max degree: 4 (Rules Compliant: 0 Violations)\n• Zero Routing Overhead (0 SWAPs, depth 29)",
             ha="center", fontsize=8.2, color=TEXT_DARK, bbox=dict(boxstyle="round,pad=0.2", facecolor=BOX_BG, edgecolor=BOX_BORDER))

    for ax in (ax1, ax2, ax3):
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.30, 1.05)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "04_processor_topologies.png", dpi=300)
    fig.savefig(FIGURES_DIR / "04_processor_topologies.svg")
    plt.close(fig)

# ==============================================================================
# Figure 05: QAOA p=1 Quantum Circuit Schematic
# ==============================================================================
def generate_figure_05():
    print("Generating Figure 05: QAOA Circuit Schematic...")
    fig, ax = plt.subplots(figsize=(11, 5.8), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")
    
    # Title
    ax.text(0.5, 0.96, "Figure 05: Logical Quantum Circuit Architecture for PS-O1 Network Partitioning (QAOA $p=1$)\n"
                       "Exact Hamiltonian Decomposition into Basis Gates: 18 CX Gates, 6 Single-Qubit $R_Z$, 6 $R_X$ Mixers",
            ha="center", va="top", fontsize=11.5, weight="bold", color=TEXT_DARK)

    # 6 Qubit lines
    qubit_y = [0.78 - i * 0.12 for i in range(6)]
    for i, y in enumerate(qubit_y):
        ax.plot([0.05, 0.95], [y, y], color=TEXT_MUTED, lw=1.2, zorder=1)
        ax.text(0.03, y, f"$q_{i}$", fontsize=10, weight="bold", color=TEXT_DARK, va="center", ha="right")
        ax.text(0.97, y, r"$M_Z$", fontsize=9, color=TEXT_MUTED, va="center", ha="left")

    # Time stages shading
    stages = [
        (0.08, 0.16, "Initialization\n$|+\\rangle^{\\otimes 6} = H^{\\otimes 6}|0\\rangle$", "#F1F5F9"),
        (0.24, 0.65, "Cost Hamiltonian Unitary Layer: $U_C(\\gamma) = \\prod_{(u,v)\\in E} R_{ZZ}^{(u,v)}(w_{uv}\\gamma)$\n"
                     "(9 Pairwise Interactions = 18 CX + 9 $R_Z$ Gates Decomposed Natively)", "#F8FAFC"),
        (0.72, 0.85, "Mixer Layer\n$U_M(\\beta) = R_X^{\\otimes 6}(2\\beta)$", "#FEF3C7"),
        (0.88, 0.95, "Measurement\nComputational Basis", "#F1F5F9"),
    ]
    for x1, x2, label, col in stages:
        rect = patches.Rectangle((x1, 0.05), x2 - x1, 0.82, facecolor=col, alpha=0.5, edgecolor=BOX_BORDER, lw=0.8, zorder=0)
        ax.add_patch(rect)
        ax.text((x1 + x2) / 2.0, 0.08, label, fontsize=8, ha="center", color=TEXT_DARK, weight="bold")

    # 1. Hadamard gates
    for y in qubit_y:
        box = patches.FancyBboxPatch((0.10, y - 0.035), 0.04, 0.07, boxstyle="round,pad=0.005",
                                     facecolor="#FFFFFF", edgecolor=STEEL_BLUE, lw=1.4, zorder=3)
        ax.add_patch(box)
        ax.text(0.12, y, "H", ha="center", va="center", fontsize=9, weight="bold", color=STEEL_BLUE_DARK, zorder=4)

    # 2. R_ZZ Cost Unitary representations
    # Problem edges: (0,2:1), (0,3:4), (0,4:4), (1,4:3), (1,5:3), (2,3:5), (2,4:1), (3,4:4), (3,5:2)
    # Draw representative R_ZZ blocks
    edges = [
        (0, 2, 1, 0.26),
        (0, 3, 4, 0.31),
        (0, 4, 4, 0.36),
        (1, 4, 3, 0.41),
        (1, 5, 3, 0.46),
        (2, 3, 5, 0.51),
        (2, 4, 1, 0.56),
        (3, 4, 4, 0.61),
        (3, 5, 2, 0.66),
    ]
    for u, v, w, x in edges:
        yu, yv = qubit_y[u], qubit_y[v]
        # Connecting vertical interaction line
        ax.plot([x, x], [yu, yv], color=STEEL_BLUE, lw=1.6, zorder=2)
        # Control & target dots
        ax.scatter([x, x], [yu, yv], color=STEEL_BLUE_DARK, s=40, zorder=3)
        # R_ZZ block in the middle
        ymid = (yu + yv) / 2.0
        rbox = patches.FancyBboxPatch((x - 0.018, ymid - 0.025), 0.036, 0.05, boxstyle="round,pad=0.003",
                                      facecolor="#FFFFFF", edgecolor=STEEL_BLUE_DARK, lw=1.2, zorder=4)
        ax.add_patch(rbox)
        ax.text(x, ymid, f"$R_{{zz}}$\n{w}$\\gamma$", ha="center", va="center", fontsize=6.8, weight="bold", color=TEXT_DARK, zorder=5)

    # 3. Mixer R_X gates
    for y in qubit_y:
        rx_box = patches.FancyBboxPatch((0.76, y - 0.035), 0.06, 0.07, boxstyle="round,pad=0.005",
                                        facecolor="#FFFFFF", edgecolor=BRONZE_DARK, lw=1.4, zorder=3)
        ax.add_patch(rx_box)
        ax.text(0.79, y, "$R_X(2\\beta)$", ha="center", va="center", fontsize=7.5, weight="bold", color=BRONZE_DARK, zorder=4)

    # 4. Measurement meters
    for y in qubit_y:
        mbox = patches.FancyBboxPatch((0.89, y - 0.035), 0.04, 0.07, boxstyle="round,pad=0.005",
                                      facecolor="#FFFFFF", edgecolor=TEXT_MUTED, lw=1.2, zorder=3)
        ax.add_patch(mbox)
        ax.text(0.91, y, "M", ha="center", va="center", fontsize=8.5, weight="bold", color=TEXT_DARK, zorder=4)

    ax.set_xlim(0.00, 1.02)
    ax.set_ylim(0.00, 1.00)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "05_qaoa_p1_circuit.png", dpi=300)
    fig.savefig(FIGURES_DIR / "05_qaoa_p1_circuit.svg")
    plt.close(fig)

# ==============================================================================
# Figure 06: Hardware Mapping & Resource Comparison
# ==============================================================================
def generate_figure_06():
    print("Generating Figure 06: Hardware Mapping Comparison...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), facecolor=BG_COLOR)
    for ax in (ax1, ax2):
        ax.set_facecolor(BG_COLOR)
        
    fig.suptitle("Figure 06: Cross-Processor Resource & Empirical Quality Comparison (Processors B vs D)\n"
                 "Hardware Routing Advantage vs. Statistically Indistinguishable Solution Quality Under Noisy Simulation",
                 fontsize=11.5, weight="bold", color=TEXT_DARK, y=0.98)

    # Panel A: Circuit Compilation Resources
    categories = ["SWAP Gates", "CX Gate Count", "Circuit Depth", "Two-Qubit Depth"]
    proc_b_res = [1, 21, 37, 17]
    proc_d_res = [0, 18, 29, 14]
    
    x = np.arange(len(categories))
    width = 0.32
    
    rects1 = ax1.bar(x - width/2, proc_b_res, width, label="Processor B (9Q)", color=STEEL_BLUE, edgecolor=STEEL_BLUE_DARK, lw=1.2)
    rects2 = ax1.bar(x + width/2, proc_d_res, width, label="Processor D (9Q Co-Design)", color=BRONZE, edgecolor=BRONZE_DARK, lw=1.2)
    
    # Annotate percent reductions
    reductions = ["-100% (Zero SWAP)", "-14.3% (18 vs 21)", "-21.6% (29 vs 37)", "-17.6% (14 vs 17)"]
    for i, rect in enumerate(rects2):
        h = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width()/2.0, h + 0.8, reductions[i],
                 ha="center", va="bottom", fontsize=7.5, weight="bold", color=BRONZE_DARK)

    ax1.set_ylabel("Compiled Circuit Resource Quantity", fontsize=9.5, weight="bold", color=TEXT_DARK)
    ax1.set_title("A. Physical Transpilation Metrics (SABRE Opt-Level 1)", fontsize=10, weight="bold", color=TEXT_DARK)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=9, weight="bold")
    ax1.set_ylim(0, 44)
    ax1.grid(axis="y", linestyle=":", color="#E2E8F0", alpha=0.8)
    ax1.legend(frameon=True, facecolor=BOX_BG, edgecolor=BOX_BORDER, fontsize=8.5)

    # Panel B: Measured Solution Quality (with standard errors)
    metrics = ["Sampled Cut $\\langle C \\rangle$", "Approx. Ratio $r$", "Optimal Prob. $P_{\\text{opt}}$ (%)"]
    
    # Normalized for side-by-side display:
    # Processor B: Cut = 17.3220 +- 0.0598, r = 0.7874 +- 0.0027, P_opt = 12.60% +- 0.52%
    # Processor D: Cut = 17.2971 +- 0.0612, r = 0.7862 +- 0.0028, P_opt = 12.50% +- 0.52%
    b_vals = [17.3220, 0.7874 * 20, 12.60]  # scale r to visually align
    b_errs = [0.0598, 0.0027 * 20, 0.52]
    d_vals = [17.2971, 0.7862 * 20, 12.50]
    d_errs = [0.0612, 0.0028 * 20, 0.52]

    x2 = np.arange(len(metrics))
    ax2.bar(x2 - width/2, [17.3220, 0.7874, 12.60], width, yerr=[0.0598, 0.0027, 0.52],
            capsize=4, label="Processor B (Noisy 4096 Shots)", color=STEEL_BLUE, edgecolor=STEEL_BLUE_DARK, lw=1.2)
    ax2.bar(x2 + width/2, [17.2971, 0.7862, 12.50], width, yerr=[0.0612, 0.0028, 0.52],
            capsize=4, label="Processor D (Noisy 4096 Shots)", color=BRONZE, edgecolor=BRONZE_DARK, lw=1.2)

    ax2.set_ylabel("Empirical Benchmark Value (4096 Shots)", fontsize=9.5, weight="bold", color=TEXT_DARK)
    ax2.set_title("B. Solution Quality Under Noisy Simulation", fontsize=10, weight="bold", color=TEXT_DARK)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(["Mean Cut $\\langle C \\rangle$\n($C^*=22$)", "Approx Ratio $r$\n(Random = 0.614)", "$P_{\\text{opt}}$ (%)\n(Random = 3.125%)"],
                        fontsize=8.5, weight="bold")
    ax2.set_ylim(0, 24)
    ax2.grid(axis="y", linestyle=":", color="#E2E8F0", alpha=0.8)
    ax2.legend(frameon=True, facecolor=BOX_BG, edgecolor=BOX_BORDER, fontsize=8.5)

    # Scientific Note
    fig.text(0.5, 0.02,
             "Scientific Rigor Note: Hypothesis test between noisy B and D gives $z = 0.291\\sigma$ ($p = 0.7711$). Mean cuts are statistically indistinguishable;\n"
             "Processor D's verified advantage is physical resource efficiency (eliminating 100% of routing SWAPs and saving 14.3% CX gates).",
             ha="center", fontsize=8.2, color=TEXT_MUTED, style="italic")

    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    fig.savefig(FIGURES_DIR / "06_hardware_mapping_comparison.png", dpi=300)
    fig.savefig(FIGURES_DIR / "06_hardware_mapping_comparison.svg")
    plt.close(fig)

# ==============================================================================
# Figure 07: Bell-State Measurement Workflow
# ==============================================================================
def generate_figure_07():
    print("Generating Figure 07: Bell State Measurement Workflow...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.2), facecolor=BG_COLOR)
    for ax in (ax1, ax2):
        ax.set_facecolor(BG_COLOR)
        
    fig.suptitle("Figure 07: Objective 1 Bell-State Tomography Protocol & Routing Decoherence Penalty\n"
                 "Verification of Maximally Entangled State $|\\Phi^+\\rangle$ on Native ($d=1$) vs. Distant ($d=4$) Pairs on Processor D",
                 fontsize=11.5, weight="bold", color=TEXT_DARK, y=0.98)

    # Subplot A: Schematic Flowchart of Tomography Experiment
    ax1.axis("off")
    ax1.set_title("A. State Tomography Experimental Workflow", fontsize=10, weight="bold", color=TEXT_DARK, pad=8)
    
    workflow_steps = [
        (0.05, 0.76, 0.90, 0.16, "1. Bell State Generation",
         "• State: $|\\Phi^+\\rangle = \\frac{|00\\rangle + |11\\rangle}{\\sqrt{2}}$ prepared via $H \\to CX$\n"
         "• Evaluated across 2 representative physical pairs on Processor D:\n"
         "  - Near pair $(0, 2)$: Native neighbor (distance $d=1$, 1 direct CX)\n"
         "  - Far pair $(0, 7)$: Distant pair (distance $d=4$, 10 CX gates via multi-hop routing)"),
        
        (0.05, 0.44, 0.90, 0.26, "2. Tomography Measurement Bases & Parity",
         "• $XX$ Basis: Apply $H \\otimes H \\to$ Measure in $Z$ basis $\\to \\langle XX \\rangle = P(\\text{even}) - P(\\text{odd})$\n"
         "• $YY$ Basis: Apply $S^\\dagger H \\otimes S^\\dagger H \\to$ Measure in $Z$ basis $\\to \\langle YY \\rangle = P(\\text{even}) - P(\\text{odd})$\n"
         "• $ZZ$ Basis: Direct measurement in $Z$ basis $\\to \\langle ZZ \\rangle = P(\\text{even}) - P(\\text{odd})$\n"
         "• Execution: 4096 shots/basis on Qiskit Aer with official depolarizing + readout noise\n"
         "• Complete circuit suite: 12 individual measurement circuits"),
        
        (0.05, 0.12, 0.90, 0.26, "3. Fidelity Evaluation Formula",
         "• State Fidelity to theoretical target $|\\Phi^+\\rangle$:\n"
         "  $\\mathcal{F} = \\langle \\Phi^+ | \\rho | \\Phi^+ \\rangle = \\frac{1 + \\langle XX \\rangle - \\langle YY \\rangle + \\langle ZZ \\rangle}{4}$\n"
         "• Standard Error Propagation:\n"
         "  $\\text{SE}_{\\mathcal{F}} = \\frac{1}{4} \\sqrt{\\text{Var}(\\langle XX \\rangle) + \\text{Var}(\\langle YY \\rangle) + \\text{Var}(\\langle ZZ \\rangle)}$\n"
         "• Theoretical Ideal: $\\mathcal{F} = 1.0000$ (with $\\langle XX \\rangle = +1, \\langle YY \\rangle = -1, \\langle ZZ \\rangle = +1$)"),
    ]
    for x, y, w, h, title, text in workflow_steps:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015",
                                      facecolor=BOX_BG, edgecolor=STEEL_BLUE_DARK, lw=1.2)
        ax1.add_patch(rect)
        ax1.text(x + 0.02, y + h - 0.04, title, fontsize=9, weight="bold", color=STEEL_BLUE_DARK)
        ax1.text(x + 0.02, y + h - 0.075, text, fontsize=7.8, color=TEXT_DARK, va="top", linespacing=1.3)

    # Subplot B: Measured Correlators & Fidelity Degradation
    ax2.set_title("B. Measured Correlators & Routing Degradation", fontsize=10, weight="bold", color=TEXT_DARK, pad=8)
    
    bases = ["$\\langle XX \\rangle$", "$-\\langle YY \\rangle$", "$\\langle ZZ \\rangle$", "Fidelity $\\mathcal{F}$"]
    near_vals = [0.9458, 0.9521, 0.9551, 0.9633]
    near_errs = [0.0051, 0.0048, 0.0046, 0.0021]
    
    far_vals = [0.9243, 0.9038, 0.9399, 0.9420]
    far_errs = [0.0060, 0.0067, 0.0053, 0.0026]

    x = np.arange(len(bases))
    width = 0.35
    
    ax2.bar(x - width/2, near_vals, width, yerr=near_errs, capsize=4,
            label="Near Pair (0, 2) [d=1, 1 CX]", color=STEEL_BLUE, edgecolor=STEEL_BLUE_DARK, lw=1.2)
    ax2.bar(x + width/2, far_vals, width, yerr=far_errs, capsize=4,
            label="Far Pair (0, 7) [d=4, 10 CX]", color=BRONZE, edgecolor=BRONZE_DARK, lw=1.2)

    # Annotate fidelity drop
    delta_f = 0.9633 - 0.9420
    ax2.annotate(f"$\\Delta \\mathcal{{F}} = -{delta_f:.4f}$\n($6.37\\sigma$ penalty)",
                 xy=(3 + width/2, 0.9420), xytext=(2.4, 0.88),
                 arrowprops=dict(arrowstyle="->", color=ERROR_RED, lw=1.5),
                 fontsize=8.5, weight="bold", color=ERROR_RED,
                 bbox=dict(boxstyle="round,pad=0.2", facecolor="#FEF2F2", edgecolor=ERROR_RED, lw=0.8))

    ax2.set_ylabel("Expectation / Fidelity Value", fontsize=9.5, weight="bold", color=TEXT_DARK)
    ax2.set_xticks(x)
    ax2.set_xticklabels(bases, fontsize=9, weight="bold")
    ax2.set_ylim(0.85, 1.02)
    ax2.grid(axis="y", linestyle=":", color="#E2E8F0", alpha=0.8)
    ax2.legend(loc="lower left", frameon=True, facecolor=BOX_BG, edgecolor=BOX_BORDER, fontsize=8.5)

    fig.text(0.5, 0.02,
             "Hardware Implication: Multi-hop routing across 4 lattice hops introduces 9 additional CX gates, incurring a verified $6.37\\sigma$ fidelity penalty.\n"
             "This quantitatively demonstrates why Processor D's zero-SWAP native embedding is vital on NISQ systems. Simulated via Qiskit Aer.",
             ha="center", fontsize=8.2, color=TEXT_MUTED, style="italic")

    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    fig.savefig(FIGURES_DIR / "07_bell_state_measurement_workflow.png", dpi=300)
    fig.savefig(FIGURES_DIR / "07_bell_state_measurement_workflow.svg")
    plt.close(fig)

def main():
    print("=================================================================")
    print("  PROJECT VARANASI — SUPPLEMENTARY SCIENTIFIC FIGURES GENERATOR")
    print("=================================================================")
    print(f"Target directory: {FIGURES_DIR}")
    
    generate_figure_01()
    generate_figure_02()
    generate_figure_03()
    generate_figure_04()
    generate_figure_05()
    generate_figure_06()
    generate_figure_07()
    
    # Verification
    expected = [
        "01_weighted_network_3d",
        "02_classical_optimization_workflow",
        "03_hybrid_qaoa_architecture",
        "04_processor_topologies",
        "05_qaoa_p1_circuit",
        "06_hardware_mapping_comparison",
        "07_bell_state_measurement_workflow",
    ]
    missing = []
    for base in expected:
        png_p = FIGURES_DIR / f"{base}.png"
        svg_p = FIGURES_DIR / f"{base}.svg"
        if not png_p.exists() or png_p.stat().st_size == 0:
            missing.append(f"{base}.png")
        if not svg_p.exists() or svg_p.stat().st_size == 0:
            missing.append(f"{base}.svg")
            
    if missing:
        print(f"ERROR: Missing or empty files: {missing}")
        sys.exit(1)
        
    print("=================================================================")
    print(f"  SUCCESS: All 14 files (7 PNG + 7 SVG) verified in {FIGURES_DIR}")
    print("=================================================================")

if __name__ == "__main__":
    main()
