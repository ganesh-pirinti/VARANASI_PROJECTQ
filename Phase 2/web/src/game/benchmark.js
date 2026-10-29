/** PS-O1 six-node weighted Max-Cut benchmark used by the Mission 22 teaching game. */
export const EDGES = Object.freeze([
  Object.freeze({ u: 0, v: 2, w: 1 }),
  Object.freeze({ u: 0, v: 3, w: 4 }),
  Object.freeze({ u: 0, v: 4, w: 4 }),
  Object.freeze({ u: 1, v: 4, w: 3 }),
  Object.freeze({ u: 1, v: 5, w: 3 }),
  Object.freeze({ u: 2, v: 3, w: 5 }),
  Object.freeze({ u: 2, v: 4, w: 1 }),
  Object.freeze({ u: 3, v: 4, w: 4 }),
  Object.freeze({ u: 3, v: 5, w: 2 }),
]);

export const TOTAL_WEIGHT = EDGES.reduce((sum, edge) => sum + edge.w, 0);
export const KNOWN_OPTIMUM = 22;
export const OPTIMAL_BITS = Object.freeze([1, 1, 0, 1, 0, 0]);
export const INITIAL_BITS = Object.freeze([0, 0, 0, 1, 1, 1]);

export function cutScore(bits) {
  if (!Array.isArray(bits) || bits.length !== 6 || bits.some(bit => bit !== 0 && bit !== 1)) {
    throw new TypeError('A valid PS-O1 assignment is an array of six binary values.');
  }
  return EDGES.reduce((score, edge) => score + (bits[edge.u] !== bits[edge.v] ? edge.w : 0), 0);
}

export function crossedEdgeCount(bits) {
  if (!Array.isArray(bits) || bits.length !== 6 || bits.some(bit => bit !== 0 && bit !== 1)) {
    throw new TypeError('A valid PS-O1 assignment is an array of six binary values.');
  }
  return EDGES.filter(edge => bits[edge.u] !== bits[edge.v]).length;
}

export function enumerateAssignments() {
  return Array.from({ length: 64 }, (_, mask) =>
    Array.from({ length: 6 }, (_, qubit) => (mask >> qubit) & 1));
}

/** Find the shortest coordinated move that improves the score. Ties prefer the higher score. */
export function findImprovingMove(bits) {
  const currentScore = cutScore(bits);
  const candidates = enumerateAssignments()
    .map(assignment => ({
      assignment,
      score: cutScore(assignment),
      changedNodes: assignment.map((bit, index) => bit === bits[index] ? -1 : index).filter(index => index >= 0),
    }))
    .filter(candidate => candidate.score > currentScore);
  candidates.sort((a, b) => a.changedNodes.length - b.changedNodes.length || b.score - a.score);
  return candidates[0] ?? null;
}
