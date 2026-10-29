# VARANASI — Research & Implementation Report
## Quantum Optimization of Network Partitioning Using QAOA: Hardware Co-Design Paradigm, Classical Ground Truth, and Transpilation Analysis

**Track:** Optimization  
**Competition:** Qiskit Fall Fest 2026 — SRM University-AP  
**Problem Statement Code:** `PS-O1` (Network Partitioning / Weighted Max-Cut)  
**Registered Team Name:** `VARANASI`  
**Official Team / Participant ID:** `AP251100708044`  
**Team Leader:** Ganesh Pirinti (`ganeshpirinti95218@gmail.com`)  
**Team Member:** Mohammed Sadiq (`sadiqmohammedkhan12@gmail.com`)  
**Host Institution:** SRM University-AP, Andhra Pradesh  
**Repository:** [https://github.com/ganesh-pirinti/VARANASI_PROJECTQ](https://github.com/ganesh-pirinti/VARANASI_PROJECTQ)  
**Date:** October 2026 (Phase 2 Final Submission)  

---

## 1. Executive Summary

In current Noisy Intermediate-Scale Quantum (NISQ) devices, compiler-driven routing overhead represents a primary bottleneck to algorithmic success. When mapping an optimization problem's interaction graph onto a sparse physical coupling topology, compilers must insert SWAP networks to bring non-adjacent qubits into mutual interaction. Because physical two-qubit gates are the dominant source of decoherence ($p_2 = 0.005$ vs. $p_1 = 0.001$), these additional operations degrade circuit fidelity and inflate execution depth.

**Team VARANASI** presents an end-to-end, mathematically verified study for Problem Statement **PS-O1** (Network Partitioning via QAOA) demonstrating a **hardware co-design paradigm**. By engineering a 9-qubit processor architecture (**Processor D**) whose native coupling graph embeds the 9 interaction edges of the locked PS-O1 instance, we achieve **100% elimination of routing SWAPs** (0 SWAPs vs. 1 SWAP on generic Processor B). This saves **14.29% physical CX gates** (18 vs. 21) and compresses **circuit depth by 21.62%** (29 vs. 37) and **two-qubit depth by 17.65%** (14 vs. 17).

Under the official depolarizing and readout noise model with 4,096 shots, QAOA ($p=1$) on Processor D achieves an approximation ratio of $r = 0.7862$ (mean cut $\langle C \rangle = 17.297$), which is numerically similar to Processor B ($r = 0.7874$, delta $\Delta r = -0.0012$, within finite-shot standard error $\text{SE}_r \approx 0.0028$). Crucially, QAOA concentrates probability mass onto the exact optimal cut ($C^* = 22$) with $P_{\text{opt}} = 12.50\%$ (512 / 4096 shots), representing a **$4.0\times$ optimal-solution sampling probability enhancement** over uniform random guessing ($3.125\%$).

---

## 2. Official Problem Statement & Compliance Decision

### 2.1 Problem Assignment Verification
From the official Phase 2 documentation (`START_HERE.txt`, `OPTIMISATION_PS.docx`, and `QFF2026_Optimization_Challenge_Kit.docx`), the governance rules mandate:
- *"Continue with the SAME team and SAME problem statement as Phase 1."*
- Team VARANASI was assigned and qualified under **PS-O1: Quantum Optimization of Network Partitioning Using QAOA**.
- The primary evaluation is conducted strictly on the locked 6-vertex, 9-weighted-edge PS-O1 benchmark graph from `instances.json`.
- Exploratory extensions (such as PS-O3 Knapsack resource allocation) are presented as clearly separated research modules and do not overwrite or replace official PS-O1 metadata.

### 2.2 Phase 2 Compliance Rules Summary
- **Processor Scope:** Processors A, B, and D are evaluated. Processor C is explicitly ruled out in Section 12 FAQ of the Challenge Kit (*"Is Processor C part of Phase 2? No. Phase 2 uses Processors A, B and D only"*).
- **Processor D Constraints:** Maximum 12 qubits (VARANASI uses 9); connected topology; maximum vertex degree $\le 4$ (nodes 3 and 4 have degree 4; all others degree 2 or 3); basis gates `['rz', 'sx', 'x', 'cx']`.
- **QAOA Depth:** Depth $p=1$ is mandatory; $p=2$ is optional.
- **Simulator & Noise:** Local `AerSimulator` from `qiskit_aer` executing with official seeds (`SEED=42`), 4,096 shots, 1-qubit depolarizing $p_1=0.001$, 2-qubit depolarizing $p_2=0.005$, and symmetric readout bit-flip $p_{\text{readout}}=0.01$.

---

## 3. Real-World Motivation: Why Network Partitioning Matters

Network bi-partitioning is a foundational NP-hard combinatorial problem with direct applications across telecommunications, wireless spectrum allocation, and distributed computing:

### 3.1 Interference-Aware Frequency Channel Planning (5G/6G Microcells)
In dense cellular networks, base stations sharing adjacent physical coverage areas generate mutual co-channel interference if assigned identical radio frequency bands. This interference degrades the Signal-to-Interference-plus-Noise Ratio (SINR), reduces throughput, and causes packet drops.
- **Problem Formulation:** We represent base stations as vertices $V$ and potential co-channel interference penalties as weighted edges $w_{uv} \in E$.
- **Two-Channel Allocation:** Partitioning the network into two orthogonal frequency bands $A$ ($x_i = 1$) and $B$ ($x_i = 0$) maximizes inter-channel isolation by placing adjacent high-interference towers into opposite frequency bands.
- **Objective:** Maximizing the total weight of cut edges minimizes the residual internal co-channel interference.

### 3.2 Real-Life Scope & Limitations
In our 6-node benchmark graph, the optimal cut $C^* = 22 / 27$ separates $81.48\%$ of the total potential interference weight onto orthogonal channels, leaving $18.52\%$ ($5/27$) on internal uncut edges: $(2, 4)$ with weight 1 and $(3, 4)$ with weight 4.  
*Caveat:* We present this as an illustrative application mapping of binary Max-Cut; production-grade radio frequency planning involves multi-channel chromatic coloring ($K > 2$), power control, and dynamic traffic scheduling.

---

## 4. Mathematical Formulation & Cost Hamiltonian

### 4.1 Quadratic Unconstrained Binary Optimization (QUBO)
Let $G = (V, E, w)$ be an undirected graph with vertices $V = \{0, 1, \dots, n-1\}$ and edge weights $w_{uv} > 0$. Each vertex is assigned a binary decision variable $x_i \in \{0, 1\}$.
An edge $(u, v)$ is cut if and only if $x_u \ne x_v$. The total cut weight objective is:
$$C(x) = \sum_{(u, v) \in E} w_{uv} (x_u + x_v - 2 x_u x_v)$$

### 4.2 Mapping to Ising Spin Variables
To construct the quantum cost Hamiltonian, binary variables are mapped to Pauli-$Z$ operators via the transformation:
$$x_i = \frac{I - Z_i}{2}$$
Substituting into the objective:
$$x_u + x_v - 2 x_u x_v = \frac{I - Z_u Z_v}{2}$$
Thus, the cost Hamiltonian becomes:
$$\hat{H}_C = \sum_{(u, v) \in E} \frac{w_{uv}}{2} (I - Z_u Z_v)$$
Dropping the constant energy shift $\sum_{(u, v)} \frac{w_{uv}}{2} I$, the problem Hamiltonian to be minimized is:
$$\hat{H}_{\text{problem}} = -\frac{1}{2} \sum_{(u, v) \in E} w_{uv} (I - Z_u Z_v)$$

### 4.3 Mixer Hamiltonian
The transverse field mixer Hamiltonian drives transitions between computational basis states:
$$\hat{H}_M = \sum_{i=0}^{n-1} X_i$$
where $X_i$ is the Pauli-$X$ operator acting on qubit $i$.

---

## 5. Input Data & Provenance

The PS-O1 instance is permanently frozen in `data/instance.json` (SHA-256: `fba157735abec12ab24b51aa5f1270fb94de086da4eea965f2135d6c278f9fa0`).
- **Vertices:** $n = 6$ (indices $0, 1, 2, 3, 4, 5$)
- **Weighted Edges:** 9 edges:
  $$\{(0,2,1), (0,3,4), (0,4,4), (1,4,3), (1,5,3), (2,3,5), (2,4,1), (3,4,4), (3,5,2)\}$$
- **Total Graph Weight:** $W = 1 + 4 + 4 + 3 + 3 + 5 + 1 + 4 + 2 = 27$

---

## 6. Classical Ground Truth & Exhaustive Baseline

Because $n = 6$, the state space consists of $2^6 = 64$ binary states, allowing exhaustive classical evaluation in under 1 millisecond.

### 6.1 Exact Enumeration Results
- **Maximum Cut Weight ($C^*$):** $22$
- **Total Graph Weight ($W$):** $27$
- **Weighted Cut Fraction:** $22 / 27 = 81.4815\%$
- **Edge-Count Cut Fraction:** $7 / 9 = 77.7778\%$
- **Optimal States:** Exactly 2 bitwise-complement states:
  1. $x = (1, 1, 0, 1, 0, 0) \implies S = \{0, 1, 3\}, \quad \bar{S} = \{2, 4, 5\}$ (Qiskit bitstring `001011`)
  2. $x = (0, 0, 1, 0, 1, 1) \implies S = \{2, 4, 5\}, \quad \bar{S} = \{0, 1, 3\}$ (Qiskit bitstring `110100`)

### 6.2 Uniform Random Guessing Baseline
Across all 64 states with equal probability $1/64$:
- **Mean Cut:** $\mu_{\text{random}} = 13.5000$
- **Approximation Ratio:** $r_{\text{random}} = 13.50 / 22 = 0.613636\dots$
- **Optimal Hit Probability:** $P_{\text{opt, random}} = 2 / 64 = 0.03125$ ($3.125\%$)

This provides an immutable reference: any valid QAOA implementation must significantly surpass $r = 0.6136$ and $P_{\text{opt}} = 3.125\%$.

---

## 7. Quantum Circuit Construction & Gate Decomposition

### 7.1 Initial State Preparation
The circuit initializes in a uniform superposition over all $2^6 = 64$ computational basis states using single-qubit Hadamard gates:
$$|\psi_0\rangle = |+\rangle^{\otimes 6} = \frac{1}{\sqrt{64}} \sum_{x \in \{0, 1\}^6} |x\rangle$$

### 7.2 Cost Unitary Evolution
For depth $p=1$, the cost unitary is:
$$U(C, \gamma) = \exp(-i \gamma \hat{H}_C) = \prod_{(u, v) \in E} \exp\left( -i \gamma \frac{w_{uv}}{2} (I - Z_u Z_v) \right)$$
Using basis gates `['rz', 'sx', 'x', 'cx']`, each two-qubit term $\exp(i \frac{\gamma w_{uv}}{2} Z_u Z_v)$ decomposes into:
$$\text{CX}(u, v) \longrightarrow R_Z(\gamma \cdot w_{uv}, v) \longrightarrow \text{CX}(u, v)$$
For 9 edges, this requires exactly $9 \times 2 = 18$ logical CX gates.

### 7.3 Mixer Unitary Evolution
The mixer unitary rotates each qubit around the $X$-axis:
$$U(M, \beta) = \exp(-i \beta \hat{H}_M) = \prod_{i=0}^{n-1} R_X(2 \beta, i)$$
In the basis set `['rz', 'sx', 'x']`, $R_X(\theta) = R_Z(\pi/2) \cdot SX \cdot R_Z(\theta + \pi) \cdot SX \cdot R_Z(5\pi/2)$.

---

## 8. Hybrid Optimization Loop & Convergence

The hybrid variational loop optimizes parameters $(\gamma, \beta)$ to maximize the expected cut value:
$$\langle C \rangle(\gamma, \beta) = \langle \psi(\gamma, \beta) | \hat{H}_C | \psi(\gamma, \beta) \rangle$$
- **Classical Optimizer:** COBYLA (Constrained Optimization BY Linear Approximation).
- **Objective Function:** Negative statevector expectation value $-\langle C \rangle$.
- **Multi-Seed Restarts:** To avoid local minima, optimization was executed across 5 random initial seeds ($0, 1, 2, 3, 4$), drawing starting angles from $[0, \pi]$.
- **Convergence:** Seed 3 converged to the global maximum:
  $$\gamma^* = -0.16801984, \quad \beta^* = 0.33266185$$
  $$\text{Theoretical Expectation } \langle C \rangle = 17.7128, \quad r_{\text{theoretical}} = 0.805128$$
- Across all 5 seeds, the mean theoretical ratio was $0.7264 \pm 0.0394$.

---

## 9. Hardware Topologies & Transpilation Analysis

### 9.1 Processor Comparison

| Processor | Qubits | Coupling Topography | PS-O1 Executable | Routing SWAPs | Physical CX | Total Depth | 2Q Depth |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Processor A** | 5 | Linear tree (`0-1-2`, `1-3-4`) | **`false`** | — | — | — | — |
| **Processor B** | 9 | Heavy-hex grid subgraph | **`true`** | **1** | **21** | **37** | **17** |
| **Processor D** | 9 | Native core (0–5) + Ancilla ring (6–8) | **`true`** | **0** | **18** | **29** | **14** |

### 9.2 The Routing Bottleneck on Processor B
Processor B possesses 9 physical qubits with 12 coupling edges. However, the physical placement lacks a direct edge corresponding to problem interaction $(1, 4)$.  
During transpilation at Optimization Level 1, SABRE inserts **1 SWAP gate** between qubits 1 and 4. A SWAP decomposes into 3 physical CX gates:
$$\text{SWAP}(u, v) = \text{CX}(u, v) \cdot \text{CX}(v, u) \cdot \text{CX}(u, v)$$
This increases physical CX gates from 18 to 21 (+16.7% overhead) and two-qubit depth from 14 to 17 (+21.4% overhead).

### 9.3 The Co-Design Solution on Processor D
Processor D features 9 qubits arranged in two coordinated subgraphs:
1. **Core Problem Subgraph (Qubits 0–5):** Natively embeds all 9 edges of the PS-O1 graph: `(0,2), (0,3), (0,4), (1,4), (1,5), (2,3), (2,4), (3,4), (3,5)`. Every logical two-qubit interaction exists physically.
2. **Ancillary Closed Ring (Qubits 6–8):** Closed routing ring connecting `(5,6), (6,7), (7,8), (8,1)`.
3. **Degree Limit Compliance:** Node degrees are $\{3, 3, 3, 4, 4, 3, 2, 2, 2\}$. The maximum node degree is 4 (at nodes 3 and 4), strictly satisfying the official rule $\le 4$.
Because all problem edges exist physically, the compiler requires **0 SWAP gates** and compiles with the minimum possible **18 physical CX gates**.

---

## 10. Objective 1: Quantum Hardware Diagnostic (Bell State Tomography)

To verify the physical fidelity of Processor D prior to executing optimization algorithms, we performed quantum state tomography on the maximally entangled Bell state:
$$|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$$
across near and far qubit pairs using 4,096 shots per measurement basis ($XX, YY, ZZ$).

### 10.1 Tomography Results

| Pair Type | Physical Qubits | Graph Distance | Condition | CX Count | $\langle XX \rangle \pm \text{SE}$ | $\langle YY \rangle \pm \text{SE}$ | $\langle ZZ \rangle \pm \text{SE}$ | Fidelity $F \pm \text{SE}$ |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Near** | $(0, 2)$ | 1 | Ideal | 1 | $+1.0000 \pm 0.0000$ | $-1.0000 \pm 0.0000$ | $+1.0000 \pm 0.0000$ | **$1.0000 \pm 0.0000$** |
| **Near** | $(0, 2)$ | 1 | Noisy | 1 | $+0.9458 \pm 0.0051$ | $-0.9521 \pm 0.0048$ | $+0.9551 \pm 0.0046$ | **$0.9633 \pm 0.0021$** |
| **Far** | $(0, 7)$ | 4 | Ideal | 10 | $+1.0000 \pm 0.0000$ | $-1.0000 \pm 0.0000$ | $+1.0000 \pm 0.0000$ | **$1.0000 \pm 0.0000$** |
| **Far** | $(0, 7)$ | 4 | Noisy | 10 | $+0.9243 \pm 0.0060$ | $-0.9038 \pm 0.0067$ | $+0.9399 \pm 0.0053$ | **$0.9420 \pm 0.0026$** |

### 10.2 Physical Gate Error Accumulation
- For distance 1, preparation requires 1 CX gate, yielding fidelity $F = 0.9633$.
- For distance 4, routing across the ancillary ring requires 3 SWAPs (9 CX) plus 1 entangling CX (10 total CX gates), reducing fidelity to $F = 0.9420$.
- The 2.13 percentage-point drop directly quantifies the cumulative effect of multi-hop CX depolarizing error ($p_2 = 0.005$) and readout errors ($p_{\text{readout}} = 0.01$), validating our hardware noise simulation.

---

## 11. Empirical QAOA Sampling & Statistical Rigor

### 11.1 Official Benchmark Table (`results/tables/results.csv`)

| Processor | Condition | Executable | Logical CX | CX | Depth | 2Q Depth | SWAPs | Approx Ratio $r$ | $P_{\text{opt}}$ | Optimal Counts |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Processor A** | Ideal / Noisy | `false` | 18 | — | — | — | — | — | — | 0 / 4096 |
| **Processor B** | Ideal | `true` | 18 | 21 | 37 | 17 | 1 | 0.8074 | 13.96% | 572 / 4096 |
| **Processor B** | Noisy | `true` | 18 | 21 | 37 | 17 | 1 | 0.7874 | 12.60% | 516 / 4096 |
| **Processor D** | Ideal | `true` | 18 | **18** | **29** | **14** | **0** | 0.8052 | 13.84% | 567 / 4096 |
| **Processor D** | Noisy | `true` | 18 | **18** | **29** | **14** | **0** | 0.7862 | 12.50% | 512 / 4096 |

### 11.2 Addressing Statistical Equivalence
Notice that Processor D's noisy approximation ratio ($r = 0.7862$) is slightly lower than Processor B ($r = 0.7874$).  
**We do not claim that Processor D produces a higher mean cut quality than Processor B.**  
Here is the exact statistical calculation:
- Sample size: $N = 4,096$ shots per run.
- Standard deviation of sampled cuts: $\sigma \approx 3.9$, yielding a standard error of the mean cut $\text{SE}_{\langle C \rangle} = 3.9 / \sqrt{4096} \approx 0.061$.
- Standard error of the approximation ratio: $\text{SE}_r = 0.061 / 22 \approx 0.0028$.
- Observed delta: $\Delta r = 0.7862 - 0.7874 = -0.0012$ (a relative difference of $-0.15\%$).
Because $|\Delta r| < \text{SE}_r$, this delta is **numerically indistinguishable within finite-shot sampling noise**.  
Processor D's genuine, verified scientific contribution is **architectural**: achieving identical solution fidelity while saving 14.3% CX gates, 21.6% depth, and 100% of routing SWAPs.

### 11.3 4.0x Sampling Enhancement vs. Algorithmic Speedup
We state clearly that this experiment does **not** demonstrate quantum algorithmic speedup or quantum supremacy:
1. On 6 variables ($2^6 = 64$ states), classical enumeration takes less than 1 millisecond.
2. What QAOA achieves is a **$4.0\times$ optimal-solution sampling probability enhancement**: Processor D samples the optimal cut ($C^* = 22$) with $12.50\%$ probability (512 / 4096 shots), compared to only $3.125\%$ (2 / 64) for uniform random guessing.
3. The Complementary CDF $P(C \ge c)$ proves that QAOA strictly stochastically dominates the random baseline for all cut thresholds $c \ge 14$.

---

## 12. Exploratory Scenario: Resource-Constrained Knapsack (PS-O3)

To explore how quantum optimization extends to constrained resource selection, we analyzed the official PS-O3 Knapsack instance from `instances.json`.

### 12.1 Problem Definition
- 5 items with values $v = [10, 4, 7, 5, 8]$ and weights $w = [5, 3, 4, 2, 6]$.
- Vehicle capacity constraint: $W_{\text{cap}} = 15$.
- Binary decision variables: $x_i \in \{0, 1\}$.

### 12.2 QUBO Penalty Formulation
To encode the capacity inequality $\sum_i w_i x_i \le W_{\text{cap}}$, 4 binary slack variables $s = s_0 + 2 s_1 + 4 s_2 + 8 s_3$ ($s \in [0, 15]$) are introduced, requiring 9 total qubits ($x_0..x_4$ and $s_5..s_8$). The penalized QUBO objective is:
$$\min_{x, s} -\sum_{i=0}^4 v_i x_i + P \cdot \left( \sum_{i=0}^4 w_i x_i + \sum_{k=0}^3 2^k s_k - 15 \right)^2$$
where $P = 5$ is the penalty weight.

### 12.3 Exact Classical Enumeration
Evaluating all $2^5 = 32$ subsets confirms:
- **Maximum Feasible Value:** $V^* = 26$
- **Optimal Item Selection:** $\{0, 1, 2, 3\}$ (items: Emergency Water Kit, Trauma Pack, Radio Comms, Thermal Blankets).
- **Total Weight:** $5 + 3 + 4 + 2 = 14 \le 15$ (Capacity utilization: $14 / 15 = 93.3\%$).

---

## 13. Limitations & Engineering Trade-offs

1. **Topology Specialization vs. Generalization:** Direct embedding of the PS-O1 graph on Processor D maximizes performance for this instance, but would incur routing overhead if compiled with a non-isomorphic problem graph.
2. **Physical Crosstalk Risks:** Raising node degree to 4 introduces higher capacitive coupling and frequency crowding risks in real superconducting transmon processors.
3. **Absence of Quantum Error Mitigation (QEM):** At depth $p=1$, bare noisy simulation yields $r = 0.7862$. Applying Zero-Noise Extrapolation (ZNE) could extrapolate the expectation value toward the ideal statevector bound ($17.71$).

---

## 14. Verification & Reproducibility Guide

The entire codebase is verified and deterministically reproducible in seconds:
```powershell
# 1. Verify exact ground truth and raw histograms (14 tests)
python -m unittest tests/test_raw_results.py -v

# 2. Run consolidated 8-stage verification suite
python tests/consolidated_test_suite.py

# 3. Regenerate all 7 scientific figures (PNG + SVG)
python -m src.visualizations

# 4. Rebuild the PowerPoint (.pptx) and Publication PDF (.pdf) pitch decks
python scripts/generate_pitch_deck.py

# 5. Export studio data payload for the interactive web frontend
python scripts/export_studio_data.py
```

---

## 15. AI Tool Disclosure

In compliance with hackathon guidelines:
- **AI Tools Used:** Large Language Model coding assistants (Claude 3.7 / 3.8 via Cursor / Antigravity).
- **Role:** Script scaffolding, Markdown formatting, LaTeX notation typing, and drafting test harnesses.
- **Scientific Responsibility:** All mathematical formulations, Hamiltonian derivations, topology co-design choices, parameter optimization, and statistical evaluations were formulated, audited, and verified by Team VARANASI.

---

## 16. References

1. Farhi, E., Goldstone, J., & Gutmann, S. (2014). *A Quantum Approximate Optimization Algorithm*. arXiv:1411.4028.
2. Qiskit Team. (2024). *Qiskit: An Open-Source Framework for Quantum Computing*. DOI: 10.5281/zenodo.2573505.
3. SRM University-AP Hackathon & Competitions Cell. (2026). *Qiskit Fall Fest 2026 — Optimization Track Challenge Kit & Problem Statement PS-O1*.
4. Lucas, A. (2014). *Ising formulations of many NP problems*. Frontiers in Physics, 2, 5.
5. Li, G., Ding, Y., & Xie, Y. (2020). *Tackling the qubit mapping problem for NISQ-era quantum devices*. ASPLOS '20, pp. 1001–1014.
