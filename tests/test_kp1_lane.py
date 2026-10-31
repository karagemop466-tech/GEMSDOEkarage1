"""Tests for lane H-KP1 (K-PROXY-DETECT), session `arena/9a378959-gemsdoekarage1`.

These tests are data-light on purpose: CI does not carry the 400 MB competition
rasters.  Everything that can be checked from committed receipts and pure
arithmetic is checked here; the deeper numeric re-derivations live in
``evidence/kp1_*.json`` and are re-run by ``scripts/kp1_*.py``.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "evidence" / "kp1_release_gate.json"
CARD = ROOT / "evidence" / "kp1_run_card.json"
EXP1 = ROOT / "evidence" / "kp1_exp1_forensics.json"
EXP2 = ROOT / "evidence" / "kp1_exp2_holdout.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def test_metric_identity_holds_exactly():
    """beta = 1 - alpha makes DTI = TP/(alpha(TP+FP)+beta|G|) an identity."""
    import sys
    sys.path.insert(0, str(ROOT / "vendor"))
    from gems57.metric import ALPHA, BETA, dti_bruteforce
    assert ALPHA + BETA == pytest.approx(1.0)
    rng = np.random.default_rng(7)
    for _ in range(5):
        truth = np.zeros((60, 60), bool)
        ys, xs = rng.integers(10, 50, size=(2, 12))
        truth[ys, xs] = True
        pred = np.zeros_like(truth, dtype=float)
        py, px = rng.integers(0, 60, size=(2, 40))
        pred[py, px] = rng.uniform(0.2, 1.0, size=40)
        r = dti_bruteforce(pred, truth)
        reduced = r["tp"] / (ALPHA * (r["tp"] + r["fp"]) + BETA * truth.sum())
        assert reduced == pytest.approx(r["dti"], abs=1e-9)


def test_release_gate_receipt_is_self_consistent():
    gate = load(GATE)
    assert gate["gate"] == "kp1-release-gate/v1"
    assert gate["decision"]["ok_to_submit"] is False
    assert gate["decision"]["registry_complete"] is False
    assert gate["decision"]["lattice_gate_passes"] is False
    assert gate["decision"]["slots_used"] == 0
    assert gate["format"]["all_checks_passed"] is True
    assert gate["format"]["checks"]["range_0_1_guaranteed"] is True
    assert gate["format"]["checks"]["no_nan_anywhere"] is True
    assert gate["format"]["checks"]["outside_footprint_zero"] is True
    assert gate["format"]["checks"]["zero_dots_on_mapped_catalogue"] is True
    assert gate["format"]["sha256"] == gate["sha256"]
    u = gate["uniqueness"]
    assert u["passes_rho_rule"] and u["passes_overlap_rule"]
    assert u["max_abs_spearman"] <= 0.90
    assert u["max_dot_overlap"] <= 0.70
    assert gate["candidate_covariates"]["d_cat_le_2px_frac"] == 0.0
    # the projection must never be labelled as a score
    assert gate["projection"]["evidence_class"].startswith("PROJECTED")
    assert "not a score" in gate["projection"]["evidence_class"]


def test_gate_describes_the_file_on_disk_when_present():
    gate = load(GATE)
    tif = ROOT / gate["tif"]
    if not tif.is_file():
        pytest.skip("competition data/artifacts are not restored in this checkout")
    digest = hashlib.sha256(tif.read_bytes()).hexdigest()
    assert digest == gate["sha256"]


def test_downloadable_tif_and_zip_exist_and_match():
    gate = load(GATE)
    tif = ROOT / gate["tif"]
    if not tif.is_file():
        pytest.skip("artifact not restored in this checkout")
    zpath = tif.with_suffix(".zip")
    rpath = tif.with_suffix(".json")
    assert zpath.is_file() and rpath.is_file()
    receipt = json.loads(rpath.read_text())
    assert receipt["sha256"] == gate["sha256"]
    assert receipt["approved_for_weekly_slot"] is False
    assert receipt["submission_slots_used"] == 0
    import zipfile
    with zipfile.ZipFile(zpath) as z:
        assert z.namelist() == [tif.name]
        assert z.read(tif.name) == tif.read_bytes()


def test_tif_passes_the_shared_validator_when_data_present():
    gate = load(GATE)
    sample = ROOT / "data" / "official" / "sample_submission.tif"
    if not sample.is_file():
        pytest.skip("competition reference grid is not restored in this checkout")
    import sys
    sys.path.insert(0, str(ROOT / "vendor"))
    from gems57 import validate
    receipt = validate.validate(ROOT / gate["tif"])
    assert receipt["all_checks_passed"], receipt["checks"]


def test_run_card_has_every_protocol_field():
    card = load(CARD)
    for key in ("hypothesis", "mechanism", "named_non_fault_process_that_could_mimic",
                "holdout_dti", "correlation_and_overlap_vs_registry", "raster_sha256",
                "validator_output", "submission_name", "submission_note", "verdict"):
        assert key in card, key
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert len(card["submission_note"]) <= 140
    assert card["slot_selected_or_spent"] is False
    assert card["holdout_dti"]["label"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["evaluator_version"]
    # the negative instrument result must stay on the record
    assert card["holdout_dti"]["instrument_calibration_spearman_vs_known_scores"] == -1.0
    assert card["raster_sha256"] == load(GATE)["sha256"]


def test_nine_site_forensics_are_labelled_and_complete():
    e1 = load(EXP1)
    assert len(e1["per_file"]) == 9
    for site, row in e1["per_file"].items():
        assert row["score_class"] == "USER-REPORTED / UNVERIFIED"
        assert 0.0 <= row["d_cat_le_2px_frac"] <= 1.0
        assert row["dots"] > 0
    # the two best-scoring files must have zero corridor mass
    best = sorted(e1["per_file"].values(), key=lambda r: -r["user_reported_score"])[:2]
    assert all(r["d_cat_le_2px_frac"] == 0.0 for r in best)
    assert len(e1["pairs"]) == 36
    assert e1["score_covariate_association"]["d_cat_gt_15px_frac"]["spearman"] == 1.0
    assert e1["score_covariate_association"]["dots"]["spearman"] < -0.9


def test_instrument_calibration_records_the_inversion():
    e2 = load(EXP2)
    cal = e2["instrument_calibration"]
    assert cal["spearman_instrument_vs_known"] == -1.0
    assert len(cal["holdout_dti"]) == 9
    assert max(cal["holdout_dti"], key=cal["holdout_dti"].get) == "GEMSDOE27"
    assert e2["leakage_canary"] and not any(v["leakage_alarm"] for v in e2["leakage_canary"].values())
    assert max(v["auc_mean"] for v in e2["leakage_canary"].values()) < 0.90
    # the run-level caveat must not present holdout DTI as a leaderboard score
    assert "not the organizer metric" in e2["caveat"]


def test_site_pages_are_rendered_from_the_gate():
    import sys
    sys.path.insert(0, str(ROOT))
    from scripts import build_kp1_site
    build_kp1_site.main()
    gate = load(GATE)
    index = (ROOT / "docs" / "kp1" / "index.html").read_text()
    assert gate["sha256"] in index
    assert f'{gate["projection"]["projected_value"]:.4f}' in index
    assert "DO NOT SUBMIT" in index and "not cleared" in index
    assert "Download the GeoTIFF" in index
    assert "Table 1" in index
    for rel in ("kp1/index.html", "kp1/executive-summary.html", "kp1/nine-sites.html",
                "kp1/how-to-submit.html", "kp1/research.html", "kp1/sources.html"):
        assert (ROOT / "docs" / rel).is_file(), rel


def test_landing_page_banner_is_fail_closed(tmp_path, monkeypatch):
    import sys
    sys.path.insert(0, str(ROOT))
    from scripts import render_site
    good = render_site.kp1_banner("")
    assert "no file cleared" in good  # gate is on hold, so the banner must demote

    # a receipt that clears nothing must demote the banner
    tampered = tmp_path / "gate.json"
    gate = load(GATE)
    gate["decision"]["ok_to_submit"] = False
    tampered.write_text(json.dumps(gate))
    monkeypatch.setattr(render_site, "KP1_GATE", tampered)
    assert "no file cleared" in render_site.kp1_banner("")

    # a receipt describing different bytes must also demote the banner
    gate["decision"]["ok_to_submit"] = True
    gate["sha256"] = "0" * 64
    tampered.write_text(json.dumps(gate))
    assert "no file cleared" in render_site.kp1_banner("")

    # a missing receipt must not raise
    monkeypatch.setattr(render_site, "KP1_GATE", tmp_path / "nope.json")
    assert "receipt is missing" in render_site.kp1_banner("")


def test_old_artifacts_are_still_marked_do_not_submit():
    index = (ROOT / "docs" / "index.html").read_text()
    assert "DO NOT SUBMIT · HOLD" in index
    assert "DO NOT SUBMIT" in index
    for name in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        page = (ROOT / "docs" / "kp1" / "nine-sites.html").read_text()
        assert name in page
        assert (ROOT / "docs" / "kp1" / "nine-sites.html").is_file()


def test_no_private_fork_of_the_shared_template():
    """The lane must reuse vendor/gems57 rather than re-implement metric or writer."""
    for name in ("kp1_data.py", "kp1_planes.py", "kp1_exp1_forensics.py",
                 "kp1_exp2_holdout.py", "kp1_build_candidate.py", "kp1_release_gate.py"):
        text = (ROOT / "scripts" / name).read_text()
        assert "gems57" in text or "kp1_data" in text, name
    writer = (ROOT / "scripts" / "kp1_build_candidate.py").read_text()
    assert "submission_writer.write_submission" in writer
    assert "def write_submission" not in writer
    metric_users = (ROOT / "scripts" / "kp1_exp2_holdout.py").read_text()
    assert "evaluate_holdout.evaluate" in metric_users
