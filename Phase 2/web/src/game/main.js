import * as THREE from 'three';
import { EDGES, TOTAL_WEIGHT, KNOWN_OPTIMUM, OPTIMAL_BITS, INITIAL_BITS, cutScore, crossedEdgeCount, findImprovingMove } from './benchmark.js';

const NODE_POSITIONS = [
  [-3.7, 0.15, 1.8], [-2.7, -0.55, -1.4], [-1.6, 1.45, 0.05],
  [0.15, -0.55, 2.15], [1.75, 0.65, -0.8], [3.25, -0.25, 1.25],
];
const COLORS = { a: 0x55e6d2, b: 0x8c92ff, cut: 0xffa45c, internal: 0x34445d };

export function mountMission22Game(container) {
  if (!container) throw new Error('Mission 22 needs a mounting element.');

  container.innerHTML = `
    <main class="mission22">
      <header class="m22-topbar">
        <a class="m22-brand" href="#mission22" aria-label="VARANASI Mission 22 home">
          <span class="m22-mark">V</span><span><b>VARANASI</b><small>ENGINEERING SIMULATION / PS-O1</small></span>
        </a>
        <div class="m22-top-meta"><span class="m22-live-dot"></span> INTERACTIVE LAB <span class="m22-meta-divider">/</span> SIMULATED RESULTS</div>
        <button class="m22-quiet-button" data-action="reset" type="button">Reset mission ↺</button>
      </header>

      <section class="m22-intro">
        <div>
          <div class="m22-eyebrow">MISSION 22 <span>•</span> QUANTUM NETWORK ARCHITECT</div>
          <h1>Partition the network.<br><em>Understand the quantum path.</em></h1>
          <p>Explore the six-node weighted graph behind the PS-O1 benchmark. Every move updates the cut score using the real edge weights.</p>
        </div>
        <div class="m22-target-card"><span>BEST KNOWN CUT</span><strong>22 <small>/ 27</small></strong><div class="m22-target-line"><i></i></div><small>Exact classical optimum · 64 assignments checked</small></div>
      </section>

      <nav class="m22-tabs" aria-label="Learning missions">
        <button class="is-active" data-tab="network" type="button"><span>01</span> Network lab</button>
        <button data-tab="baseline" type="button"><span>02</span> Random baseline</button>
        <button data-tab="circuit" type="button"><span>03</span> QAOA circuit</button>
        <button data-tab="processors" type="button"><span>04</span> Processor routing</button>
        <button data-tab="noise" type="button"><span>05</span> Noise & results</button>
      </nav>

      <section class="m22-page is-visible" data-page="network">
        <div class="m22-workspace">
          <section class="m22-scene-panel">
            <div class="m22-panel-head"><div><span class="m22-kicker">LIVE GRAPH</span><h2>Choose the partition</h2></div><span class="m22-scene-tag"><i></i> 6 NODES / 9 EDGES</span></div>
            <div class="m22-scene-wrap" data-scene-host>
              <div class="m22-scene-hint">SELECT ANY NODE TO SWITCH ITS GROUP</div>
              <div class="m22-scene-corner">WEIGHTED MAX-CUT <span>↗</span></div>
              <div class="m22-scene-loading" data-scene-loading>Preparing 3D network…</div>
            </div>
            <div class="m22-legend"><span><i class="m22-dot-a"></i> GROUP A</span><span><i class="m22-dot-b"></i> GROUP B</span><span><i class="m22-line-cut"></i> CUT EDGE</span><span><i class="m22-line-inner"></i> INTERNAL EDGE</span></div>
          </section>
          <aside class="m22-score-panel">
            <div class="m22-panel-head"><div><span class="m22-kicker">MISSION OBJECTIVE</span><h2>Maximize the cut</h2></div><span class="m22-step">01 / 05</span></div>
            <div class="m22-score-number"><strong data-score>20</strong><span>/ 27<br><small>weighted cut</small></span></div>
            <div class="m22-progress"><i data-progress style="width:74.07%"></i></div>
            <div class="m22-stat-row"><span>Cut fraction</span><b data-fraction>74.07%</b></div>
            <div class="m22-stat-row"><span>Edges separated</span><b data-separated>6 / 9</b></div>
            <div class="m22-divider"></div>
            <div class="m22-groups">
              <div class="m22-group m22-group-a"><span class="m22-group-title"><i></i> GROUP A</span><strong data-group-a>3 nodes</strong><small data-members-a>3 · 4 · 5</small></div>
              <div class="m22-group m22-group-b"><span class="m22-group-title"><i></i> GROUP B</span><strong data-group-b>3 nodes</strong><small data-members-b>0 · 1 · 2</small></div>
            </div>
            <div class="m22-feedback" data-feedback role="status"><b>Keep exploring.</b><span>Move a node across groups. Only edges connecting different groups add to the cut.</span></div>
            <div class="m22-actions"><button class="m22-button m22-button-primary" data-action="hint" type="button">Get a hint <span>↗</span></button><button class="m22-button m22-button-secondary" data-action="reveal" type="button">Reveal optimum</button></div>
            <div class="m22-optimal-note" data-optimal-note hidden></div>
          </aside>
        </div>
        <div class="m22-learning-strip"><div class="m22-learning-icon">i</div><div><b>What you're learning</b><p>A weighted edge contributes to the cut only when its endpoints are in different groups. Your goal is to maximize the sum—not the number—of crossing edge weights.</p></div><div class="m22-formula">C(x) = ∑ wᵢⱼ · [xᵢ ≠ xⱼ]</div></div>
      </section>

      <section class="m22-page" data-page="baseline">
        <div class="m22-section-card"><div class="m22-kicker">MISSION 02 / CLASSICAL REFERENCE</div><h2>How hard is it to get lucky?</h2><p>Six binary node assignments create 2⁶ = 64 bitstrings. Exactly two complementary assignments achieve the optimal cut of 22.</p>
          <div class="m22-baseline-grid"><div class="m22-metric"><span>Random mean cut</span><strong>13.50</strong><small>Expected weighted score</small></div><div class="m22-metric"><span>Optimal bitstrings</span><strong>2 / 64</strong><small>One solution and its complement</small></div><div class="m22-metric"><span>Random optimum chance</span><strong>3.125%</strong><small>Uniform random bitstrings</small></div></div>
          <div class="m22-baseline-visual"><div class="m22-baseline-bar"><span>Random average</span><div><i style="width:61.36%"></i></div><b>13.50</b></div><div class="m22-baseline-bar"><span>Best known cut</span><div><i style="width:100%"></i></div><b>22.00</b></div></div>
          <div class="m22-callout"><b>Try the challenge:</b> return to <button data-goto="network" type="button">Network Lab</button> and reach 22 by switching node groups. The random baseline is a reference point, not evidence of quantum speedup.</div>
        </div>
      </section>

      <section class="m22-page" data-page="circuit">
        <div class="m22-section-card"><div class="m22-kicker">MISSION 03 / QAOA BUILD PATH</div><h2>From graph edges to quantum gates</h2><p>The benchmark's cut objective becomes a QUBO, then a Hamiltonian, and finally a repeated cost/mixer circuit before measurement.</p>
          <div class="m22-pipeline"><div><span>01</span><b>Weighted graph</b><small>6 vertices · 9 edges</small></div><i>→</i><div><span>02</span><b>QUBO objective</b><small>Minimize −C(x)</small></div><i>→</i><div><span>03</span><b>Cost Hamiltonian</b><small>Pairwise Z terms</small></div><i>→</i><div><span>04</span><b>Measure</b><small>Bitstrings → cut scores</small></div></div>
          <div class="m22-math-grid"><div><span class="m22-kicker">MAX-CUT OBJECTIVE</span><div class="m22-equation">C(x) = ∑ wᵢⱼ(xᵢ + xⱼ − 2xᵢxⱼ)</div><p>Each edge contributes its weight if its endpoint bits differ.</p></div><div><span class="m22-kicker">QUBO USED BY THE SOLVER</span><div class="m22-equation">minimize −C(x)</div><p>The implementation converts a maximization target to minimization.</p></div><div><span class="m22-kicker">MAX-CUT HAMILTONIAN</span><div class="m22-equation">H₍cut₎ = ∑ wᵢⱼ/2 (I − ZᵢZⱼ)</div><p>The solver minimizes −C(x). The circuit's cost-unitary sign convention must remain consistent with that minimization.</p></div><div><span class="m22-kicker">MIXER</span><div class="m22-equation">RX(2β) on each qubit</div><p>The mixer explores assignments; measurement produces candidate bitstrings.</p></div></div>
          <div class="m22-circuit-box"><div><b>One cost interaction</b><small>Conceptual gate sequence for a weighted edge</small></div><div class="m22-gate-row"><span class="m22-qubit-label">qᵢ</span><span class="m22-gate m22-gate-cx">CX</span><span class="m22-wire"></span><span class="m22-gate m22-gate-rz">RZ(γw)</span><span class="m22-wire"></span><span class="m22-gate m22-gate-cx">CX</span></div><div class="m22-gate-row"><span class="m22-qubit-label">qⱼ</span><span class="m22-wire"></span><span class="m22-wire m22-wire-link"></span><span class="m22-wire"></span><span class="m22-wire m22-wire-link"></span><span class="m22-wire"></span></div><div class="m22-circuit-foot">Conceptual explanation of the entangling pattern used for a pair term. Actual circuit parameters and sign conventions must match the implementation.</div></div>
        </div>
      </section>

      <section class="m22-page" data-page="processors">
        <div class="m22-section-card"><div class="m22-kicker">MISSION 04 / CONNECTIVITY COST</div><h2>A circuit has to fit the hardware</h2><p>Both B and D can host the six-qubit workload in this benchmark. Processor A has only five qubits, so it cannot execute the six-qubit instance as specified.</p>
          <div class="m22-processor-grid"><article class="m22-processor-card"><div class="m22-processor-heading"><span>PROCESSOR B</span><span class="m22-chip">9 qubits</span></div><div class="m22-resource"><span>Physical CX gates</span><b>21</b></div><div class="m22-resource"><span>Total circuit depth</span><b>37</b></div><div class="m22-resource"><span>Two-qubit depth</span><b>17</b></div><div class="m22-resource"><span>SWAP count</span><b>1</b></div><p>Higher routing/resource overhead in this reported transpilation.</p></article><article class="m22-processor-card m22-processor-card-featured"><div class="m22-processor-heading"><span>PROCESSOR D</span><span class="m22-chip m22-chip-good">9 qubits</span></div><div class="m22-resource"><span>Physical CX gates</span><b>18</b></div><div class="m22-resource"><span>Total circuit depth</span><b>29</b></div><div class="m22-resource"><span>Two-qubit depth</span><b>14</b></div><div class="m22-resource"><span>SWAP count</span><b>0</b></div><p>Lower reported routing overhead; sampled solution quality is a separate measure.</p></article></div>
          <div class="m22-callout"><b>Engineering takeaway:</b> connectivity and routing affect circuit resources. Fewer gates or lower depth do not automatically guarantee a better noisy result.</div>
        </div>
      </section>

      <section class="m22-page" data-page="noise">
        <div class="m22-section-card"><div class="m22-kicker">MISSION 05 / SIMULATION RESULTS</div><h2>Noise changes the sampled outcome</h2><p>These are stored simulated benchmark summaries, not measurements from physical quantum hardware. P(opt) is the sampled probability of measuring an optimal bitstring.</p>
          <div class="m22-results-wrap"><table class="m22-results"><thead><tr><th>Processor / mode</th><th>Mean cut</th><th>Approx. ratio</th><th>Optimal samples</th><th>P(opt)</th></tr></thead><tbody><tr><td>B · Ideal</td><td>17.762</td><td>0.8074</td><td>572 / 4096</td><td><b>13.96%</b></td></tr><tr><td>B · Noisy</td><td>17.322</td><td>0.7874</td><td>516 / 4096</td><td><b>12.60%</b></td></tr><tr><td>D · Ideal</td><td>17.713</td><td>0.8052</td><td>567 / 4096</td><td><b>13.84%</b></td></tr><tr><td>D · Noisy</td><td>17.297</td><td>0.7862</td><td>512 / 4096</td><td><b>12.50%</b></td></tr></tbody></table></div>
          <div class="m22-results-bars"><div><span>B ideal</span><i><b style="width:13.96%"></b></i><strong>13.96%</strong></div><div><span>B noisy</span><i><b style="width:12.60%"></b></i><strong>12.60%</strong></div><div><span>D ideal</span><i><b style="width:13.84%"></b></i><strong>13.84%</strong></div><div><span>D noisy</span><i><b style="width:12.50%"></b></i><strong>12.50%</strong></div></div>
          <div class="m22-callout"><b>Read the evidence correctly:</b> these results compare simulated sampling quality and routing resources. They do not establish a quantum speedup over classical methods.</div>
        </div>
      </section>
      <footer class="m22-footer"><span>VARANASI / PS-O1</span><span>EDUCATIONAL SIMULATION · NO PHYSICAL QPU CLAIMS</span><span>MISSION 22</span></footer>
    </main>`;

  const root = container.querySelector('.mission22');
  const host = root.querySelector('[data-scene-host]');
  const loading = root.querySelector('[data-scene-loading]');
  const state = { bits: [...INITIAL_BITS], activeTab: 'network', hintedNodes: [], optimalRevealed: false };
  let renderer, scene, camera, raycaster, pointer, resizeObserver, animationFrame;
  let nodeObjects = [], edgeObjects = [], edgeLabelObjects = [];

  function crossedCount(bits) { return crossedEdgeCount(bits); }
  function members(bit) { return bit === 1 ? state.bits.map((b, i) => b === 1 ? i : -1).filter(i => i >= 0) : state.bits.map((b, i) => b === 0 ? i : -1).filter(i => i >= 0); }
  function activeEdges() { return EDGES.map(e => ({ ...e, cut: state.bits[e.u] !== state.bits[e.v] })); }

  function setFeedback(title, message, kind = 'neutral') {
    const feedback = root.querySelector('[data-feedback]');
    feedback.className = `m22-feedback ${kind === 'success' ? 'is-success' : kind === 'hint' ? 'is-hint' : ''}`;
    feedback.innerHTML = `<b></b><span></span>`;
    feedback.querySelector('b').textContent = title;
    feedback.querySelector('span').textContent = message;
  }

  function updateGraphVisuals() {
    edgeObjects.forEach(({ line, edge }) => {
      const isCut = state.bits[edge.u] !== state.bits[edge.v];
      line.material.color.setHex(isCut ? COLORS.cut : COLORS.internal);
      line.material.opacity = isCut ? 0.95 : 0.42;
      line.material.emissive?.setHex(isCut ? 0x5a230b : 0x000000);
    });
    nodeObjects.forEach(({ mesh, ring, label }, i) => {
      const isA = state.bits[i] === 1;
      const color = isA ? COLORS.a : COLORS.b;
      mesh.material.color.setHex(color);
      mesh.material.emissive.setHex(color);
      mesh.material.emissiveIntensity = state.hintedNodes.includes(i) ? 1.1 : 0.45;
      ring.material.color.setHex(color);
      ring.material.opacity = state.hintedNodes.includes(i) ? 0.95 : 0.42;
      label.material.opacity = 1;
    });
    edgeLabelObjects.forEach(({ sprite, edge }) => {
      sprite.material.opacity = state.bits[edge.u] !== state.bits[edge.v] ? 1 : 0.68;
    });
  }

  function updateHUD() {
    const score = cutScore(state.bits);
    const crossed = crossedCount(state.bits);
    const groupA = members(1), groupB = members(0);
    root.querySelector('[data-score]').textContent = String(score);
    root.querySelector('[data-fraction]').textContent = `${(100 * score / TOTAL_WEIGHT).toFixed(2)}%`;
    root.querySelector('[data-separated]').textContent = `${crossed} / ${EDGES.length}`;
    root.querySelector('[data-progress]').style.width = `${100 * score / TOTAL_WEIGHT}%`;
    root.querySelector('[data-group-a]').textContent = `${groupA.length} node${groupA.length === 1 ? '' : 's'}`;
    root.querySelector('[data-group-b]').textContent = `${groupB.length} node${groupB.length === 1 ? '' : 's'}`;
    root.querySelector('[data-members-a]').textContent = groupA.length ? groupA.join(' · ') : 'No nodes assigned';
    root.querySelector('[data-members-b]').textContent = groupB.length ? groupB.join(' · ') : 'No nodes assigned';
    const note = root.querySelector('[data-optimal-note]');
    if (score === KNOWN_OPTIMUM) {
      setFeedback('Optimal cut reached!', 'You found a maximum cut with weight 22. The complementary partition scores equally well.', 'success');
      note.hidden = false;
      note.textContent = 'MISSION CLEAR · Exact optimum verified by exhaustive enumeration of all 64 assignments.';
    } else {
      note.hidden = true;
      if (state.hintedNodes.length === 0) setFeedback('Keep exploring.', 'Move a node across groups. Only edges connecting different groups add to the cut.');
    }
    updateGraphVisuals();
  }


  function addTextSprite(text, color = '#eaf3ff', scale = 1) {
    const canvas = document.createElement('canvas');
    canvas.width = 256; canvas.height = 96;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, 256, 96);
    ctx.font = '700 46px ui-monospace, SFMono-Regular, Menlo, monospace';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = color; ctx.shadowColor = color; ctx.shadowBlur = 14;
    ctx.fillText(text, 128, 48);
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false });
    const sprite = new THREE.Sprite(material); sprite.scale.set(0.85 * scale, 0.32 * scale, 1);
    return sprite;
  }

  function setupScene() {
    try {
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x080d19);
      scene.fog = new THREE.Fog(0x080d19, 12, 25);
      camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
      camera.position.set(0, 6.4, 12.8);
      camera.lookAt(0, 0.15, 0.25);
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'low-power' });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.05;
      renderer.domElement.className = 'm22-webgl';
      renderer.domElement.setAttribute('aria-label', 'Interactive 3D six-node network. Click a node to switch its partition group.');
      renderer.domElement.setAttribute('tabindex', '0');
      host.appendChild(renderer.domElement);
      scene.add(new THREE.HemisphereLight(0x9fc6ff, 0x11192b, 1.7));
      const keyLight = new THREE.PointLight(0x5be8d5, 30, 24); keyLight.position.set(-5, 6, 5); scene.add(keyLight);
      const rimLight = new THREE.PointLight(0x8a89ff, 24, 24); rimLight.position.set(5, 3, -5); scene.add(rimLight);

      const floorGrid = new THREE.GridHelper(24, 30, 0x23314a, 0x172135);
      floorGrid.position.y = -1.75;
      floorGrid.material.transparent = true; floorGrid.material.opacity = 0.34;
      scene.add(floorGrid);
      const ambientPoints = [];
      for (let i = 0; i < 180; i += 1) ambientPoints.push((Math.random() - 0.5) * 20, Math.random() * 9 - 1, (Math.random() - 0.5) * 18);
      const starGeometry = new THREE.BufferGeometry();
      starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(ambientPoints, 3));
      const starField = new THREE.Points(starGeometry, new THREE.PointsMaterial({ color: 0x7d90b3, size: 0.025, transparent: true, opacity: 0.55 })); scene.add(starField);

      const vectorFor = i => new THREE.Vector3(...NODE_POSITIONS[i]);
      EDGES.forEach((edge) => {
        const start = vectorFor(edge.u), end = vectorFor(edge.v);
        const lineGeometry = new THREE.BufferGeometry().setFromPoints([start, end]);
        const lineMaterial = new THREE.LineBasicMaterial({ color: COLORS.internal, transparent: true, opacity: 0.5 });
        const line = new THREE.Line(lineGeometry, lineMaterial); scene.add(line);
        edgeObjects.push({ line, edge });
        const midpoint = start.clone().add(end).multiplyScalar(0.5); midpoint.y += 0.23;
        const label = addTextSprite(`×${edge.w}`, '#dce8fa', 0.62); label.position.copy(midpoint); scene.add(label);
        edgeLabelObjects.push({ sprite: label, edge });
      });

      const sphereGeo = new THREE.IcosahedronGeometry(0.34, 2);
      NODE_POSITIONS.forEach((position, i) => {
        const group = new THREE.Group(); group.position.set(...position); scene.add(group);
        const isA = state.bits[i] === 1, color = isA ? COLORS.a : COLORS.b;
        const material = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.45, metalness: 0.18, roughness: 0.28 });
        const mesh = new THREE.Mesh(sphereGeo, material); mesh.userData.nodeIndex = i; group.add(mesh);
                const ringMaterial = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.42, side: THREE.DoubleSide });
        const ring = new THREE.Mesh(new THREE.TorusGeometry(0.48, 0.012, 8, 48), ringMaterial); ring.rotation.x = Math.PI / 2.5; group.add(ring);
        const label = addTextSprite(`NODE ${i}`, '#f0f5ff', 0.9); label.position.set(0, 0.73, 0); group.add(label);
        nodeObjects.push({ mesh, ring, label, group });
      });

      raycaster = new THREE.Raycaster(); pointer = new THREE.Vector2();
      renderer.domElement.addEventListener('pointerup', onScenePointerUp);
      resizeObserver = new ResizeObserver(resizeScene);
      resizeObserver.observe(host);
      resizeScene();
      loading?.remove();
      return true;
    } catch (error) {
      console.error('Mission 22 3D renderer failed to initialize:', error);
      loading.textContent = '3D preview is unavailable in this browser. You can still use the controls and learn from the result panels.';
      loading.classList.add('m22-scene-error');
      return false;
    }
  }

  function onScenePointerUp(event) {
    if (!renderer || !camera || !raycaster) return;
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const meshes = nodeObjects.map(o => o.mesh);
    const hit = raycaster.intersectObjects(meshes, false)[0];
    if (hit && Number.isInteger(hit.object.userData.nodeIndex)) toggleNode(hit.object.userData.nodeIndex);
  }

  function resizeScene() {
    if (!renderer || !camera) return;
    const width = Math.max(1, host.clientWidth), height = Math.max(1, host.clientHeight);
    camera.aspect = width / height; camera.updateProjectionMatrix(); renderer.setSize(width, height, false);
  }

  const clock = new THREE.Clock();
  function animate() {
    animationFrame = requestAnimationFrame(animate);
    if (!renderer || !scene || !camera) return;
    const t = clock.getElapsedTime();
    nodeObjects.forEach(({ group }, i) => { group.position.y = NODE_POSITIONS[i][1] + Math.sin(t * 0.65 + i * 0.8) * 0.035; });
    renderer.render(scene, camera);
  }

  function setTab(tab) {
    state.activeTab = tab;
    root.querySelectorAll('[data-tab]').forEach(button => button.classList.toggle('is-active', button.dataset.tab === tab));
    root.querySelectorAll('[data-page]').forEach(page => page.classList.toggle('is-visible', page.dataset.page === tab));
    if (tab === 'network') resizeScene();
  }

  root.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => setTab(button.dataset.tab)));
  root.querySelectorAll('[data-goto]').forEach(button => button.addEventListener('click', () => setTab(button.dataset.goto)));
  root.querySelectorAll('[data-action="reset"]').forEach(button => button.addEventListener('click', () => {
    state.bits = [...INITIAL_BITS]; state.hintedNodes = []; state.optimalRevealed = false;
    root.querySelector('[data-optimal-note]').hidden = true;
    updateHUD(); setFeedback('Mission reset.', 'Switch nodes between groups and watch the weighted cut score update.');
  }));
  root.querySelector('[data-action="hint"]').addEventListener('click', () => {
    const move = findImprovingMove(state.bits);
    if (!move) {
      setFeedback('You are at the optimum.', 'No assignment has a higher cut score than this one.', 'success');
      return;
    }
    state.hintedNodes = [...move.changedNodes];
    updateGraphVisuals();
    const nodePhrase = move.changedNodes.map(index => `node ${index}`).join(' and ');
    const moveCount = move.changedNodes.length;
    setFeedback(
      moveCount === 1 ? `Hint: try ${nodePhrase}.` : `Coordinated hint: try ${nodePhrase}.`,
      `The shortest improving move changes ${moveCount} node${moveCount === 1 ? '' : 's'} and reaches score ${move.score}. Apply the highlighted nodes yourself; this is a search hint, not a quantum result.`,
      'hint',
    );
  });
  root.querySelector('[data-action="reveal"]').addEventListener('click', () => {
    state.bits = [...OPTIMAL_BITS]; state.hintedNodes = []; state.optimalRevealed = true;
    updateHUD();
    setFeedback('Optimal partition revealed.', 'Group A = {0, 1, 3}; Group B = {2, 4, 5}. The separated edge weights sum to 22.', 'success');
    root.querySelector('[data-optimal-note]').hidden = false;
  });

  // A graceful fallback retains the actual scoring game even when WebGL is disabled.
  updateHUD();
  setupScene();
  if (renderer) animate();

  return () => {
    if (animationFrame) cancelAnimationFrame(animationFrame);
    resizeObserver?.disconnect();
    if (renderer) {
      renderer.domElement.removeEventListener('pointerup', onScenePointerUp);
      renderer.dispose();
      renderer.domElement.remove();
    }
    scene?.traverse(object => {
      object.geometry?.dispose?.();
      if (Array.isArray(object.material)) object.material.forEach(material => material.dispose?.());
      else object.material?.dispose?.();
    });
    container.innerHTML = '';
  };
}
