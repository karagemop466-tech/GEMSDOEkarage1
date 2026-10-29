"""Regression tests for the 2026-10-29 StrainPhase / SignedOffset holdout runs.

These tests read committed evidence and check pure helper functions. They need no
restored competition data, so they run in CI.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
for sub in (".", "src", "vendor"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

EVID = ROOT / "evidence"
RECORDED_GPC_DTI = 0.07339389911540638  # evidence/exp2_dipdual_holdout.json, arm GPC


def _load(name: str) -> dict:
    return json.loads((EVID / name).read_text())


@pytest.mark.parametrize("lane", ["strainphase", "signedoffset"])
def test_canary_has_no_leakage_alarm(lane):
    d = _load(f"exp1_{lane}_canary.json")
    assert d["any_alarm"] is False and d["pass"] is True
    assert all(r["max_direction_invariant_auc"] <= 0.90 for r in d["canary_rows"])
    assert all(r["declared_label_free_by_code_review"] is True for r in d["canary_rows"]
               if r["feature"] != "GPC_control")


@pytest.mark.parametrize("lane", ["strainphase", "signedoffset"])
def test_holdout_is_negative_and_matches_protocol(lane):
    d = _load(f"exp2_{lane}_holdout.json")
    assert d["evaluator_version"] == "gemsk-hide-recover-v1"
    assert d["withheld_positives"] == 60988
    assert d["budget_per_fold"] == 37654
    assert d["beats_gpc_control"] is False
    gpc = d["arms"]["GPC_control"]["dti"]
    cand = d["arms"][lane]["dti"]
    assert cand < gpc, "candidate must not beat the holdout best"
    assert d["control_reproduction_vs_exp2_dipdual"]["abs_difference"] <= 1e-9
    assert abs(gpc - RECORDED_GPC_DTI) <= 1e-9


def test_overlap_check_is_below_both_gates():
    d = _load("surface_registry_overlap_20261029.json")
    rows = d["rows"]
    assert d["registry_files_checked"] == len({r["registry_file"] for r in rows}) == 15
    assert len(rows) == 2 * 15
    assert max(abs(r["spearman_rho"]) for r in rows) <= 0.90
    assert max(r["share_registry_dots_within_3px_of_top_budget"] for r in rows) <= 0.70
    for r in d["registry_file_sha256"].values():
        assert len(r) == 64


def test_fill_nearest_and_rank01_helpers():
    from scripts.run_strainphase_experiment import _fill_nearest, _rank01

    foot = np.zeros((6, 6), bool)
    foot[1:5, 1:5] = True
    a = np.arange(36, dtype=np.float32).reshape(6, 6)
    a[2, 2] = np.nan  # invalid inside footprint
    a[0, 0] = np.nan  # invalid outside footprint
    filled = _fill_nearest(a, foot)
    assert np.isfinite(filled).all()
    assert filled[~foot].sum() == 0.0          # zero outside footprint
    assert np.isfinite(filled[2, 2])           # filled inside footprint
    r = _rank01(filled, foot)
    assert r[foot].min() == 0.0 and r[foot].max() == 1.0
    assert r[~foot].sum() == 0.0


def test_site_renderer_panel_is_fail_closed_and_negative():
    import importlib.util

    spec = importlib.util.spec_from_file_location("render_site", ROOT / "scripts" / "render_site.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    lanes, overlap = mod.session_evidence()
    assert [name for name, _ in lanes] == ["strainphase", "signedoffset"]
    html = mod.session_panel("")
    assert "NOTHING CLEARED" in html
    assert "No cleared TIF to download" in html
    lowered = html.lower()
    assert "ok to download" not in lowered
    assert "cleared for submission" not in lowered
