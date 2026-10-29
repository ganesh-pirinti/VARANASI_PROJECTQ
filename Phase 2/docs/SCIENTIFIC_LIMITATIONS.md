# VARANASI — Scientific Limitations, NISQ Realities, and Responsible Quantum Claims

**Project:** VARANASI  
**Event:** Qiskit Fall Fest 2026 — SRM University-AP  
**Track:** Quantum Optimization  
**Problem Statement:** PS-O1: Quantum Optimization of Network Partitioning Using QAOA  
**Document Purpose:** Transparent disclosure of theoretical, architectural, and experimental boundaries governing the VARANASI project.

---

## 1. Classical Tractability vs. Quantum Advantage

### 1.1 The 64-State Search Space
The official PS-O1 benchmark consists of a locked 6-vertex, 9-edge weighted graph ($W=27$). The entire state space contains exactly:
$$2^6 = 64 \text{ possible binary partition assignments}$$
An exhaustive classical evaluation of all 64 assignments executes in less than **$1 \text{ millisecond}$** on standard commodity hardware. The exact maximum cut ($C^* = 22$) is established unequivocally.

### 1.2 Refusal of Quantum Advantage Claims
In accordance with scientific integrity guidelines:
- **No Quantum Advantage or Quantum Supremacy:** A 6-qubit QAOA simulation does not, and cannot, establish quantum advantage over classical computation.
- **No Algorithmic Speedup:** The observed $4.0\times$ enhancement in optimal-solution sampling probability ($12.50\%$ on Processor D vs. $3.125\%$ uniform random baseline) represents **quantum state concentration**, not a runtime or computational complexity speedup.
- **Pedagogical and Engineering Value:** The scientific merit of this project lies in demonstrating **hardware-software co-design**, gate-level compilation overheads, transpiler routing bottlenecks, and the empirical impact of simulated depolarizing noise on discrete optimization.

---

## 2. NISQ Simulation vs. Physical Quantum Hardware

### 2.1 Simulation Boundary
All benchmark results reported in `results/tables/results.csv`, `results/tables/bell.csv`, and `results/raw/qaoa_counts.json` were computed using **Qiskit Aer (`AerSimulator`)**:
- No physical superconducting quantum processor (e.g., IBM Quantum Eagle or Heron) was accessed.
- No remote cloud backend execution or quantum hardware queue times are reported.
- Reference Processors A (5Q), B (9Q), and custom Processor D (9Q) are simulated topological graphs and noise models running locally.

### 2.2 Depolarizing Noise Model Approximations
The official Phase 2 noise model approximates physical hardware decoherence via Pauli depolarizing channels and symmetric readout bit-flip error:
- Single-qubit gate depolarizing probability: $p_1 = 0.001$ ($0.1\%$).
- Two-qubit CX gate depolarizing probability: $p_2 = 0.005$ ($0.5\%$).
- Readout bit-flip probability: $p_{\text{readout}} = 0.01$ ($1.0\%$).

**Physical Disclosures:**
1. **Uncorrelated Error Assumption:** Physical quantum processors suffer from non-Markovian noise, spectator qubit crosstalk, $T_1$ relaxation, and $T_2$ dephasing that vary dynamically with spatial layout. The depolarizing model assumes spatially uncorrelated, time-independent stochastic errors.
2. **Readout Symmetry:** Physical readout error is asymmetric ($P(1|0) \neq P(0|1)$ due to thermal relaxation toward $|0\rangle$). Our benchmark strictly employs the official symmetric noise model to ensure fair cross-team comparison.

---

## 3. Hardware Co-Design Trade-Offs (Processor D vs. Processor B)

### 3.1 Workload-Specific Customization
Processor D was co-designed specifically to embed the 9 interaction edges of the PS-O1 graph into hardware coupling:
- **Advantage:** Eliminates all SWAP gates (0 SWAPs vs. 1 SWAP on Processor B), compressing compiled physical CX count by $14.29\%$ (18 vs. 21 CX) and two-qubit depth by $17.65\%$ (14 vs. 17).
- **Limitation (Workload Overfitting):** A processor topology optimized for one specific 6-vertex graph is not a general-purpose quantum architecture. On an arbitrary 9-vertex graph, Processor D may incur routing overhead comparable to or greater than Processor B.

### 3.2 Solution Quality Under Simulated Noise
In our simulated benchmark:
- **Processor B (Noisy):** Approximation ratio $r = 0.7874$, $P_{\text{opt}} = 12.60\%$ (516/4096).
- **Processor D (Noisy):** Approximation ratio $r = 0.7862$, $P_{\text{opt}} = 12.50\%$ (512/4096).
- **Delta:** $\Delta r = -0.0012$ ($-0.15\%$ relative).

**Scientific Interpretation:**
Within the finite-shot statistical uncertainty of 4,096 shots ($SE \approx 0.0028$), this difference is **statistically and numerically indistinguishable**. Processor D does not drastically improve the sampled cut quality under this light noise model, but it provides significant circuit compression (-3 CX, -8 total layers) that becomes critical on hardware with short coherence times.

---

## 4. Scalability Boundaries and QAOA Limitations

### 4.1 Shallow Depth Constraint ($p=1$)
In compliance with the official challenge kit, our primary benchmark evaluates depth $p=1$:
- For $p=1$, QAOA acts as a localized quantum expectation operator with an analytical reach limited to the 1-hop subgraph neighborhood.
- Higher depth ($p \ge 2$) expands correlation reach across graph diameter but increases gate count linearly, exposing NISQ circuits to compounded gate infidelity.

### 4.2 Barren Plateaus and Parameter Optimization
For small graphs ($n=6$), classical gradient-free optimizers (such as COBYLA) efficiently locate the global parameter basin from multi-start initializations. As graph size $n$ scales into the hundreds:
- The parameter optimization landscape can develop barren plateaus, where variance in cost gradients vanishes exponentially with qubit count.
- Parameter setting strategies (e.g., Fourier heuristics or adiabatic quantum evolution transfer) would be required.

---

## 5. Real-World Network Scenario Boundaries

In the presentation and web studio, we demonstrate a **Cellular Radio Access Network (RAN) Frequency Reuse Optimization** scenario:
- **Synthetic Input:** The 6-cell cluster and its edge weights (1 to 5) are synthetic model representations derived strictly from the locked benchmark instance.
- **Cut Weight Fraction:** The score 22 out of total edge weight 27 represents an **$81.48\%$ weighted cut fraction**, not an empirical $81.48\%$ reduction in physical radio frequency interference.
- **Production Status:** This scenario illustrates how graph partitioning models real-world engineering decisions; it is an illustrative demonstration and has not been deployed to live telecommunications networks.

---

## 6. Summary of Responsible Engineering Stance

1. **Ground truth is classical:** $C^* = 22$, verified by exhaustive enumeration.
2. **QAOA samples efficiently:** Outperforms uniform random sampling by $4.0\times$ in optimal state probability.
3. **Hardware co-design succeeds:** Eliminates routing SWAP gates and reduces compiled circuit depth.
4. **All data is reproducible:** Deterministic seeds, open-source code, and audited SHA-256 checksums ensure complete independent verification.
