"""Synthetic check of the H-E1 window Euler solver against an analytic point source.

For T = 1/r (homogeneous of degree -1, so structural index N = 1 with no background), the
exact Euler solution is the source position and depth. With z positive down and the
observation on the surface, Tz = z_s / r^3 (per metre). The solver must recover the truth.
"""
import numpy as np

from scripts.run_he1_euler_deconvolution import DEPTH_MAX_M, DEPTH_MIN_M, euler_solutions


def _point_source(H=61, Wd=61, row_s=28.7, col_s=30.4, z_s=500.0, cell=100.0):
    rows, cols = np.mgrid[0:H, 0:Wd].astype(float)
    dx = (cols - col_s) * cell
    dy = -(rows - row_s) * cell            # northing = -row, the runner's convention
    r = np.sqrt(dx ** 2 + dy ** 2 + z_s ** 2)
    T = 1.0 / r
    Tz = z_s / r ** 3                       # d/dz, z positive down, per metre
    core = np.zeros((H, Wd), bool)
    core[6:-6, 6:-6] = True
    return T, Tz, core, row_s, col_s, z_s


def test_euler_recovers_point_source_position_and_depth():
    T, Tz, core, row_s, col_s, z_s = _point_source()
    acc, row0, col0, z0 = euler_solutions(T, Tz, core, N=1)
    assert acc.sum() >= 80, "solver accepted too few windows (expect about 10x10 around one source)"
    assert abs(np.median(row0[acc]) - row_s) < 0.05
    assert abs(np.median(col0[acc]) - col_s) < 0.05
    assert abs(np.median(z0[acc]) - z_s) < 0.05 * z_s
    assert np.all((z0[acc] >= DEPTH_MIN_M) & (z0[acc] <= DEPTH_MAX_M))


def test_euler_chunking_does_not_change_solutions():
    T, Tz, core, *_ = _point_source()
    a1, r1, c1, z1 = euler_solutions(T, Tz, core, N=1, chunk=256)
    a2, r2, c2, z2 = euler_solutions(T, Tz, core, N=1, chunk=7)
    assert np.array_equal(a1, a2)
    both = a1 & a2
    assert np.allclose(r1[both], r2[both], atol=1e-9)
    assert np.allclose(c1[both], c2[both], atol=1e-9)
    assert np.allclose(z1[both], z2[both], atol=1e-6)
