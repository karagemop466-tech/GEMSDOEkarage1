"""Hide-and-recover holdout on the public catalogue (the only truth available locally).

Protocol (shared template semantics):
* the catalogue is split into *whole segments* (8-connected components of ``labels.tif``);
* the footprint is tiled into square spatial blocks (default 200 px = 20 km); blocks are dealt to K
  folds in a checkerboard so every fold is spatially interleaved with the others;
* a segment is WITHHELD in fold k when the majority of its pixels fall in fold-k blocks;
* VISIBLE faults (all other segments) are masked pixel-exactly from the scored domain, and a
  buffer of ``buffer_px`` around every visible pixel is also removed so credit cannot leak from a
  withheld segment that abuts a visible one;
* any catalogue-derived step of a candidate (here only the catalogue-apron prune) must be
  recomputed from the VISIBLE faults of that fold, never from the full catalogue;
* the score is the POOLED DTI (TP/FP/FN summed over folds), with a 95% CI from a block bootstrap
  over the same 20 km blocks (paired when two arms are compared).

Caveat recorded by the sibling repositories and repeated here: catalogue-truth holdouts rank the
owner-reported live scores only weakly across detector families (Spearman ~0.5, n = 12). A
holdout gain is a screen, never a leaderboard estimate.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy import ndimage

from . import metric

VERSION = "gemsk-hide-recover-v1"
BLOCK_PX = 200
K_FOLDS = 4
BUFFER_PX = 3


def implementation_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]


def make_folds(catalogue: np.ndarray, footprint: np.ndarray, k: int = K_FOLDS, block_px: int = BLOCK_PX,
               buffer_px: int = BUFFER_PX, scheme: str = "blocked", seed: int = 20261027) -> list[dict]:
    """Two schemes, both withholding WHOLE segments:

    * ``blocked``     - 20 km checkerboard blocks dealt to folds; a segment is withheld with the fold
                        owning the majority of its pixels. Tests blind discovery far from any visible
                        fault (every withheld block is emptied of visible faults).
    * ``interleaved`` - segments assigned to folds at random (seeded). Withheld strands sit among
                        visible ones, which is the live scenario (expert-mapped new strands next to
                        catalogued ones). Spatial autocorrelation can flatter *trained* models here,
                        which is why label-free fields are screened on both.
    """
    cat = catalogue & footprint
    lab, n = ndimage.label(cat, structure=np.ones((3, 3), int))
    if scheme == "blocked":
        H, W = cat.shape
        by = (np.arange(H) // block_px)[:, None]
        bx = (np.arange(W) // block_px)[None, :]
        block_fold = (by + bx) % k                      # checkerboard dealing of blocks to folds
        yy, xx = np.nonzero(lab)
        ids = lab[yy, xx]
        folds_at = block_fold[yy, xx]
        counts = np.zeros((n + 1, k), int)
        np.add.at(counts, (ids, folds_at), 1)
        seg_fold = counts.argmax(axis=1)
    elif scheme == "interleaved":
        rng = np.random.default_rng(seed)
        seg_fold = rng.integers(0, k, size=n + 1)
    else:
        raise ValueError(scheme)
    out = []
    for f in range(k):
        seg_ids = np.nonzero(seg_fold == f)[0]
        seg_ids = seg_ids[seg_ids != 0]                 # label 0 is background
        withheld = np.isin(lab, seg_ids) & cat
        visible = cat & ~withheld
        vis_buf = ndimage.binary_dilation(visible, iterations=buffer_px) if buffer_px > 0 else visible
        active = footprint & ~vis_buf
        out.append({"fold": f, "scheme": scheme, "withheld": withheld, "visible": visible, "active": active,
                    "n_withheld": int(withheld.sum()), "n_visible": int(visible.sum()),
                    "n_segments_withheld": int(((seg_fold == f)[1:]).sum())})
    return out


def block_ids(shape, block_px: int = BLOCK_PX):
    H, W = shape
    ncols = (W + block_px - 1) // block_px
    return ncols, lambda y, x: (y // block_px) * ncols + (x // block_px)


def evaluate_dots(dots: np.ndarray, fold: dict, block_px: int = BLOCK_PX) -> tuple[dict, np.ndarray]:
    """Score a binary dot raster on one fold; also return per-block (tp, fp, fn, n_truth) terms."""
    active = fold["active"]
    p = (np.asarray(dots, bool) & active).astype(np.float64)
    truth = fold["withheld"] & active
    res = metric.dti_components(p, truth, active=active)
    # per-block terms for the bootstrap (recomputed with the same kernel arithmetic)
    H, W = p.shape
    ncols, bid = block_ids(p.shape, block_px)
    nblocks = ncols * ((H + block_px - 1) // block_px)
    terms = np.zeros((nblocks, 4))
    yy, xx = np.nonzero(truth)
    if yy.size:
        credit = np.zeros(yy.size)
        for dy, dx, k in metric._OFFS:
            ny, nx = yy + dy, xx + dx
            ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
            credit[ok] = np.maximum(credit[ok], p[ny[ok], nx[ok]] * k)
        ids = bid(yy, xx)
        terms[:, 0] = np.bincount(ids, weights=credit, minlength=nblocks)
        terms[:, 2] = np.bincount(ids, weights=1.0 - credit, minlength=nblocks)
        terms[:, 3] = np.bincount(ids, minlength=nblocks)
    py, px = np.nonzero(p > 0)
    if py.size:
        d = ndimage.distance_transform_edt(~truth) if yy.size else np.full(p.shape, 1e9)
        w = p[py, px] * (1.0 - metric.kernel(d[py, px]))
        terms[:, 1] = np.bincount(bid(py, px), weights=w, minlength=nblocks)
    tot = terms.sum(axis=0)
    assert abs(tot[0] - res["tp"]) < 1e-6 and abs(tot[1] - res["fp"]) < 1e-6, (tot, res)
    return res, terms


def pooled(terms_list: list[np.ndarray]) -> dict:
    t = np.sum(terms_list, axis=0)
    tp, fp, fn, n = t.sum(axis=0)
    return {"tp": float(tp), "fp": float(fp), "fn": float(fn), "n_truth": int(n), "dti": metric.dti_from_components(tp, fp, fn)}


def bootstrap_ci(terms_by_arm: dict[str, list[np.ndarray]], draws: int = 1000, seed: int = 20261027):
    """Block bootstrap (paired across arms) of pooled DTI; returns per-arm CI and paired deltas vs the first arm."""
    arms = {k: np.sum(v, axis=0) for k, v in terms_by_arm.items()}
    names = list(arms)
    nb = len(arms[names[0]])
    nonempty = np.any([a.sum(axis=1) > 0 for a in arms.values()], axis=0)
    idx_all = np.nonzero(nonempty)[0]
    rng = np.random.default_rng(seed)
    picks = rng.integers(0, len(idx_all), size=(draws, len(idx_all)))
    vals = {}
    for nme, a in arms.items():
        sub = a[idx_all]
        s = sub[picks].sum(axis=1)
        vals[nme] = s[:, 0] / (s[:, 0] + metric.ALPHA * s[:, 1] + metric.BETA * s[:, 2] + metric.EPS)
    out = {}
    for nme in names:
        lo, hi = np.percentile(vals[nme], [2.5, 97.5])
        out[nme] = {"ci95": [float(lo), float(hi)]}
        if nme != names[0]:
            dlt = vals[nme] - vals[names[0]]
            out[nme]["paired_delta_vs_" + names[0]] = {"mean": float(dlt.mean()), "ci95": [float(np.percentile(dlt, 2.5)), float(np.percentile(dlt, 97.5))], "frac_positive": float((dlt > 0).mean())}
    return out


def auc_on_fold(score: np.ndarray, fold: dict, rng=None, n_neg: int = 200_000) -> float:
    """Rank AUC of a continuous surface for withheld-truth vs. other active pixels (leakage canary)."""
    from sklearn.metrics import roc_auc_score

    rng = rng or np.random.default_rng(0)
    act = fold["active"]
    pos = fold["withheld"] & act
    neg = act & ~pos
    ny, nx = np.nonzero(neg)
    sel = rng.choice(ny.size, size=min(n_neg, ny.size), replace=False)
    s_pos = score[pos]
    s_neg = score[ny[sel], nx[sel]]
    s = np.concatenate([s_pos, s_neg]).astype(np.float64)
    s = np.nan_to_num(s, nan=np.nanmin(s) if np.isfinite(s).any() else 0.0)
    y = np.concatenate([np.ones(s_pos.size), np.zeros(s_neg.size)])
    return float(roc_auc_score(y, s))
