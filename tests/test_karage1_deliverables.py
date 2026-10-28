"""End-to-end automated contract, physics, uniqueness, and UI audit tests for GEMSDOEkarage1."""
from __future__ import annotations

import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path

import numpy as np
import pytest
import rasterio
from scipy.spatial import cKDTree

from gems57 import grid as G57
from gems57.validate import assert_submittable, validate
from gemskarage1.emitter import emit_submodular_300m, sharpen_axial_crest
from gemskarage1.features import ALL_CHANNELS, LIDAR_GLOBAL_INDICES, MSUB_INDICES
from gemskarage1.paths import DOCS_DIR, DOWNLOADS_DIR, EVIDENCE_DIR, REPO_ROOT, data_dir


def test_channel_schema_and_lidar_quarantine() -> None:
    assert len(ALL_CHANNELS) == 58
    assert len(MSUB_INDICES) == 52
    for idx in MSUB_INDICES:
        assert idx not in LIDAR_GLOBAL_INDICES
        assert not ALL_CHANNELS[idx].startswith("lidar_")


def test_emitter_edge_cases_and_spacing_contract() -> None:
    rng = np.random.default_rng(123)
    surf = rng.uniform(0.0, 1.0, size=(64, 64)).astype(np.float32)
    surf[0, 0] = np.nan
    surf[0, 1] = -5.0
    dom = np.ones((64, 64), dtype=bool)
    dom[:4, :] = False
    vis = np.zeros((64, 64), dtype=bool)
    vis[30, 20:45] = True

    sharp = sharpen_axial_crest(surf, dom)
    assert np.isfinite(sharp).all()
    assert float(sharp[~dom].max()) == 0.0

    # Zero budget edge case
    empty = emit_submodular_300m(sharp, dom, vis, 0, b_collar_px=2.2, min_sep_px=2.9)
    assert int(empty.sum()) == 0

    emitted = emit_submodular_300m(sharp, dom, vis, 40, b_collar_px=2.2, min_sep_px=2.9)
    assert 1 <= int(emitted.sum()) <= 40
    assert not np.any(emitted & ~dom)
    assert not np.any(emitted & vis)

    # Verify strict Euclidean inter-dot spacing > 2.9 px
    ys, xs = np.nonzero(emitted)
    pts = np.column_stack([ys, xs]).astype(np.float64)
    if len(pts) >= 2:
        dists, _ = cKDTree(pts).query(pts, k=2)
        assert float(dists[:, 1].min()) > 2.9 - 1e-6


def test_historical_leakage_canary_is_not_a_clearance() -> None:
    canary = json.loads((EVIDENCE_DIR / "leakage_canary_58ch.json").read_text())
    assert canary["n_channels_tested"] == 58
    assert canary["original_all_passed_superseded"] is True
    assert canary["all_passed"] is False
    assert "not established" in canary["validation_status"].lower()


def test_geotiff_and_zip_contract_zero_human_inspection() -> None:
    rc = json.loads((EVIDENCE_DIR / "run_card_hmas_sinter.json").read_text())
    tif_path = DOWNLOADS_DIR / rc["submission_file"]
    zip_path = DOWNLOADS_DIR / rc["submission_zip"]
    rec_path = tif_path.with_suffix(".json")

    assert tif_path.is_file()
    assert zip_path.is_file()
    assert rec_path.is_file()

    # Check world-readable permissions (0o644) for static web servers
    for p in (tif_path, zip_path, rec_path):
        mode = stat.S_IMODE(p.stat().st_mode)
        assert mode & stat.S_IROTH, f"{p.name} is not world-readable: {oct(mode)}"

    tif_bytes = tif_path.read_bytes()
    assert hashlib.sha256(tif_bytes).hexdigest() == rc["raster_sha256"]
    assert hashlib.sha256(zip_path.read_bytes()).hexdigest() == rc["zip_sha256"]

    with zipfile.ZipFile(zip_path) as zf:
        assert zf.namelist() == [tif_path.name]
        assert zf.read(tif_path.name) == tif_bytes

    with rasterio.open(tif_path) as ds:
        assert ds.count == 1
        assert ds.dtypes[0] == "float32"
        assert (ds.height, ds.width) == (G57.HEIGHT, G57.WIDTH)
        assert str(ds.crs) == G57.CRS_EPSG
        assert tuple(ds.transform)[:6] == tuple(G57.TRANSFORM)[:6]
        arr = ds.read(1)
        assert np.isfinite(arr).all()
        assert int(np.isnan(arr).sum()) == 0
        assert float(arr.min()) >= 0.0
        assert float(arr.max()) <= 1.0

    ddir = data_dir()
    if (ddir / "sample_submission.tif").is_file() and (ddir / "labels.tif").is_file():
        with rasterio.open(ddir / "sample_submission.tif") as ds_s:
            foot = np.isfinite(ds_s.read(1))
            assert tuple(ds_s.transform)[:6] == tuple(G57.TRANSFORM)[:6]
        with rasterio.open(ddir / "labels.tif") as ds_l:
            cat = (ds_l.read(1) > 0.5) & foot
        rep = validate(tif_path, foot, cat)
        assert_submittable(rep)
        assert rep["all_checks_passed"] is True
        assert rep["on_catalogue_positive_pixels"] == 0


def test_historical_fleet_uniqueness_is_superseded_by_lattice() -> None:
    uniq = json.loads((EVIDENCE_DIR / "fleet_uniqueness_593.json").read_text())
    audit = json.loads((EVIDENCE_DIR / "candidate_audit_20261028.json").read_text())
    lattice = audit["candidates"][0]["comparisons"][0]
    assert uniq["original_passed_superseded"] is True
    assert uniq["passed"] is False
    assert lattice["reference"] == "lattice" and lattice["overlap_exceeds_70_percent"]
    assert lattice["candidate_dots_within_3px"] == 38174
    assert lattice["candidate_dots"] == 38200
    assert uniq["literal_lattice_overlap"] == lattice["directed_overlap"]
    assert audit["registry_complete"] is False


def test_run_card_and_protocol_budget() -> None:
    rc = json.loads((EVIDENCE_DIR / "run_card_hmas_sinter.json").read_text())
    required_keys = {
        "hypothesis",
        "mechanism",
        "mimic_process",
        "holdout_dti",
        "registry_correlation_overlap",
        "raster_sha256",
        "validator_output",
        "submission_name",
        "submission_note",
        "verdict",
    }
    assert required_keys.issubset(rc.keys())
    assert 1 <= len(rc["submission_note"]) <= 140
    assert rc["verdict"] == "negative" and rc["ok_to_submit"] is False

    led = json.loads((EVIDENCE_DIR / "experiments_summary.json").read_text())
    exp_arms = [k for k in led["arms"] if k.startswith("EXP")]
    assert len(exp_arms) <= 3, "Protocol Rule 6: max 3 experiments!"


def test_pages_ui_and_readme_integrity() -> None:
    lane_dir = DOCS_DIR / "hmas-sinter"
    idx = (lane_dir / "index.html").read_text()
    exe = (lane_dir / "executive-summary.html").read_text()
    readme = (REPO_ROOT / "README.md").read_text()

    assert "OK TO SUBMIT" in idx or "DO NOT SUBMIT" in idx
    assert "human inspector" not in idx.lower()
    assert "TODO" not in idx

    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert site in idx
        assert site in readme

    # Verify all relative href/src assets referenced in docs/hmas-sinter/{index,executive-summary}.html exist
    for html_doc in (idx, exe):
        for ref in re.findall(r'(?:href|src)="([^"#]+)"', html_doc):
            if ref.startswith(("http://", "https://", "mailto:", "javascript:")):
                continue
            target = (lane_dir / ref).resolve()
            assert target.exists(), f"Broken relative link in HTML: {ref} -> {target}"
