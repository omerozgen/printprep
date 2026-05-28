"use strict";

import * as THREE from "three";
import { STLLoader } from "./vendor/addons/STLLoader.js";
import { OrbitControls } from "./vendor/addons/OrbitControls.js";
import { connectedComponents, overhangFlags, openEdges as findOpenEdges } from "./geometry-utils.js";

const NEUTRAL = new THREE.Color(0x9aa7b8);
const OVERHANG = new THREE.Color(0xf85149);
const THIN = new THREE.Color(0xe3b341);
const OVERHANG_THRESHOLD_DEG = 45;
const MIN_WALL_MM = 1.2;

let scene, camera, renderer, controls, container;
let mesh = null;
let grid = null;
let geometry = null;
let openEdges = null;
let invertedMesh = null;
let initialized = false;

// Measurement state
let measureMode = false;
let measurePending = null;     // first point of an in-progress measurement
let measurements = [];         // [{a, b, distance_mm, group}] group = THREE.Group of markers+line
let measureRoot = null;

// Cross-section state
let clipPlane = null;          // THREE.Plane; null when disabled
let clipAxis = "z";            // 'x'|'y'|'z'
let clipPosition = 0;          // world coord on that axis
let clipFlip = false;

const state = { overhang: true, thin: false, holes: true, bodies: false, inverted: false };
let thinFaces = null; // Set of face-start indices; null = not computed yet
let bodyOfFace = null; // Int32Array[F] -> body index; null = not computed
let bodyCount = 0;
let bodyColors = []; // THREE.Color per body index

function bodyColorFor(i) {
  // distinct hues via the golden angle
  return new THREE.Color().setHSL(((i * 137.508) % 360) / 360, 0.55, 0.6);
}

function init(el) {
  container = el;
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x12181f);

  const { clientWidth: w, clientHeight: h } = container;
  camera = new THREE.PerspectiveCamera(45, (w || 1) / (h || 1), 0.1, 100000);
  camera.up.set(0, 0, 1); // STL build direction is +Z

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(w, h);
  container.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const key = new THREE.DirectionalLight(0xffffff, 0.8);
  key.position.set(1, 1, 2);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xffffff, 0.4);
  fill.position.set(-1, -1, 1);
  scene.add(fill);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;

  renderer.localClippingEnabled = true;

  measureRoot = new THREE.Group();
  measureRoot.renderOrder = 3;
  scene.add(measureRoot);

  // Click-vs-drag detection so OrbitControls still rotates with a real drag.
  let downX = 0, downY = 0;
  renderer.domElement.addEventListener("pointerdown", (e) => {
    downX = e.clientX; downY = e.clientY;
  });
  renderer.domElement.addEventListener("pointerup", (e) => {
    const dx = e.clientX - downX, dy = e.clientY - downY;
    if (!measureMode || !mesh || dx * dx + dy * dy > 25) return;
    const rect = renderer.domElement.getBoundingClientRect();
    const ndc = new THREE.Vector2(
      ((e.clientX - rect.left) / rect.width) * 2 - 1,
      -((e.clientY - rect.top) / rect.height) * 2 + 1,
    );
    const ray = new THREE.Raycaster();
    ray.setFromCamera(ndc, camera);
    const hits = ray.intersectObject(mesh, false);
    if (hits.length) addMeasurePoint(hits[0].point.clone());
  });

  new ResizeObserver(onResize).observe(container);
  animate();
  initialized = true;
}

function onResize() {
  if (!container.clientWidth || !container.clientHeight) return;
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
  requestAnimationFrame(animate);
  if (controls) controls.update();
  if (renderer) renderer.render(scene, camera);
}

function colorize() {
  if (!geometry) return;
  const pos = geometry.attributes.position;
  const count = pos.count;
  const colors = new Float32Array(count * 3);

  const oflags = state.overhang ? overhangFlags(pos.array, count, OVERHANG_THRESHOLD_DEG) : null;

  for (let f = 0; f < count; f += 3) {
    const fi = f / 3;
    let col;
    if (state.bodies && bodyOfFace) {
      // body view: color each connected body distinctly (overrides issue colors)
      col = bodyColors[bodyOfFace[fi]] || NEUTRAL;
    } else {
      const isOver = oflags && oflags[fi];
      const isThin = state.thin && thinFaces && thinFaces.has(f);
      col = isOver ? OVERHANG : (isThin ? THIN : NEUTRAL);
    }
    for (let k = 0; k < 3; k++) {
      colors[(f + k) * 3] = col.r;
      colors[(f + k) * 3 + 1] = col.g;
      colors[(f + k) * 3 + 2] = col.b;
    }
  }
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  geometry.attributes.color.needsUpdate = true;
}

// ---- connected components (separate bodies) via union-find on welded verts ----
function computeBodies() {
  const pos = geometry.attributes.position;
  const q = Math.max(1e-5, (geometry.boundingSphere?.radius || 1) * 1e-5);
  const result = connectedComponents(pos.array, pos.count, q);
  bodyOfFace = result.bodyOfFace;
  bodyCount = result.bodyCount;
  bodyColors = Array.from({ length: bodyCount }, (_, i) => bodyColorFor(i));
}

// ---- open (boundary) edges = holes / non-watertight seams ----
function buildOpenEdges() {
  if (openEdges) {
    scene.remove(openEdges);
    openEdges.geometry.dispose();
    openEdges.material.dispose();
    openEdges = null;
  }
  const pos = geometry.attributes.position;
  const q = Math.max(1e-5, (geometry.boundingSphere?.radius || 1) * 1e-5);
  const boundary = findOpenEdges(pos.array, pos.count, q);

  const verts = [];
  for (const [i1, i2] of boundary) {
    verts.push(pos.getX(i1), pos.getY(i1), pos.getZ(i1),
               pos.getX(i2), pos.getY(i2), pos.getZ(i2));
  }

  if (verts.length === 0) return;
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(verts, 3));
  const m = new THREE.LineBasicMaterial({ color: 0xff5cf4, depthTest: false });
  openEdges = new THREE.LineSegments(g, m);
  openEdges.renderOrder = 2;
  openEdges.visible = state.holes;
  scene.add(openEdges);
}

// ---- thin-wall faces via inward ray casting (sampled, on demand) ----
function computeThinFaces() {
  const pos = geometry.attributes.position;
  const faceCount = pos.count / 3;
  const samples = Math.min(2500, Math.max(200, Math.floor(2_000_000 / Math.max(1, faceCount))));
  const step = Math.max(1, Math.floor(faceCount / samples));

  const r = geometry.boundingSphere?.radius || 1;
  const eps = Math.max(1e-3, r * 1e-4);
  const ray = new THREE.Raycaster();
  ray.near = eps * 2;
  ray.far = MIN_WALL_MM;

  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  const ab = new THREE.Vector3(), ac = new THREE.Vector3(), n = new THREE.Vector3();
  const origin = new THREE.Vector3(), dir = new THREE.Vector3();
  const found = new Set();

  for (let fi = 0; fi < faceCount; fi += step) {
    const f = fi * 3;
    a.fromBufferAttribute(pos, f);
    b.fromBufferAttribute(pos, f + 1);
    c.fromBufferAttribute(pos, f + 2);
    ab.subVectors(b, a);
    ac.subVectors(c, a);
    n.crossVectors(ab, ac).normalize();
    origin.set((a.x + b.x + c.x) / 3, (a.y + b.y + c.y) / 3, (a.z + b.z + c.z) / 3)
      .addScaledVector(n, -eps);
    dir.copy(n).multiplyScalar(-1);
    ray.set(origin, dir);
    const hits = ray.intersectObject(mesh, false);
    if (hits.length) found.add(f); // opposite wall within MIN_WALL_MM -> thin
  }
  thinFaces = found;
}

function frameCamera() {
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();
  const box = geometry.boundingBox;
  const sphere = geometry.boundingSphere;
  const center = sphere.center;
  const rad = sphere.radius || 1;

  controls.target.copy(center);
  const dist = rad * 2.6;
  camera.position.set(center.x + dist * 0.8, center.y - dist, center.z + dist * 0.7);
  camera.near = rad / 100;
  camera.far = rad * 100;
  camera.updateProjectionMatrix();
  controls.update();

  if (grid) {
    scene.remove(grid);
    grid.geometry.dispose();
    grid.material.dispose();
  }
  const span = Math.max(box.max.x - box.min.x, box.max.y - box.min.y) * 2 || 20;
  grid = new THREE.GridHelper(span, 20, 0x3b82f6, 0x2d3848);
  grid.rotation.x = Math.PI / 2;
  grid.position.set(center.x, center.y, box.min.z);
  scene.add(grid);
}

export function loadModelFromFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const el = document.getElementById("viewer");
        if (!initialized) init(el);
        else onResize();

        const parsed = new STLLoader().parse(reader.result);
        if (mesh) {
          scene.remove(mesh);
          mesh.geometry.dispose();
          mesh.material.dispose();
        }
        geometry = parsed;
        geometry.computeBoundingSphere();
        thinFaces = null;
        computeBodies();
        colorize();
        const material = new THREE.MeshStandardMaterial({
          vertexColors: true,
          flatShading: true,
          metalness: 0.0,
          roughness: 0.75,
          side: THREE.DoubleSide,
        });
        mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);
        buildOpenEdges();
        applyInverted();
        clearMeasurements();
        _applyClippingToMaterials();
        frameCamera();
        resolve();
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = () => reject(new Error("Dosya okunamadı"));
    reader.readAsArrayBuffer(file);
  });
}

export function setOverhang(enabled) {
  state.overhang = enabled;
  colorize();
}

export function setHoles(enabled) {
  state.holes = enabled;
  if (openEdges) openEdges.visible = enabled;
}

export function setThin(enabled) {
  state.thin = enabled;
  if (enabled && thinFaces === null && geometry) computeThinFaces();
  colorize();
}

export function setBodies(enabled) {
  state.bodies = enabled;
  colorize();
}

// Reversed-winding highlight: render back-faces in red. On a correctly wound
// solid the back-faces are interior (hidden); where the winding is flipped the
// surface's inside faces outward, so it shows up red. Always well-defined.
function applyInverted() {
  if (invertedMesh) {
    scene.remove(invertedMesh);
    invertedMesh.material.dispose();
    invertedMesh = null;
  }
  if (!mesh) return;
  if (state.inverted) {
    mesh.material.side = THREE.FrontSide;
    invertedMesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({
      color: 0xff3344,
      side: THREE.BackSide,
      polygonOffset: true,
      polygonOffsetFactor: 1,
      polygonOffsetUnits: 1,
    }));
    invertedMesh.renderOrder = 1;
    scene.add(invertedMesh);
  } else {
    mesh.material.side = THREE.DoubleSide;
  }
}

export function setInverted(enabled) {
  state.inverted = enabled;
  applyInverted();
}

export function getBodyCount() {
  return bodyCount;
}

// ---- measurement tool ----
function markerSize() {
  const r = (geometry && geometry.boundingSphere?.radius) || 10;
  return Math.max(0.3, r * 0.012);
}

function addMeasurePoint(point) {
  const radius = markerSize();
  const marker = new THREE.Mesh(
    new THREE.SphereGeometry(radius, 16, 12),
    new THREE.MeshBasicMaterial({ color: 0xfde047, depthTest: false }),
  );
  marker.position.copy(point);
  marker.renderOrder = 4;

  if (!measurePending) {
    const grp = new THREE.Group();
    grp.add(marker);
    measureRoot.add(grp);
    measurePending = { a: point, group: grp };
    return;
  }

  // Second click finalises the measurement.
  measurePending.group.add(marker);
  const a = measurePending.a, b = point;
  const lineGeom = new THREE.BufferGeometry().setFromPoints([a, b]);
  const line = new THREE.Line(
    lineGeom,
    new THREE.LineBasicMaterial({ color: 0xfde047, depthTest: false }),
  );
  line.renderOrder = 4;
  measurePending.group.add(line);

  const distance = a.distanceTo(b);
  measurements.push({
    a: { x: a.x, y: a.y, z: a.z },
    b: { x: b.x, y: b.y, z: b.z },
    distance_mm: distance,
    group: measurePending.group,
  });
  measurePending = null;
  if (window.__printprepOnMeasure) window.__printprepOnMeasure();
}

export function setMeasureMode(enabled) {
  measureMode = !!enabled;
  if (controls) controls.enabled = !measureMode || true; // keep orbit working alongside
  document.body.style.cursor = measureMode ? "crosshair" : "";
}

export function clearMeasurements() {
  for (const m of measurements) {
    measureRoot.remove(m.group);
    m.group.traverse((o) => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); });
  }
  if (measurePending) {
    measureRoot.remove(measurePending.group);
    measurePending.group.traverse((o) => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); });
    measurePending = null;
  }
  measurements = [];
  if (window.__printprepOnMeasure) window.__printprepOnMeasure();
}

export function getMeasurements() {
  return measurements.map((m, i) => ({
    index: i + 1, distance_mm: m.distance_mm,
  }));
}

// ---- cross-section (clipping plane) ----
function _axisNormal(axis, flip) {
  const v = new THREE.Vector3(
    axis === "x" ? 1 : 0,
    axis === "y" ? 1 : 0,
    axis === "z" ? 1 : 0,
  );
  // Plane equation in three.js: n.x + constant = 0; clip where n.x + constant > 0.
  // To keep the "low" side (e.g. z <= position): normal = (0,0,1), constant = -position.
  // To keep the "high" side: flip the normal.
  return flip ? v : v.multiplyScalar(-1);
}

function _applyClippingToMaterials() {
  const planes = clipPlane ? [clipPlane] : [];
  if (mesh) mesh.material.clippingPlanes = planes;
  if (openEdges) openEdges.material.clippingPlanes = planes;
  if (invertedMesh) invertedMesh.material.clippingPlanes = planes;
}

export function setClipping(enabled, axis, position, flip) {
  if (axis) clipAxis = axis;
  if (typeof position === "number") clipPosition = position;
  if (typeof flip === "boolean") clipFlip = flip;
  if (!enabled) {
    clipPlane = null;
  } else {
    const n = _axisNormal(clipAxis, clipFlip);
    // n.x + constant = 0 at the plane; for axis=z, n=(0,0,-1)+flip flips sign.
    // We want plane at coord=position. With normal (0,0,-1): -z + c = 0 -> z = c -> constant = position.
    // With normal (0,0,+1) (flipped): z + c = 0 -> z = -c -> constant = -position.
    const constant = clipFlip ? -clipPosition : clipPosition;
    clipPlane = new THREE.Plane(n, constant);
  }
  _applyClippingToMaterials();
}

export function getModelBounds() {
  if (!geometry) return null;
  const b = geometry.boundingBox || geometry.computeBoundingBox() || geometry.boundingBox;
  return {
    min: { x: b.min.x, y: b.min.y, z: b.min.z },
    max: { x: b.max.x, y: b.max.y, z: b.max.z },
  };
}
