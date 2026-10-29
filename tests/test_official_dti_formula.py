"""Verify the shared DTI implementation against the published equations.

Sources (fetched 2026-10-29):
* DrivenData competition 306, problem description, "Performance metric" section:
  https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
  (TI = TP_w / (TP_w + alpha*FP_w + beta*FN_w); k(d) = max(1 - d/R, 0); R = 300 m;
  alpha = 0.2, beta = 0.8; worked example TP_w = 3.00, FP_w = 1.89, FN_w = 2.00 -> 0.60.)
* DrivenData community, organiser answer of 2026-09-16 (topic 11516): pixels on known
  USGS/INGENIOUS faults are masked from evaluation.
"""
import numpy as np

from gems57.metric import ALPHA, BETA, RADIUS_PX, dti_bruteforce, dti_exact, kernel


def test_official_worked_example_arithmetic():
    # Published example: TP_w=3.00, FP_w=1.89, FN_w=2.00 -> TI_w = 0.60 (2 dp).
    ti = 3.00 / (3.00 + ALPHA * 1.89 + BETA * 2.00)
    assert round(ti, 2) == 0.60
    assert (ALPHA, BETA, RADIUS_PX) == (0.2, 0.8, 3.0)


def test_kernel_is_triangular_300m():
    d = np.array([0.0, 1.0, 1.5, 3.0, 4.0])
    np.testing.assert_allclose(kernel(d), [1.0, 2 / 3, 0.5, 0.0, 0.0])


def test_exact_matches_literal_bruteforce_on_soft_predictions():
    rng = np.random.default_rng(7)
    for _ in range(6):
        truth = rng.random((18, 21)) < 0.06
        pred = np.where(rng.random((18, 21)) < 0.25, rng.random((18, 21)), 0.0)
        if not truth.any():
            truth[9, 10] = True
        a = dti_exact(pred, truth)
        b = dti_bruteforce(pred, truth)
        for key in ("tp", "fp", "fn", "dti"):
            assert abs(a[key] - b[key]) < 1e-9, (key, a[key], b[key])


def test_perfect_and_empty_predictions():
    truth = np.zeros((12, 12), bool)
    truth[3:9, 5] = True
    perfect = truth.astype(float)
    assert dti_exact(perfect, truth)["dti"] == 1.0 or abs(dti_exact(perfect, truth)["dti"] - 1.0) < 1e-9
    assert dti_exact(np.zeros((12, 12)), truth)["dti"] == 0.0


def test_known_pixels_are_excluded_from_both_terms():
    truth = np.zeros((10, 10), bool)
    truth[4, 2:8] = True
    pred = np.zeros((10, 10))
    pred[0, 0] = 1.0                       # far-away false positive
    known = np.zeros((10, 10), bool)
    known[0, 0] = True                     # masked: must not count as FP
    r = dti_exact(pred, truth, known=known)
    assert r["fp"] == 0.0
