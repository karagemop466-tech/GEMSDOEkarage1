"""Unit checks for the K1-HGRID-STRAIN lane helpers (no competition data required)."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts")]
import hgridge_strain_lane as L  # noqa: E402


def test_pct_rank_is_a_permutation_in_unit_interval():
    v = np.array([[3.0, 1.0], [2.0, 4.0]])
    m = np.ones_like(v, bool)
    r = L.pct_rank(v, m)
    assert np.allclose(sorted(r.ravel()), [0.25, 0.5, 0.75, 1.0])


def test_top_k_respects_mask_and_count():
    score = np.arange(100.0).reshape(10, 10)
    crest = np.ones((10, 10), bool)
    allowed = np.zeros((10, 10), bool)
    allowed[:5] = True
    out = L.top_k(score, crest, 7, allowed)
    assert out.sum() == 7
    assert not out[5:].any()
    assert out.ravel()[np.argmax(np.where(allowed, score, -1))]


def test_top_k_caps_at_pool_size():
    score = np.ones((4, 4))
    crest = np.zeros((4, 4), bool)
    crest[0, :2] = True
    out = L.top_k(score, crest, 50, np.ones((4, 4), bool))
    assert out.sum() == 2


def test_random_control_count_and_seed_determinism():
    fp = np.ones((20, 20), bool)
    a = L.random_control(fp, 30, 7)
    b = L.random_control(fp, 30, 7)
    assert a.sum() == 30 and np.array_equal(a, b)


def test_bootstrap_ci_is_ordered_and_bounded():
    cells = [dict(tp=10.0 + i, fp=50.0, fn=30.0 - i) for i in range(8)]
    lo, hi = L.bootstrap_ci(cells)
    assert 0.0 <= lo <= hi <= 1.0


def test_run_card_is_fail_closed_on_disk():
    cards = sorted((ROOT / "evidence").glob("hgridge_run_card_*.json"))
    if not cards:
        pytest.skip("no K1-HGRID-STRAIN run card in this checkout")
    card = json.loads(cards[-1].read_text())
    assert card["ok_to_submit"] is False
    assert card["slot_selected_or_spent"] is False
    assert card["verdict"] == "negative"
