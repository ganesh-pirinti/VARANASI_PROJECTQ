/**
 * VARANASI: Mission 22 — Quantum Network Architect
 * Interactive 3D Educational Concept Prototype
 * Built with Three.js (WebGL)
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

// ============================================================================
// 1. DATA STRUCTURES & OFFICIAL PS-O1 BENCHMARK SPECIFICATION
// ============================================================================

const BENCHMARK_GRAPH = {
  num_nodes: 6,
  nodes: [
    { id: 0, name: "node_0", pos: [-7.0, 3.8, -2.0] },
    { id: 1, name: "node_1", pos: [7.0, 3.8, 2.0] },
    { id: 2, name: "node_2", pos: [-5.0, -3.8, 3.8] },
    { id: 3, name: "node_3", pos: [-0.5, 5.2, 0.5] },
    { id: 4, name: "node_4", pos: [3.2, -4.2, -2.5] },
    { id: 5, name: "node_5", pos: [8.0, -2.6, -3.2] }
  ],
  edges: [
    { u: 0, v: 2, weight: 1, name: "edge_0_2" },
    { u: 0, v: 3, weight: 4, name: "edge_0_3" },
    { u: 0, v: 4, weight: 4, name: "edge_0_4" },
    { u: 1, v: 4, weight: 3, name: "edge_1_4" },
    { u: 1, v: 5, weight: 3, name: "edge_1_5" },
    { u: 2, v: 3, weight: 5, name: "edge_2_3" },
    { u: 2, v: 4, weight: 1, name: "edge_2_4" },
    { u: 3, v: 4, weight: 4, name: "edge_3_4" },
    { u: 3, v: 5, weight: 2, name: "edge_3_5" }
  ],
  total_weight: 27,
  target_cut: 22,
  optimal_group_s: [0, 1, 3], // Group S (Cyan)
  optimal_group_sbar: [2, 4, 5] // Group S-bar (Muted Blue/Gray)
};

// Processor D (9 Qubits) Topology Specification
const PROCESSOR_D = {
  num_qubits: 9,
  qubits: [
    { id: 0, label: "Q0", pos: [-4.0, 3.0, 0] },
    { id: 1, label: "Q1", pos: [4.0, 3.0, 0] },
    { id: 2, label: "Q2", pos: [-3.0, -2.5, 2] },
    { id: 3, label: "Q3", pos: [-0.5, 3.5, 0] },
    { id: 4, label: "Q4", pos: [2.0, -2.5, -1.5] },
    { id: 5, label: "Q5", pos: [4.5, -2.0, -2] },
    // Ancillary routing ring
    { id: 6, label: "Q6", pos: [5.5, -0.5, -4] },
    { id: 7, label: "Q7", pos: [3.5, 2.0, -5] },
    { id: 8, label: "Q8", pos: [5.5, 4.0, -3] }
  ],
  edges: [
    // 9 core graph embedding edges
    [0, 2], [0, 3], [0, 4], [1, 4], [1, 5],
    [2, 3], [2, 4], [3, 4], [3, 5],
    // 4 ancillary routing ring edges
    [5, 6], [6, 7], [7, 8], [8, 1]
  ]
};

// ============================================================================
// 2. AUDIO SYNTHESIZER (WEB AUDIO API)
// ============================================================================

class ScientificAudio {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx && (window.AudioContext || window.webkitAudioContext)) {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
  }

  playTone(freq, type = 'sine', duration = 0.12, gain = 0.15) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }

    const osc = this.ctx.createOscillator();
    const g = this.ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

    g.gain.setValueAtTime(gain, this.ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);

    osc.connect(g);
    g.connect(this.ctx.destination);

    osc.start();
    osc.stop(this.ctx.currentTime + duration);
  }

  playNodeToggle(isS) {
    this.playTone(isS ? 587.33 : 440.0, 'sine', 0.1, 0.12);
  }

  playVictory() {
    if (!this.enabled) return;
    const notes = [440, 554.37, 659.25, 880];
    notes.forEach((freq, idx) => {
      setTimeout(() => {
        this.playTone(freq, 'triangle', 0.35, 0.2);
      }, idx * 90);
    });
  }
}

const audio = new ScientificAudio();

// ============================================================================
// 3. GAME STATE
// ============================================================================

const state = {
  // 0 = Group S-bar (default/blue-gray), 1 = Group S (cyan)
  partition: [0, 0, 0, 0, 0, 0],
  currentCutWeight: 0,
  attempts: 0,
  bestCut: 0,
  selectedNode: null,
  activeStep: 0, // 0=Init, 1=Cost, 2=Mixer, 3=Measure
  qaoaGamma: -0.168,
  qaoaBeta: 0.333,
  cameraPreset: 'arena',
  targetCameraPos: new THREE.Vector3(0, 8, 26),
  targetCameraLook: new THREE.Vector3(0, 0, 0),
  isCameraTransitioning: false
};

// ============================================================================
// 4. THREE.JS SCENE, LIGHTS & RENDERER SETUP
// ============================================================================

const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x050a17);
scene.fog = new THREE.FogExp2(0x050a17, 0.012);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 500);
camera.position.set(0, 8, 26);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.maxDistance = 140;
controls.minDistance = 6;
controls.target.set(0, 0, 0);

// Lighting
const ambientLight = new THREE.AmbientLight(0x0e1c38, 1.4);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 1.8);
dirLight.position.set(20, 35, 20);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;
dirLight.shadow.camera.near = 0.5;
dirLight.shadow.camera.far = 100;
scene.add(dirLight);

// Scientific Rim Lighting
const cyanRimLight = new THREE.DirectionalLight(0x00e5ff, 2.2);
cyanRimLight.position.set(-30, 15, -20);
scene.add(cyanRimLight);

const orangeRimLight = new THREE.DirectionalLight(0xff7043, 1.8);
orangeRimLight.position.set(30, -15, 25);
scene.add(orangeRimLight);

// Floor Grid Plane
const gridHelper = new THREE.GridHelper(120, 60, 0x00e5ff, 0x132342);
gridHelper.position.y = -8;
scene.add(gridHelper);

// ============================================================================
// 5. MATERIALS & OBJECT BUILDERS
// ============================================================================

const materials = {
  // Group S (Cyan)
  nodeGroupS: new THREE.MeshPhysicalMaterial({
    color: 0x00e5ff,
    emissive: 0x00b4d8,
    emissiveIntensity: 0.65,
    roughness: 0.2,
    metalness: 0.4,
    clearcoat: 0.8
  }),
  // Group S-bar (Muted Blue/Gray)
  nodeGroupSBar: new THREE.MeshPhysicalMaterial({
    color: 0x546e7a,
    emissive: 0x263238,
    emissiveIntensity: 0.3,
    roughness: 0.35,
    metalness: 0.6,
    clearcoat: 0.4
  }),
  // Selected Node Highlight
  nodeSelected: new THREE.MeshPhysicalMaterial({
    color: 0xffd54f,
    emissive: 0xffb300,
    emissiveIntensity: 0.9,
    roughness: 0.1,
    metalness: 0.2
  }),
  // Cut Edge (Orange Glowing)
  edgeCut: new THREE.MeshStandardMaterial({
    color: 0xff7043,
    emissive: 0xff5722,
    emissiveIntensity: 0.85,
    roughness: 0.3,
    metalness: 0.1
  }),
  // Uncut Edge (Muted Dark Blue/Gray)
  edgeUncut: new THREE.MeshStandardMaterial({
    color: 0x223554,
    emissive: 0x111c30,
    emissiveIntensity: 0.15,
    roughness: 0.6,
    metalness: 0.2,
    transparent: true,
    opacity: 0.45
  }),
  // Quantum Wire
  quantumWire: new THREE.MeshStandardMaterial({
    color: 0x00e5ff,
    emissive: 0x008ba3,
    emissiveIntensity: 0.3,
    roughness: 0.4,
    metalness: 0.5
  }),
  // Gate Material (Glassmorphic)
  gateH: new THREE.MeshPhysicalMaterial({
    color: 0x29b6f6,
    emissive: 0x0288d1,
    emissiveIntensity: 0.5,
    roughness: 0.1,
    metalness: 0.3,
    transparent: true,
    opacity: 0.85
  }),
  gateCost: new THREE.MeshPhysicalMaterial({
    color: 0xff7043,
    emissive: 0xf4511e,
    emissiveIntensity: 0.6,
    roughness: 0.1,
    metalness: 0.3,
    transparent: true,
    opacity: 0.85
  }),
  gateMixer: new THREE.MeshPhysicalMaterial({
    color: 0xab47bc,
    emissive: 0x8e24aa,
    emissiveIntensity: 0.5,
    roughness: 0.1,
    metalness: 0.3,
    transparent: true,
    opacity: 0.85
  }),
  gateMeasure: new THREE.MeshPhysicalMaterial({
    color: 0x26a69a,
    emissive: 0x00897b,
    emissiveIntensity: 0.5,
    roughness: 0.1,
    metalness: 0.3,
    transparent: true,
    opacity: 0.85
  }),
  // Hardware Physical Qubit
  hardwareQubit: new THREE.MeshPhysicalMaterial({
    color: 0x90caf9,
    emissive: 0x1565c0,
    emissiveIntensity: 0.4,
    roughness: 0.25,
    metalness: 0.7
  }),
  hardwareEdge: new THREE.MeshStandardMaterial({
    color: 0x37474f,
    emissive: 0x263238,
    emissiveIntensity: 0.2,
    roughness: 0.5
  })
};

// Canvas Sprite Generator for Crisp 3D Text Labels
function createTextSprite(text, color = '#00e5ff', bgColor = 'rgba(5, 10, 23, 0.8)', fontSize = 28) {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 96;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = bgColor;
  ctx.roundRect(10, 10, 236, 76, 12);
  ctx.fill();
  ctx.strokeStyle = color;
  ctx.lineWidth = 3;
  ctx.stroke();

  ctx.font = `bold ${fontSize}px "JetBrains Mono", monospace`;
  ctx.fillStyle = color;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 128, 48);

  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(3.2, 1.2, 1.0);
  return sprite;
}

// ============================================================================
// 6. 3D SCENE OBJECTS CREATION
// ============================================================================

const networkArenaGroup = new THREE.Group();
networkArenaGroup.name = "network_arena";
scene.add(networkArenaGroup);

const quantumWorkbenchGroup = new THREE.Group();
quantumWorkbenchGroup.name = "quantum_workbench";
quantumWorkbenchGroup.position.set(-36, 0, -4);
scene.add(quantumWorkbenchGroup);

const hardwareStationGroup = new THREE.Group();
hardwareStationGroup.name = "hardware_station";
hardwareStationGroup.position.set(36, 0, -4);
scene.add(hardwareStationGroup);

// --- 6.1 Network Arena Nodes & Edges ---
const nodeMeshes = [];
const edgeObjects = [];
const nodeGeom = new THREE.SphereGeometry(1.2, 32, 32);

BENCHMARK_GRAPH.nodes.forEach(node => {
  const mesh = new THREE.Mesh(nodeGeom, materials.nodeGroupSBar);
  mesh.name = node.name; // Exact requirement: node_0, node_1, etc.
  mesh.userData = { id: node.id, name: node.name, type: 'network_node' };
  mesh.position.set(...node.pos);
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  // Outer glowing ring
  const ringGeom = new THREE.TorusGeometry(1.5, 0.06, 16, 64);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x00e5ff, transparent: true, opacity: 0.6 });
  const ring = new THREE.Mesh(ringGeom, ringMat);
  ring.rotation.x = Math.PI / 2;
  mesh.add(ring);
  mesh.userData.ring = ring;

  // Billboard 3D Label
  const labelSprite = createTextSprite(`N${node.id}`, '#ffffff', 'rgba(10, 19, 38, 0.85)', 32);
  labelSprite.position.set(0, 2.1, 0);
  mesh.add(labelSprite);

  networkArenaGroup.add(mesh);
  nodeMeshes.push(mesh);
});

// Build 9 Weighted Edges
BENCHMARK_GRAPH.edges.forEach(edge => {
  const nodeU = BENCHMARK_GRAPH.nodes[edge.u];
  const nodeV = BENCHMARK_GRAPH.nodes[edge.v];
  const p1 = new THREE.Vector3(...nodeU.pos);
  const p2 = new THREE.Vector3(...nodeV.pos);

  const dist = p1.distanceTo(p2);
  const dir = new THREE.Vector3().subVectors(p2, p1).normalize();
  const mid = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);

  const edgeGeom = new THREE.CylinderGeometry(0.18, 0.18, dist, 16);
  const edgeMesh = new THREE.Mesh(edgeGeom, materials.edgeUncut);
  edgeMesh.name = edge.name; // Exact requirement: edge_0_2, edge_0_3, etc.
  edgeMesh.userData = { edge, type: 'network_edge' };

  // Orient cylinder along the edge
  edgeMesh.position.copy(mid);
  edgeMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
  edgeMesh.castShadow = true;

  // Weight Badge
  const weightSprite = createTextSprite(`w=${edge.weight}`, '#ffab91', 'rgba(15, 23, 42, 0.9)', 26);
  weightSprite.scale.set(2.4, 0.9, 1.0);
  // Slightly offset badge so it doesn't intersect the tube
  const normal = new THREE.Vector3(0, 1, 0).cross(dir).normalize();
  if (normal.lengthSq() < 0.01) normal.set(1, 0, 0);
  weightSprite.position.copy(mid).add(normal.multiplyScalar(0.9)).add(new THREE.Vector3(0, 0.5, 0));

  networkArenaGroup.add(edgeMesh);
  networkArenaGroup.add(weightSprite);

  edgeObjects.push({
    mesh: edgeMesh,
    weightSprite,
    edge
  });
});

// --- 6.2 Quantum Circuit Workbench ---
// 6 Wires
const wireMeshes = [];
const wireGeom = new THREE.CylinderGeometry(0.06, 0.06, 26, 16);
const wireQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), Math.PI / 2);

for (let i = 0; i < 6; i++) {
  const yPos = 5.0 - i * 2.0;
  const wire = new THREE.Mesh(wireGeom, materials.quantumWire);
  wire.position.set(0, yPos, 0);
  wire.quaternion.copy(wireQuat);
  quantumWorkbenchGroup.add(wire);
  wireMeshes.push(wire);

  // Wire label sprite
  const wireLabel = createTextSprite(`q${i}`, '#00e5ff', 'rgba(5, 10, 23, 0.8)', 28);
  wireLabel.position.set(-14.5, yPos, 0);
  wireLabel.scale.set(2.0, 0.9, 1.0);
  quantumWorkbenchGroup.add(wireLabel);

  // Hadamard Gate
  const hGeom = new THREE.BoxGeometry(1.2, 1.2, 0.6);
  const hGate = new THREE.Mesh(hGeom, materials.gateH);
  hGate.position.set(-10, yPos, 0);
  quantumWorkbenchGroup.add(hGate);
  const hLabel = createTextSprite('H', '#ffffff', 'rgba(2, 136, 209, 0.9)', 36);
  hLabel.scale.set(1.0, 1.0, 1.0);
  hLabel.position.set(-10, yPos, 0.4);
  quantumWorkbenchGroup.add(hLabel);

  // Mixer Gate RX(2beta)
  const rxGeom = new THREE.BoxGeometry(1.4, 1.2, 0.6);
  const rxGate = new THREE.Mesh(rxGeom, materials.gateMixer);
  rxGate.position.set(6, yPos, 0);
  quantumWorkbenchGroup.add(rxGate);
  const rxLabel = createTextSprite('RX', '#ffffff', 'rgba(142, 36, 170, 0.9)', 30);
  rxLabel.scale.set(1.2, 1.0, 1.0);
  rxLabel.position.set(6, yPos, 0.4);
  quantumWorkbenchGroup.add(rxLabel);

  // Measurement Gate
  const mGeom = new THREE.BoxGeometry(1.2, 1.2, 0.6);
  const mGate = new THREE.Mesh(mGeom, materials.gateMeasure);
  mGate.position.set(11, yPos, 0);
  quantumWorkbenchGroup.add(mGate);
  const mLabel = createTextSprite('M', '#ffffff', 'rgba(0, 137, 123, 0.9)', 36);
  mLabel.scale.set(1.0, 1.0, 1.0);
  mLabel.position.set(11, yPos, 0.4);
  quantumWorkbenchGroup.add(mLabel);
}

// Cost Unitary Central Block Representation UC(gamma)
const ucBoxGeom = new THREE.BoxGeometry(9.0, 12.0, 0.8);
const ucBoxMat = new THREE.MeshPhysicalMaterial({
  color: 0xff7043,
  emissive: 0xd84315,
  emissiveIntensity: 0.35,
  roughness: 0.2,
  metalness: 0.3,
  transparent: true,
  opacity: 0.65
});
const ucBox = new THREE.Mesh(ucBoxGeom, ucBoxMat);
ucBox.position.set(-2.0, 0, 0);
quantumWorkbenchGroup.add(ucBox);

const ucLabel = createTextSprite('UC(γ) : 9 Edges', '#ffab91', 'rgba(191, 54, 12, 0.95)', 24);
ucLabel.scale.set(5.5, 1.2, 1.0);
ucLabel.position.set(-2.0, 6.8, 0.6);
quantumWorkbenchGroup.add(ucLabel);

// Label banner above workbench
const wbHeader = createTextSprite('QUANTUM WORKBENCH: QAOA p=1', '#00e5ff', 'rgba(10, 19, 38, 0.9)', 24);
wbHeader.scale.set(10.0, 1.4, 1.0);
wbHeader.position.set(0, 8.5, 0);
quantumWorkbenchGroup.add(wbHeader);

// --- 6.3 Hardware Station (Processor D Simulated Coupling) ---
const hwQubitMeshes = [];
const hwGeom = new THREE.SphereGeometry(0.9, 24, 24);

PROCESSOR_D.qubits.forEach(q => {
  const mesh = new THREE.Mesh(hwGeom, materials.hardwareQubit);
  mesh.name = `qubit_${q.label}`;
  mesh.position.set(...q.pos);
  mesh.castShadow = true;

  const lbl = createTextSprite(q.label, '#ffffff', 'rgba(21, 101, 192, 0.85)', 30);
  lbl.position.set(0, 1.5, 0);
  lbl.scale.set(1.8, 0.8, 1.0);
  mesh.add(lbl);

  hardwareStationGroup.add(mesh);
  hwQubitMeshes.push(mesh);
});

// Couplers
PROCESSOR_D.edges.forEach(([u, v]) => {
  const q1 = PROCESSOR_D.qubits[u];
  const q2 = PROCESSOR_D.qubits[v];
  const p1 = new THREE.Vector3(...q1.pos);
  const p2 = new THREE.Vector3(...q2.pos);

  const dist = p1.distanceTo(p2);
  const dir = new THREE.Vector3().subVectors(p2, p1).normalize();
  const mid = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);

  const coupGeom = new THREE.CylinderGeometry(0.08, 0.08, dist, 12);
  const coupMesh = new THREE.Mesh(coupGeom, materials.hardwareEdge);
  coupMesh.position.copy(mid);
  coupMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);

  hardwareStationGroup.add(coupMesh);
});

// Hardware Station Header & Disclaimer
const hwHeader = createTextSprite('PROCESSOR D: 9-QUBIT TOPOLOGY', '#90caf9', 'rgba(10, 19, 38, 0.9)', 22);
hwHeader.scale.set(10.5, 1.4, 1.0);
hwHeader.position.set(1.0, 6.5, 0);
hardwareStationGroup.add(hwHeader);

const hwSub = createTextSprite('Simulated topology; not real quantum hardware', '#90a4ae', 'rgba(0, 0, 0, 0.7)', 18);
hwSub.scale.set(9.0, 1.0, 1.0);
hwSub.position.set(1.0, 5.0, 0);
hardwareStationGroup.add(hwSub);

// ============================================================================
// 7. PARTITION LOGIC & LIVE CUT RECALCULATION
// ============================================================================

function recalculateCut() {
  let cutWeight = 0;
  const cutEdgeNames = [];

  edgeObjects.forEach(({ mesh, weightSprite, edge }) => {
    const isCut = state.partition[edge.u] !== state.partition[edge.v];
    if (isCut) {
      cutWeight += edge.weight;
      cutEdgeNames.push(edge.name);
      mesh.material = materials.edgeCut;
      mesh.scale.set(1.4, 1.0, 1.4); // Thicker highlighted tube
      weightSprite.material.color.setHex(0xffffff);
    } else {
      mesh.material = materials.edgeUncut;
      mesh.scale.set(1.0, 1.0, 1.0);
      weightSprite.material.color.setHex(0x90a4ae);
    }
  });

  state.currentCutWeight = cutWeight;
  if (cutWeight > state.bestCut) {
    state.bestCut = cutWeight;
  }

  // Update Node Visuals
  nodeMeshes.forEach(mesh => {
    const id = mesh.userData.id;
    const isS = state.partition[id] === 1;
    mesh.material = isS ? materials.nodeGroupS : materials.nodeGroupSBar;
    if (mesh.userData.ring) {
      mesh.userData.ring.material.color.setHex(isS ? 0x00e5ff : 0x78909c);
      mesh.userData.ring.scale.set(isS ? 1.15 : 1.0, isS ? 1.15 : 1.0, 1.0);
    }
  });

  // Update UI Elements
  updateHUD();

  // Check Victory
  if (cutWeight === BENCHMARK_GRAPH.target_cut) {
    showVictoryBanner();
    audio.playVictory();
  } else {
    hideVictoryBanner();
  }
}

function setPartition(newPartition, recordAttempt = true) {
  state.partition = [...newPartition];
  if (recordAttempt) {
    state.attempts++;
  }
  recalculateCut();
}

function toggleNode(nodeId) {
  state.partition[nodeId] = 1 - state.partition[nodeId];
  state.attempts++;
  audio.playNodeToggle(state.partition[nodeId] === 1);
  recalculateCut();
}

// ============================================================================
// 8. HUD & UI BINDINGS
// ============================================================================

const elCutWeight = document.getElementById('stat-cut-weight');
const elAttempts = document.getElementById('stat-attempts');
const elBestCut = document.getElementById('stat-best-cut');
const elRatio = document.getElementById('stat-ratio');
const elVictoryBanner = document.getElementById('victory-banner');
const elEdgeList = document.getElementById('edge-status-list');
const elNodeChips = document.querySelectorAll('.node-chip');

function updateHUD() {
  if (elCutWeight) {
    elCutWeight.textContent = `${state.currentCutWeight} / ${BENCHMARK_GRAPH.total_weight}`;
    if (state.currentCutWeight === 22) {
      elCutWeight.className = 'stat-value highlight-orange';
    } else {
      elCutWeight.className = 'stat-value highlight-cyan';
    }
  }

  if (elAttempts) elAttempts.textContent = state.attempts;
  if (elBestCut) elBestCut.textContent = `${state.bestCut} / 22`;
  if (elRatio) {
    const ratio = (state.currentCutWeight / BENCHMARK_GRAPH.target_cut).toFixed(4);
    elRatio.textContent = ratio;
  }

  // Update Node Chips
  elNodeChips.forEach(chip => {
    const id = parseInt(chip.dataset.nodeId, 10);
    const isS = state.partition[id] === 1;
    if (isS) {
      chip.className = 'node-chip group-s';
      chip.querySelector('.node-chip-group').textContent = 'Group S';
    } else {
      chip.className = 'node-chip group-sbar';
      chip.querySelector('.node-chip-group').textContent = 'Group S̄';
    }
  });

  // Update Edge Status List
  if (elEdgeList) {
    elEdgeList.innerHTML = '';
    BENCHMARK_GRAPH.edges.forEach(edge => {
      const isCut = state.partition[edge.u] !== state.partition[edge.v];
      const item = document.createElement('div');
      item.className = `edge-item ${isCut ? 'is-cut' : ''}`;
      item.innerHTML = `
        <span>(${edge.u}, ${edge.v}) [w=${edge.weight}]</span>
        <span class="${isCut ? 'edge-badge-cut' : 'edge-badge-uncut'}">${isCut ? 'SEVERED (CUT)' : 'INTERNAL'}</span>
      `;
      elEdgeList.appendChild(item);
    });
  }
}

function showVictoryBanner() {
  if (elVictoryBanner) elVictoryBanner.classList.add('visible');
}

function hideVictoryBanner() {
  if (elVictoryBanner) elVictoryBanner.classList.remove('visible');
}

// Bind Node Chip Clicks
elNodeChips.forEach(chip => {
  chip.addEventListener('click', () => {
    const id = parseInt(chip.dataset.nodeId, 10);
    toggleNode(id);
  });
});

// Bind Quick Action Buttons
const btnReset = document.getElementById('btn-reset-neutral');
if (btnReset) {
  btnReset.addEventListener('click', () => {
    setPartition([0, 0, 0, 0, 0, 0]);
  });
}

const btnSnapOpt = document.getElementById('btn-snap-optimal');
if (btnSnapOpt) {
  btnSnapOpt.addEventListener('click', () => {
    // S = {0, 1, 3} -> partition = [1, 1, 0, 1, 0, 0]
    setPartition([1, 1, 0, 1, 0, 0]);
  });
}

const btnSnapComp = document.getElementById('btn-snap-complement');
if (btnSnapComp) {
  btnSnapComp.addEventListener('click', () => {
    // S = {2, 4, 5} -> partition = [0, 0, 1, 0, 1, 1]
    setPartition([0, 0, 1, 0, 1, 1]);
  });
}

const btnRandom = document.getElementById('btn-random-partition');
if (btnRandom) {
  btnRandom.addEventListener('click', () => {
    const rand = Array.from({ length: 6 }, () => Math.random() > 0.5 ? 1 : 0);
    setPartition(rand);
  });
}

// Audio Toggle Button
const btnAudio = document.getElementById('btn-toggle-audio');
if (btnAudio) {
  btnAudio.addEventListener('click', () => {
    audio.enabled = !audio.enabled;
    btnAudio.textContent = audio.enabled ? '🔊' : '🔇';
  });
}

// Circuit Stepper Buttons
const stepChips = document.querySelectorAll('.step-chip');
stepChips.forEach(chip => {
  chip.addEventListener('click', () => {
    stepChips.forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    state.activeStep = parseInt(chip.dataset.step, 10);
  });
});

// QAOA Sliders
const sliderGamma = document.getElementById('slider-gamma');
const valGamma = document.getElementById('val-gamma');
if (sliderGamma && valGamma) {
  sliderGamma.addEventListener('input', (e) => {
    state.qaoaGamma = parseFloat(e.target.value);
    valGamma.textContent = state.qaoaGamma.toFixed(3);
  });
}

const sliderBeta = document.getElementById('slider-beta');
const valBeta = document.getElementById('val-beta');
if (sliderBeta && valBeta) {
  sliderBeta.addEventListener('input', (e) => {
    state.qaoaBeta = parseFloat(e.target.value);
    valBeta.textContent = state.qaoaBeta.toFixed(3);
  });
}

const btnApplyQAOA = document.getElementById('btn-apply-qaoa-opt');
if (btnApplyQAOA) {
  btnApplyQAOA.addEventListener('click', () => {
    if (sliderGamma) sliderGamma.value = -0.168;
    if (sliderBeta) sliderBeta.value = 0.333;
    if (valGamma) valGamma.textContent = "-0.168";
    if (valBeta) valBeta.textContent = "0.333";
    state.qaoaGamma = -0.168;
    state.qaoaBeta = 0.333;
    // Set to optimal partition
    setPartition([1, 1, 0, 1, 0, 0]);
  });
}

// Camera Preset Transitions
const CAMERA_PRESETS = {
  arena: { pos: new THREE.Vector3(0, 8, 26), look: new THREE.Vector3(0, 0, 0) },
  workbench: { pos: new THREE.Vector3(-36, 4, 20), look: new THREE.Vector3(-36, 0, -2) },
  hardware: { pos: new THREE.Vector3(36, 4, 20), look: new THREE.Vector3(36, 0, -2) },
  wide: { pos: new THREE.Vector3(0, 18, 56), look: new THREE.Vector3(0, 0, -2) }
};

function transitionCamera(presetKey) {
  const p = CAMERA_PRESETS[presetKey];
  if (!p) return;
  state.cameraPreset = presetKey;
  state.targetCameraPos.copy(p.pos);
  state.targetCameraLook.copy(p.look);
  state.isCameraTransitioning = true;

  document.querySelectorAll('.preset-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.preset === presetKey);
  });
}

document.querySelectorAll('.preset-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    transitionCamera(btn.dataset.preset);
  });
});

// Modals: Hint & Explain Why
const modalHint = document.getElementById('modal-hint');
const modalExplain = document.getElementById('modal-explain');

const btnHint = document.getElementById('btn-hint');
if (btnHint && modalHint) {
  btnHint.addEventListener('click', () => modalHint.classList.add('active'));
}

const btnExplain = document.getElementById('btn-explain');
if (btnExplain && modalExplain) {
  btnExplain.addEventListener('click', () => modalExplain.classList.add('active'));
}

document.querySelectorAll('.modal-close, .modal-backdrop').forEach(el => {
  el.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-backdrop') || e.target.classList.contains('modal-close')) {
      document.querySelectorAll('.modal-backdrop').forEach(m => m.classList.remove('active'));
    }
  });
});

// ============================================================================
// 9. RAYCASTING & 3D INTERACTION
// ============================================================================

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

window.addEventListener('pointermove', (event) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(nodeMeshes);

  if (intersects.length > 0) {
    container.style.cursor = 'pointer';
  } else {
    container.style.cursor = 'default';
  }
});

window.addEventListener('pointerdown', (event) => {
  // Only handle left clicks directly on canvas
  if (event.button !== 0 || event.target.tagName !== 'CANVAS') return;

  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(nodeMeshes);

  if (intersects.length > 0) {
    const clickedNode = intersects[0].object;
    if (clickedNode.userData && clickedNode.userData.id !== undefined) {
      toggleNode(clickedNode.userData.id);
    }
  }
});

// ============================================================================
// 10. ANIMATION LOOP & SMOOTH INTERPOLATION
// ============================================================================

let clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();
  const time = clock.getElapsedTime();

  // Smooth Camera Lerp
  if (state.isCameraTransitioning) {
    camera.position.lerp(state.targetCameraPos, 0.08);
    controls.target.lerp(state.targetCameraLook, 0.08);

    if (camera.position.distanceTo(state.targetCameraPos) < 0.1 &&
        controls.target.distanceTo(state.targetCameraLook) < 0.1) {
      camera.position.copy(state.targetCameraPos);
      controls.target.copy(state.targetCameraLook);
      state.isCameraTransitioning = false;
    }
  }

  // Gentle node floating / breathing animation
  nodeMeshes.forEach((mesh, idx) => {
    mesh.position.y += Math.sin(time * 2.0 + idx) * 0.003;
  });

  // Animated energy flow along severed (cut) edges
  edgeObjects.forEach(({ mesh, edge }) => {
    const isCut = state.partition[edge.u] !== state.partition[edge.v];
    if (isCut) {
      const pulse = 0.8 + Math.sin(time * 4.0 + edge.u) * 0.25;
      mesh.material.emissiveIntensity = pulse;
    }
  });

  // Subtle rotation of Processor D coupling qubits
  hwQubitMeshes.forEach((mesh, idx) => {
    mesh.rotation.y = time * 0.5 + idx * 0.2;
  });

  controls.update();
  renderer.render(scene, camera);
}

// Window Resize Handling
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Initialize Scene to Target Optimal State by default for impressive showcase
setPartition([1, 1, 0, 1, 0, 0], false);
animate();
