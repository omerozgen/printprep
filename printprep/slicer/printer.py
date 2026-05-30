"""Printer (machine) specifications and where to get them.

Two sources, both 100% offline:

1. The user's installed slicer — OrcaSlicer / Creality Print / Anycubic Slicer
   all share the same machine-profile JSON schema, so one parser covers all
   three. This gives the *real* configured printer: bed size, nozzle diameter,
   max speeds and (importantly) retraction, which OrcaSlicer stores at the
   machine level rather than per-filament.

2. A small bundled database (`config/printers.json`) of common models, used as
   a fallback when no slicer is installed or the profile can't be found. These
   are factual build-volume / nozzle numbers, not copyrightable settings.

No network access — printer data never comes from the internet.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List, Optional

_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "config", "printers.json")


@dataclass
class PrinterSpec:
    """A printer's physical constraints, used to sharpen slicer suggestions."""
    name: str
    bed_x_mm: float
    bed_y_mm: float
    bed_z_mm: float
    nozzle_diameter_mm: float = 0.4
    max_print_speed_mms: Optional[int] = None
    max_volumetric_speed_mm3s: Optional[float] = None
    retraction_mm: Optional[float] = None
    retraction_speed_mms: Optional[int] = None
    source: str = "bundled"  # "slicer" | "bundled"

    def fits(self, dx: float, dy: float, margin_mm: float = 0.0) -> bool:
        """True if a dx×dy footprint fits the bed (either orientation)."""
        bx, by = self.bed_x_mm - margin_mm, self.bed_y_mm - margin_mm
        return (dx <= bx and dy <= by) or (dx <= by and dy <= bx)


def _first(value, default=None):
    """OrcaSlicer stores many scalars as one-element lists; unwrap them."""
    if isinstance(value, (list, tuple)):
        return value[0] if value else default
    return value if value is not None else default


def _parse_printable_area(area) -> Optional[tuple]:
    """Derive (x, y) bed size from a `printable_area` corner list.

    Two on-disk formats are seen in the wild:
      - list (OrcaSlicer / Anycubic): ["0x0", "420x0", "420x420", "0x420"]
      - comma-separated string (Creality Print): "0x0,220x0,220x220,0x220"
    We take the span on each axis. Returns None if it can't be parsed.
    """
    if isinstance(area, str):
        area = [c for c in area.split(",") if c.strip()]
    if not isinstance(area, (list, tuple)) or not area:
        return None
    xs, ys = [], []
    for corner in area:
        try:
            xstr, ystr = str(corner).lower().split("x", 1)
            xs.append(float(xstr))
            ys.append(float(ystr))
        except (ValueError, AttributeError):
            continue
    if not xs or not ys:
        return None
    return (max(xs) - min(xs), max(ys) - min(ys))


def parse_orca_machine(data: dict) -> Optional[PrinterSpec]:
    """Build a PrinterSpec from an OrcaSlicer/Creality/Anycubic machine dict.

    Returns None if the dict doesn't look like a machine profile (no bed size).
    Tolerant of missing keys — slicer profiles often inherit and omit fields.
    """
    if not isinstance(data, dict):
        return None

    bed = _parse_printable_area(data.get("printable_area"))
    if bed is None:
        return None
    bed_x, bed_y = bed

    try:
        bed_z = float(_first(data.get("printable_height"), 0) or 0)
    except (ValueError, TypeError):
        bed_z = 0.0

    try:
        nozzle = float(_first(data.get("nozzle_diameter"), 0.4) or 0.4)
    except (ValueError, TypeError):
        nozzle = 0.4

    def _opt_float(key):
        try:
            v = _first(data.get(key))
            return float(v) if v is not None and str(v) != "" else None
        except (ValueError, TypeError):
            return None

    def _opt_int(key):
        v = _opt_float(key)
        return int(round(v)) if v is not None else None

    name = (data.get("name") or data.get("printer_settings_id")
            or data.get("printer_model") or "Unknown printer")

    # max_print_speed isn't always present; fall back to the X-axis mechanical
    # max (machine_max_speed_x is a list whose first value is the top speed).
    max_speed = _opt_int("max_print_speed")
    if max_speed is None:
        try:
            mx = data.get("machine_max_speed_x")
            if isinstance(mx, (list, tuple)) and mx:
                max_speed = int(round(float(mx[0])))
        except (ValueError, TypeError):
            max_speed = None

    return PrinterSpec(
        name=str(name),
        bed_x_mm=round(bed_x, 1),
        bed_y_mm=round(bed_y, 1),
        bed_z_mm=round(bed_z, 1),
        nozzle_diameter_mm=nozzle,
        max_print_speed_mms=max_speed,
        max_volumetric_speed_mm3s=_opt_float("max_volumetric_extrusion_rate")
                                  or _opt_float("filament_max_volumetric_speed"),
        retraction_mm=_opt_float("retraction_length"),
        retraction_speed_mms=_opt_int("retraction_speed"),
        source="slicer",
    )


def parse_machine_file(path: str) -> Optional[PrinterSpec]:
    """Parse a machine profile from a JSON file path. None on any failure."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    spec = parse_orca_machine(data)
    if spec is not None and (not spec.name or spec.name == "Unknown printer"):
        # Fall back to the file name (minus extension) for a readable label.
        spec.name = os.path.splitext(os.path.basename(path))[0]
    return spec


# ---- bundled database ----

def _load_db() -> List[PrinterSpec]:
    try:
        with open(_DB_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return []
    specs = []
    for p in data.get("printers", []):
        specs.append(PrinterSpec(
            name=p["name"],
            bed_x_mm=float(p["bed_x_mm"]),
            bed_y_mm=float(p["bed_y_mm"]),
            bed_z_mm=float(p["bed_z_mm"]),
            nozzle_diameter_mm=float(p.get("nozzle_diameter_mm", 0.4)),
            max_print_speed_mms=p.get("max_print_speed_mms"),
            max_volumetric_speed_mm3s=p.get("max_volumetric_speed_mm3s"),
            retraction_mm=p.get("retraction_mm"),
            retraction_speed_mms=p.get("retraction_speed_mms"),
            source="bundled",
        ))
    return specs


BUNDLED_PRINTERS = _load_db()


def bundled_names() -> List[str]:
    return [p.name for p in BUNDLED_PRINTERS]


def get_bundled(name: str) -> Optional[PrinterSpec]:
    """Look up a bundled printer by name (case-insensitive, exact or prefix)."""
    key = name.strip().lower()
    for p in BUNDLED_PRINTERS:
        if p.name.lower() == key:
            return p
    for p in BUNDLED_PRINTERS:
        if p.name.lower().startswith(key):
            return p
    return None
