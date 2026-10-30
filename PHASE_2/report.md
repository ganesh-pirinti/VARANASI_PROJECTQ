# Technical Report: Quantum Optimization of Network Partitioning Using QAOA
## Qiskit Fall Fest 2026 — Phase 2 Optimization Track PS-O1

**Author / Team**: QFF2026 Research Engineering Team (`QFF2026_RESEARCH_TEAM` — *Pending Phase 1 Official Registration Confirmation*)  
**Clean Workspace Reference**: `C:\QFF\PS-O1_Phase2_REBUILD`  
**Execution Date**: October 30, 2026  
**System Environment**: Python 3.11, Qiskit 2.6.1, Qiskit Aer 0.18.2, NumPy 2.2.6, SciPy 1.15.3  
**Execution Mode**: Classical Numerical Simulation via Qiskit Aer (`AerSimulator`); no physical QPU hardware accessed.  

---

## Executive Summary

Combinatorial graph partitioning problems represent a ubiquitous class of NP-hard optimization challenges with critical applications in telecommunications traffic routing, distributed database sharding, and parallel computing load balancing. In Problem Statement PS-O1 of the Qiskit Fall Fest 2026 Phase 2 Optimization Track, network partitioning is formulated as a weighted Maximum Cut (Max-Cut) problem on a defined 6-vertex, 9-edge communication graph with total link weight $W = 27$.

This report documents the independent engineering, mathematical derivation, hardware-software co-design, simulation benchmarking, and error-propagated verification of the Quantum Approximate Optimization Algorithm (QAOA) for PS-O1.

### Key Verified Results:
1. **Classical Ground Truth**: Exhaustive brute-force evaluation of all $2^6 = 64$ binary states confirms the exact global maximum cut $C^* = 22$, achieved by the symmetric partition pair $S = \{0, 1, 3\}$ and $\bar{S} = \{2, 4, 5\}$ (Qiskit bitstrings `'001011'` and `'110100'`). Internal edge weights total 5 ($w_{03}=4, w_{24}=1$). The uniform random baseline cut is $13.5000$ ($r = 0.6136$).
2. **QAOA Variational Optimization**: A depth $p = 1$ QAOA ansatz optimized via COBYLA across five mandatory initial random seeds converges to $(\gamma^* = -0.1680, \beta^* = 0.3327)$ on Seed 3, producing a statevector expected cut of $\langle C \rangle = 17.7128$ and a theoretical approximation ratio of $r = 0.8051$ (+31.2% over random).
3. **Processor D Architecture**: We co-designed **Processor D** as a custom 9-qubit simulator coupling-graph model embedding all 9 problem edges natively on physical qubits $0 \dots 5$, augmented by a 4-qubit peripheral ring ($5 \to 6 \to 7 \to 8 \to 1$). Processor D adheres strictly to all official constraints (max degree $\le 4$, edge count $\le 14$, connected, planar) and was validated via `qff_phase2.validate_processor_d(d, required_qubits=6)` with **0 violations** (SHA-256: `f3f16cf1825f8365e9c0b850f4df73bc5590697c94fa1bdb8925d0801b44c4f9`).
4. **Cross-Processor Simulation Benchmarking**:
   - **Processor A** (5 qubits) is structurally non-executable (`needs 6 qubits > 5`).
   - **Processor B** (9 qubits, 12 edges) requires 1 SWAP gate, 21 CX gates, and circuit depth 37.
   - **Processor D** eliminates routing entirely (**0 SWAP gates**), achieving the **theoretical minimum CX count of 18 gates** ($-14.3\%$), while reducing circuit depth by $-21.6\%$ (29 vs 37) and two-qubit depth by $-17.6\%$ (14 vs 17).
   - Under simulated noise ($p_1 = 10^{-3}, p_2 = 5 \times 10^{-3}, p_{\text{readout}} = 10^{-2}$), Processor D achieves an approximation ratio of $r = 0.7862$ ($P_{\text{opt}} = 12.50\%$, $4.0\times$ random), comparable to Processor B ($r = 0.7874, P_{\text{opt}} = 12.60\%$). We emphasize that Processor D's verified advantage is **resource efficiency** (eliminating 100% of routing overhead), rather than an increased noisy solution quality at depth $p=1$.
5. **Bell-State Tomography on Processor D**: Simulated measurements of $|\Phi^+\rangle$ states on Processor D reveal a statistically significant fidelity drop of $\Delta \mathcal{F} = -0.0213$ ($6.37\sigma$) between native nearest neighbors ($d=1$, 1 CX, $\mathcal{F} = 0.9633 \pm 0.0021$) and distant multi-hop pairs ($d=4$, 10 CX, $\mathcal{F} = 0.9420 \pm 0.0026$), quantitatively proving the noise penalty of routing SWAPs in NISQ devices.

---

## 1. Problem Formulation and Mathematical Derivation

### 1.1 Problem Graph Specification
Let $G = (V, E)$ be the official PS-O1 graph with $|V| = 6$ vertices and $|E| = 9$ weighted edges from `instances.json`:

$$\begin{aligned}
E = \{ &(0, 2): 1, \quad (0, 3): 4, \quad (0, 4): 4, \\
       &(1, 4): 3, \quad (1, 5): 3, \quad (2, 3): 5, \\
       &(2, 4): 1, \quad (3, 4): 4, \quad (3, 5): 2 \}
\end{aligned}$$

Total edge weight is $W = \sum_{(u, v) \in E} w_{uv} = 27$.

The network partitioning problem partitions $V$ into two disjoint clusters $S$ and $\bar{S} = V \setminus S$ to maximize inter-cluster edge weights:
$$C(S) = \sum_{(u, v) \in E, u \in S, v \notin S} w_{uv}$$

### 1.2 QUBO and Ising Spin Mapping
Defining binary indicator variables $x_i \in \{0, 1\}$ ($x_i = 1$ if $i \in S$, $x_i = 0$ if $i \in \bar{S}$), an edge $(u, v)$ is cut if $x_u \neq x_v$:
$$\text{Cut}_{uv} = x_u (1 - x_v) + x_v (1 - x_u) = x_u + x_v - 2 x_u x_v$$

The total cut objective is:
$$C(x) = \sum_{(u, v) \in E} w_{uv} (x_u + x_v - 2 x_u x_v)$$

Applying the spin transformation $x_i = \frac{1 - z_i}{2}$ with $z_i \in \{-1, +1\}$:
$$x_u + x_v - 2 x_u x_v = \frac{1 - z_u z_v}{2}$$

Summing over all edges gives:
$$C(z) = \sum_{(u, v) \in E} w_{uv} \frac{1 - z_u z_v}{2} = \frac{W}{2} - \frac{1}{2} \sum_{(u, v) \in E} w_{uv} z_u z_v$$

Promoting classical spin variables to quantum Pauli-$Z$ operators ($\hat{Z}_i$), the cost Hamiltonian $\hat{H}_C$ is:
$$\hat{H}_C = \sum_{(u, v) \in E} \frac{w_{uv}}{2} \hat{Z}_u \hat{Z}_v$$

With the constant shift $\frac{W}{2} = 13.5$, the expected cut value is:
$$\langle C \rangle = 13.5 - \langle \hat{H}_C \rangle$$

### 1.3 QAOA Parameterized Circuit Ansatz ($p=1$)
The quantum circuit begins in uniform superposition $|\psi_0\rangle = H^{\otimes 6} |0\rangle^{\otimes 6}$. For depth $p = 1$, the state is:
$$|\psi(\gamma, \beta)\rangle = e^{-i \beta \hat{H}_M} e^{-i \gamma \hat{H}_C} |\psi_0\rangle$$

1. **Problem Unitary $U_C(\gamma)$**:
   $$U_C(\gamma) = \prod_{(u, v) \in E} \exp\left(-i \frac{\gamma w_{uv}}{2} \hat{Z}_u \hat{Z}_v\right) = \prod_{(u, v) \in E} R_{ZZ}^{(u, v)}(w_{uv} \gamma)$$
   where each $R_{ZZ}(\theta)$ gate is decomposed into native basis gates:
   $$\text{CX}(u, v) \to R_Z(v, \theta) \to \text{CX}(u, v)$$
   Requiring exactly $9 \times 2 = 18$ CX gates when all edges are directly coupled.
2. **Mixer Unitary $U_M(\beta)$**:
   $$U_M(\beta) = \prod_{j=0}^{5} \exp(-i \beta \hat{X}_j) = \prod_{j=0}^{5} R_X^{(j)}(2\beta)$$

---

## 2. Classical Exhaustive Ground Truth

Brute-force evaluation over all $2^6 = 64$ bitstrings establishes the definitive classical baseline:
- **Maximum Cut ($C^*$): 22**
- **Optimal Partitions**:
  - $x = (1, 1, 0, 1, 0, 0) \implies S = \{0, 1, 3\}, \bar{S} = \{2, 4, 5\}$ (Qiskit bitstring `'001011'`)
  - $x = (0, 0, 1, 0, 1, 1) \implies S = \{2, 4, 5\}, \bar{S} = \{0, 1, 3\}$ (Qiskit bitstring `'110100'`)
- **Internal Edges**: Edge $(0, 3)$ with weight 4 and edge $(2, 4)$ with weight 1 (total internal weight = 5).
- **Cut Fraction**: $22 / 27 \approx 81.48\%$
- **Uniform Random Baseline**:
  $$\langle C \rangle_{\text{random}} = \frac{W}{2} = 13.5000 \implies r_{\text{random}} = \frac{13.5}{22} \approx 0.6136, \quad P_{\text{opt, random}} = \frac{2}{64} = 0.03125$$

---

## 3. QAOA Variational Optimization

COBYLA optimization across the five mandatory initialization seeds ($s \in \{0, 1, 2, 3, 4\}$) with initial parameters drawn via `rng = np.random.default_rng(seed); rng.uniform(0.0, np.pi, size=2)` produced the following trajectories:

| Seed | Initial $(\gamma_0, \beta_0)$ | Final $\gamma^*$ | Final $\beta^*$ | Expected Cut $\langle C \rangle$ | Approx. Ratio $r$ | Iterations | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | (2.0011, 0.8476) | 2.9604 | -0.4071 | 15.5515 | 0.7069 | 43 | Converged |
| 1 | (1.6079, 2.9860) | 2.9607 | 4.2997 | 15.5510 | 0.7069 | 80 | MaxIter (Terminated) |
| 2 | (0.8219, 0.9377) | 2.9605 | -0.4072 | 15.5515 | 0.7069 | 36 | Converged |
| **3** | **(0.2691, 0.7440)** | **-0.1680** | **0.3327** | **17.7128** | **0.8051** | **37** | **Converged (Best Observed)** |
| 4 | (2.9627, 1.6064) | 4.7080 | 0.8494 | 15.5324 | 0.7060 | 49 | Converged |

**Observations and Ensemble Statistics**:
- **Trajectory Differences**: Seed 1 reached the maximum iteration budget (`MaxIter` = 80) without full convergence. Seeds 0, 2, and 4 converged to suboptimal local plateaus ($\langle C \rangle \approx 15.53$–$15.55$, $r \approx 0.7060$–$0.7069$), illustrating the non-convex multi-modal landscape of QAOA even at $p=1$.
- **Best Observed Initialization**: Seed 3 produced the best observed result among the five starts, uniquely converging to the lowest energy basin on this grid with $\langle C \rangle = 17.7128$ ($r = 0.8051$, a $+31.2\%$ improvement over the uniform random expectation of $13.5000$).
- **Ensemble Summary**: Across the five initializations, the mean approximation ratio is $\bar{r} = 0.7264 \pm 0.0440$, and the mean expected cut is $\overline{\langle C \rangle} = 15.98 \pm 0.97$.
- **Angle Coordinate Properties**: The negative angle $\gamma^* = -0.1680$ for Seed 3 is a valid equivalent minimum resulting from unconstrained directional updates in the $2\pi$-periodic $R_{ZZ}$ parameter space ($\gamma^* \equiv 2\pi - 0.1680 \approx 6.115$).
- **Distinction from Combinatorial Optimum**: The best continuous variational expectation ($\langle C \rangle = 17.7128$) is strictly distinct from the exact combinatorial maximum cut ($C^* = 22$), which is extracted upon projective computational basis sampling ($P_{\text{opt}} \approx 12.50\%$).

---

## 4. Hardware Co-Design: Processor D

Processor D is a **custom simulator coupling-graph model** designed for superconducting transmon layouts:
- **Footprint**: 9 physical qubits ($Q_0 \dots Q_8$).
- **Coupling Topology**: 13 undirected edges:
  - 9 core edges embedding the problem graph: $(0,2), (0,3), (0,4), (1,4), (1,5), (2,3), (2,4), (3,4), (3,5)$.
  - 4 peripheral ring edges: $(5,6), (6,7), (7,8), (8,1)$.
- **Validation**: Validated via `qff_phase2.validate_processor_d(d, required_qubits=6)` with **0 violations** (Max degree $\le 4$, edge count $\le 14$, connected, planar).
- **Configuration SHA-256**: `f3f16cf1825f8365e9c0b850f4df73bc5590697c94fa1bdb8925d0801b44c4f9`.

---

## 5. Bell-State Tomography on Processor D (Simulated Measurements)

To isolate and quantify the simulated decoherence and gate infidelity introduced by multi-hop routing, we prepared the Bell state $|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$ on Processor D across two pairs:
- **Adjacent Pair $(0, 2)$**: Distance $d = 1$, 1 direct CX gate.
- **Distant Pair $(0, 7)$**: Distance $d = 4$, 10 CX gates (including multi-hop routing SWAPs).

State tomography was conducted across Pauli bases $XX$, $YY$, and $ZZ$ (4096 shots/basis):

| Qubit Pair | Distance | CX | Condition | $\langle ZZ \rangle$ | $\langle XX \rangle$ | $\langle YY \rangle$ | Fidelity $\mathcal{F}$ | Uncertainty $SE(\mathcal{F})$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $(0, 2)$ | 1 | 1 | Ideal | +1.0000 | +1.0000 | -1.0000 | **1.0000** | $\pm 0.0000$ |
| $(0, 2)$ | 1 | 1 | Noisy | +0.9551 | +0.9458 | -0.9521 | **0.9633** | $\pm 0.0021$ |
| $(0, 7)$ | 4 | 10 | Ideal | +1.0000 | +1.0000 | -1.0000 | **1.0000** | $\pm 0.0000$ |
| $(0, 7)$ | 4 | 10 | Noisy | +0.9399 | +0.9243 | -0.9038 | **0.9420** | $\pm 0.0026$ |

The simulated fidelity drop is $\Delta \mathcal{F} = -0.0213 \pm 0.0033$, yielding a significance of **$6.37\sigma$**. This provides definitive simulated evidence that routing SWAPs degrade quantum state fidelity. All 12 individual measurement circuits (2 pairs $\times$ 2 conditions $\times$ 3 bases) are recorded in `results/tables/bell_circuits.csv`, and all raw 4096-shot measurement count dictionaries are preserved in `results/raw/bell_counts.json`.

---

## 6. Cross-Processor Benchmarking Simulation Results

The compiled QAOA circuits were simulated across Processors A, B, and D with 4096 shots:

| Processor | Condition | Executable | SWAPs | CX Gates | Circuit Depth | 2Q Depth | Mean Cut $\langle C \rangle$ | Approx Ratio $r$ | $P_{\text{opt}}$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Processor A** | N/A | **No** | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **Processor B** | Ideal | Yes | 1 | 21 | 37 | 17 | 17.7620 | 0.8074 | 0.1396 |
| **Processor B** | Noisy | Yes | 1 | 21 | 37 | 17 | 17.3220 | 0.7874 | 0.1260 |
| **Processor D** | Ideal | Yes | 0 | 18 | 29 | 14 | 17.7134 | 0.8052 | 0.1384 |
| **Processor D** | Noisy | Yes | 0 | 18 | 29 | 14 | 17.2971 | 0.7862 | 0.1250 |
| **Random Baseline** | Analytic | Yes | N/A | N/A | N/A | N/A | 13.5000 | 0.6136 | 0.0313 |
| **Classical Ground Truth** | Brute-force | Yes | N/A | N/A | N/A | N/A | 22.0000 | 1.0000 | N/A |

### Objective Discussion:
- **Resource Savings**: Processor D reduces CX gate count from 21 to 18 ($-14.3\%$), total circuit depth from 37 to 29 ($-21.6\%$), and two-qubit depth from 17 to 14 ($-17.6\%$) by requiring **0 SWAP gates**.
- **Sampled Solution Quality & Standard Error**:
  - Processor B (Noisy, 4096 shots): Sampled mean cut $\langle C \rangle = 17.3220 \pm 0.0598$, corresponding to approximation ratio $r = 0.7874 \pm 0.0027$ ($17.3220 / 22 = 0.7874$), $P_{\text{opt}} = 12.60\% \pm 0.52\%$.
  - Processor D (Noisy, 4096 shots): Sampled mean cut $\langle C \rangle = 17.2971 \pm 0.0612$, corresponding to approximation ratio $r = 0.7862 \pm 0.0028$ ($17.2971 / 22 = 0.7862$), $P_{\text{opt}} = 12.50\% \pm 0.52\%$.
  - Numerical difference (B - D): $\Delta \langle C \rangle = 0.0249 \pm 0.0856$, $\Delta r = 0.0011 \pm 0.0039$.
  - Hypothesis testing: $z = \frac{0.024902}{0.085588} = 0.2910\sigma$ ($p = 0.7711$). Under 4096 shots, the difference in sampled mean cut is not statistically significant.
  - **Distributional Nuance**: A failure to detect a statistically significant difference in sampled mean cut does not prove that the underlying 64-element output distributions are identical. Transpilation targeting Processor B introduces a physical SWAP gate with three additional CX operations, which perturbs transition probabilities across specific bitstring paths even if the expectation value $\langle C \rangle$ remains within sampling error.
- **Honest Finding and Depth Scaling Potential**: Processor D does not show a superior noisy approximation ratio over Processor B at depth $p=1$ because a single SWAP gate introduces limited error. However, Processor D eliminates routing SWAPs entirely, which represents future potential to prevent cumulative error escalation if the QAOA ansatz is scaled to higher depths ($p \ge 2$), though depth $p=1$ was the required and evaluated scope of this benchmark.

---

## 7. Conclusions

This project rigorously implements and validates the QAOA pipeline for PS-O1 network partitioning. By co-designing physical processor connectivity to match the problem graph, Processor D achieves zero-SWAP compilation, eliminating routing overhead. All models, simulation results, figures, and automated test suites are verified and ready for independent evaluation.

---

## 8. AI Tool Use & Pair Programming Disclosure

In accordance with the hackathon rules and academic ethics guidelines:
- **Assisting Technology:** Antigravity AI was employed as an interactive pair-programming assistant for boilerplate generation, script formatting, test harness configuration, and document drafting.
- **Human Authorship & Rigor:** All theoretical formulations, QUBO derivations, cost Hamiltonian energy offsets, QAOA parameterized circuit designs, Processor D topology matrices, multi-restart optimization protocols, and error analyses were designed, audited, and verified by the human research engineering team (`QFF2026_RESEARCH_TEAM` — *Pending Phase 1 Official Registration Confirmation*). All executions were carried out locally via official Qiskit 2.6 and Aer 0.18 simulator libraries without ungrounded approximations or external data imports.

