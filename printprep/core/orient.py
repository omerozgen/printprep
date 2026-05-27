"""Suggest the best print orientation (minimize support-needing overhangs).

Candidate "down" directions are the convex-hull facet normals — the set of
flat faces the object can physically rest on. Each candidate is scored by the
support-needing overhang area fraction; the lowest wins (current orientation is
included as a baseline so we never suggest a worse pose).
"""

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import trimesh

from printprep.core.validator import overhang_stats


@dataclass
class OrientationResult:
    rotation_matrix: List[List[float]]
    euler_deg: Tuple[float, float, float]
    overhang_before: float
    overhang_after: float
    improved: bool


def _drop_to_bed(mesh: trimesh.Trimesh) -> None:
    """Translate so the mesh is centered in XY and rests on z = 0."""
    center = mesh.bounds.mean(axis=0)
    mesh.apply_translation([-center[0], -center[1], -mesh.bounds[0, 2]])


def suggest_orientation(mesh: trimesh.Trimesh, max_candidates: int = 64):
    """Return (oriented_mesh, OrientationResult).

    oriented_mesh is a transformed copy resting on the bed in the suggested pose.
    """
    before = overhang_stats(mesh)[1]

    best_frac = before
    best_T = np.eye(4)

    try:
        hull = mesh.convex_hull
        normals = hull.face_normals
        areas = hull.area_faces
    except Exception:
        normals = np.empty((0, 3))
        areas = np.empty((0,))

    seen = set()
    for i in np.argsort(-areas):  # largest resting facets first
        n = normals[i]
        key = tuple(np.round(n, 2))
        if key in seen:
            continue
        seen.add(key)
        if len(seen) > max_candidates:
            break

        T = trimesh.geometry.align_vectors(n, [0.0, 0.0, -1.0])
        candidate = mesh.copy()
        candidate.apply_transform(T)
        frac = overhang_stats(candidate)[1]
        if frac < best_frac - 1e-4:
            best_frac = frac
            best_T = T

    oriented = mesh.copy()
    oriented.apply_transform(best_T)
    _drop_to_bed(oriented)

    euler = trimesh.transformations.euler_from_matrix(best_T)
    result = OrientationResult(
        rotation_matrix=best_T.tolist(),
        euler_deg=tuple(round(float(np.degrees(a)), 1) for a in euler),
        overhang_before=round(before, 4),
        overhang_after=round(best_frac, 4),
        improved=bool(best_frac < before - 1e-4),
    )
    return oriented, result
