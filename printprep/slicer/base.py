"""Slicer profile model and shared suggestion heuristics."""

import json
from dataclasses import asdict, dataclass
from typing import Optional

from printprep.config import defaults
from printprep.config.presets import get_material
from printprep.core.analyzer import AnalysisResult
from printprep.slicer.printer import PrinterSpec


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
    nozzle_diameter_mm: float = defaults.NOZZLE_DIAMETER_MM
    printer: Optional[str] = None  # printer name when a PrinterSpec was used


class BaseSlicer:
    """Base profile generator. Subclasses set name and support_style."""

    name = "base"
    support_style = "normal"

    def _wall_count(self, result: AnalysisResult, nozzle_mm: float) -> int:
        if result.min_wall_mm is None:
            return defaults.DEFAULT_WALL_COUNT
        fits = int(result.min_wall_mm / max(0.1, nozzle_mm))
        return max(2, min(4, fits))

    def _brim(self, result: AnalysisResult) -> bool:
        dx, dy, dz = result.dimensions_mm
        footprint = min(dx, dy)
        if footprint <= 0:
            return False
        if footprint < defaults.BRIM_MIN_FOOTPRINT_MM:
            return True
        return (dz / footprint) > defaults.BRIM_ASPECT_RATIO

    def _print_speed(self, preset, layer_height: float, line_width: float,
                     printer: Optional[PrinterSpec]) -> int:
        """Recommended speed from the material's max flow, clamped to a sane
        range and (when known) to the printer's mechanical max speed."""
        flow_limited = preset.max_volumetric_speed_mm3s / (layer_height * line_width)
        ceiling = defaults.MAX_PRINT_SPEED_MMS
        if printer is not None and printer.max_print_speed_mms:
            ceiling = min(ceiling, printer.max_print_speed_mms)
        return int(round(max(defaults.MIN_PRINT_SPEED_MMS, min(ceiling, flow_limited))))

    def build_profile(self, result: AnalysisResult, material: str,
                      printer: Optional[PrinterSpec] = None) -> SlicerProfile:
        return self.build_profile_from_preset(result, get_material(material), printer)

    def build_profile_from_preset(self, result: AnalysisResult, preset,
                                  printer: Optional[PrinterSpec] = None) -> SlicerProfile:
        supports = result.overhang_face_count > 0
        layer_height = defaults.DEFAULT_LAYER_HEIGHT_MM

        # Real nozzle diameter (from the printer) sharpens wall count + line width.
        nozzle = printer.nozzle_diameter_mm if printer else defaults.NOZZLE_DIAMETER_MM
        line_width = round(nozzle * 1.05, 3)  # ~5% over nozzle, the common default

        # OrcaSlicer keeps retraction at the machine level; prefer the printer's
        # real value when we have it, otherwise fall back to the material preset.
        retraction = preset.retraction_mm
        retraction_speed = preset.retraction_speed_mms
        if printer is not None:
            if printer.retraction_mm is not None:
                retraction = printer.retraction_mm
            if printer.retraction_speed_mms is not None:
                retraction_speed = printer.retraction_speed_mms

        return SlicerProfile(
            slicer=self.name,
            material=preset.name,
            layer_height_mm=layer_height,
            infill_pct=defaults.DEFAULT_INFILL_PCT,
            wall_count=self._wall_count(result, nozzle),
            supports=supports,
            support_style=self.support_style if supports else "none",
            brim=self._brim(result),
            nozzle_temp_c=preset.nozzle_temp_c,
            bed_temp_c=preset.bed_temp_c,
            print_speed_mms=self._print_speed(preset, layer_height, line_width, printer),
            max_volumetric_speed_mm3s=preset.max_volumetric_speed_mm3s,
            retraction_mm=retraction,
            retraction_speed_mms=retraction_speed,
            nozzle_diameter_mm=nozzle,
            printer=printer.name if printer else None,
        )

    def to_json(self, profile: SlicerProfile) -> str:
        return json.dumps(asdict(profile), indent=2)


def bed_fit_warning(result: AnalysisResult, printer: Optional[PrinterSpec],
                    margin_mm: float = 0.0) -> Optional[dict]:
    """Return an issue dict if the model footprint won't fit the printer bed.

    Only meaningful when a real printer is known. Checks both orientations
    (the part can be rotated 90° about Z). None when it fits or no printer.
    """
    if printer is None:
        return None
    dx, dy, dz = result.dimensions_mm
    msgs = []
    if not printer.fits(dx, dy, margin_mm):
        msgs.append(f"footprint {dx:.0f}×{dy:.0f}mm exceeds bed "
                    f"{printer.bed_x_mm:.0f}×{printer.bed_y_mm:.0f}mm")
    if printer.bed_z_mm and dz > printer.bed_z_mm:
        msgs.append(f"height {dz:.0f}mm exceeds {printer.bed_z_mm:.0f}mm")
    if not msgs:
        return None
    return {
        "text": f"Model may not fit {printer.name}: " + "; ".join(msgs) + ".",
        "kind": "bed_fit",
    }
