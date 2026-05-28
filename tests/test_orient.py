import numpy as np
import trimesh

from printprep.core import suggest_orientation


def test_tilted_box_is_reoriented_flat():
    # A cube tilted 30° has a downward-facing overhang; the best pose is flat.
    box = trimesh.creation.box(extents=[20, 20, 20])
    box.apply_transform(trimesh.transformations.rotation_matrix(np.radians(30), [1, 0, 0]))

    oriented, result = suggest_orientation(box)

    assert result.overhang_before > 0.0
    assert result.improved is True
    assert result.overhang_after < result.overhang_before
    assert result.overhang_after < 0.05  # essentially no overhangs once flat
    # the re-oriented mesh should rest on the bed (min z ~ 0)
    assert abs(oriented.bounds[0, 2]) < 1e-6


def test_flat_cube_already_optimal():
    box = trimesh.creation.box(extents=[20, 20, 20])
    _, result = suggest_orientation(box)
    assert result.overhang_before == 0.0
    assert result.improved is False
