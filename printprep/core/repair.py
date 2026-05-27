"""Mesh repair operations with a fixed, correct ordering."""

from dataclasses import dataclass
from typing import Tuple

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


def _boundary_edge_count(mesh: trimesh.Trimesh) -> int:
    """Number of edges used by only one face (open/boundary edges)."""
    if len(mesh.faces) == 0:
        return 0
    return int(len(grouping.group_rows(mesh.edges_sorted, require_count=1)))


def repair_mesh(mesh: trimesh.Trimesh) -> Tuple[trimesh.Trimesh, RepairReport]:
    """Repair a mesh in place and return (mesh, report).

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

    # Iterative hole filling: stop when watertight or a pass makes no progress.
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

    repair.fix_normals(mesh)  # winding + outward direction, last

    report = RepairReport(
        merged_vertices=merged_vertices,
        removed_degenerate=removed_degenerate,
        removed_duplicate=removed_duplicate,
        holes_filled=holes_filled,
        watertight_before=watertight_before,
        watertight_after=bool(mesh.is_watertight),
        volume_after=abs(float(mesh.volume)),
        open_edges_after=_boundary_edge_count(mesh),
    )
    return mesh, report
