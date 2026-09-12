import trimesh

from printprep.core import repair_mesh
from printprep.core.repair import geometry_preserved


def test_geometry_preserved_rejects_shape_change(clean_cube):
    # a result with very different extents (mangled) must be rejected
    shrunk = trimesh.creation.box(extents=[2, 2, 2])
    assert geometry_preserved(clean_cube, shrunk) is False


def test_geometry_preserved_accepts_similar(clean_cube):
    similar = trimesh.creation.box(extents=[20, 20, 20])
    assert geometry_preserved(clean_cube, similar) is True


def test_repair_makes_watertight(broken_cube):
    assert broken_cube.is_watertight is False
    _, report = repair_mesh(broken_cube)
    assert report.watertight_after is True
    # Volume must be positive — guards against the fix-normals-before-fill ordering bug.
    assert report.volume_after > 0


def test_repair_report_counts(broken_cube):
    _, report = repair_mesh(broken_cube)
    assert report.watertight_before is False
    assert report.holes_filled is True


def test_repair_reports_no_open_edges_when_watertight(broken_cube):
    _, report = repair_mesh(broken_cube)
    assert report.watertight_after is True
    assert report.open_edges_after == 0
