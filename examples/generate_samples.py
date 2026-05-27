"""Generate sample STL files so the tool can be tried without user files.

Run:  python examples/generate_samples.py
Produces examples/clean_cube.stl and examples/broken_cube.stl.
"""

import os

import numpy as np
import trimesh


def make_clean_cube() -> trimesh.Trimesh:
    """A watertight 20mm cube — ready for slicing."""
    return trimesh.creation.box(extents=[20, 20, 20])


def make_broken_cube() -> trimesh.Trimesh:
    """A 20mm cube with its top face removed (hole) and some faces flipped."""
    box = trimesh.creation.box(extents=[20, 20, 20])
    # Remove the entire +Z top square (its 2 triangles) -> one clean square hole.
    z_max = box.vertices[:, 2].max()
    face_z = box.vertices[box.faces][:, :, 2]
    top_mask = np.all(np.abs(face_z - z_max) < 1e-6, axis=1)
    faces = box.faces[~top_mask].copy()
    faces[0] = faces[0][::-1]  # reverse winding
    faces[1] = faces[1][::-1]  # -> inconsistent normals
    # process=False keeps the mesh deliberately broken (no auto-repair on load)
    return trimesh.Trimesh(vertices=box.vertices.copy(), faces=faces, process=False)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    clean_path = os.path.join(out_dir, "clean_cube.stl")
    broken_path = os.path.join(out_dir, "broken_cube.stl")

    make_clean_cube().export(clean_path)
    make_broken_cube().export(broken_path)

    print(f"Wrote {clean_path}")
    print(f"Wrote {broken_path}")


if __name__ == "__main__":
    main()
