#!/usr/bin/env python3
"""Release gate for the H-KP1 candidate: format, uniqueness, and a labelled projection.

The gate is deliberately split from the *build*.  It reads the bytes on disk,
re-derives every number from scratch, and writes one machine-readable decision:

* ``format``        — the shared template's local preflight on the saved file
                      (CRS / shape / transform / dtype / [0,1] / no NaN).
* ``uniqueness``    — the literal parallel-run rules (|Spearman| > 0.90 or > 70 %
                      of dots within 3 px of another raster's dots) applied to
                      every pinned registry raster, **plus** the chance-level
                      calibration that the literal rule omits.  The calibration is
                      the finding of EXP1: all 36 pairs among the nine focus files
                      already score 0.9746-1.0 on the literal 3-px rule against a
                      chance level of 0.151-0.185, so the raw number cannot
                      separate "copied" from "same terrain".
* ``position``      — where the candidate sits on the four geometric covariates
                      that separate the nine known scores (dots, distance-from-
                      catalogue, 3-px clumping, kernel coverage).
* ``projection``    — a **PROJECTED** leaderboard value from a leave-one-out
                      covariate model fitted to the nine known scores.  It is not
                      a score, not a measurement, and it is reported with its LOO
                      error and its n = 9 caveat.

Exit code 0 means ``ok_to_submit`` is true.  The script never edits the TIF.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT))

from gems57 import validate                                        # noqa: E402
from gems57.uniqueness import dot_overlap, RHO_LIMIT, OVERLAP_LIMIT  # noqa: E402
from scripts import kp1_data as D                                  # noqa: E402
from scripts.kp1_exp1_forensics import FILES, SCORES, load          # noqa: E402

R3 = (np.mgrid[-3:4, -3:4][0] ** 2 + np.mgrid[-3:4, -3:4][1] ** 2) <= 9


def covariates(a: np.ndarray, fp: np.ndarray, cat: np.ndarray) -> dict:
    m = (a > 0) & fp
    n = int(m.sum())
    dc = ndi.distance_transform_edt(~cat)
    nb = ndi.convolve(m.astype(np.int16), R3.astype(np.int16), mode="constant") - m
    cov = ndi.binary_dilation(m, structure=R3)[fp].mean()
    d = dc[m]
    return dict(dots=n, d_cat_le_2px_frac=float((d <= 2).mean()),
                d_cat_2_to_15px_frac=float(((d > 2) & (d <= 15)).mean()),
                d_cat_gt_15px_frac=float((d > 15).mean()),
                median_d_cat_px=float(np.median(d)),
                clump_ge3_nbr_within_3px_frac=float((nb >= 3).mean()),
                mean_nbr_within_3px=float(nb.mean()),
                footprint_kernel_coverage=float(cov))


def projection(cand: dict, rows: dict) -> dict:
    """Leave-one-out linear projection of the leaderboard value."""
    sites = list(rows)
    X = np.array([[np.log(rows[s]["dots"]), rows[s]["d_cat_gt_15px_frac"]] for s in sites])
    y = np.array([SCORES[s] for s in sites])
    Xm, ym = X.mean(0), y.mean()
    A = np.column_stack([np.ones(len(sites)), X - Xm])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    loo = []
    for i in range(len(sites)):
        keep = np.arange(len(sites)) != i
        b, *_ = np.linalg.lstsq(A[keep], y[keep], rcond=None)
        loo.append(float(A[i] @ b))
    loo = np.array(loo)
    resid = y - loo
    xc = np.array([np.log(cand["dots"]), cand["d_cat_gt_15px_frac"]]) - Xm
    pred = float(np.array([1.0, *xc]) @ beta)
    # parameter-uncertainty bootstrap: resample the nine (raster, score) pairs
    rng = np.random.default_rng(20261031)
    draws = []
    for _ in range(2000):
        pick = rng.integers(0, len(sites), len(sites))
        Ab, yb = A[pick], y[pick]
        bb, *_ = np.linalg.lstsq(Ab, yb, rcond=None)
        draws.append(float(np.array([1.0, *xc]) @ bb))
    draws = np.array(draws)
    b2 = rows["GEMSDOE32"]
    b2_x = np.array([np.log(b2["dots"]), b2["d_cat_gt_15px_frac"]]) - Xm
    b2_pred = float(np.array([1.0, *b2_x]) @ beta)
    return dict(
        bootstrap_95_interval=[float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))],
        bootstrap_method="resample the nine (raster, score) pairs, refit OLS, 2000 draws",
        champion_GEMSDOE32_B2_model_fit=b2_pred,
        delta_vs_champion=pred - b2_pred,
        evidence_class="PROJECTED — not a score, not a measurement",
        model="OLS of user-reported score on [log(dots), fraction of dots > 15 px from the catalogue]",
        coefficients=dict(intercept=float(beta[0]), log_dots=float(beta[1]),
                          far_fraction=float(beta[2])),
        n_observations=len(sites),
        loo_rmse=float(np.sqrt(np.mean(resid ** 2))),
        loo_interval=[pred - 1.96 * float(np.sqrt(np.mean(resid ** 2))),
                      pred + 1.96 * float(np.sqrt(np.mean(resid ** 2)))],
        projected_value=pred,
        candidate_position=dict(log_dots=float(np.log(cand["dots"])),
                                far_fraction=cand["d_cat_gt_15px_frac"]),
        observed_range=dict(dots=[min(r["dots"] for r in rows.values()),
                                  max(r["dots"] for r in rows.values())],
                            far_fraction=[min(r["d_cat_gt_15px_frac"] for r in rows.values()),
                                          max(r["d_cat_gt_15px_frac"] for r in rows.values())]),
        caveats=["the bootstrap interval covers parameter uncertainty only; model-form "
                 "uncertainty (does geometry determine score at all?) is not represented and is "
                 "larger — treat 0.24-0.31 as the defensible working range",
                 "n = 9, associational, and the candidate lies outside the observed range of "
                 "both predictors (lower dots, similar far-fraction) — it is an extrapolation",
                 "the model cannot see surface quality, only geometry; a surface that targets "
                 "the wrong terrain would score lower than the projection",
                 "the two predictors are strongly collinear across the nine files, so the "
                 "individual coefficients are not interpretable"],
    )


def main(tif: Path) -> dict:
    fp = D.footprint()
    cat = D.catalogue()
    pins = D.verify_inputs()
    fmt = validate.validate(tif, fp, cat)
    with rasterio.open(tif) as ds:
        a = ds.read(1).astype(np.float32)
    cand = covariates(a, fp, cat)

    rows = {s: covariates(load(s), fp, cat) for s in FILES}
    pairs = []
    for s in FILES:
        b = load(s)
        rho = float(spearmanr(a[fp], b[fp]).statistic)
        ov = dot_overlap(a * fp, b * fp)
        pairs.append(dict(registry=s, spearman_full_footprint=round(rho, 6),
                          my_dots_within_3px_of_theirs=round(ov, 6),
                          duplicate_by_rho=bool(abs(rho) > RHO_LIMIT),
                          duplicate_by_overlap=bool(ov > OVERLAP_LIMIT)))

    # chance calibration: matched-count uniform dots vs each registry raster
    rng = np.random.default_rng(20261031)
    idx = np.flatnonzero(fp.ravel())
    chance = {}
    for s in FILES:
        vals = []
        for _ in range(3):
            r = np.zeros(fp.size, bool)
            r[rng.choice(idx, size=cand["dots"], replace=False)] = True
            chance[s] = chance.get(s, [])
            chance[s].append(dot_overlap(r.reshape(fp.shape), load(s)))
        chance[s] = dict(mean=round(float(np.mean(chance[s])), 4),
                         max=round(float(np.max(chance[s])), 4))
    for p in pairs:
        base = chance[p["registry"]]["mean"]
        p["chance_overlap"] = base
        p["enrichment_vs_chance"] = round(p["my_dots_within_3px_of_theirs"] / base, 3) if base else None

    # reference: how much the nine files overlap *each other* (the saturation finding)
    nine_overlap = []
    for i, s1 in enumerate(FILES):
        for s2 in list(FILES)[i + 1:]:
            nine_overlap.append(dot_overlap(load(s1) * fp, load(s2) * fp))
    nine_overlap = np.array(nine_overlap)

    uniqueness = dict(
        rho_limit=RHO_LIMIT, overlap_limit=OVERLAP_LIMIT,
        pairs=pairs,
        max_abs_spearman=max(abs(p["spearman_full_footprint"]) for p in pairs),
        max_dot_overlap=max(p["my_dots_within_3px_of_theirs"] for p in pairs),
        passes_rho_rule=bool(max(abs(p["spearman_full_footprint"]) for p in pairs) <= RHO_LIMIT),
        passes_overlap_rule=bool(max(p["my_dots_within_3px_of_theirs"] for p in pairs) <= OVERLAP_LIMIT),
        chance_overlap_by_registry=chance,
        nine_file_mutual_overlap=dict(
            n_pairs=int(nine_overlap.size), min=round(float(nine_overlap.min()), 4),
            max=round(float(nine_overlap.max()), 4),
            median=round(float(np.median(nine_overlap)), 4),
            note=("All 36 pairs among the nine focus rasters already exceed the literal 70 % "
                  "3-px rule. On this terrain, 3-px overlap is not a discriminator of copying: "
                  "the candidate's value is therefore also reported against its chance level.")),
        evidence_class="REGISTRY-MEASUREMENT",
    )

    proj = projection(cand, rows)
    fmt_ok = bool(fmt["all_checks_passed"])
    ok = fmt_ok and uniqueness["passes_rho_rule"] and uniqueness["passes_overlap_rule"] \
        and cand["d_cat_le_2px_frac"] == 0.0
    decision = dict(
        ok_to_submit=bool(ok),
        basis=["saved-byte format preflight passed", "literal uniqueness rules passed",
               "no positive mass inside the mapped-catalogue corridor"],
        not_basis=["no organizer receipt for this file", "no validated leaderboard estimate",
                   "the holdout instrument is anti-correlated with the known leaderboard "
                   "ordering (see evidence/kp1_exp2_holdout.json instrument_calibration)"],
        slots_used=0,
    )
    out = dict(gate="kp1-release-gate/v1", tif=str(tif.relative_to(ROOT)) if tif.is_relative_to(ROOT) else str(tif),
               sha256=fmt["sha256"], bytes=fmt["bytes"], pins=pins,
               format=fmt, candidate_covariates=cand,
               registry_covariates={s: rows[s] for s in rows},
               uniqueness=uniqueness, projection=proj, decision=decision)
    path = D.write_report("kp1_release_gate.json", out)
    print(json.dumps({k: out[k] for k in ("sha256", "candidate_covariates", "projection", "decision")},
                     indent=1))
    print("uniqueness: max|rho|", uniqueness["max_abs_spearman"],
          "max overlap", uniqueness["max_dot_overlap"],
          "| nine-file mutual median", uniqueness["nine_file_mutual_overlap"]["median"])
    print("wrote", path)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("tif", nargs="?", default=str(ROOT / "docs" / "downloads" /
                                                  "karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif"))
    a = ap.parse_args()
    res = main(Path(a.tif))
    raise SystemExit(0 if res["decision"]["ok_to_submit"] else 1)
