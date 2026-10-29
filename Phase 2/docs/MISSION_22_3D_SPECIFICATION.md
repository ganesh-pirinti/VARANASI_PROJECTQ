# VARANASI: Mission 22 — Quantum Network Architect
## 3D Concept Prototype Architecture, Scene Hierarchy & Spline Handoff Specification

**Project:** VARANASI  
**Event:** Qiskit Fall Fest 2026 — SRM University-AP  
**Track:** Quantum Optimization | **Problem Statement:** PS-O1 (Network Partitioning Using QAOA)  
**Deliverable:** 3D Educational Game Prototype & Engineering Handoff Specification  
**Source Implementation:** [`Phase 2/web/mission22.html`](file:///c:/Projects/VARANASI_PROJECTQ/Phase%202/web/mission22.html) & [`Phase 2/web/mission22.js`](file:///c:/Projects/VARANASI_PROJECTQ/Phase%202/web/mission22.js)  

---

## 1. Executive Summary & Design Aesthetics

"VARANASI: Mission 22 — Quantum Network Architect" serves as the visual and interactive foundation for an educational quantum computing game. It teaches the mathematical principles of weighted Max-Cut partitioning, QAOA circuit synthesis, and zero-SWAP quantum processor co-design.

### Aesthetic Principles
- **Color Palette:**
  - **Deep Navy Background:** `#050a17` / `#0a1326` with distance fog (`FogExp2`, density `0.012`) and subtle scientific coordinate floor grid (`#00e5ff`, `#132342`).
  - **Group S (Partition 1):** Vibrant Cyan (`#00e5ff`, emissive `#00b4d8`, intensity `0.65`).
  - **Group S̄ (Partition 0):** Muted Blue/Gray (`#546e7a`, emissive `#263238`, intensity `0.30`).
  - **Severed (Cut) Edges:** Glowing Orange (`#ff7043`, emissive `#ff5722`, intensity `0.85`).
  - **Uncut (Internal) Edges:** Muted Dark Blue (`#223554`, opacity `0.45`).
  - **Selected Node Highlight:** Warm Gold (`#ffd54f`, emissive `#ffb300`, intensity `0.90`).
- **Tone:** Premium scientific and aerospace engineering instrumentation. Clean typography, restrained glow, and high readability over flashy cyberpunk tropes.
- **Mandatory Scientific Disclaimers:**
  - *"Synthetic benchmark graph inspired by network planning; not a real telecommunications deployment."*
  - *"Simulated processor topology; not real physical quantum hardware."*

---

## 2. 3D Scene Graph & Object Hierarchy

The 3D environment is structured into three distinct modular zones: the central **Network Arena**, the **Quantum Workbench**, and the **Hardware Station**.

```
Scene Root (0x050a17)
├── DirectionalLight_Key (0xffffff, pos: [20, 35, 20])
├── DirectionalLight_Rim_Cyan (0x00e5ff, pos: [-30, 15, -20])
├── DirectionalLight_Rim_Orange (0xff7043, pos: [30, -15, 25])
├── AmbientLight (0x0e1c38)
├── GridHelper (y = -8)
│
├── Group: network_arena (pos: [0, 0, 0])
│   ├── Mesh: node_0 (Sphere, r=1.2, pos: [-7.0, 3.8, -2.0])
│   ├── Mesh: node_1 (Sphere, r=1.2, pos: [7.0, 3.8, 2.0])
│   ├── Mesh: node_2 (Sphere, r=1.2, pos: [-5.0, -3.8, 3.8])
│   ├── Mesh: node_3 (Sphere, r=1.2, pos: [-0.5, 5.2, 0.5])
│   ├── Mesh: node_4 (Sphere, r=1.2, pos: [3.2, -4.2, -2.5])
│   ├── Mesh: node_5 (Sphere, r=1.2, pos: [8.0, -2.6, -3.2])
│   │
│   ├── Mesh: edge_0_2 (Cylinder, w=1, connects node_0 -> node_2)
│   ├── Mesh: edge_0_3 (Cylinder, w=4, connects node_0 -> node_3) [INTERNAL UNCUT]
│   ├── Mesh: edge_0_4 (Cylinder, w=4, connects node_0 -> node_4)
│   ├── Mesh: edge_1_4 (Cylinder, w=3, connects node_1 -> node_4)
│   ├── Mesh: edge_1_5 (Cylinder, w=3, connects node_1 -> node_5)
│   ├── Mesh: edge_2_3 (Cylinder, w=5, connects node_2 -> node_3)
│   ├── Mesh: edge_2_4 (Cylinder, w=1, connects node_2 -> node_4) [INTERNAL UNCUT]
│   ├── Mesh: edge_3_4 (Cylinder, w=4, connects node_3 -> node_4)
│   ├── Mesh: edge_3_5 (Cylinder, w=2, connects node_3 -> node_5)
│   │
│   └── Sprites: weight_badge_0_2 ... weight_badge_3_5 (Billboarded)
│
├── Group: quantum_workbench (pos: [-36, 0, -4])
│   ├── Mesh: wire_q0 ... wire_q5 (6 Horizontal Logical Wires, y: 5 to -5)
│   ├── Group: layer_hadamard (6 Boxes: gate_H_0 ... gate_H_5, x: -10)
│   ├── Group: layer_cost_unitary (UC(γ) Enclosure & CX-RZ-CX blocks, x: -2)
│   ├── Group: layer_mixer (6 Boxes: gate_RX_0 ... gate_RX_5, x: 6)
│   └── Group: layer_measurement (6 Boxes: gate_M_0 ... gate_M_5, x: 11)
│
└── Group: hardware_station (pos: [36, 0, -4])
    ├── Mesh: qubit_Q0 ... qubit_Q5 (6 Core Qubits embedding benchmark graph)
    ├── Mesh: qubit_Q6 ... qubit_Q8 (3 Ancillary Routing Qubits)
    └── Couplers: 9 Core Couplers + 4 Routing Ring Couplers ([5,6], [6,7], [7,8], [8,1])
```

---

## 3. Benchmark Graph Topology & Optimal Partition

### Exact Edge & Weight Registry
$$\sum_{(u,v) \in E} w_{uv} = 1 + 4 + 4 + 3 + 3 + 5 + 1 + 4 + 2 = 27$$

| Edge Object Name | Node $u$ | Node $v$ | Weight ($w_{uv}$) | Optimal State Status ($S=\{0,1,3\}$) |
| :--- | :--- | :--- | :--- | :--- |
| `edge_0_2` | 0 (Group S) | 2 (Group S̄) | 1 | **SEVERED (CUT)** |
| `edge_0_3` | 0 (Group S) | 3 (Group S) | 4 | **INTERNAL (UNCUT)** |
| `edge_0_4` | 0 (Group S) | 4 (Group S̄) | 4 | **SEVERED (CUT)** |
| `edge_1_4` | 1 (Group S) | 4 (Group S̄) | 3 | **SEVERED (CUT)** |
| `edge_1_5` | 1 (Group S) | 5 (Group S̄) | 3 | **SEVERED (CUT)** |
| `edge_2_3` | 2 (Group S̄) | 3 (Group S) | 5 | **SEVERED (CUT)** |
| `edge_2_4` | 2 (Group S̄) | 4 (Group S̄) | 1 | **INTERNAL (UNCUT)** |
| `edge_3_4` | 3 (Group S) | 4 (Group S̄) | 4 | **SEVERED (CUT)** |
| `edge_3_5` | 3 (Group S) | 5 (Group S̄) | 2 | **SEVERED (CUT)** |

**Optimal Cut Capacity:** $1 + 4 + 3 + 3 + 5 + 4 + 2 = 22 / 27$ ($81.48\%$).  
**Internal Capacity Surrendered:** $(0,3)[w=4] + (2,4)[w=1] = 5 / 27$ ($18.52\%$).

---

## 4. Spline 3D Variable & Event Specification

When authoring or importing this scene into **Spline 3D**, use the following official schema:

### Spline Variables
| Variable Name | Type | Initial Value | Description |
| :--- | :--- | :--- | :--- |
| `cut_weight` | Number | `22` | Current total severed edge capacity (0 to 27) |
| `target_cut` | Number | `22` | Constant benchmark maximum cut |
| `approximation_ratio` | Number | `0.8148` | `cut_weight / target_cut` |
| `attempts_count` | Number | `0` | Number of player node-toggle moves |
| `is_optimal` | Boolean | `true` | True when `cut_weight == 22` |
| `partition_bitstring`| String | `"110100"` | Binary vector $(x_0, x_1, x_2, x_3, x_4, x_5)$ |
| `selected_node` | String | `""` | Name of hovered/clicked node |
| `active_circuit_step`| Number | `0` | 0=Init, 1=Cost, 2=Mixer, 3=Measure |
| `camera_view` | String | `"arena"` | Camera preset: `"arena"`, `"workbench"`, `"hardware"`, `"wide"` |

### Spline State Machine & Event Triggers
1. **Node Click Trigger (`Mouse Down` on `node_i`):**
   - Action: Toggle variable `node_i_state` (`0` $\leftrightarrow$ `1`).
   - Transition: Target mesh triggers state transition:
     - `State: Group_S`: Material set to Cyan `#00e5ff`, halo ring scales to 1.15.
     - `State: Group_SBar`: Material set to Blue/Gray `#546e7a`, halo ring scales to 1.0.
   - Action: Increment `attempts_count`.
   - Action: Invoke JS callback `window.onSplineNodeToggled(nodeId)`.
2. **Edge Cut Trigger (`State Change` on `edge_u_v`):**
   - Condition: `node_u_state != node_v_state`.
   - `State: Severed`: Material shifts to Glowing Orange `#ff7043`, tube radius scales 1.4x, emissive intensity pulse activated.
   - `State: Internal`: Material shifts to Muted Navy `#223554`, tube radius normal, opacity 0.45.
3. **Victory Celebration Trigger (`is_optimal == true`):**
   - Condition: `cut_weight == 22`.
   - Action: Toast banner `victory-banner` translates $Y$ from $-20\text{px} \rightarrow 0\text{px}$, opacity $0 \rightarrow 1$.
   - Action: Play victory harmonic chime via Web Audio synthesizer.

---

## 5. JavaScript Bridge Integration (@splinetool/runtime)

To bind Spline-exported assets with real-time experimental data from the VARANASI Python pipeline (`results.csv` / `studio_data.json`):

```javascript
import { Application } from '@splinetool/runtime';

const canvas = document.getElementById('canvas-container');
const spline = new Application(canvas);

spline.load('https://prod.spline.design/varanasi-mission22/scene.splinecode')
  .then(() => {
    console.log('Spline scene loaded successfully');

    // Query 3D Nodes
    const node0 = spline.findObjectByName('node_0');
    const edge03 = spline.findObjectByName('edge_0_3');

    // Listen to Spline Events
    spline.addEventListener('mouseDown', (e) => {
      if (e.target.name.startsWith('node_')) {
        const nodeId = parseInt(e.target.name.split('_')[1], 10);
        handleNodeClick(nodeId);
      }
    });

    // Programmatically set Spline variables
    function updateSplineHUD(cutWeight, isOptimal) {
      spline.setVariable('cut_weight', cutWeight);
      spline.setVariable('is_optimal', isOptimal);
    }
  });
```

---

## 6. Camera Rig Specifications

| Preset Name | Focus Target Position | Camera Coordinate $(X, Y, Z)$ | Field of View (FOV) |
| :--- | :--- | :--- | :--- |
| **Network Arena (Main)** | `(0, 0, 0)` | `(0, 8, 26)` | $45^\circ$ |
| **Quantum Workbench** | `(-36, 0, -2)` | `(-36, 4, 20)` | $45^\circ$ |
| **Hardware Station** | `(36, 0, -2)` | `(36, 4, 20)` | $45^\circ$ |
| **Wide Overview (All 3)** | `(0, 0, -2)` | `(0, 18, 56)` | $45^\circ$ |

---

## 7. Deliverable Verification Check

- [x] All 6 network nodes named `node_0` through `node_5`
- [x] All 9 weighted edges named `edge_0_2` through `edge_3_5`
- [x] Exact weights verified: $(0,2,1)$, $(0,3,4)$, $(0,4,4)$, $(1,4,3)$, $(1,5,3)$, $(2,3,5)$, $(2,4,1)$, $(3,4,4)$, $(3,5,2)$
- [x] Group coloring: Cyan for Group S, Muted Blue/Gray for Group S̄, Glowing Orange for cut edges
- [x] Optimal partition cut weight verified: 22 / 27
- [x] Internal uncut edges: `(0,3)` with weight 4 and `(2,4)` with weight 1
- [x] Quantum workbench with 6 horizontal wires and H, UC, RX, M gates
- [x] Hardware station with 9 physical qubits of Processor D (zero-SWAP embedding)
- [x] Game HUD with Mission, Cut Weight, Best Known, Attempts, Hint, Explain Why
- [x] Neutral state and Solution-reveal state supported
- [x] Navigable, interactive WebGL 3D implementation tested and verified
