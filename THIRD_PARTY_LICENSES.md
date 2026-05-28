# Third-Party Licenses & Attributions

PrintPrep is released under the [MIT License](LICENSE). This document credits
the third-party software and data that PrintPrep ships with or depends on.

---

## Bundled (vendored) code

These files live inside this repository and are redistributed as part of
PrintPrep. Their original license notices are preserved in-file.

### three.js (r160) — `printprep/web/static/vendor/three.module.js`
- **Project:** https://github.com/mrdoob/three.js
- **License:** MIT
- **Copyright:** © 2010–2023 Three.js Authors
- **Notes:** Used by the in-browser 3D viewer. Unmodified from the upstream
  r160 distribution. License header is retained at the top of the file.

### three.js addons — `printprep/web/static/vendor/addons/`
- `OrbitControls.js`, `STLLoader.js`
- **License:** MIT (same as three.js core)
- **Copyright:** © three.js Authors

---

## Bundled data

### OrcaSlicer filament base profiles — `printprep/config/slicer_profiles.json`
- **Source:** [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer), specifically
  `resources/profiles/OrcaFilamentLibrary/filament/base/fdm_filament_*.json`
- **OrcaSlicer license:** AGPL-3.0
- **Fields used:** `nozzle_temp_c`, `bed_temp_c`, `max_volumetric_speed_mm3s`,
  density values for PLA/PETG/ABS/TPU base materials.
- **Position:** These are numeric physical-process parameters (extrusion
  temperatures, flow caps, polymer densities) sourced from upstream — they
  describe physical fact, not creative expression, and PrintPrep treats them
  as factual reference data rather than copyrightable software. PrintPrep
  itself does **not** copy any OrcaSlicer source code.
- **Attribution kept in-file:** see the `_source` field at the top of
  `slicer_profiles.json`.
- **If you object to this use:** open an issue at
  https://github.com/omerozgen/printprep/issues and we will adjust.

---

## Required runtime dependencies (installed via pip)

These are pulled in by `pip install printprep` and are **not** redistributed
inside this repository. Their licenses apply when you install them.

| Package    | License       | Project URL                                  |
|------------|---------------|----------------------------------------------|
| numpy      | BSD-3-Clause  | https://numpy.org                            |
| scipy      | BSD-3-Clause  | https://scipy.org                            |
| trimesh    | MIT           | https://github.com/mikedh/trimesh            |
| networkx   | BSD-3-Clause  | https://networkx.org                         |
| rtree      | MIT           | https://github.com/Toblerity/rtree           |
| click      | BSD-3-Clause  | https://palletsprojects.com/p/click/         |
| rich       | MIT           | https://github.com/Textualize/rich           |

---

## Optional dependencies (extras)

These are only installed when you opt in (`pip install printprep[name]`).
Some have licenses that may affect how you distribute *your* derivative —
read carefully if you plan to redistribute a build that includes them.

| Extra     | Package     | License       | Notes                                                                                          |
|-----------|-------------|---------------|------------------------------------------------------------------------------------------------|
| `web`     | fastapi     | MIT           | Local web UI server.                                                                           |
| `web`     | uvicorn     | BSD-3-Clause  | ASGI server.                                                                                   |
| `web`     | python-multipart | Apache-2.0 | File-upload parsing.                                                                          |
| `desktop` | pywebview   | BSD-3-Clause  | Native window for `printprep app`.                                                             |
| `merge`   | manifold3d  | Apache-2.0    | Boolean union for `merge` command.                                                             |
| `repair`  | pymeshfix   | MIT (wrapper) over GPL-licensed MeshFix core | The underlying MeshFix is GPL — installing `[repair]` and redistributing the result may require you to release your distribution under GPL. |
| `analyze` | pymeshlab   | **GPL-2.0+**  | Self-intersection face detection. Pulls a GPL runtime — installing `[analyze]` and shipping a derived binary triggers GPL copyleft for that distribution. |
| `dev`     | pytest, ruff, black, httpx, pytest-cov | MIT/BSD | Development only. |

**Short version:** the base install of PrintPrep is MIT-clean. If you opt
into `[repair]` or `[analyze]` and then redistribute a bundled binary, you
need to comply with GPL terms for that bundle. Most end users just running
PrintPrep locally on their own machine are unaffected.

---

## How to report a licensing concern

If you are an author or maintainer of any third-party project listed above
and believe PrintPrep is using your work incorrectly, please open an issue
or email the maintainer via the address in `pyproject.toml`. We will respond
promptly and remove/relicense as needed.
