"""Mesh repair operations with a fixed, correct ordering.

Standard repair uses trimesh (merge/degenerate/duplicate/fill_holes/fix_normals).
When that leaves the mesh non-watertight and `aggressive` is on, it escalates to
pymeshfix (optional `[repair]` extra) — but only accepts the result when a guard
confirms the geometry wasn't mangled (pymeshfix collapses thin shells, so e.g. a
ventilated tray would be rejected and the standard result kept).
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import trimesh
import trimesh.repair as repair
from trimesh import grouping


@dataclass
class RepairReport:
    merged_vertices: int
    removed_degenerate: int
    removed_duplicate: int
    holes_filled: bool
    watertight_before: bool
    watertight_after: bool
    volume_after: float
    open_edges_after: int  # remaining boundary edges (0 == watertight)
    method: str  # "standard" or "meshfix"


def _boundary_edge_count(mesh: trimesh.Trimesh) -> int:
    """Number of edges used by only one face (open/boundary edges)."""
    if len(mesh.faces) == 0:
        return 0
    return int(len(grouping.group_rows(mesh.edges_sorted, require_count=1)))


def meshfix_available() -> bool:
    try:
        import pymeshfix  # noqa: F401
        return True
    except Exception:
        return False


def apply_meshfix(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Run pymeshfix and return a new Trimesh (may differ substantially)."""
    import pymeshfix
    v, f = pymeshfix.clean_from_arrays(np.asarray(mesh.vertices, dtype=np.float64),
                                       np.asarray(mesh.faces, dtype=np.int32))
    return trimesh.Trimesh(vertices=v, faces=f, process=True)


def geometry_preserved(before: trimesh.Trimesh, after: trimesh.Trimesh) -> bool:
    """True if `after` keeps roughly the same shape as `before`.

    Guards against pymeshfix collapsing thin shells: rejects big bounding-box
    changes or a drastic face-count collapse.
    """
    if len(after.faces) == 0:
        return False
    eb = np.asarray(before.extents, dtype=float)
    ea = np.asarray(after.extents, dtype=float)
    if np.any(np.abs(ea - eb) > 0.10 * np.maximum(eb, 1e-9)):
        return False
    if len(after.faces) < 0.2 * max(1, len(before.faces)):
        return False
    return True


def repair_mesh(mesh: trimesh.Trimesh, aggressive: bool = True) -> Tuple[trimesh.Trimesh, RepairReport]:
    """Repair a mesh and return (mesh, report).

    Order matters: fill holes BEFORE fixing normals, otherwise newly added fill
    faces can leave the solid inside-out (negative volume). Hole-filling runs a
    few passes since one pass can expose new fillable boundaries.
    """
    watertight_before = bool(mesh.is_watertight)
    verts_before = len(mesh.vertices)

    mesh.merge_vertices()
    merged_vertices = verts_before - len(mesh.vertices)

    faces_before = len(mesh.faces)
    mesh.update_faces(mesh.nondegenerate_faces())
    removed_degenerate = faces_before - len(mesh.faces)

    faces_before = len(mesh.faces)
    mesh.update_faces(mesh.unique_faces())
    removed_duplicate = faces_before - len(mesh.faces)

    mesh.remove_unreferenced_vertices()

    holes_filled = False
    for _ in range(3):
        if mesh.is_watertight:
            break
        remaining = _boundary_edge_count(mesh)
        repair.fill_holes(mesh)
        if mesh.is_watertight or _boundary_edge_count(mesh) < remaining:
            holes_filled = True
        else:
            break

    repair.fix_normals(mesh)
    method = "standard"

    # Escalate to pymeshfix only if still open and the result is shape-preserving.
    if aggressive and not mesh.is_watertight and meshfix_available():
        try:
            candidate = apply_meshfix(mesh)
            if candidate.is_watertight and geometry_preserved(mesh, candidate):
                repair.fix_normals(candidate)
                mesh = candidate
                method = "meshfix"
        except Exception:
            pass

    report = RepairReport(
        merged_vertices=merged_vertices,
        removed_degenerate=removed_degenerate,
        removed_duplicate=removed_duplicate,
        holes_filled=holes_filled,
        watertight_before=watertight_before,
        watertight_after=bool(mesh.is_watertight),
        volume_after=abs(float(mesh.volume)),
        open_edges_after=_boundary_edge_count(mesh),
        method=method,
    )
    return mesh, report
