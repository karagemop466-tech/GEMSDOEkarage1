"""Synthetic checks on the pinned shared metric; no geological experiments."""
import numpy as np

from gems57 import metric


def test_one_dot_can_credit_more_than_one_truth_pixel():
    truth = np.zeros((9, 9), bool)
    truth[4, 3:6] = True
    pred = np.zeros((9, 9), float)
    pred[4, 4] = 1
    result = metric.dti_exact(pred, truth)
    # The dot covers one center and two neighbors; a sum is not a maximum.
    assert np.isclose(result['tp'], 7 / 3)
    assert result['tp'] > metric.kernel(0)


def test_deletion_tradeoff_matches_metric_for_small_binary_examples():
    # For deleted mass c and lost truth credit L, deletion improves DTI iff
    # alpha*T*c > L*(alpha*F + beta*G + eps), with positive denominators.
    rng = np.random.default_rng(219)
    checked = 0
    for _ in range(100):
        truth = rng.random((9, 9)) < .15
        before = rng.random((9, 9)) < .20
        if not truth.any() or not before.any():
            continue
        after = before & (rng.random((9, 9)) >= .3)
        a = metric.dti_exact(before.astype(float), truth)
        b = metric.dti_exact(after.astype(float), truth)
        loss = a['tp'] - b['tp']
        saved_fp = a['fp'] - b['fp']
        assert loss >= -1e-12 and saved_fp >= -1e-12
        lhs = metric.ALPHA * a['tp'] * saved_fp
        rhs = loss * (metric.ALPHA * a['fp'] + metric.BETA * a['n_truth'] + metric.EPS)
        # Skip numerically indistinguishable cases near the equality boundary.
        if abs(lhs - rhs) < 1e-10:
            continue
        assert (b['dti'] > a['dti']) == (lhs > rhs)
        checked += 1
    assert checked >= 20
