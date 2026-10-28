"""One-call GPC-Z pipeline (what scripts/run_experiment3_build.py does, reusable)."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from . import emission, features, grid, holdout, prior, submission, uniqueness

WEIGHTS = {"step": 0.45, "curvbreak": 0.25, "lidar_step": 0.30}
GATE_FLOOR = 0.25
SPACING = 2.8
APRON = 2


def physics_field() -> np.ndarray:
    foot = grid.footprint()
    S = features.build_all()
    rk = {k: emission.rank_normalise(S[k], foot) for k in WEIGHTS}
    gate = GATE_FLOOR + (1 - GATE_FLOOR) * S["concord"]
    f = emission.nms_thin(sum(w * rk[k] for k, w in WEIGHTS.items()) * gate)
    f[~foot] = 0
    return f.astype(np.float32)


def damage_zone_prior_full() -> tuple[np.ndarray, np.ndarray]:
    """g(d) estimated from all interleaved folds, applied to distance from the FULL catalogue."""
    foot, cat = grid.footprint(), grid.catalogue()
    folds = holdout.make_folds(cat, foot, scheme="interleaved")
    dens = prior.density_from_tables([prior.fold_table(f) for f in folds])
    return dens, prior.apply(dens, cat)


def build(budget: int, coupling: str = "linear") -> tuple[np.ndarray, np.ndarray]:
    raise RuntimeError("Historical GPC-Z pipeline disabled: its saved candidate failed the literal lattice duplicate rule.")


def ship(dots: np.ndarray, field: np.ndarray, tag: str, note: str, out_dir: Path) -> dict:
    raise RuntimeError("Historical shipping helper disabled: it checked an incomplete registry after writing the raster.")
