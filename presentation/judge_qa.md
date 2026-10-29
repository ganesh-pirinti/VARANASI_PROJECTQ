# VARANASI — Comprehensive Judge Q&A & Adversarial Defense Guide

**Event:** Qiskit Fall Fest 2026 — SRM University-AP  
**Track:** Optimization  
**Problem Statement:** PS-O1 — Quantum Optimization of Network Partitioning Using QAOA  
**Team ID:** AP251100708044  
**Team:** VARANASI  

---

### Category 1: Problem Definition & Classical Ground Truth

#### Q1: How did you verify the locked PS-O1 problem graph and establish the classical optimum?
**Answer:**  
We evaluated the locked 6-vertex, 9-weighted-edge graph loaded from `data/instance.json` (SHA-256: `fba157735abec12ab24b51aa5f1270fb94de086da4eea965f2135d6c278f9fa0`).  
Before running quantum circuits, we performed an exhaustive classical enumeration across all $2^6 = 64$ binary states:
- **Total Graph Weight:** 27
- **Exact Maximum Cut ($C^*$):** 22 (81.48% of total weight; 7 of 9 edges cut)
- **Optimal Partitions:** Exactly 2 bitwise-complement states:
  - Partition 1: $S = \{0, 1, 3\}$ and $\bar{S} = \{2, 4, 5\}$ (logical state `110100`)
  - Partition 2: $S = \{2, 4, 5\}$ and $\bar{S} = \{0, 1, 3\}$ (logical state `001011`)
- **Uniform Random Baseline:** Mean cut $\mu = 13.50$, approximation ratio $r = 0.6136$, and optimal hit probability $P_{\text{opt}} = 2/64 = 3.125\%$.  
This benchmark is permanently locked and verified by `tests/test_raw_results.py` (Test 1 & 2).

#### Q2: How did you handle bitstring endianness between Qiskit and graph node indexing?
**Answer:**  
Qiskit outputs measurement bitstrings in little-endian order (where character index 0 corresponds to qubit $q_{N-1}$ and the rightmost character corresponds to qubit $q_0$).  
To prevent bitstring inversion bugs, we utilized the official starter pack mapping function `counts_to_x(bitstring)`:
$$\text{bitstring}[::-1] \rightarrow (x_0, x_1, \dots, x_{N-1})$$
This guarantees that node $i$ strictly receives value $x[i]$, ensuring 100% agreement between sampled bitstrings and graph cut evaluations.

---

### Category 2: Processor Topologies & Hardware Co-Design

#### Q3: Why is Processor A reported as non-executable?
**Answer:**  
Processor A possesses exactly 5 physical qubits with a tree topology (`0-1-2`, `1-3-4`).  
Problem Statement PS-O1 requires 6 logical qubits for its 6 vertices. Mapping a 6-qubit graph onto a 5-qubit processor violates fundamental capacity constraints. In accordance with the official rules, Processor A is strictly marked:
```json
{"processor": "Processor A", "executable": false, "reason": "needs 6 qubits > 5"}
```
Zero shots were fabricated or recorded for Processor A.

#### Q4: What makes Processor D compliant with the official Challenge Kit rules?
**Answer:**  
Processor D satisfies every constraint mandated by the Phase 2 Challenge Kit:
1. **Qubit Count:** 9 qubits, which is $\le 12$ maximum allowed.
2. **Connectivity:** Fully connected single graph with no isolated nodes.
3. **Maximum Degree:** Node degrees are $\{3, 3, 3, 4, 4, 3, 2, 2, 2\}$. The maximum node degree is 4 (at nodes 3 and 4), strictly satisfying the rule $\le 4$.
4. **Basis Gates:** Exactly `['rz', 'sx', 'x', 'cx']`.
5. **Noise Model:** Official depolarizing rates ($p_1 = 0.001$, $p_2 = 0.005$) and readout bit-flip ($p_{\text{readout}} = 0.01$).  
The official validator `qff_phase2.validate_processor_d()` returns 0 violations.

#### Q5: How was Processor D's topology designed to eliminate SWAPs?
**Answer:**  
Processor D uses a two-tier co-design approach:
- **Core Problem Graph (Nodes 0–5):** Directly embeds all 9 edges of the PS-O1 graph: `(0,2), (0,3), (0,4), (1,4), (1,5), (2,3), (2,4), (3,4), (3,5)`. Every required two-qubit interaction exists physically.
- **Ancillary Routing Ring (Nodes 6–8):** Completes the 9-qubit processor via edges `(5,6), (6,7), (7,8), (8,1)`. This provides routing paths for ancillary quantum operations while capping vertex degree at 4.
Because all problem edges exist physically, the compiler requires **0 SWAP gates** and executes with the theoretical minimum of **18 physical CX gates**.

---

### Category 3: Transpilation & Circuit Metrics

#### Q6: How does Processor D compare to Processor B in compiled circuit resources?
**Answer:**  
Transpiling the locked PS-O1 QAOA circuit with Qiskit 2.5.2 at Optimization Level 1 (seed 42) produces:
- **Physical CX Count:** Processor B = 21, Processor D = 18 ($\mathbf{-14.29\%}$, saving 3 CX gates).
- **Total Circuit Depth:** Processor B = 37, Processor D = 29 ($\mathbf{-21.62\%}$, saving 8 layers).
- **Two-Qubit Depth:** Processor B = 17, Processor D = 14 ($\mathbf{-17.65\%}$, saving 3 layers).
- **Routing SWAPs:** Processor B = 1, Processor D = 0 ($\mathbf{-100\%}$, zero SWAPs).

#### Q7: Why does Processor B require a SWAP gate?
**Answer:**  
Processor B is a generic 9-qubit grid/heavy-hex subgraph. While it contains 12 coupling edges, it lacks a direct edge between the physical qubits assigned to logical nodes 1 and 4.  
To execute the cost Hamiltonian term $\exp(-i \gamma w_{14} Z_1 Z_4)$, the Qiskit compiler must route qubit 1 adjacent to qubit 4 by inserting a SWAP gate. In the standard basis gate set, a SWAP decomposes into 3 CX gates, inflating the CX count from 18 to 21 (+16.7% overhead).

---

### Category 4: Objective 1 — Bell State Tomography

#### Q8: What was the purpose and outcome of the Bell state tomography on Processor D?
**Answer:**  
Objective 1 evaluates the physical viability of Processor D using quantum state tomography on Bell states ($|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$) across two pairs under 4,096 shots per basis:
1. **Near Pair $(0, 2)$ — Distance 1:** Connected by a direct edge.
   - Ideal: $F = 1.0000 \pm 0.0000$
   - Noisy: $F = 0.9633 \pm 0.0021$ ($1\text{ CX gate}$)
2. **Far Pair $(0, 7)$ — Distance 4:** Separated across the ancillary ring.
   - Ideal: $F = 1.0000 \pm 0.0000$
   - Noisy: $F = 0.9420 \pm 0.0026$ ($10\text{ CX gates}$ due to SWAP routing)
- **Decoherence Analysis:** The 2.13 percentage-point drop directly tracks cumulative depolarizing gate noise ($10 \times p_2$) and readout errors, empirically confirming hardware simulation accuracy.

---

### Category 5: QAOA Performance, Statistical Rigor & Solution Quality

#### Q9: Why is Processor D's noisy approximation ratio slightly lower than Processor B's (0.7862 vs 0.7874)?
**Answer:**  
This is a critical point of scientific integrity. We do **not** claim that Processor D produces a higher mean solution quality than Processor B on this instance.  
Here is the exact statistical reality:
- Sample size: $N = 4,096$ shots per run.
- Standard deviation of sampled cuts: $\sigma \approx 3.9$, yielding a standard error of the mean cut of $\text{SE} = \sigma / \sqrt{4096} \approx 0.061$.
- Standard error of the approximation ratio: $\text{SE}_r = 0.061 / 22 \approx 0.0028$.
- The observed difference between D and B is $\Delta r = 0.7862 - 0.7874 = -0.0012$ (a relative difference of only $-0.15\%$).
Because $|\Delta r| < \text{SE}_r$, the two values are **numerically indistinguishable** within random shot noise.  
Processor D's genuine, verified scientific contribution is **architectural**: achieving identical solution fidelity while saving 14.3% CX gates, 21.6% depth, and 100% of routing SWAPs.

#### Q10: Did you observe quantum algorithmic speedup or quantum advantage?
**Answer:**  
**No.** We state unequivocally that no quantum algorithmic speedup or quantum supremacy was demonstrated or claimed:
1. The problem has $N = 6$ vertices ($2^6 = 64$ states), which classical enumeration solves in under 1 millisecond.
2. What we *did* achieve is a **4.0x sampling probability enhancement** over uniform random guessing: QAOA samples the exact optimal cut ($C^* = 22$) with $12.50\%$ probability (512 / 4096 shots) on Processor D, compared to only $3.125\%$ (2 / 64) for uniform random guessing.
3. Our Complementary CDF analysis demonstrates that QAOA strictly stochastically dominates the random baseline for all cut thresholds $c \ge 14$.

#### Q11: Why did you benchmark depth $p=1$ rather than $p=2$?
**Answer:**  
In the official Phase 2 Challenge Kit (`OPTIMISATION_PS.docx`), depth $p=1$ is **mandatory**, while $p=2$ is designated as an **optional extension**.  
We prioritized scientific rigor at $p=1$ for three reasons:
1. **Noise Isolation:** At $p=1$, the circuit is short enough that physical differences in topology (18 vs 21 CX gates) can be isolated without being overwhelmed by circuit-wide decoherence.
2. **Optimizer Reliability:** With 2 parameters $(\gamma_1, \beta_1)$, the parameter landscape can be exhaustively visualized via statevector simulation, proving global convergence.
3. **Multi-Seed Optimization:** We ran multi-seed optimization across 5 random seeds (0 to 4), finding that Seed 3 achieved the global maximum theoretical expectation of $\langle C \rangle = 17.7128$ ($r = 0.8051$).

---

### Category 6: Official Compliance & Submission Process

#### Q12: Why is Processor C not included in your Phase 2 benchmark?
**Answer:**  
Processor C was evaluated during Phase One. However, for Phase 2, Section 12 FAQ of the official `QFF2026_Optimization_Challenge_Kit.docx` explicitly states:
> *"Is Processor C part of Phase 2? No. Phase 2 uses Processors A, B and D only."*  
Evaluating Processor C would contradict the governing rules of Phase 2.

#### Q13: Does pushing commits to GitHub complete the submission?
**Answer:**  
**No.** We recognize that pushing to the GitHub repository does NOT constitute an official submission.  
The team lead must take the clean ZIP deliverable (`dist/VARANASI_PS-O1_Phase2_Submission.zip`) and the public repository URL and submit them directly through the official QFF 2026 submission portal before the deadline.

#### Q14: What was the role of artificial intelligence tools in this project?
**Answer:**  
In accordance with official hackathon disclosure guidelines:
- **AI Tooling Used:** Large language model coding assistants were utilized for script scaffolding, generating repetitive visualization boilerplate, formatting Markdown documentation, and drafting test harnesses.
- **Human/Scientific Responsibility:** All problem modeling, Hamiltonian derivations, topology co-design choices, parameter optimization strategies, and statistical analyses were formulated, verified, and audited by Team VARANASI. Every result in this submission is reproducible from raw source code and deterministic seeds.

#### Q15: How can an independent evaluator reproduce your results from scratch?
**Answer:**  
The entire repository is built for single-command end-to-end reproducibility:
```powershell
# 1. Verify exact ground truth and raw histograms (14 tests)
python -m unittest tests/test_raw_results.py -v

# 2. Run consolidated 8-stage verification suite
python tests/consolidated_test_suite.py

# 3. Regenerate all 7 scientific figures (PNG + SVG)
python -m src.visualizations

# 4. Rebuild the PowerPoint and PDF pitch deck
python scripts/generate_pitch_deck.py
```
Every run completes within seconds with zero dependencies on external proprietary APIs.

#### Q16: How does hardware co-design scale beyond 6 qubits?
**Answer:**  
While PS-O1 is a 6-qubit instance, routing overhead in generic quantum architectures scales unfavorably: on a 2D heavy-hex lattice, mapping an arbitrary graph requires $O(N)$ to $O(N^2)$ SWAP gates, inflating two-qubit depth by $3\times$ to $10\times$.  
Hardware co-design demonstrates that when network topologies have known community or clustering structures, quantum processors fabricated with matching connectivity eliminate compiler routing overhead entirely, preserving critical quantum coherence for practical NISQ applications.
