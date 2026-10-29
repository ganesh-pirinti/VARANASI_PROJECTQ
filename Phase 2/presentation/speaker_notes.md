# VARANASI — Slide-by-Slide Speaker Notes

**Event:** Qiskit Fall Fest 2026 — SRM University-AP  
**Track:** Optimization  
**Problem Statement:** PS-O1 — Quantum Optimization of Network Partitioning Using QAOA  
**Team ID:** AP251100708044  
**Team:** VARANASI  

---

### Slide 1: Title & Executive Summary
- **Visual Cue:** Highlight the executive thesis card and the 4 quantitative metric callout badges.
- **Talking Points:**
  - Good morning/afternoon, esteemed judges. We are Team VARANASI, presenting our solution for Problem Statement PS-O1: Quantum Optimization of Network Partitioning Using QAOA.
  - In NISQ optimization, the dominant source of error is not the algorithmic formulation, but the physical routing overhead imposed by mismatched hardware topologies.
  - Our core contribution is a problem-matched hardware co-design paradigm. By engineering Processor D to natively reflect the interaction topology of the PS-O1 network partitioning instance, we completely eliminate routing SWAPs.
  - This delivers a 14.3% reduction in physical CX gates and a 21.6% reduction in circuit depth, while achieving a 4.0x sampling enhancement for optimal bi-partitions over uniform random guessing.
- **Transition:** Let's first examine the problem formulation and the exact mathematical baseline.

---

### Slide 2: The Locked Problem & Classical Ground Truth
- **Visual Cue:** Point to the two partition clusters $S=\{0,1,3\}$ in blue and $\bar{S}=\{2,4,5\}$ in slate, and the dashed cut edges in coral.
- **Talking Points:**
  - The PS-O1 instance is a 6-vertex, 9-edge weighted network partitioning graph with a total edge weight of 27.
  - Before writing a single line of quantum code, we established an immutable classical baseline by exhaustively evaluating all $2^6 = 64$ bit assignments.
  - Classical ground truth yields an exact maximum cut of $C^* = 22$, representing 81.48% of the total edge weight and cutting 7 of the 9 edges.
  - Exactly two bitwise-complement states attain this optimum: $\{0, 1, 3\}$ and $\{2, 4, 5\}$.
  - In contrast, uniform random guessing yields an expected cut of only 13.5 with an approximation ratio of $0.6136$, hitting the optimal cut only 3.125% of the time.
- **Transition:** With this benchmark locked, we investigate how hardware coupling topologies constrain quantum execution.

---

### Slide 3: Processor Architectures & The Co-Design Hypothesis
- **Visual Cue:** Walk across the 3 topology panels from left to right: Processor A, Processor B, and Processor D.
- **Talking Points:**
  - We evaluated three distinct processor coupling architectures.
  - Processor A, with only 5 qubits, represents a fundamental capacity bottleneck. Since PS-O1 requires 6 logical qubits, it cannot execute the problem and is properly marked non-executable.
  - Processor B features 9 qubits arranged in a generic grid-like subgraph. However, it lacks a direct edge between physical qubits corresponding to logical edge $(1, 4)$. The Qiskit transpiler is forced to insert 1 SWAP gate, which expands into 3 additional CX gates (+16.7% overhead).
  - Processor D is our proposed co-design architecture. Its 6-node core directly embeds all 9 edges of the PS-O1 problem graph, with a 3-node ancillary ring that ensures maximum node degree does not exceed 4, strictly complying with official rules.
- **Transition:** Let's look at the quantitative impact of this co-design on compiled circuit resources.

---

### Slide 4: Transpilation Efficiency: Hardware Co-Design in Action
- **Visual Cue:** Reference the connected-dot dumbbell plot showing the horizontal distance between Processor B (indigo) and Processor D (teal).
- **Talking Points:**
  - Transpilation benchmarks reveal decisive physical resource savings across all primary metrics.
  - Physical CX gates are reduced from 21 down to 18—a 14.29% reduction.
  - Total circuit depth decreases from 37 down to 29 layers—a 21.62% reduction.
  - Two-qubit depth drops from 17 down to 14 layers—a 17.65% reduction.
  - Most importantly, routing SWAPs drop from 1 to 0—a complete 100% elimination of routing overhead.
  - In noisy quantum computing, two-qubit CX gates are five times noisier than single-qubit gates ($p_2 = 0.005$ vs $p_1 = 0.001$). Eliminating 3 CX gates preserves precious coherence across every shot.
- **Transition:** Before sampling QAOA, we empirically verified Processor D's physical behavior using quantum state tomography.

---

### Slide 5: Objective 1: Quantum Hardware Diagnostic (Bell State Tomography)
- **Visual Cue:** Highlight the point-and-whisker plot and the Pauli expectation breakdown ($\langle XX \rangle, \langle YY \rangle, \langle ZZ \rangle$).
- **Talking Points:**
  - Objective 1 mandates physical verification of Processor D using Bell state generation ($|\Phi^+\rangle$) across near and far qubit pairs under ideal and official noisy simulation.
  - For the near pair $(0, 2)$ at distance 1, requiring a single direct CX gate, the noisy fidelity is $0.9633 \pm 0.0021$.
  - For the far pair $(0, 7)$ at distance 4, requiring 10 CX gates due to routing across the ancillary ring, the noisy fidelity degrades to $0.9420 \pm 0.0026$.
  - This 2.13 percentage-point drop directly quantifies the accumulation of depolarizing gate noise and readout error across routing paths, demonstrating the accuracy of our hardware simulation.
- **Transition:** Now let us examine QAOA performance on the full PS-O1 instance.

---

### Slide 6: QAOA Solution Quality & 4.0x Sampling Enhancement
- **Visual Cue:** Direct attention to the dual-panel chart: the probability mass function on the left and the staircase Complementary CDF on the right.
- **Talking Points:**
  - We executed 4,096 shots per configuration, observing all 64 possible bitstrings.
  - On noisy simulation, Processor B achieves an approximation ratio of $r = 0.7874$, and Processor D achieves $r = 0.7862$.
  - The difference of $-0.0012$ (-0.15% relative) is well within finite-shot sampling error ($\text{SE} \approx 0.0027$), confirming that both processors achieve numerically similar solution quality.
  - Crucially, QAOA concentrates probability mass at the optimal cut $C^* = 22$: Processor D samples optimal bitstrings 512 times out of 4,096 ($12.50\%$), compared to only $3.125\%$ under random guessing.
  - This represents a 4.0x sampling enhancement. Furthermore, the Complementary CDF demonstrates strict stochastic dominance over the uniform random baseline for all cut values $c \ge 14$.
- **Transition:** Finally, let us explore the statevector optimization landscape and synthesize our conclusions.

---

### Slide 7: Algorithmic Landscape & Hardware Co-Design Conclusion
- **Visual Cue:** Point out the optimizer best-parameters star on the 2D energy landscape and the Pareto trade-off map.
- **Talking Points:**
  - Using statevector simulation, we mapped the exact energy expectation $\langle C \rangle(\gamma, \beta)$ across parameter space.
  - Multi-seed classical optimization converges to the global minimum at $\gamma^* = -0.1680$ and $\beta^* = 0.3327$, yielding a theoretical expectation of $17.7128$ ($r = 0.8051$).
  - The architecture trade-off map clearly illustrates the co-design advantage: Processor D shifts the Pareto frontier horizontally, drastically cutting physical gate resources while preserving solution fidelity.
  - As quantum optimization scales to deeper circuits ($p \ge 2$), eliminating routing overhead compounds multiplicatively, making co-design essential for practical quantum utility.
- **Transition:** Thank you. We are ready for your questions. Backup slides 8 and 9 detail our compliance checklist and adversarial defense.
