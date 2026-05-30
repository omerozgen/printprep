"""Discover filament/process profiles in locally installed slicers.

Scans standard user-config directories for the major slicers on each OS, looks
for `.json` / `.ini` / `.fdm_material` files that look like filament or process
profiles, and returns a structured list. Used by `printprep slicer-discover`.
"""

import glob as _glob
import os
import platform
from typing import Dict, List


def _expand_versioned(paths: List[str]) -> List[str]:
    """Resolve version subfolders some slicers insert before `user/`.

    Creality Print, for example, stores config under `Creality Print/7.0/user`
    rather than `Creality Print/user`. For any `.../user` path that doesn't
    exist literally, glob one level deeper (`.../*/user`) and use what's found.
    """
    out = []
    for p in paths:
        if os.path.isdir(p):
            out.append(p)
            continue
        if os.path.basename(p) == "user":
            matches = _glob.glob(os.path.join(os.path.dirname(p), "*", "user"))
            if matches:
                out.extend(sorted(matches))
                continue
        out.append(p)  # keep literal (harmless if missing)
    return out


def _config_roots() -> Dict[str, List[str]]:
    home = os.path.expanduser("~")
    system = platform.system()
    roots: Dict[str, List[str]] = {}
    if system == "Darwin":
        appsup = os.path.join(home, "Library", "Application Support")
        roots = {
            "OrcaSlicer": [os.path.join(appsup, "OrcaSlicer", "user")],
            "Creality Print": [
                os.path.join(appsup, "Creality", "Creality Print", "user"),
                os.path.join(appsup, "Creality Print", "user"),
            ],
            "AnycubicSlicerNext": [os.path.join(appsup, "AnycubicSlicerNext", "user")],
            "PrusaSlicer": [os.path.join(appsup, "PrusaSlicer")],
            "Cura": [os.path.join(appsup, "cura")],
        }
    elif system == "Linux":
        cfg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
        roots = {
            "OrcaSlicer": [os.path.join(cfg, "OrcaSlicer", "user")],
            "Creality Print": [os.path.join(cfg, "Creality Print", "user")],
            "AnycubicSlicerNext": [os.path.join(cfg, "AnycubicSlicerNext", "user")],
            "PrusaSlicer": [os.path.join(cfg, "PrusaSlicer")],
            "Cura": [os.path.join(cfg, "cura")],
        }
    elif system == "Windows":
        appdata = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
        roots = {
            "OrcaSlicer": [os.path.join(appdata, "OrcaSlicer", "user")],
            "Creality Print": [os.path.join(appdata, "Creality Print", "user")],
            "AnycubicSlicerNext": [os.path.join(appdata, "AnycubicSlicerNext", "user")],
            "PrusaSlicer": [os.path.join(appdata, "PrusaSlicer")],
            "Cura": [os.path.join(appdata, "cura")],
        }
    return {k: _expand_versioned(v) for k, v in roots.items()}


def _classify(rel_dir: str, filename: str):
    """Guess whether a file looks like a filament, process or machine profile."""
    parts = set(rel_dir.lower().replace("\\", "/").split("/"))
    name = filename.lower()
    if name.endswith(".fdm_material"):
        return "filament"
    if {"filament", "filaments"} & parts or "filament" in name:
        return "filament"
    if {"machine", "printer", "printers"} & parts or "machine" in name:
        return "machine"
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


def _read_active_machine_names(base: str) -> set:
    """Best-effort read of the selected machine preset name(s) from a slicer's
    `.conf` file (JSON). OrcaSlicer / Creality / Anycubic store the active
    printer under a "machine" key inside a presets block."""
    import json

    names = set()
    try:
        confs = [f for f in os.listdir(base) if f.endswith(".conf")]
    except OSError:
        return names
    for cf in confs:
        try:
            with open(os.path.join(base, cf), encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "machine" and isinstance(v, str) and v and v != "Default Printer":
                        names.add(v)
                    else:
                        stack.append(v)
            elif isinstance(node, list):
                stack.extend(node)
    return names


def discover_printers(roots: Dict[str, List[str]] = None) -> List[Dict]:
    """Find the user's printer(s) in installed slicers and parse to PrinterSpec.

    Strategy (OrcaSlicer / Creality Print / Anycubic Slicer share one schema):
      - All *custom* machine profiles in `user/**/machine/`.
      - Plus the *active* machine (read from the slicer's .conf), resolved even
        when it's a built-in profile under `system/**/machine/` — this is the
        common case, since most people just pick a bundled printer model.

    Returns [{slicer, path, spec, active}], active printers sorted first.
    """
    from printprep.slicer.printer import parse_machine_file

    if roots is None:
        roots = _config_roots()

    printers: List[Dict] = []
    seen = set()
    for slicer, paths in roots.items():
        bases = {os.path.dirname(p) if os.path.basename(p) == "user" else p for p in paths}
        for base in bases:
            if not os.path.isdir(base):
                continue
            active = _read_active_machine_names(base)
            # Collect machine JSONs from user (custom), system + ota (built-in).
            for sub in ("user", "system", "ota"):
                sub_root = os.path.join(base, sub)
                if not os.path.isdir(sub_root):
                    continue
                for root, _, files in os.walk(sub_root):
                    if os.path.basename(root).lower() != "machine":
                        continue
                    for fname in files:
                        if not fname.lower().endswith(".json"):
                            continue
                        stem = os.path.splitext(fname)[0]
                        is_active = stem in active
                        # Include user customs always; built-ins only if active.
                        if sub != "user" and not is_active:
                            continue
                        spec = parse_machine_file(os.path.join(root, fname))
                        if spec is None:  # common base files have no bed -> skipped
                            continue
                        key = (spec.name, spec.bed_x_mm, spec.bed_y_mm)
                        if key in seen:
                            continue
                        seen.add(key)
                        printers.append({"slicer": slicer, "path": os.path.join(root, fname),
                                         "spec": spec, "active": is_active})
    printers.sort(key=lambda r: (not r["active"], r["slicer"], r["spec"].name.lower()))
    return printers


def _read_active_presets(base: str) -> Dict[str, str]:
    """Read the *currently selected* machine/process/filament preset names from
    a slicer's `.conf`. Prefers an explicit "presets" block; otherwise falls
    back to the first machine/process/filament string values seen."""
    import json

    chosen: Dict[str, str] = {}
    first: Dict[str, str] = {}
    try:
        confs = [f for f in os.listdir(base) if f.endswith(".conf")]
    except OSError:
        return chosen
    for cf in confs:
        try:
            with open(os.path.join(base, cf), encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        presets = data.get("presets") if isinstance(data, dict) else None
        if isinstance(presets, dict):
            for kind in ("machine", "process", "filament"):
                v = presets.get(kind)
                if isinstance(v, str) and v and v != "Default Printer":
                    chosen.setdefault(kind, v)
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for k, v in node.items():
                    if k in ("machine", "process", "filament") and isinstance(v, str) \
                            and v and v != "Default Printer":
                        first.setdefault(k, v)
                    else:
                        stack.append(v)
            elif isinstance(node, list):
                stack.extend(node)
    for kind in ("machine", "process", "filament"):
        chosen.setdefault(kind, first.get(kind))
    return {k: v for k, v in chosen.items() if v}


def _index_profiles(base: str) -> Dict[str, Dict[str, str]]:
    """Index every profile JSON under base by kind -> {stem: path}, preferring
    user/ over system/ over ota/ (so customs win over built-ins)."""
    index: Dict[str, Dict[str, str]] = {"machine": {}, "process": {}, "filament": {}}
    for sub in ("ota", "system", "user"):  # later wins -> user overrides
        sub_root = os.path.join(base, sub)
        if not os.path.isdir(sub_root):
            continue
        for root, _, files in os.walk(sub_root):
            kind = os.path.basename(root).lower()
            if kind not in index:
                continue
            for fname in files:
                if fname.lower().endswith(".json"):
                    index[kind][os.path.splitext(fname)[0]] = os.path.join(root, fname)
    return index


def _load_with_inherits(path: str, kind_index: Dict[str, str], _depth: int = 0) -> dict:
    """Load a profile JSON, merging its `inherits` parent chain (child wins)."""
    import json

    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    parent_name = data.get("inherits")
    if parent_name and _depth < 12 and parent_name in kind_index:
        parent = _load_with_inherits(kind_index[parent_name], kind_index, _depth + 1)
        merged = dict(parent)
        merged.update(data)
        return merged
    return data


def detect_active_config(roots: Dict[str, List[str]] = None) -> List[Dict]:
    """Resolve the user's *currently selected* printer + process + filament for
    each installed slicer, with inherits chains merged.

    Returns [{slicer, printer, process, filament}] where each value is the
    parsed dataclass (or None). Slicers with no detectable active config are
    skipped.
    """
    from printprep.slicer.printer import parse_orca_machine
    from printprep.slicer.settings import parse_filament, parse_process

    if roots is None:
        roots = _config_roots()

    out: List[Dict] = []
    for slicer, paths in roots.items():
        bases = {os.path.dirname(p) if os.path.basename(p) == "user" else p for p in paths}
        for base in bases:
            if not os.path.isdir(base):
                continue
            presets = _read_active_presets(base)
            if not presets:
                continue
            index = _index_profiles(base)
            cfg = {"slicer": slicer, "printer": None, "process": None, "filament": None}

            machine_data = {}
            mname = presets.get("machine")
            if mname and mname in index["machine"]:
                machine_data = _load_with_inherits(index["machine"][mname], index["machine"])
                cfg["printer"] = parse_orca_machine(machine_data)

            def _resolve(preset_name, kind, machine_default):
                # A real custom selection wins; "Default Setting/Filament" and
                # unresolved names fall back to the printer's declared default.
                if (preset_name and not str(preset_name).lower().startswith("default")
                        and preset_name in index[kind]):
                    return preset_name
                md = machine_default[0] if isinstance(machine_default, (list, tuple)) \
                    and machine_default else machine_default
                if isinstance(md, str) and md in index[kind]:
                    return md
                if preset_name and preset_name in index[kind]:
                    return preset_name
                return None

            pname = _resolve(presets.get("process"), "process",
                             machine_data.get("default_print_profile"))
            if pname:
                cfg["process"] = parse_process(
                    _load_with_inherits(index["process"][pname], index["process"]))

            fname = _resolve(presets.get("filament"), "filament",
                             machine_data.get("default_filament_profile"))
            if fname:
                cfg["filament"] = parse_filament(
                    _load_with_inherits(index["filament"][fname], index["filament"]))

            if cfg["printer"] or cfg["process"] or cfg["filament"]:
                out.append(cfg)
    return out
