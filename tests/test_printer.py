"""Tests for printer-spec parsing, the bundled DB, and suggestion wiring."""

import trimesh

from printprep.core.analyzer import analyze
from printprep.slicer import bed_fit_warning, get_bundled, get_slicer
from printprep.slicer.printer import (
    BUNDLED_PRINTERS,
    PrinterSpec,
    parse_orca_machine,
)


ORCA_MACHINE = {
    "type": "machine",
    "name": "Anycubic Kobra 3 Max 0.4 nozzle",
    "printable_area": ["0x0", "420x0", "420x420", "0x420"],
    "printable_height": "500",
    "nozzle_diameter": ["0.4"],
    "retraction_length": ["0.8"],
    "retraction_speed": ["40"],
    "max_print_speed": "500",
}


def _cube(size=20.0):
    return trimesh.creation.box(extents=(size, size, size))


def test_bundled_db_loads():
    assert len(BUNDLED_PRINTERS) >= 10
    names = [p.name for p in BUNDLED_PRINTERS]
    assert "Anycubic Kobra 3 Max" in names


def test_get_bundled_exact_and_prefix():
    exact = get_bundled("Creality K1 Max")
    assert exact is not None and exact.bed_x_mm == 300
    # prefix match
    pref = get_bundled("Prusa MK4")
    assert pref is not None
    assert get_bundled("does-not-exist") is None


def test_parse_orca_machine():
    spec = parse_orca_machine(ORCA_MACHINE)
    assert spec is not None
    assert spec.bed_x_mm == 420 and spec.bed_y_mm == 420 and spec.bed_z_mm == 500
    assert spec.nozzle_diameter_mm == 0.4
    assert spec.retraction_mm == 0.8
    assert spec.retraction_speed_mms == 40
    assert spec.max_print_speed_mms == 500
    assert spec.source == "slicer"


def test_parse_non_machine_returns_none():
    assert parse_orca_machine({"type": "filament", "name": "PLA"}) is None
    assert parse_orca_machine({}) is None
    assert parse_orca_machine("nonsense") is None


def test_printable_area_comma_string():
    # Creality Print stores printable_area as a comma-separated string, not a list.
    spec = parse_orca_machine({
        "type": "machine",
        "name": "Creality CR-10 SE 0.4 nozzle",
        "printable_area": "0x0,220x0,220x220,0x220",
        "printable_height": "265",
        "nozzle_diameter": ["0.4"],
        "retraction_length": ["0.5"],
    })
    assert spec is not None
    assert spec.bed_x_mm == 220 and spec.bed_y_mm == 220 and spec.bed_z_mm == 265
    assert spec.retraction_mm == 0.5


def test_max_speed_fallback_from_machine_max_speed_x():
    spec = parse_orca_machine({
        "printable_area": ["0x0", "300x0", "300x300", "0x300"],
        "printable_height": "300",
        "machine_max_speed_x": ["600", "300", "780"],
    })
    assert spec is not None and spec.max_print_speed_mms == 600


def test_printable_area_offset_origin():
    # A bed whose corners are offset should still yield correct extents.
    spec = parse_orca_machine({
        "printable_area": ["10x10", "260x10", "260x260", "10x260"],
        "printable_height": "250",
    })
    assert spec is not None
    assert spec.bed_x_mm == 250 and spec.bed_y_mm == 250


def test_fits_both_orientations():
    spec = PrinterSpec("t", bed_x_mm=300, bed_y_mm=200, bed_z_mm=300)
    assert spec.fits(250, 150)
    assert spec.fits(150, 250)   # rotated
    assert not spec.fits(350, 50)


def test_bed_fit_warning():
    result = analyze(_cube(450.0))  # 450mm cube — too big for most beds
    small = get_bundled("Prusa MINI+")
    warn = bed_fit_warning(result, small)
    assert warn is not None and warn["kind"] == "bed_fit"
    # No printer -> no warning.
    assert bed_fit_warning(result, None) is None


def test_suggestion_uses_printer_nozzle_and_retraction():
    result = analyze(_cube(20.0))
    gen = get_slicer("creality")
    spec = PrinterSpec("Custom 0.6", bed_x_mm=300, bed_y_mm=300, bed_z_mm=300,
                       nozzle_diameter_mm=0.6, retraction_mm=1.5, retraction_speed_mms=25)
    profile = gen.build_profile_from_preset(result, get_material_pla(), spec)
    assert profile.nozzle_diameter_mm == 0.6
    assert profile.retraction_mm == 1.5
    assert profile.retraction_speed_mms == 25
    assert profile.printer == "Custom 0.6"


def get_material_pla():
    from printprep.config.presets import get_material
    return get_material("pla")
