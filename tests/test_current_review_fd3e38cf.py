"""Regression checks for the current fail-closed decision page and run card."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "evidence/run_card_arena_fd3e38cf_20261031.json"
PAGE = ROOT / "docs/current-review-20261031.html"


def test_current_run_card_is_fail_closed_and_complete():
    card = json.loads(CARD.read_text(encoding="utf-8"))
    assert card["session"] == "arena/fd3e38cf-gemsdoekarage1"
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["download_available"] is False
    assert card["slot_selected_or_spent"] is False
    assert card["holdout_dti"]["label"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["value"] is None
    assert card["holdout_dti"]["ci95"] is None
    assert card["raster_sha256"] is None
    assert card["submission_name"] is None
    assert card["submission_note"] is None


def test_current_review_lists_all_focus_sites_without_download_links():
    from scripts.build_current_review_fd3e38cf import build

    html = build()
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert site in html
    assert "DO NOT SUBMIT — no file is cleared." in html
    assert "NOT ESTIMABLE" in html
    assert "USER-REPORTED / UNVERIFIED" in html
    assert "0.2778" in html
    assert "H-SPEC" in html
    assert not re.search(r'<a\b[^>]*\bdownload\b', html, re.IGNORECASE)
    assert not re.search(r'href=["\'][^"\']+\.tif', html, re.IGNORECASE)


def test_generator_is_reproducible_and_renders_committed_page():
    from scripts.build_current_review_fd3e38cf import main

    main()
    html = PAGE.read_text(encoding="utf-8")
    assert "Current decision and nine-site table" not in html
    assert "No download button is provided for a submission candidate" in html
    assert not re.search(r'<a\b[^>]*\bdownload\b', html, re.IGNORECASE)
