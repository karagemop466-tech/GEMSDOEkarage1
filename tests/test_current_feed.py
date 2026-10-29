"""Regression checks for the current, fail-closed executive feed and research slate."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

from scripts import render_site

ROOT = Path(__file__).resolve().parents[1]
FOCUS = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")


def _load(relative: str):
    return json.loads((ROOT / relative).read_text())


def test_current_nine_site_table_links_pinned_peer_files_and_marks_all_blocked():
    html = render_site.nine_site_section("../")
    scores = _load("registry/user_reported_scores_20261029.json")
    assets = {row["id"]: row for row in _load("registry/reference_assets.json")}
    assert "SUBMISSION STATUS: NO FILE APPROVED" in html
    assert "USER-REPORTED / UNVERIFIED" in html
    assert "NO · INTERNAL STOP" in html
    assert "not a continuous-surface Spearman test" in html
    assert "not stated as an organizer rule" in html
    for site in FOCUS:
        top = max((row for row in scores["entries"] if row["site"] == site), key=lambda row: row["score"])
        asset = assets[site]
        pinned_url = ("https://raw.githubusercontent.com/" + asset["repo"] + "/" + asset["ref"] + "/"
                      + asset["path"])
        assert f"{site} ↗" in html
        assert asset["path"].rsplit("/", 1)[-1] in html
        assert pinned_url in html
        assert f"{top['score']:.4f}" in html
    assert "0.2778 USER-REPORTED / UNVERIFIED" in html
    assert html.count("DO NOT SUBMIT") == len(FOCUS)


def test_research_page_has_four_ranked_hypotheses_and_source_limits():
    html = render_site.research(1)
    assert html.count('<article class="hypothesis-card">') == 4
    for name in ("CP-DPCS", "BERB-STC", "WD-KRMT", "CF-DIKA"):
        assert name in html
    assert "not a predicted DTI gain" in html
    assert "no hypothesis was implemented or holdout-tested" in html.lower()
    assert "Area 1: 43.57 MB; Area 2: 230.54 MB" in html
    assert "Catalog availability is verified; bytes were not fetched" in html
    assert "specific tile" in html
    assert "α=0.2, β=0.8 and a 300 m triangular kernel" in html


def test_current_run_card_records_negative_no_run_and_complete_null_gates():
    card = _load("evidence/session_f40ee5b6_run_card.json")
    assert card["session"] == "arena/f40ee5b6-gemsdoekarage1"
    assert card["experiments_this_session"] == 0
    assert card["verdict"] == "negative"
    assert card["promotion_eligible"] is False
    assert card["slot_selected_or_spent"] is False
    assert card["holdout_dti"]["label"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["value"] is None
    assert card["holdout_dti"]["ci95"] is None
    assert card["correlation_overlap_vs_registry"]["continuous_surface_rank_correlation_abs"] is None
    assert card["correlation_overlap_vs_registry"]["final_dot_overlap_within_3px"] is None
    assert card["raster_sha256"] is None and card["submission_name"] is None
    assert {key: value for key, value in card["validator_output"].items() if key != "status"} == {
        "no_nan_inside_footprint": None,
        "values_in_0_1": None,
        "crs_shape_transform_match": None,
        "outside_footprint_null_or_nan": None,
    }
    assert card["submission_note_characters"] == len(card["submission_note"])
    assert card["submission_note_characters"] <= 140


def test_current_preflight_is_saved_and_fails_closed():
    preflight = _load("evidence/session_f40ee5b6_shared_preflight.json")
    assert preflight["ready_for_shared_tools"] is False
    assert preflight["ok_to_submit"] is False
    assert preflight["canonical_assignment_recorded"] is False
    assert preflight["lane"] is None
    assert len(preflight["missing"]) == 5
    integrity = _load("evidence/session_f40ee5b6_template_integrity.json")
    assert integrity["execution_authorized"] is False
    mismatches = {row["path"] for row in integrity["files"] if not row["matches"]}
    assert mismatches == {"vendor/gems57/submission_writer.py", "vendor/gems57/uniqueness.py"}


def test_readme_starts_with_current_decision_and_cites_unverified_site_reports():
    text = (ROOT / "README.md").read_text()
    assert "CURRENT FEED · 29 OCT 2026 · NEGATIVE / DO NOT SUBMIT" in text
    assert text.index("CURRENT FEED") < text.index("## Project brief and hard rules")
    assert "0.2778 USER-REPORTED / UNVERIFIED" in text
    assert "No organizer receipt tied to the GEMSDOE32 hash" in text
    assert "discrete-dot comparison, not a continuous-surface correlation" in text


def test_historical_experiment_runner_refuses_and_emits_no_tiff():
    downloads = ROOT / "docs/downloads"
    before = sorted(path.name for path in downloads.glob("*.tif"))
    result = subprocess.run(
        [sys.executable, "scripts/run_karage1_experiments.py", "--stage", "all"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert "BLOCKED: Historical H-K1-1 runner disabled" in result.stderr
    assert sorted(path.name for path in downloads.glob("*.tif")) == before


def test_built_current_pages_have_review_date_and_four_hypothesis_labels():
    index = (ROOT / "docs/index.html").read_text()
    summary = (ROOT / "docs/executive-summary.html").read_text()
    research = (ROOT / "docs/research.html").read_text()
    assert "CURRENT SUBMISSION DECISION · 29 OCT 2026" in index
    assert "No eligible submission file. No new candidate was evaluated." in index
    assert "Highest reported file, peer overlap, and download decision" in summary
    assert "CURRENT FEED · NINE FOCUS SITES · 29 OCT 2026" in summary
    for name in ("CP-DPCS", "BERB-STC", "WD-KRMT", "CF-DIKA"):
        assert name in research
    assert "DO NOT SUBMIT" in index
    assert not re.search(r"OK TO SUBMIT|CLEARED FOR SUBMISSION", index)
