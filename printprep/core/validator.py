"""Problem detection: overhangs, degenerate/duplicate faces, thin walls."""

import math

import numpy as np
import trimesh

from printprep.config import defaults
from printprep.core.mesh import ray_available


def overhang_mask(mesh: trimesh.Trimesh, threshold_deg: float = defaults.OVERHANG_THRESHOLD_DEG) -> np.ndarray:
    """Boolean mask of faces that need support.

    Build direction is +Z. A downward-facing face needs support when it tilts
    more than `threshold_deg` away from vertical, i.e. nz < -sin(threshold).
    Faces resting on the build plate (the model's footprint) are excluded —
    they print on the bed and need no support.
    """
    nz = mesh.face_normals[:, 2]
    downward = nz < -math.sin(math.radians(threshold_deg))

    bed_z = mesh.bounds[0, 2]
    height = mesh.extents[2]
    tol = 1e-6 + 1e-3 * height
    elevated = mesh.triangles_center[:, 2] > bed_z + tol
    return downward & elevated


def overhang_stats(mesh: trimesh.Trimesh, threshold_deg: float = defaults.OVERHANG_THRESHOLD_DEG):
    """Return (face_count, area_fraction, steepest_overhang_deg)."""
    mask = overhang_mask(mesh, threshold_deg)
    count = int(mask.sum())
    if count == 0:
        return 0, 0.0, 0.0
    area_fraction = float(mesh.area_faces[mask].sum() / mesh.area)
    # steepest = face pointing most straight down -> largest -nz -> angle from horizontal
    steepest_nz = float(mesh.face_normals[mask, 2].min())  # most negative
    steepest_deg = math.degrees(math.asin(min(1.0, -steepest_nz)))
    return count, area_fraction, steepest_deg


def degenerate_count(mesh: trimesh.Trimesh) -> int:
    """Number of zero-area / collinear faces."""
    return int((~mesh.nondegenerate_faces()).sum())


def duplicate_face_count(mesh: trimesh.Trimesh) -> int:
    """Number of duplicate faces (total minus unique)."""
    return int((~mesh.unique_faces()).sum())


def estimate_wall_thickness(mesh: trimesh.Trimesh, max_samples: int = defaults.MAX_RAY_SAMPLES,
                            eps: float = 1e-4, seed: int = defaults.THIN_WALL_SEED):
    """Distribution of wall thicknesses (mm) via inward ray casting.

    Returns a dict with min/p5/p50/max/samples, or None when ray casting is
    unavailable or no hits are found. Deterministic via fixed seed.
    """
    if not ray_available(mesh):
        return None
    centers = mesh.triangles_center
    normals = mesh.face_normals
    n_faces = len(centers)
    if n_faces == 0:
        return None
    if n_faces > max_samples:
        idx = np.random.default_rng(seed).choice(n_faces, max_samples, replace=False)
    else:
        idx = np.arange(n_faces)
    centers = centers[idx]
    normals = normals[idx]
    origins = centers - normals * eps
    directions = -normals
    try:
        locations, index_ray, _ = mesh.ray.intersects_location(
            ray_origins=origins, ray_directions=directions, multiple_hits=True
        )
    except Exception:
        return None
    if len(locations) == 0:
        return None
    dist = np.linalg.norm(locations - origins[index_ray], axis=1)
    dist = dist[dist > eps * 10]
    if len(dist) == 0:
        return None
    return {
        "samples": int(len(dist)),
        "min_mm": float(np.min(dist)),
        "p5_mm": float(np.percentile(dist, 5)),
        "p50_mm": float(np.percentile(dist, 50)),
        "max_mm": float(np.max(dist)),
    }


def estimate_min_wall(mesh: trimesh.Trimesh, **kw):
    """Backwards-compat: 5th-percentile wall thickness, or None."""
    stats = estimate_wall_thickness(mesh, **kw)
    return stats["p5_mm"] if stats else None


def non_manifold_edge_count(mesh: trimesh.Trimesh) -> int:
    """Edges shared by 3+ faces (non-manifold). 0 for a clean mesh."""
    if len(mesh.faces) == 0:
        return 0
    _, counts = np.unique(mesh.edges_sorted, axis=0, return_counts=True)
    return int((counts > 2).sum())


def check_self_intersection(mesh: trimesh.Trimesh):
    """Return number of self-intersecting faces, or None if pymeshlab is absent.

    pymeshlab is an optional `[analyze]` extra because the wheel is heavy.
    """
    try:
        import pymeshlab
    except Exception:
        return None
    try:
        ms = pymeshlab.MeshSet()
        ms.add_mesh(pymeshlab.Mesh(np.asarray(mesh.vertices, dtype=np.float64),
                                   np.asarray(mesh.faces, dtype=np.int32)))
        # filter name varies a bit by version — try the common ones
        for fname in ("compute_selection_by_self_intersections_per_face",
                      "select_self_intersecting_faces"):
            try:
                ms.apply_filter(fname)
                break
            except Exception:
                continue
        else:
            return None
        face_mask = ms.current_mesh().face_selection_array()
        return int(np.sum(face_mask))
    except Exception:
        return None


def detect_holes(mesh: trimesh.Trimesh):
    """Return a list of distinct holes (open boundary loops) with perimeters.

    Each entry: {"perimeter_mm": float, "edge_count": int}. Sorted by perimeter
    descending. Empty for a watertight mesh.
    """
    if len(mesh.faces) == 0:
        return []
    unique_edges, counts = np.unique(mesh.edges_sorted, axis=0, return_counts=True)
    boundary_edges = unique_edges[counts == 1]  # (B, 2) vertex-index pairs
    if len(boundary_edges) == 0:
        return []

    verts = np.unique(boundary_edges.ravel())
    index_of = {int(v): i for i, v in enumerate(verts)}
    parent = list(range(len(verts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in boundary_edges:
        a, b = find(index_of[int(u)]), find(index_of[int(v)])
        if a != b:
            parent[a] = b

    components: dict = {}
    for idx, (u, _) in enumerate(boundary_edges):
        c = find(index_of[int(u)])
        components.setdefault(c, []).append(idx)

    holes = []
    for edge_idx_list in components.values():
        sub = boundary_edges[edge_idx_list]
        v0 = mesh.vertices[sub[:, 0]]
        v1 = mesh.vertices[sub[:, 1]]
        perim = float(np.linalg.norm(v0 - v1, axis=1).sum())
        holes.append({"perimeter_mm": round(perim, 3), "edge_count": int(len(edge_idx_list))})

    holes.sort(key=lambda h: -h["perimeter_mm"])
    return holes


def collect_issues(result, cfg=defaults) -> list:
    """Build structured warnings from an analysis result (duck-typed).

    Each issue is {text, kind, locate?} so the web UI can wire a click to the
    matching 3D highlight. `kind` is one of: holes, inverted, bodies, degenerate,
    duplicate, overhang, thin, non_manifold, self_intersection, ray_unavailable.
    """
    issues = []
    if not result.is_watertight:
        n = len(result.holes) if result.holes else None
        biggest = max((h["perimeter_mm"] for h in result.holes), default=0) if result.holes else 0
        if n:
            issues.append({
                "text": f"Model is not watertight: {n} hole(s), largest perimeter ~{biggest:.1f}mm.",
                "kind": "holes",
            })
        else:
            issues.append({"text": "Model is not watertight (no isolated holes — likely non-manifold edges).",
                           "kind": "non_manifold"})
    if not result.is_winding_consistent:
        issues.append({"text": "Inconsistent face winding / inverted normals detected.",
                       "kind": "inverted"})
    if result.body_count > 1:
        issues.append({"text": f"Model has {result.body_count} separate bodies.",
                       "kind": "bodies"})
    if result.degenerate_faces > 0:
        issues.append({"text": f"{result.degenerate_faces} degenerate (zero-area) face(s).",
                       "kind": "degenerate"})
    if result.duplicate_faces > 0:
        issues.append({"text": f"{result.duplicate_faces} duplicate face(s).",
                       "kind": "duplicate"})
    if result.overhang_face_count > 0:
        issues.append({
            "text": (f"Overhang(s) up to {result.steepest_overhang_deg:.0f}° "
                     f"({result.overhang_area_fraction * 100:.1f}% of surface) — supports recommended."),
            "kind": "overhang",
        })
    if result.wall_thickness is None:
        issues.append({"text": "Thin-wall analysis unavailable (install rtree or embree for ray casting).",
                       "kind": "ray_unavailable"})
    else:
        wt = result.wall_thickness
        if wt["p5_mm"] < cfg.MIN_WALL_MM:
            issues.append({
                "text": (f"Thin wall: min {wt['min_mm']:.2f}mm, median {wt['p50_mm']:.2f}mm "
                         f"(recommended minimum {cfg.MIN_WALL_MM}mm)."),
                "kind": "thin",
            })
    if result.non_manifold_edges > 0:
        issues.append({
            "text": (f"{result.non_manifold_edges} non-manifold edge(s) "
                     "(edge shared by 3+ faces) — slicer may misbehave."),
            "kind": "non_manifold",
        })
    if result.self_intersecting is True:
        n = result.self_intersection_count
        issues.append({
            "text": ("Self-intersecting faces detected"
                     + (f" ({n})." if n is not None else ".")),
            "kind": "self_intersection",
        })
    return issues
