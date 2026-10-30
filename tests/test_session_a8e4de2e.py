"""Regression tests for session arena/a8e4de2e (30 Oct 2026).

These pin the fail-closed verdict, the research-only file's format and hash,
the official leaderboard snapshot, and the consistency of the page and run card
with the evidence they are built from. None of them clears a file.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "evidence/exp_h_r1_kth_magedge_20261030.json"
CARD = ROOT / "evidence/run_card_h_r1_20261030.json"
BOARD = ROOT / "registry/leaderboard_snapshot_20261030.json"
PAGE = ROOT / "docs/session-a8e4de2e.html"
ARCH = ROOT / "archive/research-hr1-20261030"
HYP = ROOT / "knowledge/hypotheses-20261030.md"
REVIEW = ROOT / "knowledge/session-review-arena-a8e4de2e.md"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_verdict_is_fail_closed():
    exp = _load(EXP)
    card = _load(CARD)
    assert exp["verdict"] == "negative"
    assert exp["ok_to_submit"] is False and exp["slot_selected_or_spent"] is False
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False and card["slot_selected_or_spent"] is False


def test_decision_rule_criteria_are_all_evaluated_and_failed_as_recorded():
    exp = _load(EXP)
    crit = exp["criteria"]
    # Every pre-registered criterion is present; the rule passes only if all are True.
    assert set(crit) == {
        "candidate_beats_null_pooled", "paired_ci_lower_bound_gt_zero", "canary_all_below_0_90",
        "validator_passed", "registry_surface_rho_le_0_90", "registry_dot_overlap_le_0_70",
    }
    assert crit["candidate_beats_null_pooled"] is False
    assert crit["paired_ci_lower_bound_gt_zero"] is False
    assert exp["verdict"] == ("promote-to-selector" if all(crit.values()) else "negative")


def test_holdout_numbers_are_labelled_and_consistent():
    exp = _load(EXP)
    h = exp["candidate"]["holdout"]
    assert exp["evaluator"]["label"] == "HOLDOUT-DTI"
    assert exp["evaluator"]["version"] == "gems57-pooled-hide-v2"
    assert exp["evaluator"]["cells"] == 16
    lo, hi = h["ci95_cell_bootstrap_of_mean"]
    assert lo <= h["mean_cell_dti"] <= hi
    assert exp["controls"]["random_null_matched_count"]["pooled_mean"] == pytest.approx(
        float(np.mean(exp["controls"]["random_null_matched_count"]["pooled_dti_per_seed"])))
    assert exp["candidate"]["dots"] == 37654


def test_canary_all_below_alarm():
    exp = _load(EXP)
    for name, row in exp["leakage_canary"].items():
        assert row["max_direction_invariant_auc"] < 0.90, name


def test_archive_tif_matches_receipt_and_format():
    rasterio = pytest.importorskip("rasterio")
    card = _load(CARD)
    name = card["submission_name"]
    tif = ARCH / f"{name}.tif"
    assert tif.is_file()
    assert _sha(tif) == card["raster_sha256"]["zeros_primary"]
    with rasterio.open(tif) as ds:
        a = ds.read(1)
        assert ds.count == 1 and ds.dtypes[0] == "float32"
        assert ds.shape == (3730, 3292)
        assert ds.crs.to_epsg() == 32611
        assert ds.transform.a == 100.0 and ds.transform.e == -100.0
    assert not np.isnan(a).any() and not np.isinf(a).any()
    assert float(a.min()) >= 0.0 and float(a.max()) <= 1.0
    assert set(np.unique(a).tolist()) <= {0.0, 1.0}
    assert int((a > 0).sum()) == 37654


def test_archive_zip_contains_only_the_tif():
    card = _load(CARD)
    name = card["submission_name"]
    z = ARCH / f"{name}.zip"
    with zipfile.ZipFile(z) as zf:
        assert zf.namelist() == [f"{name}.tif"]
        assert zf.read(f"{name}.tif") == (ARCH / f"{name}.tif").read_bytes()


def test_name_and_note_within_limits_and_flagged_research_only():
    card = _load(CARD)
    assert len(card["submission_name"]) <= 140
    assert len(card["submission_note"]) <= 140
    assert "RESEARCH ONLY" in card["submission_note"]
    assert "do not submit" in card["submission_note"].lower()


def test_nan_twin_has_nan_exactly_outside_footprint_and_same_dots():
    rasterio = pytest.importorskip("rasterio")
    card = _load(CARD)
    name = card["submission_name"]
    twin = ARCH / f"{name.replace('-zeros', '-nan')}.tif"
    zero = ARCH / f"{name}.tif"
    assert twin.is_file()
    with rasterio.open(twin) as ds:
        b = ds.read(1)
        assert ds.nodata is not None and np.isnan(ds.nodata)
    with rasterio.open(zero) as ds:
        a = ds.read(1)
    fp = ~np.isnan(b)
    assert int(fp.sum()) == 5167373  # footprint size, pinned to the sample's finite cells
    assert np.array_equal(np.nan_to_num(b) > 0, a > 0)


def test_leaderboard_snapshot_facts():
    board = _load(BOARD)
    rows = board["rows"]
    assert len(rows) == 50
    assert [r["rank"] for r in rows] == list(range(1, 51))
    assert board["top_score"] == 0.4544 == rows[0]["public_score"]
    assert board["user_reported_0_4413_in_top_50"] is False
    assert board["user_reported_0_3195_rank"] == [48]
    assert rows[46]["public_score"] == 0.3217  # #47
    assert board["source_url"].endswith("/leaderboard/")


def test_page_and_card_agree_with_evidence():
    exp = _load(EXP)
    card = _load(CARD)
    html = PAGE.read_text(encoding="utf-8")
    assert "Can I download and submit a file from this site? NO." in html
    assert f"{exp['candidate']['holdout']['pooled_dti']:.4f}" in html
    assert card["holdout_dti"]["value"] == exp["candidate"]["holdout"]["pooled_dti"]
    assert card["raster_sha256"]["zeros_primary"] == exp["artefacts"]["zeros_primary"]["sha256"]


def test_home_strip_points_at_this_session():
    for page in (ROOT / "index.html", ROOT / "docs/index.html"):
        t = page.read_text(encoding="utf-8")
        assert "karage1-hr1-kth-magedge-37654-20261030-zeros.tif" in t
        assert "NOT CLEARED: DO NOT SUBMIT" in t


def test_hypotheses_preregistered_and_ranked():
    t = HYP.read_text(encoding="utf-8")
    for hid in ("H-R1", "H-E1", "H-G1"):
        assert hid in t
    assert "NOT TESTED" in t and "TESTED** this session" in t


def test_review_has_three_passes_and_irregularities():
    t = REVIEW.read_text(encoding="utf-8")
    for needle in ("Pass 1", "Pass 2", "Pass 3", "Irregularities", "Remaining work", "Limitations"):
        assert needle in t
