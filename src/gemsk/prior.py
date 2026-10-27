"""Damage-zone prior g(d): density of (withheld) catalogue strands vs distance to the visible catalogue.

Estimated non-parametrically in distance bins from a hide-and-recover split, then smoothed into a
monotone-decreasing step function for d >= apron and normalised to max 1. In the holdout the prior
for fold k is estimated from the OTHER folds (leave-one-fold-out) so no fold sees its own truth.
For the final build the prior is estimated from all folds and the distance is measured to the full
catalogue (everything the live scorer treats as already known).
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

BINS = np.array([0, 3, 4, 6, 8, 10, 15, 20, 30, 40, 60, 80, 120, 200, 100000], dtype=float)


def fold_table(fold: dict) -> tuple[np.ndarray, np.ndarray]:
    d = ndimage.distance_transform_edt(~fold["visible"])
    act = fold["active"]
    tr = fold["withheld"] & act
    ht, _ = np.histogram(d[tr], BINS)
    ha, _ = np.histogram(d[act], BINS)
    return ht.astype(float), ha.astype(float)


def density_from_tables(tables: list[tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    ht = np.sum([t[0] for t in tables], axis=0)
    ha = np.sum([t[1] for t in tables], axis=0)
    dens = ht / np.maximum(ha, 1.0)
    # enforce monotone non-increasing beyond the peak (isotonic from the max bin outward) and floor
    peak = int(np.argmax(dens))
    for i in range(peak + 1, len(dens)):
        dens[i] = min(dens[i], dens[i - 1])
    dens = np.maximum(dens, dens.max() * 0.02)
    return dens / dens.max()


def apply(dens: np.ndarray, visible: np.ndarray) -> np.ndarray:
    d = ndimage.distance_transform_edt(~visible)
    idx = np.clip(np.searchsorted(BINS, d, side="right") - 1, 0, len(dens) - 1)
    return dens[idx].astype(np.float32)
