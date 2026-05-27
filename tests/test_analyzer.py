from pytest import approx

from printprep.core import analyze


def test_clean_cube_geometry(clean_cube):
    result = analyze(clean_cube, path="clean_cube.stl")
    assert result.volume_mm3 == approx(8000, abs=1.0)
    assert result.dimensions_mm == (20.0, 20.0, 20.0)
    assert result.is_watertight is True
    assert result.is_winding_consistent is True
    assert result.is_volume is True
    assert result.body_count == 1
    assert result.degenerate_faces == 0
    assert result.duplicate_faces == 0


def test_clean_cube_has_no_overhangs(clean_cube):
    # The bottom face rests on the bed and must not be flagged as an overhang.
    result = analyze(clean_cube, path="clean_cube.stl")
    assert result.overhang_face_count == 0


def test_clean_cube_no_issues(clean_cube):
    result = analyze(clean_cube, path="clean_cube.stl")
    assert result.issues == []
