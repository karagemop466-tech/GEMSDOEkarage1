#!/usr/bin/env python3
"""Experiment 1 of session arena/a8e4de2e (30 Oct 2026): hypothesis H-R1.

Hypothesis (pre-registered in knowledge/hypotheses-20261030.md, rank 1):
    Potassic (K-high, Th-low) alteration that coincides with a magnetic
    gradient maximum marks a fault-controlled fluid pathway.

Method (label-free: the mapped catalogue is NOT used to build the surface):
    1. zK, zTh = acquisition-block z-scores of GeoDAWN K and Th
       (external/geodawn_rad_u8.tif bands 1-2; block ids from
       external/acquisition_block_id_100m.tif), valid where TC>0 and block>0.
    2. r = zK - zTh, normalised-convolution smoothed (sigma 1.5 px); r+ = max(r, 0).
    3. m = clip(tmi_hg / P98(tmi_hg), 0, 1), official band 3 of training_features.tif.
    4. S = r+ * m inside the valid footprint.  S_norm = S / max(S)  (the surface).
    5. Dots = local maxima of S (3x3), strongest first, spacing >= 2.8 px,
       up to the 37,654-dot budget used by the other lanes.

Scoring (reuses the shared template, unmodified):
    * PRIMARY: vendor/gems57 holdout.build_holdout / holdout.evaluate, the
      `gems57-pooled-hide-v2` evaluator (alpha 0.2, beta 0.8, 3 px kernel,
      16 hide-and-recover cells).  Truth = withheld MAPPED catalogue segments.
    * SECONDARY PROXY (not the competition truth): recall of off-catalogue
      USGS SGMC geologic-map fault pixels (> 3 px from the mapped catalogue)
      within 3 px of the dots.  Owner-derived uint8 mirror; labelled proxy.
    * Controls: matched-count uniform random dots (3 seeds) and the registry's
      GEMSDOE32_B2 raster, all scored on the same cells.
    * Leakage canary: each feature alone, per-cell AUC on the holdout cells.
    * Uniqueness: surface Spearman and final-dot 3 px overlap vs every local
      TIF (shared gems57.uniqueness.compare_array_to_registry, diagnostic list).
    * Validation: shared writer + validator (zeros-outside primary); NaN-outside
      twin for the official wording, checked separately.

Labels: every number is HOLDOUT-DTI (evaluator version, withheld positives, CI)
or PROXY.  Nothing here is ORGANIZER-CONFIRMED.

Usage:  GEMS_DATA_DIR=/tmp/gems_data python scripts/run_h_r1_kth_magedge.py
"""
from __future__ import annotations

import glob
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

from gems57 import evaluate_holdout as EH57  # noqa: E402
from gems57 import grid as G57  # noqa: E402
from gems57 import holdout as H57  # noqa: E402
from gems57 import submission_writer as SW57  # noqa: E402
from gems57 import uniqueness as U57  # noqa: E402
from gems57.validate import validate  # noqa: E402

DATA = Path(os.environ.get("GEMS_DATA_DIR", "/tmp/gems_data"))
SESSION = "arena/a8e4de2e-gemsdoekarage1"
DATE = "2026-10-30"
NAME = "karage1-hr1-kth-magedge-37654-20261030-zeros"
NAME_NAN = "karage1-hr1-kth-magedge-37654-20261030-nan"
ARCHIVE = ROOT / "archive" / "research-hr1-20261030"
EVIDENCE = ROOT / "evidence" / "exp_h_r1_kth_magedge_20261030.json"
RUN_CARD = ROOT / "evidence" / "run_card_h_r1_20261030.json"

BUDGET_DOTS = 37654
SPACING_PX = 2.8
SEEDS = (101, 202, 303)
SIGMA_PX = 1.5
DOT_RADIUS_PX = 3.0
REG_GLOBS = ("registry/*.tif", "docs/downloads/*.tif", "docs/candidates/*.tif", "archive/**/*.tif")

# Fixed BEFORE the run.  Not edited after the result is seen.
DECISION_RULE = dict(
    primary_metric="HOLDOUT-DTI pooled, gems57-pooled-hide-v2, 16 cells",
    promote_requires=[
        "candidate pooled DTI > matched-random-null pooled DTI (mean of 3 seeds)",
        "paired per-cell bootstrap 95% CI lower bound of (candidate - null) > 0",
        "leakage canary: every single feature's per-cell direction-invariant AUC < 0.90",
        "shared validator passes on the zeros-outside primary",
        "literal registry gate: surface Spearman <= 0.90 AND final-dot 3 px overlap <= 0.70 vs every local TIF",
    ],
    secondary_proxy="SGMC off-catalogue recall within 3 px; informational only; cannot promote on its own",
    note="A promote verdict here would still NOT clear a weekly slot; a separate selector step is required.",
)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def block_z(x: np.ndarray, blk: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Per-acquisition-block z-score; zero outside ``valid``."""
    out = np.zeros(x.shape, np.float32)
    ids = blk[valid].astype(np.int64)
    vals = x[valid].astype(np.float64)
    nb = int(ids.max()) + 1
    n = np.bincount(ids, minlength=nb).astype(np.float64)
    s = np.bincount(ids, vals, nb)
    ss = np.bincount(ids, vals * vals, nb)
    mu = s / np.maximum(n, 1.0)
    sd = np.sqrt(np.maximum(ss / np.maximum(n, 1.0) - mu * mu, 1e-12))
    out[valid] = ((vals - mu[ids]) / sd[ids]).astype(np.float32)
    return out


def smooth_masked(x: np.ndarray, valid: np.ndarray, sigma: float) -> np.ndarray:
    """Normalised convolution: smooth only over valid cells."""
    v = valid.astype(np.float64)
    num = ndi.gaussian_filter(x.astype(np.float64) * v, sigma, mode="constant")
    den = ndi.gaussian_filter(v, sigma, mode="constant")
    out = np.where(den > 1e-6, num / np.maximum(den, 1e-6), 0.0)
    return (out * valid).astype(np.float32)


def build_surface(foot: np.ndarray) -> dict:
    with rasterio.open(DATA / "external" / "geodawn_rad_u8.tif") as ds:
        assert ds.count >= 4 and list(ds.descriptions[:4]) == ["K", "Th", "U", "TC"], ds.descriptions
        k = ds.read(1).astype(np.float32)
        th = ds.read(2).astype(np.float32)
        tc = ds.read(4).astype(np.float32)
    with rasterio.open(DATA / "external" / "acquisition_block_id_100m.tif") as ds:
        blk = ds.read(1)
    with rasterio.open(DATA / "training_features.tif") as ds:
        assert ds.descriptions[2].startswith("tmi_hg "), ds.descriptions[2]
        tmi_hg = ds.read(3).astype(np.float32)
    tmi_ok = np.isfinite(tmi_hg) & (tmi_hg > -1e30)
    valid = foot & (tc > 0) & (blk > 0) & tmi_ok
    zk = block_z(k, blk, valid)
    zt = block_z(th, blk, valid)
    r = zk - zt
    r_s = smooth_masked(r, valid, SIGMA_PX)
    rp = np.maximum(r_s, 0.0) * valid
    p98 = float(np.percentile(tmi_hg[valid], 98))
    m = np.clip(np.where(valid, tmi_hg, 0.0) / p98, 0.0, 1.0).astype(np.float32) * valid
    s = (rp * m).astype(np.float32)
    s_max = float(s.max())
    s_norm = (s / s_max).astype(np.float32) if s_max > 0 else s
    return dict(zk=zk, zt=zt, rp=rp.astype(np.float32), m=m, s=s, s_norm=s_norm,
                valid=valid, p98=p98, s_max=s_max, valid_cells=int(valid.sum()))


def place_dots(s: np.ndarray, foot: np.ndarray, budget: int, spacing: float) -> np.ndarray:
    """Local maxima (3x3), strongest first, greedy minimum spacing."""
    h, w = s.shape
    peaks = (s > 0) & (s == ndi.maximum_filter(s, size=3)) & foot
    ys, xs = np.nonzero(peaks)
    order = np.argsort(-s[ys, xs], kind="stable")
    ys, xs = ys[order], xs[order]
    r = int(np.ceil(spacing)) - 1
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (yy * yy + xx * xx) < spacing * spacing
    blocked = np.zeros((h, w), bool)
    dots = np.zeros((h, w), bool)
    n = 0
    for y, x in zip(ys.tolist(), xs.tolist()):
        if blocked[y, x]:
            continue
        dots[y, x] = True
        n += 1
        y0, y1 = max(0, y - r), min(h, y + r + 1)
        x0, x1 = max(0, x - r), min(w, x + r + 1)
        blocked[y0:y1, x0:x1] |= disk[(y0 - (y - r)):(y1 - (y - r)), (x0 - (x - r)):(x1 - (x - r))]
        if n >= budget:
            break
    return dots


def canary(surf: dict, ctx) -> dict:
    """Per-feature, per-cell AUC of withheld-truth vs other active pixels."""
    feats = {"zK_block": surf["zk"], "zTh_block": surf["zt"], "r_plus_KminusTh": surf["rp"],
             "tmi_hg_norm": surf["m"], "surface_S": surf["s"]}
    out = {}
    for name, arr in feats.items():
        aucs = {}
        for c in ctx.cells:
            a = arr[c.bbox]
            act = c.active & np.isfinite(a)
            truth = np.zeros(c.active.shape, bool)
            truth[c.truth_yx] = True
            y = truth[act]
            if y.sum() == 0 or y.sum() == y.size:
                continue
            auc = float(roc_auc_score(y, a[act]))
            aucs[c.key] = dict(auc=auc, direction_invariant=max(auc, 1.0 - auc))
        di = [v["direction_invariant"] for v in aucs.values()]
        out[name] = dict(
            cells=len(aucs), mean_direction_invariant_auc=float(np.mean(di)) if di else None,
            max_direction_invariant_auc=float(np.max(di)) if di else None,
            passed=bool(di and max(di) < 0.90), per_cell=aucs,
        )
    return out


def paired_ci(delta: np.ndarray, n: int = 4000, seed: int = 7) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, delta.size, size=(n, delta.size))
    stats = delta[idx].mean(axis=1)
    return float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))


def score(dots: np.ndarray, ctx) -> dict:
    r = H57.evaluate(dots, ctx)
    keys = [c.key for c in ctx.cells]
    per_cell = np.array([r["per_fold_dti"][k] for k in keys])
    lo, hi = paired_ci(per_cell)  # bootstrap over the 16 cells of the mean per-cell DTI
    return dict(pooled_dti=r["pooled_dti"], mean_cell_dti=float(per_cell.mean()),
                ci95_cell_bootstrap_of_mean=[lo, hi], per_cell_dti=dict(zip(keys, per_cell.tolist())),
                withheld_positives=r["pooled_n_truth"], emitted_pixels=r["emitted_pixels"],
                on_visible_catalogue=r["on_visible_catalogue"], pooled_tp=r["pooled_tp"],
                pooled_fp=r["pooled_fp"], pooled_fn=r["pooled_fn"])


def proxy_recall(dots: np.ndarray, sgmc_off: np.ndarray) -> dict:
    near = ndi.distance_transform_edt(~dots) <= DOT_RADIUS_PX
    n = int(sgmc_off.sum())
    return dict(sgmc_off_pixels=n, recall_within_3px=float((near & sgmc_off).sum() / n) if n else None,
                label="PROXY (owner-derived USGS SGMC mirror), not the competition truth")


def registry_files() -> list[dict]:
    seen, rows = set(), []
    patterns = [str(ROOT / pat) for pat in REG_GLOBS] + [str(DATA / "scored" / "*.tif")]
    for pat in patterns:
        for f in sorted(glob.glob(pat, recursive=True)):
            p = Path(f).resolve()
            if p in seen or ARCHIVE in p.parents or "/data/" in str(p):
                continue
            seen.add(p)
            rows.append(dict(repo="local-repo", submission=p.name, file=str(p)))
    return rows


def main() -> None:
    grid = G57.load_grid(DATA)
    foot = grid.footprint
    cat = grid.catalogue
    ctx = H57.build_holdout(grid)
    print(f"holdout cells={len(ctx.cells)} withheld={sum(c.n_truth for c in ctx.cells)}", flush=True)

    surf = build_surface(foot)
    print(f"surface valid_cells={surf['valid_cells']} p98={surf['p98']:.4f} s_max={surf['s_max']:.4f}", flush=True)

    dots = place_dots(surf["s"], foot, BUDGET_DOTS, SPACING_PX)
    n_dots = int(dots.sum())
    print(f"dots placed={n_dots} (budget {BUDGET_DOTS})", flush=True)

    cand_score = score(dots, ctx)
    print(f"candidate pooled DTI={cand_score['pooled_dti']:.5f}", flush=True)

    # --- controls on the same cells
    foot_idx = np.flatnonzero(foot.ravel())
    null_runs = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        pick = rng.choice(foot_idx, size=n_dots, replace=False)
        nd = np.zeros(foot.size, bool)
        nd[pick] = True
        sc = score(nd.reshape(foot.shape), ctx)
        null_runs.append(sc)
        print(f"null seed={seed} pooled DTI={sc['pooled_dti']:.5f}", flush=True)
    keys = [c.key for c in ctx.cells]
    null_cell = np.mean([[r["per_cell_dti"][k] for k in keys] for r in null_runs], axis=0)
    cand_cell = np.array([cand_score["per_cell_dti"][k] for k in keys])
    delta = cand_cell - null_cell
    d_lo, d_hi = paired_ci(delta)
    null_pooled = float(np.mean([r["pooled_dti"] for r in null_runs]))

    champ_path = ROOT / "registry" / "GEMSDOE32_B2.tif"
    with rasterio.open(champ_path) as ds:
        champ = np.nan_to_num(ds.read(1), nan=0.0) > 0
    champ_score = score(champ & foot, ctx)
    print(f"champion GEMSDOE32_B2 pooled DTI={champ_score['pooled_dti']:.5f}", flush=True)

    # --- canary
    can = canary(surf, ctx)
    for k, v in can.items():
        print(f"canary {k}: max DI-AUC={v['max_direction_invariant_auc']}", flush=True)

    # --- secondary proxy (off-catalogue SGMC, > 3 px from mapped catalogue)
    with rasterio.open(DATA / "external" / "derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = (ds.read(1) > 0) & foot
    d_cat = ndi.distance_transform_edt(~cat)
    sgmc_off = sgmc & (d_cat > 3.0)
    def random_mask(seed: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        m = np.zeros(foot.size, bool)
        m[rng.choice(foot_idx, size=n_dots, replace=False)] = True
        return m.reshape(foot.shape)

    null_recalls = [proxy_recall(random_mask(s), sgmc_off)["recall_within_3px"] for s in SEEDS]
    proxy = dict(candidate=proxy_recall(dots, sgmc_off),
                 random_null_per_seed=null_recalls,
                 random_null_mean=float(np.mean(null_recalls)),
                 champion=proxy_recall(champ & foot, sgmc_off))

    # --- artefacts: shared writer (zeros outside, the gated primary)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    values = dots.astype(np.float32)
    note = "H-R1 K-Th alteration x tmi_hg co-location, label-free; RESEARCH ONLY; holdout-negative; do not submit"
    assert len(note) <= 140 and len(NAME) <= 140
    receipt = SW57.write_submission(ARCHIVE / f"{NAME}.tif", values, DATA / "sample_submission.tif", foot,
                                    note=note, name=NAME, catalogue=None,
                                    metadata=dict(session=SESSION, hypothesis="H-R1", date=DATE))
    tif_path = ARCHIVE / f"{NAME}.tif"
    v_zero = validate(tif_path, foot, None)

    # --- NaN-outside twin (official wording), validated separately
    nan_vals = np.where(foot, values, np.float32("nan")).astype(np.float32)
    nan_path = ARCHIVE / f"{NAME_NAN}.tif"
    G57.write_submission(nan_path, nan_vals, mode="nan")
    with rasterio.open(nan_path) as ds:
        a = ds.read(1)
        nan_meta = dict(crs=str(ds.crs), shape=[ds.height, ds.width], dtype=ds.dtypes[0],
                        count=ds.count, nodata=ds.nodata, transform=list(tuple(ds.transform)[:6]))
    nan_checks = dict(
        single_band=nan_meta["count"] == 1, float32=nan_meta["dtype"] == "float32",
        shape_3730x3292=nan_meta["shape"] == [3730, 3292], crs_32611=nan_meta["crs"] == "EPSG:32611",
        transform_matches=nan_meta["transform"] == list(tuple(G57.TRANSFORM)[:6]),
        nan_exactly_outside_footprint=bool(np.array_equal(np.isnan(a), ~foot)),
        finite_in_footprint_in_0_1=bool(np.isfinite(a[foot]).all() and (a[foot] >= 0).all() and (a[foot] <= 1).all()),
    )
    nan_checks["all_passed"] = all(nan_checks.values())

    # --- uniqueness: surface (pre-placement) and final dots, vs every local TIF
    reg = registry_files()
    print(f"registry rasters scanned={len(reg)}", flush=True)
    surface_rows = U57.compare_array_to_registry(surf["s_norm"], reg, foot, include_reverse=False)
    dot_rows = U57.compare_array_to_registry(values, reg, foot, file_sha256=sha256(tif_path))

    def worst(summary: dict) -> dict:
        rows = [r for r in summary.get("rows", []) if "error" not in r]
        if not rows:
            return {}
        top_rho = max(rows, key=lambda r: r.get("spearman_full_footprint") or -2)
        top_ov = max(rows, key=lambda r: r.get("my_dots_within_3px_of_theirs") or -1)
        return dict(max_spearman=top_rho.get("spearman_full_footprint"), max_spearman_file=top_rho.get("file"),
                    max_my_dots_within_3px=top_ov.get("my_dots_within_3px_of_theirs"),
                    max_overlap_file=top_ov.get("file"), rows_compared=len(rows))

    surface_worst = worst(surface_rows)
    dot_worst = worst(dot_rows)
    dot_rows_ok = [r for r in dot_rows.get("rows", []) if "error" not in r]
    over_gate = [dict(file=r["file"], my_dots_within_3px=r["my_dots_within_3px_of_theirs"],
                      their_dots_within_3px_of_mine=r["their_dots_within_3px_of_mine"],
                      jaccard=r["jaccard_dot_sets"], their_positive_cells=r["their_dots"])
                 for r in dot_rows_ok if r["my_dots_within_3px_of_theirs"] > 0.70]
    focus_rows = [r for r in dot_rows_ok if Path(r["file"]).parent == ROOT / "registry"
                  and Path(r["file"]).name.startswith("GEMSDOE")]
    focus_nine = dict(files=len(focus_rows),
                      max_my_dots_within_3px=max((r["my_dots_within_3px_of_theirs"] for r in focus_rows), default=None),
                      max_their_dots_within_3px_of_mine=max((r["their_dots_within_3px_of_mine"] for r in focus_rows), default=None),
                      max_jaccard=max((r["jaccard_dot_sets"] for r in focus_rows), default=None))
    gate_rho_ok = surface_worst.get("max_spearman") is not None and surface_worst["max_spearman"] <= 0.90
    gate_ov_ok = dot_worst.get("max_my_dots_within_3px") is not None and dot_worst["max_my_dots_within_3px"] <= 0.70

    # --- verdict under the pre-registered rule
    crit = dict(
        candidate_beats_null_pooled=bool(cand_score["pooled_dti"] > null_pooled),
        paired_ci_lower_bound_gt_zero=bool(d_lo > 0),
        canary_all_below_0_90=all(v["passed"] for v in can.values()),
        validator_passed=bool(v_zero["all_checks_passed"]),
        registry_surface_rho_le_0_90=bool(gate_rho_ok),
        registry_dot_overlap_le_0_70=bool(gate_ov_ok),
    )
    promote = all(crit.values())
    verdict = "promote-to-selector" if promote else "negative"

    out = dict(
        schema="karage1-exp-hr1-v1", session=SESSION, date_utc=DATE,
        evaluator=dict(module="vendor/gems57 evaluate_holdout/holdout (unmodified)",
                       version=EH57.VERSION, label="HOLDOUT-DTI",
                       alpha=0.2, beta=0.8, kernel_px=3.0, cells=len(ctx.cells),
                       withheld_positives=sum(c.n_truth for c in ctx.cells),
                       truth_is="withheld MAPPED catalogue segments (not the competition's new-fault test set)",
                       implementation_hashes=EH57.implementation_hashes()),
        decision_rule=DECISION_RULE,
        inputs=dict(data_dir=str(DATA), data_status="pinned third-party mirrors; organizer authenticity NOT established",
                    geodawn_rad=dict(file="external/geodawn_rad_u8.tif", sha256=sha256(DATA / "external" / "geodawn_rad_u8.tif")),
                    blocks=dict(file="external/acquisition_block_id_100m.tif",
                                sha256=sha256(DATA / "external" / "acquisition_block_id_100m.tif")),
                    tmi_hg=dict(file="training_features.tif band 3 (official)", sha256=sha256(DATA / "training_features.tif")),
                    p98_tmi_hg=surf["p98"], valid_cells=surf["valid_cells"], s_max=surf["s_max"]),
        candidate=dict(dots=n_dots, budget=BUDGET_DOTS, spacing_px=SPACING_PX, sigma_px=SIGMA_PX,
                       shortfall_vs_budget=BUDGET_DOTS - n_dots, on_visible_catalogue=cand_score["on_visible_catalogue"],
                       holdout=cand_score),
        controls=dict(random_null_matched_count=dict(seeds=list(SEEDS), pooled_dti_per_seed=[r["pooled_dti"] for r in null_runs],
                                                      pooled_mean=null_pooled),
                      champion_GEMSDOE32_B2=dict(holdout=champ_score, label="HOLDOUT-DTI; registry raster; owner-reported 0.2778 is unverified")),
        paired_vs_null=dict(mean_delta=float(delta.mean()), ci95=[d_lo, d_hi], per_cell_delta=dict(zip(keys, delta.tolist()))),
        leakage_canary=can,
        proxy_sgmc_offcatalogue=proxy,
        artefacts=dict(zeros_primary=dict(file=str(tif_path.relative_to(ROOT)), sha256=receipt["sha256"],
                                          bytes=receipt["bytes"], name=NAME, note=note, note_chars=len(note),
                                          validator_checks=v_zero["checks"], validator_all_passed=v_zero["all_checks_passed"],
                                          submission_slots_used=0, approved_for_weekly_slot=False),
                       nan_outside_twin=dict(file=str(nan_path.relative_to(ROOT)), sha256=sha256(nan_path),
                                             checks=nan_checks,
                                             note="Official text says outside-bounds cells are null or NaN. The shared writer's zeros policy is stricter; the two readings conflict and are reported, not resolved.")),
        uniqueness=dict(registry_rasters_scanned=len(reg), surface_pre_placement=surface_worst,
                        final_dots=dot_worst, dot_gate_trips_70pct=over_gate, nine_focus_site_rasters=focus_nine,
                        rows_surface=surface_rows.get("rows"), rows_dots=dot_rows.get("rows")),
        criteria=crit,
        verdict=verdict,
        ok_to_submit=False,
        slot_selected_or_spent=False,
    )
    EVIDENCE.write_text(json.dumps(out, indent=2, sort_keys=True, default=float) + "\n")
    print(f"verdict={verdict}; wrote {EVIDENCE.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
