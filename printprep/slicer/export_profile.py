"""Export a SlicerProfile as files importable directly into real slicers.

Formats:
  - "orca"  : OrcaSlicer / Creality Print preset JSONs (a filament + a process
              profile). Both are Orca-lineage slicers and read the same schema.
  - "prusa" : a single PrusaSlicer / SuperSlicer config .ini.

Returns a {filename: text} mapping so callers can zip or write the files.
"""

import json
from typing import Dict

from printprep.slicer.base import SlicerProfile

EXPORT_FORMATS = ("orca", "prusa")

# our support_style -> OrcaSlicer support_type
_ORCA_SUPPORT = {"normal": "normal(auto)", "tree_auto": "tree(auto)"}
# our support_style -> PrusaSlicer support_material_style
_PRUSA_SUPPORT_STYLE = {"normal": "grid", "tree_auto": "organic"}

_PROFILE_VERSION = "1.10.0.0"


def _orca_filament(p: SlicerProfile, printer: str = "") -> dict:
    nozzle = str(p.nozzle_temp_c)
    bed = str(p.bed_temp_c)
    out = {
        "type": "filament",
        "name": f"PrintPrep {p.material} @{p.slicer.capitalize()}",
        "from": "User",
        "instantiation": "true",
        "version": _PROFILE_VERSION,
        "filament_type": [p.material],
        "nozzle_temperature": [nozzle],
        "nozzle_temperature_initial_layer": [nozzle],
        "hot_plate_temp": [bed],
        "hot_plate_temp_initial_layer": [bed],
        "cool_plate_temp": [bed],
        "cool_plate_temp_initial_layer": [bed],
        "textured_plate_temp": [bed],
        "textured_plate_temp_initial_layer": [bed],
        "filament_max_volumetric_speed": [str(p.max_volumetric_speed_mm3s)],
        "filament_retraction_length": [str(p.retraction_mm)],
        "filament_retraction_speed": [str(p.retraction_speed_mms)],
    }
    if printer:
        out["compatible_printers"] = [printer]
    return out


def _orca_process(p: SlicerProfile, printer: str = "") -> dict:
    layer = str(p.layer_height_mm)
    out = {
        "type": "process",
        "name": f"PrintPrep {p.layer_height_mm}mm @{p.slicer.capitalize()}",
        "from": "User",
        "instantiation": "true",
        "version": _PROFILE_VERSION,
        "layer_height": layer,
        "initial_layer_print_height": layer,
        "sparse_infill_density": f"{p.infill_pct}%",
        "wall_loops": str(p.wall_count),
        "enable_support": "1" if p.supports else "0",
        "support_type": _ORCA_SUPPORT.get(p.support_style, "normal(auto)"),
        "support_threshold_angle": "45",
        "brim_type": "outer_only" if p.brim else "no_brim",
        "brim_width": "5" if p.brim else "0",
    }
    if printer:
        out["compatible_printers"] = [printer]
    return out


def _prusa_ini(p: SlicerProfile) -> str:
    lines = [
        "# PrintPrep export — import via PrusaSlicer/SuperSlicer: File > Import > Import Config",
        f"# slicer target: {p.slicer}, material: {p.material}",
        "",
        f"temperature = {p.nozzle_temp_c}",
        f"first_layer_temperature = {p.nozzle_temp_c}",
        f"bed_temperature = {p.bed_temp_c}",
        f"first_layer_bed_temperature = {p.bed_temp_c}",
        f"filament_retract_length = {p.retraction_mm}",
        f"filament_retract_speed = {p.retraction_speed_mms}",
        f"filament_max_volumetric_speed = {p.max_volumetric_speed_mm3s}",
        f"layer_height = {p.layer_height_mm}",
        f"first_layer_height = {p.layer_height_mm}",
        f"fill_density = {p.infill_pct}%",
        f"perimeters = {p.wall_count}",
        f"support_material = {1 if p.supports else 0}",
        f"support_material_style = {_PRUSA_SUPPORT_STYLE.get(p.support_style, 'grid')}",
        "support_material_threshold = 45",
        f"brim_width = {5 if p.brim else 0}",
        "",
    ]
    return "\n".join(lines)


def export_profile(profile: SlicerProfile, fmt: str = "orca",
                   printer: str = "") -> Dict[str, str]:
    """Return {filename: file_text} for the requested format.

    When `printer` is non-empty, Orca exports embed it as compatible_printers
    so the profile binds to that specific printer on import.
    """
    fmt = fmt.lower()
    if fmt not in EXPORT_FORMATS:
        valid = ", ".join(EXPORT_FORMATS)
        raise ValueError(f"Unknown export format '{fmt}'. Available: {valid}")

    base = f"PrintPrep_{profile.slicer}_{profile.material}".replace(" ", "_")
    if fmt == "orca":
        return {
            f"{base}_filament.json": json.dumps(_orca_filament(profile, printer), indent=2),
            f"{base}_process.json": json.dumps(_orca_process(profile, printer), indent=2),
        }
    return {f"{base}.ini": _prusa_ini(profile)}
