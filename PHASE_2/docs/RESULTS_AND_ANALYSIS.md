# Results and Performance Analysis: PS-O1 Network Partitioning

## 1. Classical Ground Truth and Verification

Exhaustive brute-force evaluation of all $2^6 = 64$ bitstrings on the 6-vertex, 9-edge, $W = 27$ network graph yielded the definitive classical benchmark:

- **Maximum Cut Value ($C^*$)**: **22**
- **Optimal Partitions**:
  - Assignment $(1, 1, 0, 1, 0, 0) \implies S = \{0, 1, 3\}, \bar{S} = \{2, 4, 5\}$ (Qiskit bitstring `'001011'`)
  - Assignment $(0, 0, 1, 0, 1, 1) \implies S = \{2, 4, 5\}, \bar{S} = \{0, 1, 3\}$ (Qiskit bitstring `'110100'`)
  - These two partitions are exact bitwise complements, reflecting the fundamental $\mathbb{Z}_2$ spin-reversal symmetry of Max-Cut.
- **Internal Edge Weights**:
  - In $S = \{0, 1, 3\}$: internal edge $(0, 3)$ with weight 4.
  - In $\bar{S} = \{2, 4, 5\}$: internal edge $(2, 4)$ with weight 1.
  - Total internal edge weight = $4 + 1 = 5$.
  - Cut weight = $27 - 5 = 22$.
- **Fractional Metrics**:
  - Weighted cut fraction: $22 / 27 \approx 81.48\%$
  - Cut edge fraction: $7 / 9 \approx 77.78\%$
- **Uniform Random Baseline**:
  - Expected cut: $\langle C \rangle_{\text{random}} = \frac{W}{2} = 13.5000$
  - Approximation ratio: $r_{\text{random}} = \frac{13.5}{22} \approx 0.6136$
  - Optimal hit probability: $P_{\text{opt, random}} = \frac{2}{64} = 0.03125$ ($3.125\%$)

---

## 2. QAOA Variational Optimization Trajectory

The level-1 QAOA ansatz ($p = 1$) was optimized using the COBYLA algorithm initialized across 5 distinct random seeds ($s \in \{0, 1, 2, 3, 4\}$):

| Seed | Initial $(\gamma_0, \beta_0)$ | Final $\gamma^*$ | Final $\beta^*$ | Expected Cut $\langle C \rangle$ | Approx. Ratio ($r$) | Iterations | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | (2.0011, 0.8476) | 2.9604 | -0.4071 | 15.5515 | 0.7069 | 43 | Converged |
| 1 | (1.6079, 2.9860) | 2.9607 | 4.2997 | 15.5510 | 0.7069 | 80 | MaxIter (Terminated) |
| 2 | (0.8219, 0.9377) | 2.9605 | -0.4072 | 15.5515 | 0.7069 | 36 | Converged |
| **3** | **(0.2691, 0.7440)** | **-0.1680** | **0.3327** | **17.7128** | **0.8051** | **37** | **Converged (Best Observed)** |
| 4 | (2.9627, 1.6064) | 4.7080 | 0.8494 | 15.5324 | 0.7060 | 49 | Converged |

**Analysis of Multi-Start Optimization Runs**:
- **Distribution of Trajectories**: Seed 1 reached the maximum iteration budget (`MaxIter` = 80) without achieving full convergence. Seeds 0, 2, and 4 converged to suboptimal local plateaus with $\langle C \rangle \approx 15.53$–$15.55$ ($r \approx 0.7060$–$0.7069$).
- **Best Observed Result**: Seed 3 produced the best observed result among the five starts, uniquely converging to the lowest energy basin on this grid with $\langle C \rangle = 17.7128$ and an approximation ratio of $r = 0.8051$ (+31.2% over uniform random baseline of $0.6136$).
- **Ensemble Summary Statistics**:
  - Mean approximation ratio across 5 seeds: $\bar{r} = 0.7264 \pm 0.0440$ ($72.64\% \pm 4.40\%$)
  - Mean expected cut: $\overline{\langle C \rangle} = 15.98 \pm 0.97$
  - Best observed approximation ratio: $r_{\text{best}} = 0.8051$ (Seed 3)
- **Explanation of Negative $\gamma^*$ on Seed 3**: The cost Hamiltonian unitary $e^{-i \gamma \hat{H}_C}$ generates periodic expectation values with period $2\pi / \gcd(w_{uv}) = 2\pi$. Unconstrained local optimization routines like COBYLA can explore negative coordinate directions, finding an equivalent minimum basin at $\gamma^* = -0.1680 \equiv 2\pi - 0.1680 \approx 6.115$. This is a standard feature of continuous trigonometric optimization.
- **Critical Distinction**: The best variational continuous parameter result ($\langle C \rangle = 17.7128$) is distinct from the exact discrete Max-Cut combinatorial ground truth ($C^* = 22$). Variational sampling provides a state from which optimal bitstrings are sampled with $P_{\text{opt}} \approx 12.5\%$.

---

## 3. Cross-Processor Benchmarking

The optimized QAOA circuit ($p = 1$, 4096 shots) was compiled and evaluated across Processors A, B, and D under both ideal (noiseless) and noisy simulation:

| Processor | Condition | Executable | SWAPs | CX Gates | Circuit Depth | 2Q Depth | Mean Cut $\langle C \rangle$ | Approx Ratio ($r$) | $P_{\text{opt}}$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Processor A** | N/A | **No** | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **Processor B** | Ideal | Yes | 1 | 21 | 37 | 17 | 17.7620 | 0.8074 | 0.1396 |
| **Processor B** | Noisy | Yes | 1 | 21 | 37 | 17 | 17.3220 | 0.7874 | 0.1260 |
| **Processor D** | Ideal | Yes | 0 | 18 | 29 | 14 | 17.7134 | 0.8052 | 0.1384 |
| **Processor D** | Noisy | Yes | 0 | 18 | 29 | 14 | 17.2971 | 0.7862 | 0.1250 |
| **Random Baseline** | Analytic | Yes | N/A | N/A | N/A | N/A | 13.5000 | 0.6136 | 0.0313 |
| **Classical Ground Truth**| Brute-force | Yes | N/A | N/A | N/A | N/A | 22.0000 | 1.0000 | N/A |

### Objective Scientific Interpretation:
1. **Compilation Resource Advantage**:
   - Processor D achieves the **theoretical minimum CX count** of 18 gates (2 CX gates per edge for 9 problem edges) with **0 SWAP gates**.
   - Compared to Processor B, Processor D reduces CX count by $-14.3\%$ (18 vs. 21), overall circuit depth by $-21.6\%$ (29 vs. 37), and two-qubit depth by $-17.6\%$ (14 vs. 17).
2. **Sampled Solution Quality and Standard Error Analysis**:
   - Using the 4096 raw measurement shots, we compute the sample standard error for both noisy processors:
     - **Processor B (Noisy)**: Sampled mean cut $\langle C \rangle = 17.3220 \pm 0.0598$, Approx. Ratio $r = 0.7874 \pm 0.0027$ ($17.3220 / 22 = 0.7874$), $P_{\text{opt}} = 0.1260 \pm 0.0052$.
     - **Processor D (Noisy)**: Sampled mean cut $\langle C \rangle = 17.2971 \pm 0.0612$, Approx. Ratio $r = 0.7862 \pm 0.0028$ ($17.2971 / 22 = 0.7862$), $P_{\text{opt}} = 0.1250 \pm 0.0052$.
   - The observed numerical difference between Processor B and Processor D is:
     $$\Delta \langle C \rangle = 0.0249 \pm 0.0856 \implies \Delta r = 0.0011 \pm 0.0039$$
   - Computing the z-score: $z = \frac{0.024902}{0.085588} \approx 0.2910\sigma$ ($p = 0.7711$). Because $z \ll 2\sigma$, the difference in sampled mean cut is not statistically significant under 4096 shots.
   - **Distributional Identity Nuance**: Crucially, failing to reject the null hypothesis of equal means does not prove that the underlying 64-element output probability distributions are identical. Transpiling onto Processor B inserts a routing SWAP gate (+3 CX gates), creating subtle differences in state-to-state transition amplitudes across computational basis states even though the overall expectation value $\langle C \rangle$ remains within statistical noise.
   - Both processors deliver an optimal hit probability of $P_{\text{opt}} \approx 12.5\%$, which is **$4.0\times$ higher than classical random sampling** ($3.125\%$).
   - **Theoretical Scaling Potential**: Processor D's primary benefit is **resource efficiency** (eliminating 100% of routing overhead). While at $p=1$ the single SWAP gate on Processor B incurs limited error, Processor D represents future architectural potential to prevent cumulative error escalation if QAOA circuits are scaled to higher depths ($p \ge 2$), where routing overhead would compound linearly. Only depth $p=1$ was evaluated in this benchmark.

---

## 4. Bell State Tomography on Processor D (Simulated Measurements)

To isolate and quantify the simulated decoherence and gate infidelity introduced by multi-hop routing, we prepared the maximally entangled Bell state $|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$ on Processor D across two pairs:
1. **Adjacent Pair $(0, 2)$**: Graph distance $d = 1$, connected directly by native hardware coupling. Requires **1 CX gate**.
2. **Distant Pair $(0, 7)$**: Graph distance $d = 4$, requiring multi-hop SWAP routing. Requires **10 CX gates**.

State tomography was conducted across the Pauli bases $XX$, $YY$, and $ZZ$ (4096 shots per basis). State fidelity was evaluated via:
$$\mathcal{F} = \frac{1 + \langle Z_A Z_B \rangle + \langle X_A X_B \rangle - \langle Y_A Y_B \rangle}{4}$$
with standard error:
$$SE(\mathcal{F}) = \frac{1}{4} \sqrt{SE_{XX}^2 + SE_{YY}^2 + SE_{ZZ}^2}$$

| Qubit Pair | Distance ($d$) | CX Gates | Condition | $\langle ZZ \rangle$ | $\langle XX \rangle$ | $\langle YY \rangle$ | Fidelity $\mathcal{F}$ | Uncertainty $SE(\mathcal{F})$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $(0, 2)$ | 1 | 1 | Ideal | +1.0000 | +1.0000 | -1.0000 | **1.0000** | $\pm 0.0000$ |
| $(0, 2)$ | 1 | 1 | Noisy | +0.9551 | +0.9458 | -0.9521 | **0.9633** | $\pm 0.0021$ |
| $(0, 7)$ | 4 | 10 | Ideal | +1.0000 | +1.0000 | -1.0000 | **1.0000** | $\pm 0.0000$ |
| $(0, 7)$ | 4 | 10 | Noisy | +0.9399 | +0.9243 | -0.9038 | **0.9420** | $\pm 0.0026$ |

### Statistical Analysis:
- Near pair $(0, 2)$ simulated fidelity: $\mathcal{F}_{\text{near}} = 0.9633 \pm 0.0021$.
- Distant pair $(0, 7)$ simulated fidelity: $\mathcal{F}_{\text{far}} = 0.9420 \pm 0.0026$.
- Measured degradation: $\Delta \mathcal{F} = \mathcal{F}_{\text{far}} - \mathcal{F}_{\text{near}} = -0.0213$.
- Combined uncertainty:
  $$\sigma_{\Delta} = \sqrt{SE_{\text{near}}^2 + SE_{\text{far}}^2} = \sqrt{(0.00209)^2 + (0.00261)^2} \approx 0.00334$$
- Z-score:
  $$z = \frac{|\Delta \mathcal{F}|}{\sigma_{\Delta}} = \frac{0.02124}{0.00334} \approx 6.37\sigma$$
- This confirms with $>6.3\sigma$ statistical significance that multi-hop routing SWAPs degrade quantum state fidelity under the official depolarizing noise model.
