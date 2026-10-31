"""Regression guards for session arena/8e91c377 (31 Oct 2026).

These tests never grant clearance. They pin the fail-closed state: the new H-V31 raster
is NOT cleared, every submission flag is false, the lattice gate is recorded as failing,
and every number in the run card and the site block is traceable to an evidence file.
"""
import hashlib
import json
import math
import re
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

TIF = ROOT / "docs/downloads/karage1-h31-visgrad-nms3px-40k-20261031-zeros.tif"
ZIP = ROOT / "docs/downloads/karage1-h31-visgrad-nms3px-40k-20261031-zeros.zip"
SHA = ROOT / "docs/downloads/karage1-h31-visgrad-nms3px-40k-20261031-zeros.sha256"
CARD = ROOT / "evidence/run_card_h31_20261031.json"
SUMMARY = ROOT / "evidence/nine_site_executive_20261031.json"
FINAL = ROOT / "evidence/h31_final_20261031.json"
HOLD = ROOT / "evidence/h31_holdout_20261031.json"
SAVED = ROOT / "evidence/audit_h31_candidate_saved_bytes_20261031.json"
NINE = ROOT / "evidence/focus_nine_audit_20261031.json"
FORBIDDEN = ("CLEARED FOR SUBMISSION", "IT IS OK TO DOWNLOAD AND SUBMIT")


def _strict(path: Path):
    def reject(value):
        raise ValueError(f"non-standard JSON constant {value} in {path.name}")
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)


@pytest.mark.parametrize("path", [CARD, SUMMARY, FINAL, HOLD, SAVED, NINE])
def test_session_evidence_is_strict_json(path):
    _strict(path)


def test_run_card_is_negative_and_authorises_nothing():
    card = _strict(CARD)
    assert card["schema"] == "karage1-parallel-run-card-v2"
    assert card["ok_to_submit"] is False
    assert card["verdict"] == "negative"
    assert card["slot_selected_or_spent"] is False
    assert card["experiments_used"] == card["experiments_budget"] == 3
    assert card["holdout"]["label"] == "HOLDOUT-DTI"
    assert card["holdout"]["preregistered_verdict"] == "PASS_HOLDOUT_ONLY"


def test_run_card_note_and_name_within_limit():
    card = _strict(CARD)
    assert len(card["note"]) <= 140
    assert card["note_chars"] == len(card["note"])
    assert card["name"] == "karage1-h31-visgrad-nms3px-40k-20261031-zeros"


def test_lattice_gate_is_recorded_as_failing_not_hidden():
    card = _strict(CARD)
    cc = card["registry_correlation_and_overlap"]
    assert cc["lattice_gate_passes"] is False
    assert cc["lattice_forward_3px_overlap"] > 0.70
    assert "not used to evade" in cc["note"]


def test_raster_bytes_match_recorded_sha_and_zip():
    card = _strict(CARD)
    raw = TIF.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == card["raster"]["sha256"]
    assert SHA.read_text().split()[0] == card["raster"]["sha256"]
    with zipfile.ZipFile(ZIP) as zf:
        assert zf.namelist() == [TIF.name]
        assert zf.read(TIF.name) == raw


def test_validator_output_pass_and_zero_violations():
    v = _strict(FINAL)["validator"]
    assert v["pass"] is True
    assert v["nan_cells"] == 0
    assert v["in_0_1"] is True
    assert v["dots_outside_footprint"] == 0
    assert v["dots_on_catalogue"] == 0
    assert v["dots"] == 40000


def test_saved_byte_audit_agrees_and_flags_lattice():
    saved = _strict(SAVED)
    assert saved["schema"] == "karage1-local-tif-audit-v1"
    assert saved["ok_to_submit"] is False
    assert all(v is True for v in saved["checks"].values()), saved["checks"]
    assert saved["uniqueness_vs_focus_passes"] is True
    assert saved["lattice_gate_passes"] is False


def test_saved_byte_audit_matches_runner_overlaps():
    saved = _strict(SAVED)["comparisons"]
    final = _strict(FINAL)["uniqueness_vs_nine_focus"]
    for name, row in final.items():
        assert abs(saved[name]["forward_3px_overlap"] - row["fwd3_candidate_dots_within_3px_of_registry"]) < 1e-3, name


def test_holdout_numbers_and_leakage_canary():
    hold = _strict(HOLD)
    cand = hold["pooled"]["scores"]["candidate_H_V31"]
    assert hold["evaluator_version"] == "gems57-pooled-hide-v2"
    assert hold["verdict_holdout_only"] == "PASS_HOLDOUT_ONLY"
    assert cand["ci95"][0] <= cand["dti"] <= cand["ci95"][1]
    assert max(hold["leakage_canary"]["max_symmetric_auc_per_channel"].values()) <= 0.90


def test_nine_site_table_is_complete_and_fail_closed():
    summary = _strict(SUMMARY)
    rows = summary["rows"]
    assert [r["site"] for r in rows] == [f"GEMSDOE{n}" for n in (24, 25, 27, 28, 30, 31, 32, 33, 36)]
    for r in rows:
        assert r["ok_to_download_and_submit"] is False
        assert r["estimated_leaderboard_score"] == "NOT ESTIMABLE"
        assert r["reported_score"] is not None
    assert summary["candidate"]["ok_to_download_and_submit"] is False
    assert summary["candidate"]["lattice_gate_passes"] is False
    assert summary["candidate"]["unique_vs_nine_focus"] is True


def test_nine_site_uniqueness_is_measured_not_assumed():
    # Every focus file duplicates at least one sibling under the protocol rule (measured).
    rows = _strict(SUMMARY)["rows"]
    assert all(r["unique_vs_other_focus_sites"] is False for r in rows)


def test_b2_is_a_strict_subset_of_d28_and_removed_dots_are_near_catalogue():
    b2 = _strict(NINE)["b2_vs_d28"]
    assert b2["b2_subset_of_d28"] is True
    assert b2["removed_dots"] == 6436
    assert b2["removed_distance_gt2px"] == 0
    assert b2["removed_max_distance_px"] <= 2.0


def test_focus_audit_has_no_nan_anywhere():
    text = NINE.read_text()
    assert "NaN" not in text and "Infinity" not in text


def test_rendered_pages_never_claim_clearance_and_show_session_block():
    for rel in ("index.html", "docs/index.html", "docs/executive-summary.html",
                "docs/how-to-submit.html", "docs/submission-hub.html", "docs/submission-20261031.html"):
        page = (ROOT / rel).read_text(encoding="utf-8")
        for phrase in FORBIDDEN:
            assert phrase not in page, f"{rel} claims clearance: {phrase}"
    for rel in ("index.html", "docs/index.html", "docs/executive-summary.html"):
        assert 'id="session-20261031"' in (ROOT / rel).read_text(encoding="utf-8"), rel
    live = (ROOT / "docs/submission-20261031.html").read_text(encoding="utf-8")
    assert "OK to download and submit: NO." in live
    assert "NOT CLEARED" in live


def test_rendered_page_numbers_match_the_card():
    card = _strict(CARD)
    live = (ROOT / "docs/submission-20261031.html").read_text(encoding="utf-8")
    assert f'{card["holdout"]["dti"]:.4f}' in live
    assert f'{card["registry_correlation_and_overlap"]["lattice_forward_3px_overlap"]:.2%}' in live
    assert card["raster"]["sha256"] in live


def test_session_loader_refuses_a_flipped_flag(monkeypatch, tmp_path):
    import render_site
    bad = _strict(CARD)
    bad["ok_to_submit"] = True
    p = tmp_path / "card.json"
    p.write_text(json.dumps(bad))
    monkeypatch.setattr(render_site, "SESSION_CARD", p)
    with pytest.raises(ValueError):
        render_site.session_20261031()


def test_session_loader_refuses_a_changed_raster(monkeypatch, tmp_path):
    import render_site
    card = _strict(CARD)
    card["raster"]["sha256"] = "0" * 64
    p = tmp_path / "card.json"
    p.write_text(json.dumps(card))
    monkeypatch.setattr(render_site, "SESSION_CARD", p)
    with pytest.raises(ValueError):
        render_site.session_20261031()


def test_note_guard_and_no_placeholder_numbers():
    card = _strict(CARD)
    text = json.dumps(card)
    for bad in ("TBD", "TODO", "XXXX", "nan,", "NaN"):
        assert bad not in text, bad
    assert math.isfinite(card["holdout"]["dti"])
