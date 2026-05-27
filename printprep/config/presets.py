"""Material presets.

Values are loaded from slicer_profiles.json, which is sourced from OrcaSlicer's
open-source generic filament library (see the file's _source field). Nozzle/bed
temperatures and max volumetric flow are taken directly from upstream; retraction
values are standard direct-drive defaults (printer-dependent).
"""

import json
import os
from dataclasses import dataclass

_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slicer_profiles.json")


@dataclass(frozen=True)
class MaterialPreset:
    name: str
    nozzle_temp_c: int
    bed_temp_c: int
    max_volumetric_speed_mm3s: float
    retraction_mm: float
    retraction_speed_mms: int


def _load() -> dict:
    with open(_DATA_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    presets = {}
    for key, m in data["materials"].items():
        presets[key] = MaterialPreset(
            name=m["name"],
            nozzle_temp_c=m["nozzle_temp_c"],
            bed_temp_c=m["bed_temp_c"],
            max_volumetric_speed_mm3s=m["max_volumetric_speed_mm3s"],
            retraction_mm=m["retraction_mm"],
            retraction_speed_mms=m["retraction_speed_mms"],
        )
    return presets


MATERIAL_PRESETS = _load()
PROFILE_SOURCE = json.load(open(_DATA_PATH, encoding="utf-8"))["_source"]


def get_material(name: str) -> MaterialPreset:
    key = name.lower()
    if key not in MATERIAL_PRESETS:
        valid = ", ".join(sorted(MATERIAL_PRESETS))
        raise KeyError(f"Unknown material '{name}'. Available: {valid}")
    return MATERIAL_PRESETS[key]
