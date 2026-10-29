# VARANASI — Judge Evaluation & Technical Defense Guide

**Event:** Qiskit Fall Fest 2026 — SRM University-AP  
**Track:** Quantum Optimization (Phase 2 Final Submission)  
**Problem Statement:** PS-O1 — Quantum Optimization of Network Partitioning Using QAOA  
**Team Name:** `VARANASI` | **Team / Participant ID:** `AP251100708044`  
**Team Leader:** Ganesh Pirinti (`ganeshpirinti95218@gmail.com`)  
**Team Member:** Mohammed Sadiq (`sadiqmohammedkhan12@gmail.com`)  
**Repository:** [https://github.com/ganesh-pirinti/VARANASI_PROJECTQ](https://github.com/ganesh-pirinti/VARANASI_PROJECTQ)  
**Primary Verification Environment:** Python 3.14.6 | Qiskit 2.5.2 | Qiskit Aer 0.17.2 | NumPy 2.5.2  

---

## 1. 30-Second Executive Summary

VARANASI implements an end-to-end, reproducible QAOA ($p=1$) solver for the locked 6-vertex, 9-edge PS-O1 network partitioning benchmark ($W=27$). We establish exact classical ground truth ($C^*=22$) via exhaustive 64-state enumeration and benchmark quantum compilation across reference **Processor A** (5 qubits), **Processor B** (9 qubits), and our co-designed **Processor D** (9 qubits). 

By directly embedding the 9 problem interaction edges into hardware connectivity, **Processor D completely eliminates the SWAP routing bottleneck** observed on Processor B (0 SWAPs vs. 1 SWAP, 0 CX overhead vs. +3 CX), reducing two-qubit depth by **17.65%** and total circuit depth by **21.62%**, while maintaining numerically similar noisy solution quality in these simulated runs ($r=0.7862$, $P_{\text{opt}}=12.50\%$ on D vs. $r=0.7874$, $P_{\text{opt}}=12.60\%$ on B), providing a **$4.0\times$** optimal-state sampling probability enhancement over uniform random guessing ($3.125\%$).

---

### 1.1 Presentation & Communication Suite
- **Editable PowerPoint Deck:** [presentation/VARANASI_Pitch_Deck.pptx](../presentation/VARANASI_Pitch_Deck.pptx) (16:9 dark-slate publication aesthetic)
- **Universal Publication PDF:** [presentation/VARANASI_Pitch_Deck.pdf](../presentation/VARANASI_Pitch_Deck.pdf) (High-resolution vector slide deck)
- **Speaker Notes & Timing:** [presentation/speaker_notes.md](../presentation/speaker_notes.md) (Slide-by-slide quantitative cues)
- **3-Minute Timed Pitch:** [presentation/pitch_script_3min.md](../presentation/pitch_script_3min.md) (~410 words calibrated script)
- **60-Second Elevator Pitch:** [presentation/pitch_script_60sec.md](../presentation/pitch_script_60sec.md) (~140 words fast-track pitch)
- **Adversarial Judge Q&A:** [presentation/judge_qa.md](../presentation/judge_qa.md) (16 evidence-grounded defense answers)
- **Visualizations Package:** 7 figures in both 300 DPI PNG and scalable vector SVG under [
esults/figures/](../results/figures/)

---

## 2. Core Engineering Contribution

The core contribution is **hardware-software co-design for quantum optimization circuits**:
- Reference processors with generic lattice topologies force the transpiler routing stage (SABRE) to insert SWAP gates (each decomposing into 3 physical CX gates), inflating circuit depth and accelerating decoherence.
- Processor D demonstrates that a problem-matched hardware coupling graph with degree $\le 4$ and $\le 12$ physical qubits natively executes the target QAOA cost unitary with zero routing overhead.
- We provide full statistical provenance: discrete 64-state raw histograms, metadata checksums, Bell-state tomography, and 14 automated unit tests proving mathematical and cross-file consistency.

---

## 3. Key Quantitative Benchmarks

### 3.1 Ground Truth vs. Uniform Random Baseline
- **Vertices:** 6 | **Edges:** 9 | **Total Graph Weight ($W$):** 27
- **Exact Maximum Cut ($C^*$):** 22
- **Optimal Partitions:** Exactly 2 complementary assignments:
  - $x_1 = (1, 1, 0, 1, 0, 0) \implies S = \{0, 1, 3\}, \quad \bar{S} = \{2, 4, 5\}$ (Qiskit bitstring `001011`)
  - $x_2 = (0, 0, 1, 0, 1, 1) \implies S = \{2, 4, 5\}, \quad \bar{S} = \{0, 1, 3\}$ (Qiskit bitstring `110100`)
- **Weighted Cut Fraction:** $22 / 27 = 81.4815\%$ (fraction of total graph weight crossing the cut)
- **Edge Count Cut Fraction:** $7 / 9 = 77.7778\%$ (7 cut edges out of 9)
- **Uniform Random Baseline:** Expected cut $\langle C \rangle = 13.5$, $r = 13.5/22 = 0.6136$, $P_{\text{opt}} = 2/64 = 3.125\%$.

### 3.2 Compilation & Resource Comparison (Processor B vs. Processor D)

| Metric | Processor A | Processor B | Processor D (VARANASI) | Delta (D vs. B) |
| :--- | :---: | :---: | :---: | :---: |
| **Physical Qubits** | 5 | 9 | 9 | Same register capacity |
| **Executable for PS-O1** | `false` ($5 < 6$) | `true` | `true` | N/A |
| **Logical CX Count** | 18 | 18 | 18 | 0 (identical ansatz) |
| **Physical CX Count** | — | 21 | **18** | **-14.29%** (-3 CX) |
| **Routing SWAPs** | — | 1 | **0** | **-100.0%** (-1 SWAP) |
| **CX Routing Overhead** | — | +3 | **0** | **-100.0%** |
| **Total Circuit Depth** | — | 37 | **29** | **-21.62%** (-8 layers) |
| **Two-Qubit Depth** | — | 17 | **14** | **-17.65%** (-3 layers) |
| **Noisy Approx Ratio ($r$)** | — | 0.7874 | 0.7862 | -0.15% relative (-0.12 percentage points, numerically similar in these simulated runs) |
| **Noisy $P_{\text{opt}}$ (4096 shots)** | — | 12.60% (516/4096) | **12.50% (512/4096)** | $4.0\times$ random baseline |

---

## 4. Single-Command Reproduction

From the repository root:
```bash
# Execute full benchmark pipeline (recalculates ground truth, optimizes QAOA, samples B & D, runs Bell tomography, exports tables, figures, and raw histograms)
python -c "from src.benchmark_runner import run_all_benchmarks; run_all_benchmarks()"

# Run automated test suites (Phase 2 + Raw Reproducibility + Consolidated)
python -m unittest discover tests -v
python tests/consolidated_test_suite.py
```
*Total execution time:* ~15 seconds on a standard multi-core laptop CPU.

---

## 5. Artifact & Provenance Directory Map

| Artifact Type | File Path | Content Description |
| :--- | :--- | :--- |
| **Raw QAOA Histograms** | `results/raw/qaoa_counts.json` | Complete 64-element state-space frequency counts, decoded assignments, cut weights, and probabilities for all 4 runs. |
| **Provenance Metadata** | `results/raw/benchmark_metadata.json` | Canonical edge hashes, exact optimum, optimizer parameters, seeds, noise rates, and environment versions. |
| **Official Benchmark Table** | `results/tables/results.csv` | Official Section 9 schema (6 rows covering Processors A, B, D under ideal and noisy simulation). |
| **Bell-State Table** | `results/tables/bell.csv` | Objective 1 tomography fidelities and standard errors for near $(0,2)$ and far $(0,7)$ pairs. |
| **Executable Notebook** | `main.ipynb` | Clean 13-cell notebook executable top-to-bottom via `nbclient` in ~15s with zero errors. |
| **Technical Report** | `report.md` | Comprehensive 6-page technical report with formal derivations and engineering analysis. |
| **Delivery Archive** | `dist/VARANASI_PS-O1_Phase2_Submission.zip` | Deterministic delivery package (3.26 MB) with SHA-256 manifest, excluding `.git` and caches. |

---

## 6. Real-World Applications Scope (Exactly Two)

1. **Interference-Aware Channel Assignment (5G/6G Frequency Planning):**
   - Maps base station clusters to graph vertices and inter-cell co-channel interference to edge weights. Max-Cut partitions cells into two orthogonal frequency bands ($A$ and $B$).
   - *Verified metric:* Cuts $81.48\%$ of total potential interference weight ($22/27$).
   - *Limitation:* Simulated domain mapping of the abstract 6-cell benchmark; production deployment requires multi-channel chromatic coloring ($K > 2$) and continuous transmission power control.
2. **Traffic Engineering (Load-Balanced Routing):**
   - Formulates simplified two-path load balancing minimizing squared demand difference $\min_y (\sum_k d_k (2y_k - 1))^2$.
   - *Status:* **Explicitly labeled as a Proposed Architectural Extension**, illustrating how dense quadratic QUBO interactions benefit from custom topology embedding.

---

## 7. Adversarial Defense: Answers to 14 Judge Questions

### Q1: Why use QAOA when the 6-vertex graph can be solved in milliseconds on a classical computer?
**Answer:** The goal of PS-O1 is not to claim quantum supremacy on a 6-vertex toy graph (which we solve in 0.001s classically), but to benchmark and characterize QAOA circuit compilation, parameter landscape convergence, and routing overhead on constrained quantum hardware architectures. The 6-vertex graph serves as a controlled, verifiable benchmark where exact ground truth is provable, allowing exact measurement of approximation ratios without approximation uncertainty.

### Q2: What is the actual contribution beyond running a default QAOA example?
**Answer:** Running QAOA on default processors inserts SWAP routing gates. Our contribution is the **co-design and empirical validation of Processor D**: we designed a 9-qubit hardware coupling map meeting all official rules (degree $\le 4$, capacity $\le 12$) that natively embeds the PS-O1 graph. This eliminated 100% of SWAPs, reduced physical CX count by 14.29%, and reduced two-qubit depth by 17.65%, providing empirical evidence of how architectural co-design mitigates NISQ noise.

### Q3: How was the exact maximum cut of 22 established?
**Answer:** By independent, exhaustive enumeration of all $2^6 = 64$ binary vectors in `src/exact_solver.py`. For each vector $x \in \{0, 1\}^6$, we computed $C(x) = \sum_{(u,v,w)} w_{uv} [x_u \neq x_v]$. Exactly 2 vectors achieved the maximum cut of 22: $x = (1,1,0,1,0,0)$ and its bitwise complement $x = (0,0,1,0,1,1)$. Total graph weight is 27; uncut weight is 5 (edges $(0,3)$ with weight 4 and $(2,4)$ with weight 1).

### Q4: How are QUBO and Ising conventions validated?
**Answer:** Using the canonical Pauli-Z transformation $x_i = (I - Z_i)/2$. Substituting this into $x_u + x_v - 2x_u x_v$ yields $(I - Z_u Z_v)/2$. Summing over edges yields the cut operator $\hat{C} = \frac{W}{2}I - \frac{1}{2}\sum_{(u,v)} w_{uv} Z_u Z_v$. Maximizing $\langle \hat{C} \rangle$ corresponds to minimizing the cost Hamiltonian $\hat{H}_C = \sum_{(u,v)} \frac{w_{uv}}{2} Z_u Z_v$. Our classical optimizer explicitly minimizes $-\langle \psi(\gamma, \beta) | \hat{C} | \psi(\gamma, \beta) \rangle$.

### Q5: How were bitstring counts converted into logical assignments?
**Answer:** Qiskit measurement keys use little-endian indexing where qubit 0 is the rightmost character: `bitstring[5-i] = x_i`. The official starter function `counts_to_x(bitstring)` reverses the string. Thus, key `'001011'` has bit 0 as `1`, bit 1 as `1`, bit 2 as `0`, bit 3 as `1`, bit 4 as `0`, bit 5 as `0`, giving logical vector $x = (1, 1, 0, 1, 0, 0)$ and cut weight 22. This mapping is verified by unit test `test_14_artificial_histogram_optimal_validation`.

### Q6: Why does Processor D reduce SWAPs?
**Answer:** Processor B lacks direct physical coupling between several interacting qubit pairs (such as $(0, 3)$ and $(2, 4)$ within a 6-node subgraph), forcing SABRE to insert a SWAP gate during routing. Processor D natively embeds all 9 edges of the PS-O1 graph into physical qubits $0..5$. Because every required two-qubit interaction corresponds to an existing hardware coupling edge, the routing stage requires **zero SWAPs**.

### Q7: Why is Processor D's noisy mean ratio slightly lower than B's (0.7862 vs 0.7874) despite fewer gates?
**Answer:** In NISQ simulation, single-qubit gates and readout bit-flips ($p_{\text{readout}} = 0.01$ per qubit) also introduce errors. On a 9-qubit processor, both circuits execute the same number of measurements (6 qubits) and 1-qubit gates. The 3 extra CX gates on Processor B introduce marginal depolarizing noise, but due to stochastic shot variation (4096 shots) and local noise dynamics, the mean approximation ratio difference is within statistical tolerance ($\Delta r = 0.0012$, or $0.15\%$). Processor D achieves parity in solution quality while executing significantly fewer physical gates and lower depth.

### Q8: How is the 12.50% probability computed?
**Answer:** From the full 4096-shot histogram in `results/raw/qaoa_counts.json` for Processor D under noisy simulation. The two optimal complementary states were sampled 254 times (`'001011'`) and 258 times (`'110100'`). Total optimal counts = $254 + 258 = 512$. $P_{\text{opt}} = 512 / 4096 = 0.1250$ ($12.50\%$).

### Q9: What exactly does the 4.0x random-baseline comparison mean?
**Answer:** On a 6-vertex graph, there are 64 possible binary assignments, of which exactly 2 are optimal. A uniform random guess selects an optimal partition with probability $P_{\text{random}} = 2 / 64 = 0.03125$ ($3.125\%$). QAOA on Processor D samples an optimal partition with $12.50\%$ probability: $12.50\% / 3.125\% = 4.0\times$. This represents a $4.0\times$ higher probability of sampling an exact optimal solution per shot, not an algorithmic speedup.

### Q10: Which results are simulated rather than run on physical quantum hardware?
**Answer:** **All benchmark results are obtained via noisy quantum simulation** using Qiskit Aer (`AerSimulator`) with the official synthetic noise model ($p_1 = 0.001$, $p_2 = 0.005$, $p_{\text{readout}} = 0.01$). No physical quantum hardware execution was mandated or conducted; all claims refer strictly to the official transpilation and simulator benchmark.

### Q11: What assumptions make the channel-assignment interpretation valid?
**Answer:** It assumes a two-channel frequency reuse scenario where co-channel interference between adjacent base stations is the dominant impairment. Placing adjacent cells in different sets ($S$ vs. $\bar{S}$) corresponds to orthogonal frequency allocation, eliminating co-channel interference along cut edges. It is a conceptual domain mapping, not a full cellular network simulator.

### Q12: Why is traffic engineering labeled a proposed extension rather than an implemented solver?
**Answer:** General traffic engineering requires multi-commodity flow conservation, link capacity bounds, and path routing tables. Our formulation demonstrates how a simplified two-path scalar load balancing problem maps to a quadratic binary objective with all-to-all couplings. Because this model was not benchmarked on hardware, scientific honesty requires labeling it as a proposed architectural extension.

### Q13: What are the most important limitations of p=1 QAOA and the 6-vertex benchmark?
**Answer:** 
1. *Depth limitation:* Depth $p=1$ limits the theoretical approximation ratio to $\sim 0.80$; higher depth ($p \ge 2$) is needed for higher cuts but introduces more CX gates that suffer from NISQ decoherence.
2. *Scale limitation:* A 6-vertex graph is easily tractable classically. Real combinatorial advantage requires $N \ge 100$ vertices where classical solvers struggle.
3. *Specialization trade-off:* Processor D is co-designed specifically for the PS-O1 graph topology; it may not provide SWAP elimination for non-isomorphic graphs.

### Q14: What would be the next valid experiment to establish whether the architecture advantage generalizes?
**Answer:** Evaluate Processor D against a family of non-isomorphic random 6-node graphs (Erdős–Rényi and Barabási–Albert models) to quantify average SWAP insertion overhead, and test multi-depth QAOA ($p \in \{2, 3, 4\}$) with Zero-Noise Extrapolation (ZNE) error mitigation.

---

## 8. Final Deliverables & Submission Verification

- [x] **Repository URL:** `https://github.com/ganesh-pirinti/VARANASI_PROJECTQ`
- [x] **Branch:** `main`
- [x] **Public Remote Commit:** `3d00f26` (to be updated with final audited commit)
- [x] **Clean Submission ZIP:** `dist/VARANASI_PS-O1_Phase2_Submission.zip` (3.26 MB)
- [x] **Phase One Archive:** Intact under `Phase One/` with 18/18 passing regression tests.
- [x] **AI Tool Disclosure:** Complete and transparent in `README.md`, `report.md`, and `docs/JUDGE_GUIDE.md`.
