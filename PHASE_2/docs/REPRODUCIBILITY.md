# Reproducibility Guide: PS-O1 Quantum Optimization

This guide provides step-by-step instructions to set up the environment, verify dependencies, execute the end-to-end simulation pipeline, run the automated test suite, and evaluate the Jupyter notebook on any standard workstation (Windows, macOS, or Linux).

---

## 1. System Requirements & Portability

- **Python Version**: Python 3.11 (tested on Python 3.11.9, compatible with Python 3.10–3.12).
- **Core Quantum Libraries**: Qiskit `>=1.4,<3` (tested with Qiskit 2.6.1) and Qiskit Aer `>=0.17` (tested with 0.18.2).
- **Compute Requirements**: Standard laptop/desktop CPU (no GPU or quantum hardware required). All quantum circuits are simulated via Qiskit Aer. Full pipeline execution takes under 10 seconds.
- **Paths**: All scripts, source modules, tests, and notebooks use repository-relative paths (`Path(__file__).resolve().parent.parent`), allowing the project to run from any directory.

---

## 2. Environment Setup (Any Machine)

### Step 1: Clone or Extract the Repository
```powershell
# Open a terminal and navigate to the project directory
cd <PROJECT_ROOT>
```

### Step 2: Create and Activate a Python 3.11 Virtual Environment
```powershell
# Windows (PowerShell):
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS (bash/zsh):
python3.11 -m venv .venv
source .venv/bin/activate
```

*(Note for local reference machine: the pre-configured environment in `C:\QFF\.qff2026-venv\Scripts\python.exe` may be used directly without recreating `.venv`.)*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

Verify installed package versions:
```powershell
python -c "import qiskit, qiskit_aer, numpy, scipy; print('Qiskit:', qiskit.__version__, 'Aer:', qiskit_aer.__version__, 'NumPy:', numpy.__version__)"
```

---

## 3. Step-by-Step Reproduction Commands

From the project root directory:

### 3.1 Run the Full Master Pipeline
```powershell
python scripts/run_all.py
```
*What this does:*
1. Solves exact classical ground truth over all 64 bitstrings ($C^* = 22$).
2. Validates Processor D architecture rules (0 violations).
3. Executes multi-restart QAOA optimization across seeds $0 \dots 4$ (Seed 3 best: $\langle C \rangle = 17.7128, r = 0.8051$).
4. Runs cross-processor benchmarks (A, B, D) under ideal and noisy simulation (4096 shots).
5. Runs Objective 1 Bell-state tomography across all 12 circuits ($2 \text{ pairs} \times 2 \text{ conditions} \times 3 \text{ bases}$).
6. Generates 20 scientific figures in both PNG and SVG formats.
7. Computes and exports sampling statistics and difference z-scores to `results/raw/benchmark_metadata.json`.
*Expected runtime:* ~6–8 seconds on a standard CPU.

### 3.2 Validate Output and Artifact Integrity
```powershell
python scripts/validate_results.py
```
*Expected Output:*
`VALIDATION RESULT: ALL PASS [OK]` (validating Processor D, results.csv, bell.csv, bell_circuits.csv, bell_counts.json, all 20 PNG figures, and metadata).

### 3.3 Run the Automated Test Suite (24 Tests)
```powershell
pytest -v tests/
```
*Expected Output:*
`24 passed in ~3-5s` (0 failures, 0 errors, 0 warnings across 6 test modules).

### 3.4 Execute and Populate the Jupyter Notebook
```powershell
python -m jupyter nbconvert --execute --inplace main.ipynb
```
*Expected Output:*
Converts and executes `main.ipynb` top-to-bottom in ~7 seconds without error, populating all outputs, tables, and rendered figures inline.

### 3.5 Package Submission Archive
```powershell
python scripts/package_submission.py
```
*Expected Output:*
Creates `dist/QFF2026_PS-O1_Phase2_Submission.zip` and `dist/QFF2026_PS-O1_Phase2_Submission.sha256`, and validates the archive via clean-extraction smoke testing in an isolated temporary directory.

---

## 4. Hardware Simulation Disclaimer

All quantum circuits in this project are executed on classical simulators using the official Qiskit Aer noise model ($p_1 = 10^{-3}, p_2 = 5 \times 10^{-3}, p_{\text{readout}} = 10^{-2}$). No physical quantum processing unit (QPU) hardware access was provided or claimed for Phase 2.
