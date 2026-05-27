import json

import pytest

from printprep.config.presets import get_material
from printprep.core import analyze
from printprep.slicer import get_slicer


def test_clean_cube_no_supports(clean_cube):
    result = analyze(clean_cube, path="clean_cube.stl")
    profile = get_slicer("creality").build_profile(result, "pla")
    assert profile.supports is False
    assert profile.support_style == "none"
    assert profile.slicer == "creality"
    assert profile.material == "PLA"


def test_material_temps_applied(clean_cube):
    # Values sourced from OrcaSlicer's generic PETG base profile.
    result = analyze(clean_cube, path="clean_cube.stl")
    profile = get_slicer("anycubic").build_profile(result, "petg")
    assert profile.nozzle_temp_c == 255
    assert profile.bed_temp_c == 80
    assert profile.max_volumetric_speed_mm3s == 10.0


def test_profile_serializes_to_json(clean_cube):
    result = analyze(clean_cube, path="clean_cube.stl")
    gen = get_slicer("creality")
    profile = gen.build_profile(result, "pla")
    parsed = json.loads(gen.to_json(profile))
    assert parsed["slicer"] == "creality"
    assert "layer_height_mm" in parsed


def test_unknown_slicer_raises():
    with pytest.raises(KeyError):
        get_slicer("nonexistent")


def test_unknown_material_raises():
    with pytest.raises(KeyError):
        get_material("wood")
