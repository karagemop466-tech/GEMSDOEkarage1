"""Re-checks for the 2026-10-29 focus-site summary, research candidate and run card.

These tests never grant clearance. They check that the NOT CLEARED / DO NOT SUBMIT status is
consistent across the candidate file, the run card, the published page and the receipts.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))

CAND = ROOT / "docs/candidates/karage1-probcollar-gbm-K37654-collar3-20261029-nan.tif"
ZEROS = ROOT / "docs/candidates/karage1-probcollar-gbm-K37654-collar3-20261029-zeros.tif"
CARD_A = ROOT / "evidence/run_card_probcollar_20261029.json"
CARD_B = ROOT / "docs/data/run-card-probcollar-20261029.json"
PAGE = ROOT / "docs/focus-sites.html"
RECEIPTS = [
    "focus_site_table_20261029.json",
    "candidate_uniqueness_probcollar-nan_20261029.json",
    "candidate_uniqueness_probcollar-zeros_20261029.json",
    "holdout_probcollar_20261029.json",
    "holdout_probcollar_detached_20261029.json",
    "holdout_ring_tiebreak_all_20261029.json",
    "holdout_ring_tiebreak_detached_20261029.json",
]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_candidate_is_research_only_and_format_valid():
    """Saved-byte checks need no bridge rasters and never grant submission clearance."""
    from gems57.grid import EPSG, HEIGHT, WIDTH, TRANSFORM

    with rasterio.open(CAND) as src:
        assert src.count == 1 and src.dtypes[0] == "float32"
        assert src.crs.to_epsg() == EPSG
        assert (src.height, src.width) == (HEIGHT, WIDTH)
        assert tuple(src.transform)[:6] == tuple(TRANSFORM)[:6]
        nan_arr = src.read(1)
    finite = np.isfinite(nan_arr)
    assert finite.any() and (~finite).any()
    assert np.isnan(nan_arr[~finite]).all()
    assert nan_arr[finite].min() >= 0 and nan_arr[finite].max() <= 1

    with rasterio.open(ZEROS) as src:
        assert src.count == 1 and src.dtypes[0] == "float32"
        assert src.crs.to_epsg() == EPSG
        assert (src.height, src.width) == (HEIGHT, WIDTH)
        assert tuple(src.transform)[:6] == tuple(TRANSFORM)[:6]
        zarr = src.read(1)
    assert np.isfinite(zarr).all()
    assert (zarr >= 0).all() and (zarr <= 1).all()
    assert (zarr[~finite] == 0).all()
    assert np.array_equal(np.nan_to_num(nan_arr, nan=0.0), zarr)
    assert int((zarr > 0).sum()) == 37654


def test_candidate_stays_more_than_three_pixels_from_catalogue_when_bridge_is_available():
    """The data-dependent geometry check is explicit when an offline checkout lacks its rasters."""
    import pytest
    from scipy import ndimage as ndi
    from gems57.grid import REPO_ROOT, load_grid

    candidates = []
    configured = os.environ.get("GEMS_DATA_DIR")
    if configured:
        candidates.append(Path(configured))
    candidates.extend((
        REPO_ROOT / "data" / "bridge",
        REPO_ROOT / "data",
        REPO_ROOT / ".cache" / "gems_data",
    ))
    data_dir = next((p for p in candidates
                     if (p / "existing_faults.tif").is_file()
                     and (p / "sample_submission.tif").is_file()), None)
    if data_dir is None:
        pytest.skip("bridge existing_faults.tif and sample_submission.tif are absent; geometry check needs data")

    grid = load_grid(data_dir)
    with rasterio.open(ZEROS) as src:
        dots = src.read(1) > 0
    assert dots.shape == grid.footprint.shape
    distances = ndi.distance_transform_edt(~grid.catalogue)[dots]
    assert distances.size == 37654
    assert distances.min() > 3.0


def test_candidate_is_not_in_public_downloads():
    assert not list((ROOT / "docs/downloads").glob("karage1-probcollar-*"))


def test_run_card_is_negative_and_identical_copies():
    a = json.loads(CARD_A.read_text())
    assert CARD_A.read_bytes() == CARD_B.read_bytes()
    assert a["verdict"] == "negative"
    assert a["ok_to_submit"] is False
    assert a["slot_selected_or_spent"] is False
    assert a["submission_slots_used"] == 0
    assert a["lane"]["experiments_used"] <= a["lane"]["experiment_budget"] == 3
    assert len(a["submission_note"]) <= 140
    assert a["candidate"]["sha256"] == _sha(CAND)
    assert a["candidate"]["zeros_twin"]["sha256"] == _sha(ZEROS)
    assert a["candidate"]["download_offered"] is False
    assert a["holdout"]["label"] == "HOLDOUT-DTI"


def test_card_verdict_follows_the_gates():
    """A promote verdict is only legal if the candidate beats the best control in both modes."""
    a = json.loads(CARD_A.read_text())
    beats = a["holdout"]["candidate_vs_best_control"]
    all_beat = all(beats[m]["candidate_beats_best"] for m in ("all", "detached"))
    gated_ok = all_beat and a["leakage_canary"]["passes"] and not a["uniqueness"]["literal_duplicate_flag"]
    assert (a["verdict"] == "promote") == gated_ok


def test_receipts_are_copied_byte_identical():
    for name in RECEIPTS:
        assert (ROOT / "evidence" / name).read_bytes() == (ROOT / "docs/data" / name).read_bytes(), name


def test_focus_page_states_status_and_has_no_raster_download():
    text = PAGE.read_text()
    assert "NOT CLEARED" in text and "DO NOT SUBMIT" in text
    assert "Is it OK to download and submit any file? No." in text
    # no raster is linked, and no anchor carries a download attribute
    assert not re.search(r'href="[^"]*\.tif"', text, flags=re.I)
    assert not re.search(r"<a[^>]*\sdownload[\s>=]", text, flags=re.I)
    for name in ("GEMSDOE32", "GEMSDOE25", "GEMSDOE30"):
        assert name in text


def test_pages_link_the_new_summary_and_keep_guard_phrases():
    index = (ROOT / "docs/index.html").read_text()
    assert "DO NOT SUBMIT" in index and "No approved .tif to download" in index
    assert "docs/focus-sites.html" in (ROOT / "index.html").read_text()
    assert "focus-sites.html" in (ROOT / "docs/executive-summary.html").read_text()
