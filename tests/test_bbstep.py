"""BB-STEP session: unique vs nine sites, lattice stop, labeled holdout, format."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]


def test_bbstep_card_is_fail_closed_and_labeled():
    card = json.loads((ROOT / "docs/data/run-card.json").read_text())
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["slot_selected_or_spent"] is False
    assert card["lane"] == "H-K1-BBSTEP"
    dti = card["holdout_dti"]
    assert dti["label"] == "HOLDOUT-DTI"
    assert dti["evaluator_version"] == "gemsk-hide-recover-v1"
    assert dti["withheld_positives"] == 60988
    assert len(dti["ci95"]) == 2 and dti["ci95"][0] < dti["value"] < dti["ci95"][1]
    assert 0.0 < dti["value"] < 0.1
    assert len(card["submission_note"]) <= 140
    assert "DO NOT SUBMIT" in card["submission_note"]


def test_bbstep_bytes_match_card_and_range():
    card = json.loads((ROOT / "docs/data/run-card.json").read_text())
    path = ROOT / "docs/downloads" / card["submission_name"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == card["raster_sha256"]
    with rasterio.open(path) as src:
        a = src.read(1)
        assert src.count == 1 and src.dtypes[0] == "float32"
        assert src.crs.to_epsg() == 32611
        assert a.shape == (3730, 3292)
        assert np.isfinite(a).all()
        assert float(a.min()) >= 0.0 and float(a.max()) <= 1.0
        assert int((a > 0).sum()) == 17766


def test_bbstep_unique_vs_nine_not_vs_lattice():
    uniq = json.loads((ROOT / "evidence/bbstep_uniqueness.json").read_text())
    assert uniq["unique_vs_nine_focus_sites"] is True
    assert uniq["lattice_duplicate_literal"] is True
    assert uniq["lattice_overlap"] > 0.70
    focus = [r for r in uniq["rows"] if r["id"] != "lattice"]
    assert len(focus) == 9
    assert max(r["frac_our_dots_within_3px"] for r in focus) <= 0.70
    assert max(abs(r["spearman_surface"]) for r in focus) <= 0.90


def test_canary_no_leakage_alarm():
    canary = json.loads((ROOT / "evidence/exp1_bbstep_canary.json").read_text())
    assert canary["any_alarm"] is False
    assert max(r["mean_auc"] for r in canary["rows"]) <= 0.90
    assert all(r["reads_labels"] is False for r in canary["rows"])
