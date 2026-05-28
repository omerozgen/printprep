"""FastAPI backend for the PrintPrep web interface.

Wraps the existing printprep core. Runs locally (localhost) — no hosting,
API keys or external services required.
"""

import io
import os
import tempfile
import zipfile
from contextlib import contextmanager
from dataclasses import asdict

from typing import List, Optional

import trimesh
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from printprep import PrintPrepError, __version__
from printprep.config.presets import MATERIAL_PRESETS
from printprep.core import (
    analyze, estimate_print_job, load_mesh, merge_to_single, repair_mesh, suggest_orientation,
)
from printprep.config.presets import get_material
from printprep.slicer import (
    EXPORT_FORMATS,
    SLICER_NAMES,
    export_profile,
    get_slicer,
    parse_material_profile,
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app = FastAPI(title="PrintPrep", version=__version__)


@contextmanager
def _uploaded_mesh(upload: UploadFile):
    """Persist an uploaded model to a temp file and yield a loaded mesh."""
    suffix = os.path.splitext(upload.filename or "model.stl")[1] or ".stl"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        tmp.write(upload.file.read())
        tmp.flush()
        tmp.close()
        yield load_mesh(tmp.name)
    finally:
        os.unlink(tmp.name)


@app.get("/api/options")
def options():
    """Available slicers and materials for the UI dropdowns."""
    return {"slicers": list(SLICER_NAMES), "materials": sorted(MATERIAL_PRESETS)}


@app.post("/api/analyze")
def api_analyze(model: UploadFile):
    try:
        with _uploaded_mesh(model) as mesh:
            result = analyze(mesh, path=model.filename or "")
    except PrintPrepError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    data = asdict(result)
    data["filename"] = model.filename
    return data


@app.post("/api/suggest")
def api_suggest(model: UploadFile, slicer: str = Form("creality"),
                material: str = Form("pla"),
                price_per_kg: Optional[float] = Form(None),
                currency: str = Form(""),
                profile: Optional[UploadFile] = File(None)):
    try:
        with _uploaded_mesh(model) as mesh:
            result = analyze(mesh, path=model.filename or "")
        generator = get_slicer(slicer)
        if profile is not None and profile.filename:
            imported = parse_material_profile(
                profile.file.read().decode("utf-8", "replace"), profile.filename)
            built = generator.build_profile_from_preset(result, imported)
            preset = imported
        else:
            preset = get_material(material)
            built = generator.build_profile_from_preset(result, preset)
        estimate = estimate_print_job(result, built, preset,
                                      price_per_kg=price_per_kg, currency=currency)
    except PrintPrepError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except KeyError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc).strip('"')})
    return {"profile": asdict(built), "estimate": asdict(estimate)}


@app.post("/api/export")
def api_export(model: UploadFile, slicer: str = Form("creality"),
               material: str = Form("pla"), fmt: str = Form("orca"),
               printer: str = Form(""),
               profile: Optional[UploadFile] = File(None)):
    if fmt not in EXPORT_FORMATS:
        return JSONResponse(status_code=400, content={"error": f"Unknown format '{fmt}'."})
    try:
        with _uploaded_mesh(model) as mesh:
            result = analyze(mesh, path=model.filename or "")
        generator = get_slicer(slicer)
        if profile is not None and profile.filename:
            imported = parse_material_profile(
                profile.file.read().decode("utf-8", "replace"), profile.filename)
            built = generator.build_profile_from_preset(result, imported)
        else:
            built = generator.build_profile(result, material)
        files = export_profile(built, fmt, printer=printer)
    except PrintPrepError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except KeyError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc).strip('"')})

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, text in files.items():
            zf.writestr(fname, text)
    buf.seek(0)
    headers = {
        "Content-Disposition": f'attachment; filename="printprep_{slicer}_{fmt}.zip"',
    }
    return StreamingResponse(buf, media_type="application/zip", headers=headers)


@app.post("/api/fix")
def api_fix(model: UploadFile):
    try:
        with _uploaded_mesh(model) as mesh:
            mesh, report = repair_mesh(mesh)
            stl_bytes = mesh.export(file_type="stl")
    except PrintPrepError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})

    if isinstance(stl_bytes, str):
        stl_bytes = stl_bytes.encode()

    base = os.path.splitext(model.filename or "model.stl")[0]
    download_name = f"{base}_fixed.stl"
    headers = {
        "Content-Disposition": f'attachment; filename="{download_name}"',
        "X-Watertight-Before": str(report.watertight_before),
        "X-Watertight-After": str(report.watertight_after),
        "X-Merged-Vertices": str(report.merged_vertices),
        "X-Removed-Degenerate": str(report.removed_degenerate),
        "X-Removed-Duplicate": str(report.removed_duplicate),
        "X-Holes-Filled": str(report.holes_filled),
        "X-Volume-Mm3": f"{report.volume_after:.2f}",
        "X-Open-Edges": str(report.open_edges_after),
        "X-Method": report.method,
    }
    return StreamingResponse(io.BytesIO(stl_bytes), media_type="model/stl", headers=headers)


@app.post("/api/orient")
def api_orient(model: UploadFile):
    try:
        with _uploaded_mesh(model) as mesh:
            oriented, report = suggest_orientation(mesh)
            stl_bytes = oriented.export(file_type="stl")
    except PrintPrepError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})

    if isinstance(stl_bytes, str):
        stl_bytes = stl_bytes.encode()

    base = os.path.splitext(model.filename or "model.stl")[0]
    rx, ry, rz = report.euler_deg
    headers = {
        "Content-Disposition": f'attachment; filename="{base}_oriented.stl"',
        "X-Euler-Deg": f"{rx},{ry},{rz}",
        "X-Overhang-Before": f"{report.overhang_before:.4f}",
        "X-Overhang-After": f"{report.overhang_after:.4f}",
        "X-Improved": str(report.improved),
    }
    return StreamingResponse(io.BytesIO(stl_bytes), media_type="model/stl", headers=headers)


@app.post("/api/batch")
def api_batch(files: List[UploadFile] = File(...)):
    """Analyze multiple uploaded STLs and return a summary row per file."""
    rows = []
    for f in files:
        try:
            with _uploaded_mesh(f) as mesh:
                r = analyze(mesh, path=f.filename or "")
            rows.append({
                "filename": f.filename,
                "dimensions_mm": list(r.dimensions_mm),
                "volume_cm3": round(r.volume_mm3 / 1000, 2),
                "is_watertight": r.is_watertight,
                "body_count": r.body_count,
                "overhang_pct": round(r.overhang_area_fraction * 100, 1),
                "min_wall_mm": r.min_wall_mm,
                "issue_count": len(r.issues),
            })
        except PrintPrepError as exc:
            rows.append({"filename": f.filename, "error": str(exc)})
    return {"results": rows}


@app.post("/api/merge")
def api_merge(model: UploadFile):
    try:
        with _uploaded_mesh(model) as mesh:
            merged, report = merge_to_single(mesh)
            stl_bytes = merged.export(file_type="stl")
    except PrintPrepError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})

    if isinstance(stl_bytes, str):
        stl_bytes = stl_bytes.encode()

    base = os.path.splitext(model.filename or "model.stl")[0]
    headers = {
        "Content-Disposition": f'attachment; filename="{base}_merged.stl"',
        "X-Method": report.method,
        "X-Bodies-Before": str(report.bodies_before),
        "X-Bodies-After": str(report.bodies_after),
        "X-Watertight-After": str(report.watertight_after),
    }
    return StreamingResponse(io.BytesIO(stl_bytes), media_type="model/stl", headers=headers)


# Serve the static frontend at the root. Mounted last so /api/* takes priority.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
