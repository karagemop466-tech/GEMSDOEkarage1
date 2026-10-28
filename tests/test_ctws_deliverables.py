"""End-to-end automated contract, physics, canary, uniqueness, and Pages tests for Lane H-K1-2 (CTWS-2D)."""
from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

import numpy as np
import rasterio
from scipy.spatial import cKDTree

from gems57 import grid as G57
from gems57.validate import assert_submittable, validate
from gemskarage1.ctws_lane import (
    CTWS_LIDAR_INDICES,
    CTWS_MSUB_INDICES,
    CTWS_STATIC_CHANNELS,
    CTX2D_NAMES,
    STRUCTURAL_NAMES,
    compute_visible_structural_stack,
    emit_ctws_dual_regime_300m,
)
from gemskarage1.paths import DOCS_DATA_DIR, DOCS_DIR, DOWNLOADS_DIR, EVIDENCE_DIR, REPO_ROOT, data_dir
from scripts import release_gate

OFFICIAL_LINKS = (
    "https://docs.nlr.gov/docs/fy26osti/96647.pdf",
    "https://github.com/drivendataorg/gems-prize-reference-solution",
    "https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and",
    "https://gbcge.org/current-projects/ingenious/",
    "https://gdr.openei.org/submissions/1391",
    "https://epsg.io/32611",
    "https://en.wikipedia.org/wiki/Tversky_index",
)


def test_ctws_channel_schema_and_lidar_quarantine() -> None:
    assert len(CTWS_STATIC_CHANNELS) == 69
    assert len(CTWS_MSUB_INDICES) == 56
    assert len(CTX2D_NAMES) == 18
    assert len(STRUCTURAL_NAMES) == 10
    assert "st_tip_cone" not in STRUCTURAL_NAMES, "Cut-endpoint leaking feature must remain quarantined"
    for idx in CTWS_MSUB_INDICES:
        assert idx not in CTWS_LIDAR_INDICES
        assert not CTWS_STATIC_CHANNELS[idx].startswith("lidar_")


def test_visible_structural_stack_and_dual_regime_emitter_contracts() -> None:
    rng = np.random.default_rng(20261028)
    vis = np.zeros((80, 80), dtype=bool)
    vis[20:42, 22] = True
    vis[38:62, 30] = True
    dom = np.ones((80, 80), dtype=bool)
    dom[:3, :] = False
    p2 = rng.uniform(0.05, 0.95, size=(80, 80)).astype(np.float32)
    c2 = np.ones((80, 80), dtype=np.float32)
    s2 = np.zeros((80, 80), dtype=np.float32)

    st = compute_visible_structural_stack(vis, dom, p2, c2, s2)
    assert st.shape == (10, 80, 80)
    assert np.isfinite(st).all()
    assert float(np.abs(st[:, ~dom]).max()) == 0.0

    p3 = rng.uniform(0.05, 0.95, size=(80, 80)).astype(np.float32)
    em = emit_ctws_dual_regime_300m(p3, p2, dom, vis, 45, b_collar_px=2.2, min_sep_px=2.9)
    assert 1 <= int(em.sum()) <= 45
    assert not np.any(em & ~dom)
    assert not np.any(em & vis)

    ys, xs = np.nonzero(em)
    pts = np.column_stack([ys, xs]).astype(np.float64)
    if len(pts) >= 2:
        dists, _ = cKDTree(pts).query(pts, k=2)
        assert float(dists[:, 1].min()) > 2.9 - 1e-6


def test_ctws_97_feature_leakage_canary_passes() -> None:
    canary = json.loads((EVIDENCE_DIR / "leakage_canary_ctws2d.json").read_text())
    assert canary["n_features_tested"] == 97
    assert canary["all_features_tested"] is True
    assert canary["all_passed"] is True
    assert canary["leaking_features"] == []
    assert canary["max_direction_invariant_auc"] <= 0.90
    assert all(0.0 <= float(v) <= 0.90 for v in canary["feature_aucs"].values())


def test_ctws_geotiff_validator_uniqueness_and_release_gate() -> None:
    rc = json.loads((EVIDENCE_DIR / "run_card_ctws2d.json").read_text())
    rg = json.loads((EVIDENCE_DIR / "release_gate_ctws2d.json").read_text())
    uniq = json.loads((EVIDENCE_DIR / "fleet_uniqueness_ctws2d.json").read_text())
    active = json.loads((DOCS_DATA_DIR / "run-card.json").read_text())

    assert rg["result"]["verdict"] == "promote" and rg["result"]["reasons"] == []
    assert release_gate.assess(rg["input"])["verdict"] == "promote"
    assert active["raster_sha256"] == rc["raster_sha256"]
    assert 1 <= len(rc["submission_note"]) <= 140
    assert rc["experiments"] == 3 and len(rc["experiment_arms"]) == 3
    assert 0 < rc["elapsed_seconds"] <= 7200

    # Verify holdout superiority over prior-session H-K1-1 across primary & whole-component evaluators
    assert rc["holdout"]["dti"] > rc["holdout"]["current_best_dti"]
    assert rc["holdout"]["detached_dti"] > rc["holdout"]["current_best_detached_dti"]
    assert rc["holdout"]["delta_vs_hk1_all"]["ci95"][0] > 0.0
    assert rc["holdout"]["delta_vs_hk1_detached"]["ci95"][0] > 0.0
    assert rc["holdout_dti"]["hide_recover_v3_detached600m"]["delta_vs_ref_ci95"][0] > 0.0

    # Verify 834-raster fleet uniqueness
    assert uniq["passed"] is True
    assert uniq["total_fleet_rasters_scanned"] >= 830
    assert uniq["exact_hash_matches"] == []
    assert uniq["max_pre_placement_surface_spearman"] <= 0.90
    assert uniq["max_final_dot_spearman"] <= 0.90
    assert uniq["max_discrete_submission_3px_overlap"] <= 0.70

    tif_p = DOWNLOADS_DIR / rc["submission_file"]
    zip_p = DOWNLOADS_DIR / rc["submission_zip"]
    rec_p = DOWNLOADS_DIR / rc["submission_receipt"]
    for p in (tif_p, zip_p, rec_p):
        assert p.is_file()
        assert stat.S_IMODE(p.stat().st_mode) & stat.S_IROTH

    tif_bytes = tif_p.read_bytes()
    assert hashlib.sha256(tif_bytes).hexdigest() == rc["raster_sha256"]
    assert hashlib.sha256(zip_p.read_bytes()).hexdigest() == rc["zip_sha256"]
    with zipfile.ZipFile(zip_p) as zf:
        assert zf.namelist() == [tif_p.name]
        assert zf.read(tif_p.name) == tif_bytes

    with rasterio.open(tif_p) as ds:
        assert ds.count == 1
        assert ds.dtypes[0] == "float32"
        assert (ds.height, ds.width) == (G57.HEIGHT, G57.WIDTH)
        assert str(ds.crs) == G57.CRS_EPSG
        assert tuple(ds.transform)[:6] == tuple(G57.TRANSFORM)[:6]
        arr = ds.read(1)
        assert np.isfinite(arr).all()
        assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
        assert int((arr > 0).sum()) == 38_200

    ddir = data_dir()
    if (ddir / "sample_submission.tif").is_file() and (ddir / "existing_faults.tif").is_file():
        with rasterio.open(ddir / "sample_submission.tif") as ds_s:
            foot = np.isfinite(ds_s.read(1))
        with rasterio.open(ddir / "existing_faults.tif") as ds_c:
            cat = (ds_c.read(1) > 0) & foot
        rep = validate(tif_p, foot, cat)
        assert_submittable(rep)
        assert rep["on_catalogue_positive_pixels"] == 0


def test_ctws_pages_links_official_urls_and_readme_prompt() -> None:
    class LinkParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.links: list[str] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            d = dict(attrs)
            for k in ("href", "src"):
                if d.get(k):
                    self.links.append(str(d[k]))

    ctws_idx = DOCS_DIR / "ctws-2d" / "index.html"
    ctws_exe = DOCS_DIR / "ctws-2d" / "executive-summary.html"
    readme_txt = (REPO_ROOT / "README.md").read_text()

    for page in (ctws_idx, ctws_exe):
        txt = page.read_text()
        assert "TODO" not in txt
        lp = LinkParser()
        lp.feed(txt)
        for link in lp.links:
            u = urlparse(link)
            if u.scheme or u.netloc or link.startswith("mailto:"):
                continue
            target = (page.parent / unquote(u.path)).resolve() if u.path else page
            assert target.exists(), f"Broken local link in {page}: {link}"

    idx_txt = ctws_idx.read_text()
    for url in OFFICIAL_LINKS:
        assert url in idx_txt, f"Missing official URL in CTWS-2D dashboard: {url}"
        assert url in readme_txt, f"Missing official URL in README.md: {url}"

    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert site in idx_txt
        assert site in readme_txt

    assert "Fallback Data Links (Dropbox)" in readme_txt
    assert "Parallel-Run Protocol:" in readme_txt
