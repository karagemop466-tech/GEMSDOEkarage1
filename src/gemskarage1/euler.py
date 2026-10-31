"""Euler deconvolution (Reid et al., 1990) on a gridded total-field anomaly.

Hypothesis H-E1 (session arena/<this session>, 31 Oct 2026): magnetic source
edges whose Euler depth solutions cluster in a fixed depth band mark buried
contacts / fault-bounded magnetic juxtapositions. This module is label-blind:
it never reads the mapped fault catalogue.

Conventions (checked by tests/test_h_e1_euler.py)
------------------------------------------------
* Grid spacing ``dx_m`` metres; x = columns (east), y = rows (south). All
  coordinates and derivatives are in metres / nT per metre.
* z is depth, positive DOWN; the observation surface is z = 0.
* Euler equation for a source of structural index N at (x0, y0, z0)::

      (x-x0) Tx + (y-y0) Ty + (z-z0) Tz = N (B - T)

  At z = 0 this is ``x Tx + y Ty + N T = x0 Tx + y0 Ty + z0 Tz + N B``.
  For N = 0 the background B drops out and the system has 3 unknowns.
* Vertical derivative Tz (down-positive) from the FFT: for a field generated
  below the surface, ``dT/dz_down = +|k| T_hat``. The sign is verified against
  an analytic point source in the tests.
* Windowed least squares: every window centre c contributes one solution
  ``(x0, y0, z0)`` expressed as absolute metres. Window sums are computed with
  separable 1-D correlations, which are exact (no approximation).
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from scipy.fft import next_fast_len


def fft_derivatives(field: np.ndarray, dx_m: float = 100.0, pad: int = 64):
    """Return (Tx, Ty, Tz) for a 2-D field, zero-padded to limit edge wrap.

    Tx, Ty: horizontal derivatives per metre (x east, y south).
    Tz: vertical derivative per metre, positive DOWN (``+|k|`` filter).
    """
    f = np.asarray(field, np.float64)
    h, w = f.shape
    H, W = next_fast_len(h + 2 * pad, real=True), next_fast_len(w + 2 * pad, real=True)
    padded = np.zeros((H, W), np.float64)
    padded[pad:pad + h, pad:pad + w] = f
    F = np.fft.rfft2(padded)
    ky = 2 * np.pi * np.fft.fftfreq(H, d=dx_m)
    kx = 2 * np.pi * np.fft.rfftfreq(W, d=dx_m)
    KY, KX = np.meshgrid(ky, kx, indexing="ij")
    K = np.sqrt(KX * KX + KY * KY)

    def back(spec):
        return np.fft.irfft2(spec, s=(H, W))[pad:pad + h, pad:pad + w]

    tx = back(1j * KX * F)
    ty = back(1j * KY * F)
    tz = back(K * F)
    return tx, ty, tz


def _sep(field: np.ndarray, wx: np.ndarray | None, wy: np.ndarray | None) -> np.ndarray:
    """Separable correlation of ``field`` with weights wy (rows) x wx (cols).

    ``None`` means a constant 1 along that axis. Window centred, zero outside.
    """
    out = field
    if wx is not None:
        out = ndi.correlate1d(out, wx, axis=1, mode="constant", cval=0.0)
    if wy is not None:
        out = ndi.correlate1d(out, wy, axis=0, mode="constant", cval=0.0)
    return out


def window_sums(fields: dict, half: int, dx_m: float = 100.0, names=None):
    """Window sums over a (2h+1)^2 box: S(f), Sx(f) = sum(dx*f), Sy(f) = sum(dy*f).

    ``dx``/``dy`` are neighbour offsets from the window centre in metres.
    Returns dict name -> (S, Sx, Sy). Zero padding outside the array.
    """
    ones = np.ones(2 * half + 1)
    offs = np.arange(-half, half + 1, dtype=np.float64) * dx_m
    out = {}
    for name in (names if names is not None else fields):
        f = np.asarray(fields[name], np.float64)
        out[name] = (_sep(f, ones, ones), _sep(f, offs, ones), _sep(f, ones, offs))
    return out


# Sums needed by the normal equations (see euler_solutions).
_NEEDED = ("1", "Tx", "Ty", "Tz", "T", "TxTx", "TyTy", "TzTz", "TxTy", "TxTz", "TyTz",
           "TxT", "TyT", "TzT")


def euler_solutions(tx, ty, tz, t, valid, *, n_index: float = 0.0, half: int = 10,
                    dx_m: float = 100.0, depth_band=(300.0, 3000.0), strip: int = 240):
    """Windowed Euler solutions, computed in row strips (bounded memory).

    Inputs are full-grid 2-D arrays (metres, nT/m). Returns a dict with float32
    grids ``x0``, ``y0``, ``z0`` (absolute metres from the grid origin), a bool
    grid ``ok`` (accepted solution), and the solution count.
    """
    h, w = tx.shape
    W = 2 * half + 1
    N = float(n_index)
    # Euler solutions are invariant to a common rescaling of (Tx, Ty, Tz, T) and B,
    # so normalise by the RMS vertical derivative to keep the normal matrix well scaled.
    vmask0 = np.asarray(valid, bool)
    scale = float(np.sqrt(np.mean(np.square(tz[vmask0])))) if vmask0.any() else 1.0
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("degenerate vertical derivative: cannot normalise")
    tx, ty, tz, t = (np.asarray(a, np.float64) / scale for a in (tx, ty, tz, t))
    use4 = N != 0.0
    n_u = 4 if use4 else 3
    valid = np.asarray(valid, bool)
    win_ok = ndi.binary_erosion(valid, structure=np.ones((W, W), bool), border_value=0)
    ok = np.zeros((h, w), bool)
    x0 = np.full((h, w), np.nan, np.float32)
    y0 = np.full((h, w), np.nan, np.float32)
    z0 = np.full((h, w), np.nan, np.float32)
    half_m = half * dx_m
    for r0 in range(0, h, strip):
        r1 = min(h, r0 + strip)
        a0, a1 = max(0, r0 - half), min(h, r1 + half)  # halo of ``half`` rows
        sub = dict(tx=tx[a0:a1], ty=ty[a0:a1], tz=tz[a0:a1], t=t[a0:a1], v=valid[a0:a1])
        vm = sub["v"]
        base = {"Tx": sub["tx"], "Ty": sub["ty"], "Tz": sub["tz"], "T": sub["t"],
                "1": np.ones_like(sub["tx"])}
        fields = {k: np.where(vm, val, 0.0) for k, val in base.items()}
        fields.update({
            "TxTx": fields["Tx"] ** 2, "TyTy": fields["Ty"] ** 2, "TzTz": fields["Tz"] ** 2,
            "TxTy": fields["Tx"] * fields["Ty"], "TxTz": fields["Tx"] * fields["Tz"],
            "TyTz": fields["Ty"] * fields["Tz"], "TxT": fields["Tx"] * fields["T"],
            "TyT": fields["Ty"] * fields["T"], "TzT": fields["Tz"] * fields["T"],
        })
        S = window_sums(fields, half, dx_m, names=_NEEDED)
        # Slice the halo away: rows r0..r1 of the strip.
        o0, o1 = r0 - a0, r1 - a0
        def g(key, k):
            return S[key][k][o0:o1]
        Mf = np.zeros((r1 - r0, w, n_u, n_u))
        vf = np.zeros((r1 - r0, w, n_u))
        Mf[..., 0, 0] = g("TxTx", 0); Mf[..., 1, 1] = g("TyTy", 0); Mf[..., 2, 2] = g("TzTz", 0)
        Mf[..., 0, 1] = Mf[..., 1, 0] = g("TxTy", 0)
        Mf[..., 0, 2] = Mf[..., 2, 0] = g("TxTz", 0)
        Mf[..., 1, 2] = Mf[..., 2, 1] = g("TyTz", 0)
        vf[..., 0] = g("TxTx", 1) + g("TxTy", 2) + N * g("TxT", 0)
        vf[..., 1] = g("TxTy", 1) + g("TyTy", 2) + N * g("TyT", 0)
        vf[..., 2] = g("TxTz", 1) + g("TyTz", 2) + N * g("TzT", 0)
        if use4:
            Mf[..., 0, 3] = Mf[..., 3, 0] = N * g("Tx", 0)
            Mf[..., 1, 3] = Mf[..., 3, 1] = N * g("Ty", 0)
            Mf[..., 2, 3] = Mf[..., 3, 2] = N * g("Tz", 0)
            Mf[..., 3, 3] = N * N * g("1", 0)
            vf[..., 3] = N * (g("Tx", 1) + g("Ty", 2) + N * g("T", 0))
        A = Mf[..., :n_u, :n_u].reshape(-1, n_u, n_u)
        b = vf[..., :n_u].reshape(-1, n_u)
        vmask = win_ok[r0:r1].ravel()
        d = np.linalg.det(A)
        diag = np.prod(np.diagonal(A, axis1=1, axis2=2), axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            d_rel = d / diag   # scale-free collinearity test (1 = orthogonal, 0 = degenerate)
        good = vmask & np.isfinite(d_rel) & (d_rel > 1e-10)
        theta = np.full((A.shape[0], n_u), np.nan)
        if good.any():
            theta[good] = np.linalg.solve(A[good], b[good][..., None])[..., 0]
        rows, cols = np.mgrid[r0:r1, 0:w]
        cxs = cols.ravel() * dx_m
        cys = rows.ravel() * dx_m
        X0 = cxs + theta[:, 0]
        Y0 = cys + theta[:, 1]
        Z0 = theta[:, 2]
        inside = (np.abs(theta[:, 0]) <= half_m) & (np.abs(theta[:, 1]) <= half_m)
        in_band = (Z0 >= depth_band[0]) & (Z0 <= depth_band[1])
        acc = good & inside & in_band & np.isfinite(theta).all(axis=1)
        ok[r0:r1] = acc.reshape(r1 - r0, w)
        x0[r0:r1] = X0.reshape(r1 - r0, w).astype(np.float32)
        y0[r0:r1] = Y0.reshape(r1 - r0, w).astype(np.float32)
        z0[r0:r1] = Z0.reshape(r1 - r0, w).astype(np.float32)
    return dict(ok=ok, x0=x0, y0=y0, z0=z0, n_index=N, half=half,
                window_m=float(W * dx_m), depth_band=list(depth_band),
                n_solutions=int(ok.sum()), n_windows=int(win_ok.sum()))


def solution_density(sol: dict, valid: np.ndarray, dx_m: float = 100.0, smooth: int = 3) -> np.ndarray:
    """Count of accepted Euler solutions per cell (solution location), smoothed by a box.

    Depth-consistent clustering: a contact that many windows agree on produces a
    high count. Only solutions landing inside ``valid`` are counted.
    """
    h, w = valid.shape
    ok = sol["ok"]
    xs = np.rint(sol["x0"][ok] / dx_m).astype(np.int64)
    ys = np.rint(sol["y0"][ok] / dx_m).astype(np.int64)
    inb = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
    xs, ys = xs[inb], ys[inb]
    count = np.bincount(ys * w + xs, minlength=h * w).reshape(h, w).astype(np.float64)
    count *= valid
    if smooth and smooth > 1:
        # Exact integer box sum. uniform_filter (running-sum) leaves round-off
        # negatives (~-6e-14) on empty cells, which broke the [0,1] normalisation.
        ones = np.ones(smooth)
        count = _sep(count, ones, ones)
    count = np.maximum(count, 0.0)  # exact integers already; guard only against -0.0
    return count * valid
