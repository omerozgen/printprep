from printprep.core import repair_mesh


def test_repair_makes_watertight(broken_cube):
    assert broken_cube.is_watertight is False
    mesh, report = repair_mesh(broken_cube)
    assert report.watertight_after is True
    # Volume must be positive — guards against the fix-normals-before-fill ordering bug.
    assert report.volume_after > 0


def test_repair_report_counts(broken_cube):
    _, report = repair_mesh(broken_cube)
    assert report.watertight_before is False
    assert report.holes_filled is True
