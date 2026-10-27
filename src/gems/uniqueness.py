"""
Lane-discipline / duplicate checker (parallel-run protocol rule 1):

    "If your raster's rank-correlation with any registry raster exceeds
    0.90, or more than 70% of your dots fall within 3 px of one registry
    raster's dots, you have drifted into another lane: log it as a
    duplicate and stop. Check this on the surface before placement AND on
    the final dots."

This module implements both checks exactly, generically, so any future
candidate (not just this session's zero baseline) can be screened against a
registry of prior rasters before being proposed as a new, unique submission.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

DUPLICATE_SPEARMAN_THRESHOLD = 0.90
DUPLICATE_OVERLAP_FRACTION_THRESHOLD = 0.70
DUPLICATE_OVERLAP_RADIUS_PX = 3


@dataclass
class UniquenessResult:
    spearman_rho: float
    fraction_within_radius: float
    is_duplicate: bool


def surface_spearman(a: np.ndarray, b: np.ndarray, max_samples: int = 2_000_000) -> float:
    """
    Rank correlation between two equal-shaped rasters, restricted to pixels
    finite in both. Subsamples deterministically for very large rasters to
    keep this fast; the competition grid (~12.3M pixels) is subsampled.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {a.shape} vs {b.shape}")
    mask = np.isfinite(a) & np.isfinite(b)
    av, bv = a[mask], b[mask]
    if av.size == 0:
        return 0.0
    if av.size > max_samples:
        rng = np.random.default_rng(0)
        idx = rng.choice(av.size, size=max_samples, replace=False)
        av, bv = av[idx], bv[idx]
    if np.all(av == av[0]) or np.all(bv == bv[0]):
        # A constant array (e.g. an all-zero baseline) has no rank variance;
        # correlation is undefined, and by construction cannot "drift into"
        # another lane's pattern. Report 0.0 rather than NaN.
        return 0.0
    rho, _ = spearmanr(av, bv)
    return float(rho) if np.isfinite(rho) else 0.0


def fraction_of_positives_within_radius(
    candidate_positive: np.ndarray,
    registry_positive: np.ndarray,
    radius_px: float = DUPLICATE_OVERLAP_RADIUS_PX,
) -> float:
    """
    Fraction of `candidate_positive` pixels that lie within `radius_px` of
    any `registry_positive` pixel (the "70% of dots within 3px" check).
    """
    candidate_positive = np.asarray(candidate_positive, dtype=bool)
    registry_positive = np.asarray(registry_positive, dtype=bool)
    n_candidate = int(candidate_positive.sum())
    if n_candidate == 0:
        return 0.0
    if not registry_positive.any():
        return 0.0
    dist = distance_transform_edt(~registry_positive)
    within = dist[candidate_positive] <= radius_px
    return float(within.mean())


def check_against_registry_raster(
    candidate: np.ndarray,
    registry: np.ndarray,
    candidate_positive_threshold: float = 0.0,
) -> UniquenessResult:
    """Run both lane-discipline checks of a candidate against one registry raster."""
    rho = surface_spearman(candidate, registry)
    cand_pos = np.asarray(candidate) > candidate_positive_threshold
    reg_pos = np.asarray(registry) > candidate_positive_threshold
    frac = fraction_of_positives_within_radius(cand_pos, reg_pos)
    is_dup = (
        abs(rho) > DUPLICATE_SPEARMAN_THRESHOLD
        or frac > DUPLICATE_OVERLAP_FRACTION_THRESHOLD
    )
    return UniquenessResult(spearman_rho=rho, fraction_within_radius=frac, is_duplicate=is_dup)
