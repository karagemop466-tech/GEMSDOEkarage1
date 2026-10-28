"""DIPDUAL lane: synthetic emission tests + saved-byte run-card consistency.

The synthetic tests need no competition data. The run-card test reopens the
committed GeoTIFF bytes and fails if the card's hash, gates or verdict drift
from the evidence JSON files.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio

from gemskarage1.dipdual import emit_dual

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "evidence" / "run_card_dipdual_20261028.json"


def _synthetic():
    rng = np.random.default_rng(7)
    shape = (80, 90)
    exposed = rng.random(shape).astype(np.float32)
    buried = rng.random(shape).astype(np.float32)
    dual = np.maximum(exposed, buried)
    exp_reg = np.zeros(shape, bool); exp_reg[:, :45] = True
    bur_reg = ~exp_reg
    visible = np.zeros(shape, bool); visible[40, :] = True
    return exposed, buried, dual, exp_reg, bur_reg, visible


def test_emit_dual_respects_apron_regimes_and_budget():
    exposed, buried, dual, exp_reg, bur_reg, visible = _synthetic()
    dots, info = emit_dual(exposed, buried, exp_reg, bur_reg, dual, visible,
                           budget=120, frac_exposed=0.65, spacing=2.8, apron_px=2)
    from scipy import ndimage
    dvis = ndimage.distance_transform_edt(~visible)
    assert info["n_total"] == int(dots.sum()) <= 120
    assert not (dots & visible).any()
    assert (dvis[dots] > 2).all(), "apron violated"
    # Regime quotas hold up to top-up (none expected on dense random surfaces)
    assert info["n_topup"] == 0
    assert int((dots & exp_reg).sum()) == info["n_exposed"]
    assert int((dots & bur_reg).sum()) == info["n_buried"]
    # Minimum spacing: no two dots closer than 2.8 px (check via dilation)
    ys, xs = np.nonzero(dots)
    pts = np.stack([ys, xs], axis=1).astype(float)
    for i in range(len(pts)):
        d = np.hypot(*(pts - pts[i]).T)
        assert (np.sort(d)[1] >= 2.8) if len(pts) > 1 else True


def test_emit_dual_topup_when_regime_exhausted():
    exposed, buried, dual, exp_reg, bur_reg, visible = _synthetic()
    buried[:] = 0.0  # buried regime has no candidates at all
    dots, info = emit_dual(exposed, buried, exp_reg, bur_reg, dual, visible,
                           budget=60, frac_exposed=0.5, spacing=2.8, apron_px=2)
    assert info["n_buried"] == 0
    assert info["n_topup"] > 0
    assert int(dots.sum()) == info["n_total"] <= 60


@pytest.mark.skipif(not CARD.exists(), reason="DIPDUAL run card not generated")
def test_run_card_matches_saved_bytes_and_evidence():
    card = json.loads(CARD.read_text())
    tif = ROOT / "docs" / "downloads" / card["submission_name"]
    assert tif.exists()
    assert hashlib.sha256(tif.read_bytes()).hexdigest() == card["raster_sha256"]
    assert card["verdict"] in {"promote", "negative"}
    assert card["ok_to_submit"] is False
    assert card["slot_selected_or_spent"] is False
    assert len(card["submission_note"]) <= 140
    hd = card["holdout_dti"]
    assert hd["label"] == "HOLDOUT-DTI" and hd["evaluator_version"]
    assert hd["withheld_positives"] and hd["ci95"] and len(hd["ci95"]) == 2
    exp2 = json.loads((ROOT / "evidence" / "exp2_dipdual_holdout.json").read_text())
    assert hd["value"] == exp2["blocked"]["DIPDUAL"]["dti"]
    with rasterio.open(tif) as src:
        a = src.read(1)
        assert src.count == 1 and src.dtypes[0] == "float32"
        assert src.crs.to_epsg() == 32611
        assert (src.height, src.width) == (3730, 3292)
    assert np.isfinite(a).all() and a.min() >= 0.0 and a.max() <= 1.0
    assert int((a > 0).sum()) == card["emit_info"]["n_total"]
    if card["verdict"] == "negative":
        assert card["blockers"], "negative verdict must name its blockers"
