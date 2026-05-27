"""Mesh loading and capability probing."""

import os

import numpy as np
import trimesh

from printprep import PrintPrepError


def load_mesh(path: str) -> trimesh.Trimesh:
    """Load an STL (or any trimesh-supported format) as a single Trimesh.

    `force='mesh'` guarantees a concatenated Trimesh even for multi-body /
    scene files. Raises PrintPrepError with a friendly message on failure.
    """
    if not os.path.isfile(path):
        raise PrintPrepError(f"File not found: {path}")
    try:
        mesh = trimesh.load(path, force="mesh")
    except Exception as exc:  # trimesh raises ValueError/various on bad data
        raise PrintPrepError(f"Could not read mesh from '{path}': {exc}") from exc
    if not isinstance(mesh, trimesh.Trimesh) or mesh.is_empty:
        raise PrintPrepError(f"'{path}' did not contain a usable mesh.")
    return mesh


def ray_available(mesh: trimesh.Trimesh) -> bool:
    """Probe whether ray casting works (needs rtree or embree backend).

    Cached on the mesh so repeated calls are cheap. Returns False instead of
    raising when the backend is missing, so analysis degrades gracefully.
    """
    cached = getattr(mesh, "_printprep_ray_ok", None)
    if cached is not None:
        return cached
    try:
        origin = mesh.bounds.mean(axis=0).reshape(1, 3)
        direction = np.array([[0.0, 0.0, 1.0]])
        mesh.ray.intersects_location(ray_origins=origin, ray_directions=direction)
        ok = True
    except Exception:
        ok = False
    mesh._printprep_ray_ok = ok
    return ok
