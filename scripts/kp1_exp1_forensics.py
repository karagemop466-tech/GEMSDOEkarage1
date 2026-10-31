#!/usr/bin/env python3
"""EXP1 — forensic accounting of the nine focus-site rasters (lane H-KP1).

What this script answers, and what it does **not**
-------------------------------------------------
It answers: given the *published* DTI formula, the pinned catalogue and the nine
pinned registry rasters, what geometric quantities separate the file that scored
0.2778 from the files that scored 0.2449-0.2710, and what does that imply about
where a submission must put its probability mass?

It does **not** estimate any leaderboard score. The scored truth is the
organizer's private set of expert-identified new faults; it is not in this
repository and cannot be reconstructed from the catalogue. Every number written
here is labelled ``REGISTRY-MEASUREMENT`` (a property of the bytes) or
``CATALOGUE-REFERENCE`` (DTI computed with the *mapped catalogue* standing in as
truth — a control, never a score).

Metric identity used throughout (alpha = 0.2, beta = 0.8, and beta = 1 - alpha):

    FN_w = |G| - TP_w
    DTI  = TP_w / (TP_w + a*FP_w + b*FN_w) = TP_w / (a*(TP_w + FP_w) + b*|G|)

so DTI is a function of exactly three quantities: TP_w, FP_w and |G|.  For a
binary dot field with ``n`` dots and self-credit ``M = sum_x max_g k(d)``,
``FP_w = n - M``.  See ``vendor/gems57/metric.py`` and the organizer page
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/

Outputs: ``evidence/kp1_exp1_forensics.json``.
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

from gems57.metric import ALPHA, BETA, kernel                      # noqa: E402
from gems57.uniqueness import dot_overlap                          # noqa: E402
from scripts import kp1_data as D                                  # noqa: E402

REGISTRY = ROOT / "registry"
SCORES = {                       # USER-REPORTED / UNVERIFIED, from the prompt ledger
    "GEMSDOE24": 0.2477,
    "GEMSDOE25": 0.2600,
    "GEMSDOE27": 0.2449,
    "GEMSDOE28": 0.2710,
    "GEMSDOE30": 0.2600,
    "GEMSDOE31": 0.2708,
    "GEMSDOE32": 0.2778,
    "GEMSDOE33": 0.2632,
    "GEMSDOE36": 0.2750,
}
FILES = {
    "GEMSDOE24": "GEMSDOE24_gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
    "GEMSDOE25": "GEMSDOE25_d28.tif",
    "GEMSDOE27": "GEMSDOE27_gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
    "GEMSDOE28": "GEMSDOE28_gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif",
    "GEMSDOE30": "GEMSDOE30_gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
    "GEMSDOE31": "GEMSDOE31_gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
    "GEMSDOE32": "GEMSDOE32_B2.tif",
    "GEMSDOE33": "GEMSDOE33_GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
    "GEMSDOE36": "GEMSDOE36_gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
}


def load(name: str) -> np.ndarray:
    with rasterio.open(REGISTRY / FILES[name]) as ds:
        a = ds.read(1).astype(np.float32)
    a[~np.isfinite(a)] = 0.0
    return a


def disc(radius: float) -> np.ndarray:
    r = int(np.ceil(radius))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return (yy * yy + xx * xx) <= radius * radius


def dti_components(pred_binary: np.ndarray, truth: np.ndarray) -> dict:
    """Exact TP_w, FP_w, FN_w for a binary dot field under truth (vectorised)."""
    truth = np.asarray(truth, bool)
    dots = np.asarray(pred_binary, bool) & ~truth
    d = ndi.distance_transform_edt(~truth)
    k_dot = float((1.0 - np.minimum(d[dots] / 3.0, 1.0)).sum())       # M
    n = int(dots.sum())
    fp = float(n - k_dot)
    # TP_w: per truth cell, the best kernel credit among neighbouring dots.
    gy, gx = np.nonzero(truth)
    credit = np.zeros(gy.size, np.float64)
    H, W = truth.shape
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            k = float(max(1.0 - np.hypot(dy, dx) / 3.0, 0.0))
            if k <= 0.0:
                continue
            ny, nx = gy + dy, gx + dx
            ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
            hit = np.zeros(gy.size, bool)
            hit[ok] = dots[ny[ok], nx[ok]]
            np.maximum(credit, np.where(hit, k, 0.0), out=credit)
    tp = float(credit.sum())
    return dict(tpw=tp, fpw=fp, fnw=float(gy.size) - tp, n_truth=int(gy.size),
                n_dots=n, self_credit_M=k_dot,
                dti=tp / (tp + ALPHA * fp + BETA * (gy.size - tp) + 1e-12))


def main() -> None:
    pins = D.verify_inputs()
    fp = D.footprint()
    cat = D.catalogue()
    proxy = D.proxy_truth()
    proxy_detached = D.proxy_truth(min_gap_px=4)
    d_cat = ndi.distance_transform_edt(~cat)

    nbr3 = disc(3)
    dens = {k: ndi.convolve(v.astype(np.float32), np.ones((5, 5), np.float32), mode="constant")
            for k, v in ()}

    rows = {}
    masks = {}
    for site in FILES:
        a = load(site)
        m = (a > 0) & fp
        masks[site] = m
        n = int(m.sum())
        nb = ndi.convolve(m.astype(np.int16), nbr3.astype(np.int16), mode="constant") - m
        dd = d_cat[m]
        cov = ndi.binary_dilation(m, structure=nbr3)
        rows[site] = dict(
            file=FILES[site],
            sha256=D.sha256(REGISTRY / FILES[site]),
            user_reported_score=SCORES[site],
            score_class="USER-REPORTED / UNVERIFIED",
            dots=n,
            dot_fraction_of_footprint=round(n / int(fp.sum()), 6),
            total_mass=round(float(a[fp].sum()), 1),
            distinct_values=[float(v) for v in np.unique(a[fp])][:5],
            d_cat_le_2px_frac=round(float((dd <= 2).mean()), 5),
            d_cat_2_to_15px_frac=round(float(((dd > 2) & (dd <= 15)).mean()), 5),
            d_cat_gt_15px_frac=round(float((dd > 15).mean()), 5),
            median_d_cat_px=round(float(np.median(dd)), 3),
            clump_ge3_nbr_within_3px_frac=round(float((nb >= 3).mean()), 5),
            mean_nbr_within_3px=round(float(nb.mean()), 4),
            footprint_kernel_coverage=round(float(cov[fp].mean()), 6),
            dots_in_lidar_gap=round(float(1.0 - ndi.binary_dilation(
                D.lidar_band("valid") > 0, structure=nbr3)[m].mean()), 5),
            catalogue_reference_dti=dti_components(m, cat),
            proxy_reference_dti=dti_components(m, proxy),
            proxy_detached_reference_dti=dti_components(m, proxy_detached),
        )
        print(f"[exp1] {site}: dots={n} d_cat<=2={rows[site]['d_cat_le_2px_frac']:.4f} "
              f">15={rows[site]['d_cat_gt_15px_frac']:.4f} score={SCORES[site]}", flush=True)

    # ---- pairwise duplication: literal rank rule and literal 3-px rule --------
    sites = list(FILES)
    vals = {s: load(s) for s in sites}
    pairs = []
    rng = np.random.default_rng(20261031)
    for i, a in enumerate(sites):
        for b in sites[i + 1:]:
            rho = float(spearmanr(vals[a][fp], vals[b][fp]).statistic)
            ov_ab = dot_overlap(vals[a] * fp, vals[b] * fp)
            ov_ba = dot_overlap(vals[b] * fp, vals[a] * fp)
            pairs.append(dict(a=a, b=b, spearman_full_footprint=round(rho, 4),
                              overlap_a_dots_near_b=round(ov_ab, 4),
                              overlap_b_dots_near_a=round(ov_ba, 4),
                              max_overlap=round(max(ov_ab, ov_ba), 4)))

    # ---- null calibration: how much 3-px overlap is expected by chance? ------
    null = {}
    for site in sites:
        n = int(masks[site].sum())
        cand_idx = np.flatnonzero(fp.ravel())
        obs = []
        for _ in range(3):
            pick = rng.choice(cand_idx, size=n, replace=False)
            r = np.zeros(fp.size, bool)
            r[pick] = True
            r = r.reshape(fp.shape)
            obs.append(dot_overlap(r, masks[site]))
        null[site] = dict(mean=round(float(np.mean(obs)), 4),
                          max=round(float(np.max(obs)), 4), draws=len(obs))
    pair_null = []
    for p in pairs:
        obs = p["overlap_a_dots_near_b"]
        base = null[p["b"]]["mean"]
        pair_null.append(dict(a=p["a"], b=p["b"], observed=obs, chance=base,
                              enrichment=round(obs / base, 3) if base else None))
    for p, q in zip(pairs, pair_null):
        p["chance_overlap"] = q["chance"]
        p["enrichment_vs_chance"] = q["enrichment"]
        p["duplicate_by_literal_rule"] = bool(
            p["spearman_full_footprint"] > 0.90 or p["max_overlap"] > 0.70)

    # ---- does the observed score track distance-from-catalogue? --------------
    sc = np.array([SCORES[s] for s in sites])
    def rho_vs(key):
        x = np.array([rows[s][key] for s in sites], float)
        r = spearmanr(x, sc)
        # exact permutation p-value is cheap for n = 9
        perm = []
        rng2 = np.random.default_rng(7)
        for _ in range(20000):
            perm.append(abs(spearmanr(x, rng2.permutation(sc)).statistic))
        return dict(spearman=round(float(r.statistic), 4),
                    p_two_sided=round(float(np.mean(np.array(perm) >= abs(r.statistic))), 4),
                    n=len(sites))
    score_links = {k: rho_vs(k) for k in
                   ("d_cat_le_2px_frac", "d_cat_2_to_15px_frac", "d_cat_gt_15px_frac",
                    "median_d_cat_px", "dots", "clump_ge3_nbr_within_3px_frac",
                    "footprint_kernel_coverage", "dots_in_lidar_gap")}

    # ---- metric inversion: what hit fraction does 0.2778 imply? -------------
    # DTI = y_t*h*n / (a*(n + h*n*(y_t - y_m)) + b*|G|)
    #   h  = fraction of dots whose self-credit is ~1 (dot on/near a truth pixel)
    #   y_t= kernel-weighted truth pixels credited per such dot
    #   y_m= self-credit of such a dot
    inversion = {}
    b2 = rows["GEMSDOE32"]
    for y_t, y_m in ((2.0, 0.8), (3.0, 1.0)):
        curve = {}
        for G in (10000, 20000, 40000, 60988, 120000):
            n = b2["dots"]
            den0 = ALPHA * n + BETA * G
            h = b2["user_reported_score"] * den0 / (y_t * n - b2["user_reported_score"] * ALPHA * n * (y_t - y_m))
            curve[str(G)] = round(float(min(max(h, 0.0), 1.0)), 4)
        inversion[f"y_t={y_t},y_m={y_m}"] = dict(implied_hit_fraction_by_assumed_truth_size=curve)
    inversion_note = ("h is the fraction of the champion's 37,654 dots that would have to "
                      "land with self-credit ~1 (i.e. within ~1 px of an expert new-fault pixel) "
                      "to reproduce 0.2778 under the published formula. |G| (the private truth "
                      "size) is unknown, so h is a range, not a measurement; it is reported to "
                      "size the bar a new candidate must clear.")

    payload = dict(
        evidence_class="REGISTRY-MEASUREMENT",
        generated_utc="2026-10-31",
        lane="H-KP1 (K-PROXY-DETECT)",
        inputs=pins,
        footprint_pixels=int(fp.sum()),
        catalogue_pixels=int(cat.sum()),
        proxy_truth_pixels=int(proxy.sum()),
        proxy_truth_detached_pixels=int(proxy_detached.sum()),
        label_note=("labels.tif is byte-identical to existing_faults.tif (pin 7ba308cc…), so the "
                    "published 'labels' raster IS the mapped catalogue; the scored private truth is "
                    "not published (competition page 967)."),
        per_file=rows,
        pairs=pairs,
        chance_overlap_null=null,
        duplicate_rule=dict(rho_limit=0.90, overlap_limit=0.70,
                            note="literal parallel-run protocol rule 1"),
        score_covariate_association=score_links,
        metric_inversion=dict(model=inversion, note=inversion_note),
    )
    out = D.write_report("kp1_exp1_forensics.json", payload)
    print("wrote", out)
    print(json.dumps({k: v for k, v in score_links.items()}, indent=1))
    print(json.dumps(inversion, indent=1))


if __name__ == "__main__":
    main()
