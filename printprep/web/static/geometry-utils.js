"use strict";

// Pure geometry helpers — no three.js dependency, so they can be unit-tested
// under Node. `positions` is a flat array where vertex i is
// [positions[3i], positions[3i+1], positions[3i+2]]; `count` is the vertex
// count (3 * number of triangles). STLLoader geometry is non-indexed, so
// triangle f uses vertices 3f, 3f+1, 3f+2.

function quantizedKey(positions, i, q) {
  return `${Math.round(positions[3 * i] / q)},${Math.round(positions[3 * i + 1] / q)},${Math.round(positions[3 * i + 2] / q)}`;
}

// Connected components (separate bodies) via union-find on welded vertices.
export function connectedComponents(positions, count, quantum = 1e-5) {
  const q = quantum > 0 ? quantum : 1e-5;
  const keyToId = new Map();
  const canon = new Int32Array(count);
  let nextId = 0;
  for (let i = 0; i < count; i++) {
    const k = quantizedKey(positions, i, q);
    let id = keyToId.get(k);
    if (id === undefined) { id = nextId++; keyToId.set(k, id); }
    canon[i] = id;
  }

  const parent = new Int32Array(nextId);
  for (let i = 0; i < nextId; i++) parent[i] = i;
  const find = (x) => { while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; };
  const union = (x, y) => { const a = find(x), b = find(y); if (a !== b) parent[a] = b; };
  for (let f = 0; f < count; f += 3) {
    union(canon[f], canon[f + 1]);
    union(canon[f + 1], canon[f + 2]);
  }

  const rootToBody = new Map();
  const faceN = count / 3;
  const bodyOfFace = new Int32Array(faceN);
  for (let fi = 0; fi < faceN; fi++) {
    const r = find(canon[fi * 3]);
    let b = rootToBody.get(r);
    if (b === undefined) { b = rootToBody.size; rootToBody.set(r, b); }
    bodyOfFace[fi] = b;
  }
  return { bodyOfFace, bodyCount: rootToBody.size };
}

// Per-face overhang flags. A face needs support when its (right-hand-rule)
// normal points downward beyond `thresholdDeg` from vertical AND it sits above
// the build plate (so the footprint resting on the bed is excluded).
export function overhangFlags(positions, count, thresholdDeg = 45) {
  const faceN = count / 3;
  const flags = new Uint8Array(faceN);
  if (faceN === 0) return flags;

  let minZ = Infinity, maxZ = -Infinity;
  for (let i = 0; i < count; i++) {
    const z = positions[3 * i + 2];
    if (z < minZ) minZ = z;
    if (z > maxZ) maxZ = z;
  }
  const tol = 1e-6 + 1e-3 * (maxZ - minZ);
  const sinT = Math.sin((thresholdDeg * Math.PI) / 180);

  for (let fi = 0; fi < faceN; fi++) {
    const o = fi * 9;
    const ax = positions[o], ay = positions[o + 1], az = positions[o + 2];
    const bx = positions[o + 3], by = positions[o + 4], bz = positions[o + 5];
    const cx = positions[o + 6], cy = positions[o + 7], cz = positions[o + 8];
    const abx = bx - ax, aby = by - ay, abz = bz - az;
    const acx = cx - ax, acy = cy - ay, acz = cz - az;
    const nx = aby * acz - abz * acy;
    const ny = abz * acx - abx * acz;
    const nz = abx * acy - aby * acx;
    const len = Math.hypot(nx, ny, nz) || 1;
    const nzn = nz / len;
    const centroidZ = (az + bz + cz) / 3;
    flags[fi] = nzn < -sinT && centroidZ > minZ + tol ? 1 : 0;
  }
  return flags;
}

// Boundary (open) edges = edges used by exactly one triangle. Returns an array
// of [vertexIndexA, vertexIndexB] pairs. A watertight mesh returns [].
export function openEdges(positions, count, quantum = 1e-5) {
  const q = quantum > 0 ? quantum : 1e-5;
  const edges = new Map();
  for (let f = 0; f < count; f += 3) {
    const idx = [f, f + 1, f + 2];
    for (let e = 0; e < 3; e++) {
      const i1 = idx[e], i2 = idx[(e + 1) % 3];
      const k1 = quantizedKey(positions, i1, q);
      const k2 = quantizedKey(positions, i2, q);
      const ek = k1 < k2 ? `${k1}|${k2}` : `${k2}|${k1}`;
      const rec = edges.get(ek);
      if (rec) rec.count++;
      else edges.set(ek, { count: 1, i1, i2 });
    }
  }
  const result = [];
  edges.forEach((rec) => { if (rec.count === 1) result.push([rec.i1, rec.i2]); });
  return result;
}
