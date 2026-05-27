"""Import a user's own slicer profile and turn it into a MaterialPreset.

Supports the three common export formats:
  - OrcaSlicer / Bambu Studio filament profile (.json)
  - PrusaSlicer / SuperSlicer config export (.ini)
  - Cura material (.fdm_material / XML)

Only the fields PrintPrep cares about are extracted; everything else is ignored.
"""

import json
from xml.etree import ElementTree

from printprep import PrintPrepError
from printprep.config.defaults import (
    DEFAULT_LAYER_HEIGHT_MM,
    LINE_WIDTH_MM,
)
from printprep.config.presets import MaterialPreset


def _first_number(value):
    """Coerce an Orca list / comma list / scalar string to a float, or None."""
    if value is None:
        return None
    if isinstance(value, list):
        value = value[0] if value else None
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "nil":
        return None
    text = text.split(",")[0].strip()
    try:
        return float(text)
    except ValueError:
        return None


def _vol_from_speed(speed_mms, max_vol):
    """If a profile gives print speed but not volumetric flow, approximate the flow."""
    if max_vol is not None:
        return max_vol
    if speed_mms is not None:
        return round(speed_mms * DEFAULT_LAYER_HEIGHT_MM * LINE_WIDTH_MM, 1)
    return 8.0  # conservative fallback


def _build(name, nozzle, bed, retraction, retraction_speed, max_vol, speed=None):
    if nozzle is None:
        raise PrintPrepError("Could not find a nozzle temperature in the profile.")
    return MaterialPreset(
        name=name or "Imported",
        nozzle_temp_c=int(round(nozzle)),
        bed_temp_c=int(round(bed)) if bed is not None else 0,
        max_volumetric_speed_mm3s=_vol_from_speed(speed, max_vol),
        retraction_mm=retraction if retraction is not None else 0.8,
        retraction_speed_mms=int(round(retraction_speed)) if retraction_speed is not None else 40,
    )


def _parse_orca(data: dict) -> MaterialPreset:
    name = data.get("name") or _orca_str(data.get("filament_type"))
    return _build(
        name=name,
        nozzle=_first_number(data.get("nozzle_temperature")
                             or data.get("nozzle_temperature_initial_layer")),
        bed=_first_number(data.get("hot_plate_temp") or data.get("bed_temperature")
                          or data.get("textured_plate_temp") or data.get("cool_plate_temp")),
        retraction=_first_number(data.get("filament_retraction_length")),
        retraction_speed=_first_number(data.get("filament_retraction_speed")),
        max_vol=_first_number(data.get("filament_max_volumetric_speed")),
    )


def _orca_str(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _parse_ini(text: str) -> MaterialPreset:
    kv = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(";") or line.startswith("["):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            kv[k.strip().lower()] = v.strip()
    return _build(
        name=kv.get("filament_type") or kv.get("filament_settings_id"),
        nozzle=_first_number(kv.get("temperature") or kv.get("first_layer_temperature")),
        bed=_first_number(kv.get("bed_temperature") or kv.get("first_layer_bed_temperature")),
        retraction=_first_number(kv.get("filament_retract_length") or kv.get("retract_length")),
        retraction_speed=_first_number(kv.get("filament_retract_speed") or kv.get("retract_speed")),
        max_vol=_first_number(kv.get("filament_max_volumetric_speed")),
    )


def _parse_cura_xml(text: str) -> MaterialPreset:
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        raise PrintPrepError(f"Invalid XML material profile: {exc}") from exc

    def strip_ns(tag):
        return tag.split("}")[-1]

    settings = {}
    name = None
    for el in root.iter():
        tag = strip_ns(el.tag)
        if tag == "setting" and el.get("key"):
            settings[el.get("key").strip().lower()] = (el.text or "").strip()
        elif tag in ("material", "name") and el.text and not name:
            name = el.text.strip()

    return _build(
        name=name,
        nozzle=_first_number(settings.get("print temperature")
                             or settings.get("default print temperature")),
        bed=_first_number(settings.get("heated bed temperature")
                          or settings.get("default heated bed temperature")),
        retraction=_first_number(settings.get("retraction amount")),
        retraction_speed=_first_number(settings.get("retraction speed")),
        max_vol=_first_number(settings.get("maximum volumetric flow")),
    )


def parse_material_profile(content: str, filename: str = "") -> MaterialPreset:
    """Detect the format from content/filename and return a MaterialPreset."""
    stripped = content.lstrip()
    name = filename.lower()

    if stripped.startswith("{") or name.endswith(".json"):
        try:
            return _parse_orca(json.loads(content))
        except json.JSONDecodeError as exc:
            raise PrintPrepError(f"Invalid JSON profile: {exc}") from exc
    if stripped.startswith("<") or name.endswith(".fdm_material") or name.endswith(".xml"):
        return _parse_cura_xml(content)
    return _parse_ini(content)
