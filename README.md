# VARANASI — Qiskit Fall Fest 2026 (Phase 2)
## Problem Statement PS-O1: Quantum Optimization of Network Partitioning Using QAOA

---
### Team & Submission Metadata
- **Team Name:** `VARANASI`
- **Participant / Team ID:** `AP251100708044`
- **Team Leader:** Ganesh Pirinti (SRM University-AP, Andhra Pradesh | `ganeshpirinti95218@gmail.com`)
- **Team Member:** Mohammed Sadiq (SRM University-AP, Andhra Pradesh | `sadiqmohammedkhan12@gmail.com`)
- **Host Institution:** SRM University-AP | Hackathon & Competitions Cell
- **Track & Stage:** Optimization Track — Phase 2 Final Submission
- **Problem Statement Code:** `PS-O1` (Quantum Optimization of Network Partitioning Using QAOA)
- **GitHub Repository URL:** [https://github.com/ganesh-pirinti/VARANASI_PROJECTQ](https://github.com/ganesh-pirinti/VARANASI_PROJECTQ)

---

## Project Overview

This repository contains the verified Phase 2 solution for **PS-O1: Network Partitioning Using QAOA**. Using the locked six-vertex, nine-edge graph ($W = 27$) from `instances.json`, we formulate the maximum cut problem as a Quadratic Unconstrained Binary Optimization (QUBO) model and execute QAOA ($p=1$) with multi-restart classical parameter optimization (seeds $0, 1, 2, 3, 4$). 

We evaluate performance against the exact classical ground truth ($C^* = 22$) and the uniform random baseline ($r_{\text{random}} = 0.6136, P_{\text{opt, random}} = 0.03125$), benchmarking across reference **Processor A** (5 qubits), **Processor B** (9 qubits), and our co-designed **Processor D** (9 qubits).

> **Judge & Evaluator Quick Reference:** See [docs/JUDGE_GUIDE.md](docs/JUDGE_GUIDE.md) for a 30-second technical overview, verified benchmarks, and evidence-backed answers to 14 judge defense questions.

---

## Key Benchmark Results

### 1. Cross-Processor QAOA Performance (`results/tables/results.csv`)

| Problem ID | Processor | Condition | Executable | Logical CX | CX | Depth | 2Q Depth | SWAPs | CX Overhead | Quality Metric | Quality Value ($r$) | $P_{\text{opt}}$ | Classical $C^*$ | Random Baseline ($r$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **PS-O1** | **A** | Ideal | `false` | 18 | — | — | — | — | — | `approx_ratio` | — | — | 22 | 0.6136 |
| **PS-O1** | **A** | Noisy | `false` | 18 | — | — | — | — | — | `approx_ratio` | — | — | 22 | 0.6136 |
| **PS-O1** | **B** | Ideal | `true` | 18 | 21 | 37 | 17 | 1 | +3 | `approx_ratio` | 0.8074 | 0.1396 | 22 | 0.6136 |
| **PS-O1** | **B** | Noisy | `true` | 18 | 21 | 37 | 17 | 1 | +3 | `approx_ratio` | 0.7874 | 0.1260 | 22 | 0.6136 |
| **PS-O1** | **D** | Ideal | `true` | 18 | **18** | **29** | **14** | **0** | **0** | `approx_ratio` | 0.8052 | 0.1384 | 22 | 0.6136 |
| **PS-O1** | **D** | Noisy | `true` | 18 | **18** | **29** | **14** | **0** | **0** | `approx_ratio` | 0.7862 | 0.1250 | 22 | 0.6136 |

> **Key Finding:** Processor D completely eliminates Processor B's SWAP routing bottleneck (0 SWAPs vs 1 SWAP, 0 CX overhead), compressing two-qubit depth by 17.6% (14 vs 17) and total depth by 21.6% (29 vs 37). On Processor D under official noise, QAOA samples the optimal cut ($C^*=22$) with $P_{\text{opt}} = 12.50\%$, achieving a **$4.0\times$ enhancement in optimal-solution sampling probability** over uniform random guessing ($3.125\%$). Mean solution quality remains numerically similar in these simulated runs ($r = 0.7862$ on D vs. $0.7874$ on B, a delta of -0.0012 or -0.15% relative), with D providing a significant reduction in compiled circuit resources (0 SWAPs, -14.29% physical CX, -17.65% two-qubit depth).

---

### 2. Objective 1: Bell-State Verification on Processor D (`results/tables/bell.csv`)

| Pair Type | Physical Pair | Graph Distance | Condition | CX Count | $\langle XX \rangle \pm \text{SE}$ | $\langle YY \rangle \pm \text{SE}$ | $\langle ZZ \rangle \pm \text{SE}$ | Fidelity $F \pm \text{SE}$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Near** | $(0, 2)$ | 1 | Ideal | 1 | $+1.0000 \pm 0.0000$ | $-1.0000 \pm 0.0000$ | $+1.0000 \pm 0.0000$ | **$1.0000 \pm 0.0000$** |
| **Near** | $(0, 2)$ | 1 | Noisy | 1 | $+0.9458 \pm 0.0051$ | $-0.9521 \pm 0.0048$ | $+0.9551 \pm 0.0046$ | **$0.9633 \pm 0.0021$** |
| **Far** | $(0, 7)$ | 4 | Ideal | 10 | $+1.0000 \pm 0.0000$ | $-1.0000 \pm 0.0000$ | $+1.0000 \pm 0.0000$ | **$1.0000 \pm 0.0000$** |
| **Far** | $(0, 7)$ | 4 | Noisy | 10 | $+0.9243 \pm 0.0060$ | $-0.9038 \pm 0.0067$ | $+0.9399 \pm 0.0053$ | **$0.9420 \pm 0.0026$** |

---

## Processor D Architecture Co-Design

- **File:** `processors/processor_D.json`
- **Validation:** Passes `validate_processor_d(D, required_qubits=6)` with **0 rule violations**.
- **Qubit Count:** 9 physical qubits (well within the $\le 12$ rule).
- **Maximum Degree:** Exactly 4 (nodes 3 and 4 have degree 4; nodes 0, 1, 2, 5 have degree 3; nodes 6, 7, 8 have degree 2). Strictly satisfies the degree $\le 4$ constraint.
- **Topology:** The 9 interaction edges of PS-O1 are natively embedded in computational qubits $0..5$, with a closed ancillary routing ring on qubits $6..8$ connected via $(5, 6), (6, 7), (7, 8), (8, 1)$.
- **Gate Set & Noise Floor:** Locked to `["rz", "sx", "x", "cx"]` and official noise rates ($p_1=0.001, p_2=0.005, p_{\text{readout}}=0.01$).

---

## Selected Real-World Applications

While our core submission strictly addresses the locked **PS-O1: Quantum Optimization of Network Partitioning Using QAOA** benchmark, the underlying graph partitioning and QUBO formulations map directly to foundational optimization problems in telecommunications and computer networking:

### 1. Interference-Aware Channel Assignment (5G/6G Frequency Planning)
- **Real-World Problem:** In dense 5G/6G cellular deployments, adjacent cell towers sharing identical frequency carriers create severe co-channel interference, degrading user Signal-to-Interference-plus-Noise Ratio (SINR), precipitating call drops, and constraining throughput. Network operations require dynamic frequency reallocation across clusters as traffic distributions evolve.
- **Quantum Mapping:** Neighboring cell towers are modeled as vertices in an interference graph $G = (V, E)$, where weighted edges $w_{uv}$ denote the co-channel interference penalty incurred if two towers are assigned the same channel. For a two-channel frequency allocation, maximizing inter-channel isolation maps identically to the Max-Cut objective:
  $$\max_{x \in \{0, 1\}^n} \sum_{(u, v) \in E} w_{uv} (x_u + x_v - 2 x_u x_v)$$
  where binary decision variable $x_i \in \{0, 1\}$ assigns cell $i$ to Frequency Band $A$ ($x_i = 1$) or Band $B$ ($x_i = 0$). Edges intersected by the partition cut connect neighboring cells operating on mutually orthogonal channels.
- **Why It Fits VARANASI:** The locked 6-vertex PS-O1 instance directly provides a two-channel frequency assignment model for a 6-cell cluster without modifying the official competition problem. *(Note: This demonstrates the conceptual domain mapping of our abstract Max-Cut formulation; production-grade radio frequency planning requires multi-channel chromatic coloring with $K > 2$ and dynamic power control).*
- **Mathematical Metrics & Physical Interpretation:**
  - **Exact Optimum Cut Weight ($C^*$):** $C^* = 22$ (maximum achievable cut weight out of total graph weight $W = 27$).
  - **Approximation Ratio ($r$):** Defined as achieved cut weight divided by exact optimum ($C / C^*$). For the optimal partition, $r_{\text{best}} = 22/22 = 1.0000$ ($100.00\%$). Under official noisy simulation on Processor D, the mean sampled cut weight is $\langle C \rangle = 17.297$, achieving a mean approximation ratio of $r = 0.7862$ ($78.62\%$).
  - **Fraction of Total Edge Weight Cut:** $C^* / W = 22 / 27 \approx 81.48\%$. In the interference mapping, this corresponds to assigning $81.48\%$ of the total potential co-channel interference weight between cells onto orthogonal channels, leaving $5/27 \approx 18.52\%$ residual co-channel interference on internal uncut links: $(0, 3)$ with weight 4 and $(2, 4)$ with weight 1. *(Note: This is the theoretical weighted fraction of the benchmark graph crossing the optimal cut, not an empirical measurement of physical radio interference).*
  - **Fraction of Edge Count Cut:** $7 / 9 \approx 77.78\%$ (7 of the 9 interference edges are cut).
- **Demonstration Status (Directly Supported by Repository Results):** In our 4096-shot noisy simulation on Processor D, the two optimal complementary partitions—logical vector $x = (1, 1, 0, 1, 0, 0)$ ($S=\{0, 1, 3\}, \bar{S}=\{2, 4, 5\}$, Qiskit little-endian bitstring `001011`) and $x = (0, 0, 1, 0, 1, 1)$ ($S=\{2, 4, 5\}, \bar{S}=\{0, 1, 3\}$, Qiskit little-endian bitstring `110100`)—are the two highest-probability states sampled (254 and 258 counts respectively, 512 total), combining for $P_{\text{opt}} = 12.50\%$ ($4.0\times$ the uniform random baseline of $3.125\%$). The partition cut is directly visualized in `results/figures/network_partitioning_graph.png`.

### 2. Traffic Engineering (Load-Balanced Routing)
- **Real-World Problem:** Telecommunications transport and data-center networks route high-volume traffic flows across capacity-constrained links. Inefficient routing leads to link saturation, buffer queue build-up, latency spikes, and packet loss while alternate parallel links remain underutilized.
- **Quantum Mapping (Simplified Two-Path Load Balancing):** The formulation models the simplified problem of balancing scalar traffic demands across two parallel paths (equivalent to binary number partitioning). For a set of traffic demands $d_k$ partitioned across two redundant paths, binary decision variables $y_k \in \{0, 1\}$ minimize the squared link load differential:
  $$\min_{y} \left( \sum_{k} d_k (2 y_k - 1) \right)^2$$
  Expanding this expression yields all-to-all quadratic interaction terms $d_j d_k (2 y_j - 1)(2 y_k - 1)$, producing an Ising Hamiltonian with dense two-qubit couplings. *(Note: This simplified model illustrates two-path load balancing only and does not solve general multi-commodity flow routing, which requires multi-hop path variables, link capacity inequalities, and flow conservation constraints).*
- **Why It Fits VARANASI:** Dense interaction topologies in load-balancing QUBOs illustrate why hardware architecture co-design is essential: generic sparse coupling graphs suffer extensive SWAP overhead, whereas problem-informed topologies (like Processor D) highlight how native embeddings preserve quantum circuit fidelity by minimizing two-qubit gate depth.
- **Demonstration Status (Proposed Architectural Extension):** This application represents a proposed architectural demonstration showing how two-path load balancing maps to QAOA; the benchmark results in this repository remain dedicated to the locked PS-O1 network partitioning instance.

---

## Repository Structure (Challenge Kit Section 10 Layout)

```
VARANASI_PROJECTQ/
├── README.md                 # Team, PS code, setup, key results table, AI disclosure
├── main.ipynb                # End-to-end reproducible notebook (runs in < 30 minutes)
├── requirements.txt          # Pinned dependency versions
├── qff_phase2.py             # Official organizer starter module (unchanged)
├── docs/
│   └── JUDGE_GUIDE.md        # Technical defense guide and answers to 14 judge questions
├── data/
│   └── instance.json         # Locked PS-O1 graph instance (copied from instances.json)
├── processors/
│   ├── processor_A.json      # Reference Processor A (5 qubits)
│   ├── processor_B.json      # Reference Processor B (9 qubits)
│   └── processor_D.json      # Final frozen Processor D architecture
├── src/                      # Modular Python package
│   ├── __init__.py
│   ├── exact_solver.py       # Exhaustive classical ground-truth solver (C* = 22)
│   ├── qaoa_solver.py        # Parameterized QAOA ansatz and COBYLA multi-start optimizer
│   ├── bell_evaluator.py     # Bell-state tomography and fidelity verification
│   ├── visualizations.py     # High-resolution figure generation
│   └── benchmark_runner.py   # Automated benchmark pipeline
├── presentation/             # Professional research communication & pitch assets
│   ├── VARANASI_Pitch_Deck.pptx # Editable 16:9 PowerPoint pitch deck
│   ├── VARANASI_Pitch_Deck.pdf  # Publication-grade vector PDF pitch deck
│   ├── speaker_notes.md      # Slide-by-slide notes, quantitative evidence & timing
│   ├── pitch_script_3min.md  # 3-minute spoken pitch script (~410 words)
│   ├── pitch_script_60sec.md # 60-second elevator pitch script (~140 words)
│   └── judge_qa.md           # 16 comprehensive judge defense Q&As
├── results/
│   ├── tables/
│   │   ├── results.csv       # Section 9 official benchmark results
│   │   └── bell.csv          # Section 4 Bell-state verification results
│   ├── raw/
│   │   ├── qaoa_counts.json  # Complete 64-bitstring histograms and per-bitstring metrics
│   │   └── benchmark_metadata.json # Complete provenance, environment, seeds, and hashes
│   └── figures/              # Publication figures in 300 DPI PNG and scalable SVG
│       ├── network_partitioning_graph.png (.svg)
│       ├── processor_topologies.png (.svg)
│       ├── bell_fidelity_comparison.png (.svg)
│       ├── qaoa_cut_distribution.png (.svg)
│       ├── processor_resource_comparison.png (.svg)
│       ├── qaoa_parameter_landscape.png (.svg)
│       └── architecture_tradeoff_map.png (.svg)
├── scripts/
│   └── create_submission_zip.py # Deterministic delivery zip packager and manifest auditor
├── requirements-lock.txt     # Exact pinned reproducible environment specification
├── report.md                 # Comprehensive 6-page technical report
├── Phase One/                # Preserved Phase One qualification archive
├── instances.json            # Locked organizer instances file
└── example_usage.py          # Official starter example script
```

---

## Setup & Reproducibility Instructions

### 1. Environment Setup
Recommended Python environment: Python 3.10–3.12 (also tested on Python 3.14).
```bash
# Clone the repository
git clone https://github.com/ganesh-pirinti/VARANASI_PROJECTQ.git
cd VARANASI_PROJECTQ

# Create and activate virtual environment
python -m venv opt-env
opt-env\Scripts\activate            # Windows
source opt-env/bin/activate         # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Starter Script & Processor D Validation
```bash
# Official starter test
python example_usage.py

# Validate actual frozen Processor D submission
python -c "from qff_phase2 import load_processor, validate_processor_d; D = load_processor('processors/processor_D.json'); print('VALID' if not validate_processor_d(D, 6) else 'INVALID')"
```

### 3. Run End-to-End Pipeline
```bash
# Execute full benchmark suite and regenerate all tables and figures
python -c "from src.benchmark_runner import run_all_benchmarks; run_all_benchmarks()"

# Regenerate all 7 publication figures (PNG + SVG)
python -m src.visualizations

# Rebuild PowerPoint (.pptx) and Publication PDF (.pdf) pitch decks
python scripts/generate_pitch_deck.py

# Run consolidated verification suite (8/8 PASS)
python tests/consolidated_test_suite.py

# Or open and run the notebook from top to bottom
jupyter notebook main.ipynb
```
The notebook executes end-to-end in approximately **15 seconds** on a standard laptop CPU, satisfying the 30-minute requirement with wide margin.

---

## Official Settings & Constants

All benchmark runs strictly use the locked official settings from `qff_phase2.py`:
- **Basis Gates:** `["rz", "sx", "x", "cx"]`
- **Optimization Level:** 1 with SABRE layout and routing
- **Transpiler Seed:** 42
- **Simulator Seed:** 42
- **Shots:** 4096 per reported sampled run
- **Noise Model:** 1-qubit depolarizing $p_1 = 0.001$, 2-qubit depolarizing $p_2 = 0.005$, symmetric readout bit-flip $p_{\text{readout}} = 0.01$.

---

## AI Tool Disclosure

In compliance with hackathon regulations:
- **AI Tools Used:** Anthropic Claude (via Claude Sonnet 4.6), Google Antigravity Agentic Assistant.
- **Role:** Assisted in modular code structuring, documentation formatting, LaTeX mathematical typing, and drafting report explanations. All circuit transpilation, parameter optimization, noise modeling, and benchmark statistics were computed directly by Qiskit and Qiskit Aer within the project repository.
