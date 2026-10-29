# VARANASI — Official PS-O1 Submission Dossier

**Qiskit Fall Fest 2026 — SRM University-AP**  
**Track:** Quantum Optimization  
**Problem Statement:** PS-O1 — Quantum Optimization of Network Partitioning Using QAOA  
**Project Name:** VARANASI — Quantum Optimization Studio  
**Submission Package:** `Phase 2/dist/VARANASI_PS-O1_Phase2_Submission.zip`  

---

## 1. Official Team & Project Metadata

| Field | Official Value |
| :--- | :--- |
| **Team ID** | `AP251100708044` |
| **Team Name** | **VARANASI** |
| **Team Leader** | Ganesh Pirinti (`ganeshpirinti95218@gmail.com`) |
| **Institution** | SRM University-AP |
| **Event Track** | Quantum Optimization (PS-O1) |
| **Target Problem** | Weighted Network Partitioning via QAOA |
| **Benchmark Graph** | 6 Vertices, 9 Weighted Edges, Total Weight = 27, Optimal Cut = 22 |
| **Live Web Studio** | [https://web-delta-seven-31.vercel.app](https://web-delta-seven-31.vercel.app) |
| **Session 01 3D Explorer** | [https://web-delta-seven-31.vercel.app/mission22.html](https://web-delta-seven-31.vercel.app/mission22.html) |
| **Git Repository** | [https://github.com/ganesh-pirinti/VARANASI_PROJECTQ](https://github.com/ganesh-pirinti/VARANASI_PROJECTQ) |
| **Default Branch** | `main` |
| **Release Archive** | `Phase 2/dist/VARANASI_PS-O1_Phase2_Submission.zip` |
| **Release Archive Size** | `10,761,227 bytes` |
| **Release SHA-256** | `6865A60174AAD873F3408644B394D49967B492C43C65F4E75D55B71C1969A0B7` |

---

## 2. Executive Scientific Summary

The **VARANASI** submission delivers an end-to-end, scientifically validated, and hardware-aware quantum optimization pipeline for weighted network partitioning using the Quantum Approximate Optimization Algorithm (QAOA).

### 2.1 First-Principles Mathematical Truth
- **Problem Instance:** Graph $G=(V, E, w)$ with $|V| = 6$ nodes and $|E| = 9$ edges:
  $$(0,2):1, (0,3):4, (0,4):4, (1,4):3, (1,5):3, (2,3):5, (2,4):1, (3,4):4, (3,5):2$$
- **Total Weight:** $W_{\text{total}} = 27.0$.
- **Max-Cut Ground Truth:** Exhaustive classical enumeration across all $2^6 = 64$ bitstrings proves the exact maximum cut is $C^* = 22.0$.
- **Complementary Global Optima:** Exactly **two** bitstrings achieve $C^* = 22.0$:
  1. $x = (1, 1, 0, 1, 0, 0)$ $\implies$ Group $S = \{0, 1, 3\}$, Group $\bar{S} = \{2, 4, 5\}$
  2. $x = (0, 0, 1, 0, 1, 1)$ $\implies$ Group $S = \{2, 4, 5\}$, Group $\bar{S} = \{0, 1, 3\}$
  Separating 7 crossing edges (weight 22) and leaving 2 internal uncut edges: $(0,3)$ (weight 4) and $(2,4)$ (weight 1).
- **Uniform Random Guessing Baseline:** $\mathbb{E}[C] = 27 / 2 = 13.5$ with sampling probability $P_{\text{random}}(\text{optimal}) = 2 / 64 = 3.125\%$.
- **QUBO Equivalence:** Verified that $-C(x) = x^T Q x$ for all 64 bitstrings with $Q_{ii} = -\text{deg}_w(i)$ and $Q_{ij} = 2 w_{ij}$ ($i < j$).

### 2.2 Quantum vs Classical Benchmark Performance
All metrics derived from 4,096 shots per run under Qiskit `AerSimulator` and `FakeKyoto` thermal relaxation and depolarization noise models:

| Processor | Simulation Mode | Mean Cut $\langle C \rangle$ | Approx Ratio $r$ | Optimal Shots ($C=22$) | Optimal Sampling Prob | Probability Gain vs Random |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Uniform Random**| Classical Baseline | 13.5000 | 0.6136 | 128 / 4096 | 3.125% | $1.0\times$ |
| **Processor B** | Ideal Simulation | 17.7620 | 0.8074 | 572 / 4096 | 13.96% | $4.47\times$ |
| **Processor B** | FakeKyoto Noise | 17.3220 | 0.7874 | 516 / 4096 | 12.60% | $4.03\times$ |
| **Processor D** | Ideal Simulation | 17.7134 | 0.8052 | 567 / 4096 | 13.84$ | $4.43\times$ |
| **Processor D** | FakeKyoto Noise | 17.2971 | 0.7862 | 512 / 4096 | 12.50% | **$4.00\times$** |

### 2.3 Hardware Co-Design & Routing Elimination
- **Processor A (5-qubit linear):** Insufficient qubits ($N=5 < 6$); physically incapable of embedding the 6-vertex problem graph.
- **Processor B (127-qubit heavy-hex subgrid):** Requires routing SWAPs due to limited nearest-neighbor connectivity.
  - Physical CX gates: **21** (18 algorithmic + 3 from 1 SWAP).
  - 2-qubit gate depth: **17**.
- **Processor D (9-qubit ring-core co-design):** Designed specifically to natively embed the 6-vertex graph topology.
  - Routing SWAPs: **0 SWAPs (100% elimination)**.
  - Physical CX gates: **18** (exact algorithmic minimum, **14.3% reduction**).
  - 2-qubit gate depth: **14 (21.6% reduction)**.
  - Total gate count: **34 gates (8.1% reduction)**.
  - Noise parity: Matches Processor B solution quality ($r=0.7862$ vs $0.7874$, $|\Delta r| < \text{SE}_r$) while executing on a dramatically smaller, more efficient footprint.

---

## 3. Judge Presentation & Walkthrough Scripts

### 3.1 Elevator Pitch (60 Seconds)
> "Honorable judges, in Problem Statement PS-O1, quantum network partitioning faces a critical bottleneck: hardware topology constraints force heavy SWAP gate overhead, degrading circuit fidelity in noisy quantum hardware.
>
> In **VARANASI**, we implemented QAOA at depth $p=1$ on the locked 6-vertex, 9-edge benchmark. On standard heavy-hex architectures like Processor B, 3 additional CX gates and a routing SWAP are required, elevating physical CX gates to 21.
>
> To solve this, we introduced **Processor D**, a 9-qubit ring-core hardware co-design that embeds the problem graph natively. Processor D achieves **zero routing SWAPs**, saving 14.3% of two-qubit gates and reducing two-qubit depth by 21.6%. In realistic FakeKyoto noise simulation, it achieves an approximation ratio of $0.7862$ and a **4.0x sampling probability enhancement** over uniform random guessing.
>
> We back our research with a complete reproducible Python pipeline, an interactive Three.js 3D spatial explorer, and a playable puzzle challenge."

---

### 3.2 Technical Walkthrough (5 Minutes)

#### Step 1: Problem Definition & Mathematical Ground Truth (Slide 2–3)
- Point out the 6 nodes and 9 edges totaling weight 27.
- Emphasize that exhaustive classical scoring proves the maximum cut is exactly 22.0, with exactly two complementary global optima: $(1,1,0,1,0,0)$ and $(0,0,1,0,1,1)$.
- Explain the uniform random baseline of 13.5 (expectation $27/2$), which samples an optimum with only 3.125% probability.

#### Step 2: QAOA Circuit Implementation & Optimization (Slide 4–5)
- Explain the QAOA ansatz at depth $p=1$ with initial equal superposition $|+\rangle^{\otimes 6}$.
- Detail the cost unitary $U_C(\gamma) = \prod_{(u,v)} e^{-i \frac{\gamma w_{uv}}{2} Z_u Z_v}$, implemented with $CX - RZ(\gamma w_{uv}) - CX$ gate blocks.
- Highlight the multi-seed parameter optimization over 5 random seeds, converging to optimal parameters $(\gamma^*, \beta^*) = (2.7489, 0.3927)$.

#### Step 3: Hardware Topologies & Transpilation Analysis (Slide 6–7)
- Contrast Processor A (5 qubits, unroutable), Processor B (127-qubit heavy-hex subgrid), and Processor D (9-qubit ring-core).
- Demonstrate that Processor B requires 1 SWAP, causing 21 CX gates and depth 17.
- Demonstrate that Processor D eliminates all SWAPs, using exactly 18 CX gates with depth 14.

#### Step 4: Noisy Simulation & Bell State Validation (Slide 8–9)
- Present the AerSimulator results using IBM FakeKyoto calibration data.
- Show the 4.0x sampling probability enhancement ($12.50\%$ vs $3.125\%$).
- Reference the Bell state tomography showing nearest-neighbor fidelity of $0.9633$ vs distant-neighbor fidelity of $0.9420$, experimentally proving why SWAP elimination is vital.

#### Step 5: Interactive Studio Demo (Slide 10)
- Launch the web application and show:
  1. Overview and problem scenario.
  2. 3D WebGL Graph visualization and adjacency matrix.
  3. Interactive Labs: Session 01 (3D Explorer) and Session 02 (Mission 22 playable puzzle).

---

### 3.3 Judge Q&A Defense Quick Reference

- **Q: Did you claim quantum speedup?**  
  *A:* No. On a 6-node graph ($2^6 = 64$ states), classical enumeration takes under 1 ms. What we demonstrated is a **4.0x sampling probability enhancement** over random guessing and hardware co-design efficiency.
- **Q: Did you run on real physical hardware?**  
  *A:* No. All noisy benchmarks used Qiskit Aer's `FakeKyoto` thermal relaxation and depolarization noise models to ensure scientific reproducibility without queuing delays.
- **Q: Why are Processor B and D approximation ratios identical under noise?**  
  *A:* $|\Delta r| = |0.7862 - 0.7874| = 0.0012$, which is smaller than the standard error of the mean ($\text{SE}_r \approx 0.0016$). The solution quality is numerically equivalent, but Processor D achieves it with 14.3% fewer CX gates and zero SWAPs.

---

## 4. Verification & Reproduction Instructions for Judges

To verify the entire project from scratch in a clean environment:

### Step 1: Environment Setup
```bash
git clone https://github.com/ganesh-pirinti/VARANASI_PROJECTQ.git
cd VARANASI_PROJECTQ/"Phase 2"
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Run Consolidated Validation (Zero Errors Expected)
```bash
python scripts/validate_all.py
```
*Expected output:*
```
[Check 1/6] Locked Instance Integrity: PASS
[Check 2/6] Processor D Official Validation: PASS
[Check 3/6] CSV Tables Schema and Row Counts: PASS
[Check 4/6] Raw QAOA Histograms Integrity: PASS
[Check 5/6] Running Automated Unit Tests: PASS (27/27)
[Check 6/6] Studio Visualization Data: PASS
ALL 6 CONSOLIDATED CHECKS PASSED WITH ZERO ERRORS!
```

### Step 3: Run JavaScript Test Suite
```bash
cd web
npm install
npm test
```
*Expected output:* `7 passed, 0 failed`.

### Step 4: Run Vite Production Build & Web Studio
```bash
npm run build
npm run preview
# Open http://localhost:4173 in browser
```

---

## 5. Official Deliverables Checklist

- [x] `README.md` — Complete project documentation & quickstart.
- [x] `main.ipynb` — Fully executed Jupyter Notebook with all outputs and figures.
- [x] `qff_phase2.py` — Standalone execution script.
- [x] `results/tables/results.csv` — Official 6-row benchmark table.
- [x] `results/tables/bell.csv` — Bell state fidelity table.
- [x] `results/raw/qaoa_counts.json` — 4x 4096-shot raw QAOA histogram counts.
- [x] `processors/processor_A.json`, `processor_B.json`, `processor_D.json` — Official topologies.
- [x] `report.md` & `docs/VARANASI_RESEARCH_AND_IMPLEMENTATION_REPORT.md` — Comprehensive research paper.
- [x] `presentation/VARANASI_Pitch_Deck.pptx` & `.pdf` — Professional presentation deck.
- [x] `web/` — Interactive Quantum Optimization Studio with 2 Educational Game Sessions.
- [x] `dist/VARANASI_PS-O1_Phase2_Submission.zip` — Deterministic submission package with SHA-256 manifest.
