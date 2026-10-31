#!/usr/bin/env python3
"""Experiment 2 of session 2026-10-31: H-V31 visible-only gradient discriminator.

Implements the design in knowledge/preregistration-h31-visgrad-20261031.md.

Modes
  holdout  spatially blocked hide-and-recover on catalogue segments, four quadrant folds,
           10 px buffer, leakage canary, controls C1/C2/C3, pooled HOLDOUT-DTI with CI.
           Writes evidence/h31_holdout_20261031.json. Writes no GeoTIFF.
  final    trains on ALL catalogue pixels (no withholding), emits 40,000 3-px-spaced dots,
           writes a single-band float32 GeoTIFF on the sample grid, validates it, runs the
           uniqueness check against the nine focus rasters and the 13GEMS lattice probe.
           Writes docs/downloads/<name>.tif and evidence/h31_final_20261031.json.

Labels: every score is HOLDOUT-DTI (evaluator gems57-pooled-hide-v2). Nothing here is an
organizer-confirmed score. The catalogue used as truth is the mirror labels.tif, not the
organizer's hidden labels.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from scipy import ndimage
from sklearn.metrics import roc_auc_score
import lightgbm as lgb

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57 import evaluate_holdout as eh  # noqa: E402  (vendored, unchanged)
from gems57 import metric as gmetric  # noqa: E402  (vendored, unchanged)

SEED = 20261031
BUFFER_PX = 10          # 1 km at 100 m
SPACING_PX = 3.0        # kernel radius, 300 m
N_TOTAL = 40000
NEG_SAMPLE = 200000
BLOCK_SIDE = 200        # 20 km spatial clusters for the bootstrap
CANARY_AUC_LIMIT = 0.90
DATA = ROOT / "data"
NAME = "karage1-h31-visgrad-nms3px-40k-20261031-zeros"
RAW_BAND_NODATA = -3.4028234663852886e38
TMI_HG_INDEX = 2        # band 3 (tmi_hg), zero-based index

_DISK = [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9]
DISK_Y = np.array([d[0] for d in _DISK])
DISK_X = np.array([d[1] for d in _DISK])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_inputs():
    with rasterio.open(DATA / "sample_submission.tif") as s:
        footprint = np.isfinite(s.read(1))
        grid = dict(crs=s.crs, transform=s.transform, width=s.width, height=s.height)
    with rasterio.open(DATA / "labels.tif") as s:
        catalogue = s.read(1) == 1
    with rasterio.open(DATA / "training_features.tif") as s:
        feats = s.read().astype(np.float32)  # (19, H, W)
    feats[feats <= RAW_BAND_NODATA * 0.999] = np.nan
    feats[:, ~footprint] = np.nan
    all_finite = np.isfinite(feats).all(axis=0)
    emit_ok = footprint & all_finite          # emission only where every channel is valid
    return footprint, catalogue, feats, emit_ok, grid


def nms_select(order_y: np.ndarray, order_x: np.ndarray, n_target: int, shape) -> tuple[np.ndarray, np.ndarray]:
    """Greedy: accept cells in priority order, block every cell within SPACING_PX of an accepted dot."""
    blocked = np.zeros(shape, bool)
    ys, xs = [], []
    h, w = shape
    for y, x in zip(order_y.tolist(), order_x.tolist()):
        if blocked[y, x]:
            continue
        ys.append(y)
        xs.append(x)
        by, bx = y + DISK_Y, x + DISK_X
        ok = (by >= 0) & (by < h) & (bx >= 0) & (bx < w)
        blocked[by[ok], bx[ok]] = True
        if len(ys) >= n_target:
            break
    return np.array(ys, np.int64), np.array(xs, np.int64)


def near(mask: np.ndarray, radius: float) -> np.ndarray:
    """True where a cell lies within `radius` px of a True cell in `mask` (Euclidean)."""
    if not mask.any():
        return np.zeros(mask.shape, bool)
    return ndimage.distance_transform_edt(~mask) <= radius


def dots_to_array(ys, xs, shape) -> np.ndarray:
    out = np.zeros(shape, np.float64)
    out[ys, xs] = 1.0
    return out


def fit_model(feats, pos_mask, neg_mask, rng):
    neg_idx = np.flatnonzero(neg_mask)
    if neg_idx.size > NEG_SAMPLE:
        neg_idx = rng.choice(neg_idx, NEG_SAMPLE, replace=False)
    pos_idx = np.flatnonzero(pos_mask)
    idx = np.concatenate([pos_idx, neg_idx])
    y = np.concatenate([np.ones(pos_idx.size), np.zeros(neg_idx.size)])
    X = feats.reshape(feats.shape[0], -1)[:, idx].T
    model = lgb.LGBMClassifier(
        n_estimators=300, learning_rate=0.05, num_leaves=63, subsample=0.8, subsample_freq=1,
        colsample_bytree=0.8, random_state=SEED, n_jobs=4, verbose=-1,
    )
    model.fit(X, y)
    return model


def predict_map(model, feats, shape) -> np.ndarray:
    flat = feats.reshape(feats.shape[0], -1).T
    ok = np.isfinite(flat).all(axis=1)
    p = np.zeros(flat.shape[0], np.float64)
    p[ok] = model.predict_proba(flat[ok])[:, 1]
    return p.reshape(shape)


def canary(feats, truth, background_mask):
    """Single-channel AUC on the withheld truth against background. Symmetric: max(AUC, 1-AUC)."""
    rows = []
    t_idx = np.flatnonzero(truth)
    b_idx = np.flatnonzero(background_mask)
    rng = np.random.default_rng(SEED)
    if b_idx.size > 60000:
        b_idx = rng.choice(b_idx, 60000, replace=False)
    for band in range(feats.shape[0]):
        flat = feats[band].ravel()
        tv, bv = flat[t_idx], flat[b_idx]
        tv, bv = tv[np.isfinite(tv)], bv[np.isfinite(bv)]
        if tv.size < 50 or bv.size < 50:
            rows.append(dict(band=band + 1, auc=None, symmetric_auc=None, n_truth=int(tv.size)))
            continue
        y = np.concatenate([np.ones(tv.size), np.zeros(bv.size)])
        s = np.concatenate([tv, bv]).astype(np.float64)
        auc = float(roc_auc_score(y, s))
        rows.append(dict(band=band + 1, auc=round(auc, 4), symmetric_auc=round(max(auc, 1 - auc), 4), n_truth=int(tv.size)))
    return rows


def run_holdout() -> dict:
    footprint, catalogue, feats, emit_ok, grid = load_inputs()
    H, W = footprint.shape
    rng = np.random.default_rng(SEED)

    # Four quadrant folds from footprint medians; segments assigned by centroid.
    rows, cols = np.nonzero(footprint)
    row_mid, col_mid = np.median(rows), np.median(cols)
    quad = np.zeros((H, W), np.int64)
    rr, cc = np.indices((H, W))
    quad = 2 * (rr >= row_mid).astype(np.int64) + (cc >= col_mid).astype(np.int64)

    seg_lab, n_seg = ndimage.label(catalogue, structure=np.ones((3, 3)))
    centroids = ndimage.center_of_mass(catalogue, seg_lab, range(1, n_seg + 1))
    seg_quad = np.array([quad[int(round(cy)), int(round(cx))] for cy, cx in centroids])
    sizes = np.bincount(seg_lab.ravel())[1:]

    fp_total = int(footprint.sum())
    cat_near_all_neg = ~near(catalogue, BUFFER_PX)   # far from every catalogue pixel

    arms = {"candidate_H_V31": [], "C1_random": [], "C2_tmi_hg_top": [], "C3_catalogue_proximity": []}
    fold_rows = []
    canary_rows = []
    truth_counts = []
    for k in range(4):
        in_k = quad == k
        withheld_seg_ids = np.flatnonzero(seg_quad == k) + 1
        withheld = np.isin(seg_lab, withheld_seg_ids)          # all withheld catalogue pixels
        visible = catalogue & ~withheld
        truth_in_region = withheld & in_k & footprint
        if not truth_in_region.any():
            raise SystemExit(f"fold {k} has no withheld truth in its region; check segment assignment")

        # Training positives: visible pixels, excluding those within the buffer of withheld truth.
        near_withheld = near(withheld, BUFFER_PX)
        pos = visible & ~near_withheld
        neg = footprint & cat_near_all_neg & ~near_withheld
        model = fit_model(feats, pos, neg, rng)

        p_map = predict_map(model, feats, (H, W))
        region_emit = in_k & emit_ok & ~visible       # visible catalogue pixels are masked anyway
        n_k = int(round(N_TOTAL * int((in_k & footprint).sum()) / fp_total))

        # Candidate: top-N by model probability.
        cand_y, cand_x = np.nonzero(region_emit)
        order = np.argsort(-p_map[cand_y, cand_x], kind="stable")
        ys, xs = nms_select(cand_y[order], cand_x[order], n_k, (H, W))
        arms["candidate_H_V31"].append((ys, xs))

        # C1: uniform random cells in the region (footprint, not visible catalogue).
        c1_cand = np.flatnonzero((in_k & footprint & ~visible).ravel())
        c1_perm = rng.permutation(c1_cand)
        ys1, xs1 = nms_select(c1_perm // W, c1_perm % W, n_k, (H, W))
        arms["C1_random"].append((ys1, xs1))

        # C2: top-N by tmi_hg (band 3) alone, no model.
        tmi = feats[TMI_HG_INDEX]
        c2_cand = np.flatnonzero((in_k & footprint & ~visible & np.isfinite(tmi)).ravel())
        c2_order = c2_cand[np.argsort(-tmi.ravel()[c2_cand], kind="stable")]
        ys2, xs2 = nms_select(c2_order // W, c2_order % W, n_k, (H, W))
        arms["C2_tmi_hg_top"].append((ys2, xs2))

        # C3: random cells 1-2 px from visible catalogue (the B2-style rule without withheld information).
        d_vis = ndimage.distance_transform_edt(~visible) if visible.any() else np.full((H, W), np.inf)
        c3_cand = np.flatnonzero((in_k & footprint & (d_vis > 0) & (d_vis <= 2.0)).ravel())
        c3_perm = rng.permutation(c3_cand)
        ys3, xs3 = nms_select(c3_perm // W, c3_perm % W, n_k, (H, W))
        arms["C3_catalogue_proximity"].append((ys3, xs3))

        # Leakage canary, per channel, on this fold's withheld truth vs background in its region.
        background = in_k & footprint & cat_near_all_neg
        canary_rows.append({"fold": k, "channels": canary(feats, truth_in_region, background)})

        # Scoring for each arm in this fold. Dots are restricted to the fold region by the evaluator.
        fold = dict(region=in_k & footprint, masked_known=visible, visible=visible, truth=withheld)
        row = {"fold": k, "withheld_segments": int(withheld_seg_ids.size),
               "withheld_positive_pixels_in_region": int(truth_in_region.sum()),
               "visible_catalogue_pixels": int(visible.sum()), "n_per_arm_target": n_k, "arms": {}}
        for arm, (ys_a, xs_a) in ((a, arms[a][-1]) for a in arms):
            pred = dots_to_array(ys_a, xs_a, (H, W))
            res, terms = eh.evaluate(pred, fold, footprint, block_side=BLOCK_SIDE,
                                     origin=(0, 0), global_shape=(H, W))
            arms[arm][-1] = (ys_a, xs_a, terms)
            row["arms"][arm] = {"dots": int(ys_a.size), "dti": round(float(res["dti"]), 6),
                                "tpw": round(float(res["tp"]), 3), "fpw": round(float(res["fp"]), 3),
                                "fnw": round(float(res["fn"]), 3), "n_truth": int(res["n_truth"])}
        fold_rows.append(row)
        truth_counts.append(truth_in_region.sum())

    # Pool per-block terms across folds (regions are disjoint, blocks are global-aligned).
    terms_by_arm = {}
    for arm in arms:
        acc = None
        for ys_a, xs_a, terms in arms[arm]:
            acc = terms if acc is None else acc + terms
        terms_by_arm[arm] = acc

    summary = eh.pooled_summary(terms_by_arm, draws=1000, seed=SEED, candidate="candidate_H_V31")

    canary_max = {}
    for fold_entry in canary_rows:
        for ch in fold_entry["channels"]:
            if ch["symmetric_auc"] is None:
                continue
            key = ch["band"]
            canary_max[key] = max(canary_max.get(key, 0.0), ch["symmetric_auc"])
    leak = {b: a for b, a in canary_max.items() if a > CANARY_AUC_LIMIT}

    cand = summary["scores"]["candidate_H_V31"]["dti"]
    diffs = summary["paired_differences"]
    c1, c2 = diffs["C1_random"], diffs["C2_tmi_hg_top"]
    promote_test = (cand > summary["scores"]["C1_random"]["dti"] and c1["ci95"][0] > 0
                    and cand > summary["scores"]["C2_tmi_hg_top"]["dti"] and c2["ci95"][0] > 0)
    verdict = "NEGATIVE" if (leak or not promote_test) else "PASS_HOLDOUT_ONLY"

    return {
        "schema": "karage1-h31-holdout-v1",
        "date_utc": "2026-10-31",
        "evidence_class": "HOLDOUT-DTI",
        "evaluator_version": eh.VERSION,
        "truth_source": "data/labels.tif (mirror catalogue; NOT organizer hidden labels)",
        "preregistration": "knowledge/preregistration-h31-visgrad-20261031.md",
        "folds": fold_rows,
        "pooled": summary,
        "leakage_canary": {"per_fold": canary_rows, "max_symmetric_auc_per_channel": canary_max,
                           "limit": CANARY_AUC_LIMIT, "channels_over_limit": leak},
        "verdict_holdout_only": verdict,
        "verdict_note": ("Holdout-only result. The uniqueness gate is evaluated in the final mode; "
                         "the lattice gate is reported there and is not waived."),
        "config": {"seed": SEED, "buffer_px": BUFFER_PX, "spacing_px": SPACING_PX, "n_total": N_TOTAL,
                   "neg_sample": NEG_SAMPLE, "block_side_px": BLOCK_SIDE, "grid": {"crs": str(grid["crs"]),
                   "width": grid["width"], "height": grid["height"]}},
    }


def run_final() -> dict:
    footprint, catalogue, feats, emit_ok, grid = load_inputs()
    H, W = footprint.shape
    rng = np.random.default_rng(SEED)
    near_cat = near(catalogue, BUFFER_PX)
    pos = catalogue.copy()
    neg = footprint & ~near_cat
    model = fit_model(feats, pos, neg, rng)
    p_map = predict_map(model, feats, (H, W))
    emit = emit_ok & ~catalogue
    cy, cx = np.nonzero(emit)
    order = np.argsort(-p_map[cy, cx], kind="stable")
    ys, xs = nms_select(cy[order], cx[order], N_TOTAL, (H, W))
    raster = dots_to_array(ys, xs, (H, W)).astype(np.float32)
    raster[~footprint] = 0.0

    out_dir = ROOT / "docs" / "downloads"
    out_dir.mkdir(parents=True, exist_ok=True)
    tif = out_dir / f"{NAME}.tif"
    profile = dict(driver="GTiff", height=H, width=W, count=1, dtype="float32", crs=grid["crs"],
                   transform=grid["transform"], compress="deflate", nodata=None)
    with rasterio.open(tif, "w", **profile) as dst:
        dst.write(raster, 1)

    # Validate the saved bytes, not the in-memory array.
    with rasterio.open(tif) as src:
        back = src.read(1)
        valid = {
            "crs_match": str(src.crs) == str(grid["crs"]),
            "shape_match": (src.height, src.width) == (H, W),
            "transform_match": tuple(src.transform)[:6] == tuple(grid["transform"])[:6],
            "dtype": src.dtypes[0],
            "count": src.count,
            "nan_cells": int(np.isnan(back).sum()),
            "min": float(back.min()), "max": float(back.max()),
            "in_0_1": bool(np.isfinite(back).all() and back.min() >= 0.0 and back.max() <= 1.0),
            "dots": int((back == 1).sum()),
            "dots_outside_footprint": int(((back != 0) & ~footprint).sum()),
            "dots_on_catalogue": int(((back == 1) & catalogue).sum()),
        }
    valid["pass"] = bool(valid["crs_match"] and valid["shape_match"] and valid["transform_match"]
                         and valid["nan_cells"] == 0 and valid["in_0_1"] and valid["dots_outside_footprint"] == 0)

    # Uniqueness gate against the nine focus rasters and the 13GEMS lattice probe.
    from scipy.stats import rankdata
    surf_rank = rankdata(p_map[footprint]).astype(np.float64)
    dots = back == 1
    comparisons = {}
    names = []
    for path in sorted(glob.glob(str(ROOT / "registry" / "GEMSDOE*.tif"))) + sorted(
            glob.glob(str(ROOT / "data" / "scored" / "13gems_*nan-outside.tif"))):
        with rasterio.open(path) as s:
            arr = s.read(1)
        other = arr == 1
        name = Path(path).name
        names.append(name)
        fwd = None
        if dots.sum():
            dist_other = ndimage.distance_transform_edt(~other) if other.any() else np.full((H, W), np.inf)
            fwd = float((dist_other[dots] <= SPACING_PX).mean())
        ph = None
        fp = footprint
        x, y = dots[fp].astype(float), other[fp].astype(float)
        if x.std() > 0 and y.std() > 0:
            ph = float(np.corrcoef(x, y)[0, 1])
        # Surface check (protocol: before placement). Spearman(surface, binary registry raster)
        # equals Pearson(rank(surface), indicator) because the rank map of a binary variable is affine.
        yb = other[fp].astype(float)
        surf_rho = float(np.corrcoef(surf_rank, yb)[0, 1]) if yb.std() > 0 else None
        comparisons[name] = {"exact_positive_mask_equal": bool(np.array_equal(dots, other)),
                             "fwd3_candidate_dots_within_3px_of_registry": round(fwd, 6) if fwd is not None else None,
                             "phi_spearman_footprint": round(ph, 6) if ph is not None else None,
                             "registry_dots": int(other.sum()),
                             "surface_spearman_vs_registry_raster": round(surf_rho, 6) if surf_rho is not None else None}
    is_lattice = {k: v for k, v in comparisons.items() if k.startswith("13gems")}
    focus = {k: v for k, v in comparisons.items() if not k.startswith("13gems")}
    unique_vs_focus = all((not v["exact_positive_mask_equal"]) and v["fwd3_candidate_dots_within_3px_of_registry"] < 0.70
                          and abs(v["phi_spearman_footprint"]) < 0.90 for v in focus.values())
    lattice_ok = all(v["fwd3_candidate_dots_within_3px_of_registry"] < 0.70 for v in is_lattice.values())
    surface_ok = all(abs(v["surface_spearman_vs_registry_raster"]) < 0.90 for v in comparisons.values())

    digest = sha256(tif)
    import zipfile
    zip_path = out_dir / f"{NAME}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(tif, arcname=tif.name)
    zip_digest = sha256(zip_path)
    (out_dir / f"{NAME}.sha256").write_text(f"{digest}  {tif.name}\n")

    gate_status = ("PASS" if (valid["pass"] and unique_vs_focus and lattice_ok and surface_ok) else
                   "NOT CLEARED")
    return {
        "schema": "karage1-h31-final-candidate-v1",
        "date_utc": "2026-10-31",
        "file": f"docs/downloads/{tif.name}",
        "zip": f"docs/downloads/{zip_path.name}",
        "sha256_tif": digest,
        "sha256_zip": zip_digest,
        "bytes_tif": tif.stat().st_size,
        "dots_requested": N_TOTAL,
        "dots_written": valid["dots"],
        "validator": valid,
        "uniqueness_vs_nine_focus": comparisons,
        "unique_vs_nine_focus_passes": unique_vs_focus,
        "lattice_gate_passes": lattice_ok,
        "surface_gate_passes_all_registry": surface_ok,
        "lattice_gate_note": "13GEMS covering probe; every dotted focus raster exceeds 0.70 forward overlap (see evidence/focus_nine_audit_20261031.json).",
        "holdout_label": "HOLDOUT-DTI only via evidence/h31_holdout_20261031.json; no organizer score",
        "gate_status": gate_status,
        "submission_status": ("DO NOT SUBMIT: NOT CLEARED. Fails the lattice gate (by construction for any dotted raster); "
                              "owner must resolve the gate before any selector step. No leaderboard estimate exists."),
    }


def main() -> int:
    global BUFFER_PX
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["holdout", "final"])
    ap.add_argument("--buffer-px", type=int, default=BUFFER_PX,
                    help="holdout buffer; default is the preregistered 10 px. Other values are post-hoc sensitivity runs.")
    ap.add_argument("--tag", default="", help="suffix for the output file of a sensitivity run")
    args = ap.parse_args()
    BUFFER_PX = args.buffer_px
    if args.mode == "holdout":
        report = run_holdout()
        report["sensitivity"] = {"post_hoc": BUFFER_PX != 10, "buffer_px": BUFFER_PX,
                                 "note": "Post-hoc sensitivity; does not change the preregistered verdict."}
        out = ROOT / "evidence" / ("h31_holdout_20261031" + (f"_{args.tag}" if args.tag else "") + ".json")
    else:
        report = run_final()
        out = ROOT / "evidence" / "h31_final_20261031.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
