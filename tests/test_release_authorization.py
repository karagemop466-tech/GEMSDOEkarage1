"""Regression tests: stale lane-level receipts cannot authorize current uploads."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.release_authorization import authorization_for, load_active_status

ROOT = Path(__file__).resolve().parents[1]


def test_active_review_is_negative_and_has_no_candidate():
    status = load_active_status()
    assert status["session"] == "arena/a79c8595-gemsdoekarage1"
    assert status["verdict"] == "negative"
    assert status["ok_to_submit"] is False
    assert status["candidate_name"] is None
    assert status["slot_selected_or_spent"] is False
    card = json.loads((ROOT / "evidence/run_card_arena_a79c8595_20261031.json").read_text())
    assert card["holdout_dti"]["label"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["value"] is None and card["holdout_dti"]["ci95"] is None
    assert card["raster_sha256"] is None and card["submission_name"] is None
    assert card["verdict"] == "negative" and card["ok_to_submit"] is False


def test_historical_kp1_gate_does_not_override_active_negative_status():
    gate = json.loads((ROOT / "evidence/kp1_release_gate.json").read_text())
    assert gate["decision"]["ok_to_submit"] is True  # historical receipt, retained unmodified
    authorized, reason = authorization_for(gate)
    assert authorized is False
    assert reason


def test_authorization_requires_every_current_gate_and_exact_hash(tmp_path, monkeypatch):
    import hashlib
    import scripts.release_authorization as release_authorization
    monkeypatch.setattr(release_authorization, "ROOT", tmp_path)
    candidate = tmp_path / "research.tif"
    candidate.write_bytes(b"candidate")
    digest = hashlib.sha256(b"candidate").hexdigest()
    gate = {"sha256": digest, "tif": "research.tif"}
    try:
        status = {
            "schema": "gems-active-submission-status-v1",
            "verdict": "promote",
            "ok_to_submit": True,
            "candidate_sha256": digest,
            "gates": {
                "assigned_lane": True,
                "canonical_template": True,
                "organizer_authenticated_inputs": True,
                "preplacement_surface_registry_check": True,
                "leakage_canary": True,
                "spatial_holdout_beats_frozen_best": True,
                "final_dot_registry_check": True,
                "saved_byte_format_validation": True,
            },
            "preplacement_surface_registry": {"complete_registry_checked": True, "max_abs_spearman": 0.2},
            "final_dot_registry": {"complete_registry_checked": True, "max_forward_overlap_within_3px": 0.5},
            "leakage_canary_auc_max": 0.6,
            "validator_output": {"no_nan_inside_footprint": True, "values_in_0_1": True,
                                 "crs_shape_transform_match": True, "saved_bytes_verified": True},
            "holdout_dti": {"label": "HOLDOUT-DTI", "evaluator_version": "test-eval",
                             "withheld_positive_pixels": 10, "value": 0.2, "ci95_low": 0.1,
                             "ci95_high": 0.3, "paired_ci95_low_vs_frozen_best": 0.01},
        }
        assert authorization_for(gate, status)[0] is True
        status["gates"]["preplacement_surface_registry_check"] = False
        assert authorization_for(gate, status)[0] is False
        status["gates"]["preplacement_surface_registry_check"] = True
        status["final_dot_registry"]["max_forward_overlap_within_3px"] = 0.71
        assert authorization_for(gate, status)[0] is False
        status["final_dot_registry"]["max_forward_overlap_within_3px"] = 0.5
        status["holdout_dti"]["paired_ci95_low_vs_frozen_best"] = 0.0
        assert authorization_for(gate, status)[0] is False
        status["holdout_dti"]["paired_ci95_low_vs_frozen_best"] = 0.01
        status["candidate_sha256"] = "0" * 64
        assert authorization_for(gate, status)[0] is False
    finally:
        (ROOT / "research.tif").unlink(missing_ok=True)


def test_missing_malformed_or_nonfinite_status_fails_closed(tmp_path):
    missing = tmp_path / "missing.json"
    assert load_active_status(missing)["ok_to_submit"] is False
    malformed = tmp_path / "bad.json"
    malformed.write_text('{"schema":"gems-active-submission-status-v1","value":NaN}')
    assert load_active_status(malformed)["ok_to_submit"] is False
