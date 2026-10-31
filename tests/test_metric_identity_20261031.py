"""Regression tests for the binary-dot DTI identity (session arena/d454d34a, 31 Oct 2026).

The published metric (DrivenData competition 306, page 967) is

    DTI = TP_w / (TP_w + alpha*FP_w + beta*FN_w),   FN_w = |G| - TP_w.

For a binary dot field with n dots, T = TP_w, M = sum over dots of their own
kernel self-credit, and G = |truth| this becomes

    DTI = T / ((1 - beta)*T + alpha*(n - M) + beta*G).

An earlier version of scripts/kp1_metric_analysis.py wrote the T term with
coefficient 1.  That gave a false perfect-knowledge ceiling of 0.556 instead of
1.0.  The shared template's marginal_accept writes alpha in place of (1 - beta) for the T
term.  Its two-sided decision is unaffected (the T terms cancel), so the template is
left unchanged: it is hash-pinned by evidence/template_integrity_20261028.json, and
changing it would need an owner-approved receipt.  That coupling is an open item in
the review.  The identity tests compare
against the literal brute-force oracle ``gems57.metric.dti_bruteforce`` at
parameters where alpha != 1 - beta, so the coupling cannot hide behind the
competition's alpha + beta = 1.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
for rel in ("vendor", "."):
    if str(ROOT / rel) not in sys.path:
        sys.path.insert(0, str(ROOT / rel))

from gems57 import metric as M  # noqa: E402


def _kernel(d: float, radius: float = 3.0) -> float:
    return max(1.0 - d / radius, 0.0)


def _components(dots: np.ndarray, truth: np.ndarray, radius: float = 3.0):
    """Independent, literal T, M, n, G for a binary dot grid (no shared code)."""
    gs = np.argwhere(truth)
    xs = np.argwhere(dots > 0)
    T = 0.0
    for g in gs:
        best = 0.0
        for x in xs:
            best = max(best, _kernel(float(np.hypot(*(x - g))), radius))
        T += best
    M_ = 0.0
    for x in xs:
        best = 0.0
        for g in gs:
            best = max(best, _kernel(float(np.hypot(*(x - g))), radius))
        M_ += best
    return T, M_, int(len(xs)), int(len(gs))


def _identity(T: float, M_: float, n: int, G: int, alpha: float, beta: float) -> float:
    return T / ((1.0 - beta) * T + alpha * (n - M_) + beta * G)


def _toy(seed: int):
    rng = np.random.default_rng(seed)
    H = W = 24
    truth = np.zeros((H, W), np.float64)
    r0, c0 = rng.integers(2, 8), rng.integers(2, W - 2)
    truth[r0:r0 + 14, c0] = 1.0
    dots = np.zeros((H, W), np.float64)
    for _ in range(int(rng.integers(8, 30))):
        dots[rng.integers(0, H), rng.integers(0, W)] = 1.0
    # some dots on and near the fault
    for r in range(r0, r0 + 14, 3):
        dots[r, c0 + int(rng.integers(-2, 3))] = 1.0
    return dots, truth


def test_identity_matches_bruteforce_oracle_at_competition_parameters():
    for seed in range(12):
        dots, truth = _toy(seed)
        T, M_, n, G = _components(dots, truth)
        oracle = M.dti_bruteforce(dots, truth)["dti"]
        assert abs(_identity(T, M_, n, G, 0.2, 0.8) - oracle) < 1e-9


def test_identity_matches_bruteforce_oracle_at_non_competition_parameters():
    # alpha + beta != 1 on purpose: this is where the old coefficient on T fails.
    for seed in range(12):
        dots, truth = _toy(100 + seed)
        T, M_, n, G = _components(dots, truth)
        for alpha, beta in ((0.3, 0.6), (0.5, 0.5), (0.1, 0.9)):
            oracle = M.dti_bruteforce(dots, truth, alpha=alpha, beta=beta)["dti"]
            assert abs(_identity(T, M_, n, G, alpha, beta) - oracle) < 1e-9


def test_perfect_prediction_scores_exactly_one():
    truth = np.zeros((20, 20), np.float64)
    truth[5:15, 10] = 1.0
    dots = truth.copy()
    assert abs(M.dti_bruteforce(dots, truth)["dti"] - 1.0) < 1e-12
    T, M_, n, G = _components(dots, truth)
    assert abs(_identity(T, M_, n, G, 0.2, 0.8) - 1.0) < 1e-12


def test_kp1_analysis_score_uses_the_corrected_identity():
    from scripts import kp1_metric_analysis as K

    assert abs(K.score(n=5000, T=0.0, M=0.0, G=60988)) < 1e-15
    assert abs(K.score(n=10.0, T=10.0, M=10.0, G=10.0) - 1.0) < 1e-12
    assert abs(K.score(n=37654, T=9000.0, M=4000.0, G=60988)
               - _identity(9000.0, 4000.0, 37654, 60988, 0.2, 0.8)) < 1e-12
    # the ceiling reported by the analysis must be 1.0 (was 0.556)
    assert K.score(n=60988, T=60988, M=60988, G=60988) == 1.0


def test_precision_bar_matches_exact_marginal_test():
    from scripts import kp1_metric_analysis as K

    # Adding a dot with credit dT and self-credit m raises DTI iff dT > bar.
    rng = np.random.default_rng(7)
    for _ in range(4000):
        T = rng.uniform(1.0, 400.0)
        n = int(rng.integers(50, 4000))
        Mx = float(rng.uniform(0.0, min(T, n)))
        G = int(rng.integers(int(T) + 1, 9000))
        for alpha, beta in ((0.2, 0.8), (0.3, 0.6)):
            D0 = (1 - beta) * T + alpha * (n - Mx) + beta * G
            s = T / D0
            m = float(rng.uniform(0.0, 1.0))
            dT = float(rng.uniform(0.0, 1.0))
            D1 = (1 - beta) * (T + dT) + alpha * ((n + 1) - (Mx + m)) + beta * G
            improves = (T + dT) / D1 > s
            bar = alpha * (1 - m) * s / (1 - (1 - beta) * s)
            if abs(dT - bar) > 1e-9:
                assert improves == (dT > bar)


def test_marginal_accept_matches_recomputation_at_general_parameters():
    rng = np.random.default_rng(11)
    for _ in range(3000):
        T = float(rng.uniform(1.0, 400.0))
        n = int(rng.integers(50, 4000))
        Mx = float(rng.uniform(0.0, min(T, n)))
        K = float(T + rng.uniform(0.0, 3000.0))
        dT = float(rng.uniform(0.0, 1.0))
        k_self = float(rng.uniform(dT, 1.0))
        for alpha, beta in ((0.2, 0.8), (0.3, 0.6)):
            D0 = (1 - beta) * T + alpha * (n - Mx) + beta * K + M.EPS
            D1 = (1 - beta) * (T + dT) + alpha * ((n + 1) - (Mx + k_self)) + beta * K + M.EPS
            expect = (T + dT) / D1 > T / D0
            assert M.marginal_accept(dT, k_self, T, Mx, n, K, alpha=alpha, beta=beta) == expect
