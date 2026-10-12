# Qiskit Fall Fest 2026 — Phase 1 Submission

## Problem Statement: PS-O1 — Max-Cut on Weighted Graphs
### Focus Area: QAOA Circuit Construction & SWAP Bottleneck Analysis on Official Processors A & B

---

### Submission Metadata
- **Track:** Quantum Optimization
- **Problem Statement Code:** PS-O1 (Max-Cut)
- **Host Institution:** SRM University-AP | Hackathon & Competitions Cell
- **Stage:** Phase 1 — Online Qualification Stage
- **Team Name:** YOUR_ACTUAL_REGISTERED_TEAM_NAME
- **Participant / Team ID:** YOUR_ACTUAL_REGISTERED_PARTICIPANT_OR_TEAM_ID
- **Team Leader:** Ganesh Pirinti (SRM University-AP, Andhra Pradesh | Email: ganeshpirinti95218@gmail.com)
- **Additional Team Member:** Mohammed Sadiq (SRM University-AP, Andhra Pradesh | Email: sadiqmohammedkhan12@gmail.com)
- **GitHub Repository URL:** https://github.com/ganesh-pirinti/VARANASI_PROJECTQ
- **Hugging Face Space URL:** N/A (Not Applicable for Phase 1 Python/Notebook Pipeline)
- **Hardware Source Authority:** Participant challenge brief citing `Processor_AB_Benchmark_Configuration_FINAL.pdf` & `Problem_Statment_Details.pdf`

---

## 1. Official Hardware Specifications & Architecture Conflict Resolution

### 1.1 Official Processor Topologies
Per the authoritative challenge configuration files (`Processor_AB_Benchmark_Configuration_FINAL.pdf`):
- **Processor A (5 Physical Qubits):**
  - **Topology:** 5-node branching / T-tree architecture.
  - **Coupling Edges (Undirected):** `(0, 1)`, `(1, 2)`, `(1, 3)`, `(3, 4)`.
  - **Structure:** Node 1 is central (degree 3), Node 3 has degree 2, and Nodes 0, 2, 4 are leaves (degree 1). Diameter $D = 3$.
- **Processor B (9 Physical Qubits):**
  - **Topology:** 9-node heavy-hex inspired cyclic mesh lattice.
  - **Coupling Edges (Undirected):** `(0, 1)`, `(1, 2)`, `(1, 6)`, `(2, 3)`, `(2, 6)`, `(2, 5)`, `(3, 4)`, `(4, 5)`, `(5, 6)`, `(6, 7)`, `(6, 8)`, `(8, 0)`.
  - **Structure:** 12 undirected edges. Qubit 6 is a major hub (degree 5); Qubit 2 has degree 4. Diameter $D = 4$.
- **Shared Basis Gate Set:** Standard transmon universal basis `['rz', 'sx', 'x', 'cx']`.
- **Hardware Verification Disclosure:** The topology coupling maps above match the official challenge brief provided for Phase 1. Because raw PDF challenge files were not stored in this local workspace, direct file-hash verification against the original PDF remains pending organizer portal access.

### 1.2 Resolution of the 6-Vertex Graph vs. 5-Qubit Hardware Capacity Conflict

> [!CAUTION]
> **Identified Challenge Conflict:**
> - Problem Statement **PS-O1** mandates: *"Given a graph of 6 vertices with random edge weights, formulate the Max-Cut cost Hamiltonian... Provide 2–3 example graphs with 6 nodes and integer weights 1–5."*
> - The Universal Challenge Framework mandates: *"Processor A = 5 qubits with coupling edges (0,1), (1,2), (1,3), (3,4)."*
>
> In standard gate-based quantum compilation, mapping a 6-qubit quantum state ($2^6 = 64$ dimensions) onto a 5-qubit hardware register ($2^5 = 32$ dimensions) is **physically impossible without circuit cutting or problem-size reduction**. Attempting compilation in Qiskit strictly raises:
> `TranspilerError: Number of qubits (6) in circuit is greater than maximum (5) in the coupling_map`.
>
> **Our Scientifically Rigorous Resolution (Dual-Tier Benchmark):**
> 1. **Do not fabricate results:** We formally evaluate the 6-qubit circuit against Processor A and log its status as **`INFEASIBLE_CAPACITY_EXCEEDED`**, demonstrating the fundamental register capacity limitation of NISQ processors.
> 2. **Canonical 6-Vertex Benchmark on Processor B:** The 6-qubit QAOA circuit is compiled and benchmarked on **Processor B (9 qubits)**, utilizing its multi-path heavy-hex routing lattice.
> 3. **Co-Design 5-Vertex Induced Subgraph Benchmark:** To fulfill the mandatory head-to-head A vs. B comparative analysis (30 points of the judging rubric), we evaluate the maximal 5-node induced subgraph on **BOTH Processor A (5 qubits) and Processor B (9 qubits)**, directly measuring the routing SWAP penalty imposed by Processor A's branching tree vs. Processor B's heavy-hex mesh.

---

## 2. Mathematical Formulation & Algorithmic Design

### 2.1 The Weighted Max-Cut Problem
Given an undirected graph $G = (V, E, w)$ with vertex set $V$, edge set $E$, and integer weights $w_{uv} \in \{1, \dots, 5\}$:
$$C(s) = \sum_{(u, v) \in E} w_{uv} \frac{1 - s_u s_v}{2}, \quad s_u \in \{-1, +1\}$$

Mapping spins to Pauli-$Z$ operators ($s_u \to Z_u$), the cost Hamiltonian is:
$$H_C = \sum_{(u, v) \in E} \frac{w_{uv}}{2} (I - Z_u Z_v)$$

Minimizing $-H_C$ maximizes the cut value.

### 2.2 Quantum Approximate Optimization Algorithm (QAOA)
Starting from uniform superposition $|+\rangle^{\otimes n}$, the $p$-layer ansatz applies:
$$|\psi(\boldsymbol{\gamma}, \boldsymbol{\beta})\rangle = \prod_{k=1}^p U(M, \beta_k) U(C, \gamma_k) |+\rangle^{\otimes n}$$
- **Cost Unitary:** $U(C, \gamma) = \prod_{(u, v) \in E} R_{ZZ}(2 \gamma w_{uv})$, synthesized natively via $\text{CX}(u, v) \to R_Z(2 \gamma w_{uv}) \to \text{CX}(u, v)$.
- **Mixer Unitary:** $U(M, \beta) = \prod_{u \in V} R_X(2 \beta)$.

---

## 3. Evaluated Problem Graph Instances

### 3.1 Canonical 6-Node Graph (`data/benchmark_graph_6node.json`)
- **Vertices:** $V = \{0, 1, 2, 3, 4, 5\}$
- **Edges & Integer Weights:**
  - Perimeter cycle: $(0,1): 2$, $(1,2): 3$, $(2,3): 1$, $(3,4): 4$, $(4,5): 2$, $(5,0): 3$
  - Frustrating chords: $(0,2): 3$, $(2,4): 2$, $(0,4): 3$
- **Total Weight:** $W = 23$

### 3.2 Co-Design 5-Node Induced Subgraph (`data/benchmark_graph_5node.json`)
- **Vertices:** $V = \{0, 1, 2, 3, 4\}$
- **Edges & Integer Weights:** $(0,1): 2$, $(1,2): 3$, $(2,3): 1$, $(3,4): 4$, $(0,2): 3$, $(2,4): 2$, $(0,4): 3$
- **Total Weight:** $W = 18$

---

## 4. Experimental Results & Verification

All results were obtained from local execution of `main.py` using Qiskit 2.5.2 and Qiskit-Aer 0.17.2:

### 4.1 Classical Baselines vs. QAOA Algorithmic Performance

| Metric | 6-Node Canonical Instance | 5-Node Co-Design Subgraph | Theoretical Significance |
| :--- | :---: | :---: | :--- |
| **Classical Brute-Force Optimum ($C_{\text{max}}$)** | **17.0** | **14.0** | Evaluated exhaustively ($2^6=64$ and $2^5=32$ states) |
| **Degenerate Optimal Partitions** | 6 optimal cuts | 4 optimal cuts | Verified symmetric cut sets |
| **Random Baseline Expectation $\mathbb{E}[C_{\text{rand}}]$** | **11.5** | **9.0** | Unbiased coin-toss expectation ($0.5 \times W$) |
| **QAOA Optimal Parameters** | $\gamma = 0.4856, \beta = 0.3875$ | $\gamma = 0.4308, \beta = 0.9041$ | Converged via COBYLA optimizer ($p=1$, seed=42) |
| **QAOA Expected Cut $\langle C \rangle$** | **13.5491** | **10.2357** | Statevector analytical expectation value |
| **Approximation Ratio ($\alpha = \frac{\langle C \rangle}{C_{\text{max}}}$)** | **0.7970 (79.70%)** | **0.7311 (73.11%)** | Substantially outperforms random baseline |

---

### 4.2 Official Processor A & B Transpilation Benchmark Table

Exported directly from `results/benchmark_metrics.csv`:

| Instance | Circuit Qubits | Processor | Processor Qubits | Compilation Status | Opt Level | Depth | Measured SWAPs | Routing Pass | Physical CX | CX Overhead | Routing Overhead | Total Gates | Transpile Time |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **6-Node_Canonical** | 6 | **Processor_A** | 5 | **INFEASIBLE_CAPACITY_EXCEEDED** | 1 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **6-Node_Canonical** | 6 | **Processor_A** | 5 | **INFEASIBLE_CAPACITY_EXCEEDED** | 2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **6-Node_Canonical** | 6 | **Processor_A** | 5 | **INFEASIBLE_CAPACITY_EXCEEDED** | 3 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **6-Node_Canonical** | 6 | **Processor_B** | 9 | **COMPILED_SUCCESSFULLY** | 1 | 37 | 2 | `SabreLayout` | 20 | +2 | 11.1% | 80 | 0.068 s |
| **6-Node_Canonical** | 6 | **Processor_B** | 9 | **COMPILED_SUCCESSFULLY** | 2 | 48 | 2 | `SabreLayout` | 20 | +2 | 11.1% | 101 | 0.045 s |
| **6-Node_Canonical** | 6 | **Processor_B** | 9 | **COMPILED_SUCCESSFULLY** | 3 | 42 | **1** | `SabreLayout` | **19** | **+1** | **5.6%** | 90 | 0.028 s |
| **5-Node_Subgraph** | 5 | **Processor_A** | 5 | **COMPILED_SUCCESSFULLY** | 1 | 32 | 2 | `SabreLayout` | 20 | +6 | 42.9% | 70 | 0.016 s |
| **5-Node_Subgraph** | 5 | **Processor_A** | 5 | **COMPILED_SUCCESSFULLY** | 2 | 32 | 2 | `SabreLayout` | 20 | +6 | 42.9% | 70 | 0.021 s |
| **5-Node_Subgraph** | 5 | **Processor_A** | 5 | **COMPILED_SUCCESSFULLY** | 3 | 32 | **2** | `SabreLayout` | **20** | **+6** | **42.9%** | 70 | 0.025 s |
| **5-Node_Subgraph** | 5 | **Processor_B** | 9 | **COMPILED_SUCCESSFULLY** | 1 | 32 | 1 | `SabreLayout` | 17 | +3 | 21.4% | 67 | 0.013 s |
| **5-Node_Subgraph** | 5 | **Processor_B** | 9 | **COMPILED_SUCCESSFULLY** | 2 | 32 | 1 | `SabreLayout` | 17 | +3 | 21.4% | 67 | 0.019 s |
| **5-Node_Subgraph** | 5 | **Processor_B** | 9 | **COMPILED_SUCCESSFULLY** | 3 | 32 | **1** | `SabreLayout` | **17** | **+3** | **21.4%** | 67 | 0.023 s |

---

## 5. Technical Architectural Interpretation: The SWAP Bottleneck

### 5.1 Single-Lineage Transpilation & SWAP Gate Decomposition
In superconducting processors with fixed nearest-neighbor couplers, non-adjacent logical two-qubit interactions cannot execute directly. The compiler must insert `SWAP` gates during layout and routing to permute qubit states until interacting pairs become physically adjacent. In the native transmon basis set (`['rz', 'sx', 'x', 'cx']`), each SWAP decomposes into **three alternating CX gates**:
$$\text{SWAP}(q_i, q_j) = \text{CX}(q_i, q_j) \cdot \text{CX}(q_j, q_i) \cdot \text{CX}(q_i, q_j)$$

**Counting Routing SWAPs When Decomposed into CX Gates:**
- To guarantee that SWAP counts and physical circuit metrics describe the exact same compilation run without combining disjoint runs, our `RoutingStageInstrumenter` callback intercepts the compiler DAG during the routing stage (`SabreLayout` / `SabreRouting`) before basis translation (`BasisTranslator`).
- It explicitly records the responsible pass name (`routing_pass = 'SabreLayout'`), validates that routing instrumentation executed, and captures the routed circuit snapshot containing explicit SWAPs.
- During basis translation, each inserted SWAP expands into 3 CX gates ($14 + 3 \times 2 = 20$ CX for 5-Node on Processor A; $14 + 3 \times 1 = 17$ CX for 5-Node on Processor B).
- In subsequent peephole optimization stages (e.g., `TwoQubitPeepholeOptimization` at Optimization Level 3 on 6-Node Processor B), commuting operations may cancel redundant CX pairs, yielding 19 physical CX gates (+1 net CX overhead above the 18 logical CXs).

**Methodologically Consistent Routing Overhead Definition:**
To isolate physical routing overhead without optimization-level mismatch, for each optimization level $L \in \{1, 2, 3\}$, an unconstrained baseline circuit is synthesized into the native basis without coupling constraints at that exact same level $L$:
$$\text{CX Overhead} = \text{Physical CX} - \text{Logical CX}(L)$$
$$\text{Routing Overhead Ratio} = \frac{\text{Physical CX} - \text{Logical CX}(L)}{\text{Logical CX}(L)}$$
$$\text{Depth Overhead} = \text{Physical Depth} - \text{Logical Depth}(L)$$
For the QAOA instances, unconstrained baselines produce $\text{Logical CX} = 18$ (6-node) and $\text{Logical CX} = 14$ (5-node) consistently across levels 1–3, providing a rigorous, matched reference.

### 5.2 Comparative Analysis: Processor A vs. Processor B

1. **Hardware Capacity Constraint (6-Node Instance):**
   - Monolithic unitary compilation requires $N_{\text{logical}} \le N_{\text{physical}}$. Processor A's 5-qubit limit physically bars compiling the 6-node QAOA instance. This proves that qubit count is the primary gating constraint for combinatorial optimization on NISQ hardware.
   - Processor B (9 physical qubits) accommodates the 6-qubit circuit with ease, requiring only **1 SWAP** via `SabreLayout` at Optimization Level 3 (physical depth 42, 19 CX gates, +1 CX overhead above 18 logical CXs, routing overhead ratio 5.6%).

2. **Topological Routing Bottlenecks (5-Node Co-Design Benchmark):**
   - **Processor A (T-Tree Architecture):** Node 1 acts as a central junction (degree 3) connecting to 0, 2, and 3, while node 3 connects to 4. Qubits 0, 2, and 4 are leaves of degree 1. In a graph with cycle edges like $(0, 2)$ and $(2, 4)$, leaf qubits cannot interact without routing through the central hub. This severe structural bottleneck forces **2 SWAP gates** via `SabreLayout` and inflates physical CX count to **20** (+6 overhead, 42.9% routing overhead ratio).
   - **Processor B (Heavy-Hex Mesh Architecture):** Contains multiple alternative cycles and hubs (node 6 has degree 5, node 2 has degree 4). The SABRE routing pass exploits parallel routing pathways, requiring only **1 SWAP gate** and **17 physical CX gates** (+3 overhead, 21.4% routing overhead ratio across all optimization levels).

3. **Theoretical Error Budget & NISQ Impact:**
   - *Two-Qubit Gate Error Scaling:* In fixed-frequency transmon processors with cross-resonance coupling (e.g., reported in Bravyi et al., *Nature* 603, 2022 and Kim et al., *Nature* 618, 2023), typical median two-qubit CX gate error rates $\epsilon_{2\text{Q}}$ range between $0.5\%$ and $1.0\%$. Under an uncorrelated depolarizing model $F \approx (1 - \epsilon_{2\text{Q}})^{N_{\text{CX}}}$, the +6 CX routing overhead on Processor A imposes an estimated state fidelity penalty of $(1 - 0.005)^6 \approx 97.0\%$ (or $94.1\%$ at $1.0\%$ error), compared to only +3 CX on Processor B ($(1 - 0.005)^3 \approx 98.5\%$).
   - *Spectator Crosstalk & Congestion:* Fixed-frequency planar transmons exhibit $ZZ$-crosstalk and spectator Stark dephasing when multiple coupled edges are driven concurrently (Mckay et al., *Phys. Rev. Applied* 6, 2016; Sundaresan et al., *PRX Quantum* 1, 2020). Because Processor A is a tree graph with node 1 as the sole central junction (degree 3), all leaf-to-leaf interactions must serialize through this single hub, precluding parallel two-qubit executions. Conversely, Processor B's heavy-hex cyclic mesh provides alternate topological pathways that spatially distribute gate operations and mitigate localized spectator crosstalk.

---

## 6. Generated Visualization Artifacts

1. **Topologies & Problem Graph (`results/topology_comparison.png`):**  
   Side-by-side visualization of the 6-node problem graph, official 5-qubit Processor A tree, and official 9-qubit Processor B mesh.
2. **QAOA Sampling Distribution (`results/cut_distribution.png`):**  
   Measurement probabilities across all 64 basis states, highlighting peak concentration on high-cut partitions.
3. **SWAP & CX Overhead Comparison (`results/swap_overhead_bar.png`):**  
   Grouped bar charts comparing SWAP counts, CX gate counts, and circuit depth across optimization levels 1–3 for both processors.

---

## 7. Reproduction Instructions

```bash
# 1. Clone repository and navigate to root directory
git clone https://github.com/ganesh-pirinti/VARANASI_PROJECTQ.git
cd VARANASI_PROJECTQ

# 2. Install pinned dependencies in virtual environment
pip install -r requirements.txt

# 3. Run automated end-to-end CLI workflow
python main.py

# 4. Run automated test suite (18 unit and regression tests)
python -m unittest tests/test_project.py -v

# 5. (Optional) Run interactive Jupyter Notebook
jupyter notebook main.ipynb
```

---

## 8. AI / LLM Assistance Disclosure

In accordance with **Section 11 (AI / LLM Use Policy)** of the official Qiskit Fall Fest 2026 Phase 1 instructions:
1. **Tool Used:** Gemini 3.6 Flash / Antigravity Agent.
2. **Scope of Assistance:** Modular project architecture, transpilation DAG pipeline construction, capacity bottleneck detection handling, and technical documentation drafting.
3. **Verification & Responsibility:** All quantum circuits, simulations, classical brute-force baselines, and transpilation runs were executed locally on Python 3.14. All empirical metrics and analysis were validated against theoretical bounds. The participant takes full responsibility for the submitted work.
