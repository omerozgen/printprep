import trimesh

from printprep.core import merge_to_single


def test_merge_boolean_union_when_bodies_are_volumes(clean_cube):
    # two overlapping watertight cubes -> separate bodies, both volumes
    b = trimesh.creation.box(extents=[20, 20, 20])
    b.apply_translation([10, 0, 0])
    combo = trimesh.util.concatenate([clean_cube, b])

    merged, report = merge_to_single(combo)

    assert report.bodies_before == 2
    if report.method == "boolean":  # manifold3d available
        assert report.bodies_after == 1
        assert report.watertight_after is True
        assert report.volume_after > 0


def test_merge_repairs_non_volume_body_when_possible(clean_cube, broken_cube):
    # broken_cube (simple open box) can be repaired to a volume by pymeshfix,
    # so when it's available the merge uses a real boolean union.
    import pytest
    pytest.importorskip("pymeshfix")
    pytest.importorskip("manifold3d")
    bc = broken_cube.copy()
    bc.apply_translation([40, 0, 0])
    combo = trimesh.util.concatenate([clean_cube, bc])

    _, report = merge_to_single(combo)
    assert report.bodies_before == 2
    assert report.method == "boolean"


def test_merge_concatenate_fallback_without_meshfix(monkeypatch, clean_cube, broken_cube):
    # with no aggressive repair available, a non-volume body forces concatenation
    monkeypatch.setattr("printprep.core.merge.meshfix_available", lambda: False)
    bc = broken_cube.copy()
    bc.apply_translation([40, 0, 0])
    combo = trimesh.util.concatenate([clean_cube, bc])

    merged, report = merge_to_single(combo)
    assert report.bodies_before == 2
    assert report.method == "concatenate"
    assert len(merged.faces) > 0
