"""Discover filament/process profiles in locally installed slicers.

Scans standard user-config directories for the major slicers on each OS, looks
for `.json` / `.ini` / `.fdm_material` files that look like filament or process
profiles, and returns a structured list. Used by `printprep slicer-discover`.
"""

import os
import platform
from typing import Dict, List


def _config_roots() -> Dict[str, List[str]]:
    home = os.path.expanduser("~")
    system = platform.system()
    if system == "Darwin":
        appsup = os.path.join(home, "Library", "Application Support")
        return {
            "OrcaSlicer": [os.path.join(appsup, "OrcaSlicer", "user")],
            "Creality Print": [
                os.path.join(appsup, "Creality", "Creality Print", "user"),
                os.path.join(appsup, "Creality Print", "user"),
            ],
            "AnycubicSlicerNext": [os.path.join(appsup, "AnycubicSlicerNext", "user")],
            "PrusaSlicer": [os.path.join(appsup, "PrusaSlicer")],
            "Cura": [os.path.join(appsup, "cura")],
        }
    if system == "Linux":
        cfg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
        return {
            "OrcaSlicer": [os.path.join(cfg, "OrcaSlicer", "user")],
            "Creality Print": [os.path.join(cfg, "Creality Print", "user")],
            "AnycubicSlicerNext": [os.path.join(cfg, "AnycubicSlicerNext", "user")],
            "PrusaSlicer": [os.path.join(cfg, "PrusaSlicer")],
            "Cura": [os.path.join(cfg, "cura")],
        }
    if system == "Windows":
        appdata = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
        return {
            "OrcaSlicer": [os.path.join(appdata, "OrcaSlicer", "user")],
            "Creality Print": [os.path.join(appdata, "Creality Print", "user")],
            "AnycubicSlicerNext": [os.path.join(appdata, "AnycubicSlicerNext", "user")],
            "PrusaSlicer": [os.path.join(appdata, "PrusaSlicer")],
            "Cura": [os.path.join(appdata, "cura")],
        }
    return {}


def _classify(rel_dir: str, filename: str):
    """Guess whether a file looks like a filament or a process profile."""
    parts = set(rel_dir.lower().replace("\\", "/").split("/"))
    name = filename.lower()
    if name.endswith(".fdm_material"):
        return "filament"
    if {"filament", "filaments"} & parts or "filament" in name:
        return "filament"
    if {"process", "print", "print_settings"} & parts:
        return "process"
    return None


def discover_profiles(roots: Dict[str, List[str]] = None) -> List[Dict[str, str]]:
    """Return a sorted list of {slicer, kind, name, path}."""
    if roots is None:
        roots = _config_roots()
    found: List[Dict[str, str]] = []
    for slicer, paths in roots.items():
        for base in paths:
            if not os.path.isdir(base):
                continue
            for root, _, files in os.walk(base):
                for fname in files:
                    if not fname.lower().endswith((".json", ".ini", ".fdm_material")):
                        continue
                    kind = _classify(os.path.relpath(root, base), fname)
                    if kind is None:
                        continue
                    found.append({
                        "slicer": slicer,
                        "kind": kind,
                        "name": os.path.splitext(fname)[0],
                        "path": os.path.join(root, fname),
                    })
    found.sort(key=lambda r: (r["slicer"], r["kind"], r["name"].lower()))
    return found
