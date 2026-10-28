"""End-to-end automated contract, physics, uniqueness, and UI audit tests for Lane TD-KSCK (2026-10-28)."""
from __future__ import annotations

import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.spatial import cKDTree

from gems57 import grid as G57
from gems57.validate import assert_submittable, validate
from gemskarage1.paths import DOCS_DIR, DOWNLOADS_DIR, EVIDENCE_DIR, REPO_ROOT, data_dir
from gemskarage1.td_ksck import TD_KSCK_CHANNELS


def test_td_ksck_channel_schema() -> None:
    assert len(TD_KSCK_CHANNELS) == 19
    assert "true_neg_mag_tilt_slot" in TD_KSCK_CHANNELS
    assert "mag_tilt_angle_rad" in TD_KSCK_CHANNELS
    assert "fluvial10_knick_strike_bridge_1200m" in TD_KSCK_CHANNELS
    assert "lahontan_dixie_shoreline_mimic" in TD_KSCK_CHANNELS
    assert "pluton_core_nonq_mimic" in TD_KSCK_CHANNELS


def test_td_ksck_77ch_leakage_canary() -> None:
    canary = json.loads((EVIDENCE_DIR / "leakage_canary_td_ksck_77ch.json").read_text())
    assert canary["n_channels_tested"] == 77
    assert canary["all_passed"] is True
    assert canary["leaking_features"] == []
    assert canary["max_direction_invariant_auc"] <= 0.90
    assert canary["repaired_neg_mag_tilt_nonzero_fraction"] > 0.50


def test_td_ksck_geotiff_zip_and_spacing_contract() -> None:
    rc = json.loads((EVIDENCE_DIR / "run_card_td_ksck.json").read_text())
    assert rc["verdict"] == "promote"
    assert 1 <= len(rc["submission_note"]) <= 140

    tif_path = DOWNLOADS_DIR / rc["submission_file"]
    zip_path = DOWNLOADS_DIR / rc["submission_zip"]
    rec_path = tif_path.with_suffix(".json")
    for p in (tif_path, zip_path, rec_path):
        assert p.is_file(), f"Missing deliverable {p}"
        mode = stat.S_IMODE(p.stat().st_mode)
        assert mode & stat.S_IROTH, f"{p.name} must be world-readable: {oct(mode)}"

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
        assert int(np.isinf(arr).sum()) == 0
        assert float(arr.min()) == 0.0
        assert float(arr.max()) == 1.0
        emitted = arr > 0.5
        assert int(emitted.sum()) == 37654

    # Verify strict Euclidean inter-dot spacing >= 3.18 px
    ys, xs = np.nonzero(emitted)
    pts = np.column_stack([ys, xs]).astype(np.float64)
    dists, _ = cKDTree(pts).query(pts, k=2)
    assert float(dists[:, 1].min()) > 3.18 - 1e-5

    ddir = data_dir()
    if (ddir / "sample_submission.tif").is_file() and (ddir / "labels.tif").is_file():
        with rasterio.open(ddir / "sample_submission.tif") as ds_s:
            foot = np.isfinite(ds_s.read(1))
        with rasterio.open(ddir / "labels.tif") as ds_l:
            cat = (ds_l.read(1) > 0.5) & foot
        rep = validate(tif_path, foot, cat)
        assert_submittable(rep)
        assert rep["all_checks_passed"] is True
        assert rep["on_catalogue_positive_pixels"] == 0


def test_td_ksck_holdout_improvements_and_817_fleet_uniqueness() -> None:
    exp = json.loads((EVIDENCE_DIR / "experiments_td_ksck.json").read_text())
    gate = json.loads((EVIDENCE_DIR / "release_gate_td_ksck.json").read_text())
    uniq = json.loads((EVIDENCE_DIR / "fleet_uniqueness_td_ksck.json").read_text())

    assert len([k for k in exp["arms"] if k.startswith("EXP")]) <= 3
    assert gate["result"]["verdict"] == "promote"
    assert gate["result"]["reasons"] == []

    w = exp["arms"]["EXP3_TD_KSCK_PIED_OPT"]
    b35 = exp["baselines"]["BASE_35"]
    hk1 = exp["baselines"]["PRIOR_HK1_HMAS_MULT"]
    champ = exp["baselines"]["CHAMPION_GEMSDOE32"]

    assert w["gems57_per_cell_detached"]["dti"] > hk1["gems57_per_cell_detached"]["dti"] > b35["gems57_per_cell_detached"]["dti"]
    assert w["gems57_per_cell_all"]["dti"] > hk1["gems57_per_cell_all"]["dti"] > b35["gems57_per_cell_all"]["dti"]
    assert w["hide_recover_v3_per_cell"]["detached"]["dti"] > hk1["hide_recover_v3_per_cell"]["detached"]["dti"] + 0.008
    assert w["c_pied"]["c_pied_pooled_dti"] > champ["c_pied"]["c_pied_pooled_dti"] + 0.005

    assert uniq["passed"] is True
    assert uniq["total_fleet_rasters_scanned"] >= 800
    assert uniq["exact_hash_matches"] == []
    assert uniq["max_pre_placement_surface_spearman"] <= 0.90
    assert uniq["max_final_dot_spearman"] <= 0.90
    assert uniq["max_discrete_submission_3px_overlap"] <= 0.70

    hk1_ov = next(r for r in uniq["top_25_closest_discrete_submissions"] if "hmas-sinter-dualcover" in r["path"])
    assert hk1_ov["ov_cand_in_ref"] <= 0.70
    assert hk1_ov["ov_sym_max"] <= 0.70


def test_td_ksck_ui_consistency_and_irregularity_resolutions() -> None:
    rc = json.loads((EVIDENCE_DIR / "run_card_td_ksck.json").read_text())
    sha_prefix = rc["raster_sha256"][:16]

    for rel in ("index.html", "executive-summary.html", "docs/index.html", "docs/executive-summary.html", "docs/td-ksck/index.html", "docs/td-ksck/executive-summary.html"):
        txt = (REPO_ROOT / rel).read_text()
        assert rc["submission_file"] in txt, f"{rel} missing active TD-KSCK filename"
        assert sha_prefix in txt, f"{rel} missing active TD-KSCK SHA-256 prefix"
        # IR-KARAGE1-UI-01: ensure stale negative-session contradictions are absent
        for stale in ("No model was fit", "There is no such file now", "Nothing is approved for upload today", "No new TIFF is available to submit"):
            assert stale not in txt, f"Stale contradictory copy '{stale}' found in {rel}"

    # Verify all relative links in docs/td-ksck/*.html resolve on disk
    td_dir = DOCS_DIR / "td-ksck"
    for name in ("index.html", "executive-summary.html"):
        doc = (td_dir / name).read_text()
        for ref in re.findall(r'(?:href|src)="([^"#]+)"', doc):
            if ref.startswith(("http://", "https://", "mailto:", "javascript:")):
                continue
            target = (td_dir / ref).resolve()
            assert target.exists(), f"Broken link in docs/td-ksck/{name}: {ref} -> {target}"

    # IR-KARAGE1-ZIP-01: verify prior H-K1-1 zip hash in README matches actual disk prefix
    prior_zip = DOWNLOADS_DIR / "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.zip"
    actual_prior_zip_sha = hashlib.sha256(prior_zip.read_bytes()).hexdigest()[:12]
    readme = (REPO_ROOT / "README.md").read_text()
    assert actual_prior_zip_sha in readme
    assert "8657f37517a4" not in readme
