"""Regression checks for the 31 Oct 2026 session arena/55dc7b72 artifacts.

These guard the verdict logic, not the geology: the candidate must stay labelled DO-NOT-SUBMIT,
the holdout must keep its negative verdict, and the nine-site table must not clear any file.
Tests skip cleanly when ignored bulk inputs (data/) are absent.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence"
CAND = ROOT / "docs" / "downloads" / "DO-NOT-SUBMIT_karage1-catexcl-halo-r3-t0.292-20261031T010556Z-zeros.tif"


def _load(name):
    p = EVID / name
    if not p.exists():
        pytest.skip(f"{name} not present")
    return json.loads(p.read_text())


def test_candidate_is_labelled_do_not_submit():
    # The name itself must make the status obvious to anyone who downloads it.
    assert CAND.name.startswith("DO-NOT-SUBMIT_")


def test_candidate_validation_format_pass_and_unique_vs_focus():
    v = _load("candidate_validation_catexcl_20261031.json")
    assert v["format_pass"] is True
    assert v["candidate_sha256"] and len(v["candidate_sha256"]) == 64
    focus = [r for r in v["rows"] if r["registry_file"].startswith("registry/")]
    assert len(focus) == 9
    # Unique versus the nine focus files under the literal 3-px / 0.90 Spearman gate.
    assert all(not r["literal_gate_duplicate"] for r in focus)
    # Literal lattice gate trips (expected for any dense dot set); recorded, not bypassed.
    lattice = [r for r in v["rows"] if "13gems" in r["registry_file"]]
    assert lattice and lattice[0]["literal_gate_duplicate"] is True


@pytest.mark.skipif(not CAND.exists(), reason="candidate raster absent")
def test_candidate_raster_format():
    rasterio = pytest.importorskip("rasterio")
    import numpy as np

    with rasterio.open(CAND) as ds:
        assert ds.count == 1 and ds.dtypes[0] == "float32"
        assert ds.crs.to_string() == "EPSG:32611"
        a = ds.read(1)
    assert np.isfinite(a).all()
    assert a.min() >= 0.0 and a.max() <= 1.0


def test_holdout_verdict_is_negative():
    e2 = _load("catexcl_e2_holdout_20261031.json")
    rc = e2["random_control"]
    # Candidate DTI must sit well below the density-matched random control (3 SD margin).
    assert e2["best_config"]["dti_pooled"] < rc["mean_dti"] - 3 * rc["sd_dti"]
    # Sparse-N control: model below random at every N >= 10,000.
    for row in e2["sparse_n_control"]:
        if row["n_dots_total"] >= 10000:
            assert row["model_minus_random"] < 0


def test_halo_radius_is_insensitive_in_holdout_proxy():
    # Documents the structural blindness of the proxy: removing the 0-6 px halo barely moves DTI
    # because halo dots next to WITHHELD segments are hits in the proxy, but would be false
    # positives under the organizer rule (catalogue masked). Do not read this as a halo refutation.
    e2 = _load("catexcl_e2_holdout_20261031.json")
    by_r = {r["halo_r_px"]: r["dti_pooled"] for r in e2["grid"] if r["threshold"] == e2["best_config"]["threshold"]}
    assert abs(by_r[0] - by_r[3]) < 0.001


def test_nine_site_table_clears_nothing():
    t = _load("nine_site_table_20261031.json")
    assert len(t["rows"]) == 9
    assert all(r["ok_to_download_and_submit"] is False for r in t["rows"])
    assert all("NOT ESTIMABLE" in r["leaderboard_estimate"] for r in t["rows"])
    pairs = {tuple(sorted((r["site"], x.split("_")[0]))) for r in t["rows"] for x in r["identical_dot_set_with_other_site"]}
    # GEMSDOE25 and GEMSDOE30 are dot-identical (Jaccard 1.0) though byte-different.
    assert ("GEMSDOE25", "GEMSDOE30") in pairs
