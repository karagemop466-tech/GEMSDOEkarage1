import numpy as np
from gemsk import metric


def test_matches_bruteforce_soft_and_binary():
    rng = np.random.default_rng(0)
    for trial in range(6):
        truth = np.zeros((24, 24), bool)
        truth[rng.integers(0, 24, 9), rng.integers(0, 24, 9)] = True
        pred = np.zeros((24, 24))
        yy, xx = rng.integers(0, 24, 14), rng.integers(0, 24, 14)
        pred[yy, xx] = rng.random(14) if trial % 2 else 1.0
        a = metric.dti_components(pred, truth)
        b = metric.dti_bruteforce(pred, truth)
        for k in ("tp", "fp", "fn", "dti"):
            assert abs(a[k] - b[k]) < 1e-9, (k, a[k], b[k])


def test_perfect_and_empty():
    truth = np.zeros((10, 10), bool); truth[5, 2:8] = True
    assert abs(metric.dti_components(truth.astype(float), truth)["dti"] - 1.0) < 1e-9
    assert metric.dti_components(np.zeros((10, 10)), truth)["dti"] == 0.0


def test_fn_identity_and_scaling_monotone():
    rng = np.random.default_rng(1)
    truth = rng.random((30, 30)) < 0.05
    pred = (rng.random((30, 30)) < 0.05).astype(float)
    r = metric.dti_components(pred, truth)
    assert abs(r["fn"] - (r["n_truth"] - r["tp"])) < 1e-9
    # scaling all predictions down never helps: binary emission is optimal for a fixed support
    assert metric.dti_components(0.5 * pred, truth)["dti"] <= r["dti"] + 1e-12


def test_active_domain_excludes_truth_and_predictions():
    truth = np.zeros((10, 10), bool); truth[2, 2] = True; truth[7, 7] = True
    pred = np.zeros((10, 10)); pred[2, 2] = 1; pred[7, 7] = 1
    active = np.ones((10, 10), bool); active[7, 7] = False
    r = metric.dti_components(pred, truth, active=active)
    assert r["n_truth"] == 1 and r["n_emitted"] == 1 and abs(r["dti"] - 1.0) < 1e-9
