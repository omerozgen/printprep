"""Rough estimate of filament use, print time and (optionally) cost.

These are heuristic estimates derived from the analysis result + the chosen
slicer profile — NOT a full toolpath simulation. Expected accuracy is
roughly ±10–15% for filament weight (the geometry math is concrete) and
±25–35% for print time (efficiency varies a lot with model shape).
"""

import math
from dataclasses import dataclass
from typing import Optional

from printprep.config import defaults
from printprep.config.presets import MaterialPreset
from printprep.core.analyzer import AnalysisResult
from printprep.slicer.base import SlicerProfile


# Toolpath efficiency: ratio of actual extrusion time to "length / speed".
# Real slicers see 0.45–0.7 depending on model. 0.6 is a sober middle.
_EFFICIENCY = 0.6
# Top + bottom solid layers slicers add regardless of infill %.
_TOP_BOTTOM_LAYERS = 4
# Heat-up / level / start-end overhead in seconds.
_OVERHEAD_S = 180


@dataclass
class PrintEstimate:
    filament_volume_mm3: float  # plastic actually extruded
    filament_length_mm: float
    filament_weight_g: float
    print_time_min: float
    cost: Optional[float] = None
    currency: Optional[str] = None
    # Breakdown so the user can sanity-check the estimate.
    shell_volume_mm3: float = 0.0
    infill_volume_mm3: float = 0.0
    top_bottom_volume_mm3: float = 0.0


def estimate_from_active(result: AnalysisResult, printer=None, process=None,
                         filament=None, supports: Optional[bool] = None,
                         currency: str = "", price_per_kg: Optional[float] = None):
    """Estimate a print job from the user's *real* slicer settings.

    `printer`/`process`/`filament` are the dataclasses from
    discover.detect_active_config(); any may be None (gaps fall back to sane
    defaults). Cost is auto-filled from the filament's cost-per-kg when known.

    Returns (PrintEstimate, SlicerProfile) — the profile reflects the actual
    settings used, so callers can show them.
    """
    from printprep.config.presets import MaterialPreset, get_material

    base = get_material("pla")
    density = filament.density_g_cm3 if (filament and filament.density_g_cm3) else base.density_g_cm3
    max_vol = (filament.max_volumetric_speed_mm3s
               if (filament and filament.max_volumetric_speed_mm3s) else base.max_volumetric_speed_mm3s)
    material = MaterialPreset(
        name=(filament.name if filament else "filament"),
        nozzle_temp_c=(filament.nozzle_temp_c if (filament and filament.nozzle_temp_c) else base.nozzle_temp_c),
        bed_temp_c=(filament.bed_temp_c if (filament and filament.bed_temp_c) else base.bed_temp_c),
        max_volumetric_speed_mm3s=max_vol,
        retraction_mm=(printer.retraction_mm if (printer and printer.retraction_mm is not None) else base.retraction_mm),
        retraction_speed_mms=(printer.retraction_speed_mms if (printer and printer.retraction_speed_mms is not None) else base.retraction_speed_mms),
        density_g_cm3=density,
    )

    nozzle = printer.nozzle_diameter_mm if printer else defaults.NOZZLE_DIAMETER_MM
    layer = process.layer_height_mm if (process and process.layer_height_mm) else defaults.DEFAULT_LAYER_HEIGHT_MM
    infill = process.infill_pct if (process and process.infill_pct is not None) else defaults.DEFAULT_INFILL_PCT
    walls = process.wall_count if (process and process.wall_count) else defaults.DEFAULT_WALL_COUNT
    speed = process.print_speed_mms if (process and process.print_speed_mms) else None
    if speed is None:
        speed = printer.max_print_speed_mms if (printer and printer.max_print_speed_mms) else 60
    if supports is None:
        supports = result.overhang_face_count > 0

    profile = SlicerProfile(
        slicer="active", material=material.name, layer_height_mm=layer,
        infill_pct=infill, wall_count=walls, supports=supports,
        support_style="normal" if supports else "none", brim=False,
        nozzle_temp_c=material.nozzle_temp_c, bed_temp_c=material.bed_temp_c,
        print_speed_mms=speed, max_volumetric_speed_mm3s=material.max_volumetric_speed_mm3s,
        retraction_mm=material.retraction_mm, retraction_speed_mms=material.retraction_speed_mms,
        nozzle_diameter_mm=nozzle, printer=(printer.name if printer else None),
    )
    # Manually-entered price wins; the filament profile's cost is only a fallback.
    price = price_per_kg if (price_per_kg and price_per_kg > 0) else \
        (filament.cost_per_kg if (filament and filament.cost_per_kg) else None)
    est = estimate_print_job(result, profile, material, price_per_kg=price, currency=currency)
    return est, profile


def estimate_print_job(result: AnalysisResult, profile: SlicerProfile,
                       material: MaterialPreset,
                       price_per_kg: Optional[float] = None,
                       currency: str = "",
                       filament_diameter_mm: float = 1.75,
                       line_width_mm: Optional[float] = None) -> PrintEstimate:
    """Estimate filament use and print time from analysis + slicer profile."""
    if line_width_mm is not None:
        line_w = line_width_mm
    else:
        # Derive from the profile's nozzle when known (real printer), else default.
        nozzle = getattr(profile, "nozzle_diameter_mm", defaults.NOZZLE_DIAMETER_MM)
        line_w = round(nozzle * 1.05, 3)
    layer = profile.layer_height_mm
    walls = max(1, profile.wall_count)
    infill_pct = max(0.0, min(100.0, float(profile.infill_pct))) / 100.0

    volume = max(0.0, result.volume_mm3)
    surface_area = max(0.0, result.surface_area_mm2)
    dx, dy, _dz = result.dimensions_mm
    footprint = max(0.0, float(dx) * float(dy))  # bounding-box approximation

    # Walls/shell: outer perimeters around the whole surface.
    shell_vol = surface_area * walls * line_w
    # Solid top + bottom infill layers.
    tb_vol = footprint * layer * _TOP_BOTTOM_LAYERS * 2.0
    # Remaining interior + infill density.
    interior = max(0.0, volume - shell_vol - tb_vol)
    infill_vol = interior * infill_pct

    extruded = shell_vol + tb_vol + infill_vol
    # Tiny slack for shell overlap, then cap at model volume (can't extrude more plastic
    # than the model takes up).
    extruded = min(extruded, volume * 1.1) if volume > 0 else extruded

    # Support adds ~5–15% by area when enabled; use a flat 10% surcharge.
    if profile.supports:
        extruded *= 1.10

    # Filament length on the spool (round 1.75mm stock by default).
    cross_section = math.pi * (filament_diameter_mm / 2.0) ** 2
    filament_mm = extruded / cross_section if cross_section > 0 else 0.0

    # Weight: density is g/cm³, volume in mm³ -> divide by 1000 to get cm³.
    weight_g = (extruded / 1000.0) * material.density_g_cm3

    # Print time: total toolpath length / speed / efficiency, plus fixed overhead.
    speed = max(1, profile.print_speed_mms)
    toolpath_mm = extruded / max(1e-6, layer * line_w)
    print_time_s = toolpath_mm / speed / _EFFICIENCY + _OVERHEAD_S

    cost = None
    if price_per_kg is not None and price_per_kg > 0:
        cost = round((weight_g / 1000.0) * price_per_kg, 2)

    return PrintEstimate(
        filament_volume_mm3=round(extruded, 1),
        filament_length_mm=round(filament_mm, 1),
        filament_weight_g=round(weight_g, 2),
        print_time_min=round(print_time_s / 60.0, 1),
        cost=cost,
        currency=currency or None,
        shell_volume_mm3=round(shell_vol, 1),
        infill_volume_mm3=round(infill_vol, 1),
        top_bottom_volume_mm3=round(tb_vol, 1),
    )
