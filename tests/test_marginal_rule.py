"""Regression test for the marginal inclusion rule of the pooled Tversky/DTI score.

With ALPHA + BETA = 1, DTI = T / (alpha*(T+F) + beta*G). Adding one non-redundant
dot with truth credit k (and false-positive mass 1-k) raises DTI iff k > alpha*DTI.
This is an algebraic identity; it needs no data and it is checked here against
the shared metric implementation in vendor/gems57/metric.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
for rel in ("vendor",):
    if str(ROOT / rel) not in sys.path:
        sys.path.insert(0, str(ROOT / rel))

from gems57 import metric as M  # noqa: E402


def test_alpha_plus_beta_is_one_for_the_official_convention():
    assert abs(M.ALPHA + M.BETA - 1.0) < 1e-15
    assert M.ALPHA == 0.2 and M.BETA == 0.8


def test_adding_a_dot_raises_dti_iff_credit_exceeds_alpha_dti():
    rng = np.random.default_rng(20261029)
    mismatches = 0
    for _ in range(5000):
        T = rng.uniform(0.0, 500.0)
        F = rng.uniform(0.0, 5000.0)
        G = T + rng.uniform(0.0, 3000.0)
        dti0 = M.dti_from_components(T, F, G - T)
        k = rng.uniform(0.0, 1.0)
        dti1 = M.dti_from_components(T + k, F + (1.0 - k), G - T - k)
        mismatches += int((dti1 > dti0) != (k > M.ALPHA * dti0))
    assert mismatches == 0


def test_worked_example_at_the_reported_b2_level():
    # At DTI = 0.2778 (USER-REPORTED, not organizer-confirmed) the bar is 0.2 * 0.2778.
    assert abs(M.marginal_inclusion_threshold(0.2778) - 0.05556) < 1e-5
