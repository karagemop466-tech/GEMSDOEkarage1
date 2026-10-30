"""Regression checks for the fail-closed 2026-10-30 review and public status source."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "evidence/session_f077a66c_run_card.json"


def test_current_review_card_is_a_negative_non_experiment():
    card = json.loads(CARD.read_text(encoding="utf-8"))
    assert card["schema"] == "karage1-session-run-card-v1"
    assert card["session"] == "arena/f077a66c-gemsdoekarage1"
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["slot_selected_or_spent"] is False
    assert card["experiments_run"] == 0
    assert card["submission_name"] is None
    assert card["raster_sha256"] is None
    assert card["holdout_dti"]["label"] == "NOT RUN"
    assert card["holdout_dti"]["value"] is None
    assert card["holdout_dti"]["ci95"] is None
    assert card["correlation_overlap_vs_registry"]["candidate_sha256"] is None
    assert card["shared_tool_preflight"]["execution_authorized"] is False
    assert card["shared_tool_preflight"]["ready_for_shared_tools"] is False
    assert card["shared_tool_preflight"]["ok_to_submit"] is False
    assert card["leaderboard_snapshot"]["evidence_class"] == "ORGANIZER-PUBLISHED / PUBLIC LEADERBOARD SNAPSHOT"
    assert card["leaderboard_snapshot"]["public_rank_48_score"] == 0.3195
    assert card["user_reported_focus_site_scores"]["evidence_class"] == "USER-REPORTED / UNVERIFIED"
    assert card["validator_output"]["pytest"].startswith("PASS — 436 passed, 2 skipped")
    assert card["validator_output"]["site_build"].startswith("PASS — 34 decision pages")


def test_published_current_card_is_an_exact_copy_after_site_build():
    published = ROOT / "docs/data/current-review.json"
    assert published.is_file(), "run scripts/build_site.py first"
    assert published.read_bytes() == CARD.read_bytes()


def test_public_pages_put_current_status_above_archived_files():
    index = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    current = (ROOT / "docs/current-review.html").read_text(encoding="utf-8")
    hub = (ROOT / "docs/submission-hub.html").read_text(encoding="utf-8")
    research = (ROOT / "docs/research.html").read_text(encoding="utf-8")

    for page in (index, current, hub):
        assert "NEGATIVE / DO NOT SUBMIT" in page
        assert "CURRENT REVIEW" in page and "30 OCT 2026" in page
        assert "no current candidate TIFF" in page
        assert "No file is cleared" in page or "no file is cleared" in page
        assert "Current review" in page

    assert "No current TIFF to download" in current
    assert "HISTORICAL EXPERIMENT RECORD · 29 OCT 2026" in hub
    assert "ARCHIVED FILE · research only · NOT CLEARED" in hub
    assert "Download archived research TIFF" in hub
    assert "Latest run card</a>" not in index
    assert "Newest file" not in index
    assert "generated this session" not in index
    assert "Latest forensic &amp; 9-site audit" not in research
    assert "Current verified-source register" in research
    assert "Current repository review" in research


def test_submission_hub_machine_data_marks_only_an_archive():
    payload = json.loads((ROOT / "docs/data/submission-hub.json").read_text(encoding="utf-8"))
    assert payload["current_decision"].startswith("NEGATIVE / DO NOT SUBMIT")
    assert payload["current_candidate"] is None
    assert payload["archived_research_file"]["submit_authorized"] is False
    assert all("cand_fwd" not in row for row in payload["sites"])
    assert all("archived_research_forward_overlap" in row for row in payload["sites"])
