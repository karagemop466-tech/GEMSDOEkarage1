"""
Distance-weighted Tversky Index (DTI) -- the official GEMS Prize metric.

Verbatim source (fetched live 2026-10-27 from the official, public problem
description page, no login required):
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric

    TI(alpha, beta) = sum(p*g) / [sum(p*g) + alpha*sum(p*(1-g)) + beta*sum((1-p)*g)]

    k(d) = max(1 - d/R, 0)          triangular kernel, R = 300 m (3 px @ 100 m)

    TPw = sum_{g in G} max_{x: d(x,g)<=R} p(x) * k(d(x,g))
    FPw = sum_{x: p(x)>0} p(x) * [1 - max_{g in G} k(d(x,g))]
    FNw = sum_{g in G} [1 - max_{x: d(x,g)<=R} p(x) * k(d(x,g))]

    DTI(alpha, beta) = TPw / (TPw + alpha*FPw + beta*FNw + epsilon)

For this competition: alpha = 0.2, beta = 0.8 (official value, same page).

Worked-example check (official page, "Scoring example" section):
    TPw = 3.00, FPw = 1.89, FNw = 2.00 -> DTI(0.2, 0.8) = 0.60
    3.00 / (3.00 + 0.2*1.89 + 0.8*2.00) = 3.00 / 4.978 = 0.6026 -> rounds to 0.60
This algebraic identity is asserted in tests/test_metric.py::test_official_worked_example.

Implementation notes (ours, not organizer code -- the organizer has not
published their evaluator source as of this writing):
  - R = 3 px is small enough that the "max over x within R of g" term can be
    computed exactly with a brute-force windowed max over integer pixel
    offsets within the disk of radius R, rather than an approximation. This
    is exact, not a heuristic.
  - FNw reduces algebraically to |G| - TPw because every ground-truth pixel
    g has d(g, g) = 0 and is therefore included in the window used for TPw
    by construction (k(0) = 1, d(g,g)=0 <= R always).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import distance_transform_edt

EPS = 1e-9


@dataclass(frozen=True)
class DTIResult:
    dti: float
    tp_w: float
    fp_w: float
    fn_w: float
    n_ground_truth_positive: int
    n_predicted_positive: int


def _offsets_within_radius_px(radius_px: float) -> list[tuple[int, int]]:
    """All integer (dy, dx) pixel offsets with euclidean distance <= radius_px."""
    r = int(np.ceil(radius_px))
    offsets = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if (dy * dy + dx * dx) ** 0.5 <= radius_px + 1e-9:
                offsets.append((dy, dx))
    return offsets


def _shift(arr: np.ndarray, dy: int, dx: int, fill: float) -> np.ndarray:
    """Shift arr by (dy, dx), filling vacated edges with `fill`."""
    out = np.full_like(arr, fill)
    h, w = arr.shape
    src_y0, src_y1 = max(0, -dy), min(h, h - dy)
    src_x0, src_x1 = max(0, -dx), min(w, w - dx)
    dst_y0, dst_y1 = max(0, dy), min(h, h + dy)
    dst_x0, dst_x1 = max(0, dx), min(w, w + dx)
    out[dst_y0:dst_y1, dst_x0:dst_x1] = arr[src_y0:src_y1, src_x0:src_x1]
    return out


def distance_weighted_tversky_index(
    pred: np.ndarray,
    ground_truth: np.ndarray,
    valid_mask: np.ndarray | None = None,
    *,
    alpha: float = 0.2,
    beta: float = 0.8,
    pixel_size_m: float = 100.0,
    kernel_range_m: float = 300.0,
) -> DTIResult:
    """
    Compute the official GEMS Prize distance-weighted Tversky index.

    Parameters
    ----------
    pred : (H, W) float array, probabilities in [0, 1] (NaN treated as 0
        everywhere it is not inside `valid_mask`; NaN inside `valid_mask`
        raises -- a submission must never contain NaN inside its footprint).
    ground_truth : (H, W) array, nonzero / True = known fault pixel.
    valid_mask : (H, W) bool array, True where this scoring run should
        consider the pixel (e.g. the holdout evaluation footprint). If None,
        every finite pixel of `pred` is considered valid.
    alpha, beta : Tversky penalty weights. Competition default: 0.2, 0.8.
    pixel_size_m : raster resolution in meters (100 m for this competition).
    kernel_range_m : triangular kernel support radius R (300 m official).
    """
    pred = np.asarray(pred, dtype=np.float64)
    gt = np.asarray(ground_truth) != 0

    if valid_mask is None:
        valid_mask = np.isfinite(pred)
    else:
        valid_mask = np.asarray(valid_mask, dtype=bool)

    if np.any(~np.isfinite(pred) & valid_mask):
        raise ValueError(
            "pred contains NaN/Inf inside valid_mask; a compliant submission "
            "must be fully finite within its scored footprint."
        )

    p = np.where(valid_mask, pred, 0.0)
    if np.any((p < -1e-6) | (p > 1 + 1e-6)):
        raise ValueError("pred contains values outside [0, 1] inside valid_mask")
    p = np.clip(p, 0.0, 1.0)

    radius_px = kernel_range_m / pixel_size_m

    # N(x) = max_{g in G} k(d(x, g)) = triangular kernel of distance to the
    # nearest ground-truth pixel. Exact via Euclidean distance transform.
    if gt.any():
        dist_to_gt = distance_transform_edt(~gt, sampling=(pixel_size_m, pixel_size_m))
    else:
        dist_to_gt = np.full(gt.shape, np.inf)
    N = np.clip(1.0 - dist_to_gt / kernel_range_m, 0.0, None)

    fp_w = float(np.sum(p * (1.0 - N)))

    # M(y) = max_{x: d(x,y)<=R} p(x) * k(d(x,y)), via exact windowed max
    # over integer pixel offsets within the (small) kernel radius.
    offsets = _offsets_within_radius_px(radius_px)
    M = np.zeros_like(p)
    for dy, dx in offsets:
        d_m = ((dy * pixel_size_m) ** 2 + (dx * pixel_size_m) ** 2) ** 0.5
        k = max(1.0 - d_m / kernel_range_m, 0.0)
        if k <= 0.0:
            continue
        shifted = _shift(p, dy, dx, fill=0.0) * k
        np.maximum(M, shifted, out=M)

    tp_w = float(np.sum(M[gt]))
    n_gt = int(gt.sum())
    fn_w = float(n_gt - tp_w)

    dti = tp_w / (tp_w + alpha * fp_w + beta * fn_w + EPS)

    return DTIResult(
        dti=dti,
        tp_w=tp_w,
        fp_w=fp_w,
        fn_w=fn_w,
        n_ground_truth_positive=n_gt,
        n_predicted_positive=int(np.sum(p > 0)),
    )
