# VARANASI — Official QFF 2026 Phase 2 Compliance Matrix

**Project:** VARANASI  
**Event:** Qiskit Fall Fest 2026 — SRM University-AP  
**Track:** Quantum Optimization  
**Problem Statement:** PS-O1: Quantum Optimization of Network Partitioning Using QAOA  
**Team ID:** `AP251100708044`  
**Team Leader:** Ganesh Pirinti (`ganeshpirinti95218@gmail.com`)  
**Repository:** `https://github.com/ganesh-pirinti/VARANASI_PROJECTQ`  
**Target Delivery Root:** `Phase 2/`  

---

## 1. Eligibility Gates Audit

| Gate # | Eligibility Gate Requirement | Relevant File | Verification Method | Status | Evidence / Verification Output | Remaining Risk / Mitigation |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **G1** | **Hackathon Portal Submission**<br>Required public repository URL and submission package submitted to portal before deadline. | Portal form / `dist/VARANASI_PS-O1_Phase2_Submission.zip` | URL inspection and ZIP verification. | **PENDING / NOT VERIFIED** | Deliverable package staged locally: `dist/VARANASI_PS-O1_Phase2_Submission.zip` (SHA-256 audited). Public GitHub URL: `https://github.com/ganesh-pirinti/VARANASI_PROJECTQ`. | **Critical Action Required:** Team leader must manually upload the package and submit repository URL to the hackathon portal before the midnight deadline. |
| **G2** | **Consistent Problem Statement**<br>README must identify exactly the assigned Phase 1 problem statement (PS-O1). | `Phase 2/README.md`<br>`Phase 2/report.md` | Automated text inspection and schema check. | **PASS** | README and reports explicitly title PS-O1: "Quantum Optimization of Network Partitioning Using QAOA". No secondary problem statements judged. | Zero risk. Problem statement strictly locked. |
| **G3** | **Unattended Notebook Execution**<br>Evaluator can run `main.ipynb` end-to-end without modifying code, reproducing Processor B outputs. | `Phase 2/main.ipynb` | `nbclient` top-to-bottom run with zero runtime exceptions. | **PASS** | `main.ipynb` executed top-to-bottom in 22.27s (far below 30-min limit); all 13 cells produced valid figures, tables, and metrics. | Zero risk. Local execution verified in clean virtual environment. |
| **G4** | **Deliverables Schema & Technical Report**<br>`results/tables/results.csv` follows official schema; formal technical report present. | `Phase 2/results/tables/results.csv`<br>`Phase 2/report.md` | Schema validator in `tests/test_results.py` and file length check. | **PASS** | `results.csv` has exactly 6 rows and all 18 official columns; `report.md` contains comprehensive technical analysis (32.4 KB, 4–8 page equivalent). | Zero risk. All numbers match raw JSON and notebook. |

---

## 2. Five Scoring Objectives Audit (100 Points Total)

### Objective 1: Bell-State Preparation and Verification (10 Points)
*Requirement: Prepare $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$, evaluate adjacent pair and farthest pair on Processor D under ideal and noisy conditions, measure in XX, YY, ZZ bases (4096 shots/basis), compute correlations, fidelity, and standard errors.*

| Check ID | Requirement Detail | Governing Document Citation | Target Deliverable | Verification Method | Status | Evidence & Actual Output |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **O1.1** | **Target State & Circuit** | Challenge Kit, Section 4 | `src/bell_evaluator.py`<br>`main.ipynb` | Qiskit circuit inspection | **PASS** | H on qubit 0, CX between pair. Basis rotations: ZZ (none), XX (H on both), YY ($S^\dagger H$ on both). |
| **O1.2** | **Physical Pair Selection** | Challenge Kit, Section 4 | `processors/processor_D.json` | Graph distance BFS | **PASS** | Adjacent pair $(0, 2)$ has physical distance $d=1$ (1 CX). Farthest pair $(0, 7)$ has physical distance $d=4$ (10 CX via SWAP routing). |
| **O1.3** | **Official Fidelity Formula** | Challenge Kit, Section 4 | `src/metrics.py`<br>`results/tables/bell.csv` | Independent recalculation | **PASS** | $F = (1 + \langle XX\rangle - \langle YY\rangle + \langle ZZ\rangle)/4$. Zero credit shortcut $P(00)+P(11)$ strictly rejected. |
| **O1.4** | **Standard Error Propagation** | Challenge Kit, Section 4 | `results/tables/bell.csv` | Numerical check | **PASS** | $SE(F) = \frac{1}{4}\sqrt{SE_{XX}^2 + SE_{YY}^2 + SE_{ZZ}^2}$. Standard errors verified for all 4 rows. |
| **O1.5** | **Physical Trend Analysis** | Challenge Kit, Section 4 & 11 | `report.md`<br>`results/figures/` | Comparative analysis | **PASS** | Ideal fidelity: $1.0000 \pm 0.0000$. Noisy near: $0.9633 \pm 0.0021$. Noisy far: $0.9420 \pm 0.0026$. Correctly accounts for 4-hop routing gate exposure. |

---

### Objective 2: Custom Processor D Hardware Co-Design (20 Points)
*Requirement: Design custom Processor D topology targeting measured A/B bottleneck. Pass `validate_processor_d(D, 6)` with 0 violations. Explain routing, gate overhead, depth, and noise trade-offs.*

| Check ID | Requirement Detail | Governing Document Citation | Target Deliverable | Verification Method | Status | Evidence & Actual Output |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **O2.1** | **Official Rule Validation** | Challenge Kit, Section 5 | `processors/processor_D.json` | `validate_processor_d(D, 6)` | **PASS** | 0 rule violations. Qubits: 9 (allowed $6 \le n \le 12$). Max degree: 4 (nodes 3, 4 degree 4; all others $\le 3$). Gate set: `['rz', 'sx', 'x', 'cx']`. |
| **O2.2** | **Noise Constraints** | Challenge Kit, Section 5 | `processors/processor_D.json` | Json parser check | **PASS** | $p_1 = 0.001 \ge 0.001$, $p_2 = 0.005 \ge 0.005$, $p_{\text{readout}} = 0.01 \ge 0.01$. |
| **O2.3** | **SWAP Elimination** | Challenge Kit, Section 5 & 11 | `results/tables/resource_comparison.csv` | Transpiler audit (`qff_phase2.py`) | **PASS** | Processor B requires 1 SWAP (+3 CX overhead, 21 physical CX). Processor D embeds all 9 graph edges, achieving **0 SWAPs** (18 CX, 0 overhead). |
| **O2.4** | **Depth Compression** | Challenge Kit, Section 5 & 11 | `results/tables/resource_comparison.csv` | Transpiler audit | **PASS** | Two-qubit depth reduced from 17 to 14 (**-17.65%**); total depth reduced from 37 to 29 (**-21.62%**). |
| **O2.5** | **Engineering Trade-off** | Challenge Kit, Section 5 & 11 | `report.md`<br>`docs/SCIENTIFIC_LIMITATIONS.md` | Technical discussion | **PASS** | Honest disclosure: D optimizes this specific graph topology; under simulated noise, $r=0.7862$ on D vs $0.7874$ on B ($\Delta r = -0.0012$, numerically indistinguishable within shot noise $SE \approx 0.0028$). |

---

### Objective 3: Solution Development and Benchmarking (35 Points)
*Requirement: Correct Max-Cut QUBO and cost Hamiltonian (10 pts). Solution quality vs classical optimum ($C^*=22$) and random baseline ($13.5$) for $r$ and $P_{\text{opt}}$ (15 pts). Resource efficiency across A/B/D (10 pts).*

| Check ID | Requirement Detail | Governing Document Citation | Target Deliverable | Verification Method | Status | Evidence & Actual Output |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **O3.1** | **QUBO & Cost Hamiltonian** | `OPTIMISATION_PS.docx`, Sec 2 | `src/problem_model.py`<br>`report.md` | Matrix algebra check | **PASS** | Minimized QUBO: $\min_x -C(x) = x^T Q x$. Ising mapping: $x_i = (I-Z_i)/2 \implies H_C = \sum \frac{w_{ij}}{2}(I - Z_i Z_j)$. Energy offset strictly matches. |
| **O3.2** | **Exact Classical Optimum** | Challenge Kit, Section 2 & 6 | `src/classical_baselines.py` | 64-state exhaustive enumeration | **PASS** | $C^* = 22$ (81.48% cut fraction). Optimal bitstrings: `110100` and `001011` (decoded partitions $\{0, 1, 3\}$ vs $\{2, 4, 5\}$). |
| **O3.3** | **Random Baseline Comparison** | Challenge Kit, Section 6 & 11 | `src/classical_baselines.py` | Combinatorial analysis | **PASS** | Uniform random expected cut: $27/2 = 13.5$. Random $r = 0.6136$. Random $P_{\text{opt}} = 2/64 = 3.125\%$. |
| **O3.4** | **Noisy Solution Quality** | Challenge Kit, Section 9 & 11 | `results/tables/results.csv`<br>`results/raw/qaoa_counts.json` | 4096-shot histogram evaluation | **PASS** | Processor D noisy: $r = 0.7862$, $P_{\text{opt}} = 12.50\%$ (512/4096). $4.0\times$ optimal-sampling probability enhancement over random guessing. |
| **O3.5** | **Multi-Start Optimization** | `OPTIMISATION_PS.docx` | `results/tables/initializations.csv` | Seeds 0..4 COBYLA run | **PASS** | Evaluated 5 seeds. Seed 3 achieved optimal parameters ($\gamma = -0.1680, \beta = 0.3327$, expected cut 17.7128, $r = 0.8051$). Mean $r = 0.7264 \pm 0.0394$. |
| **O3.6** | **Processor A Handling** | Challenge Kit, Section 3 | `results/tables/results.csv` | Capacity check | **PASS** | Processor A (5 qubits) marked `executable: false`, reason "needs 6 qubits, has 5". Graph preserved intact. |

---

### Objective 4: Validation and Reproducibility (15 Points)
*Requirement: Unattended notebook execution, required files present, numbers in report match CSV and raw data, official settings used.*

| Check ID | Requirement Detail | Governing Document Citation | Target Deliverable | Verification Method | Status | Evidence & Actual Output |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **O4.1** | **Notebook End-to-End Run** | Challenge Kit, Section 10 & 11 | `Phase 2/main.ipynb` | `nbclient` automated execution | **PASS** | Notebook executes cleanly in 22.27s (< 30 min limit). All 13 cells populated with valid outputs and zero errors. |
| **O4.2** | **Numerical Synchronization** | Challenge Kit, Section 11 | `results.csv`, `report.md`, `studio_data.json` | Automated cross-audit script | **PASS** | Exact numerical agreement across CSV tables, raw JSON histograms, markdown reports, and web studio data. |
| **O4.3** | **Official Benchmark Settings** | Challenge Kit, Section 3 | `qff_phase2.py`<br>`benchmark_metadata.json` | Hash and parameter audit | **PASS** | Optimization level 1, SABRE seed 42, simulator seed 42, shots 4096, noise $p_1=0.001, p_2=0.005, p_{\text{readout}}=0.01$. `qff_phase2.py` SHA-256 matches starter kit byte-for-byte. |
| **O4.4** | **Clean Packaging** | Challenge Kit, Section 10 | `dist/VARANASI_PS-O1_Phase2_Submission.zip` | Archive inspection | **PASS** | 7.42 MB (< 50 MB limit), 79 entries, strictly excludes `.git`, `node_modules`, `dist/`, `.backups/`, `.pyc`. |

---

### Objective 5: Technical Analysis and Recommendation (20 Points)
*Requirement: Explains why results differ using empirical evidence; limitations; concrete next improvements; clear figures and presentation.*

| Check ID | Requirement Detail | Governing Document Citation | Target Deliverable | Verification Method | Status | Evidence & Actual Output |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **O5.1** | **Root-Cause Analysis** | Challenge Kit, Section 11 | `report.md`<br>`docs/VARANASI_RESEARCH_AND_IMPLEMENTATION_REPORT.md` | Architectural trace | **PASS** | Documents why Processor B incurs 1 SWAP (qubits 1 and 4 have distance 2 in Processor B heavy-hex coupling), and how Processor D's problem-matched coupling eliminates it. |
| **O5.2** | **Scientific Limitations** | Challenge Kit, Section 11 | `docs/SCIENTIFIC_LIMITATIONS.md`<br>`report.md` | Theoretical analysis | **PASS** | Explicitly refrains from claiming quantum supremacy or production speedup. Discusses 64-state classical tractability, finite-shot noise, and Barren Plateaus at scale. |
| **O5.3** | **Publication Figures** | Challenge Kit, Section 11 | `results/figures/` (PNG + SVG) | Visual inspection | **PASS** | 7 professional figures in 300 DPI PNG and scalable vector SVG (graph, topologies, Bell fidelity, cut distributions, resource comparisons, parameter landscape, architecture map). |
| **O5.4** | **Presentation Suite** | Challenge Kit, Section 11 | `presentation/` | Slide deck and script review | **PASS** | 9-slide PowerPoint (`.pptx`, 2.36 MB) + Publication vector PDF (`.pdf`, 903 KB), speaker notes, 3-min/60-s pitch scripts, and 16 judge defense answers. |
| **O5.5** | **Interactive Web Studio** | Hackathon innovation | `Phase 2/web/` | `npm run build` & browser smoke test | **PASS** | 12 interactive stations (2D/3D Three.js Graph Lab, 64-state Matrix, QUBO Explorer, Circuit Microscope, Parameter Landscape, Hardware Compiler Trace, Cellular Scenario Walkthrough). |

---

## 3. Compliance & Self-Audit Summary

- **Eligibility Gates:** 3 / 4 PASS (Gate G1 is **PENDING / NOT VERIFIED** pending manual portal upload by team leader).
- **Internal Verification Checks:** 100% PASS across all 5 challenge objectives in automated project self-audit.
- **Automated Unit Tests:** 24 / 24 PASS (0.038s).
- **Consolidated Master Suite:** 6 / 6 Checks PASS (0 errors).
- **Governing Document Compliance:** 100% aligned with `QFF2026_Optimization_Challenge_Kit.docx` and `OPTIMISATION_PS.docx`.
- **Official Evaluation Notice:** All scoring points listed above reflect internal self-audit verification against official rubric criteria; official scores are determined exclusively by the hackathon judging panel upon review of the submitted repository and portal deliverable.
