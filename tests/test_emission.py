import numpy as np
from gemsk import emission


def test_poisson_spacing_and_budget():
    rng = np.random.default_rng(0)
    s = rng.random((120, 120)).astype(np.float32)
    dots = emission.poisson_select(s, budget=300, spacing=2.8)
    assert dots.sum() == 300
    yy, xx = np.nonzero(dots)
    pts = np.stack([yy, xx], 1).astype(float)
    d = np.sqrt(((pts[:, None] - pts[None]) ** 2).sum(-1)) + np.eye(len(pts)) * 1e9
    assert d.min() >= 2.8


def test_apron_prune_removes_near_catalogue():
    dots = np.zeros((20, 20), bool); dots[5, 5] = dots[5, 9] = dots[15, 15] = True
    cat = np.zeros((20, 20), bool); cat[5, 6] = True
    out = emission.apron_prune(dots, cat, 2)
    assert not out[5, 5] and out[5, 9] and out[15, 15]  # d<=2 pruned (champion rule), d=3 kept


def test_emit_respects_budget_and_apron():
    rng = np.random.default_rng(1)
    s = rng.random((150, 150)).astype(np.float32)
    cat = np.zeros((150, 150), bool); cat[70, :] = True
    dots = emission.emit(s, 400, cat, spacing=2.8, apron_px=2)
    assert dots.sum() == 400
    yy, _ = np.nonzero(dots)
    assert np.all(np.abs(yy - 70) > 2)
