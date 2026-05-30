"""Parse process + filament settings from a slicer profile dict.

These let the print-job estimate reflect *your real slicing settings* (layer
height, infill, walls, speeds, filament density and cost) instead of
PrintPrep's generic defaults. Same OrcaSlicer-lineage JSON schema as the
machine profiles (OrcaSlicer / Creality Print / Anycubic Slicer).

The dicts passed in are expected to already have their `inherits` chain
merged (see discover._load_with_inherits).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProcessSettings:
    name: str
    layer_height_mm: Optional[float] = None
    infill_pct: Optional[int] = None
    wall_count: Optional[int] = None
    print_speed_mms: Optional[int] = None
    source: str = "slicer"


@dataclass
class FilamentSettings:
    name: str
    density_g_cm3: Optional[float] = None
    cost_per_kg: Optional[float] = None
    max_volumetric_speed_mm3s: Optional[float] = None
    nozzle_temp_c: Optional[int] = None
    bed_temp_c: Optional[int] = None
    source: str = "slicer"


def _first(value, default=None):
    if isinstance(value, (list, tuple)):
        return value[0] if value else default
    return value if value is not None else default


def _f(value):
    try:
        v = _first(value)
        if v is None or str(v).strip() == "":
            return None
        return float(str(v).replace("%", ""))
    except (ValueError, TypeError):
        return None


def _i(value):
    v = _f(value)
    return int(round(v)) if v is not None else None


def parse_process(data: dict) -> Optional[ProcessSettings]:
    """Build ProcessSettings from a (merged) process profile dict."""
    if not isinstance(data, dict):
        return None
    layer = _f(data.get("layer_height"))
    infill = _f(data.get("sparse_infill_density"))  # "15%" -> 15.0
    walls = _i(data.get("wall_loops"))
    # Representative speed: median of the speeds that drive most of the print.
    speeds = [s for s in (_f(data.get("inner_wall_speed")),
                          _f(data.get("outer_wall_speed")),
                          _f(data.get("sparse_infill_speed")),
                          _f(data.get("internal_solid_infill_speed"))) if s]
    speed = None
    if speeds:
        speeds.sort()
        speed = int(round(speeds[len(speeds) // 2]))
    if layer is None and infill is None and walls is None:
        return None  # doesn't look like a process profile
    name = data.get("name") or "process"
    return ProcessSettings(
        name=str(name),
        layer_height_mm=layer,
        infill_pct=int(round(infill)) if infill is not None else None,
        wall_count=walls,
        print_speed_mms=speed,
    )


def parse_filament(data: dict) -> Optional[FilamentSettings]:
    """Build FilamentSettings from a (merged) filament profile dict."""
    if not isinstance(data, dict):
        return None
    density = _f(data.get("filament_density"))
    cost = _f(data.get("filament_cost"))
    flow = _f(data.get("filament_max_volumetric_speed"))
    nozzle_t = _i(data.get("nozzle_temperature"))
    bed_t = _i(data.get("hot_plate_temp") or data.get("bed_temperature"))
    if density is None and cost is None and flow is None:
        return None
    name = data.get("name") or "filament"
    return FilamentSettings(
        name=str(name),
        density_g_cm3=density,
        cost_per_kg=cost,
        max_volumetric_speed_mm3s=flow,
        nozzle_temp_c=nozzle_t,
        bed_temp_c=bed_t,
    )
