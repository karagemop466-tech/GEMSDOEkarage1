"""Validation of the H-E1 Euler deconvolution library (src/gemskarage1/euler.py).

These tests are the evidence that the solver is correct BEFORE it is run on
real data: exact window sums, the vertical-derivative sign convention, and
recovery of known source positions and depths from analytic fields.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemskarage1 import euler as E  # noqa: E402

DX = 100.0


def test_window_sums_match_brute_force():
    rng = np.random.default_rng(3)
    f = rng.normal(size=(23, 19))
    half = 2
    S = E.window_sums({"f": f}, half, DX, names=["f"])["f"]
    offs = np.arange(-half, half + 1) * DX
    for (i, j) in [(10, 9), (3, 3), (20, 15), (half, half)]:
        s = sx = sy = 0.0
        for a in range(-half, half + 1):
            for b in range(-half, half + 1):
                yy, xx = i + a, j + b
                if 0 <= yy < f.shape[0] and 0 <= xx < f.shape[1]:
                    s += f[yy, xx]
                    sx += offs[b + half] * f[yy, xx]
                    sy += offs[a + half] * f[yy, xx]
        assert np.isclose(S[0][i, j], s, rtol=1e-10, atol=1e-10)
        assert np.isclose(S[1][i, j], sx, rtol=1e-10, atol=1e-10)
        assert np.isclose(S[2][i, j], sy, rtol=1e-10, atol=1e-10)


def _point_source_field(shape, src_rc, z0):
    """1/r point source at depth z0 (m), observed at the surface z = 0."""
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]].astype(float) * DX
    x0, y0 = src_rc[1] * DX, src_rc[0] * DX
    r = np.sqrt((xx - x0) ** 2 + (yy - y0) ** 2 + z0 ** 2)
    T = 1.0 / r
    r3 = r ** 3
    tx = -(xx - x0) / r3
    ty = -(yy - y0) / r3
    tz = z0 / r3          # d/dz_down of 1/r at z = 0 is +z0/r^3 (depth positive down)
    return T, tx, ty, tz, (x0, y0)


def test_fft_vertical_derivative_sign_and_accuracy():
    shape = (160, 160)
    T, tx_a, ty_a, tz_a, _ = _point_source_field(shape, (80, 80), 500.0)
    tx, ty, tz = E.fft_derivatives(T, DX, pad=64)
    inner = (slice(40, 120), slice(40, 120))
    assert np.corrcoef(tz[inner].ravel(), tz_a[inner].ravel())[0, 1] > 0.98
    assert (tz[inner] > 0).mean() > 0.99          # positive-down convention
    assert np.corrcoef(tx[inner].ravel(), tx_a[inner].ravel())[0, 1] > 0.98
    rel = np.abs(tz[inner] - tz_a[inner]).max() / np.abs(tz_a[inner]).max()
    assert rel < 0.05, rel


def test_euler_n1_recovers_point_source_exactly_with_analytic_derivatives():
    shape = (160, 160)
    T, tx, ty, tz, (x0, y0) = _point_source_field(shape, (80, 80), 500.0)
    valid = np.ones(shape, bool)
    sol = E.euler_solutions(tx, ty, tz, T, valid, n_index=1.0, half=8, depth_band=(100, 3000))
    m = sol["ok"]
    assert m.sum() >= 150   # only windows containing the source can accept it (~17x17)
    assert np.abs(sol["z0"][m] - 500.0).max() < 1.0
    assert np.abs(sol["x0"][m] - x0).max() < 1.0
    assert np.abs(sol["y0"][m] - y0).max() < 1.0


def test_euler_n0_contact_recovers_source_from_degree0_field():
    """N = 0 (contact) path, the one used in production.

    T = atan2(X*Y, z0*R) with X = x-x0, Y = y-y0, R = sqrt(X^2+Y^2+z0^2) is
    homogeneous of degree 0 in (X, Y, z - z0) at fixed z0, so the exact Euler
    equation holds with N = 0. Its gradient is not collinear, so the source is
    identifiable. Derivatives are central differences with a 1 m step.
    (A purely 1-D contact, T = atan2(u, w), was rejected as a test: it depends on
    one linear combination of x and y, so its along-strike position is unidentifiable.)
    """
    shape = (160, 160)
    x0, y0, z0 = 8000.0, 8100.0, 600.0

    def T_of(x, y, zz):
        X, Y, Z = x - x0, y - y0, zz - z0
        R = np.sqrt(X * X + Y * Y + Z * Z)
        return np.arctan2(X * Y, -Z * R)

    yy, xx = np.mgrid[0:shape[0], 0:shape[1]].astype(float) * DX
    T = T_of(xx, yy, 0.0)
    h = 1.0
    tx = (T_of(xx + h, yy, 0.0) - T_of(xx - h, yy, 0.0)) / (2 * h)
    ty = (T_of(xx, yy + h, 0.0) - T_of(xx, yy - h, 0.0)) / (2 * h)
    tz = (T_of(xx, yy, h) - T_of(xx, yy, -h)) / (2 * h)   # d/dz, z positive down
    valid = np.ones(shape, bool)
    sol = E.euler_solutions(tx, ty, tz, T, valid, n_index=0.0, half=8, depth_band=(100, 3000))
    m = sol["ok"]
    assert m.sum() >= 150   # only windows containing the source can accept it (~17x17)
    assert np.abs(sol["z0"][m] - z0).max() < 1.0
    assert np.abs(sol["x0"][m] - x0).max() < 1.0
    assert np.abs(sol["y0"][m] - y0).max() < 1.0


def test_solution_density_counts_only_valid_landings():
    shape = (60, 60)
    valid = np.zeros(shape, bool)
    valid[10:50, 10:50] = True
    ok = np.zeros(shape, bool)
    ok[20, 20] = True
    sol = dict(ok=ok, x0=np.full(shape, 2000.0, np.float32), y0=np.full(shape, 2000.0, np.float32))
    d = E.solution_density(sol, valid, DX, smooth=1)
    assert d[20, 20] == 1.0
    assert d.sum() == 1.0
    assert (d[~valid] == 0).all()


def test_solution_density_is_exact_nonnegative_integer_box_sum():
    shape = (40, 40)
    valid = np.ones(shape, bool)
    rng = np.random.default_rng(5)
    ok = rng.random(shape) < 0.05
    xs = rng.integers(0, 40, size=shape) * DX
    ys = rng.integers(0, 40, size=shape) * DX
    sol = dict(ok=ok, x0=xs.astype(np.float32), y0=ys.astype(np.float32))
    d = E.solution_density(sol, valid, DX, smooth=3)
    assert (d >= 0).all()
    assert np.array_equal(d, np.round(d))
    # each accepted solution lands in one cell and is spread over at most a 3x3 box
    assert 0 < d.sum() <= 9 * ok.sum()
