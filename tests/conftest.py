import numpy as np
import pytest
import trimesh


@pytest.fixture
def clean_cube():
    """Watertight 20mm cube."""
    return trimesh.creation.box(extents=[20, 20, 20])


@pytest.fixture
def broken_cube():
    """Cube with its top face removed (clean square hole) and flipped winding."""
    box = trimesh.creation.box(extents=[20, 20, 20])
    z_max = box.vertices[:, 2].max()
    face_z = box.vertices[box.faces][:, :, 2]
    top_mask = np.all(np.abs(face_z - z_max) < 1e-6, axis=1)
    faces = box.faces[~top_mask].copy()
    faces[0] = faces[0][::-1]
    faces[1] = faces[1][::-1]
    return trimesh.Trimesh(vertices=box.vertices.copy(), faces=faces, process=False)


@pytest.fixture
def slab():
    """40 x 40 x 2 mm slab — known 2mm minimum wall thickness."""
    return trimesh.creation.box(extents=[40, 40, 2])
