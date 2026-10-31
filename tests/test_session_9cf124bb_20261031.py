"""Session arena/9cf124bb (31 Oct 2026): regression checks for the E1 record, the candidate bytes,
the GEMSDOE32 subset claim, and the nine-site overlap claims. Everything is recomputed from
committed files where possible; nothing here clears a submission."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "vendor")]
from gems57 import uniqueness as UQ  # noqa: E402

CAND = "docs/downloads/DO-NOT-SUBMIT_karage1-o2-lidar-scarp-halo-prune-37654-20261031"


def _load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_e1_record_is_negative_and_not_cleared():
    e = _load("evidence/exp_o2_halo_prune_lidar_20261031.json")
    assert e["verdict"] == "negative"
    assert e["ok_to_submit"] is False
    crit = e["criteria"]
    # The pre-registered rule: these must be false for the verdict to stand.
    for key in ("b_beats_unpruned_A", "b_beats_matched_random", "canary_all_features_below_0_90",
                "registry_dot_overlap_le_0_70", "b_beats_h_r1_reference_control"):
        assert crit[key] is False, key
    assert crit["validator_passed"] is True and crit["nan_twin_passed"] is True


def test_run_card_matches_experiment_and_is_fail_closed():
    card = _load("evidence/run_card_arena_9cf124bb_20261031.json")
    e = _load("evidence/exp_o2_halo_prune_lidar_20261031.json")
    assert card["schema"] == "karage1-run-card-v1"
    assert card["session"] == "arena/9cf124bb-gemsdoekarage1"
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["slot_selected_or_spent"] is False
    assert card["geological_experiments_run"] <= 3
    h = card["holdout_dti"]
    assert h["label"] == "HOLDOUT-DTI" and h["evaluator"] == "gems57-pooled-hide-v2"
    assert h["withheld_positives"] == 45260 and h["cells"] == 16
    arm_b = e["holdout_DTI"]["arm_B_halo_pruned"]["pooled_dti"]
    # The card stores 6 decimal places; tolerance is half a unit in the sixth decimal.
    assert abs(h["value"] - arm_b) <= 5e-7
    assert abs(h["arm_B_halo_pruned_leak_free"] - arm_b) <= 5e-7
    assert abs(h["arm_A_unpruned"] - e["holdout_DTI"]["arm_A_unpruned"]["pooled_dti"]) <= 5e-7
    assert card["raster_sha256"] == _sha(f"{CAND}-zeros.tif")
    assert card["nan_twin_sha256"] == _sha(f"{CAND}-nan.tif")
    assert len(card["submission_note"]) <= 140


def test_candidate_zeros_file_meets_format_and_matches_receipt():
    tif = ROOT / f"{CAND}-zeros.tif"
    receipt = _load("evidence/audit_o2_candidate_zeros_20261031.json")
    assert receipt["sha256"] == _sha(f"{CAND}-zeros.tif")
    assert receipt["ok_to_submit"] is False
    with rasterio.open(tif) as s:
        a = s.read(1)
        assert s.count == 1 and s.dtypes[0] == "float32"
        assert str(s.crs) == "EPSG:32611" and s.shape == (3730, 3292)
        assert tuple(s.transform)[:6] == (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
    assert not np.isnan(a).any()
    assert float(a.min()) >= 0.0 and float(a.max()) <= 1.0
    assert int((a > 0).sum()) == receipt["positives"] == 37539


def test_candidate_nan_twin_is_nan_outside_footprint_only():
    rec = _load("evidence/audit_o2_candidate_nan_20261031.json")
    assert rec["sha256"] == _sha(f"{CAND}-nan.tif")
    # Known and documented: the repo all-finite policy rejects NaN, the organizer permits it.
    assert rec["nan_count"] > 0 and rec["format_report_ok"] is False
    with rasterio.open(ROOT / f"{CAND}-nan.tif") as s:
        a = s.read(1)
    zeros = np.nan_to_num(_read(ROOT / f"{CAND}-zeros.tif"), nan=0.0)
    finite = np.isfinite(a)
    assert np.array_equal(np.nan_to_num(a, nan=0.0), zeros)
    assert finite.sum() == 12279160 - rec["nan_count"]


def _read(path: Path):
    with rasterio.open(path) as s:
        return s.read(1)


def test_gemsdoe32_is_strict_subset_of_gemsdoe25_minus_6436():
    f25 = _read(ROOT / "registry/GEMSDOE25_d28.tif")
    f32 = _read(ROOT / "registry/GEMSDOE32_B2.tif")
    d25 = f25 > 0
    d32 = f32 > 0
    assert int(d25.sum()) == 44090 and int(d32.sum()) == 37654
    assert not (d32 & ~d25).any(), "GEMSDOE32 adds a dot"
    assert int((d25 & ~d32).sum()) == 6436


def test_gemsdoe32_forward_overlap_with_gemsdoe24_recomputes_to_one():
    a = _read(ROOT / "registry/GEMSDOE32_B2.tif")
    b = _read(ROOT / "registry/GEMSDOE24_gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif")
    b = np.nan_to_num(b, nan=0.0)
    assert abs(UQ.dot_overlap(a, b) - 1.0) < 1e-9


def test_archived_hunq1_comparison_recorded_with_metric_method():
    g = _load("evidence/gate_archived_hunq1_20261031.json")
    assert g["radius_m"] == 300.0
    assert all(c["ok_under_0_70_literal_gate"] is True for c in g["compared"])
    assert g["ok_to_submit"] is False


def test_hypothesis_h_o2_is_not_marked_validated():
    text = (ROOT / "knowledge/hypotheses-9cf124bb-20261031.md").read_text(encoding="utf-8")
    assert "Validated this session (E1)" not in text
    assert "NEGATIVE" in text


def test_readme_leads_with_core_values_and_current_review():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    head = text[:4000]
    assert head.index("CORE VALUES") < head.index("CURRENT SESSION — `arena/fd3e38cf-gemsdoekarage1`")
    assert "Maximize P(Win)" in head and "Own the Outcome" in head
    assert "normalized copy" in text
