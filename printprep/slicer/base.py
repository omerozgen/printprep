"""Slicer profile model and shared suggestion heuristics."""

import json
from dataclasses import asdict, dataclass

from printprep.config import defaults
from printprep.config.presets import get_material
from printprep.core.analyzer import AnalysisResult


@dataclass
class SlicerProfile:
    slicer: str
    material: str
    layer_height_mm: float
    infill_pct: int
    wall_count: int
    supports: bool
    support_style: str
    brim: bool
    nozzle_temp_c: int
    bed_temp_c: int
    print_speed_mms: int
    max_volumetric_speed_mm3s: float
    retraction_mm: float
    retraction_speed_mms: int


class BaseSlicer:
    """Base profile generator. Subclasses set name and support_style."""

    name = "base"
    support_style = "normal"

    def _wall_count(self, result: AnalysisResult) -> int:
        if result.min_wall_mm is None:
            return defaults.DEFAULT_WALL_COUNT
        fits = int(result.min_wall_mm / defaults.NOZZLE_DIAMETER_MM)
        return max(2, min(4, fits))

    def _brim(self, result: AnalysisResult) -> bool:
        dx, dy, dz = result.dimensions_mm
        footprint = min(dx, dy)
        if footprint <= 0:
            return False
        if footprint < defaults.BRIM_MIN_FOOTPRINT_MM:
            return True
        return (dz / footprint) > defaults.BRIM_ASPECT_RATIO

    def _print_speed(self, preset, layer_height: float) -> int:
        """Derive a recommended print speed from the material's max volumetric flow."""
        flow_limited = preset.max_volumetric_speed_mm3s / (layer_height * defaults.LINE_WIDTH_MM)
        return int(round(max(defaults.MIN_PRINT_SPEED_MMS,
                             min(defaults.MAX_PRINT_SPEED_MMS, flow_limited))))

    def build_profile(self, result: AnalysisResult, material: str) -> SlicerProfile:
        return self.build_profile_from_preset(result, get_material(material))

    def build_profile_from_preset(self, result: AnalysisResult, preset) -> SlicerProfile:
        supports = result.overhang_face_count > 0
        layer_height = defaults.DEFAULT_LAYER_HEIGHT_MM
        return SlicerProfile(
            slicer=self.name,
            material=preset.name,
            layer_height_mm=layer_height,
            infill_pct=defaults.DEFAULT_INFILL_PCT,
            wall_count=self._wall_count(result),
            supports=supports,
            support_style=self.support_style if supports else "none",
            brim=self._brim(result),
            nozzle_temp_c=preset.nozzle_temp_c,
            bed_temp_c=preset.bed_temp_c,
            print_speed_mms=self._print_speed(preset, layer_height),
            max_volumetric_speed_mm3s=preset.max_volumetric_speed_mm3s,
            retraction_mm=preset.retraction_mm,
            retraction_speed_mms=preset.retraction_speed_mms,
        )

    def to_json(self, profile: SlicerProfile) -> str:
        return json.dumps(asdict(profile), indent=2)
