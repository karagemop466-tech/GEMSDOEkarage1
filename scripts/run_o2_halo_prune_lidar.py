#!/usr/bin/env python3
"""Experiment E1 of session arena/9cf124bb-gemsdoekarage1 (31 Oct 2026): hypothesis H-O2.

Pre-registered in knowledge/hypotheses-9cf124bb-20261031.md (section 4) BEFORE this file was run.

Hypothesis: a label-free USGS 3DEP lidar scarp ridge (step_max) emits dots that the
mapped-catalogue halo rule can prune without leakage. Pruning dots within 2 px of the
*visible* catalogue (per fold) should raise pooled DTI on the shared hide-and-recover
holdout, versus the same emission unpruned and versus matched random dots.

Shared tools (unmodified): vendor/gems57 grid, holdout (cells, score_cell), metric
constants, submission_writer, validate, uniqueness. Placement, smoothing, paired bootstrap
and registry listing are imported from scripts/run_h_r1_kth_magedge.py (not copied).

Labels: every number is HOLDOUT-DTI (gems57-pooled-hide-v2, withheld positives, 95% CI) or PROXY.
Nothing here is ORGANIZER-CONFIRMED.

Usage: .venv/bin/python scripts/run_o2_halo_prune_lidar.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT))

from gems57 import grid as G57  # noqa: E402
from gems57 import holdout as H57  # noqa: E402
from gems57 import metric as M57  # noqa: E402
from gems57 import submission_writer as SW57  # noqa: E402
from gems57 import uniqueness as U57  # noqa: E402
from gems57.validate import validate  # noqa: E402
from scripts import run_h_r1_kth_magedge as HR1  # noqa: E402  (placement, smoothing, bootstrap, registry list)

DATA = ROOT / "data"
SESSION = "arena/9cf124bb-gemsdoekarage1"
DATE = "2026-10-31"
NAME = "karage1-o2-lidar-scarp-halo-prune-37654-20261031-zeros"
NAME_NAN = "karage1-o2-lidar-scarp-halo-prune-37654-20261031-nan"
PREFIX = "DO-NOT-SUBMIT_"  # every file from this run stays labelled until the owner selector clears it
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence" / "exp_o2_halo_prune_lidar_20261031.json"
RUN_CARD = ROOT / "evidence" / "run_card_o2_20261031.json"
LIDAR = DATA / "external" / "lidar_scarp_features_u8.tif"
SGMC = DATA / "external" / "derived_sgmc_faults_100m_u8.tif"
H_R1_RASTER = ROOT / "archive" / "research-hr1-20261030" / "karage1-hr1-kth-magedge-37654-20261030-zeros.tif"
B2_RASTER = ROOT / "registry" / "GEMSDOE32_B2.tif"
P25_RASTER = ROOT / "registry" / "GEMSDOE25_d28.tif"

BUDGET = 37654
SPACING_PX = 2.8
SIGMA_PX = 1.5
HALO_PX = 2.0          # prune dots with distance to visible catalogue <= 2 px (exact B2 rule)
SGMC_OFF_PX = 3.0      # off-catalogue proxy: SGMC fault cells > 3 px from mapped catalogue
DOT_RADIUS_PX = 3.0
SEEDS = (101, 202, 303)
NOTE = "H-O2 lidar step_max peaks minus catalogue halo<=2px; research only, not cleared; do not submit"

sha256 = HR1.sha256


def pooled(tp: float, fp: float, fn: float) -> float:
    return float(tp / (tp + M57.ALPHA * fp + M57.BETA * fn + M57.EPS)) if (tp + fp + fn) > 0 else 0.0


def build_surface(foot: np.ndarray) -> dict:
    with rasterio.open(LIDAR) as ds:
        assert ds.count == 12 and ds.descriptions[2] == "step_max" and ds.descriptions[11] == "valid", ds.descriptions
        step = ds.read(3).astype(np.float64)
        valid_code = ds.read(12)
    valid = (valid_code > 0) & foot & np.isfinite(step)
    p98 = float(np.percentile(step[valid], 98))
    m = np.where(valid, np.clip(step / p98, 0.0, 1.0), 0.0)
    s = HR1.smooth_masked(m, valid, SIGMA_PX).astype(np.float64)
    s = s / max(float(s.max()), 1e-12)
    s = np.where(valid, s, 0.0).astype(np.float32)
    return dict(s=s, valid=valid, p98=p98, lidar_valid_footprint_cells=int(valid.sum()))


def halo_of(visible: np.ndarray) -> np.ndarray:
    """Cells within HALO_PX of the visible catalogue (distance-transform rule that reproduces B2 exactly)."""
    return ndi.distance_transform_edt(~visible) <= HALO_PX


def sgmc_proxy(dots: np.ndarray, sgmc_off: np.ndarray) -> dict:
    near_dot = ndi.distance_transform_edt(~dots) <= DOT_RADIUS_PX
    near_sgmc = ndi.distance_transform_edt(~sgmc_off) <= DOT_RADIUS_PX
    n = int(sgmc_off.sum())
    nd = int(dots.sum())
    return dict(
        recall_within_3px=float((near_dot & sgmc_off).sum() / n) if n else None,
        precision_dots_within_3px_of_sgmc_off=float((near_sgmc & dots).sum() / nd) if nd else None,
        dots=nd, sgmc_off_cells=n,
        label="PROXY (USGS SGMC geologic-map fault cells > 3 px from mapped catalogue; owner-derived mirror), not the competition truth",
    )


def main() -> int:
    t0 = datetime.now(timezone.utc)
    grid = G57.load_grid(DATA)
    foot, cat = grid.footprint, grid.catalogue
    ctx = H57.build_holdout(grid)
    cell_keys = [c.key for c in ctx.cells]
    print(f"holdout cells={len(ctx.cells)} withheld={sum(c.n_truth for c in ctx.cells)}", flush=True)

    surf = build_surface(foot)
    s = surf["s"]
    valid = surf["valid"]
    print(f"surface: lidar-valid footprint cells={surf['lidar_valid_footprint_cells']} p98={surf['p98']:.2f}", flush=True)

    # --- Arm A: unpruned, cell-independent emission (identical on every fold)
    dots_A = HR1.place_dots(s, valid, BUDGET, SPACING_PX)
    print(f"arm A dots={int(dots_A.sum())}", flush=True)

    # --- per-fold scoring of arms (pooled sums follow gems57 evaluate exactly)
    def score_arm(per_cell_dots) -> dict:
        tp = fp = fn = 0.0
        n_truth = 0
        per_cell = {}
        halo_removed = []
        for cell in ctx.cells:
            d = per_cell_dots(cell)
            r = H57.score_cell(cell, d)
            tp += r["tp"]; fp += r["fp"]; fn += r["fn"]; n_truth += r["n_truth"]
            per_cell[cell.key] = r["dti"]
        return dict(pooled_dti=pooled(tp, fp, fn), pooled_tp=tp, pooled_fp=fp, pooled_fn=fn,
                    pooled_n_truth=int(n_truth), per_cell_dti=per_cell)

    arm_A = score_arm(lambda c: dots_A)
    # sanity: shared evaluator on the same cell-independent emission must match the per-cell pooling
    ev_A = H57.evaluate(dots_A, ctx)
    assert abs(ev_A["pooled_dti"] - arm_A["pooled_dti"]) < 1e-9, (ev_A["pooled_dti"], arm_A["pooled_dti"])
    print(f"arm A pooled DTI={arm_A['pooled_dti']:.6f} (matches shared evaluate)", flush=True)

    halo_stats = {}

    def arm_B_dots(c):
        vis = cat & ~ctx.hidden_by_cell[c.key]          # visible catalogue only (fold-specific)
        halo = halo_of(vis)
        d = HR1.place_dots(s, valid & ~halo, BUDGET, SPACING_PX)
        halo_stats[c.key] = dict(visible_catalogue=int(vis.sum()), halo_cells_in_footprint=int((halo & foot).sum()),
                                 dots=int(d.sum()), dots_pruned_vs_arm_A=int((dots_A & halo).sum()))
        return d

    arm_B = score_arm(arm_B_dots)
    print(f"arm B (halo-pruned, leak-free per fold) pooled DTI={arm_B['pooled_dti']:.6f}", flush=True)

    # --- matched random controls on the same cells
    foot_idx = np.flatnonzero(valid.ravel())
    rand = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        pick = rng.choice(foot_idx, size=BUDGET, replace=False)
        nd = np.zeros(foot.size, bool)
        nd[pick] = True
        nd = nd.reshape(foot.shape)
        rand.append(score_arm(lambda c, nd=nd: nd))
        print(f"random seed={seed} pooled DTI={rand[-1]['pooled_dti']:.6f}", flush=True)
    rand_pooled_mean = float(np.mean([r["pooled_dti"] for r in rand]))
    rand_cell_mean = np.mean([[r["per_cell_dti"][k] for k in cell_keys] for r in rand], axis=0)

    b_cell = np.array([arm_B["per_cell_dti"][k] for k in cell_keys])
    a_cell = np.array([arm_A["per_cell_dti"][k] for k in cell_keys])
    d_BA = b_cell - a_cell
    d_BA_lo, d_BA_hi = HR1.paired_ci(d_BA)
    d_BR = b_cell - rand_cell_mean
    d_BR_lo, d_BR_hi = HR1.paired_ci(d_BR)

    # --- reference controls on the full grid (not fold-specific)
    refs = {}
    for label, path in (("H-R1 raster (previous holdout reference)", H_R1_RASTER),
                        ("GEMSDOE32 B2 (reference only; built with full-catalogue knowledge)", B2_RASTER),
                        ("GEMSDOE25 d28 parent (reference only; full-catalogue knowledge)", P25_RASTER)):
        with rasterio.open(path) as ds:
            a = np.nan_to_num(ds.read(1), nan=0.0)
        m = (a > 0) & foot
        ev = H57.evaluate(m, ctx)
        refs[label] = dict(path=str(path.relative_to(ROOT)), positives=int(m.sum()), pooled_dti=ev["pooled_dti"],
                           pooled_n_truth=ev["pooled_n_truth"], on_visible_catalogue=ev["on_visible_catalogue"])
        print(f"ref {label}: pooled DTI={ev['pooled_dti']:.6f}", flush=True)
    h_r1_pooled = refs["H-R1 raster (previous holdout reference)"]["pooled_dti"]

    # --- canary: each feature alone, per cell direction-invariant AUC
    def canary() -> dict:
        out = {}
        feats = {"lidar_step_max_surface": lambda c: s,
                 "dist_to_visible_catalogue_px": lambda c: ndi.distance_transform_edt(~(cat & ~ctx.hidden_by_cell[c.key]))}
        for name, fn in feats.items():
            aucs = {}
            for c in ctx.cells:
                arr = fn(c)[c.bbox]
                act = c.active & np.isfinite(arr)
                truth = np.zeros(c.active.shape, bool)
                truth[c.truth_yx] = True
                y = truth[act]
                if y.sum() == 0 or y.sum() == y.size:
                    continue
                auc = float(roc_auc_score(y, arr[act]))
                aucs[c.key] = max(auc, 1.0 - auc)
            vals = list(aucs.values())
            out[name] = dict(cells=len(vals), max_direction_invariant_auc=float(max(vals)) if vals else None,
                             passed=bool(vals and max(vals) < 0.90))
        return out

    can = canary()
    for k, v in can.items():
        print(f"canary {k}: max DI-AUC={v['max_direction_invariant_auc']}", flush=True)

    # --- PROXY: off-catalogue SGMC recall and halo-class precision (no fold leakage: full-grid, proxy truth is off-catalogue)
    with rasterio.open(SGMC) as ds:
        sgmc = (ds.read(1) > 0) & foot
    d_cat = ndi.distance_transform_edt(~cat)
    sgmc_off = sgmc & (d_cat > SGMC_OFF_PX)
    halo_full = halo_of(cat)
    dots_B_full = HR1.place_dots(s, valid & ~halo_full, BUDGET, SPACING_PX)   # the file we would submit
    proxy = dict(
        arm_A_unpruned=sgmc_proxy(dots_A, sgmc_off),
        arm_B_halo_pruned_full_catalogue=sgmc_proxy(dots_B_full, sgmc_off),
        random_seed_101=sgmc_proxy(_random_mask(foot_idx, foot, 101), sgmc_off),
        B2_reference=sgmc_proxy(_read_mask(B2_RASTER, foot), sgmc_off),
    )
    halo_class = dots_A & (d_cat <= HALO_PX)
    rest_class = dots_A & ~(d_cat <= HALO_PX)
    near_off = ndi.distance_transform_edt(~sgmc_off) <= DOT_RADIUS_PX
    proxy["halo_class_precision_within_3px_of_sgmc_off"] = float((near_off & halo_class).sum() / max(int(halo_class.sum()), 1))
    proxy["non_halo_class_precision_within_3px_of_sgmc_off"] = float((near_off & rest_class).sum() / max(int(rest_class.sum()), 1))
    proxy["halo_class_dots_in_arm_A"] = int(halo_class.sum())

    # --- real candidate artefacts (full catalogue, not per-fold): shared writer + validator
    reg = HR1.registry_files()  # before any new file exists in docs/downloads
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    values = dots_B_full.astype(np.float32)
    assert len(NOTE) <= 140
    tif = DOWNLOADS / f"{PREFIX}{NAME}.tif"
    receipt = SW57.write_submission(tif, values, DATA / "sample_submission.tif", foot, note=NOTE, name=NAME,
                                    catalogue=cat, metadata=dict(session=SESSION, hypothesis="H-O2", date=DATE))
    v_zero = validate(tif, foot, cat)
    nan_vals = np.where(foot, values, np.float32("nan")).astype(np.float32)
    nan_path = DOWNLOADS / f"{PREFIX}{NAME_NAN}.tif"
    G57.write_submission(nan_path, nan_vals, mode="nan")
    with rasterio.open(nan_path) as ds:
        a = ds.read(1)
        nan_meta = dict(crs=str(ds.crs), shape=[ds.height, ds.width], dtype=ds.dtypes[0], count=ds.count,
                        transform=list(tuple(ds.transform)[:6]))
    nan_checks = dict(
        single_band=nan_meta["count"] == 1, float32=nan_meta["dtype"] == "float32",
        shape_3730x3292=nan_meta["shape"] == [3730, 3292], crs_32611=nan_meta["crs"] == "EPSG:32611",
        transform_matches=nan_meta["transform"] == list(tuple(G57.TRANSFORM)[:6]),
        nan_exactly_outside_footprint=bool(np.array_equal(np.isnan(a), ~foot)),
        finite_in_footprint_in_0_1=bool(np.isfinite(a[foot]).all() and (a[foot] >= 0).all() and (a[foot] <= 1).all()),
    )
    nan_checks["all_passed"] = all(nan_checks.values())
    zero_catalogue_ok = bool(not np.any((values > 0) & cat))
    halo_ok = bool(not np.any((values > 0) & halo_full))

    # --- literal registry gate: surface (pre-placement) and final dots vs every local TIF
    surf_rows = U57.compare_array_to_registry(s, reg, foot, include_reverse=False)
    dot_rows = U57.compare_array_to_registry(values, reg, foot, file_sha256=sha256(tif))

    def compact(rows: dict) -> list[dict]:
        out = []
        for r in rows.get("rows", []):
            if "error" in r:
                out.append(dict(file=Path(r.get("file", "?")).name, error=str(r["error"])[:200]))
                continue
            out.append(dict(file=Path(r["file"]).name,
                            my_dots_within_3px_of_theirs=r.get("my_dots_within_3px_of_theirs"),
                            their_dots_within_3px_of_mine=r.get("their_dots_within_3px_of_mine"),
                            jaccard_dot_sets=r.get("jaccard_dot_sets"),
                            spearman_full_footprint=r.get("spearman_full_footprint"),
                            their_dots=r.get("their_dots"),
                            their_fraction_of_footprint=(r.get("their_dots") or 0) / max(int(foot.sum()), 1),
                            blanket_or_parent_mask=bool((r.get("their_dots") or 0) > 100000)))
        return out

    def gate(rows: dict) -> dict:
        ok_rows = [r for r in rows.get("rows", []) if "error" not in r]
        top_rho = max(ok_rows, key=lambda r: r.get("spearman_full_footprint") or -2) if ok_rows else {}
        top_ov = max(ok_rows, key=lambda r: r.get("my_dots_within_3px_of_theirs") or -1) if ok_rows else {}
        focus = [r for r in ok_rows if Path(r["file"]).name.startswith("GEMSDOE")]
        return dict(rows_compared=len(ok_rows), errors=len(rows.get("rows", [])) - len(ok_rows),
                    max_spearman=top_rho.get("spearman_full_footprint"), max_spearman_file=top_rho.get("file"),
                    max_my_dots_within_3px=top_ov.get("my_dots_within_3px_of_theirs"), max_overlap_file=top_ov.get("file"),
                    focus_nine_files=len(focus),
                    focus_nine_max_my_dots_within_3px=max((r["my_dots_within_3px_of_theirs"] for r in focus), default=None))

    surf_gate, dot_gate = gate(surf_rows), gate(dot_rows)
    dot_gate["rows"] = compact(dot_rows)
    surf_gate["rows"] = compact(surf_rows)
    dot_gate["rows_failing_0_70_excluding_blankets"] = [r["file"] for r in dot_gate["rows"]
                                                       if (r.get("my_dots_within_3px_of_theirs") or 0) > 0.70 and not r.get("blanket_or_parent_mask")]
    dot_gate["rows_failing_0_70_blanket_only"] = [r["file"] for r in dot_gate["rows"]
                                                 if (r.get("my_dots_within_3px_of_theirs") or 0) > 0.70 and r.get("blanket_or_parent_mask")]
    dot_gate["errored_rows"] = [r for r in dot_gate["rows"] if "error" in r]
    rho_ok = surf_gate["max_spearman"] is not None and surf_gate["max_spearman"] <= 0.90
    ov_ok = dot_gate["max_my_dots_within_3px"] is not None and dot_gate["max_my_dots_within_3px"] <= 0.70

    crit = dict(
        b_beats_unpruned_A=bool(arm_B["pooled_dti"] > arm_A["pooled_dti"]),
        paired_ci_B_minus_A_lower_bound_gt_0=bool(d_BA_lo > 0),
        b_beats_matched_random=bool(arm_B["pooled_dti"] > rand_pooled_mean),
        canary_all_features_below_0_90=all(v["passed"] for v in can.values()),
        validator_passed=bool(v_zero["all_checks_passed"]) and zero_catalogue_ok and halo_ok,
        nan_twin_passed=bool(nan_checks["all_passed"]),
        registry_surface_rho_le_0_90=bool(rho_ok),
        registry_dot_overlap_le_0_70=bool(ov_ok),
        b_beats_h_r1_reference_control=bool(arm_B["pooled_dti"] > h_r1_pooled),
    )
    verdict = "promote-to-selector" if all(crit.values()) else "negative"

    out = dict(
        schema="karage1-exp-o2-v1", session=SESSION, date_utc=DATE,
        started_utc=t0.isoformat(), finished_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis="H-O2: halo-pruned lidar step_max peaks (catalogue halo <= 2 px, per fold, visible only) raise hide-and-recover pooled DTI",
        evaluator=dict(module="vendor/gems57 holdout.build_holdout / score_cell / metric constants (unmodified)",
                       version="gems57-pooled-hide-v2", cells=len(ctx.cells),
                       withheld_positives=int(sum(c.n_truth for c in ctx.cells)),
                       pooling="pooled tp/fp/fn over cells, identical formula to gems57.holdout.evaluate"),
        surface=dict(layer="external/lidar_scarp_features_u8.tif band 3 step_max (USGS 3DEP 1 m, owner-derived)",
                     p98=surf["p98"], lidar_valid_footprint_cells=surf["lidar_valid_footprint_cells"],
                     footprint_cells=int(foot.sum()), sigma_px=SIGMA_PX, spacing_px=SPACING_PX, budget=BUDGET),
        holdout_DTI=dict(
            label="HOLDOUT-DTI", evaluator="gems57-pooled-hide-v2", withheld_positives=int(sum(c.n_truth for c in ctx.cells)),
            arm_A_unpruned=dict(pooled_dti=arm_A["pooled_dti"]),
            arm_B_halo_pruned=dict(pooled_dti=arm_B["pooled_dti"],
                                   ci95_paired_B_minus_A=[d_BA_lo, d_BA_hi], mean_delta_B_minus_A=float(d_BA.mean())),
            random_matched_mean=dict(pooled_dti=rand_pooled_mean, per_seed=[r["pooled_dti"] for r in rand],
                                     ci95_paired_B_minus_random=[d_BR_lo, d_BR_hi], mean_delta_B_minus_random=float(d_BR.mean())),
            reference_controls_full_grid=refs,
            per_cell_B=arm_B["per_cell_dti"], per_cell_A=arm_A["per_cell_dti"],
            halo_per_cell=halo_stats,
        ),
        canary=can,
        proxy_PROXY_only=proxy,
        submission=dict(
            name=NAME, note=NOTE, file=str(tif.relative_to(ROOT)), zip=str(tif.with_suffix(".zip").relative_to(ROOT)),
            nan_twin=str(nan_path.relative_to(ROOT)), dots=int(values.sum()),
            dots_within_2px_of_catalogue=int((values.astype(bool) & halo_full).sum()),
            sha256_tif=sha256(tif), sha256_nan_twin=sha256(nan_path), writer_receipt=receipt,
        ),
        validator=dict(zeros_outside_primary=v_zero, nan_twin_checks=nan_checks, catalogue_zero=zero_catalogue_ok,
                       halo_zero=halo_ok),
        registry_gate=dict(surface_vs_every_local_tif=surf_gate, dots_vs_every_local_tif=dot_gate,
                           local_tif_count=len(reg)),
        criteria=crit,
        verdict=verdict,
        ok_to_submit=False,
        ok_to_submit_reason="Not cleared: promote-to-selector is not a slot decision; the holdout measures recovery of withheld "
                            "catalogue segments, while the official initial round scores non-catalogue faults (IR-H1). Owner decision required.",
    )
    EVIDENCE.write_text(json.dumps(out, indent=2, default=float) + "\n", encoding="utf-8")

    card = dict(
        schema="karage1-run-card-v1", session=SESSION, date=DATE,
        hypothesis=out["hypothesis"],
        mechanism="Lidar scarp crests (USGS 3DEP step_max) give dots; dots within 2 px of the visible catalogue are removed per fold, "
                  "so emitted dots sit where a new (non-catalogue) fault would have to be.",
        named_non_fault_mimic="Multi-strand fault zones: unmapped strands sit within 2 px of mapped ones (the GPC-Z mechanism). "
                              "Pruning those would delete real strands. Also fan-head and terrace edges mimic step_max.",
        holdout_dti=dict(label="HOLDOUT-DTI", evaluator="gems57-pooled-hide-v2",
                         withheld_positives=out["evaluator"]["withheld_positives"],
                         arm_B_pooled=arm_B["pooled_dti"], arm_A_pooled=arm_A["pooled_dti"],
                         random_pooled=rand_pooled_mean,
                         ci95_B_minus_A=[d_BA_lo, d_BA_hi],
                         ci95_note="paired bootstrap over the 16 holdout cells (HR1.paired_ci)"),
        correlation_overlap_vs_registry=dict(surface_max_spearman=surf_gate["max_spearman"],
                                             dot_max_forward_overlap_3px=dot_gate["max_my_dots_within_3px"],
                                             focus_nine_max_forward_overlap=dot_gate["focus_nine_max_my_dots_within_3px"],
                                             local_tif_count=len(reg)),
        raster_sha256=out["submission"]["sha256_tif"],
        validator_output=dict(all_checks_passed=bool(v_zero["all_checks_passed"]), catalogue_zero=zero_catalogue_ok,
                              halo_zero=halo_ok, nan_twin_all_passed=bool(nan_checks["all_passed"])),
        submission_name=NAME, submission_note=NOTE, submission_note_chars=len(NOTE),
        verdict=verdict, ok_to_submit=False, criteria=crit,
    )
    RUN_CARD.write_text(json.dumps(card, indent=2, default=float) + "\n", encoding="utf-8")
    print(json.dumps(dict(verdict=verdict, criteria=crit), indent=2))
    print("wrote", EVIDENCE.relative_to(ROOT), RUN_CARD.relative_to(ROOT))
    return 0


def _read_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = np.nan_to_num(ds.read(1), nan=0.0)
    return (a > 0) & foot


def _random_mask(foot_idx: np.ndarray, foot: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    m = np.zeros(foot.size, bool)
    m[rng.choice(foot_idx, size=BUDGET, replace=False)] = True
    return m.reshape(foot.shape)


if __name__ == "__main__":
    raise SystemExit(main())
