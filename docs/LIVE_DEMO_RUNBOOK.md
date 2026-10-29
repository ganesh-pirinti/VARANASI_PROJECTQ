# VARANASI — Live Judge Demonstration Runbook

**Event:** Qiskit Fall Fest 2026 — SRM University-AP  
**Track:** Optimization  
**Problem Statement:** PS-O1 — Quantum Optimization of Network Partitioning Using QAOA  
**Team ID:** `AP251100708044` | **Team:** VARANASI  

---

## 1. Quick Launch (Zero Setup Required)

Open a PowerShell terminal in `C:\Projects\VARANASI_PROJECTQ` and run:

```powershell
# Option A (Recommended): Launch Studio via built-in Python Server
python scripts/start_studio.py
```
This automatically serves the Studio at **`http://localhost:5173`** (or `http://localhost:8000`) and opens your default browser.

```powershell
# Option B: Run via Vite Dev Server
cd web
npm run dev
```

---

## 2. Recommended Live Demonstration Sequence (5 Minutes)

Follow this step-by-step sequence during your presentation:

### Step 1: Open Scenario & Problem Formulation (`Tab: Overview`)
- **Action:** Show the Interference-Aware Channel Allocation narrative.
- **Talking Point:** "In dense cellular networks, base stations sharing frequencies create co-channel interference. We formulate bi-partitioning a 6-node network to maximize orthogonal channel assignment, mapping directly to Problem PS-O1 (Weighted Max-Cut)."

### Step 2: Interactive 3D Graph Lab (`Tab: 3D Graph Lab`)
- **Action:** Click and drag to orbit the 3D graph. Toggle between "Locked Graph" and "Optimal Partition".
- **Inspection:** Click on node 0 or node 3 to highlight incident edges.
- **Key Number:** Highlight $C^* = 22 / 27$ (81.48% cut weight; 7 cut edges in coral dashed lines, 2 internal edges in gray solid lines).

### Step 3: Classical Optimization Station (`Tab: Classical Station`)
- **Action:** Scroll through the 64 classical bit assignments in the interactive state matrix.
- **Talking Point:** "With 6 vertices, exhaustive evaluation of all 64 states gives us an exact, immutable ground truth: exactly two complementary states (`110100` and `001011`) achieve the maximum cut of 22."
- **Contrast:** Contrast with the uniform random baseline: mean cut 13.50 ($r = 0.6136$), $P_{\text{opt}} = 3.125\%$.

### Step 4: Hybrid QAOA & Circuit Explorer (`Tab: Circuit Explorer`)
- **Action:** Click on Edge `(0, 3)` with weight 4.
- **Result:** The UI highlights logical qubit wires $q_0$ and $q_3$, displays the Hamiltonian term $2 (I - Z_0 Z_3)$, and highlights the corresponding $\text{CX}(0,3) \to R_Z(4\gamma) \to \text{CX}(0,3)$ block.
- **Interactive Parameter Slider:** Move the $\gamma$ and $\beta$ sliders to observe the theoretical statevector cut expectation update on the energy landscape. Point out global optimum $(-0.1680, 0.3327)$ with $\langle C \rangle = 17.7128$ ($r = 0.8051$).

### Step 5: Hardware Mapping & Co-Design Station (`Tab: Hardware Mapping`)
- **Action:** Toggle between Processor B and Processor D.
- **Visual:** Show how Processor B's generic coupling map requires 1 SWAP (+3 CX gates) to connect missing edge $(1, 4)$.
- **Co-Design Triumph:** Switch to Processor D to show 0 SWAPs, $-14.3\%$ physical CX gates (18 vs 21), and $-21.6\%$ depth (29 vs 37), strictly obeying degree $\le 4$.

### Step 6: Software Station vs Quantum Execution Lane (`Tab: Dual-Lane Studio`)
- **Action:** Inspect the dual-lane process flow:
  - Software Lane: Input $\to$ QUBO $\to$ Transpilation $\to$ Classical Optimizer.
  - Quantum Execution Lane: AerSimulator $\to$ Depolarizing Noise $\to$ 4,096 Shots $\to$ 64 Bitstrings.
- **Status Verification:** The UI clearly displays: *"Execution Mode: Local Qiskit AerSimulator (Official Noise Model). No physical QPU claimed."*

### Step 7: Sampled Distribution & Stochastic Dominance (`Tab: Results & CCDF`)
- **Action:** View the dual PMF and staircase Complementary CDF ($P(C \ge c)$).
- **Evidence:** Point out the spike at $C^* = 22$: Processor D samples 512 optimal cuts ($12.50\%$), exactly $4.0\times$ higher than uniform random guessing ($3.125\%$).
- **Statistical Honesty:** Point out that noisy approximation ratios ($r = 0.7862$ on D vs $0.7874$ on B) are numerically indistinguishable within shot noise ($\Delta r = -0.0012$, $\text{SE} \approx 0.0028$). D's benefit is physical resource efficiency.

### Step 8: Exploratory Knapsack Module (`Tab: Knapsack Explorer`)
- **Action:** Toggle on individual emergency supply items to observe total weight vs capacity (15) and total value update interactively. Show the exact classical optimum $\{0, 1, 2, 3\}$ (value 26, weight 14).

### Step 9: Research Report & Pitch Deck
- **Action:** Switch to `Tab: Research Report` to scroll through the full 16-section report directly in the app. Show links to `VARANASI_Pitch_Deck.pptx` and `.pdf`.

---

## 3. Fallback Steps During Live Evaluation

| Issue | Immediate Fallback |
| :--- | :--- |
| **WebGL / GPU acceleration disabled** | The 3D Graph Lab includes an automatic 2D SVG canvas fallback button (`"Switch to 2D Fallback"`). |
| **Browser fails to load** | Open static slides [`presentation/VARANASI_Pitch_Deck.pdf`](../presentation/VARANASI_Pitch_Deck.pdf) or pre-rendered figures in [`results/figures/`](../results/figures/). |
| **Port conflict on 5173** | `python scripts/start_studio.py --port 8080` or `npm run dev -- --port 8080`. |
| **Judge asks for raw proof** | Run `python -m unittest tests/test_raw_results.py -v` to print 14 passing verification proofs in 0.01 seconds. |
