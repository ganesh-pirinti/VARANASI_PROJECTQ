# QFF 2026 Phase 2: Quantum Optimization of Network Partitioning (PS-O1)

**Problem Statement:** PS-O1 — Quantum Optimization of Network Partitioning Using QAOA  
**Track:** Optimization Track (Qiskit Fall Fest 2026 Phase 2)  
**Team Identifier:** `QFF2026_RESEARCH_TEAM` (*Pending Phase 1 Official Registration Confirmation*)  
**Execution Environment:** Windows / Linux / macOS | Python 3.11 | Qiskit 2.6.1 | Qiskit Aer 0.18.2  
**Clean Workspace Reference:** `C:\QFF\PS-O1_Phase2_REBUILD`  
**Official Portal Deadline:** **5:40 PM IST on Day 2** (SRM AP Hackathon Portal, contact: `qiskitfallfest@srmap.edu.in`)  

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Qiskit 2.6](https://img.shields.io/badge/Qiskit-2.6.1-purple.svg)](https://qiskit.org/)
[![Tests](https://img.shields.io/badge/tests-24%20passed-brightgreen.svg)]()
[![Processor D](https://img.shields.io/badge/Processor%20D-0%20violations-success.svg)]()
[![Compliance](https://img.shields.io/badge/Requirements%20Audit-100%25%20PASS-brightgreen.svg)](docs/REQUIREMENTS_AUDIT.md)

> [!IMPORTANT]
> **Simulation Notice**: All quantum computational experiments in this project are conducted on classical simulators via Qiskit Aer (`AerSimulator`) using the competition-specified noise parameters (depolarizing single-qubit error $p_1 = 10^{-3}$, two-qubit error $p_2 = 5 \times 10^{-3}$, and readout error $p_{\text{readout}} = 10^{-2}$). Classical exact ground truth is obtained via exhaustive enumeration. No physical quantum processor hardware was accessed or claimed.

This repository contains the complete, scientifically validated, reproducible research codebase for **PS-O1: Quantum Optimization of Network Partitioning Using QAOA** developed for the Qiskit Fall Fest 2026 Phase 2 Optimization Track.

---

## 1. Key Scientific Results

| Metric | Random Baseline | Processor A | Processor B (Noisy) | Processor D (Noisy) | Classical Ground Truth |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Physical Qubits** | — | 5 | 9 | 9 | — |
| **Executable** | Yes | **No** (5 < 6) | Yes | Yes | Yes |
| **SWAP Gates** | — | — | 1 | **0 (Zero Routing)** | — |
| **CX Count** | — | — | 21 | **18 (-14.3%)** | — |
| **Circuit Depth** | — | — | 37 | **29 (-21.6%)** | — |
| **Two-Qubit Depth** | — | — | 17 | **14 (-17.6%)** | — |
| **Sampled Cut $\langle C \rangle$** | 13.5000 | — | $17.3220 \pm 0.0598$ | **$17.2971 \pm 0.0612$** | **22.0000** |
| **Approx. Ratio ($r$)** | 0.6136 | — | $0.7874 \pm 0.0027$ | **$0.7862 \pm 0.0028$** | **1.0000** |
| **Optimal Hit Prob. ($P_{\text{opt}}$)** | 3.125% | — | 12.60% | **12.50% ($4.0\times$ baseline)** | — |

- **Sampled Solution Quality & Uncertainty Analysis**:
  - Processor B (Noisy, 4096 shots): Mean cut $\langle C \rangle = 17.3220 \pm 0.0598$, Approx. Ratio $r = 0.7874 \pm 0.0027$ ($17.3220 / 22 = 0.7874$), $P_{\text{opt}} = 0.1260 \pm 0.0052$.
  - Processor D (Noisy, 4096 shots): Mean cut $\langle C \rangle = 17.2971 \pm 0.0612$, Approx. Ratio $r = 0.7862 \pm 0.0028$ ($17.2971 / 22 = 0.7862$), $P_{\text{opt}} = 0.1250 \pm 0.0052$.
  - Observed differences (B - D): $\Delta \langle C \rangle = +0.0249 \pm 0.0856$, $\Delta r = +0.0011 \pm 0.0039$.
  - Hypothesis testing: $z = \frac{0.024902}{0.085588} = 0.2910\sigma$ ($p = 0.7711$).
  - *Statistical Nuance & Conclusion:* Under 4096 shots, the sampled mean cuts and approximation ratios are statistically indistinguishable ($|z| \ll 2\sigma$). Crucially, this failure to reject the null hypothesis of equal first moments does not prove that the underlying 64-element output distributions are identical. Processor D's verified advantage is **resource efficiency** (eliminating 100% of routing SWAP gates, saving 14.3% CX gates and 21.6% depth).

- **Bell-State Tomography on Processor D (Simulated Measurements)**:
  - Near Pair $(0, 2)$ ($d=1$, 1 CX): Fidelity $\mathcal{F} = 0.9633 \pm 0.0021$
  - Distant Pair $(0, 7)$ ($d=4$, 10 CX): Fidelity $\mathcal{F} = 0.9420 \pm 0.0026$
  - Simulated Degradation: $\Delta \mathcal{F} = -0.0213 \pm 0.0033$ ($6.37\sigma$ significance).
  - All 12 individual measurement circuits are recorded in [`results/tables/bell_circuits.csv`](results/tables/bell_circuits.csv) with raw counts in [`results/raw/bell_counts.json`](results/raw/bell_counts.json).

- **Processor D Co-Design (Simulator Coupling-Graph Model)**:
  - Validated by `qff_phase2.validate_processor_d(d, required_qubits=6)`: **0 violations**.
  - Configuration SHA-256: `f3f16cf1825f8365e9c0b850f4df73bc5590697c94fa1bdb8925d0801b44c4f9`.

---

## 2. Quickstart & Reproduction

Detailed instructions are available in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

### 0. Environment Setup
```bash
# Create and activate a clean Python 3.11 virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install exact pinned dependencies
pip install -r requirements.txt
```
> **Reference Evaluation Environment:** Tested on Windows x64 with Python 3.11.9 (`C:\QFF\.qff2026-venv\Scripts\python.exe`).

### 1. Run Complete Pipeline (Computations, Tables, & Figures)
```bash
python scripts/run_all.py
```

### 2. Validate Results Integrity
```bash
python scripts/validate_results.py
```

### 3. Run Automated Unit Tests (24 tests)
```bash
pytest -v tests/
```

### 4. Execute Jupyter Notebook
```bash
python -m jupyter nbconvert --execute --inplace main.ipynb
```

### 5. Package Submission Archive
```bash
python scripts/package_submission.py
```

---

## 3. Repository Structure

```
.
├── COMPLETION_REPORT.md              # Full execution audit and integrity report
├── README.md                         # Master repository landing documentation
├── report.md                         # 6-page comprehensive scientific research report
├── main.ipynb                        # Pre-executed, judge-ready Jupyter notebook
├── requirements.txt                  # Pinned Python package dependencies
├── qff_phase2.py                     # Official helper module (unmodified)
├── example_usage.py                  # Official example script
├── instances.json                    # Locked official problem instance
├── data/
│   ├── instance.json                 # Dedicated PS-O1 instance specification
│   └── instances.json                # Mirror of official instance
├── docs/
│   ├── REQUIREMENTS_AUDIT.md         # Comprehensive requirements & evidence audit matrix
│   ├── DELIVERABLE_CHECKLIST.md      # Detailed verification checklist
│   ├── METHODS_AND_MATHEMATICS.md    # Mathematical derivations, QUBO, Ising, QAOA
│   ├── PROCESSOR_D_DESIGN.md         # Hardware architecture and co-design principles
│   ├── REPRODUCIBILITY.md            # Exact reproduction commands and environment notes
│   └── RESULTS_AND_ANALYSIS.md       # In-depth benchmark analysis and discussion
├── processors/
│   ├── processor_A.json              # 5-qubit official configuration
│   ├── processor_B.json              # 9-qubit official configuration
│   └── processor_D.json              # 9-qubit co-designed custom topology
├── results/
│   ├── figures/                      # 20 publication figures in PNG & SVG (40 files)
│   ├── raw/                          # qaoa_counts.json, bell_counts.json, benchmark_metadata.json
│   └── tables/                       # results.csv, bell.csv, bell_circuits.csv, optimization_runs.csv, etc.
├── scripts/
│   ├── run_all.py                    # Master execution pipeline script
│   ├── validate_results.py           # Deliverable integrity validator
│   └── package_submission.py         # Packaging & clean-extraction smoke testing
├── src/                              # Modular Python packages (classical, qaoa, bell, bench)
└── tests/                            # 24 automated unit tests
```

---

## 4. Provenance and Independence Statement

This implementation was developed completely independently inside `C:\QFF\PS-O1_Phase2_REBUILD` using the authentic organizer-provided materials (`instances.json`, `qff_phase2.py`). No source code, experiment results, figures, configurations, or test routines were copied, imported, or derived from `VARANASI_PROJECTQ` or any unrelated prior codebase.

---

## 5. AI Tool Use & Pair Programming Disclosure

In accordance with Qiskit Fall Fest 2026 hackathon guidelines and academic integrity standards:
- **Assistance Tool:** Antigravity AI was used as a pair programming and code-generation assistant for scaffolding test routines, structuring documentation, and automating repetitive data-formatting scripts.
- **Human Oversight & Verification:** All scientific problem models, mathematical derivations (QUBO, Ising transformation, cost Hamiltonian offsets), quantum circuit implementations, QAOA multi-start optimizations, Processor D topology layouts, error propagation calculations, and empirical interpretations were directed, verified, executed locally on Qiskit/Aer simulators, and audited by the human research team (`QFF2026_RESEARCH_TEAM` — *Pending Phase 1 Official Registration Confirmation*).
- **Originality:** No unauthorized proprietary code, pre-computed benchmark results, or external copyrighted repositories were utilized.

---

## 6. Public Git Repository Readiness & Portal Submission Instructions

To push this project to a public GitHub repository and submit via the hackathon portal:

### Step 1: Initialize Git and Create Initial Commit
```powershell
cd C:\QFF\PS-O1_Phase2_REBUILD
git init
git add .
git commit -m "feat: complete Phase 2 PS-O1 quantum optimization submission"
git branch -M main
```

### Step 2: Push to GitHub Remote
```powershell
# Create a new public repository on GitHub (e.g., QFF2026-PS-O1-Team)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git
git push -u origin main
```

### Step 3: Hackathon Portal Upload
- **Portal URL:** SRM AP Hackathon Portal (contact: `qiskitfallfest@srmap.edu.in`)
- **Submission Deadline:** **5:40 PM IST on Day 2**
- **Files to Upload:**
  1. `dist/QFF2026_PS-O1_Phase2_Submission.zip`
  2. Public GitHub Repository URL
  3. `dist/QFF2026_PS-O1_Phase2_Submission.sha256`
