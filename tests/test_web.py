"""End-to-end tests for the FastAPI web endpoints via TestClient."""

import io
import zipfile

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from printprep.web.app import app  # noqa: E402

client = TestClient(app)


def _stl(mesh):
    data = mesh.export(file_type="stl")
    return data if isinstance(data, (bytes, bytearray)) else data.encode()


def _file(mesh, name="cube.stl"):
    return {"model": (name, _stl(mesh), "model/stl")}


def test_options():
    r = client.get("/api/options")
    assert r.status_code == 200
    body = r.json()
    assert "creality" in body["slicers"]
    assert "anycubic" in body["slicers"]
    assert "pla" in body["materials"]


def test_analyze(clean_cube):
    r = client.post("/api/analyze", files=_file(clean_cube))
    assert r.status_code == 200
    body = r.json()
    assert body["body_count"] == 1
    assert body["is_watertight"] is True
    assert body["filename"] == "cube.stl"
    assert len(body["dimensions_mm"]) == 3


def test_analyze_rejects_garbage():
    r = client.post("/api/analyze", files={"model": ("bad.stl", b"not an stl", "model/stl")})
    assert r.status_code == 400
    assert "error" in r.json()


def test_suggest(clean_cube):
    r = client.post("/api/suggest", data={"slicer": "creality", "material": "pla"},
                    files=_file(clean_cube))
    assert r.status_code == 200
    body = r.json()
    assert body["profile"]["slicer"] == "creality"
    assert body["profile"]["material"] == "PLA"
    assert body["profile"]["supports"] is False  # cube has no overhangs
    est = body["estimate"]
    assert est["filament_weight_g"] > 0
    assert est["print_time_min"] > 0


def test_suggest_with_price_returns_cost(clean_cube):
    r = client.post(
        "/api/suggest",
        data={"slicer": "creality", "material": "pla",
              "price_per_kg": "1200", "currency": "TL"},
        files=_file(clean_cube),
    )
    assert r.status_code == 200
    est = r.json()["estimate"]
    assert est["cost"] is not None and est["cost"] > 0
    assert est["currency"] == "TL"


def test_fix(broken_cube):
    r = client.post("/api/fix", files=_file(broken_cube, "broken.stl"))
    assert r.status_code == 200
    assert r.headers["x-watertight-after"] == "True"
    assert len(r.content) > 0


def test_orient(broken_cube):
    r = client.post("/api/orient", files=_file(broken_cube, "broken.stl"))
    assert r.status_code == 200
    assert "x-improved" in r.headers
    assert len(r.content) > 0


def test_export_orca_zip(clean_cube):
    r = client.post("/api/export", data={"slicer": "anycubic", "material": "petg", "fmt": "orca"},
                    files=_file(clean_cube))
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    names = zipfile.ZipFile(io.BytesIO(r.content)).namelist()
    assert any(n.endswith("_filament.json") for n in names)
    assert any(n.endswith("_process.json") for n in names)


def test_batch(clean_cube, broken_cube):
    files = [
        ("files", ("a.stl", _stl(clean_cube), "model/stl")),
        ("files", ("b.stl", _stl(broken_cube), "model/stl")),
    ]
    r = client.post("/api/batch", files=files)
    assert r.status_code == 200
    rows = r.json()["results"]
    assert len(rows) == 2
    names = {row["filename"] for row in rows}
    assert names == {"a.stl", "b.stl"}
    clean_row = next(row for row in rows if row["filename"] == "a.stl")
    assert clean_row["is_watertight"] is True
    assert clean_row["body_count"] == 1


def test_merge(broken_cube):
    r = client.post("/api/merge", files=_file(broken_cube, "broken.stl"))
    assert r.status_code == 200
    assert r.headers["x-method"] in ("boolean", "concatenate")
    assert "x-bodies-after" in r.headers
    assert len(r.content) > 0


def test_export_unknown_format_rejected(clean_cube):
    r = client.post("/api/export", data={"slicer": "creality", "material": "pla", "fmt": "cura"},
                    files=_file(clean_cube))
    assert r.status_code == 400
