import test from "node:test";
import assert from "node:assert/strict";

import {
  connectedComponents,
  overhangFlags,
  openEdges,
} from "../../printprep/web/static/geometry-utils.js";

// helper: flatten a list of triangles ([[ax,ay,az],...]) into a positions array
function tris(...triangles) {
  const out = [];
  for (const t of triangles) for (const v of t) out.push(v[0], v[1], v[2]);
  return { positions: out, count: triangles.length * 3 };
}

test("connectedComponents: two separated triangles -> 2 bodies", () => {
  const { positions, count } = tris(
    [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
    [[10, 0, 0], [11, 0, 0], [10, 1, 0]],
  );
  const { bodyOfFace, bodyCount } = connectedComponents(positions, count);
  assert.equal(bodyCount, 2);
  assert.deepEqual([...bodyOfFace], [0, 1]);
});

test("connectedComponents: edge-sharing triangles -> 1 body", () => {
  // two triangles sharing the edge (0,0,0)-(1,0,0)
  const { positions, count } = tris(
    [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
    [[0, 0, 0], [1, 0, 0], [1, 1, 0]],
  );
  const { bodyCount } = connectedComponents(positions, count);
  assert.equal(bodyCount, 1);
});

test("overhangFlags: downward elevated face flagged, bed face not", () => {
  const { positions, count } = tris(
    [[0, 0, 0], [1, 0, 0], [0, 1, 0]], // bed, normal +z
    [[0, 0, 1], [0, 1, 1], [1, 0, 1]], // elevated, normal -z (overhang)
  );
  const flags = overhangFlags(positions, count, 45);
  assert.deepEqual([...flags], [0, 1]);
});

test("openEdges: single triangle has 3 boundary edges", () => {
  const { positions, count } = tris([[0, 0, 0], [1, 0, 0], [0, 1, 0]]);
  assert.equal(openEdges(positions, count).length, 3);
});

test("openEdges: two triangles sharing an edge -> 4 boundary edges", () => {
  const { positions, count } = tris(
    [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
    [[1, 0, 0], [0, 1, 0], [1, 1, 0]], // shares edge (1,0,0)-(0,1,0)
  );
  assert.equal(openEdges(positions, count).length, 4);
});
