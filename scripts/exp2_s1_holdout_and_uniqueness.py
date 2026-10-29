#!/usr/bin/env python3
"""Experiment 2 (session arena/5ee7ef4b): H-S1 holdout test, leakage canary, uniqueness.

Shared tools only: vendor/gems57 grid, holdout.build_holdout, holdout.score_cell,
holdout.evaluate (unmodified). Feature used for the emission: tmi_hg (magnetics only;
it never reads the mapped catalogue).

Arms (same 16 hide-and-recover cells as Experiment 1):
  A. as_submitted   : the exact submitted dots (apron 2 px from the FULL mapped catalogue),
                      scored by holdout.evaluate. Expected to be penalised by design.
  B. holdout_faithful: re-run the same selection once per cell with the apron computed from
                      that cell's VISIBLE catalogue only, so the emission never sees withheld
                      truth. Each cell is scored with its own emission (pooled TP/FP/FN).
Leakage canary: per cell, AUC of smoothed tmi_hg for withheld truth vs other active pixels.
Uniqueness: exact-hash and dot-level 3 px overlap vs every local TIF in docs/downloads and registry.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems57 import grid as G57  # noqa: E402
from gems57 import holdout as H57  # noqa: E402
from generate_s1_tmihg_ridge import read_band, select_dots  # noqa: E402  (same selection code)

DATA = Path(os.environ.get("GEMS_DATA_DIR", "/tmp/gems_data"))
SUB = ROOT / "archive" / "research-s1-20261029" / "karage1-s1-tmihg-ridge-offcat-20261029-zeros.tif"
WITNESS = DATA / "scored" / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
WITNESS_SHA = "b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2"
OUT = ROOT / "evidence" / "exp2_s1_holdout_and_uniqueness_20261029.json"
ALPHA, BETA = H57.ALPHA, H57.BETA


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pooled(cells_terms: list[dict]) -> float:
    tp = sum(t["tp"] for t in cells_terms)
    fp = sum(t["fp"] for t in cells_terms)
    fn = sum(t["fn"] for t in cells_terms)
    return float(tp / (tp + ALPHA * fp + BETA * fn + 1e-12))


def bootstrap(vals: np.ndarray, n: int = 2000, seed: int = 7) -> list[float]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, vals.size, size=(n, vals.size))
    m = vals[idx].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def overlap(a: np.ndarray, b: np.ndarray, r: float = 3.0) -> float:
    """Fraction of a's dots within r px of any b dot (literal 3 px rule)."""
    if not a.any() or not b.any():
        return 0.0
    rr = int(np.ceil(r))
    yy, xx = np.mgrid[-rr:rr + 1, -rr:rr + 1]
    near = ndi.binary_dilation(b, structure=(yy * yy + xx * xx) <= r * r)
    return float(near[a].mean())


def main() -> None:
    grid = G57.load_grid(DATA)
    ctx = H57.build_holdout(grid)
    tmi_hg = read_band(DATA / "training_features.tif", "tmi_hg")
    fp = grid.footprint

    with rasterio.open(SUB) as ds:
        sub = ds.read(1) > 0
    # ---- Arm A: as submitted --------------------------------------------------------
    rA = H57.evaluate(sub & fp, ctx)
    cells_A = [v for v in rA["folds"].values()]
    dtiA = rA["pooled_dti"]
    perA = np.array([v["dti"] for v in cells_A])

    # ---- Arm B: holdout-faithful, visible-only apron per cell -----------------------
    terms_B, per_cell_B, leak = [], {}, {}
    for cell in ctx.cells:
        vis = ctx.visible(cell.key)
        # selection uses the visible catalogue only (no withheld truth is read)
        dots_c, info_c = select_dots(tmi_hg, fp, vis)
        r = H57.score_cell(cell, dots_c)
        terms_B.append(r)
        per_cell_B[cell.key] = dict(dti=r["dti"], tp=r["tp"], fp=r["fp"], fn=r["fn"],
                                    n_truth=r["n_truth"], n_emitted=r["n_emitted"],
                                    dots_selected=info_c["dots_kept"])
        # leakage canary: single feature AUC on this cell's active pixels
        act = cell.active
        truth_full = np.zeros(fp.shape, bool)
        y0, y1 = cell.bbox[0].start, cell.bbox[0].stop
        x0, x1 = cell.bbox[1].start, cell.bbox[1].stop
        ty, tx = cell.truth_yx
        truth_full[y0 + ty, x0 + tx] = True
        f = tmi_hg[y0:y1, x0:x1]
        f = ndi.gaussian_filter(np.where(np.isfinite(f), f, 0.0), 1.0)
        y = truth_full[y0:y1, x0:x1][act]
        if y.any() and (~y).any():
            auc = float(roc_auc_score(y, f[act]))
        else:
            auc = float("nan")
        leak[cell.key] = dict(auc_tmi_hg_alone=auc, n_truth=int(y.sum()))
    dtiB = pooled(terms_B)
    perB = np.array([t["dti"] for t in terms_B])

    aucs = np.array([v["auc_tmi_hg_alone"] for v in leak.values() if np.isfinite(v["auc_tmi_hg_alone"])])
    canary = dict(feature="tmi_hg (smoothed sigma 1 px)", aucs_min=float(aucs.min()), aucs_max=float(aucs.max()),
                  aucs_mean=float(aucs.mean()), ceiling=0.90,
                  pass_below_ceiling=bool(aucs.max() < 0.90), per_cell=leak)

    # ---- Literal internal lattice witness (13GEMSDOE calibration raster, pinned sha) ----
    with rasterio.open(WITNESS) as ds:
        wit = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & fp
    assert sha256(WITNESS) == WITNESS_SHA, "lattice witness hash mismatch"
    lattice = dict(witness=str(WITNESS.name), witness_sha256=WITNESS_SHA, witness_dots=int(wit.sum()),
                   mine_within_3px_of_witness=overlap(sub & fp, wit), witness_within_3px_of_mine=overlap(wit, sub & fp),
                   literal_70pct_rule_duplicate=bool(overlap(sub & fp, wit) > 0.70))

    # ---- Uniqueness vs every local TIF --------------------------------------------
    cands = sorted(set(list((ROOT / "docs" / "downloads").glob("*.tif")) + list((ROOT / "registry").glob("*.tif"))
                       + list((ROOT / "archive").rglob("*.tif"))))
    my = sub & fp
    my_sha = sha256(SUB)
    uniq = []
    for p in cands:
        if p.resolve() == SUB.resolve():
            continue
        with rasterio.open(p) as ds:
            a = ds.read(1)
        b = (np.nan_to_num(a, nan=0.0) > 0) & fp
        uniq.append(dict(file=str(p.relative_to(ROOT)), sha256=sha256(p), exact_duplicate=sha256(p) == my_sha,
                         dots=int(b.sum()),
                         mine_within_3px_of_theirs=overlap(my, b),
                         theirs_within_3px_of_mine=overlap(b, my),
                         jaccard_exact_cells=float((my & b).sum() / max(1, (my | b).sum()))))
    worst = max(uniq, key=lambda u: max(u["mine_within_3px_of_theirs"], u["theirs_within_3px_of_mine"]))

    receipt = dict(
        schema="karage1-exp2-s1-v1", session="arena/5ee7ef4b-gemsdoekarage1", date_utc="2026-10-29",
        hypothesis="H-S1 magnetic tmi_hg crest dots, off-catalogue apron (see scripts/generate_s1_tmihg_ridge.py)",
        evaluator="vendor/gems57 holdout.score_cell / holdout.evaluate (unmodified)",
        evaluator_label="HOLDOUT-DTI alpha=0.2 beta=0.8 R=3px; 16 cells (2 draws x 4 folds x 2 modes)",
        withheld_positives_total=int(sum(c.n_truth for c in ctx.cells)),
        file=str(SUB.relative_to(ROOT)), file_sha256=my_sha,
        arm_A_as_submitted=dict(pooled_dti=dtiA, ci95_cell_bootstrap=bootstrap(perA),
                                dots=int(my.sum()), on_visible_catalogue=int((my & grid.catalogue).sum()),
                                on_full_catalogue_within_2px=int((my & (ndi.distance_transform_edt(~grid.catalogue) <= 2)).sum())),
        lattice_witness=lattice,
        arm_B_holdout_faithful=dict(pooled_dti=dtiB, ci95_cell_bootstrap=bootstrap(perB), per_cell=per_cell_B),
        leakage_canary=canary,
        uniqueness=dict(n_local_tifs_compared=len(uniq), exact_duplicates=sum(u["exact_duplicate"] for u in uniq),
                        max_mine_within_3px_of_theirs=max(u["mine_within_3px_of_theirs"] for u in uniq),
                        max_theirs_within_3px_of_mine=max(u["theirs_within_3px_of_mine"] for u in uniq),
                        worst_match=worst, all=uniq,
                        scope="local repo TIFs only (docs/downloads, registry, archive). Focus-site and 13GEMSDOE "
                              "rasters NOT compared here; the restore of the scored group was rate-limited."),
        verdict_scope="No leaderboard estimate is produced. Internal holdout DTI is not the organizer score.",
    )
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True, default=float) + "\n")
    print(f"A as_submitted   DTI={dtiA:.5f}  CI95={receipt['arm_A_as_submitted']['ci95_cell_bootstrap']}")
    print(f"B holdout-faith. DTI={dtiB:.5f}  CI95={receipt['arm_B_holdout_faithful']['ci95_cell_bootstrap']}")
    print(f"canary AUC tmi_hg alone: min={canary['aucs_min']:.3f} max={canary['aucs_max']:.3f} pass={canary['pass_below_ceiling']}")
    print(f"lattice witness: mine->witness={lattice['mine_within_3px_of_witness']:.4f} literal70_dup={lattice['literal_70pct_rule_duplicate']}")
    print(f"uniqueness: exact dupes={receipt['uniqueness']['exact_duplicates']} "
          f"max mine->theirs={receipt['uniqueness']['max_mine_within_3px_of_theirs']:.4f} "
          f"max theirs->mine={receipt['uniqueness']['max_theirs_within_3px_of_mine']:.4f} "
          f"n={len(uniq)} worst={worst['file']}")


if __name__ == "__main__":
    main()
