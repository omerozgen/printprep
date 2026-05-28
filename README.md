# PrintPrep

**English** | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

STL model analysis and slicer-profile suggestion tool.

Spot likely print problems before you slice, and get slicer settings tailored
to your model.

## Features

- **Model analysis** — overlapping geometry, thin walls, inverted normals,
  open edges / holes, separate bodies, non-manifold edges, self-intersections.
- **Problem detection** — identify potential failures before you start the
  print.
- **Slicer suggestions** — profile presets for Creality Print and
  AnycubicSlicerNext.
- **Mesh repair** — basic repair plus optional aggressive escalation via
  `pymeshfix` with a guard that rejects mangled results.
- **100% local** — model data never leaves your machine. No accounts, no
  telemetry.

## Install

```bash
pip install printprep
```

## Quick start

```bash
# Analyze a model
printprep analyze model.stl

# Repair common issues
printprep fix model.stl --output fixed_model.stl

# Auto-orient to the best print pose
printprep orient model.stl --output oriented_model.stl

# Merge separate bodies into one piece
# (boolean union requires: pip install -e ".[merge]")
printprep merge model.stl --output merged_model.stl

# Aggressive repair (optional, for stubborn meshes): pip install -e ".[repair]"
#   `fix` automatically escalates to pymeshfix when the standard repair isn't
#   enough. If the escalation would damage the geometry, a safety guard kicks
#   in and the standard result is kept.

# Batch-analyze every STL in a folder
printprep batch ./models --json report.json

# Slicer profile suggestion
printprep suggest model.stl --slicer creality --material pla

# Import your own slicer profile (OrcaSlicer .json / PrusaSlicer .ini / Cura .fdm_material)
printprep suggest model.stl --slicer creality --import-profile my_filament.json

# Export a profile that loads directly into your slicer
#   orca  -> OrcaSlicer / Creality Print / Anycubic Slicer (.json: filament + process)
#   prusa -> PrusaSlicer / SuperSlicer (.ini)
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

## Web UI

3D preview, drag-and-drop analysis, repair, and slicer suggestions — all in
the browser:

```bash
pip install -e ".[web]"   # one-time
printprep serve           # http://127.0.0.1:8000
```

## Desktop app

No browser required — `printprep app` opens the web UI inside a native
window (WKWebView on macOS, WebView2 on Windows, GTK WebKit on Linux). The
server runs in the background of the same process and shuts down when you
close the window.

```bash
pip install -e ".[web,desktop]"   # includes pywebview
printprep app                     # opens in a native window
```

Double-click launchers (all platforms):

- **macOS:** double-click `PrintPrep.app` (or drag it to the Dock /
  `/Applications`). First launch prompts you to pick the project folder
  and remembers your choice.
- **Windows:** double-click `PrintPrep.bat` (works as a Desktop shortcut
  too).
- **Linux:** run `./install-linux.sh` → installs
  `~/.local/share/applications/printprep.desktop` and shows up as
  **PrintPrep** in your app menu.

All of them call the same `printprep app` command. If pywebview isn't
installed, they fall back to `printprep serve` + your default browser.

Runs entirely locally — your model data never leaves your machine. In the
3D viewer, overhang surfaces are red, thin walls are amber, holes / open
edges are magenta, inverted normals show as cyan backfaces, and separate
bodies are colored differently. You can auto-orient the model, import
your own slicer profile, and export a slicer-loadable profile (.zip).

Material presets (temperatures, flow) are sourced from the
[OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) open-source filament
library — see [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md). Geometry
analysis is computed from the model itself.

## Development

```bash
# Clone
git clone https://github.com/omerozgen/printprep.git
cd printprep

# Virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Dependencies
pip install -e ".[dev,web]"

# Tests (Python)
pytest

# Tests (3D viewer geometry helpers, Node 18+)
node --test tests/js/geometry-utils.test.mjs
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow,
[SECURITY.md](SECURITY.md) for the security policy, and
[CHANGELOG.md](CHANGELOG.md) for what's new.

## Supported slicers

- Creality Print
- AnycubicSlicerNext
- Profile export also covers OrcaSlicer / PrusaSlicer / SuperSlicer formats.

## Status

Pre-1.0 preview (`0.1.x`). APIs and CLI surface may change. Bug reports and
PRs are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE). Third-party attributions live in
[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
