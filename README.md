# PrintPrep

<p align="center">
  <img src="https://raw.githubusercontent.com/omerozgen/printprep/main/printprep/web/static/favicon.ico" alt="PrintPrep Logo" width="80" height="80" />
</p>

<p align="center">
  <b>100% Offline & Private STL Model Analysis, Automated Mesh Repair & Slicer Assistant</b>
</p>

<p align="center">
  <a href="https://github.com/omerozgen/printprep/actions/workflows/ci.yml"><img src="https://github.com/omerozgen/printprep/actions/workflows/ci.yml/badge.svg" alt="CI Status" /></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
  <img src="https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue" alt="Python Versions" />
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey" alt="Platform" />
  <img src="https://img.shields.io/badge/privacy-100%25%20local%20%26%20offline-green" alt="100% Offline" />
</p>

---

<p align="center">
  <b>🌐 Choose Language / Dil Seçimi:</b><br>
  <b>English</b> •
  <a href="README.tr.md">Türkçe</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ja.md">日本語</a> •
  <a href="README.ko.md">한국어</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.pt.md">Português</a> •
  <a href="README.ar.md">العربية</a> •
  <a href="README.hi.md">हिन्दी</a> •
  <a href="README.bn.md">বাংলা</a> •
  <a href="README.pa.md">ਪੰਜਾਬੀ</a> •
  <a href="README.jv.md">Basa Jawa</a>
</p>

---

## 📖 Overview

**PrintPrep** is an all-in-one pre-flight diagnostic tool and slicer assistant for 3D printing. It detects structural flaws in STL meshes before slicing, fixes common geometry problems, auto-orients parts for minimal supports, packs multi-part builds onto your printer bed, and generates optimized slicer profiles tailored to your exact printer and material.

**🔒 100% Local & Private:** No cloud dependencies, no telemetry, no accounts. All mesh processing and slicing calculations happen locally on your hardware.

---

## ✨ Features

### 🔍 Deep Mesh Diagnostics
- **Watertight & Manifold Check:** Identifies holes, boundary edges, and non-manifold edges.
- **Ray-Casted Wall Thickness:** Measures actual wall thickness distribution (`min`, `p5`, `p50`, `max`) to warn about unprintable thin features.
- **Overhang Analysis:** Calculates downward-facing overhang area fraction and steepest angles based on your printer's support threshold.
- **Inverted Normals:** Flags reversed face windings that cause slicer voids.
- **Multi-body Separation:** Detects floating or disconnected islands within a single STL.
- **Self-Intersection Detection:** Pinpoints colliding triangles (via optional `[analyze]` extra).

### 🛠️ Intelligent Mesh Repair & Boolean Merge
- **One-Click Fix:** Cleans duplicate vertices, removes degenerate zero-area faces, seals open boundary holes, and corrects normals.
- **Guarded Aggressive Repair:** Automatically escalates to `pymeshfix` for complex broken meshes, with a volume-guard that prevents accidental detail collapse.
- **Boolean Union:** Combines multi-body STLs into a unified solid manifold (`manifold3d`, `[merge]` extra).

### 🧭 Auto-Orientation & Bed Packing
- **Auto-Orient (`orient`):** Tests convex-hull face projections to minimize overhang surface area and support material usage.
- **Multi-Part Bed Packing (`pack`):** Arranges multiple STL models onto your printer's bed with configurable spacing and shelf bin-packing.

### 🖨️ Printer-Aware Slicer Suggestions & Job Estimation
- **Hardware Integration:** Reads real nozzle diameters, bed dimensions, acceleration, and retraction limits from your installed slicer (Creality Print, OrcaSlicer, Anycubic Slicer, PrusaSlicer).
- **Fallback Database:** Includes pre-calibrated machine profiles for Creality, Anycubic, Bambu Lab, Prusa, and generic beds.
- **Real Settings Estimation:** Computes filament usage (length & weight in grams), print time, and total cost based on your active slicer profiles.
- **Direct Export:** Generates ready-to-import `.json` (OrcaSlicer / Creality / Anycubic) and `.ini` (PrusaSlicer / SuperSlicer) profiles.

### 🖥️ Interactive 3D Web & Desktop GUI
- **Three.js Web UI:** Drag-and-drop 3D inspection with color-coded overlays:
  - 🔴 **Red:** Overhang faces requiring support
  - 🟡 **Amber:** Ultra-thin walls (< 0.8 mm)
  - 🟣 **Magenta:** Open boundary edges & holes
  - 🔵 **Cyan:** Inverted surface normals
  - 🌈 **Rainbow:** Distinct disconnected bodies
- **Interactive Tools:** 2-point 3D measurement caliper and cross-section clipping planes (X / Y / Z).
- **Native Desktop App:** Runs via `pywebview` in a standalone window (`PrintPrep.app` on macOS, `PrintPrep.bat` on Windows, `PrintPrep.desktop` on Linux).

---

## 🚀 Installation

Install from PyPI:

```bash
pip install printprep
```

### Optional Feature Extras

| Extra | Command | Description |
| :--- | :--- | :--- |
| **Web UI** | `pip install "printprep[web]"` | FastAPI server and Three.js 3D viewer |
| **Desktop App** | `pip install "printprep[web,desktop]"` | Native OS desktop window (`pywebview`) |
| **Aggressive Repair** | `pip install "printprep[repair]"` | `pymeshfix` for stubborn, complex holes |
| **Boolean Merge** | `pip install "printprep[merge]"` | High-speed boolean unions via `manifold3d` |
| **Self-Intersection**| `pip install "printprep[analyze]"` | `pymeshlab` self-intersection checks (Py 3.10+) |
| **Full Suite** | `pip install "printprep[all]"` | Installs all core and optional features |

---

## ⚡ Quick Start (CLI)

```bash
# 1. Analyze an STL model
printprep analyze model.stl

# 2. Repair holes, non-manifold edges, and inverted normals
printprep fix model.stl --output fixed_model.stl

# 3. Orient the model for minimal support material
printprep orient model.stl --output oriented_model.stl

# 4. Merge disconnected separate bodies into a single solid mesh
printprep merge multi_body.stl --output merged.stl

# 5. Suggest slicer settings based on your printer and material
printprep suggest model.stl --slicer creality --material pla --auto-printer

# 6. Batch-analyze an entire directory of STLs
printprep batch ./models --json report.json

# 7. List all detected slicers and bundled printers
printprep printer-list

# 8. Discover installed filament and process profiles
printprep slicer-discover

# 9. Pack multiple STLs onto your build plate
printprep pack ./parts_folder --bed 220x220 --out-dir ./packed
```

---

## 🌐 Web Interface

Launch the interactive local web application:

```bash
printprep serve --host 127.0.0.1 --port 8000
```
Open your browser at `http://127.0.0.1:8000`. Drag and drop any `.stl` file to inspect geometry issues, toggle before/after repairs, take measurements, and export slicer profiles.

---

## 💻 Native Desktop Application

Run PrintPrep as a standalone desktop window without touching the browser:

```bash
printprep app
```

### Double-Click Launchers

- **macOS:** Double-click `PrintPrep.app` (or drag it to `/Applications` / Dock). Automatically handles Apple Silicon & Rosetta environments.
- **Windows:** Double-click `PrintPrep.bat` (can be pinned to your Desktop or Taskbar).
- **Linux:** Run `./install-linux.sh` to install `PrintPrep.desktop` into your system application launcher.

---

## 🖨️ Supported Slicers & Ecosystem

| Slicer | Detection | Profile Import | Profile Export |
| :--- | :---: | :---: | :---: |
| **OrcaSlicer** | ✅ Automatic | ✅ `.json` | ✅ `.json` (Process + Filament) |
| **Creality Print (5.x / 7.x)** | ✅ Automatic | ✅ `.json` | ✅ `.json` |
| **AnycubicSlicerNext** | ✅ Automatic | ✅ `.json` | ✅ `.json` |
| **PrusaSlicer / SuperSlicer** | ✅ Automatic | ✅ `.ini` | ✅ `.ini` |
| **UltiMaker Cura** | ✅ Automatic | ✅ `.fdm_material` | — |
| **Bambu Studio** | ✅ Bundled Specs | ✅ `.json` | ✅ `.json` |

---

## 🛠️ Development & Testing

```bash
# 1. Clone repository
git clone https://github.com/omerozgen/printprep.git
cd printprep

# 2. Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install development dependencies
pip install -e ".[dev,web]"

# 4. Run Python test suite (70 tests)
pytest

# 5. Run 3D viewer geometry tests (Node 18+)
node --test tests/js/geometry-utils.test.mjs

# 6. Run linter
ruff check printprep tests
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Third-party dependencies and open-source profiles (Three.js, OrcaSlicer filament database) are credited in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
