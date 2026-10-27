"""Distance-weighted Tversky index (DTI) as published for DOE GEMS (DrivenData #306, page 967).

Published definition (alpha = 0.2 on false positives, beta = 0.8 on false negatives, triangular
kernel with 300 m support = 3 px at 100 m):

    k(d)  = max(1 - d / 300 m, 0)
    TP_w  = sum_{g in truth}  max_{x} p(x) k(d(x, g))
    FP_w  = sum_{x} p(x) [1 - max_{g} k(d(x, g))]
    FN_w  = sum_{g in truth} [1 - max_{x} p(x) k(d(x, g))]  = |G| - TP_w
    DTI   = TP_w / (TP_w + 0.2 FP_w + 0.8 FN_w)

Official references (the page is login-walled from this sandbox; the formula was transcribed by the
sibling repositories and is re-verified here against a literal O(|G||P|) brute force in tests):
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

ALPHA = 0.2
BETA = 0.8
RADIUS_PX = 3.0
EPS = 1e-12


def kernel(d, radius: float = RADIUS_PX):
    return np.maximum(1.0 - np.asarray(d, dtype=np.float64) / radius, 0.0)


def _offsets(radius: float = RADIUS_PX):
    r = int(np.ceil(radius))
    out = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            k = float(kernel(np.hypot(dy, dx), radius))
            if k > 0.0:
                out.append((dy, dx, k))
    return out


_OFFS = _offsets()


def dti_components(pred, truth, active=None):
    """Exact TP_w / FP_w / FN_w for soft or binary predictions p in [0, 1].

    ``active`` restricts both predictions and truth to the scored domain (pixels outside are
    neither credited nor charged). Returns a dict with tp, fp, fn, n_truth, dti, coverage.
    """
    p = np.asarray(pred, dtype=np.float64)
    g = np.asarray(truth, dtype=bool)
    if p.shape != g.shape or p.ndim != 2:
        raise ValueError("pred/truth must be equal 2-D grids")
    if active is not None:
        active = np.asarray(active, bool)
        p = np.where(active, p, 0.0)
        g = g & active
    vals = p[p != 0]
    if not np.isfinite(vals).all() or (vals < 0).any() or (vals > 1).any():
        raise ValueError("predictions must be finite and in [0, 1]")
    H, W = p.shape
    yy, xx = np.nonzero(g)
    n = int(yy.size)
    if n == 0:
        return dict(tp=0.0, fp=float(p.sum()), fn=0.0, n_truth=0, dti=0.0, coverage=0.0)
    credit = np.zeros(n, dtype=np.float64)
    for dy, dx, k in _OFFS:
        ny, nx = yy + dy, xx + dx
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        credit[ok] = np.maximum(credit[ok], p[ny[ok], nx[ok]] * k)
    tp = float(credit.sum())
    fn = float(n) - tp
    d = distance_transform_edt(~g)
    fp = float((p * (1.0 - kernel(d))).sum())
    dti = tp / (tp + ALPHA * fp + BETA * fn + EPS)
    return dict(tp=tp, fp=fp, fn=fn, n_truth=n, dti=float(dti), coverage=tp / n, n_emitted=int((p > 0).sum()))


def dti_from_components(tp: float, fp: float, fn: float) -> float:
    return float(tp / (tp + ALPHA * fp + BETA * fn + EPS))


def dti_bruteforce(pred, truth, radius: float = RADIUS_PX):
    """Literal O(|G| |P|) transcription of the published equations (unit tests only)."""
    pred = np.asarray(pred, float)
    truth = np.asarray(truth, bool)
    gs = np.argwhere(truth)
    xs = np.argwhere(pred > 0)
    tp = 0.0
    for g in gs:
        best = 0.0
        for x in xs:
            d = float(np.hypot(*(x - g)))
            best = max(best, pred[tuple(x)] * max(1.0 - d / radius, 0.0))
        tp += best
    fn = len(gs) - tp
    fp = 0.0
    for x in xs:
        kmax = 0.0
        for g in gs:
            kmax = max(kmax, max(1.0 - float(np.hypot(*(x - g))) / radius, 0.0))
        fp += pred[tuple(x)] * (1.0 - kmax)
    return dict(tp=tp, fp=fp, fn=fn, dti=tp / (tp + ALPHA * fp + BETA * fn + EPS))


def breakeven_kernel_credit(current_dti: float) -> float:
    """Isolated-pixel break-even: a binary pixel whose full kernel credit k goes to an uncovered
    truth pixel raises DTI iff k > alpha * DTI (because 1 - beta = alpha). Special case only."""
    return ALPHA * current_dti
