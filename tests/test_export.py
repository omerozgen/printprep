import json

import pytest

from printprep.core import analyze
from printprep.slicer import export_profile, get_slicer


def _profile(clean_cube):
    result = analyze(clean_cube, path="clean_cube.stl")
    return get_slicer("creality").build_profile(result, "pla")


def test_orca_export_produces_two_valid_jsons(clean_cube):
    files = export_profile(_profile(clean_cube), "orca")
    assert len(files) == 2
    names = sorted(files)
    assert names[0].endswith("_filament.json")
    assert names[1].endswith("_process.json")

    filament = json.loads(files[names[0]])
    process = json.loads(files[names[1]])
    assert filament["type"] == "filament"
    assert filament["nozzle_temperature"] == ["220"]  # PLA from OrcaSlicer data
    assert filament["filament_type"] == ["PLA"]
    assert process["type"] == "process"
    assert process["layer_height"] == "0.2"
    assert process["sparse_infill_density"] == "15%"


def test_orca_support_toggles_with_overhangs(clean_cube):
    # A cube has no overhangs -> support disabled.
    files = export_profile(_profile(clean_cube), "orca")
    process = json.loads(files[next(n for n in files if n.endswith("_process.json"))])
    assert process["enable_support"] == "0"


def test_prusa_export_is_importable_ini(clean_cube):
    files = export_profile(_profile(clean_cube), "prusa")
    assert len(files) == 1
    text = next(iter(files.values()))
    assert "temperature = 220" in text
    assert "fill_density = 15%" in text
    assert "layer_height = 0.2" in text


def test_unknown_format_raises(clean_cube):
    with pytest.raises(ValueError):
        export_profile(_profile(clean_cube), "cura")


def test_orca_export_embeds_compatible_printer(clean_cube):
    files = export_profile(_profile(clean_cube), "orca",
                           printer="Creality K1 Max 0.4 nozzle")
    fil = json.loads(files[next(n for n in files if n.endswith("_filament.json"))])
    proc = json.loads(files[next(n for n in files if n.endswith("_process.json"))])
    assert fil["compatible_printers"] == ["Creality K1 Max 0.4 nozzle"]
    assert proc["compatible_printers"] == ["Creality K1 Max 0.4 nozzle"]


def test_orca_export_skips_printer_when_blank(clean_cube):
    files = export_profile(_profile(clean_cube), "orca")
    fil = json.loads(files[next(n for n in files if n.endswith("_filament.json"))])
    assert "compatible_printers" not in fil
