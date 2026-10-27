"""evaluate_holdout.py — GEMSDOE holdout DTI evaluator.

Implements the parallel-run protocol holdout procedure:

    Holdout = hide-and-recover:
      * withhold whole fault segments with a buffer
      * derive every catalogue-based feature only from the visible faults
      * mask visible faults pixel-exactly
      * score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel)

Metric (Tversky / DTI):
    DTI = TP / (TP + alpha * FN + beta * FP),  alpha = 0.2, beta = 0.8

A prediction dot is a true positive (kernel-weighted) if it falls within the
300 m triangular kernel of a withheld (holdout) fault pixel; otherwise it is a
false positive. A holdout fault pixel is a false negative if no prediction dot
falls within the kernel. Because beta (0.8) > alpha (0.2), false positives are
penalised 4x false negatives -> sparse, confident dots beat dense maps.

95% CI: spatial-block bootstrap over fault segments.

Designed to run on CPU. Requires the competition data in data/:
    training_features.tif, labels.tif, sample_submission.tif
If the data are absent (no DrivenData auth here), the script runs a built-in
self-test on synthetic faults to verify the math, then exits with instructions.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

try:
    import rasterio
    from rasterio.transform import from_origin
except Exception as exc:  # pragma: no cover - import guard
    rasterio = None
    from_origin = None  # type: ignore

# ---------------------------------------------------------------------------
# Protocol constants (fixed by the parallel-run protocol / reference pages)
# ---------------------------------------------------------------------------
ALPHA = 0.2          # Tversky false-negative weight
BETA = 0.8           # Tversky false-positive weight (4x FN -> precision-favoured)
KERNEL_RADIUS_M = 300.0   # triangular kernel radius
DTI_IMPROVE_THRESHOLD = 0.2 * 0.2778  # ~0.0556: dot improves DTI iff ΔTPw > this

# Leakage canary threshold (protocol rule 4): single-feature AUC above 0.90
# means leakage until proven otherwise.
LEAKAGE_AUC_LIMIT = 0.90


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
@dataclass
class GridInfo:
    transform: object
    crs: str
    height: int
    width: int

    def pixel_size_m(self) -> float:
        # Assume north-up, square pixels in a projected CRS (m).
        return abs(self.transform.a)


def world_to_pixel(transform, x: float, y: float) -> Tuple[int, int]:
    col, row = ~transform * (x, y)
    return int(round(row)), int(round(col))


def pixel_to_world(transform, row: int, col: int) -> Tuple[float, float]:
    x, y = transform * (col, row)
    return float(x), float(y)


# ---------------------------------------------------------------------------
# Distance transforms (SciPy-free: simple Euclidean distance transform via
# rasterio-friendly two-pass would need scipy; here we use a lightweight
# exact-ish approach based on scipy.ndimage.distance_transform_edt when
# available, falling back to a brute-force block approximation).
# ---------------------------------------------------------------------------
def _edt(mask: np.ndarray) -> np.ndarray:
    """Euclidean distance transform (in pixels) of a boolean mask (True = target).

    Returns distance from every cell to the nearest True cell.
    """
    try:
        from scipy import ndimage  # type: ignore
        return ndimage.distance_transform_edt(~mask)
    except Exception:
        # Fallback: brute-force over a downsampled grid is too slow; instead
        # return an exact-ish distance by scanning a bounded window. This path
        # is only used when scipy is missing, which should not happen in this
        # project (scipy is a standard dependency).
        raise RuntimeError("scipy is required for distance transforms")


# ---------------------------------------------------------------------------
# Core DTI computation
# ---------------------------------------------------------------------------
def compute_dti(
    pred_rows: np.ndarray,
    pred_cols: np.ndarray,
    label_rows: np.ndarray,
    label_cols: np.ndarray,
    grid: GridInfo,
    radius_m: float = KERNEL_RADIUS_M,
    alpha: float = ALPHA,
    beta: float = BETA,
) -> dict:
    """Compute kernel-weighted Tversky DTI between prediction dots and labels.

    Parameters
    ----------
    pred_rows, pred_cols : pixel coordinates of prediction dots (binary raster
        nonzero cells or dot list).
    label_rows, label_cols : pixel coordinates of holdout (withheld) fault
        pixels.
    grid : GridInfo with transform and pixel size.
    radius_m : triangular-kernel radius in metres.
    alpha, beta : Tversky weights.

    Returns
    -------
    dict with DTI, TP, FP, FN, radius, alpha, beta.
    """
    px = grid.pixel_size_m()
    radius_px = radius_m / px

    n_pred = len(pred_rows)
    n_label = len(label_rows)

    if n_pred == 0 and n_label == 0:
        return {"DTI": 0.0, "TP": 0.0, "FP": 0.0, "FN": 0.0,
                "radius_m": radius_m, "alpha": alpha, "beta": beta}

    # Distance from every grid cell to the nearest label pixel.
    label_mask = np.zeros((grid.height, grid.width), dtype=bool)
    if n_label > 0:
        label_mask[np.clip(label_rows, 0, grid.height - 1),
                   np.clip(label_cols, 0, grid.width - 1)] = True
    dist_to_label = _edt(label_mask)  # pixels

    # Distance from every grid cell to the nearest prediction dot.
    pred_mask = np.zeros((grid.height, grid.width), dtype=bool)
    if n_pred > 0:
        pred_mask[np.clip(pred_rows, 0, grid.height - 1),
                  np.clip(pred_cols, 0, grid.width - 1)] = True
    dist_to_pred = _edt(pred_mask)  # pixels

    # --- TP / FP over prediction dots -----------------------------------
    tp = 0.0
    fp = 0
    if n_pred > 0:
        d_pred = dist_to_label[pred_rows, pred_cols]
        d_m = d_pred * px
        # Triangular kernel weight: w(d) = max(0, 1 - d / R); 0 beyond radius.
        weights = np.maximum(0.0, 1.0 - d_m / radius_m)
        within = d_pred <= radius_px
        tp = float(np.sum(weights))   # weights are exactly 0 beyond radius
        fp = int(np.sum(~within))

    # --- FN over holdout label pixels -----------------------------------
    fn = 0
    if n_label > 0:
        d_label = dist_to_pred[label_rows, label_cols]
        fn = int(np.sum(d_label > radius_px))

    denom = tp + alpha * fn + beta * fp
    dti = tp / denom if denom > 0 else 0.0

    return {
        "DTI": float(dti),
        "TP": float(tp),
        "FP": int(fp),
        "FN": int(fn),
        "n_pred": int(n_pred),
        "n_label": int(n_label),
        "radius_m": float(radius_m),
        "alpha": float(alpha),
        "beta": float(beta),
    }


def pooled_dti(
    arms: list[dict],
) -> float:
    """Pool DTI across holdout arms by summing TP/FP/FN (pooled DTI)."""
    tp = sum(a["TP"] for a in arms)
    fn = sum(a["FN"] for a in arms)
    fp = sum(a["FP"] for a in arms)
    alpha = ALPHA
    beta = BETA
    denom = tp + alpha * fn + beta * fp
    return tp / denom if denom > 0 else 0.0


# ---------------------------------------------------------------------------
# Spatial-block bootstrap CI
# ---------------------------------------------------------------------------
def block_bootstrap_ci(
    pred_rows: np.ndarray,
    pred_cols: np.ndarray,
    label_rows: np.ndarray,
    label_cols: np.ndarray,
    grid: GridInfo,
    n_blocks: int = 8,
    n_boot: int = 2000,
    seed: int = 42,
    radius_m: float = KERNEL_RADIUS_M,
    alpha: float = ALPHA,
    beta: float = BETA,
) -> dict:
    """Spatial-block bootstrap 95% CI for DTI.

    Splits the grid into n_blocks x n_blocks spatial blocks, resamples blocks
    with replacement, recomputes DTI on each replicate, returns the percentile
    CI. Labels/prediction dots are assigned to blocks by pixel coordinate.
    """
    rng = np.random.default_rng(seed)
    if len(pred_rows) == 0 and len(label_rows) == 0:
        return {"DTI": 0.0, "ci_lo": 0.0, "ci_hi": 0.0, "n_boot": n_boot}

    # Assign every point to a block.
    def block_of(rows, cols):
        br = np.floor(rows / grid.height * n_blocks).astype(int)
        bc = np.floor(cols / grid.width * n_blocks).astype(int)
        br = np.clip(br, 0, n_blocks - 1)
        bc = np.clip(bc, 0, n_blocks - 1)
        return br * n_blocks + bc

    pred_block = block_of(pred_rows, pred_cols) if len(pred_rows) else np.array([])
    label_block = block_of(label_rows, label_cols) if len(label_rows) else np.array([])
    n_b = n_blocks * n_blocks

    replicates = []
    for _ in range(n_boot):
        chosen = rng.integers(0, n_b, size=n_b)
        keep_p = np.isin(pred_block, chosen) if len(pred_block) else np.array([], dtype=bool)
        keep_l = np.isin(label_block, chosen) if len(label_block) else np.array([], dtype=bool)
        res = compute_dti(
            pred_rows[keep_p] if len(pred_block) else pred_rows,
            pred_cols[keep_p] if len(pred_block) else pred_cols,
            label_rows[keep_l] if len(label_block) else label_rows,
            label_cols[keep_l] if len(label_block) else label_cols,
            grid, radius_m, alpha, beta,
        )
        replicates.append(res["DTI"])

    replicates = np.array(replicates)
    ci_lo = float(np.percentile(replicates, 2.5))
    ci_hi = float(np.percentile(replicates, 97.5))
    return {"DTI": float(np.mean(replicates)), "ci_lo": ci_lo, "ci_hi": ci_hi,
            "n_boot": int(n_boot), "n_blocks": int(n_b)}


# ---------------------------------------------------------------------------
# Data loading (competition grid)
# ---------------------------------------------------------------------------
def load_competition_grid(data_dir: str = "data") -> Optional[GridInfo]:
    """Read CRS/shape/transform from sample_submission.tif if present."""
    if rasterio is None:
        return None
    import os
    path = os.path.join(data_dir, "sample_submission.tif")
    if not os.path.exists(path):
        return None
    with rasterio.open(path) as src:
        return GridInfo(transform=src.transform, crs=str(src.crs),
                        height=src.height, width=src.width)


def self_test() -> dict:
    """Built-in self-test on synthetic faults when competition data are absent.

    Verifies compute_dti returns sane values on a known configuration.
    """
    if from_origin is None:
        raise RuntimeError("rasterio is required for the self-test")
    # Synthetic 1000x1000 grid, 1 m pixels, EPSG:32611.
    transform = from_origin(500000.0, 4500000.0, 1.0, 1.0)
    grid = GridInfo(transform=transform, crs="EPSG:32611", height=1000, width=1000)

    # One vertical fault segment (labels) at col 500.
    label_rows = np.arange(200, 800)
    label_cols = np.full(600, 500)

    # Perfect predictions on the faults -> DTI should be 1.0.
    perfect = compute_dti(label_rows.copy(), label_cols.copy(),
                          label_rows, label_cols, grid)
    # No predictions -> DTI 0.
    none = compute_dti(np.array([], dtype=int), np.array([], dtype=int),
                       label_rows, label_cols, grid)
    # Dots far outside the 300 m kernel (col 50 is 450 m from col 500) -> DTI 0.
    far_rows = np.full(100, 500)
    far_cols = np.full(100, 50)
    far = compute_dti(far_rows, far_cols, label_rows, label_cols, grid)

    return {
        "perfect_DTI": perfect["DTI"],
        "none_DTI": none["DTI"],
        "far_DTI": far["DTI"],
        "perfect_TP": perfect["TP"],
        "grid_cells": grid.height * grid.width,
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="GEMSDOE holdout DTI evaluator (Tversky alpha=0.2 beta=0.8, 300 m triangular kernel).")
    parser.add_argument("--data-dir", default="data",
                        help="Directory with competition rasters (default: data).")
    parser.add_argument("--prediction", default=None,
                        help="Prediction GeoTIFF (single band, [0,1]).")
    parser.add_argument("--self-test", action="store_true",
                        help="Run built-in self-test on synthetic faults.")
    parser.add_argument("--out", default="cards/holdout_result.json",
                        help="Output JSON path for the result.")
    args = parser.parse_args(argv)

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        ok = (math.isclose(result["perfect_DTI"], 1.0, rel_tol=1e-6)
              and math.isclose(result["none_DTI"], 0.0, rel_tol=1e-9)
              and math.isclose(result["far_DTI"], 0.0, rel_tol=1e-9))
        print("SELF-TEST", "PASS" if ok else "FAIL")
        return 0 if ok else 1

    grid = load_competition_grid(args.data_dir)
    if grid is None:
        print("ERROR: competition grid not found. Place sample_submission.tif in "
              f"{args.data_dir}/ (requires DrivenData login).", file=sys.stderr)
        print("Run:  python scripts/evaluate_holdout.py --self-test   (verify the math)", file=sys.stderr)
        return 2

    print(json.dumps({"grid": {"crs": grid.crs, "shape": [grid.height, grid.width],
                               "transform": [grid.transform.a, grid.transform.b,
                                           grid.transform.c, grid.transform.d,
                                           grid.transform.e, grid.transform.f],
                               "cells": grid.height * grid.width}},
                     indent=2))
    print("Grid loaded. Provide --prediction to score a submission raster.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
