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

    Defaults to ``GEMS_DATA_DIR`` if set, else ``/tmp/gems_data`` when populated
    (keeping multi-hundred-MB raw rasters out of Git snapshots), else ``REPO_ROOT / 'data'``.
    """
    env = os.environ.get("GEMS_DATA_DIR")
    if env:
        return Path(env)
    tmp = Path("/tmp/gems_data")
    if (tmp / "sample_submission.tif").is_file():
        return tmp
    return REPO_ROOT / "data"


def cache_dir() -> Path:
    env = os.environ.get("GEMS_CACHE_DIR")
    if env:
        p = Path(env)
    else:
        p = Path("/tmp/gems_karage1_cache")
    p.mkdir(parents=True, exist_ok=True)
    return p
