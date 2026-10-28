"""Canonical workspace and external data/cache path resolution."""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "evidence"
DOCS_DIR = REPO_ROOT / "docs"
DOWNLOADS_DIR = DOCS_DIR / "downloads"
DOCS_DATA_DIR = DOCS_DIR / "data"
REGISTRY_DIR = REPO_ROOT / "registry"


def data_dir() -> Path:
    """Return directory containing restored competition & external GeoTIFFs.

    Defaults to ``GEMS_DATA_DIR`` if set, else ``REPO_ROOT / 'data'`` only when
    already populated locally, else ``/tmp/gems_data`` (keeping multi-hundred-MB
    raw rasters outside Git/workspace snapshots).
    """
    env = os.environ.get("GEMS_DATA_DIR")
    if env:
        return Path(env)
    repo_data = REPO_ROOT / "data"
    if (repo_data / "sample_submission.tif").is_file():
        return repo_data
    return Path("/tmp/gems_data")


def cache_dir() -> Path:
    env = os.environ.get("GEMS_CACHE_DIR")
    if env:
        p = Path(env)
    else:
        p = Path("/tmp/gems_karage1_cache")
    p.mkdir(parents=True, exist_ok=True)
    return p
