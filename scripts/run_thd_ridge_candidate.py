#!/usr/bin/env python3
"""Label-free magnetic edge-ridge candidate, scored on the shared hide-and-recover holdout.

Method (pre-registered in evidence/thd_ridge_candidate_20261029.json before any run):
  1. Ridge score = ``tmi_hg`` band (total magnetic intensity horizontal gradient, from
     training_features.tif). Candidate pixels are 3x3 local maxima of that score in the
     footprint, at or above the footprint percentile ``pct`` (99.0 in arm A, 98.0 in arm B).
  2. Collar: candidates within ``RADIUS_PX`` (3 px = 300 m, the scoring kernel radius)
     of the *mapped* catalogue are removed. For holdout cells the collar uses only the
     visible catalogue of that fold (``HoldoutContext.visible``), never the withheld traces.
  3. Output is binary (1 on candidates, 0 elsewhere), float32, inside the footprint.

The ridge score itself uses no label. Labels enter only through the collar, the holdout
truth, and the canary. Arm selection is made on holdout DTI and is therefore OPTIMISTIC.

Scoring uses the shared template: ``gems57.holdout.build_holdout`` / ``score_cell``
(pooled DTI, alpha 0.2, beta 0.8, 3-px triangular kernel). Writing and validation use
``gems57.submission_writer`` / ``gems57.validate``. Uniqueness uses ``gems57.uniqueness``.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))

from gems57 import grid as G57  # noqa: E402
from gems57 import holdout as H57  # noqa: E402
from gems57 import metric as M57  # noqa: E402
from gems57 import submission_writer as W57  # noqa: E402
from gems57 import uniqueness as U57  # noqa: E402
from gems57.validate import validate  # noqa: E402

DATA = ROOT / "data"
SCORED = DATA / "scored"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
RUN_ID = "thd-ridge-collar-20261029"
SEED_BOOT = 520810
N_BOOT = 10_000
ARMS = {"A_pct99": 99.0, "B_pct98": 98.0}
CANARY_NEG = 300_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_inputs():
    with rasterio.open(DATA / "sample_submission.tif") as ds:
        footprint = np.isfinite(ds.read(1))
        crs = ds.crs
    with rasterio.open(DATA / "labels.tif") as ds:
        raw = ds.read(1)
    catalogue = np.isfinite(raw) & (raw > 0.5) & footprint
    with rasterio.open(DATA / "training_features.tif") as ds:
        names = [d.split(" - ")[0] for d in ds.descriptions]
        idx = names.index("tmi_hg") + 1
        tmi_hg = ds.read(idx).astype(np.float32)
        feat_names = names
    valid = footprint & np.isfinite(tmi_hg) & (tmi_hg > -1e30)
    grid = G57.Grid(footprint=footprint, catalogue=catalogue, crs=crs,
                    transform=G57.TRANSFORM, height=G57.HEIGHT, width=G57.WIDTH)
    return grid, tmi_hg, valid, feat_names


def ridge_candidates(score: np.ndarray, valid: np.ndarray, pct: float) -> np.ndarray:
    """3x3 local maxima of ``score`` on valid pixels, at/above the valid-footprint percentile."""
    filled = np.where(valid, score, -1e30).astype(np.float32)
    maxima = (ndi.maximum_filter(filled, size=3, mode="nearest") == filled) & valid
    thr = np.percentile(score[valid], pct)
    return maxima & (score >= thr)


def collar(cands: np.ndarray, known: np.ndarray) -> np.ndarray:
    """Remove candidates within RADIUS_PX of ``known`` traces (kernel-support collar)."""
    if not known.any():
        return cands
    dist = ndi.distance_transform_edt(~known)
    return cands & (dist > M57.RADIUS_PX)


def holdout_score(grid, tmi_hg, valid, pct):
    """Per-cell DTI for the arm, rebuilding candidates from visible faults per cell."""
    ctx = H57.build_holdout(grid)
    cands_raw = ridge_candidates(tmi_hg, valid & grid.footprint, pct)
    cells = []
    for cell in ctx.cells:
        vis = ctx.visible(cell.key)
        emitted = collar(cands_raw, vis)
        r = H57.score_cell(cell, emitted)
        cells.append(dict(key=cell.key, mode=cell.mode, fold=cell.fold, seed=cell.seed,
                          n_truth=r["n_truth"], n_emitted=r["n_emitted"], tp=r["tp"],
                          fp=r["fp"], fn=r["fn"], dti=r["dti"]))
    return ctx, cells


def pooled(cells, mode="all"):
    sel = [c for c in cells if c["mode"] == mode]
    tp = sum(c["tp"] for c in sel)
    fp = sum(c["fp"] for c in sel)
    fn = sum(c["fn"] for c in sel)
    n_truth = sum(c["n_truth"] for c in sel)
    dti = tp / (tp + M57.ALPHA * fp + M57.BETA * fn + M57.EPS) if (tp + fp + fn) > 0 else 0.0
    return dict(dti=float(dti), tp=tp, fp=fp, fn=fn, n_truth=int(n_truth), n_cells=len(sel))


def bootstrap_ci(cells, mode="all", draws=N_BOOT, seed=SEED_BOOT):
    """Percentile CI from resampling fold cells (whole cells, with replacement)."""
    sel = [c for c in cells if c["mode"] == mode]
    rng = np.random.default_rng(seed)
    tp = np.array([c["tp"] for c in sel])
    fp = np.array([c["fp"] for c in sel])
    fn = np.array([c["fn"] for c in sel])
    out = np.empty(draws)
    for i in range(draws):
        j = rng.integers(0, len(sel), len(sel))
        t, f, n = tp[j].sum(), fp[j].sum(), fn[j].sum()
        out[i] = t / (t + M57.ALPHA * f + M57.BETA * n + M57.EPS) if (t + f + n) > 0 else 0.0
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def leakage_canary(grid, ctx, feat_names, feat_path):
    """Single-feature AUC on holdout truth vs. background. AUC > 0.90 means leakage until proven otherwise."""
    rng = np.random.default_rng(7)
    report = []
    with rasterio.open(feat_path) as ds:
        for i, name in enumerate(feat_names, start=1):
            band = ds.read(i).astype(np.float64)
            ok = grid.footprint & np.isfinite(band) & (band > -1e30)
            aucs = []
            for cell in ctx.cells_of("all"):
                hid = ctx.hidden_by_cell[cell.key] & ok
                bg = grid.footprint & ~ctx.hidden_by_cell[cell.key] & ~grid.catalogue & ok
                pos_idx = np.flatnonzero(hid)
                bg_idx = np.flatnonzero(bg)
                if pos_idx.size < 10 or bg_idx.size < 10:
                    continue
                neg = rng.choice(bg_idx, size=min(CANARY_NEG, bg_idx.size), replace=False)
                y = np.r_[np.ones(pos_idx.size), np.zeros(neg.size)]
                x = np.r_[band.flat[pos_idx], band.flat[neg]]
                aucs.append(float(roc_auc_score(y, x)))
            auc = float(np.mean(aucs)) if aucs else None
            report.append(dict(feature=name, mean_auc_over_all_cells=auc,
                               direction_invariant_auc=None if auc is None else max(auc, 1 - auc),
                               passed=bool(auc is not None and max(auc, 1 - auc) <= 0.90)))
    return report


def registry_index(exclude: Path):
    """Every local registry raster EXCEPT the candidate itself (self-match would give a false duplicate)."""
    rasters = sorted(p for p in list(SCORED.glob("*.tif")) + list(DOWNLOADS.glob("*.tif"))
                     if p.resolve() != exclude.resolve())
    rows = []
    for p in rasters:
        rows.append(dict(repo_first="local-mirror", sources=[p.name], cache_file=str(p),
                         sha256=sha256(p)))
    return dict(rasters=rows, errors=[], expected_raster_count=len(rows),
                registry_rasters_expected=len(rows), complete_accessible_scan=False)


def main():
    grid, tmi_hg, valid, feat_names = load_inputs()
    fp = grid.footprint
    results = {}
    arms_out = {}
    for arm, pct in ARMS.items():
        ctx, cells = holdout_score(grid, tmi_hg, valid, pct)
        prim = pooled(cells, "all")
        sec = pooled(cells, "detached")
        lo, hi = bootstrap_ci(cells, "all")
        arms_out[arm] = dict(pct=pct, holdout_all=prim, holdout_detached=sec,
                             ci95_all=[lo, hi], cells=cells)
        print(arm, "pooled all DTI %.4f CI [%.4f, %.4f] n_truth %d" % (prim["dti"], lo, hi, prim["n_truth"]), flush=True)
        if arm == "A_pct99":
            canary = leakage_canary(grid, ctx, feat_names, DATA / "training_features.tif")
    results["arms"] = arms_out
    results["canary"] = canary
    best = max(arms_out, key=lambda a: arms_out[a]["holdout_all"]["dti"])
    results["selected_arm"] = best
    pct = ARMS[best]

    # Final submission uses the FULL mapped catalogue as the collar (no holdout here).
    cands = ridge_candidates(tmi_hg, valid & fp, pct)
    final = collar(cands, grid.catalogue).astype(np.float32)
    final[~fp] = 0.0
    n_dots = int((final > 0).sum())
    print("final dots", n_dots, "selected", best, flush=True)

    # Research artifacts that are not audited for the docs/downloads guard live in archive/quarantined-*.
    OUTDIR = ROOT / "archive" / "quarantined-20261029"
    OUTDIR.mkdir(parents=True, exist_ok=True)
    # Prefix makes the status unmissable: this file is NOT cleared for competition upload.
    out_tif = OUTDIR / f"DO-NOT-SUBMIT_gemsdoekarage1-{RUN_ID}-{best.lower()}-{n_dots}dots-zeros.tif"
    name = f"gemsdoekarage1-{RUN_ID}-{best.lower()}"[:140]
    note = f"label-free tmi_hg ridge, pct {pct:g}, 3px catalogue collar, {n_dots} dots"[:140]
    W57.write_submission(out_tif, final, DATA / "sample_submission.tif", fp, note=note, name=name,
                         catalogue=grid.catalogue,
                         metadata=dict(method="label-free tmi_hg 3x3 ridge, percentile threshold, 3px collar"))
    receipt = validate(out_tif, fp, grid.catalogue)
    rho_and_dupes = U57.compare_array_to_registry(final, registry_index(out_tif), fp,
                                                 file_sha256=sha256(out_tif), include_reverse=True)
    results["status"] = "NEGATIVE / DO NOT SUBMIT (see registry_check and holdout)"
    results["final"] = dict(file=str(out_tif.relative_to(ROOT)), selected_arm=best, dots=n_dots,
                            file_sha256=sha256(out_tif), zip_sha256=sha256(out_tif.with_suffix(".zip")),
                            validator=receipt)
    results["registry_check"] = {k: v for k, v in rho_and_dupes.items() if k != "rows"}
    # Saved-byte audit receipt entry, read by tests/test_session_1668dda0_hardening.py.
    results["candidates"] = [dict(file=out_tif.name, sha256=sha256(out_tif), verdict="negative",
                                  literal_lattice_duplicate=bool(rho_and_dupes["duplicate_count"] > 0),
                                  note="DO NOT SUBMIT: fails literal 70%/3px gate vs 13GEMS lattice (non-informative, see lattice_gate_null_check)")]
    results["registry_rows_top"] = sorted(
        [r for r in rho_and_dupes.get("rows", []) if "error" not in r],
        key=lambda r: -r.get("my_dots_within_3px_of_theirs", 0))[:10]
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "thd_ridge_candidate_20261029.json").write_text(
        json.dumps(results, indent=2, default=float) + "\n")
    print("wrote", out_tif, flush=True)


if __name__ == "__main__":
    main()
