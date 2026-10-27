"""One-call GPC-Z pipeline (what scripts/run_experiment3_build.py does, reusable)."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
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
    phys = physics_field()
    _, g = damage_zone_prior_full()
    gg = g if coupling == "linear" else np.sqrt(g)
    field = (phys * gg).astype(np.float32)
    dots = emission.emit(field, budget, grid.catalogue(), spacing=SPACING, apron_px=APRON)
    return dots, field


def ship(dots: np.ndarray, field: np.ndarray, tag: str, note: str, out_dir: Path) -> dict:
    n = int(dots.sum())
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest8 = hashlib.sha256(np.packbits(dots).tobytes()).hexdigest()[:8]
    slug = f"gemsk1-{tag}-{n}dots-{stamp}-{digest8}"
    rec = submission.write_bundle(dots, out_dir, slug, note[:140])
    rec["uniqueness"] = uniqueness.check(dots, surface=field)
    return rec
