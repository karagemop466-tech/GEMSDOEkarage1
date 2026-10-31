"""Regression checks for the 2026-10-31 review-only, fail-closed site state."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")


def test_current_run_card_is_explicitly_negative_and_measurements_are_null():
    card = json.loads((ROOT / "evidence/session_cd6c8044_run_card.json").read_text())
    assert card["session"] == "arena/cd6c8044-gemsdoekarage1"
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["new_candidate_generated"] is False
    assert card["download_available"] is False
    assert card["slot_selected_or_spent"] is False
    assert card["geological_experiments_run"] == 0
    assert card["holdout_dti"]["label"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["value"] is None
    assert card["holdout_dti"]["evaluator_version"] is None
    assert card["holdout_dti"]["withheld_positives"] is None
    assert card["holdout_dti"]["ci95"] is None
    assert card["raster_sha256"] is None
    assert card["validator_output"]["values_in_0_1"] is None


def test_nine_focus_sites_have_pages_and_review_table_does_not_claim_estimates():
    review = (ROOT / "knowledge/session-review-arena-cd6c8044.md").read_text()
    assert "Organizer-score estimate" in review
    assert "USER-REPORTED / UNVERIFIED" in review
    for site in SITES:
        assert f"| {site} |" in review
        page = ROOT / "docs" / f"{site}.html"
        assert page.is_file()
        text = page.read_text()
        assert "DO NOT SUBMIT" in text
        assert "USER-REPORTED" in text
    assert review.count("| Historical learning reference only; DO NOT RESUBMIT |") == 9


def test_hypothesis_queue_has_five_and_no_numeric_score_projection():
    doc = (ROOT / "knowledge/hypotheses-20261031.md").read_text()
    table = doc.split("## Preregistered validation order and gates", 1)[0]
    candidates = re.findall(r"\|\s*[1-5]\s*\| \*\*H-[A-Z-]+:", table)
    assert len(candidates) == 5
    assert "No numeric DTI forecast" in table
    assert "H-EULER" in doc and "no Euler deconvolution implementation" in doc
    assert "not a numeric leaderboard-score projection" in doc


def test_live_public_snapshot_is_labeled_and_not_a_focus_receipt():
    snapshot = json.loads((ROOT / "evidence/leaderboard_snapshot_20261031.json").read_text())
    assert snapshot["source_class"] == "ORGANIZER-PUBLIC"
    assert snapshot["observations"]["rank_1_score"] == 0.4544
    assert snapshot["observations"]["rank_50_score"] == 0.3195
    assert "not confirmed" in snapshot["focus_site_scores"].lower()


def test_readme_points_to_latest_review_and_standing_prompt_correction():
    readme = (ROOT / "README.md").read_text()
    standing = (ROOT / "docs/standing-prompt.md").read_text()
    assert "session `arena/cd6c8044-gemsdoekarage1`" in readme
    assert "evidence/session_cd6c8044_run_card.json" in readme
    assert "#50 = **0.3195**" in readme
    assert "Current addendum (31 Oct 2026)" in standing
    assert "knowledge/hypotheses-20261031.md" in standing
