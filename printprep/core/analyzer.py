"""Geometry analysis: produce an AnalysisResult that flows into suggestions."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import trimesh

from printprep.config import defaults
from printprep.core import validator


@dataclass
class AnalysisResult:
    path: str
    volume_mm3: float
    surface_area_mm2: float
    dimensions_mm: Tuple[float, float, float]
    bounds: List[List[float]]
    is_watertight: bool
    is_winding_consistent: bool
    is_volume: bool
    body_count: int
    face_count: int
    vertex_count: int
    degenerate_faces: int
    duplicate_faces: int
    overhang_face_count: int
    overhang_area_fraction: float
    steepest_overhang_deg: float
    min_wall_mm: Optional[float]
    issues: List[str] = field(default_factory=list)


def analyze(mesh: trimesh.Trimesh, path: str = "",
            overhang_threshold_deg: float = defaults.OVERHANG_THRESHOLD_DEG,
            max_ray_samples: int = defaults.MAX_RAY_SAMPLES) -> AnalysisResult:
    """Run the full analysis pipeline on a loaded mesh."""
    overhang_count, overhang_frac, steepest = validator.overhang_stats(mesh, overhang_threshold_deg)

    result = AnalysisResult(
        path=path,
        volume_mm3=abs(float(mesh.volume)),
        surface_area_mm2=float(mesh.area),
        dimensions_mm=tuple(round(float(x), 3) for x in mesh.extents),
        bounds=mesh.bounds.tolist(),
        is_watertight=bool(mesh.is_watertight),
        is_winding_consistent=bool(mesh.is_winding_consistent),
        is_volume=bool(mesh.is_volume),
        body_count=int(mesh.body_count),
        face_count=int(len(mesh.faces)),
        vertex_count=int(len(mesh.vertices)),
        degenerate_faces=validator.degenerate_count(mesh),
        duplicate_faces=validator.duplicate_face_count(mesh),
        overhang_face_count=overhang_count,
        overhang_area_fraction=overhang_frac,
        steepest_overhang_deg=steepest,
        min_wall_mm=validator.estimate_min_wall(mesh, max_samples=max_ray_samples),
    )
    result.issues = validator.collect_issues(result)
    return result
