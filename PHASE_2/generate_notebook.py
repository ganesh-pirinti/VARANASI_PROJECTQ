"""
generate_notebook.py — Generates clean, top-to-bottom executable main.ipynb
"""

import nbformat as nbf

def build_notebook(path: str = "main.ipynb"):
    nb = nbf.v4.new_notebook()

    # Markdown: Header
    c0 = r"""# QFF 2026 Phase 2 — Quantum Optimization Track
## PS-O1: Quantum Optimization of Network Partitioning Using QAOA
**Problem Statement:** PS-O1 (Max-Cut on a 6-Vertex Graph Motivated by 5G Network Partitioning)  
**Team Identifier:** `QFF2026_RESEARCH_TEAM` (*Pending Phase 1 Official Registration Confirmation*)  
**Execution Environment:** Python 3.11 | Qiskit 2.6.1 | Qiskit Aer 0.18.2  
**Simulation Notice:** Classical simulation via Qiskit Aer (`AerSimulator`) with realistic depolarizing and readout noise; no physical QPU hardware used.  
**Ground Truth:** Exact Classical Optimum $C^* = 22$ | Uniform Random Baseline $r = 0.6136$  

---
### Notebook Outline
1. **Environment & Verification:** Check Qiskit, Aer, basis gates, and noise settings.
2. **Problem Definition & Formulation:** Locked 6-vertex, 9-edge weighted graph ($W=27$) and QUBO derivation.
3. **Classical Ground Truth:** Exhaustive enumeration over all $2^6=64$ bitstrings establishing $C^* = 22$.
4. **Objective 1 (Bell-State Tomography on Processor D):** Verification of $|\Phi^+\rangle$ state on adjacent ($d=1$) and distant ($d=4$) physical pairs.
5. **Objective 2 (Processor D Architecture):** Official validation and bottleneck resolution over Processor B.
6. **Objective 3 (QAOA Multi-Restart Optimization & Benchmarking):** Mandatory seeds $[0, 1, 2, 3, 4]$ and cross-processor evaluation (A, B, D).
7. **Results & Scientific Figures:** Rendered tables and publication-grade visualizations.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(c0))

    # Code: Environment Verification
    c1 = """# Section 1: Environment Verification
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Image
import qiskit
from qiskit import QuantumCircuit
import qiskit_aer

import qff_phase2
from qff_phase2 import (
    BASIS_GATES,
    OPT_LEVEL,
    SEED,
    SHOTS,
    P1_DEPOL,
    P2_DEPOL,
    P_READOUT,
    PROCESSOR_A,
    PROCESSOR_B,
    load_processor,
    validate_processor_d,
    circuit_metrics,
    transpile_for,
    simulator,
    counts_to_x,
)

print(f"Python Version:     {sys.version.split()[0]}")
print(f"Qiskit Version:     {qiskit.__version__}")
print(f"Qiskit Aer Version: {qiskit_aer.__version__}")
print(f"Basis Gates:        {BASIS_GATES}")
print(f"Transpiler Opt:     Level {OPT_LEVEL} (SABRE, Seed {SEED})")
print(f"Official Noise:     p1={P1_DEPOL}, p2={P2_DEPOL}, p_readout={P_READOUT}")
"""
    nb.cells.append(nbf.v4.new_code_cell(c1))

    # Markdown: Problem Model
    c2 = """# Section 2: Problem Definition, QUBO & Classical Ground Truth
The Max-Cut objective for graph $G=(V, E, w)$ is:
$$C(x) = \\sum_{(u,v) \\in E} w_{uv} (x_u + x_v - 2 x_u x_v)$$
Minimizing $-C(x)$ defines the QUBO form: $x^T Q x$.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(c2))

    # Code: Classical Baseline
    c3 = """# Section 3: Exhaustive Classical Ground Truth Enumeration
from src.problem_model import LOCKED_EDGES, NUM_VERTICES, TOTAL_WEIGHT
from src.classical_baseline import solve_exhaustive

classical_res = solve_exhaustive(LOCKED_EDGES)
print("=== EXACT CLASSICAL GROUND TRUTH ===")
print(f"Vertices:               {NUM_VERTICES}")
print(f"Edges:                  {len(LOCKED_EDGES)} (Total Weight W = {TOTAL_WEIGHT})")
print(f"Exact Maximum Cut C*:   {classical_res['max_cut']}")
print(f"Optimal Assignments:    {classical_res['optimal_assignments']}")
print(f"Optimal Bitstrings:     {classical_res['optimal_bitstrings']}")
print(f"Uniform Random Cut:     {classical_res['random_mean_cut']:.4f} (AR = {classical_res['random_approx_ratio']:.4f})")
print(f"Random P_opt:           {classical_res['random_p_opt']:.4f} ({classical_res['optimal_count']}/64)")

display(Image(filename="results/figures/network_partitioning_graph.png"))
"""
    nb.cells.append(nbf.v4.new_code_cell(c3))

    # Markdown: Objective 1 Bell States
    c4 = """# Section 4: Objective 1 — Bell-State Preparation and Tomography
We prepare $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\\sqrt{2}$ on Processor D:
- **Adjacent physical pair:** $(0, 2)$ at shortest-path distance $d=1$ (1 CX)
- **Maximally separated pair:** $(0, 7)$ at shortest-path distance $d=4$ (10 CX via ancillary ring)
Evaluated across XX, YY, ZZ bases (4096 shots/basis) under ideal and official noisy simulation.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(c4))

    # Code: Bell States
    c5 = """# Section 4.1: Bell-State Tomography Execution & Data Display
from src.bell_verification import run_bell_verification

bell_results = run_bell_verification(
    processor_path="processors/processor_D.json",
    near_pair=(0, 2),
    far_pair=(0, 7),
    output_csv_path="results/tables/bell.csv",
    output_circuits_csv="results/tables/bell_circuits.csv",
    output_raw_counts="results/raw/bell_counts.json",
)

df_bell = pd.read_csv("results/tables/bell.csv")
print("=== Bell State Verification Summary (results/tables/bell.csv) ===")
display(df_bell[["pair_type", "qubit_pair", "pair_distance", "condition", "cx_count", "exp_XX", "exp_YY", "exp_ZZ", "fidelity", "fidelity_se"]])

df_bell_circuits = pd.read_csv("results/tables/bell_circuits.csv")
print("\\n=== All 12 Bell Measurement Circuits (results/tables/bell_circuits.csv) ===")
display(df_bell_circuits)

display(Image(filename="results/figures/bell_fidelity_comparison.png"))
"""
    nb.cells.append(nbf.v4.new_code_cell(c5))

    # Markdown: Objective 2 Processor D Design
    c6 = """# Section 5: Objective 2 — Processor D Co-Design & Rule Verification
Processor D embeds the 6-vertex PS-O1 graph on qubits 0–5 and connects an ancillary routing ring (qubits 5–8, 1) of degree $\\le 4$.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(c6))

    # Code: Processor D Check
    c7 = """# Section 5.1: Processor D Validation
proc_d = load_processor("processors/processor_D.json")
errs = validate_processor_d(proc_d, required_qubits=6)
print(f"Processor D Rule Validation: {'PASS (0 violations)' if not errs else errs}")
print(f"Num Qubits:      {proc_d['num_qubits']}")
print(f"Num Edges:       {len(proc_d['edges'])}")
print(f"Basis Gates:     {proc_d['basis_gates']}")
print(f"Noise Settings:  {proc_d['noise']}")

display(Image(filename="results/figures/processor_topologies.png"))
"""
    nb.cells.append(nbf.v4.new_code_cell(c7))

    # Markdown: Objective 3 Benchmarking
    c8 = """# Section 6: Objective 3 — QAOA Parameter Optimization & Cross-Processor Benchmarking
QAOA ($p=1$) is optimized across mandatory initialization seeds $[0, 1, 2, 3, 4]$ using COBYLA on exact statevector expectation.
Cross-processor sampling ($4096$ shots) is conducted on Processors A, B, and D.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(c8))

    # Code: QAOA Optimization & Benchmarks
    c9 = """# Section 6.1: Cross-Processor Benchmark Execution
from src.benchmarking import run_benchmarks

bench_data = run_benchmarks(
    processor_d_path="processors/processor_D.json",
    results_csv_path="results/tables/results.csv",
    opt_runs_csv_path="results/tables/optimization_runs.csv",
    proc_metrics_csv_path="results/tables/processor_metrics.csv",
    raw_counts_path="results/raw/qaoa_counts.json",
)

df_opt = pd.read_csv("results/tables/optimization_runs.csv")
print("=== QAOA Multi-Restart Parameter Optimization (seeds 0..4) ===")
display(df_opt)

df_results = pd.read_csv("results/tables/results.csv")
print("\\n=== Cross-Processor Benchmark Comparison (results/tables/results.csv) ===")
display(df_results)
"""
    nb.cells.append(nbf.v4.new_code_cell(c9))

    # Code: Figures Display
    c10 = """# Section 7: Scientific Visualizations
print("=== Circuit Resource Comparison: B vs D ===")
display(Image(filename="results/figures/processor_resource_comparison.png"))

print("=== QAOA Sampled Cut Weight Distribution ===")
display(Image(filename="results/figures/qaoa_cut_distribution.png"))

print("=== QAOA Parameter Energy Landscape ===")
display(Image(filename="results/figures/qaoa_parameter_landscape.png"))

print("=== Architecture Trade-Off Map ===")
display(Image(filename="results/figures/architecture_tradeoff_map.png"))
"""
    nb.cells.append(nbf.v4.new_code_cell(c10))

    # Markdown: Discussion
    c11 = """# Section 8: Scientific Analysis, Trade-Offs & Conclusion

### 8.1 Key Findings & Discussion
1. **Processor A Infeasibility:** Correctly identified as not executable ($5 < 6$ qubits).
2. **SWAP Overhead Elimination:** Processor B incurs 1 SWAP (+3 CX gates, 16.7% two-qubit overhead), while Processor D achieves **0 SWAPs** and **0 CX overhead**, compressing depth from 37 to 29 (-21.6%) and two-qubit depth from 17 to 14 (-17.6%).
3. **Noisy Solution Quality & Statistical Comparability:** Under official noise ($p_1=0.001, p_2=0.005, p_{\\text{readout}}=0.01$), Processor B achieves sampled mean cut $\\langle C \\rangle = 17.3220 \\pm 0.0598$ ($r = 0.7874 \\pm 0.0027$) and Processor D yields $\\langle C \\rangle = 17.2971 \\pm 0.0612$ ($r = 0.7862 \\pm 0.0028$). The difference $\\Delta \\langle C \\rangle = 0.0249 \\pm 0.0856 \\implies \\Delta r = 0.0011 \\pm 0.0039$ ($z = 0.2910\\sigma, p = 0.7711$) indicates that the sampled mean cuts are statistically indistinguishable under 4096 shots. Importantly, this equivalence in sampled mean does not imply that the full 64-element output probability distributions are identical. Both provide a $4.0\\times$ probability enhancement of sampling the optimal partition ($12.5\\%$ vs. $3.125\\%$). Processor D's zero-SWAP compilation represents future architectural potential if scaled to higher depths ($p \\ge 2$).
4. **Bell-State Tomography:** Fidelity drops from $0.9633 \\pm 0.0021$ on adjacent physical pair $(0, 2)$ to $0.9420 \\pm 0.0026$ on distant pair $(0, 7)$ ($d=4$, 10 CX gates), validating simulated two-qubit routing error accumulation at $6.37\\sigma$ significance.

### 8.2 Reproducibility & Integrity
All experiments are reproducible deterministically using `scripts/run_all.py` and validated by automated pytest suites.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(c11))

    nb.metadata.kernelspec = {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3"
    }
    nb.metadata.language_info = {
        "name": "python",
        "version": "3.11.9"
    }

    with open(path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"{path} successfully created!")

if __name__ == "__main__":
    build_notebook()
