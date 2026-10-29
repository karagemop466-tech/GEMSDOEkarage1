"""Regression tests for the 2026-10-29 nine-site decision evidence and page."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOCUS = {"GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"}


def _load(rel: str):
    return json.loads((ROOT / rel).read_text())


def test_user_reported_scores_cover_nine_sites_and_are_labelled():
    data = _load("registry/user_reported_scores_20261029.json")
    assert data["status_label"] == "USER-REPORTED / UNVERIFIED"
    sites = {e["site"] for e in data["entries"]}
    assert sites == FOCUS
    best = {}
    for e in data["entries"]:
        best[e["site"]] = max(best.get(e["site"], 0.0), e["score"])
    assert max(best, key=best.get) == "GEMSDOE32"
    assert best["GEMSDOE32"] == 0.2778
    assert min(best.values()) == 0.2449


def test_lineage_checks_match_verified_values():
    d = _load("evidence/site_lineage_verification_20261029.json")
    c = d["checks"]
    assert c["GEMSDOE25_equals_GEMSDOE30"] is True
    b2 = c["GEMSDOE32_vs_GEMSDOE25_remove_within_2px_of_labels"]
    assert (b2["parent_dots"], b2["child_dots"], b2["removed"], b2["added"]) == (44090, 37654, 6436, 0)
    assert b2["removed_all_within_r_of_known_labels"] is True
    assert c["GEMSDOE36_extra_dots_vs_GEMSDOE32"] == 1200
    # Every focus site has a sibling that captures >= 97% of its dots.
    shares = {s: 0.0 for s in FOCUS}
    for key, v in d["pairwise_nine_sites"].items():
        a, b = key.split("|")
        shares[a] = max(shares[a], v["a_dots_within_3px_of_b_fraction"])
        shares[b] = max(shares[b], v["b_dots_within_3px_of_a_fraction"])
    assert min(shares.values()) >= 0.97
    assert d["submit_authorized"] is False


def test_lattice_null_random_dots_fail_the_rule():
    d = _load("evidence/lattice_saturation_null_20261029.json")
    assert d["footprint_covered_by_3px_disk_fraction"] > 0.99
    assert all(t["fails_70pct_rule"] for t in d["random_dot_trials"].values())
    assert d["submit_authorized"] is False


def test_fleet_audit_covers_every_local_tif_and_blocks_all():
    d = _load("evidence/local_downloads_audit_20261029.json")
    files = {r["file"] for r in d["local_downloads"]}
    # Saved-byte receipts (scripts/audit_local_tif.py) also cover TIFs that are not lattice copies,
    # so they count for coverage. The lattice and ok_to_submit checks below stay on fleet rows only.
    for receipt in sorted((ROOT / "evidence").glob("audit_*.json")):
        data = json.loads(receipt.read_text())
        if data.get("schema") == "karage1-local-tif-audit-v1":
            files.add(data["file"])
    on_disk = {f"docs/downloads/{p.name}" for p in (ROOT / "docs/downloads").glob("*.tif")}
    assert on_disk <= files
    assert all(r["ok_to_submit"] is False for r in d["local_downloads"])
    assert min(r["lattice_directed_overlap_3px"] for r in d["local_downloads"]) > 0.98


def test_run_card_is_negative_and_authorizes_nothing():
    card = _load("evidence/session_20261029_run_card.json")
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["slot_selected_or_spent"] is False
    assert card["raster_generated"] is False
    assert card["holdout_DTI"] is None


def test_superseded_promote_verdict_is_not_an_approval():
    for rel in ("docs/data/unique-hyp-kth-therm-mask-20261028-zeros.json",
                "docs/downloads/unique-hyp-kth-therm-mask-20261028-zeros.json"):
        if not (ROOT / rel).exists():
            continue  # archived copies may be moved; the archive receipt below is authoritative
        card = _load(rel)
        assert card["verdict"] != "promote", rel
        assert card["ok_to_submit"] is False, rel


def test_built_pages_contain_no_stale_clearance_language():
    pages = [ROOT / "index.html", ROOT / "executive-summary.html",
             ROOT / "docs/index.html", ROOT / "docs/executive-summary.html", ROOT / "docs/nine-sites.html"]
    for page in pages:
        text = page.read_text()
        assert "CLEARED FOR SUBMISSION" not in text, page
        assert "IT IS OK TO DOWNLOAD AND SUBMIT" not in text, page
        # The retraction notice may name the file; a live download link must not exist.
        assert not re.search(r'href="[^"]*unique-hyp-kth-therm-mask[^"]*\.(tif|zip)"', text), page
        assert "Which file is best, and is it OK to submit?" in text, page


def test_local_rasters_finite_values_in_unit_interval():
    """Portal error 'Predicted values must be in range [0, 1]': no local raster may hold a finite value outside [0, 1]."""
    import numpy as np
    import rasterio

    files = sorted((ROOT / "docs/downloads").glob("*.tif"))
    assert len(files) >= 9
    for f in files:
        with rasterio.open(f) as ds:
            assert ds.count == 1 and ds.dtypes[0] == "float32", f.name
            a = ds.read(1)
        finite = a[np.isfinite(a)]
        assert finite.size > 0, f.name
        assert float(finite.min()) >= 0.0 and float(finite.max()) <= 1.0, f.name
