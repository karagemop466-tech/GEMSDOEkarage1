"""Regression guards for session arena/5ee7ef4b (2026-10-29).

These tests pin the session's fail-closed guarantees: the H-S1 raster is a
negative research artifact, the run card and page cannot authorise an upload,
and every pinned hash matches the bytes on disk.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIF = ROOT / "archive/research-s1-20261029/karage1-s1-tmihg-ridge-offcat-20261029-zeros.tif"
CARD = ROOT / "evidence/session_5ee7ef4b_run_card.json"
PAGE = ROOT / "docs/session-5ee7ef4b.html"
EXP1 = ROOT / "evidence/exp1_shared_holdout_calibration_20261029.json"
EXP2 = ROOT / "evidence/exp2_s1_holdout_and_uniqueness_20261029.json"
MANIFEST = ROOT / "registry/karage1_data_manifest.json"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_card_is_negative_and_authorises_nothing():
    card = json.loads(CARD.read_text())
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["slot_selected_or_spent"] is False
    assert card["promoted"] is False
    assert card["validator_ok"] is True
    assert card["holdout"]["label"] == "HOLDOUT-DTI"


def test_card_hashes_match_bytes_on_disk():
    card = json.loads(CARD.read_text())
    assert card["raster_sha256"] == _sha(TIF)
    assert card["zip_sha256"] == _sha(TIF.with_suffix(".zip"))


def test_submission_name_and_note_within_140_chars():
    card = json.loads(CARD.read_text())
    assert 1 <= len(card["submission_name"]) <= 140
    assert 1 <= len(card["submission_note"]) <= 140


def test_raster_is_format_valid_and_not_in_download_folder():
    # Format checks from the official rules (values in [0,1], float32, one band, no NaN).
    import numpy as np
    import rasterio

    with rasterio.open(TIF) as ds:
        a = ds.read(1)
        assert ds.count == 1 and ds.dtypes[0] == "float32"
        assert ds.crs.to_epsg() == 32611
    assert np.isfinite(a).all()
    assert float(a.min()) >= 0.0 and float(a.max()) <= 1.0
    # Negative artifact must not sit in the download folder that the site presents as candidates.
    assert not (ROOT / "docs/downloads" / TIF.name).exists()


def test_page_says_do_not_submit_and_never_clears():
    text = PAGE.read_text()
    assert "DO NOT SUBMIT" in text
    for forbidden in ("CLEARED FOR SUBMISSION", "OK TO DOWNLOAD AND SUBMIT", "approved for weekly slot"):
        assert forbidden.lower() not in text.lower()


def test_page_labels_every_score_source():
    text = PAGE.read_text()
    assert "USER-REPORTED" in text
    assert "HOLDOUT-DTI" in text
    assert "ORGANIZER-PUBLIC" in text


def test_lattice_witness_pin_matches_manifest():
    manifest = json.loads(MANIFEST.read_text())
    entries = [f for f in manifest["files"] if "13gems_20261001_r13-lattice" in f.get("dest", "")]
    assert len(entries) == 1
    assert entries[0]["sha256"] == "b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2"


def test_holdout_experiments_record_labels_and_cells():
    e1 = json.loads(EXP1.read_text())
    e2 = json.loads(EXP2.read_text())
    assert len(e1["cells"]) == 16
    assert e2["arm_B_holdout_faithful"]["ci95_cell_bootstrap"][0] <= e2["arm_B_holdout_faithful"]["pooled_dti"]
    assert e2["leakage_canary"]["pass_below_ceiling"] is True
    assert e2["lattice_witness"]["literal_70pct_rule_duplicate"] is True
    assert e2["uniqueness"]["exact_duplicates"] == 0


def test_no_session_tif_is_listed_as_cleared_on_home_page():
    home = (ROOT / "docs/index.html").read_text()
    assert re.search(r"CLEARED FOR SUBMISSION", home) is None
    assert "session-5ee7ef4b.html" in home
