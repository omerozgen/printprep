"""Merge a multi-body mesh into a single piece.

Two strategies, picked automatically:
  - boolean union (needs the `manifold3d` engine and every body to be a closed
    volume) -> truly fuses overlapping/touching solids into one watertight body.
  - concatenate + weld fallback -> combines all bodies into one mesh/file when a
    real union isn't possible (e.g. a non-watertight body). The slicer will still
    fuse overlapping geometry at slice time.
"""

from dataclasses import dataclass
from typing import List, Optional

import trimesh

from printprep.core.repair import apply_meshfix, geometry_preserved, meshfix_available


@dataclass
class MergeReport:
    method: str  # "boolean" or "concatenate"
    bodies_before: int
    bodies_after: int
    watertight_after: bool
    volume_after: float
    note: str


def _as_volumes(parts: List[trimesh.Trimesh]) -> Optional[List[trimesh.Trimesh]]:
    """Return a list where every part is a closed volume, repairing non-volume
    bodies with guarded pymeshfix. Returns None if any body can't be made a
    volume without mangling it (so the caller falls back to concatenation)."""
    out = []
    for p in parts:
        if p.is_volume:
            out.append(p)
            continue
        if not meshfix_available():
            return None
        try:
            fixed = apply_meshfix(p)
        except Exception:
            return None
        if fixed.is_volume and geometry_preserved(p, fixed):
            out.append(fixed)
        else:
            return None
    return out


def merge_to_single(mesh: trimesh.Trimesh):
    """Return (merged_mesh, MergeReport)."""
    parts = mesh.split(only_watertight=False)
    if len(parts) <= 1:
        parts = [mesh]
    bodies_before = len(parts)

    # Preferred: true boolean union. Every body must be a closed volume; try to
    # repair non-volume bodies first (guarded, so thin shells are left alone).
    union_parts = _as_volumes(parts) if bodies_before > 1 else None
    if union_parts is not None:
        try:
            merged = trimesh.boolean.union(union_parts)
            merged.merge_vertices()
            return merged, MergeReport(
                method="boolean",
                bodies_before=bodies_before,
                bodies_after=int(merged.body_count),
                watertight_after=bool(merged.is_watertight),
                volume_after=abs(float(merged.volume)),
                note="Bodies fused with a boolean union.",
            )
        except Exception as exc:  # engine missing or non-manifold input
            note = f"Boolean union unavailable ({exc}); combined into one file instead."
    else:
        note = ("Some bodies are not closed volumes; combined into one file. "
                "Overlapping parts still print as one piece.")

    # Fallback: concatenate everything into a single mesh and weld shared verts.
    merged = trimesh.util.concatenate(parts) if bodies_before > 1 else mesh.copy()
    merged.merge_vertices()
    return merged, MergeReport(
        method="concatenate",
        bodies_before=bodies_before,
        bodies_after=int(merged.body_count),
        watertight_after=bool(merged.is_watertight),
        volume_after=abs(float(merged.volume)),
        note=note,
    )
