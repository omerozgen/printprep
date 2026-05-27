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


def estimate_min_wall(mesh: trimesh.Trimesh, max_samples: int = defaults.MAX_RAY_SAMPLES,
                      eps: float = 1e-4, seed: int = defaults.THIN_WALL_SEED):
    """Estimate the minimum wall thickness (mm) via inward ray casting.

    Returns None when ray casting is unavailable or no hits are found. Uses the
    5th percentile of measured thicknesses (not the raw min) to resist a single
    numerically-degenerate ray. Deterministic via fixed seed.
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
    origins = centers - normals * eps  # start just inside the surface
    directions = -normals  # cast into the solid

    try:
        locations, index_ray, _ = mesh.ray.intersects_location(
            ray_origins=origins, ray_directions=directions, multiple_hits=True
        )
    except Exception:
        return None

    if len(locations) == 0:
        return None

    dist = np.linalg.norm(locations - origins[index_ray], axis=1)
    dist = dist[dist > eps * 10]  # drop residual self-hits
    if len(dist) == 0:
        return None

    return float(np.percentile(dist, 5))


def collect_issues(result, cfg=defaults) -> list:
    """Build human-readable warnings from an analysis result (duck-typed)."""
    issues = []
    if not result.is_watertight:
        issues.append("Model is not watertight (open mesh / holes) — fix before slicing.")
    if not result.is_winding_consistent:
        issues.append("Inconsistent face winding / inverted normals detected.")
    if result.body_count > 1:
        issues.append(f"Model has {result.body_count} separate bodies.")
    if result.degenerate_faces > 0:
        issues.append(f"{result.degenerate_faces} degenerate (zero-area) face(s).")
    if result.duplicate_faces > 0:
        issues.append(f"{result.duplicate_faces} duplicate face(s).")
    if result.overhang_face_count > 0:
        issues.append(
            f"Overhang(s) up to {result.steepest_overhang_deg:.0f}° "
            f"({result.overhang_area_fraction * 100:.1f}% of surface) — supports recommended."
        )
    if result.min_wall_mm is None:
        issues.append("Thin-wall analysis unavailable (install rtree or embree for ray casting).")
    elif result.min_wall_mm < cfg.MIN_WALL_MM:
        issues.append(
            f"Thin wall ~{result.min_wall_mm:.2f}mm "
            f"(recommended minimum {cfg.MIN_WALL_MM}mm)."
        )
    return issues
