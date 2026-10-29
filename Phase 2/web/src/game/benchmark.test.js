import test from 'node:test';
import assert from 'node:assert/strict';
import { EDGES, TOTAL_WEIGHT, KNOWN_OPTIMUM, OPTIMAL_BITS, INITIAL_BITS, cutScore, crossedEdgeCount, enumerateAssignments, findImprovingMove } from '../src/game/benchmark.js';

test('benchmark has six vertices and nine weighted edges totaling 27', () => {
  assert.equal(EDGES.length, 9);
  assert.equal(TOTAL_WEIGHT, 27);
  assert.deepEqual(EDGES.map(e => [e.u, e.v, e.w]), [
    [0,2,1], [0,3,4], [0,4,4], [1,4,3], [1,5,3], [2,3,5], [2,4,1], [3,4,4], [3,5,2],
  ]);
});

test('reported optimal partition scores 22 and separates seven of nine edges', () => {
  assert.equal(cutScore(OPTIMAL_BITS), KNOWN_OPTIMUM);
  assert.equal(crossedEdgeCount(OPTIMAL_BITS), 7);
  assert.equal(cutScore(OPTIMAL_BITS.map(bit => 1 - bit)), KNOWN_OPTIMUM);
});

test('initial playable state has weighted cut 20', () => {
  assert.equal(cutScore(INITIAL_BITS), 20);
  assert.equal(crossedEdgeCount(INITIAL_BITS), 6);
});

test('all 64 bitstrings have maximum 22, with exactly two optimal bitstrings', () => {
  const scores = enumerateAssignments().map(cutScore);
  assert.equal(scores.length, 64);
  assert.equal(Math.max(...scores), KNOWN_OPTIMUM);
  assert.equal(scores.filter(score => score === KNOWN_OPTIMUM).length, 2);
});

test('uniform random assignment mean cut is 13.5', () => {
  const scores = enumerateAssignments().map(cutScore);
  assert.equal(scores.reduce((sum, value) => sum + value, 0) / scores.length, 13.5);
});

test('cut scoring rejects invalid assignments', () => {
  assert.throws(() => cutScore([0, 1]), TypeError);
  assert.throws(() => cutScore([0, 0, 0, 0, 0, 2]), TypeError);
});

test('hint escapes the initial local plateau with the smallest improving move', () => {
  const move = findImprovingMove(INITIAL_BITS);
  assert.equal(move.score, KNOWN_OPTIMUM);
  assert.deepEqual(move.changedNodes, [2, 3]);
  assert.deepEqual(move.assignment, [0, 0, 1, 0, 1, 1]);
});
