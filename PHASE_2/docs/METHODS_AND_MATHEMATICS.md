# Mathematical Foundations and Methods: PS-O1 Quantum Optimization of Network Partitioning

## 1. Network Partitioning Problem Formulation

In the context of the Qiskit Fall Fest 2026 Phase 2 Optimization Track (Problem Statement PS-O1), network partitioning is modeled as a weighted Maximum Cut (Max-Cut) graph problem.

Let $G = (V, E)$ be an undirected graph with vertex set $V = \{0, 1, 2, 3, 4, 5\}$ ($|V| = 6$) and edge set $E \subset V \times V$ ($|E| = 9$) with positive edge weights $w_{uv} > 0$. The total edge weight is:
$$W = \sum_{(u, v) \in E} w_{uv} = 27$$

The official problem instance defined in `instances.json` consists of:
- Vertices: $V = \{0, 1, 2, 3, 4, 5\}$
- Weighted Edges:
  - $(0, 2): 1$
  - $(0, 3): 4$
  - $(0, 4): 4$
  - $(1, 4): 3$
  - $(1, 5): 3$
  - $(2, 3): 5$
  - $(2, 4): 1$
  - $(3, 4): 4$
  - $(3, 5): 2$

The objective of network partitioning (Max-Cut) is to find a binary partition of the vertices $V$ into two disjoint subsets $S$ and $\bar{S} = V \setminus S$ that maximizes the sum of weights of edges crossing the partition cut:
$$C(S) = \sum_{(u, v) \in E, u \in S, v \notin S} w_{uv}$$

---

## 2. Binary and Spin Variable Formulations

### 2.1 Quadratic Unconstrained Binary Optimization (QUBO)
Let $x_i \in \{0, 1\}$ denote the binary indicator variable for vertex $i$, where:
$$x_i = \begin{cases} 1 & \text{if } i \in S \\ 0 & \text{if } i \in \bar{S} \end{cases}$$

An edge $(u, v) \in E$ is cut if and only if $x_u \neq x_v$. In binary arithmetic:
$$x_u \oplus x_v = x_u + x_v - 2 x_u x_v$$

The total cut weight is:
$$C(x) = \sum_{(u, v) \in E} w_{uv} (x_u + x_v - 2 x_u x_v)$$

Because optimization routines minimize an objective function, the QUBO minimization objective is defined as the negative cut weight:
$$f_{\text{QUBO}}(x) = -C(x) = x^T Q x$$
where $Q \in \mathbb{R}^{6 \times 6}$ is an upper-triangular matrix whose diagonal elements represent linear contributions ($-w_{uv}$ to $x_u$ and $x_v$) and off-diagonal elements represent pairwise quadratic interactions ($+2w_{uv}$ to $x_u x_v$).

### 2.2 Mapping to the Ising Spin Hamiltonian
To translate the binary optimization problem into a quantum Hamiltonian suitable for quantum algorithms, we introduce spin variables $z_i \in \{-1, +1\}$ via the canonical affine transformation:
$$x_i = \frac{1 - z_i}{2}$$

Substituting this into the cut expression for an edge $(u, v)$:
$$x_u + x_v - 2 x_u x_v = \left(\frac{1 - z_u}{2}\right) + \left(\frac{1 - z_v}{2}\right) - 2 \left(\frac{1 - z_u}{2}\right)\left(\frac{1 - z_v}{2}\right) = \frac{1 - z_u z_v}{2}$$

Summing over all edges $(u, v) \in E$:
$$C(z) = \sum_{(u, v) \in E} w_{uv} \frac{1 - z_u z_v}{2} = \frac{1}{2} \sum_{(u, v) \in E} w_{uv} - \frac{1}{2} \sum_{(u, v) \in E} w_{uv} z_u z_v = \frac{W}{2} - \frac{1}{2} \sum_{(u, v) \in E} w_{uv} z_u z_v$$

Promoting the classical spin variables $z_i \in \{-1, +1\}$ to quantum Pauli-$Z$ operators $\hat{Z}_i$, the cost Hamiltonian $\hat{H}_C$ is defined such that:
$$\hat{H}_C = \sum_{(u, v) \in E} \frac{w_{uv}}{2} \hat{Z}_u \hat{Z}_v$$

With the constant shift $\frac{W}{2} = 13.5$, the expected cut value is:
$$\langle C \rangle = \frac{W}{2} - \langle \hat{H}_C \rangle = 13.5 - \langle \hat{H}_C \rangle$$
Minimizing $\langle \hat{H}_C \rangle$ directly maximizes expected cut $\langle C \rangle$.

---

## 3. Quantum Approximate Optimization Algorithm (QAOA)

The Quantum Approximate Optimization Algorithm (Farhi et al., 2014) is a hybrid quantum-classical variational algorithm designed to find approximate solutions to combinatorial optimization problems.

### 3.1 Initial State Preparation
The system starts in a uniform superposition of all computational basis states:
$$|\psi_0\rangle = H^{\otimes n} |0\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}} \sum_{x \in \{0, 1\}^n} |x\rangle$$

### 3.2 Parameterized Circuit Ansatz ($p=1$)
For depth $p = 1$, the variational ansatz alternates between the problem cost unitary $U_C(\gamma)$ and the transverse mixer unitary $U_M(\beta)$:
$$|\psi(\gamma, \beta)\rangle = U_M(\beta) U_C(\gamma) |\psi_0\rangle$$

1. **Problem Cost Unitary $U_C(\gamma)$**:
   $$U_C(\gamma) = e^{-i \gamma \hat{H}_C} = \prod_{(u, v) \in E} \exp\left(-i \frac{\gamma w_{uv}}{2} \hat{Z}_u \hat{Z}_v\right) = \prod_{(u, v) \in E} R_{ZZ}^{(u, v)}(w_{uv} \gamma)$$
   Each two-qubit interaction is implemented as an $R_{ZZ}$ gate parameterized by $\theta_{uv} = w_{uv} \gamma$, decomposed into native basis gates:
   $$\text{CX}(u, v) \to R_Z(v, w_{uv} \gamma) \to \text{CX}(u, v)$$

2. **Mixer Unitary $U_M(\beta)$**:
   $$\hat{H}_M = \sum_{j=0}^{n-1} \hat{X}_j$$
   $$U_M(\beta) = e^{-i \beta \hat{H}_M} = \prod_{j=0}^{n-1} R_X^{(j)}(2\beta)$$

### 3.3 Variational Optimization
The classical optimization loop seeks parameters $(\gamma, \beta)$ that maximize the expected cut value:
$$\max_{\gamma, \beta} \langle C \rangle_{\gamma, \beta} = \langle \psi(\gamma, \beta) | \hat{C} | \psi(\gamma, \beta)\rangle = 13.5 - \langle \psi(\gamma, \beta) | \hat{H}_C | \psi(\gamma, \beta)\rangle$$

In our simulation, statevector analysis computes the exact expectation value:
$$\langle C \rangle = \sum_{x \in \{0, 1\}^n} |\langle x | \psi(\gamma, \beta) \rangle|^2 C(x)$$

The optimization is performed using the Constrained Optimization BY Linear Approximation (COBYLA) algorithm across five mandatory random initial seeds:
$$\text{seeds} \in \{0, 1, 2, 3, 4\}$$
where initial angles are drawn independently and uniformly from $[0, \pi]$.

---

## 4. Classical Ground Truth and Exhaustive Enumeration

Because the instance size is small ($n = 6$), the state space comprises $2^6 = 64$ bitstrings, permitting exact verification via exhaustive brute-force enumeration.

### 4.1 Ground Truth Results
- **Total edge weight**: $W = 27$
- **Total valid configurations**: $2^6 = 64$
- **Global maximum cut**: $C^* = 22$
- **Number of optimal bitstrings**: 2 (exact bitwise complements due to $\mathbb{Z}_2$ spin-flip symmetry):
  1. $x = (1, 1, 0, 1, 0, 0) \implies S = \{0, 1, 3\}, \bar{S} = \{2, 4, 5\}$ (Qiskit bitstring `'001011'`)
  2. $x = (0, 0, 1, 0, 1, 1) \implies S = \{2, 4, 5\}, \bar{S} = \{0, 1, 3\}$ (Qiskit bitstring `'110100'`)
- **Internal edge weights**:
  - In $S=\{0, 1, 3\}$: edge $(0, 3)$ with weight 4.
  - In $\bar{S}=\{2, 4, 5\}$: edge $(2, 4)$ with weight 1.
  - Total internal edge weight = $4 + 1 = 5$.
  - Cut weight = $27 - 5 = 22$.
- **Weighted cut fraction**: $\frac{C^*}{W} = \frac{22}{27} \approx 81.48\%$
- **Edge-count fraction**: 7 cut edges out of 9 total ($7/9 \approx 77.78\%$).
- **Uniform random baseline cut**:
  $$C_{\text{random}} = \frac{W}{2} = 13.5$$
- **Random baseline approximation ratio**:
  $$r_{\text{random}} = \frac{13.5}{22} \approx 0.6136$$
- **Random optimal hit probability**:
  $$P_{\text{opt, random}} = \frac{2}{64} = 0.03125 \quad (3.125\%)$$

---

## 5. Summary of Mathematical Metrics

| Metric | Formula | Exact Value |
| :--- | :--- | :--- |
| **Ground Truth Max-Cut ($C^*$)** | $\max_{x \in \{0, 1\}^6} C(x)$ | **22** |
| **Total Weight ($W$)** | $\sum_{(u, v) \in E} w_{uv}$ | **27** |
| **Random Cut Expectation** | $\frac{W}{2}$ | **13.5** |
| **Random Approx Ratio ($r_{\text{random}}$)** | $\frac{13.5}{C^*}$ | **0.6136** |
| **Random Optimal Probability** | $\frac{2}{2^n}$ | **3.125%** |
| **Best Initialized QAOA Parameters** | $(\gamma^*, \beta^*)$ from Seed 3 | **(-0.1680, 0.3327)** |
| **QAOA Statevector Expectation** | $\langle C \rangle_{\text{statevector}}$ | **17.7128** |
| **QAOA Theoretical Approx Ratio** | $\frac{\langle C \rangle}{C^*}$ | **0.8051** |
