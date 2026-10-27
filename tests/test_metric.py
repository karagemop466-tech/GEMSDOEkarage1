"""
Unit tests for src/gems/metric.py.

These tests require NO competition data -- they validate the metric
implementation against the official formula using small synthetic rasters
and the algebraic identity from the official worked example. This is the
"leakage canary" / correctness-before-trust discipline required by the
parallel-run protocol: we verify the tool before we trust any number it
produces.
"""

import numpy as np
import pytest

from gems.metric import (
    distance_weighted_tversky_index,
    dti_from_precomputed_M,
    windowed_max_prediction,
    EPS,
)


def test_official_worked_example_algebra():
    """
    Official page: "TPw = 3.00, FPw = 1.89, FNw = 2.00" with alpha=0.2,
    beta=0.8 gives DTI = 0.60 (displayed rounded to 2 dp).
    https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
    """
    tp_w, fp_w, fn_w = 3.00, 1.89, 2.00
    alpha, beta = 0.2, 0.8
    dti = tp_w / (tp_w + alpha * fp_w + beta * fn_w)
    assert round(dti, 2) == 0.60


def test_perfect_prediction_scores_near_one():
    gt = np.zeros((40, 40), dtype=bool)
    gt[20, :] = True  # a straight fault line
    pred = gt.astype(np.float32)  # perfect prediction
    result = distance_weighted_tversky_index(pred, gt)
    assert result.fp_w == pytest.approx(0.0, abs=1e-9)
    assert result.fn_w == pytest.approx(0.0, abs=1e-9)
    assert result.dti > 0.999


def test_all_zero_prediction_scores_zero():
    gt = np.zeros((40, 40), dtype=bool)
    gt[20, :] = True
    pred = np.zeros((40, 40), dtype=np.float32)
    result = distance_weighted_tversky_index(pred, gt)
    assert result.tp_w == pytest.approx(0.0, abs=1e-9)
    assert result.fn_w == pytest.approx(result.n_ground_truth_positive, abs=1e-6)
    assert result.dti == pytest.approx(0.0, abs=1e-6)


def test_no_ground_truth_and_no_prediction_is_degenerate_zero():
    gt = np.zeros((10, 10), dtype=bool)
    pred = np.zeros((10, 10), dtype=np.float32)
    result = distance_weighted_tversky_index(pred, gt)
    # 0 / (0 + 0 + 0 + eps) == 0, not NaN -- must never raise or divide by zero.
    assert result.dti == pytest.approx(0.0, abs=1e-6)


def test_false_positive_far_from_truth_is_penalized_fully():
    gt = np.zeros((40, 40), dtype=bool)
    gt[5, 5] = True
    pred = np.zeros((40, 40), dtype=np.float32)
    pred[35, 35] = 1.0  # far outside the 3px/300m kernel support
    result = distance_weighted_tversky_index(pred, gt)
    assert result.fp_w == pytest.approx(1.0, abs=1e-6)
    assert result.tp_w == pytest.approx(0.0, abs=1e-9)


def test_false_positive_near_truth_is_penalized_less():
    gt = np.zeros((40, 40), dtype=bool)
    gt[20, 20] = True
    pred_far = np.zeros((40, 40), dtype=np.float32)
    pred_far[20, 35] = 1.0
    pred_near = np.zeros((40, 40), dtype=np.float32)
    pred_near[20, 21] = 1.0  # 1 px / 100 m away -> partial credit both ways
    far = distance_weighted_tversky_index(pred_far, gt)
    near = distance_weighted_tversky_index(pred_near, gt)
    assert near.dti > far.dti


def test_nan_inside_valid_mask_raises():
    gt = np.zeros((10, 10), dtype=bool)
    pred = np.zeros((10, 10), dtype=np.float32)
    pred[3, 3] = np.nan
    valid = np.ones((10, 10), dtype=bool)
    with pytest.raises(ValueError):
        distance_weighted_tversky_index(pred, gt, valid_mask=valid)


def test_out_of_range_prediction_raises():
    gt = np.zeros((10, 10), dtype=bool)
    pred = np.zeros((10, 10), dtype=np.float32)
    pred[3, 3] = 1.5
    with pytest.raises(ValueError):
        distance_weighted_tversky_index(pred, gt)


def test_eps_is_tiny_and_only_affects_degenerate_cases():
    assert EPS < 1e-6


def test_precomputed_M_matches_direct():
    """
    scripts/run_holdout_experiment.py's bootstrap reuses a precomputed M
    across many ground-truth resamples for speed (avoiding a ~29-offset
    windowed-max recompute per resample). This test pins that fast path to
    agree exactly with the slower, independently-written direct formula
    across several random ground-truth masks against one fixed prediction.
    """
    rng = np.random.default_rng(0)
    p = rng.random((60, 60)).astype(np.float64)
    valid = np.ones((60, 60), dtype=bool)
    M = windowed_max_prediction(p)
    for _ in range(5):
        gt = rng.random((60, 60)) < 0.02
        direct = distance_weighted_tversky_index(p, gt, valid_mask=valid)
        fast = dti_from_precomputed_M(M, p, gt, valid)
        assert fast.dti == pytest.approx(direct.dti, rel=1e-9, abs=1e-12)
        assert fast.tp_w == pytest.approx(direct.tp_w, rel=1e-9, abs=1e-9)
        assert fast.fp_w == pytest.approx(direct.fp_w, rel=1e-9, abs=1e-9)
        assert fast.fn_w == pytest.approx(direct.fn_w, rel=1e-9, abs=1e-9)
