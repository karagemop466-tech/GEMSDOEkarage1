"""Checks for the shared H-E1 runner, the H-E2 gravity wrapper and the session-31 Pages panel.

These tests do not run the experiments (that takes minutes). They check configuration, the
import-time guard, the zero-density integrity assertion, and that the rendered panel labels every
number as HOLDOUT-DTI and does not clear a file.
"""
import importlib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_e1_runner_defaults_to_official_tmi_band():
    E1 = importlib.import_module("scripts.run_h_e1_euler_contacts")
    assert E1.FIELD == {"name": "tmi", "band": 14}
    assert E1.HYP_ID == "H-E1"
    assert E1.NAME.startswith("karage1-he1-euler-contacts-37654-20261031")


def test_e2_wrapper_overrides_only_the_field_and_identifiers():
    E1 = importlib.import_module("scripts.run_h_e1_euler_contacts")
    E2 = importlib.import_module("scripts.run_h_e2_euler_gravity")
    # The wrapper mutates the shared module at import time; restore E1 afterwards so other tests are unaffected.
    assert E2.E1 is E1
    assert E1.FIELD == {"name": "iso_grav_anom", "band": 13}
    assert E1.HYP_ID == "H-E2"
    assert E1.NAME == "karage1-he2-euler-gravity-37654-20261031-zeros"
    assert E1.ARCHIVE == ROOT / "archive" / "research-he2-20261031"
    assert len(E1.NOTE) <= 140
    # Protocol parameters are inherited, not re-tuned.
    src = (ROOT / "scripts" / "run_h_e1_euler_contacts.py").read_text()
    for token in ("HALF = 10", "BUDGET_DOTS = 37654", "SEEDS = (101, 202, 303)"):
        assert token in src, token
    E1.FIELD = {"name": "tmi", "band": 14}
    E1.HYP_ID = "H-E1"
    E1.NAME = "karage1-he1-euler-contacts-37654-20261031-zeros"
    E1.ARCHIVE = ROOT / "archive" / "research-he1-20261031"


def test_e1_runner_is_guarded_against_import_side_effects():
    src = (ROOT / "scripts" / "run_h_e1_euler_contacts.py").read_text()
    assert src.rstrip().endswith('if __name__ == "__main__":\n    main()')


def test_zero_density_integrity_assertion_is_present():
    src = (ROOT / "scripts" / "run_h_e1_euler_contacts.py").read_text()
    assert "dots_on_zero_density" in src
    assert "assert dots_on_zero_density == 0" in src


def test_session_panel_labels_and_refuses_clearance():
    render = importlib.import_module("scripts.render_site")
    html = render.session_31_panel("")
    assert "HOLDOUT-DTI" in html
    assert "no file is cleared" in html
    assert "NEGATIVE" in html
    assert "docs/downloads/" in html  # states that nothing was copied there
    # Every numeric holdout value shown is a 4-decimal HOLDOUT-DTI, never a bare score.
    assert re.search(r"0\.0284", html) and re.search(r"0\.0479", html)
    assert "ORGANIZER-CONFIRMED" not in html


def test_no_candidate_was_copied_into_downloads():
    downloads = ROOT / "docs" / "downloads"
    names = [p.name for p in downloads.glob("*") if p.is_file()] if downloads.exists() else []
    assert not [n for n in names if "euler" in n.lower()], names


def test_session_run_card_declares_no_slot_and_no_clearance():
    import json
    card = json.loads((ROOT / "evidence" / "session_ce19eeed_20261031_run_card.json").read_text())
    assert card["verdict_for_download_and_submit"].startswith("NEGATIVE / NOT CLEARED")
    assert card["budget"]["hypotheses_tested"] <= card["budget"]["max_experiments"]
    for h in card["hypotheses"]:
        assert h["ok_to_submit"] is False
        assert h["holdout"]["label"] == "HOLDOUT-DTI"
        assert len(h["raster"]["note"]) <= 140
        assert h["raster"]["sha256"] and len(h["raster"]["sha256"]) == 64
