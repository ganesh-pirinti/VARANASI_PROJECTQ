# PROJECTQ_VARANASI — Qiskit Fall Fest 2026

**Problem Statement:** PS-O1 — Quantum Optimization of Network Partitioning Using QAOA  
**Track:** Optimization Track (Qiskit Fall Fest 2026)  
**Host Institution:** SRM University-AP | Hackathon & Competitions Cell  
**Team Name:** `VARANASI`  
**Registration ID:** `AP251100708044`  
**Team Leader:** Ganesh Pirinti (`ganeshpirinti95218@gmail.com`)  
**Team Member:** Mohammed Sadiq (`sadiqmohammedkhan12@gmail.com`)  
**Official Submission Portal:** SRM AP Hackathon Portal (contact: `qiskitfallfest@srmap.edu.in`)  
**Portal Deadline:** **5:40 PM IST on Day 2**  
**Repository URL:** [https://github.com/ganesh-pirinti/VARANASI_PROJECTQ](https://github.com/ganesh-pirinti/VARANASI_PROJECTQ)

---

## Repository Overview

This repository houses the complete, end-to-end research, simulation code, co-designed quantum architectures, interactive web tools, and submission deliverables for **Team VARANASI** in **Qiskit Fall Fest 2026 (PS-O1: Quantum Optimization of Network Partitioning Using QAOA)**.

The project is structured into distinct, self-contained directories for each phase of the hackathon, alongside presentation materials and web demonstrators:

```
PROJECTQ_VARANASI/
├── README.md                         # Master root documentation & navigation guide
├── vercel.json                       # Deployment configuration for web UI
├── .gitignore                        # Git ignore rules for Python, virtual environments, and caches
│
├── PHASE_1/                          # Complete original Phase 1 qualification project
│   ├── README.md                     # Phase 1 submission report & technical specifications
│   ├── main.ipynb                    # Phase 1 executable Jupyter notebook
│   ├── main.py                       # Phase 1 execution pipeline
│   ├── build_notebook.py             # Phase 1 notebook generator
│   ├── requirements.txt              # Phase 1 dependencies
│   ├── data/                         # Benchmark graph instances (5-node & 6-node)
│   ├── processors/                   # Official Processors A & B JSON configurations
│   ├── results/                      # Phase 1 metrics CSV, circuit traces, & comparative plots
│   ├── src/                          # Graph utils, QAOA solver, & transpiler benchmarking
│   └── tests/                        # Phase 1 automated test suite (18 tests)
│
├── PHASE_2/                          # Complete verified Phase 2 rebuild project
│   ├── README.md                     # Phase 2 comprehensive technical README
│   ├── report.md                     # 6-page formal scientific research paper
│   ├── main.ipynb                    # Top-to-bottom pre-executed JupyterLab notebook
│   ├── qff_phase2.py                 # Official competition helper module (unmodified)
│   ├── instances.json                # Locked official 6-vertex, 9-edge problem graph (W=27)
│   ├── processor_D_template.json     # Official Processor D template
│   ├── COMPLETION_REPORT.md          # Full verification & deliverable audit report
│   ├── FINAL_READINESS_REPORT.md     # Automated readiness, hash audit, & environment report
│   ├── requirements.txt              # Pinned Python 3.11 dependencies (inc. Qiskit 2.6 & Aer 0.18)
│   ├── data/                         # Problem instance specifications
│   ├── processors/                   # Processors A, B, and custom co-designed Processor D
│   ├── src/                          # Modular Python source (classical, QAOA, Bell, benchmark)
│   ├── scripts/                      # run_all.py, validate_results.py, package_submission.py
│   ├── tests/                        # 24 automated unit & integration tests (100% PASS)
│   ├── results/
│   │   ├── tables/                   # results.csv, bell.csv, bell_circuits.csv, etc.
│   │   ├── raw/                      # Raw counts JSON (QAOA & 12 Bell tomography circuits)
│   │   └── figures/                  # 20 unique publication-grade figure designs (40 PNG + SVG)
│   └── docs/                         # In-depth mathematical derivations & architecture reports
│
├── presentation/                     # Final pitch deck and presentation assets
│   ├── VARANASI_Pitch_Deck.pdf       # 10-slide final presentation deck (PDF)
│   ├── VARANASI_Pitch_Deck.pptx      # Editable PowerPoint presentation deck
│   ├── speaker_notes.md              # Slide-by-slide speaker notes
│   ├── pitch_script_60sec.md         # 60-second elevator pitch script
│   ├── pitch_script_3min.md          # 3-minute technical pitch script
│   └── judge_qa.md                   # 14 defense answers for judging panels
│
└── web/                              # Interactive 3D Quantum Studio & Mission 22 web application
    ├── index.html                    # Single-page web dashboard
    ├── app.js                        # UI logic and graph visualizer
    ├── styles.css                    # Responsive dark-mode styling
    └── ...
```

---

## Phase 1 Summary: Qualification & Architecture Bottleneck Discovery

- **Objective:** Formulate Max-Cut on 5-node and 6-node weighted graphs, construct QAOA circuits ($p=1$), and analyze the SWAP routing bottleneck between Processor A (5 physical qubits, tree topology) and Processor B (9 physical qubits, heavy-hex mesh).
- **Core Findings:**
  1. Identified the physical register capacity limitation of Processor A (cannot execute a 6-qubit circuit without problem-size reduction; logged as `INFEASIBLE_CAPACITY_EXCEEDED`).
  2. Evaluated the 5-node induced subgraph across both processors, showing Processor B's heavy-hex lattice provides multiple alternative routing pathways.
- **Directory:** Navigate to [`PHASE_1/`](PHASE_1/) for Phase 1 documentation, code, and test suites.

---

## Phase 2 Summary: Hardware-Software Co-Design & Scientific Verification

- **Objective:** Finalize the locked 6-vertex, 9-edge PS-O1 network partitioning optimization ($W=27$) with QAOA ($p=1$, multi-start seeds $0 \dots 4$), validate Bell states on adjacent ($d=1$) and distant ($d=4$) physical qubit pairs, and co-design **Processor D** to eliminate routing overhead.
- **Key Scientific Results:**
  1. **Classical Ground Truth:** Global maximum cut $C^* = 22$ (symmetric partitions $S = \{0, 1, 3\}$ and $\bar{S} = \{2, 4, 5\}$). Uniform random baseline: $\langle C \rangle = 13.5000$ ($r = 0.6136$).
  2. **Processor D Architecture:** Co-designed custom 9-qubit planar transmon processor with 13 coupling edges (degree $\le 4$, connected, planar). Validated via `qff_phase2.validate_processor_d()` with **0 violations** (SHA-256: `f3f16cf1825f8365e9c0b850f4df73bc5590697c94fa1bdb8925d0801b44c4f9`).
  3. **Zero-SWAP Routing:** Processor D natively embeds all 9 problem edges, eliminating **100% of routing SWAP gates** (0 vs 1 on B), saving 14.3% CX gates (18 vs 21), and reducing circuit depth by 21.6% (29 vs 37).
  4. **Sampled Solution Quality:** Under realistic simulated noise ($p_1 = 10^{-3}, p_2 = 5 \times 10^{-3}, p_{\text{readout}} = 10^{-2}$), Processor D achieves approximation ratio $r = 0.7862$ ($P_{\text{opt}} = 12.50\%$, a $4.0\times$ improvement over random guessing).
  5. **Bell-State Tomography (Objective 1):** Full quantum state tomography across $XX, YY, ZZ$ bases confirms significant fidelity degradation from near pair $(0, 2)$ ($d=1$, $\mathcal{F} = 0.9633 \pm 0.0021$) to distant pair $(0, 7)$ ($d=4$, $\mathcal{F} = 0.9420 \pm 0.0026$), with $\Delta \mathcal{F} = -0.0213$ ($6.37\sigma$ significance), proving the physical noise cost of multi-hop routing.

---

## How to Run & Reproduce Phase 2

All Phase 2 execution instructions use standard cross-platform commands and can be run on Windows, Linux, or macOS.

### Step 1: Navigate to the Phase 2 Directory
```bash
cd PHASE_2
```

### Step 2: Set Up Virtual Environment & Dependencies
```bash
# Create a Python 3.11 virtual environment
python -m venv .venv

# Activate environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install exact pinned requirements
pip install -r requirements.txt
```

### Step 3: Run the Complete Master Pipeline
```bash
# Executes problem modeling, classical baselines, QAOA optimization,
# cross-processor benchmarking, Bell tomography, table export, and figure generation:
python scripts/run_all.py
```

### Step 4: Validate Deliverable Integrity
```bash
python scripts/validate_results.py
```

### Step 5: Run Automated Unit Tests (24 Tests)
```bash
pytest -v tests/
```

### Step 6: Execute the Jupyter Notebook
```bash
python -m jupyter nbconvert --to notebook --execute --inplace main.ipynb
```

### Step 7: Build Validated Submission ZIP
```bash
python scripts/package_submission.py
```

---

## Scientific Data, Tables, and Figures Location

In [`PHASE_2/`](PHASE_2/):
- **Consolidated Results Table:** [`PHASE_2/results/tables/results.csv`](PHASE_2/results/tables/results.csv) (Official 6-row benchmark table).
- **Bell State Metrics:** [`PHASE_2/results/tables/bell.csv`](PHASE_2/results/tables/bell.csv).
- **Bell Measurement Circuits:** [`PHASE_2/results/tables/bell_circuits.csv`](PHASE_2/results/tables/bell_circuits.csv) (All 12 circuits documented).
- **Optimization Trajectories:** [`PHASE_2/results/tables/optimization_runs.csv`](PHASE_2/results/tables/optimization_runs.csv) (Seeds 0 through 4).
- **Classical Enumeration:** [`PHASE_2/results/tables/classical_enumeration.csv`](PHASE_2/results/tables/classical_enumeration.csv) (All 64 cut weights).
- **Raw Count Distributions:** [`PHASE_2/results/raw/qaoa_counts.json`](PHASE_2/results/raw/qaoa_counts.json) and [`PHASE_2/results/raw/bell_counts.json`](PHASE_2/results/raw/bell_counts.json).
- **Publication Figures (20 unique designs, 40 PNG/SVG files):** Located in [`PHASE_2/results/figures/`](PHASE_2/results/figures/).

---

## Submission Checklist & Compliance Status

- [x] Authentic official starter module `qff_phase2.py` preserved unmodified (`04be4fa610ba60854a2b3b9237891df7e8ade62e2fcd9659076e36e794f077ab`).
- [x] Official 6-vertex, 9-edge instance `instances.json` preserved unmodified (`2d0cba3f07a51d96053f3e280bb3b379e43b17c6031ae2e95ca74775d7b56831`).
- [x] Custom Processor D passes official validator with **0 violations** (`f3f16cf1825f8365e9c0b850f4df73bc5590697c94fa1bdb8925d0801b44c4f9`).
- [x] Fully executed JupyterLab notebook (`PHASE_2/main.ipynb`) with standard `python3` kernel.
- [x] Complete 6-page scientific report (`PHASE_2/report.md`).
- [x] Genuine Phase 1 project preserved completely under [`PHASE_1/`](PHASE_1/).
- [x] All 24 automated unit tests pass in `PHASE_2/` and all 18 unit tests pass in `PHASE_1/`.
- [x] Standalone validated submission package with external SHA-256 manifest ready for upload to the SRM AP Hackathon Portal.
