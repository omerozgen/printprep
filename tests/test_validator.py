from pytest import approx

from printprep.core import analyzer
from printprep.core import validator


def test_broken_cube_flags_problems(broken_cube):
    assert broken_cube.is_watertight is False
    assert broken_cube.is_winding_consistent is False


def test_slab_min_wall_estimate(slab):
    thickness = validator.estimate_min_wall(slab)
    assert thickness is not None
    assert thickness == approx(2.0, abs=0.2)


def test_thin_wall_estimate_is_deterministic(slab):
    a = validator.estimate_min_wall(slab)
    b = validator.estimate_min_wall(slab)
    assert a == b


def test_overhang_excludes_footprint(clean_cube):
    mask = validator.overhang_mask(clean_cube)
    assert mask.sum() == 0


def test_analyze_handles_missing_ray_backend(monkeypatch, clean_cube):
    # When ray casting is unavailable, analysis must still complete gracefully.
    monkeypatch.setattr(validator, "ray_available", lambda mesh: False)
    result = analyzer.analyze(clean_cube, path="clean_cube.stl")
    assert result.min_wall_mm is None
    assert any("Thin-wall analysis unavailable" in i for i in result.issues)
