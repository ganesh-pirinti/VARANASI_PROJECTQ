# Supplementary Scientific Diagrams — Project VARANASI
## Qiskit Fall Fest 2026: PS-O1 Network Partitioning via QAOA

**Academic Review Deliverable**  
**Host Institution:** SRM University-AP | Hackathon & Competitions Cell  
**Team Name:** `VARANASI` (`AP251100708044`)  
**Lead:** Ganesh Pirinti (`ganeshpirinti95218@gmail.com`) | **Member:** Mohammed Sadiq (`sadiqmohammedkhan12@gmail.com`)  
**Project Directory:** `SUPPLEMENTARY_WORK/`

---

## 1. Purpose of Supplementary Work

This folder provides a suite of seven publication-grade, mathematically verified scientific diagrams designed specifically for faculty evaluation, technical defense, and academic review.

The diagrams synthesize and illustrate the project's four core foundational pillars:
1. **Classical Ground-Truth Formulation:** Exhaustive evaluation of the 6-vertex, 9-edge Max-Cut problem ($W=27$) establishing $C^* = 22$.
2. **Hybrid Variational Optimization:** The closed-loop QAOA iterative optimization architecture linking classical COBYLA updates with the quantum state ansatz.
3. **Hardware-Software Co-Design:** Structural coupling analysis across Processors A, B, and the proposed Processor D, demonstrating zero-SWAP compilation.
4. **Physical Noise & Routing Penalty (Objective 1):** Rigorous quantum state tomography of Bell states $|\Phi^+\rangle$ proving the measurable decoherence cost of multi-hop routing SWAPs.

> **Simulation Methodology Disclosure:** All quantum circuit executions, cross-processor benchmarks, and Bell tomography measurements were executed using classical numerical simulation via Qiskit Aer (`AerSimulator`) incorporating official competition depolarizing ($p_1 = 0.001, p_2 = 0.005$) and readout ($p_{\text{readout}} = 0.01$) noise models. Ground truth was computed via exact classical brute-force enumeration. No physical quantum processor hardware was accessed or claimed.

---

## 2. Catalog of Supplementary Figures

| Figure ID | File Name | Subject & Scope | Authoritative Source / Data Basis |
| :---: | :--- | :--- | :--- |
| **01** | `01_weighted_network_3d` | 3D Spatial Partitioning of the PS-O1 Network Graph | `PHASE_2/instances.json` |
| **02** | `02_classical_optimization_workflow` | Deterministic Classical Ground-Truth Workflow | `PHASE_2/results/tables/classical_enumeration.csv` |
| **03** | `03_hybrid_qaoa_architecture` | Closed-Loop Hybrid Classical–Quantum QAOA Loop | `PHASE_2/src/qaoa_solver.py`, `optimization_runs.csv` |
| **04** | `04_processor_topologies` | Quantum Processor Topologies (A, B, and D) | `PHASE_2/processors/processor_*.json` |
| **05** | `05_qaoa_p1_circuit` | Logical QAOA Depth $p=1$ Circuit Decomposition | `PHASE_2/src/qaoa_solver.py`, `instances.json` |
| **06** | `06_hardware_mapping_comparison` | Compilation Resource & Noisy Quality Benchmarks | `PHASE_2/results/tables/results.csv`, `processor_metrics.csv` |
| **07** | `07_bell_state_measurement_workflow` | Objective 1 Bell-State Tomography Protocol & Data | `PHASE_2/results/tables/bell.csv`, `bell_circuits.csv` |

---

## 3. Scientific Description of Figures

### Figure 01: Three-Dimensional Spatial Partitioning (`01_weighted_network_3d`)
- **Description:** A true 3D spatial visualization of the official 6-vertex, 9-edge PS-O1 communication graph ($W=27$). Vertices are mapped into two parallel spatial planes corresponding to the optimal symmetric partition pair: $S = \{0, 1, 3\}$ at $z = +0.55$ (Blue nodes) and $\bar{S} = \{2, 4, 5\}$ at $z = -0.55$ (Bronze nodes).
- **Cut Structure:** The seven inter-cluster cut edges crossing between planes achieve the exact maximum cut weight $C^* = 22$ (81.48% of total network weight). The two internal uncut edges—$(0, 3)$ with weight 4 and $(2, 4)$ with weight 1—lie entirely within their respective planes (total internal weight = 5).
- *Note:* Spatial $(x, y, z)$ coordinates are visualization aids to visually demonstrate cluster separation; they do not represent physical hardware layout.

### Figure 02: Deterministic Classical Ground-Truth Workflow (`02_classical_optimization_workflow`)
- **Description:** Illustrates the exhaustive brute-force evaluation procedure over all $2^6 = 64$ discrete binary assignment states $x \in \{0, 1\}^6$.
- **Key Findings:** Identifies the exact global maximum cut $C^* = 22$ attained by symmetric states `'001011'` and `'110100'` ($P_{\text{opt, random}} = 3.125\%$). Formally derives the uniform random baseline expectation $\langle C \rangle_{\text{random}} = W/2 = 13.5000$ ($r = 0.6136$).
- *Methodological Distinction:* Clearly distinguishes the exact deterministic classical benchmark from the approximate quantum heuristic.

### Figure 03: Closed-Loop Hybrid QAOA Architecture (`03_hybrid_qaoa_architecture`)
- **Description:** A detailed block diagram of the iterative variational optimization loop linking the classical COBYLA optimizer with the parameterized quantum circuit on the Qiskit Aer simulation engine.
- **Parameters & Trajectories:** Documents the 5 multi-start initializations ($s \in \{0, 1, 2, 3, 4\}$) drawn uniformly from $[0, \pi]$. Documents that Seeds 0, 2, 4 converged to local plateaus ($r \approx 0.707$), Seed 1 reached the maximum iteration limit (80 iterations), and Seed 3 located the global variational optimum $(\gamma^* = -0.1680, \beta^* = 0.3327)$, yielding an expected cut of $\langle C \rangle = 17.7128$ ($r = 0.8051$, +31.2% above random).

### Figure 04: Quantum Processor Coupling Topologies (`04_processor_topologies`)
- **Description:** Side-by-side coupling graphs of reference Processors A and B against our co-designed Processor D.
- **Structural Analysis:**
  - **Processor A (5 Qubits, 4 Edges):** Branching T-tree; structurally infeasible ($5 < 6$ required qubits).
  - **Processor B (9 Qubits, 12 Edges):** Heavy-hex cyclic mesh; requires 1 SWAP gate, 21 physical CX gates, and depth 37.
  - **Processor D (9 Qubits, 13 Edges):** Custom planar transmon co-design. Computational core (qubits $0 \dots 5$) natively embeds all 9 PS-O1 interaction edges; peripheral routing ring (qubits $6 \dots 8$) provides connectivity. Complies with all official rules ($\le 12$ qubits, max degree $\le 4$, connected, planar), passing `validate_processor_d()` with **0 violations**.
- *Note:* Graphs depict logical coupling topology, not physical chip micrographs.

### Figure 05: Logical QAOA Depth $p=1$ Circuit Decomposition (`05_qaoa_p1_circuit`)
- **Description:** A technically faithful logical quantum circuit schematic for PS-O1 at depth $p=1$.
- **Circuit Composition:**
  - Initialization: $H^{\otimes 6} |0\rangle^{\otimes 6} \to |+\rangle^{\otimes 6}$.
  - Problem Unitary $U_C(\gamma)$: 9 pairwise $R_{ZZ}(w_{uv}\gamma)$ blocks decomposed into basis gates ($\text{CX} \to R_Z(w_{uv}\gamma) \to \text{CX}$), requiring exactly 18 CX gates.
  - Mixer Unitary $U_M(\beta)$: 6 single-qubit $R_X(2\beta)$ rotations.
  - Measurement: 6-qubit computational $Z$-basis readout.

### Figure 06: Cross-Processor Resource & Quality Comparison (`06_hardware_mapping_comparison`)
- **Description:** Dual-panel bar chart comparing compiled circuit resources and noisy simulation performance between Processor B and Processor D under 4096 shots.
- **Resource Advantage:** Processor D achieves complete routing overhead elimination: **0 SWAP gates** (100% reduction), 18 CX gates (-14.3%), circuit depth 29 (-21.6%), and two-qubit depth 14 (-17.6%).
- **Scientific Qualification:** Under realistic simulated noise ($p_1 = 0.001, p_2 = 0.005, p_{\text{readout}} = 0.01$), the measured solution quality on Processor B ($r = 0.7874 \pm 0.0027$) and Processor D ($r = 0.7862 \pm 0.0028$) are statistically indistinguishable ($z = 0.291\sigma, p = 0.7711$). Both achieve $\approx 12.5\%$ optimal bitstring sampling ($4.0\times$ random baseline). Processor D's advantage is physical resource efficiency.

### Figure 07: Objective 1 Bell-State Tomography Protocol (`07_bell_state_measurement_workflow`)
- **Description:** Complete experimental protocol and results for quantum state tomography of $|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$ on Processor D across Pauli bases $XX$, $YY$, and $ZZ$ (4096 shots/basis, 12 circuits total).
- **Routing Noise Penalty:**
  - Nearest-neighbor pair $(0, 2)$ ($d=1$, 1 CX): Fidelity $\mathcal{F}_{\text{near}} = 0.9633 \pm 0.0021$.
  - Distant multi-hop pair $(0, 7)$ ($d=4$, 10 CX via SWAP routing): Fidelity $\mathcal{F}_{\text{far}} = 0.9420 \pm 0.0026$.
  - Fidelity degradation: $\Delta \mathcal{F} = -0.0213 \pm 0.0033$ ($6.37\sigma$ statistical confidence).
- **Conclusion:** Experimentally demonstrates the severe gate error and decoherence accumulation caused by multi-hop routing in NISQ processors, highlighting the critical value of Processor D's zero-SWAP embedding.

---

## 4. Reproducibility

To regenerate all 14 PNG and SVG figures from the project source data:

```bash
# From the repository root:
python SUPPLEMENTARY_WORK/source/generate_figures.py
```

Requirements: Python 3.11 with `matplotlib`, `numpy`, and `qiskit` installed (available in the project virtual environment at `.venv` or `C:\QFF\.qff2026-venv`).
