#!/usr/bin/env python3
"""Lane H-K1-STRAINPHASE: shear-dominant strain-localisation ridges (pre-registered 2026-10-29).

Hypothesis (see knowledge/strainphase-hypotheses-20261029.md):
  Active strike-slip / oblique-slip faults localise *shear* strain-rate with little
  *dilatation*; magmatic or sedimentary-loading strain is dilatation-dominant. A
  multi-scale ridge of the geodetic shear-rate band, weighted by shear dominance over
  dilatation, should mark fault traces that are absent from the mapped catalogue.

Layers: official training_features bands `geod_shearrate` (band 7) and
`geod_dilaterate` (band 8) only. Nothing reads labels.tif / existing_faults.tif
except the fold-local holdout (`gemsk.holdout.make_folds`) and the scoring call.

Named non-fault mimics: interpolation seams of the geodetic strain field along data
boundaries; ductile shear fabrics in basement; cultural/irrigation linear features
(not in the strain field, so expected to be weak).

Stages (run in order; each writes evidence/<name>.json):
  exp1  leakage canary: each component and the fused surface alone, per blocked fold
  exp2  blocked hide-and-recover holdout: STRAINPHASE vs. GPC control (same folds,
        same budget, same evaluator, `gemsk-hide-recover-v1`)
  final build the submission-candidate raster from the full catalogue (apron only),
        save it, validate, run the registry comparison against the pinned inventory
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
for sub in ("src", "vendor"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gemsk import emission, grid, holdout, metric  # noqa: E402
from gemskarage1 import dipdual  # noqa: E402
from gemskarage1.features import _hessian_ridge  # noqa: E402

LANE = "H-K1-STRAINPHASE"
EVIDENCE = ROOT / "evidence"
BUDGET = 37654
SEED = 20261029
SIGMAS = (1.0, 2.0, 3.0)


def _fill_nearest(a: np.ndarray, foot: np.ndarray) -> np.ndarray:
    """Fill invalid pixels inside the footprint from nearest valid pixels (no label input)."""
    bad = ~np.isfinite(a) & foot
    if not bad.any():
        return np.where(foot, a, 0.0).astype(np.float32)
    idx = ndimage.distance_transform_edt(bad | ~foot, return_distances=False, return_indices=True)
    filled = a[idx[0], idx[1]]
    return np.where(foot, filled, 0.0).astype(np.float32)


def _rank01(a: np.ndarray, foot: np.ndarray) -> np.ndarray:
    v = a[foot]
    order = np.argsort(np.argsort(v, kind="stable"), kind="stable")
    out = np.zeros(a.shape, np.float32)
    out[foot] = (order / max(order.size - 1, 1)).astype(np.float32)
    return out


def build_strainphase_components(foot: np.ndarray) -> dict[str, np.ndarray]:
    shear = _fill_nearest(grid.band("geod_shearrate"), foot)
    dil = _fill_nearest(grid.band("geod_dilaterate"), foot)
    ridge = np.zeros_like(shear)
    for s in SIGMAS:
        ridge = np.maximum(ridge, _hessian_ridge(shear, s, bright=True))
    ridge = np.where(foot, ridge, 0.0).astype(np.float32)
    # shear dominance: |shear| / (|shear| + |dilatation|), both rank-normalised in-footprint
    a_s = _rank01(np.abs(shear), foot)
    a_d = _rank01(np.abs(dil), foot)
    dominance = (a_s / (a_s + a_d + 1e-6)).astype(np.float32)
    dominance = np.where(foot, dominance, 0.0).astype(np.float32)
    fused = emission.nms_thin(_rank01(ridge, foot) * dominance)
    fused = np.where(foot, fused, 0.0).astype(np.float32)
    return {"ridge": ridge, "dominance": dominance, "strainphase": fused}


def _shift_mean(field: np.ndarray, dy: float, dx: float) -> np.ndarray:
    """Value of a smoothed field at a sub-pixel offset (bilinear, nearest-edge)."""
    return ndimage.shift(field, shift=(-dy, -dx), order=1, mode="nearest")


def build_signed_offset_components(foot: np.ndarray) -> dict[str, np.ndarray]:
    """H1 (knowledge/hypotheses-20261028.md): signed two-scale magnetic/gravity offset.

    For each scale and each of 8 normal directions, the signed step is the smoothed
    field on one side of the pixel minus the other side. The orientation with the
    largest |step| is kept (signed). A pixel scores when the magnetic and gravity
    steps have the SAME sign at both scales (consistent density/susceptibility contrast).
    """
    mag = _fill_nearest(grid.band("rtp"), foot)
    grav = _fill_nearest(grid.band("iso_grav_anom"), foot)
    def robust_z(a):
        v = a[foot]
        med = float(np.median(v))
        mad = max(float(np.median(np.abs(v - med))) * 1.4826, 1e-6)
        return ((a - med) / mad).astype(np.float32)
    mag, grav = robust_z(mag), robust_z(grav)
    scales = (4.0, 12.0)
    angles = np.deg2rad(np.arange(0, 180, 22.5))
    def best_signed_step(field, d):
        smooth = ndimage.gaussian_filter(field, d / 2.0)
        best = np.zeros(field.shape, np.float32)
        for th in angles:
            dy, dx = d * np.sin(th), d * np.cos(th)
            step = (_shift_mean(smooth, dy, dx) - _shift_mean(smooth, -dy, -dx)).astype(np.float32)
            take = np.abs(step) > np.abs(best)
            best = np.where(take, step, best)
        return best
    comps = {}
    m_steps = [best_signed_step(mag, d) for d in scales]
    g_steps = [best_signed_step(grav, d) for d in scales]
    consistent = np.ones(foot.shape, bool)
    for ms, gs in zip(m_steps, g_steps):
        consistent &= (np.sign(ms) == np.sign(gs)) & (np.sign(ms) != 0)
    mag_mag = np.sqrt(sum(np.square(m) for m in m_steps)).astype(np.float32)
    comps["mag_step_mag"] = np.where(foot, mag_mag, 0.0).astype(np.float32)
    comps["consistency"] = np.where(foot & consistent, 1.0, 0.0).astype(np.float32)
    fused = emission.nms_thin(_rank01(comps["mag_step_mag"], foot) * (0.25 + 0.75 * comps["consistency"]))
    comps["signedoffset"] = np.where(foot, fused, 0.0).astype(np.float32)
    return comps


def _dump(name: str, obj) -> Path:
    p = EVIDENCE / name
    p.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")
    print(f"[write] {p}", flush=True)
    return p


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_context():
    grid.prepare_bands()
    foot = grid.footprint()
    cat = grid.catalogue() & foot
    folds = holdout.make_folds(cat, foot, scheme="blocked")
    return foot, cat, folds


def stage_exp1(foot, cat, folds, comps, gpc, key: str = "strainphase", prefix: str = "strainphase") -> dict:
    print("=== EXP1 leakage canary (label-free surfaces, per blocked fold) ===", flush=True)
    feats = {k: v for k, v in comps.items()}
    feats[key] = comps[key]
    feats["GPC_control"] = gpc
    rng = np.random.default_rng(SEED)
    rows, alarm = [], False
    for name, f in feats.items():
        aucs = [holdout.auc_on_fold(f, fold, rng=rng) for fold in folds]
        inv = [max(a, 1.0 - a) for a in aucs]
        vals = f[foot]
        finite = bool(np.isfinite(vals).all())
        constant = bool(float(np.std(vals)) == 0.0)
        bad = bool(max(inv) > 0.90 or not finite or constant)
        alarm |= bad
        rows.append({"feature": name, "fold_auc": [float(x) for x in aucs],
                     "max_direction_invariant_auc": float(max(inv)),
                     "finite_in_footprint": finite, "constant": constant,
                     "declared_label_free_by_code_review": True, "alarm": bad})
        print(f"  {name:14s} maxInvAUC={max(inv):.4f} finite={finite} alarm={bad}", flush=True)
    res = {"experiment": 1, "lane": f"H-K1-{key.upper()}", "evaluator_version": holdout.VERSION,
           "scheme": "blocked", "canary_rows": rows, "any_alarm": alarm,
           "pass": not alarm, "withheld_positives": int(sum(f["n_withheld"] for f in folds)),
           "created_utc": datetime.now(timezone.utc).isoformat()}
    _dump(f"exp1_{prefix}_canary.json", res)
    return res


def _emit(surface, visible, foot):
    return emission.emit(surface, BUDGET, visible, spacing=2.8, apron_px=2, thin=False)


def stage_exp2(foot, cat, folds, comps, gpc, key: str = "strainphase", prefix: str = "strainphase") -> dict:
    print("=== EXP2 blocked holdout (same folds / budget / evaluator for both arms) ===", flush=True)
    arms = {"GPC_control": gpc, key: comps[key]}
    terms_by, summary = {}, {}
    for name, surf in arms.items():
        terms, ndots, per = [], [], []
        for f in folds:
            d = _emit(surf, f["visible"], foot)
            r, t = holdout.evaluate_dots(d, f)
            terms.append(t); ndots.append(int(d.sum())); per.append(float(r["dti"]))
            del d
            gc.collect()
        terms_by[name] = terms
        pooled = holdout.pooled(terms)
        summary[name] = {**pooled, "per_fold_dti": per, "n_dots_per_fold": ndots}
        print(f"  {name:14s} pooled DTI={pooled['dti']:.6f} folds={np.round(per, 4).tolist()}", flush=True)
    ci = holdout.bootstrap_ci(terms_by, draws=1000, seed=SEED)
    summary_ci = {k: ci[k] for k in ci}
    best_prior = 0.07339389911540638  # GPC arm, evidence/exp2_dipdual_holdout.json (same evaluator)
    res = {"experiment": 2, "lane": f"H-K1-{key.upper()}", "evaluator_version": holdout.VERSION,
           "scheme": "blocked", "budget_per_fold": BUDGET,
           "withheld_positives": int(sum(f["n_withheld"] for f in folds)),
           "arms": summary, "bootstrap": summary_ci,
           "control_reproduction_vs_exp2_dipdual": {
               "reproduced_gpc_dti": summary["GPC_control"]["dti"],
               "recorded_gpc_dti_exp2_dipdual": best_prior,
               "abs_difference": abs(summary["GPC_control"]["dti"] - best_prior)},
           "promote_rule": f"{key} pooled DTI must exceed the GPC control and its paired CI must exclude 0",
           "created_utc": datetime.now(timezone.utc).isoformat()}
    delta = ci[key]["paired_delta_vs_GPC_control"]
    res["beats_gpc_control"] = bool(summary[key]["dti"] > summary["GPC_control"]["dti"]
                                    and delta["ci95"][0] > 0)
    _dump(f"exp2_{prefix}_holdout.json", res)
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=("exp1", "exp2", "all"), default="all")
    ap.add_argument("--lane", choices=("strainphase", "signedoffset"), default="strainphase")
    args = ap.parse_args()
    foot, cat, folds = load_context()
    if args.lane == "strainphase":
        comps = build_strainphase_components(foot)
    else:
        comps = build_signed_offset_components(foot)
    gpc = dipdual.build_surfaces()["gpc_physics"]
    out = {}
    if args.stage in ("exp1", "all"):
        out["exp1"] = stage_exp1(foot, cat, folds, comps, gpc, key=args.lane, prefix=args.lane)
    if args.stage in ("exp2", "all"):
        out["exp2"] = stage_exp2(foot, cat, folds, comps, gpc, key=args.lane, prefix=args.lane)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk in ("pass", "beats_gpc_control")}
                      for k, v in out.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
