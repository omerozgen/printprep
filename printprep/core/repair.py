"""Mesh repair operations with a fixed, correct ordering."""

from dataclasses import dataclass
from typing import Tuple

import trimesh
import trimesh.repair as repair


@dataclass
class RepairReport:
    merged_vertices: int
    removed_degenerate: int
    removed_duplicate: int
    holes_filled: bool
    watertight_before: bool
    watertight_after: bool
    volume_after: float


def repair_mesh(mesh: trimesh.Trimesh) -> Tuple[trimesh.Trimesh, RepairReport]:
    """Repair a mesh in place and return (mesh, report).

    Order matters: fill holes BEFORE fixing normals, otherwise newly added fill
    faces can leave the solid inside-out (negative volume).
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

    holes_filled = bool(repair.fill_holes(mesh))
    repair.fix_normals(mesh)  # winding + outward direction, last

    report = RepairReport(
        merged_vertices=merged_vertices,
        removed_degenerate=removed_degenerate,
        removed_duplicate=removed_duplicate,
        holes_filled=holes_filled,
        watertight_before=watertight_before,
        watertight_after=bool(mesh.is_watertight),
        volume_after=abs(float(mesh.volume)),
    )
    return mesh, report
