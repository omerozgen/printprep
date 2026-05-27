"""Demo: analyze -> fix -> suggest on a generated broken model.

Run:  python examples/sample_workflow.py
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_samples import make_broken_cube  # noqa: E402

from printprep.core import analyze, repair_mesh
from printprep.slicer import get_slicer


def main():
    mesh = make_broken_cube()

    print("== analyze (before) ==")
    before = analyze(mesh, path="broken_cube.stl")
    print(f"watertight={before.is_watertight} winding={before.is_winding_consistent}")
    for issue in before.issues:
        print(f"  - {issue}")

    print("\n== fix ==")
    mesh, report = repair_mesh(mesh)
    print(f"watertight {report.watertight_before} -> {report.watertight_after}, "
          f"volume={report.volume_after / 1000:.2f} cm³")

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fixed.stl")
        mesh.export(out)
        print(f"exported -> {out}")

    print("\n== suggest (creality / pla) ==")
    after = analyze(mesh, path="fixed.stl")
    profile = get_slicer("creality").build_profile(after, "pla")
    print(json.dumps(profile.__dict__, indent=2))


if __name__ == "__main__":
    main()
