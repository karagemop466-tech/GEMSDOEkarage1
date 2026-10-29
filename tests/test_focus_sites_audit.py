"""Invariants of evidence/focus_sites_audit_20261029.json (no raster data required).

These guard the numbers quoted in the session review: the lattice-coverage bound,
the literal 70 % / 3-px verdict for each focus file, identical-mask groups, and
the descriptive user-reported trend. Re-run scripts/audit_focus_sites.py to regenerate.
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
AUDIT = json.loads((ROOT / "evidence" / "focus_sites_audit_20261029.json").read_text())
FOCUS = [r["name"] for r in AUDIT["rasters"] if not r["name"].startswith("lattice")]


def test_nine_focus_files_pinned_and_measured():
    assert len(FOCUS) == 9
    refs = {r["id"]: r for r in json.loads((ROOT / "registry" / "reference_assets.json").read_text())}
    for name in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert name in refs and len(refs[name]["sha256"]) == 64


def test_lattice_bound_arithmetic():
    b = AUDIT["lattice_coverage_bound"]
    assert b["footprint_uncovered_by_lattice_3px"] == 6649
    assert b["max_dots_that_can_pass_70pct_rule"] == math.floor(6649 / 0.30) == 22163
    assert math.isclose(b["footprint_covered_fraction"], 1 - 6649 / b["footprint_px"], rel_tol=1e-12)


def test_every_focus_file_fails_literal_lattice_rule():
    rows = {p["A"]: p["fwd3_A_within_3px_of_B"] for p in AUDIT["forward_3px_overlap"] if p["B"].startswith("lattice")}
    assert set(rows) == set(FOCUS)
    for name, fwd in rows.items():
        assert fwd > 0.70, name
    # every focus file has more dots than the pass ceiling
    for r in AUDIT["rasters"]:
        if r["name"] in FOCUS:
            assert r["positive_inside_footprint"] > AUDIT["lattice_coverage_bound"]["max_dots_that_can_pass_70pct_rule"]


def test_identical_mask_groups_are_exact_and_scores_agree():
    groups = [sorted(g) for g in AUDIT["identical_mask_groups"]]
    assert sorted(groups) == sorted([sorted(["GEMSDOE25_d2-8", "GEMSDOE30_d28-offcat"]),
                                     sorted(["GEMSDOE28_h27-4-r1", "GEMSDOE31_h27-4-solo"])])
    dots = {r["name"]: r["positive_inside_footprint"] for r in AUDIT["rasters"]}
    for g in groups:
        assert len({dots[n] for n in g}) == 1


def test_user_reported_trend_is_self_consistent_and_labelled():
    t = AUDIT["user_reported_score_vs_dot_count"]
    assert t["label"].startswith("USER-REPORTED / UNVERIFIED")
    xs = np.array([p["dots"] for p in t["points"]], float)
    ys = np.array([p["user_reported"] for p in t["points"]], float)
    assert math.isclose(stats.pearsonr(xs, ys).statistic, t["pearson_r"], abs_tol=1e-4)
    assert t["spearman_rho"] == -1.0


def test_no_clearance_language_in_new_evidence():
    text = (ROOT / "evidence" / "focus_sites_audit_20261029.json").read_text().upper()
    assert "OK TO DOWNLOAD" not in text and "CLEARED FOR SUBMISSION" not in text
