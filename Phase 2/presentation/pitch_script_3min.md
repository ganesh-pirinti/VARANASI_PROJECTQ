# VARANASI — 3-Minute Timed Pitch Script

**Track:** Optimization  
**Problem Statement:** PS-O1 — Quantum Optimization of Network Partitioning Using QAOA  
**Team ID:** AP251100708044  
**Target Duration:** 3 Minutes (180 Seconds)  
**Word Count:** ~410 words (Pacing: ~135 words/minute)  

---

### [0:00 – 0:30] Executive Thesis & Problem Statement
"Distinguished judges, we are Team VARANASI. Today, we address Problem Statement PS-O1: Quantum Optimization of Network Partitioning Using QAOA.

In the NISQ era, quantum algorithms are severely limited by hardware topology. When a problem's interaction graph does not match the physical layout of the quantum processor, compilers are forced to insert SWAP gates. These extra gates rapidly erode coherence and inflate circuit depth.

Our solution is problem-matched hardware co-design. By engineering Processor D to natively reflect the PS-O1 network partitioning instance, we eliminate 100% of routing SWAPs, cutting physical CX gates by 14.3% and circuit depth by 21.6%."

---

### [0:30 – 1:00] Classical Ground Truth & Baseline
"To ensure scientific rigor, we first exhaustively evaluated all 64 bit assignments on the locked 6-vertex, 9-edge PS-O1 graph.

The exact classical maximum cut is 22 out of a total weight of 27—an 81.5% cut fraction, cutting 7 of the 9 edges. Exactly two bitwise-complement partitions achieve this optimum: subset {0, 1, 3} and subset {2, 4, 5}.

In contrast, a uniform random baseline yields an expected cut of only 13.5 with an approximation ratio of 0.6136, hitting the optimal cut only 3.1% of the time. This gave us an exact, immutable benchmark."

---

### [1:00 – 1:45] Hardware Topologies & Transpilation Efficiency
"We then benchmarked three processor architectures.

Processor A, with 5 qubits, represents a capacity bottleneck—it cannot execute a 6-qubit problem and is strictly marked infeasible.

Processor B has 9 qubits in a generic grid, but lacks the direct edge between nodes 1 and 4. The transpiler must insert a SWAP gate, adding 3 CX gates and pushing total depth to 37.

Processor D is our co-designed 9-qubit architecture. Its 6-node core embeds the complete problem graph natively, connected to a 3-node ancillary ring with maximum degree 4.

The result? Zero SWAPs. Physical CX gates drop from 21 to 18. Two-qubit depth drops from 17 to 14. Because CX gates are the dominant noise source in physical hardware, this hardware co-design provides immediate physical fidelity protection."

---

### [1:45 – 2:30] Empirical Results & 4.0x Sampling Enhancement
"We validated Processor D through Bell-state tomography, measuring 0.9633 fidelity on the near pair and 0.9420 on the far pair, accurately capturing multi-hop gate error accumulation.

Running QAOA at depth p=1 with 4,096 shots under official depolarizing and readout noise, Processor D achieved an approximation ratio of 0.7862, numerically indistinguishable from Processor B at 0.7874.

Crucially, Processor D concentrated 512 shots onto the exact optimal cut—a 12.5% sampling probability. That is a 4.0x enhancement over random guessing, and our Complementary CDF proves strict stochastic dominance across all high-value cut thresholds."

---

### [2:30 – 3:00] Conclusion & Scalability
"To conclude: our project proves that hardware co-design shifts the Pareto frontier. We achieve identical solution quality while eliminating 14.3% of two-qubit gates and 21.6% of depth.

As QAOA scales to deeper layers where routing overhead compounds exponentially, problem-matched co-design will be the key to practical quantum optimization.

Thank you. We welcome your questions."
