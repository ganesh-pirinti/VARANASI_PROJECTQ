# Technical Report: Quantum Optimization of Network Partitioning Using QAOA
**Qiskit Fall Fest 2026 — Phase 2: Quantum Optimization Track**  
**Problem Statement PS-O1: Network Partitioning / Max-Cut**

---

### Team Metadata
- **Team Name:** `VARANASI`
- **Participant / Team ID:** `AP251100708044`
- **Team Leader:** Ganesh Pirinti (SRM University-AP, Andhra Pradesh | `ganeshpirinti95218@gmail.com`)
- **Team Member:** Mohammed Sadiq (SRM University-AP, Andhra Pradesh | `sadiqmohammedkhan12@gmail.com`)
- **Host Institution:** SRM University-AP | Hackathon & Competitions Cell
- **Stage:** Phase 2 (Optimization Track Final Deliverable)
- **GitHub Repository:** [https://github.com/ganesh-pirinti/VARANASI_PROJECTQ](https://github.com/ganesh-pirinti/VARANASI_PROJECTQ)

---

## Executive Summary

This report presents the complete Phase 2 solution for **Problem Statement PS-O1: Quantum Optimization of Network Partitioning Using QAOA**. Using the locked six-vertex, nine-edge benchmark graph ($W = 27$) from the official Challenge Kit, we formulate the network partitioning problem as a Quadratic Unconstrained Binary Optimization (QUBO) model and derive its corresponding Ising cost Hamiltonian. 

We perform an exhaustive classical ground-truth enumeration over all $2^6 = 64$ bitstrings, establishing an exact maximum cut value of $C^* = 22$ (achieved by complementary partitions $(1, 1, 0, 1, 0, 0)$ and $(0, 0, 1, 0, 1, 1)$) alongside an exact uniform random baseline expectation of $\mathbb{E}[C] = 13.5$ ($r_{\text{random}} = 0.6136, P_{\text{opt, random}} = 0.03125$).

Under official benchmark settings (optimization level 1, SABRE layout/routing, seed 42, 4096 shots, official noise model $p_1=0.001, p_2=0.005, p_{\text{readout}}=0.01$), we implement the Quantum Approximate Optimization Algorithm (QAOA) at depth $p=1$ with multi-start classical parameter optimization across mandatory seeds $[0, 1, 2, 3, 4]$. We rigorously benchmark execution across reference Processors A and B, and our novel co-designed **Processor D**:
1. **Processor A (5 Qubits):** Correctly classified as **infeasible / not executable** under the official capacity rule ($6 > 5$ qubits).
2. **Processor B (9 Qubits):** Suffers from a routing bottleneck requiring **1 SWAP gate** (+3 CX gates, 16.7% two-qubit overhead), yielding depth 37 and two-qubit depth 17.
3. **Processor D (9 Qubits, VARANASI Co-Design):** Directly embeds the six-vertex interaction graph with a peripheral degree-$\le 4$ routing ring, achieving **0 SWAPs (0 CX overhead)**, reducing two-qubit depth to 14 (-17.6%) and circuit depth to 29 (-21.6%). Under noisy simulation, Processor D delivers an approximation ratio of $r = 0.7862$ and an optimal partition sampling probability of $P_{\text{opt}} = 12.50\%$, achieving numerically similar solution quality to Processor B ($r = 0.7874$, $\Delta r = -0.0012$ or $-0.15\%$ relative) while reducing compiled physical CX gates by $14.29\%$ and two-qubit depth by $17.65\%$, and providing a **$4.0\times$** optimal-state sampling probability enhancement over the classical uniform random baseline ($3.125\%$).

All deliverables, including results/tables/results.csv, results/tables/bell.csv, results/raw/qaoa_counts.json, results/raw/benchmark_metadata.json, figures, and main.ipynb, are fully reproducible and verified. A concise evaluator summary and answers to 14 defense questions are documented in [docs/JUDGE_GUIDE.md](docs/JUDGE_GUIDE.md).

---

## 1. Problem Definition, Mathematical Formulation & Classical Baseline

### 1.1 Problem Background
Network partitioning divides a communication or computational network into two disjoint communities such that connectivity (or communication traffic) across the partition interface is maximized, while isolating internal interactions. This translates directly to the **Maximum Cut (Max-Cut)** problem on an undirected weighted graph.

### 1.2 Mathematical Formulation and QUBO Construction
Let $G = (V, E, w)$ denote the locked six-vertex graph with edge set $E$ ($|E| = 9$) and integer edge weights $w_{uv} \in \{1, \dots, 5\}$. Define binary decision variables:
$$
x_i \in \{0, 1\} \quad \forall i \in \{0, \dots, 5\}
$$
where $x_i = 1$ assigns vertex $i$ to partition group $S$, and $x_i = 0$ assigns vertex $i$ to group $\bar{S} = V \setminus S$.
An edge $(u, v) \in E$ is traversed (cut) by the partition boundary if and only if $x_u \neq x_v$. The cut indicator polynomial is:
$$
(x_u - x_v)^2 = x_u + x_v - 2 x_u x_v
$$
The total cut weight objective function is:
$$
C(x) = \sum_{(u, v) \in E} w_{uv} (x_u + x_v - 2 x_u x_v)
$$
Formulated as a Quadratic Unconstrained Binary Optimization (QUBO) minimization model:
$$
\min_{x \in \{0, 1\}^6} Q(x) = -C(x) = \sum_{(u, v) \in E} w_{uv} (2 x_u x_v - x_u - x_v)
$$

### 1.3 Ising Cost Hamiltonian Derivation
To execute on quantum hardware, we map binary variables $x_i$ to Pauli-$Z$ spin observables via the standard transformation:
$$
x_i \mapsto \frac{I - Z_i}{2}
$$
Substituting this into the cut expression for edge $(u, v)$:
$$
x_u + x_v - 2 x_u x_v = \frac{I - Z_u}{2} + \frac{I - Z_v}{2} - 2\left(\frac{I - Z_u}{2}\right)\left(\frac{I - Z_v}{2}\right) = \frac{I - Z_u Z_v}{2}
$$
The total cut operator is therefore:
$$
\hat{C} = \sum_{(u, v) \in E} \frac{w_{uv}}{2} (I - Z_u Z_v) = \frac{W}{2} I - \sum_{(u, v) \in E} \frac{w_{uv}}{2} Z_u Z_v
$$
where $W = \sum_{(u, v) \in E} w_{uv} = 27$ is the constant total graph weight. Dropping the global identity offset, the cost Hamiltonian to minimize is:
$$
\hat{H}_C = \sum_{(u, v) \in E} \frac{w_{uv}}{2} Z_u Z_v
$$
The QAOA mixer Hamiltonian is the standard transverse field:
$$
\hat{H}_M = \sum_{i=0}^5 X_i
$$
The depth $p=1$ state vector parameterized by continuous variational angles $(\gamma, \beta)$ is:
$$
|\psi(\gamma, \beta)\rangle = e^{-i \beta \hat{H}_M} e^{-i \gamma \hat{H}_C} |+\rangle^{\otimes 6} = \left(\prod_{i=0}^5 R_X(2\beta)_i\right) \left(\prod_{(u, v) \in E} R_{ZZ}(w_{uv} \gamma)_{u, v}\right) |+\rangle^{\otimes 6}
$$
where each two-qubit rotation $R_{ZZ}(\theta)$ is decomposed into the native basis gate sequence:
$$
CX(u, v) \longrightarrow R_Z(\theta)_v \longrightarrow CX(u, v)
$$

### 1.4 Exact Classical Ground-Truth Enumeration
We performed an exhaustive evaluation of all $2^6 = 64$ bitstrings. The ground-truth metrics are:
- **Total Graph Weight ($W$):** 27
- **Exact Maximum Cut ($C^*$):** 22
- **Optimal Partition Assignments:**
  1. $x = (1, 1, 0, 1, 0, 0) \implies S = \{0, 1, 3\}, \bar{S} = \{2, 4, 5\}$
  2. $x = (0, 0, 1, 0, 1, 1) \implies S = \{2, 4, 5\}, \bar{S} = \{0, 1, 3\}$ (exact bitwise complement)
- **Cut Edges (Weight = 22):** $(0, 2): 1, (0, 4): 4, (1, 4): 3, (1, 5): 3, (2, 3): 5, (3, 4): 4, (3, 5): 2$
- **Uncut Edges (Weight = 5):** $(0, 3): 4, (2, 4): 1$
- **Uniform Random Baseline:**
  $$
  \mathbb{E}_{\text{random}}[C(x)] = \sum_{(u, v) \in E} w_{uv} \times \frac{1}{2} = 13.5000
  $$
  $$
  r_{\text{random}} = \frac{13.5}{22} \approx 0.6136 \quad (61.36\%)
  $$
  $$
  P_{\text{opt, random}} = \frac{2}{64} = 0.03125 \quad (3.125\%)
  $$

---

## 2. Objective 1 — Bell-State Verification on Processor D

### 2.1 State Preparation and Measurement Methodology
To establish physical gate calibration and benchmark routing penalties on Processor D, we prepared the maximally entangled Bell state:
$$
|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}
$$
State preparation executes Hadamard on physical qubit $q_0$ followed by $CX(q_0 \to q_1)$.
Measurements were performed in three orthogonal correlation bases across 4096 shots per basis:
- **$ZZ$ Basis:** Standard computational basis measurement.
- **$XX$ Basis:** $H \otimes H$ applied before measurement.
- **$YY$ Basis:** $(S^\dagger H) \otimes (S^\dagger H)$ applied before measurement.

For parity expectation $\langle P \rangle = (N_{\text{even}} - N_{\text{odd}})/N$, the exact fidelity for $|\Phi^+\rangle$ is:
$$
F(|\Phi^+\rangle) = \frac{1 + \langle XX \rangle - \langle YY \rangle + \langle ZZ \rangle}{4}, \quad \text{SE}(F) = \frac{1}{4} \sqrt{\text{SE}_{XX}^2 + \text{SE}_{YY}^2 + \text{SE}_{ZZ}^2}
$$

### 2.2 Empirical Results (`results/tables/bell.csv`)

| Pair Type | Physical Qubits | Graph Distance ($d$) | Condition | Transpiled CX | $\langle XX \rangle \pm \text{SE}$ | $\langle YY \rangle \pm \text{SE}$ | $\langle ZZ \rangle \pm \text{SE}$ | Fidelity $F \pm \text{SE}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Near** | $(0, 2)$ | 1 | Ideal | 1 | $+1.0000 \pm 0.0000$ | $-1.0000 \pm 0.0000$ | $+1.0000 \pm 0.0000$ | **$1.0000 \pm 0.0000$** |
| **Near** | $(0, 2)$ | 1 | Noisy | 1 | $+0.9458 \pm 0.0051$ | $-0.9521 \pm 0.0048$ | $+0.9551 \pm 0.0046$ | **$0.9633 \pm 0.0021$** |
| **Far** | $(0, 7)$ | 4 | Ideal | 10 | $+1.0000 \pm 0.0000$ | $-1.0000 \pm 0.0000$ | $+1.0000 \pm 0.0000$ | **$1.0000 \pm 0.0000$** |
| **Far** | $(0, 7)$ | 4 | Noisy | 10 | $+0.9243 \pm 0.0060$ | $-0.9038 \pm 0.0067$ | $+0.9399 \pm 0.0053$ | **$0.9420 \pm 0.0026$** |

### 2.3 Physical Interpretation of Fidelity Degradation
1. **Adjacent Pair ($d=1$):** Because physical qubits 0 and 2 share a direct hardware link, transpilation requires only **1 CX gate** and 2 single-qubit gates. The noisy fidelity drops from 1.0000 to $0.9633 \pm 0.0021$. This drop corresponds precisely to the analytic error budget: a single two-qubit depolarizing channel ($p_2 = 0.005$), two single-qubit channels ($p_1 = 0.001$), and readout error bit-flips ($p_{\text{readout}} = 0.01$ per qubit), yielding an expected survival probability $\approx (1 - \frac{4}{3}p_2)(1 - 2p_{\text{readout}}) \approx 0.963$.
2. **Distant Pair ($d=4$):** Preparing a Bell state between qubits 0 and 7 across graph diameter $d=4$ requires routing along intermediate physical nodes ($0 \to 3 \to 5 \to 6 \to 7$). The transpiler synthesizes 3 intermediate SWAP gates, expanding the CX count to **10 CX gates**. Each additional two-qubit gate compounds depolarizing error, resulting in a statistically significant degradation to $F = 0.9420 \pm 0.0026$ (a $\Delta F = -0.0213$ penalty). This directly demonstrates why reducing routing diameter and SWAP overhead is paramount for NISQ execution.

---

## 3. Objective 2 — Processor D Architecture Co-Design

### 3.1 Architectural Bottleneck Analysis
In NISQ architectures, physical connectivity governs algorithm performance:
- **Processor A Bottleneck (Capacity):** With only 5 physical qubits arranged in a star-chain tree, Processor A cannot map 6 logical problem variables, rendering execution impossible.
- **Processor B Bottleneck (Routing):** Processor B provides 9 physical qubits, but its coupling links form a ring-hub configuration that lacks direct physical connections between several interacting vertex pairs in the PS-O1 instance. When compiling the 9-edge QAOA ansatz, the SABRE layout and routing stage is forced to insert **1 SWAP gate** (3 CX equivalents), incurring a 16.7% two-qubit gate overhead and expanding two-qubit depth to 17.

### 3.2 Processor D Specification and Co-Design
We engineered **Processor D** (`processors/processor_D.json`) to natively support the problem graph topology while remaining realistic for physical hardware fabrication:
- **Physical Qubits ($N = 9$):** Qubits $0..5$ serve as the computational core; qubits $6..8$ form an ancillary communication bus.
- **Problem Embedding:** The 9 interaction edges of PS-O1:
  $$
  \{(0, 2), (0, 3), (0, 4), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (3, 5)\}
  $$
  are mapped directly to physical couplings.
- **Ancillary Closed Routing Ring:** Qubits $6..8$ are connected via:
  $$
  (5, 6), (6, 7), (7, 8), (8, 1)
  $$
  closing a peripheral loop between core nodes 1 and 5.
- **Full Compliance:**
  - `num_qubits = 9` (within $[6, 12]$).
  - Graph is connected with diameter $d=4$.
  - Maximum degree is exactly **4** (nodes 3 and 4 have degree 4; nodes 0, 1, 2, 5 have degree 3; nodes 6, 7, 8 have degree 2). No node violates the max-degree $\le 4$ limit.
  - Basis gates: locked to `["rz", "sx", "x", "cx"]`.
  - Noise model: identical to official floor ($p_1=0.001, p_2=0.005, p_{\text{readout}}=0.01$).
  - Verified with `validate_processor_d(D, required_qubits=6)` $\implies$ **VALID (0 violations)**.

### 3.3 Hardware Engineering Trade-offs
1. **Specialization vs. Generalization:** Directly embedding the PS-O1 interaction graph eliminates all SWAP routing overhead for this specific problem instance. However, if deployed on arbitrary non-isomorphic graphs (e.g. linear nearest-neighbor chains), the localized degree-4 dense clustering at nodes 3 and 4 may cause routing congestion.
2. **Physical Crosstalk and Frequency Crowding:** Implementing qubits with degree 4 in superconducting circuit QED requires 4 coupling resonators per transmon pad. This increases parasitic capacitive coupling and the likelihood of frequency collisions (cross-resonance microwave crosstalk), which commercial architectures often mitigate by restricting degree to 3 (e.g., IBM Heavy-Hex).

---

## 4. Objective 3 — QAOA Implementation and Benchmarking

### 4.1 Classical Parameter Optimization Across Multiple Initializations
In compliance with the official challenge rules, the classical optimizer was executed across 5 mandatory random initializations (seeds $0, 1, 2, 3, 4$), drawing starting angles uniformly from $[0, \pi]$. We utilized the COBYLA optimizer with exact statevector evaluation during parameter search:

| Seed | Initial $\gamma_0$ | Initial $\beta_0$ | Optimized $\gamma^*$ | Optimized $\beta^*$ | Expected Cut $\langle C \rangle$ | Approx. Ratio $r$ | Iterations |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | 2.0011 | 0.8476 | 2.9602 | -0.4071 | 15.552 | 0.7069 | 38 |
| **1** | 1.6079 | 2.9860 | 2.7641 | 4.2230 | 15.103 | 0.6865 | 45 |
| **2** | 0.8219 | 0.9377 | 2.9601 | -0.4072 | 15.552 | 0.7069 | 36 |
| **3** | **0.2691** | **0.7440** | **-0.1680** | **0.3327** | **17.713** | **0.8051** | **42** |
| **4** | 2.9627 | 1.6064 | 4.7083 | 0.8492 | 15.532 | 0.7060 | 40 |

**Solution Consistency:**
- Mean Approximation Ratio across all 5 seeds: $\bar{r} = 0.7223 \pm 0.0422$.
- The global optimum was identified at **Seed 3**, yielding optimal angles:
  $$
  \gamma^* = -0.1680, \quad \beta^* = 0.3327
  $$
  with a theoretical expected cut of $\langle C \rangle = 17.713$ ($r = 0.8051$).

### 4.2 Cross-Architecture Benchmark Results (`results/tables/results.csv`)

Sampling the bound optimal circuit with 4096 shots on Processors A, B, and D:

| Processor | Condition | Executable | Logical CX | Physical CX | Depth | 2Q Depth | SWAPs | CX Overhead | Quality Metric | Approx Ratio ($r$) | $P_{\text{opt}}$ | Classical $C^*$ | Random Baseline ($r$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A** | Ideal | `false` | 18 | — | — | — | — | — | `approx_ratio` | — | — | 22 | 0.6136 |
| **A** | Noisy | `false` | 18 | — | — | — | — | — | `approx_ratio` | — | — | 22 | 0.6136 |
| **B** | Ideal | `true` | 18 | 21 | 37 | 17 | 1 | +3 | `approx_ratio` | 0.8074 | 0.1396 | 22 | 0.6136 |
| **B** | Noisy | `true` | 18 | 21 | 37 | 17 | 1 | +3 | `approx_ratio` | 0.7874 | 0.1260 | 22 | 0.6136 |
| **D** | Ideal | `true` | 18 | **18** | **29** | **14** | **0** | **0** | `approx_ratio` | 0.8052 | 0.1384 | 22 | 0.6136 |
| **D** | Noisy | `true` | 18 | **18** | **29** | **14** | **0** | **0** | `approx_ratio` | 0.7862 | 0.1250 | 22 | 0.6136 |

### 4.3 Detailed Performance Analysis
1. **Resource Efficiency:** Processor D achieves **zero CX overhead** ($18$ CX gates vs $21$ on Processor B) and reduces two-qubit circuit depth from 17 to 14 (-17.6%). Total circuit depth is reduced from 37 to 29 (-21.6%).
2. **Algorithmic Quality vs Random Baseline:** 
   - On Processor D under official noise, QAOA samples an optimal cut with probability $P_{\text{opt}} = 12.50\%$ (512 out of 4096 shots landing on the ground-state cuts), compared to the classical uniform random probability of $3.125\%$. This represents a **$4.0\times$ enhancement in sampling probability** ($12.50\%$ vs. the classical uniform random baseline of $3.125\%$) per shot.
   - The primary approximation ratio is $r = 0.7862$, surpassing the random expectation ($0.6136$) by $+28.1\%$.
   - The maximum sampled cut reached $C = 22$ on every execution ($r_{\text{best}} = 1.0000$).
3. **Noisy Degradation:** Depolarizing noise induces a slight reduction in approximation ratio (from $0.8052$ ideal to $0.7862$ noisy on D), but the structural advantage of Processor D ensures minimal decoherence exposure due to its compacted circuit depth.

---

## 5. Visualizations & Research Communication Package

All figures were programmatically generated in both publication-grade 300 DPI raster (`.png`) and scalable vector graphics (`.svg`) formats under `results/figures/`:
1. `results/figures/network_partitioning_graph.png` (.svg): Visualizes the 6-vertex graph with edge weights, highlighting the optimal cut partition $S = \{0, 1, 3\}$ and $\bar{S} = \{2, 4, 5\}$, the 7 dashed cut edges ($W_{\text{cut}} = 22$), and 2 internal edges ($W_{\text{internal}} = 5$).
2. `results/figures/processor_topologies.png` (.svg): Side-by-side architectural layout of Processors A, B, and D, contrasting Processor A's capacity limit, Processor B's routing bottleneck (1 SWAP), and Processor D's problem-matched co-design topology (0 SWAPs, max degree $\le 4$).
3. `results/figures/bell_fidelity_comparison.png` (.svg): Point-and-whisker plot displaying Bell-state fidelities with exact standard errors across ideal and noisy conditions, accompanied by a Pauli expectation breakdown ($\langle XX \rangle, \langle YY \rangle, \langle ZZ \rangle$) demonstrating error accumulation over distance.
4. `results/figures/qaoa_cut_distribution.png` (.svg): Dual-panel visualization presenting the sampled cut probability mass function (PMF) and the staircase Complementary CDF ($P(C \ge c)$), illustrating probability concentration at $C^* = 22$ ($12.50\%$ vs $3.125\%$) and strict stochastic dominance.
5. `results/figures/processor_resource_comparison.png` (.svg): Connected-dot / dumbbell plot demonstrating quantitative hardware resource savings (CX: -14.29%, depth: -21.62%, 2Q depth: -17.65%, SWAPs: -100%).
6. `results/figures/qaoa_parameter_landscape.png` (.svg): Exact statevector expectation landscape $\langle C \rangle(\gamma, \beta)$ showing the global optimum $(\gamma^*, \beta^*) = (-0.1680, 0.3327)$ with expectation $17.7128$ ($r = 0.8051$) and the random baseline boundary (13.5).
7. `results/figures/architecture_tradeoff_map.png` (.svg): Hardware co-design Pareto frontier contrasting physical CX gate count against noisy solution quality, showing that Processor D provides hardware efficiency gains without compromising approximation quality.

### 5.1 Presentation Materials (`presentation/`)
- `presentation/VARANASI_Pitch_Deck.pptx`: Comprehensive 9-slide editable 16:9 PowerPoint pitch deck utilizing dark-slate scientific styling, high-resolution embedded figures, metric callouts, and backup defense slides.
- `presentation/VARANASI_Pitch_Deck.pdf`: High-resolution 16:9 publication PDF export of the complete deck for universal viewing.
- `presentation/speaker_notes.md`: Detailed slide-by-slide speaker notes with timing cues and key quantitative evidence.
- `presentation/pitch_script_3min.md`: Calibrated 3-minute timed spoken pitch script (~410 words).
- `presentation/pitch_script_60sec.md`: Calibrated 60-second elevator pitch script (~140 words).
- `presentation/judge_qa.md`: 16 comprehensive defense questions and evidence-backed answers addressing potential evaluator inquiries.

---

## 6. Selected Real-World Applications

While the formal Phase 2 benchmark is grounded in the locked **PS-O1: Quantum Optimization of Network Partitioning Using QAOA** instance, the underlying combinatorial formulation maps directly to core networking and telecommunications optimization challenges:

### 6.1 Interference-Aware Channel Assignment (5G/6G Frequency Planning)
- **Real-World Problem:** In dense cellular infrastructure (5G heterogeneous networks and 6G microcells), adjacent base stations transmitting on overlapping frequency carriers create mutual co-channel interference. This lowers the Signal-to-Interference-plus-Noise Ratio (SINR), degrades cell-edge spectral efficiency, and increases packet drop rates. Mobile network operators must periodically plan and re-plan frequency channel allocations across thousands of cell sites under shifting traffic distributions.
- **Quantum Mapping:** Adjacent cell towers are represented as vertices in an interference graph $G = (V, E)$, with edge weights $w_{uv}$ denoting the co-channel interference severity incurred if cells $u$ and $v$ share a frequency band. For a two-channel frequency allocation, maximizing frequency diversity across adjacent sites translates identically to the Max-Cut objective:
  $$\max_{x \in \{0, 1\}^n} \sum_{(u, v) \in E} w_{uv} (x_u + x_v - 2 x_u x_v)$$
  where binary decision variable $x_i \in \{0, 1\}$ assigns cell $i$ to Frequency Channel $A$ ($x_i = 1$) or Channel $B$ ($x_i = 0$). Edges traversed by the cut boundary connect towers operating on orthogonal channels, isolating co-channel interference.
- **Why It Fits VARANASI:** The locked 6-vertex PS-O1 instance directly provides a two-channel allocation model for a 6-cell cluster without modifying the official competition problem. *(Note: We clearly distinguish this binary Max-Cut abstraction from production-grade radio frequency planning systems, which require multi-channel chromatic coloring with $K > 2$ and dynamic power control).*
- **Mathematical Metrics & Physical Interpretation:**
  - **Exact Optimum Cut Weight ($C^*$):** $C^* = 22$ (maximum achievable cut weight out of total graph weight $W = 27$).
  - **Approximation Ratio ($r$):** Defined as achieved cut weight divided by exact optimum ($C / C^*$). For the optimal partition, $r_{\text{best}} = 22/22 = 1.0000$ ($100.00\%$). Under official noisy simulation on Processor D, the mean sampled cut weight is $\langle C \rangle = 17.297$, achieving a mean approximation ratio of $r = 0.7862$ ($78.62\%$).
  - **Fraction of Total Edge Weight Cut:** $C^* / W = 22 / 27 \approx 81.48\%$. In the interference mapping, this corresponds to assigning $81.48\%$ of the total potential co-channel interference weight between cells onto orthogonal channels, leaving $5/27 \approx 18.52\%$ residual co-channel interference on internal uncut links: $(0, 3)$ with weight 4 and $(2, 4)$ with weight 1. *(Note: This is the theoretical weighted fraction of the benchmark graph crossing the optimal cut, not an empirical measurement of physical radio interference).*
  - **Fraction of Edge Count Cut:** $7 / 9 \approx 77.78\%$ (7 of the 9 interference edges are cut).
- **Demonstration Status (Directly Supported by Repository Results):** In our 4096-shot noisy simulation on Processor D, the two optimal complementary partitions—logical vector $x = (1, 1, 0, 1, 0, 0)$ ($S=\{0, 1, 3\}, \bar{S}=\{2, 4, 5\}$, Qiskit little-endian bitstring `001011`) and $x = (0, 0, 1, 0, 1, 1)$ ($S=\{2, 4, 5\}, \bar{S}=\{0, 1, 3\}$, Qiskit little-endian bitstring `110100`)—are the two highest-probability states sampled (254 and 258 counts respectively, 512 total), combining for $P_{\text{opt}} = 12.50\%$ ($4.0\times$ the uniform random baseline of $3.125\%$). The partition cut is directly visualized in `results/figures/network_partitioning_graph.png`.

### 6.2 Traffic Engineering (Load-Balanced Routing)
- **Real-World Problem:** In telecommunications backbone and data-center networks, aggregated traffic demands must be routed across capacity-limited transport links. Inefficient routing creates hot spots and link saturation, increasing queueing delays and packet loss while parallel redundant paths remain underutilized.
- **Quantum Mapping (Simplified Two-Path Load Balancing):** The formulation models the simplified problem of balancing scalar traffic demands across two parallel paths (equivalent to binary number partitioning). For a set of traffic flows with demands $d_k$ to be split across two primary egress paths, binary variables $y_k \in \{0, 1\}$ minimize the squared aggregate load differential:
  $$\min_{y} \left( \sum_{k} d_k (2 y_k - 1) \right)^2$$
  Expanding this expression yields all-to-all quadratic interaction terms $d_j d_k (2 y_j - 1)(2 y_k - 1)$, producing an Ising Hamiltonian with dense two-qubit couplings. *(Note: This simplified model illustrates two-path load balancing only and does not solve general multi-commodity flow routing, which requires multi-hop path variables, link capacity inequalities, and flow conservation constraints).*
- **Why It Fits VARANASI:** Dense interaction topologies in load-balancing QUBOs underscore the imperative of hardware architecture co-design. While generic sparse processors suffer severe SWAP routing overhead on dense logical graphs, co-designed topologies (such as Processor D) provide direct architectural insights into minimizing two-qubit gate depth and preserving quantum coherence.
- **Demonstration Status (Proposed Architectural Extension):** This application represents a proposed architectural demonstration showing how two-path load balancing maps to QAOA; the benchmark results in this repository remain dedicated to the locked PS-O1 network partitioning instance.

---

## 7. Limitations and Future Improvements

1. **Higher Circuit Depth ($p \ge 2$):** While $p=1$ achieves $r \approx 0.79$, scaling to $p=2$ or $p=3$ would theoretically increase the ideal approximation ratio above $0.90$. However, on NISQ devices, additional layers introduce 18 more CX gates per layer, which under $p_2 = 0.005$ may degrade net fidelity without quantum error mitigation (QEM).
2. **Quantum Error Mitigation (Zero-Noise Extrapolation):** Integrating Richardson or polynomial Zero-Noise Extrapolation (ZNE) by intentionally scaling pulse durations or inserting identity CX pairs could recover the noiseless expectation value $\langle C \rangle \to 17.71$.
3. **Dynamical Decoupling (DD):** Applying XY4 or CPMG dynamical decoupling pulse sequences during idle qubit intervals on long multi-qubit paths would suppress low-frequency dephasing on physical hardware.

---

## 8. Submission Checklist & AI Disclosure

### 8.1 Submission Readiness Checklist
- [x] Same team (`VARANASI`, ID `AP251100708044`) and problem statement (`PS-O1`) preserved.
- [x] Locked instance and official settings strictly adhered to without modifications.
- [x] Objective 1 Bell-state verification exported to `results/tables/bell.csv`.
- [x] `processors/processor_D.json` fully validated with `validate_processor_d()` and frozen.
- [x] Processor topologies and architectural justification documented.
- [x] Cross-processor benchmark table exported to `results/tables/results.csv`.
- [x] Classical ground truth ($C^* = 22$) and uniform random baseline reported.
- [x] `main.ipynb` executes end-to-end within 30 minutes without errors.
- [x] AI tool disclosure fully documented in README.md and report.

### 8.2 AI Tool Disclosure
In compliance with hackathon regulations:
- **AI Tools Used:** Anthropic Claude (via Claude Sonnet 4.6), Google Antigravity Agentic Assistant.
- **Role:** Assisted in automating codebase restructuring, verifying mathematical equations, formatting figures, and drafting technical documentation. All algorithmic logic, quantum formulations, simulation executions, and numerical benchmarks were computed directly in the local Python environment using official Qiskit libraries.


---

## 9. Official Challenge Specification Compliance Appendix

This appendix documents the governing requirements from the official Phase 2 documentation distributed by the organizers:
- **Primary Source File:** `QFF2026_Optimization_Challenge_Kit.docx` (Last Modified: 29-Oct-2026 14:26:18, Size: 17,093 bytes)
- **Problem Statement Source File:** `OPTIMISATION_PS.docx` (Last Modified: 29-Oct-2026 14:26:18, Size: 17,777 bytes)
- **Judging Rubric:** `QFF_2026_Phase2_Optimization_Judging_Rubric_2page.pdf` (Last Modified: 29-Oct-2026 14:26:18, Size: 91,383 bytes)
- **Official Instructions:** `START_HERE.txt` (Last Modified: 29-Oct-2026 14:26:18, Size: 737 bytes)

### 9.1 Verification of Governing Rules

1. **Processors Benchmarked (Processors A, B, and D):**
   - *Official Citation:* `QFF2026_Optimization_Challenge_Kit.docx`, Section 12 (Frequently Asked Questions):
     > **Question:** *"Is Processor C part of Phase 2?"*
     > **Official Answer:** *"No. Phase 2 uses Processors A, B and D only."*
   - *Confirmation:* Processor C was present in certain Phase 1 general materials but is **explicitly ruled out** for Phase 2. The required benchmark uses only Processors A, B, and D.

2. **QAOA Circuit Depth ($p=1$ Required; $p=2$ Optional):**
   - *Official Citation:* `OPTIMISATION_PS.docx`, Section "PS-O1 Challenge requirements":
     > *"Implement QAOA with circuit depth parameter p = 1 (required; p = 2 optional), using a classical optimizer."*
   - *Confirmation:* Our primary published benchmark executes depth $p=1$ with multi-restart classical parameter optimization (seeds 0..4), adhering strictly to the mandatory requirement.

3. **Simulator Interface (`AerSimulator`):**
   - *Official Citation:* `QFF2026_Optimization_Challenge_Kit.docx`, Section 3 ("Official benchmark settings") and Section 12:
     > *"Simulator: AerSimulator, seed_simulator = 42"*
     > *"Do we need real IBM hardware or an IBM Quantum account? No. Everything runs on the local Aer simulator. No external data or account is needed."*
     > *"Can we use Qiskit's QAOAAnsatz, qiskit-optimization or our own QAOA code? Yes, any of these. The metrics must still come from the official transpilation in qff_phase2.py."*
   - *Confirmation:* Direct use of `AerSimulator` (with the official noise model) is the required reference execution mode. SamplerV2 is not required; the official metrics and simulator calls in `qff_phase2.py` govern all evaluations.

4. **Hardware Capacity Constraint & Infeasibility Handling:**
   - *Official Citation:* `QFF2026_Optimization_Challenge_Kit.docx`, Section 3 ("Capacity rule"):
     > *"A circuit that needs more qubits than a processor has is not run on it. PS-O1 needs 6 qubits... neither fits Processor A (5 qubits). For these problems, enter Processor A in your results table as 'not executable: needs N qubits, has 5'."*
   - *Confirmation:* Processor A is recorded as `executable: false` in `results/tables/results.csv`, preserving scientific integrity without modifying the graph.

5. **Processor D Architectural Design Constraints:**
   - *Official Citation:* `QFF2026_Optimization_Challenge_Kit.docx`, Section 5 ("Objective 2 — Processor D design rules"):
     - Rule 1: Number of qubits $\in [	ext{required}, 12]$ (PS-O1 needs 6, max 12). Processor D uses 9 qubits.
     - Rule 2: Connectivity must be a connected undirected graph. Verified (diameter 4).
     - Rule 3: Maximum node degree $\le 4$. Verified (nodes 3 and 4 have degree 4; all others $\le 3$).
     - Rule 4: Basis gate set must be exactly `['rz', 'sx', 'x', 'cx']`. Verified.
     - Rule 5: Noise rates $\ge$ official noise ($p_1 \ge 0.001, p_2 \ge 0.005, p_{	ext{readout}} \ge 0.01$). Verified.
     - Rule 6: Frozen at final commit. Verified.
   - *Confirmation:* Automated verification via `validate_processor_d(D, required_qubits=6)` returns 0 violations.

6. **Transpilation Settings, Noise Model, and Shots:**
   - *Official Citation:* `QFF2026_Optimization_Challenge_Kit.docx`, Section 3:
     - Optimization level: 1 (SABRE layout and routing, seed 42).
     - Shots: exactly 4096 per reported sampled result.
     - Noise: $p_1 = 0.001$, $p_2 = 0.005$, $p_{	ext{readout}} = 0.01$.
     - Bit ordering: Little-endian (qubit 0 is rightmost; decoded via `counts_to_x()`).
   - *Confirmation:* Exactly matches parameters in `results/raw/benchmark_metadata.json`.
