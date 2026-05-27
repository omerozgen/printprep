"""Merge a multi-body mesh into a single piece.

Two strategies, picked automatically:
  - boolean union (needs the `manifold3d` engine and every body to be a closed
    volume) -> truly fuses overlapping/touching solids into one watertight body.
  - concatenate + weld fallback -> combines all bodies into one mesh/file when a
    real union isn't possible (e.g. a non-watertight body). The slicer will still
    fuse overlapping geometry at slice time.
"""

from dataclasses import dataclass

import trimesh


@dataclass
class MergeReport:
    method: str  # "boolean" or "concatenate"
    bodies_before: int
    bodies_after: int
    watertight_after: bool
    volume_after: float
    note: str


def merge_to_single(mesh: trimesh.Trimesh):
    """Return (merged_mesh, MergeReport)."""
    parts = mesh.split(only_watertight=False)
    if len(parts) <= 1:
        parts = [mesh]
    bodies_before = len(parts)

    # Preferred: true boolean union (requires all bodies to be closed volumes).
    if bodies_before > 1 and all(p.is_volume for p in parts):
        try:
            merged = trimesh.boolean.union(parts)
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
