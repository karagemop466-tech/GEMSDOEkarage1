import numpy as np
import pytest
from gemsk import holdout, prior


def _toy():
    foot = np.ones((120, 120), bool)
    cat = np.zeros((120, 120), bool)
    for r in range(10, 110, 12):          # 9 horizontal segments
        cat[r, 10:100] = True
    cat[50:100, 110] = True               # one vertical segment
    return cat, foot


@pytest.mark.parametrize("scheme", ["blocked", "interleaved"])
def test_folds_partition_whole_segments(scheme):
    cat, foot = _toy()
    folds = holdout.make_folds(cat, foot, k=4, block_px=40, buffer_px=2, scheme=scheme)
    assert sum(f["n_withheld"] for f in folds) == int(cat.sum())
    for f in folds:
        # withheld and visible are disjoint and cover the catalogue
        assert not (f["withheld"] & f["visible"]).any()
        assert ((f["withheld"] | f["visible"]) == cat).all()
        # visible faults (and their 2-px buffer) are outside the scored domain
        assert not (f["active"] & f["visible"]).any()
        # a segment is never split: every row-segment is entirely in or out
        for r in range(10, 110, 12):
            row = f["withheld"][r, 10:100]
            assert row.all() or not row.any()


def test_evaluate_dots_terms_sum_to_components():
    cat, foot = _toy()
    f = holdout.make_folds(cat, foot, k=2, block_px=60, buffer_px=1, scheme="interleaved")[0]
    rng = np.random.default_rng(0)
    dots = rng.random(cat.shape) < 0.02
    res, terms = holdout.evaluate_dots(dots, f, block_px=30)
    tot = terms.sum(axis=0)
    assert abs(tot[0] - res["tp"]) < 1e-6 and abs(tot[1] - res["fp"]) < 1e-6 and abs(tot[2] - res["fn"]) < 1e-6
    assert int(tot[3]) == res["n_truth"]


def test_prior_density_monotone_and_normalised():
    cat, foot = _toy()
    folds = holdout.make_folds(cat, foot, k=2, block_px=60, buffer_px=1, scheme="interleaved")
    dens = prior.density_from_tables([prior.fold_table(f) for f in folds])
    assert dens.max() == 1.0 and dens.min() >= 0.02 - 1e-12
    peak = int(np.argmax(dens))
    assert np.all(np.diff(dens[peak:]) <= 1e-12)
    g = prior.apply(dens, folds[0]["visible"])
    assert g.shape == cat.shape and g.max() <= 1.0 and g.min() > 0
