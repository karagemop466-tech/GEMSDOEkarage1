"""Regression tests for the 2026-10-29 label-free THD-ridge candidate (verdict: NEGATIVE).

These guard three things: (1) the file is format-valid, (2) the bytes match the
evidence receipt, and (3) nothing in the evidence can be read as a clearance.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "thd_ridge_candidate_20261029.json"
NULL_CHECK = ROOT / "evidence" / "lattice_gate_null_check_20261029.json"
SAMPLE = ROOT / "data" / "sample_submission.tif"


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def receipt():
    return json.loads(EVIDENCE.read_text())


def test_evidence_is_negative_and_never_cleared(receipt):
    assert receipt["status"].startswith("NEGATIVE")
    final = receipt["final"]
    assert final["file"].startswith("archive/quarantined-20261029/DO-NOT-SUBMIT_")
    assert receipt["registry_check"]["unique"] is False
    assert receipt["registry_check"]["verdict"] == "negative"
    assert receipt["registry_check"]["stop_required"] is True
    side = json.loads((ROOT / final["file"].replace(".tif", ".json")).read_text())
    assert side["approved_for_weekly_slot"] is False and side["promoted"] is False
    assert side["submission_slots_used"] == 0


def test_holdout_numbers_are_labelled_with_n_and_ci(receipt):
    arm = receipt["arms"][receipt["selected_arm"]]
    assert arm["holdout_all"]["n_truth"] > 0
    lo, hi = arm["ci95_all"]
    assert 0.0 <= lo <= arm["holdout_all"]["dti"] <= hi <= 1.0


def test_leakage_canary_passes_for_all_19_features(receipt):
    assert len(receipt["canary"]) == 19
    assert all(c["passed"] for c in receipt["canary"])


def test_bytes_match_receipt_and_are_format_valid(receipt):
    path = ROOT / receipt["final"]["file"]
    assert _sha(path) == receipt["final"]["file_sha256"]
    if not SAMPLE.exists():
        pytest.skip("competition sample grid not restored")
    with rasterio.open(path) as ds, rasterio.open(SAMPLE) as ref:
        a = ds.read(1)
        assert ds.count == 1 and ds.dtypes[0] == "float32"
        assert (ds.height, ds.width) == (ref.height, ref.width)
        assert ds.crs.to_epsg() == 32611 == ref.crs.to_epsg()
        assert tuple(ds.transform)[:6] == tuple(ref.transform)[:6]
        fp = np.isfinite(ref.read(1))
    assert np.isfinite(a).all(), "candidate has NaN/inf"
    assert a.min() >= 0.0 and a.max() <= 1.0
    assert not a[~fp].any(), "positive mass outside footprint"
    assert int((a > 0).sum()) == receipt["final"]["dots"]


def test_null_check_shows_gate_is_non_informative():
    null = json.loads(NULL_CHECK.read_text())
    assert null["organizer_authenticated"] is False
    for n, row in null["random_dot_null"].items():
        assert row["fails_gate_in_all_draws"] is True, n
    assert null["training_features_sentinel_distinct_pixels_in_footprint_any_band"] == 3073
    assert null["labels_and_existing_faults_byte_identical"] is True
