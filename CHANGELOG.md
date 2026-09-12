# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Estimates from your real slicer settings.** With `--auto-printer` (CLI) or a
  detected printer selected (web), the filament weight / print time / cost
  estimate is now computed from your slicer's *active* process + filament
  profile instead of PrintPrep's generic defaults:
  - reads layer height, infill %, wall count and print speed from the active
    process profile;
  - reads filament density and cost-per-kg from the active filament profile
    (resolving the `inherits` chain) — cost is filled in automatically, no need
    to type a price;
  - falls back to the printer's declared default process/filament when no
    custom profile is active;
  - handles Creality's comma-string `printable_area` and version subfolders
    (`Creality Print/7.0/user`).

### Added (printer detection, continued)
- **Printer-aware suggestions.** PrintPrep can now read your printer's real
  specs instead of assuming a 0.4mm nozzle / 420×420 bed:
  - Auto-detects machine profiles from your installed slicer (OrcaSlicer /
    Creality Print / Anycubic Slicer — one shared JSON schema).
  - Bundled `config/printers.json` fallback (Anycubic / Creality / Bambu /
    Prusa / generic) for when no slicer is installed — pick from a dropdown.
  - Uses the real nozzle diameter (wall count + line width), retraction
    (which OrcaSlicer stores per-machine), and clamps the recommended print
    speed to the printer's mechanical max.
  - Bed-fit check: warns when a model's footprint/height won't fit the bed.
  - CLI: `printprep suggest --printer "<name>"`, `--printer-profile <path>`,
    `--auto-printer`; new `printprep printer-list` command.
  - Web: a Printer dropdown (auto-detected + bundled) wired into suggest and
    export; `/api/printers` endpoint.
  - 100% offline — printer data never comes from the internet.

### Added (CI & Open Source)
- Re-enabled GitHub Actions CI workflow for the public open-source repository (multi-OS pytest matrix, node --test, and ruff linting).

### Fixed
- ruff lint errors (unused imports, redundant f-string).

## [0.1.0] — 2026-05-28

First public preview release.

### Added

#### Core analysis
- STL loading via `trimesh` with `force='mesh'` and validation.
- `analyze` — watertight check, winding consistency, volume, surface area,
  bounding box / dimensions, body count, overhang area fraction & steepest
  angle, structured issue list.
- Hole / open-edge detection with `np.unique` on sorted edge pairs.
- Wall-thickness estimate via ray casting (rtree-backed), reported as
  min / p5 / p50 / max.
- Non-manifold edge count.
- Optional self-intersection face detection via `pymeshlab` (Python 3.10+,
  `[analyze]` extra).
- Separate-bodies detection (union-find on shared edges).
- Inverted-normals detection.

#### Repair
- `fix` — vertex merge, degenerate / duplicate face removal, hole fill,
  normal & winding correction.
- Optional aggressive escalation via `pymeshfix` (`[repair]` extra) with a
  geometry-preservation guard that rejects mangled results (drastic face
  collapse or bounding-box drift).
- `merge` — merge separate bodies into a single piece via boolean union
  (`manifold3d`, `[merge]` extra) with concatenate fallback when one or
  more bodies aren't solid.

#### Slicer profiles
- Material presets (PLA, PETG, ABS, TPU) sourced from OrcaSlicer's
  generic filament library — see [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
- Creality Print and AnycubicSlicerNext suggestion strategies.
- Profile export for OrcaSlicer / Creality Print / Anycubic Slicer (`.json`
  filament + process) and PrusaSlicer / SuperSlicer (`.ini`).
- Profile import from OrcaSlicer / PrusaSlicer / Cura material profiles.
- `slicer-discover` — scan local OrcaSlicer / Creality Print / Anycubic
  Slicer / PrusaSlicer / Cura config directories for available profiles.

#### Other CLI
- `orient` — auto-orientation using convex-hull face normals to minimize
  overhang area.
- `batch` — analyze every STL in a folder, JSON / CSV report.
- `pack` — first-fit-decreasing-height shelf bin-packing for multi-part
  bed layout, optional rotation.
- `suggest` — model-aware slicer-profile suggestion (wall count, supports,
  brim, layer height, infill).

#### Print job estimate
- Filament length / weight (density-aware), print time (volumetric-speed
  based), optional cost given `--price-per-kg`.

#### Web UI (`printprep serve`, `[web]` extra)
- Drag-and-drop analysis with three.js r160 in-browser 3D viewer.
- Highlighting for overhang faces (red), thin walls (amber),
  open / hole edges (magenta), inverted normals (cyan backface), and
  separately-colored bodies.
- Click-driven 3D measurement tool.
- Cross-section / clipping plane.
- Before / after fix toggle.
- Issue list links into the 3D view.
- Profile import and zipped export.
- Batch analysis with sortable table + CSV download.

#### Desktop launcher (`printprep app`, `[desktop]` extra)
- pywebview-based native window (WKWebView / WebView2 / GTK WebKit).
- `PrintPrep.app` macOS bundle with arch detection (`sysctl hw.optional.arm64`)
  to handle Rosetta launches.
- `PrintPrep.bat` Windows double-click launcher.
- `install-linux.sh` + `PrintPrep.desktop` for application-menu integration.
- Server auto-shuts when the window closes.

### Tests

- 57 Python tests (`pytest`).
- 5 JavaScript tests for the 3D viewer geometry helpers
  (`node --test tests/js/geometry-utils.test.mjs`).

[Unreleased]: https://github.com/omerozgen/printprep/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/omerozgen/printprep/releases/tag/v0.1.0
