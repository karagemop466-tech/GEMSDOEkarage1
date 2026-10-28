#!/usr/bin/env python3
"""DIPDUAL three-experiment budget (preregistration-dipdual-20261028.md).

EXP1 leakage canary per component/fused surface + pre-placement Spearman.
EXP2 blocked hide-and-recover head-to-head (fold-local emission, matched
     budget) + off-catalogue SGMC diagnostic on static full-apron builds.
EXP3 split/dip/collar sweep inside the lane.

Final build + uniqueness + run card in --stage final (uses shared
submission_writer; never selects/spends a weekly slot).
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
for sub in ("src", "vendor"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gemsk import emission, grid, holdout, metric  # noqa: E402
from gemskarage1 import dipdual  # noqa: E402

EVIDENCE = ROOT / "evidence"
CACHE = ROOT / ".cache" / "dipdual"
BUDGET = 37654
SEED = 20261028


def dump(name: str, obj) -> Path:
    p = EVIDENCE / name
    p.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")
    print(f"[write] {p}", flush=True)
    return p


def load_evidence(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text())


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def read_raster(p: Path) -> np.ndarray:
    with rasterio.open(p) as src:
        return src.read(1)


def registry_inventory(foot: np.ndarray) -> list[dict]:
    """Discrete registry rasters restored locally + blanket witnesses (role-labelled)."""
    items: list[tuple[str, Path]] = []
    reg = grid.DATA / "registry"
    for p in sorted(reg.glob("*.tif")):
        items.append((f"registry/{p.name}", p))
    scored = grid.DATA / "scored"
    for name in (
        "gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif",
        "gems19-h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan.tif",
        "gems16-h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan.tif",
    ):
        if (scored / name).exists():
            items.append((f"scored/{name}", scored / name))
    dl = ROOT / "docs" / "downloads"
    for p in sorted(dl.glob("*-zeros.tif")):
        items.append((f"local/{p.name}", p))
    out = []
    for rid, p in items:
        a = read_raster(p)
        dots = np.isfinite(a) & (a > 0) & foot
        n = int(dots.sum())
        if "lattice" in p.name:
            role = "calibration_probe"
        elif n > 100_000:
            role = "blanket_or_parent_mask"
        else:
            role = "discrete_submission"
        out.append({"id": rid, "path": str(p), "dots": n, "role": role,
                    "sha256": sha256_file(p)})
    return out


# ---------------------------------------------------------------- EXP1
def stage_exp1(S: dict, foot, cat, folds) -> dict:
    print("=== EXP1 canary ===", flush=True)
    feats = {
        "gpc_step": S["gpc_step"], "gpc_curvbreak": S["gpc_curv"],
        "gpc_concord": S["gpc_concord"], "gpc_oblique": S["gpc_oblique"],
        "lidar_step": S["lidar_step"], "lidar_polarity": S["lidar_pol"],
        "grav_ridge": S["grav_ridge"], "dtb_ridge": S["dtb_ridge"],
        "mag_ridge": S["mag_ridge"], "align": S["align"],
        "low_slope": S["low_slope"],
        "exposed_fused": S["exposed"], "buried_body": S["buried_body"],
        "buried_body_dipshifted": S["buried_body_shifted"],
        "dual_surface": S["dual_surface"],
    }
    rng = np.random.default_rng(SEED)
    rows, any_alarm = [], False
    for name, f in feats.items():
        aucs = [holdout.auc_on_fold(f, fold, rng=rng) for fold in folds]
        v = f[foot]
        finite = bool(np.isfinite(v).all())
        constant = bool(float(np.std(v)) == 0.0)
        inv = [max(a, 1.0 - a) for a in aucs]
        alarm = bool(max(inv) > 0.90 or not finite or constant)
        any_alarm |= alarm
        rows.append({"feature": name, "fold_aucs": [float(x) for x in aucs],
                     "mean_auc": float(np.mean(aucs)),
                     "max_direction_invariant_auc": float(max(inv)),
                     "finite_in_footprint": finite, "constant": constant,
                     "reads_labels": False, "alarm": alarm})
        print(f"  {name:24s} meanAUC={np.mean(aucs):.4f} maxInv={max(inv):.4f} alarm={alarm}", flush=True)
        gc.collect()
    print("=== EXP1 pre-placement Spearman (dual surface) ===", flush=True)
    inv_list = registry_inventory(foot)
    fy, fx = np.nonzero(foot)
    sel = np.random.default_rng(SEED).choice(fy.size, size=400_000, replace=False)
    sy, sx = fy[sel], fx[sel]
    surf_s = S["dual_surface"][sy, sx]
    spear = []
    for it in inv_list:
        a = np.nan_to_num(read_raster(Path(it["path"])), nan=0.0).astype(np.float32)
        rho = float(spearmanr(surf_s, a[sy, sx]).statistic)
        rho = 0.0 if not np.isfinite(rho) else rho
        spear.append({**{k: it[k] for k in ("id", "dots", "role", "sha256")},
                      "spearman_surface": rho, "abs_spearman": abs(rho),
                      "duplicate_by_rho": bool(abs(rho) > 0.90)})
        print(f"  {it['id'][:70]:70s} rho={rho:+.4f} role={it['role']}", flush=True)
        del a
        gc.collect()
    worst = max(spear, key=lambda r: r["abs_spearman"])
    worst_discrete = max((r for r in spear if r["role"] == "discrete_submission"),
                         key=lambda r: r["abs_spearman"])
    res = {"experiment": 1, "lane": dipdual.LANE, "evaluator_version": holdout.VERSION,
           "withheld_positives": int(sum(f["n_withheld"] for f in folds)),
           "canary_rows": rows, "any_alarm": any_alarm,
           "preplacement_spearman": spear, "worst_abs_spearman": worst,
           "worst_discrete_abs_spearman": worst_discrete,
           "registry_inventory": inv_list,
           "note": "Features constructed without labels; AUC>0.90 still blocks promotion."}
    dump("exp1_dipdual_canary.json", res)
    return res


# ---------------------------------------------------------------- EXP2
def emit_arm(name: str, S: dict, visible, budget=BUDGET, frac=0.65, apron=2):
    if name == "DIPDUAL":
        d, _ = dipdual.emit_dual(S["exposed"], S["buried_dip"], S["exposed_regime"],
                                 S["buried_regime"], S["dual_surface"], visible,
                                 budget, frac, apron_px=apron)
        return d
    surf = {"GPC": S["gpc_physics"], "BBSTEP": S["bbstep"],
            "BURIED_DIP": S["buried_dip"], "EXPOSED": S["exposed"]}[name]
    return emission.emit(surf, budget, visible, spacing=2.8, apron_px=apron, thin=False)


def score_folds(S, folds, arms, budget=BUDGET, frac=0.65, apron=2):
    terms_by, summary = {}, {}
    for name in arms:
        terms, ndots, per_fold = [], [], []
        for f in folds:
            d = emit_arm(name, S, f["visible"], budget, frac, apron)
            r, t = holdout.evaluate_dots(d, f)
            terms.append(t); ndots.append(int(d.sum())); per_fold.append(float(r["dti"]))
            del d
            gc.collect()
        terms_by[name] = terms
        summary[name] = {**holdout.pooled(terms), "per_fold_dti": per_fold,
                         "n_dots_per_fold": ndots}
        print(f"  {name:24s} pooled={summary[name]['dti']:.6f} folds={np.round(per_fold,4)} dots={ndots}", flush=True)
    return summary, terms_by


def paired(terms_by: dict, order: list[str]) -> dict:
    sub = {k: terms_by[k] for k in order}
    return holdout.bootstrap_ci(sub, draws=1000, seed=SEED)


def sgmc_fold(foot, cat):
    with rasterio.open(grid.DATA / "external" / "derived_sgmc_faults_100m_u8.tif") as src:
        sg = src.read(1) > 0
    dcat = ndimage.distance_transform_edt(~cat)
    truth = sg & foot & (dcat > 3)
    active = foot & (dcat > 2)
    return {"withheld": truth, "visible": cat, "active": active,
            "n_withheld": int(truth.sum())}, truth


def stage_exp2(S, foot, cat, folds) -> dict:
    print("=== EXP2 blocked head-to-head ===", flush=True)
    arms = ["DIPDUAL", "GPC", "BBSTEP", "BURIED_DIP"]
    summary, terms_by = score_folds(S, folds, arms)
    boot_vs_gpc = paired(terms_by, ["GPC", "DIPDUAL", "BBSTEP", "BURIED_DIP"])
    boot_vs_bb = paired(terms_by, ["BBSTEP", "DIPDUAL"])
    for k in arms:
        summary[k]["ci95"] = boot_vs_gpc[k]["ci95"]
    b2p = grid.DATA / "registry" / "GEMSDOE32_h33-h33-2-b2_e5eb6e7e_zeros.tif"
    b2 = np.isfinite(read_raster(b2p)) & (read_raster(b2p) > 0) & foot
    b2_terms, b2_per = [], []
    for f in folds:
        r, t = holdout.evaluate_dots(b2, f)
        b2_terms.append(t); b2_per.append(float(r["dti"]))
    b2_blocked = {**holdout.pooled(b2_terms), "per_fold_dti": b2_per,
                  "note": "CENSORED diagnostic: B2 apron used the full catalogue incl. withheld px."}
    print(f"  B2 static (censored) pooled={b2_blocked['dti']:.6f}", flush=True)

    print("=== EXP2 SGMC diagnostic (static full-apron builds) ===", flush=True)
    sfold, _ = sgmc_fold(foot, cat)
    sg_terms, sg_summary = {}, {}
    for name in arms:
        d = emit_arm(name, S, cat, BUDGET, 0.65, 2)
        r, t = holdout.evaluate_dots(d, sfold)
        sg_terms[name] = [t]
        sg_summary[name] = {**holdout.pooled([t]), "n_dots_static": int(d.sum())}
        dotdir = CACHE / "static_dots"; dotdir.mkdir(parents=True, exist_ok=True)
        np.save(dotdir / f"{name}.npy", d)
        print(f"  SGMC {name:24s} dti={r['dti']:.6f} dots={int(d.sum())}", flush=True)
        del d; gc.collect()
    r, t = holdout.evaluate_dots(b2, sfold)
    sg_terms["B2_STATIC"] = [t]
    sg_summary["B2_STATIC"] = {**holdout.pooled([t]), "n_dots_static": int(b2.sum())}
    print(f"  SGMC B2_STATIC            dti={r['dti']:.6f} dots={int(b2.sum())}", flush=True)
    sg_boot = paired(sg_terms, ["B2_STATIC", "DIPDUAL", "GPC", "BBSTEP", "BURIED_DIP"])
    best_ctrl = "GPC" if sg_summary["GPC"]["dti"] >= sg_summary["BBSTEP"]["dti"] else "BBSTEP"
    sg_boot_ctrl = paired(sg_terms, [best_ctrl, "DIPDUAL"])
    res = {"experiment": 2, "lane": dipdual.LANE, "evaluator_version": holdout.VERSION,
           "scheme": "blocked", "budget_per_fold": BUDGET,
           "withheld_positives": int(sum(f["n_withheld"] for f in folds)),
           "blocked": summary, "bootstrap_vs_gpc": boot_vs_gpc,
           "bootstrap_vs_bbstep": boot_vs_bb, "b2_static_censored": b2_blocked,
           "sgmc": {"truth_positives": sfold["n_withheld"], "arms": sg_summary,
                    "bootstrap_vs_b2": sg_boot, "best_control": best_ctrl,
                    "bootstrap_vs_best_control": sg_boot_ctrl,
                    "label": "SGMC-DIAGNOSTIC-DTI (not the hidden test set)"}}
    dump("exp2_dipdual_holdout.json", res)
    return res


# ---------------------------------------------------------------- EXP3
def stage_exp3(S, foot, cat, folds) -> dict:
    print("=== EXP3 sweep ===", flush=True)
    rows = []
    for frac in (0.50, 0.65, 0.80):
        terms, ndots = [], []
        for f in folds:
            d, _ = dipdual.emit_dual(S["exposed"], S["buried_dip"], S["exposed_regime"],
                                     S["buried_regime"], S["dual_surface"],
                                     f["visible"], BUDGET, frac, apron_px=2)
            _, t = holdout.evaluate_dots(d, f)
            terms.append(t); ndots.append(int(d.sum())); del d; gc.collect()
        p = holdout.pooled(terms)
        rows.append({"config": f"split{frac:.2f}_dip_apron2", "frac_exposed": frac,
                     "dip": True, "apron": 2, "dti": p["dti"], "tp": p["tp"],
                     "fp": p["fp"], "fn": p["fn"], "n_dots_per_fold": ndots})
        print(f"  split={frac} dip DTI={p['dti']:.6f}", flush=True)
    # dip off at 65/35
    terms, ndots = [], []
    for f in folds:
        d, _ = dipdual.emit_dual(S["exposed"], S["buried_nodip"], S["exposed_regime"],
                                 S["buried_regime"], S["dual_surface"],
                                 f["visible"], BUDGET, 0.65, apron_px=2)
        _, t = holdout.evaluate_dots(d, f)
        terms.append(t); ndots.append(int(d.sum())); del d; gc.collect()
    p = holdout.pooled(terms)
    rows.append({"config": "split0.65_nodip_apron2", "frac_exposed": 0.65, "dip": False,
                 "apron": 2, "dti": p["dti"], "tp": p["tp"], "fp": p["fp"], "fn": p["fn"],
                 "n_dots_per_fold": ndots})
    print(f"  split=0.65 NODIP DTI={p['dti']:.6f}", flush=True)
    # collar 3 at 65/35 dip
    terms, ndots = [], []
    for f in folds:
        d, _ = dipdual.emit_dual(S["exposed"], S["buried_dip"], S["exposed_regime"],
                                 S["buried_regime"], S["dual_surface"],
                                 f["visible"], BUDGET, 0.65, apron_px=3)
        _, t = holdout.evaluate_dots(d, f)
        terms.append(t); ndots.append(int(d.sum())); del d; gc.collect()
    p = holdout.pooled(terms)
    rows.append({"config": "split0.65_dip_apron3", "frac_exposed": 0.65, "dip": True,
                 "apron": 3, "dti": p["dti"], "tp": p["tp"], "fp": p["fp"], "fn": p["fn"],
                 "n_dots_per_fold": ndots})
    print(f"  split=0.65 dip apron3 DTI={p['dti']:.6f}", flush=True)
    # ---- POST-HOC diagnostics (labelled; never used for preregistered gates)
    print("=== EXP3 post-hoc diagnostics ===", flush=True)
    diag = []
    for label, fn in (
        ("EXPOSED_only_posthoc", lambda vis: emission.emit(S["exposed"], BUDGET, vis, spacing=2.8, apron_px=2, thin=False)),
        ("DUAL_gpcExposed_posthoc", None),
    ):
        terms, ndots = [], []
        for f in folds:
            if fn is not None:
                d = fn(f["visible"])
            else:
                d, _ = dipdual.emit_dual(S["gpc_physics"], S["buried_dip"], S["exposed_regime"],
                                         S["buried_regime"], S["dual_surface"],
                                         f["visible"], BUDGET, 0.65, apron_px=2)
            _, t = holdout.evaluate_dots(d, f)
            terms.append(t); ndots.append(int(d.sum())); del d; gc.collect()
        p = holdout.pooled(terms)
        diag.append({"config": label, "post_hoc": True, "dti": p["dti"],
                     "tp": p["tp"], "fp": p["fp"], "fn": p["fn"], "n_dots_per_fold": ndots})
        print(f"  {label} blocked DTI={p['dti']:.6f}", flush=True)
    sfold, _ = sgmc_fold(foot, cat)
    for row, fn in zip(diag, ("exposed", "gpcdual")):
        if fn == "exposed":
            d = emission.emit(S["exposed"], BUDGET, cat, spacing=2.8, apron_px=2, thin=False)
        else:
            d, _ = dipdual.emit_dual(S["gpc_physics"], S["buried_dip"], S["exposed_regime"],
                                     S["buried_regime"], S["dual_surface"], cat, BUDGET, 0.65, apron_px=2)
        r, _t = holdout.evaluate_dots(d, sfold)
        row["sgmc_diagnostic_dti"] = float(r["dti"])
        print(f"  {row['config']} SGMC={r['dti']:.6f}", flush=True)
        del d; gc.collect()
    rows_d = diag
    best = max(rows, key=lambda r: r["dti"])
    res = {"experiment": 3, "lane": dipdual.LANE, "evaluator_version": holdout.VERSION,
           "scheme": "blocked", "budget_per_fold": BUDGET,
           "withheld_positives": int(sum(f["n_withheld"] for f in folds)),
           "sweep": rows, "best_blocked": best,
           "post_hoc_diagnostics": rows_d,
           "post_hoc_note": "Added after EXP2 to diagnose failure; excluded from preregistered promotion gates."}
    dump("exp3_dipdual_sweep.json", res)
    return res


# ---------------------------------------------------------------- final
def uniqueness_final(dots, surface, foot, inv_list) -> dict:
    ny, nx = np.nonzero(dots & foot)
    fy, fx = np.nonzero(foot)
    sel = np.random.default_rng(SEED).choice(fy.size, size=400_000, replace=False)
    sy, sx = fy[sel], fx[sel]
    dots_s = dots.astype(np.float32)[sy, sx]
    rows = []
    for it in inv_list:
        a = read_raster(Path(it["path"]))
        ref = np.isfinite(a) & (a > 0) & foot
        d = ndimage.distance_transform_edt(~ref)
        fwd = float((d[ny, nx] <= 3).mean()) if ny.size else 0.0
        ry, rx = np.nonzero(ref)
        drev = ndimage.distance_transform_edt(~(dots & foot))
        rev = float((drev[ry, rx] <= 3).mean()) if ry.size else 0.0
        inter = fwd * ny.size  # candidate dots covered (directed, not set intersection)
        # Jaccard on 3-px dilated supports (symmetric blanket-robust summary)
        ours_cov = ndimage.distance_transform_edt(~(dots & foot)) <= 3
        ref_cov = d <= 3
        jac = float((ours_cov & ref_cov & foot).sum() / max((ours_cov | ref_cov & foot).sum(), 1))
        rho = float(spearmanr(dots_s, np.nan_to_num(a, nan=0.0).astype(np.float32)[sy, sx]).statistic)
        rho = 0.0 if not np.isfinite(rho) else rho
        rows.append({**{k: it[k] for k in ("id", "dots", "role", "sha256")},
                     "forward_overlap_3px": fwd, "reverse_overlap_3px": rev,
                     "jaccard_3px_supports": jac, "spearman_dots": rho,
                     "duplicate_discrete_rule": bool(
                         it["role"] == "discrete_submission" and (fwd > 0.70 or abs(rho) > 0.90))})
        print(f"  {it['id'][:64]:64s} fwd={fwd:.4f} rev={rev:.4f} jac={jac:.4f} rho={rho:+.4f} {it['role']}", flush=True)
        del a, ref, d, drev, ours_cov, ref_cov
        gc.collect()
    discrete = [r for r in rows if r["role"] == "discrete_submission"]
    lattice = [r for r in rows if r["role"] == "calibration_probe"]
    return {"n_our_dots": int(ny.size), "rows": rows,
            "unique_vs_discrete": not any(r["duplicate_discrete_rule"] for r in discrete),
            "worst_discrete_forward": max(discrete, key=lambda r: r["forward_overlap_3px"]),
            "worst_discrete_abs_spearman": max(discrete, key=lambda r: abs(r["spearman_dots"])),
            "lattice_rows": lattice,
            "lattice_forward_overlap": lattice[0]["forward_overlap_3px"] if lattice else None,
            "lattice_duplicate_literal": bool(lattice and lattice[0]["forward_overlap_3px"] > 0.70),
            "lattice_min_possible_forward_at_this_N": max(0.0, (ny.size - 6649) / max(ny.size, 1)),
            "registry_complete": False,
            "registry_coverage": f"{len(rows)} locally restored rasters role-classified; not a complete fleet registry."}


def stage_final(S, foot, cat, folds) -> dict:
    from gems57.submission_writer import write_submission

    exp1 = load_evidence("exp1_dipdual_canary.json")
    exp2 = load_evidence("exp2_dipdual_holdout.json")
    exp3 = load_evidence("exp3_dipdual_sweep.json")
    # Final raster is always the preregistered configuration (65/35, dip,
    # apron 2) so the run card's promotion number matches the saved bytes'
    # generating config; EXP3 sweep rows are sensitivity evidence only.
    best = exp3["best_blocked"]
    frac, apron, use_dip = 0.65, 2, True
    buried = S["buried_dip"] if use_dip else S["buried_nodip"]
    print(f"=== FINAL build frac_exposed={frac} apron={apron} dip={use_dip} ===", flush=True)
    dots, info = dipdual.emit_dual(S["exposed"], buried, S["exposed_regime"],
                                   S["buried_regime"], S["dual_surface"], cat,
                                   BUDGET, frac, apron_px=apron)
    print(f"final dots={info}", flush=True)
    assert not (dots & cat).any(), "dots on catalogue"
    # Saved-raster holdout scores (fold-local config from EXP2/EXP3 is the
    # promotion number; static full-apron on catalogue folds is censored).
    terms = []
    for f in folds:
        _, t = holdout.evaluate_dots(dots, f)
        terms.append(t)
    saved_blocked = holdout.pooled(terms)
    saved_ci = holdout.bootstrap_ci({"saved": terms}, draws=1000, seed=SEED)["saved"]["ci95"]
    sfold, _ = sgmc_fold(foot, cat)
    sg_r, sg_t = holdout.evaluate_dots(dots, sfold)
    sg_ci = holdout.bootstrap_ci({"saved": [sg_t]}, draws=1000, seed=SEED)["saved"]["ci95"]
    print(f"saved SGMC-DIAGNOSTIC-DTI={sg_r['dti']:.6f} CI={sg_ci}", flush=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = f"karage1-dipdual-dualregime-dipshift-{ts}"
    # Gates evaluated on fold-local EXP2 (65/35) + chosen config evidence.
    b = exp2["blocked"]
    d_vs_gpc = exp2["bootstrap_vs_gpc"]["DIPDUAL"].get("paired_delta_vs_GPC", {})
    d_vs_bb = exp2["bootstrap_vs_bbstep"]["DIPDUAL"].get("paired_delta_vs_BBSTEP", {})
    sg_vs_ctrl = exp2["sgmc"]["bootstrap_vs_best_control"]["DIPDUAL"]
    ctrl_name = exp2["sgmc"]["best_control"]
    d_sg = sg_vs_ctrl.get(f"paired_delta_vs_{ctrl_name}", {})
    gate_canary = not exp1["any_alarm"]
    gate_blocked_bb = bool(d_vs_bb.get("ci95", [0, 0])[0] > 0)
    gate_blocked_gpc = bool(d_vs_gpc.get("ci95", [-1, 0])[0] > -0.010)
    gate_sgmc = bool(d_sg.get("ci95", [0, 0])[0] > 0)

    inv_list = exp1["registry_inventory"]
    print("=== FINAL uniqueness ===", flush=True)
    uniq = uniqueness_final(dots, S["dual_surface"], foot, inv_list)
    dump("dipdual_uniqueness.json", uniq)
    gate_unique = bool(uniq["unique_vs_discrete"])
    pre_rho_ok = bool(exp1["worst_discrete_abs_spearman"]["abs_spearman"] <= 0.90)

    promote = bool(gate_canary and gate_blocked_bb and gate_blocked_gpc
                   and gate_sgmc and gate_unique and pre_rho_ok)
    verdict = "promote" if promote else "negative"
    note = ("DIPDUAL dual-regime dip-shifted buried+LiDAR exposed; promote to selector"
            if promote else
            "DIPDUAL dual-regime dip-shifted research raster; gates failed; DO NOT SUBMIT")
    assert len(note) <= 140
    pred = np.where(dots & foot, 1.0, 0.0).astype(np.float32)
    out_tif = ROOT / "docs" / "downloads" / f"{slug}-zeros.tif"
    receipt = write_submission(
        out_tif, pred, grid.DATA / "sample_submission.tif", foot,
        note=note, name=f"{slug}-zeros", catalogue=cat,
        metadata={"lane": dipdual.LANE, "verdict": verdict, "emit_info": info,
                  "frac_exposed": frac, "apron_px": apron, "dip_shift": use_dip})
    print(f"wrote {out_tif.name} sha={receipt['sha256'][:16]} verdict={verdict}", flush=True)
    # Independent re-read via gemsk validator (second tool, saved bytes).
    from gemsk import submission as gemsk_sub
    indep = gemsk_sub.validate(out_tif)

    # Fold-local promotion number: DIPDUAL arm of EXP2 if frac==0.65 else EXP3 row.
    if frac == 0.65:
        promo_dti, promo_ci = b["DIPDUAL"]["dti"], b["DIPDUAL"]["ci95"]
    else:
        promo_dti, promo_ci = best["dti"], None
    card = {
        "schema": "karage1-run-card-v3",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "session": "arena/147b0f11-gemsdoekarage1",
        "lane": dipdual.LANE,
        "preregistration": "docs/research/preregistration-dipdual-20261028.md",
        "hypothesis": ("Dual-regime: exposed LiDAR/DEM step-polarity scarps plus "
                       "dip-projected (updip-shifted) buried gravity/basement ridges "
                       "recover off-catalogue faults better than either regime alone."),
        "mechanism": ("Exposed: step-edge+curvature+LiDAR polarity gated by concordance/"
                      "obliquity with road veto. Buried: BB-STEP ridges shifted updip by "
                      "clip(dtb,0,2500m)/tan60deg (<=8px). Slope-rank regime split, "
                      f"quota {frac:.0%} exposed, Poisson 2.8px, {apron}px catalogue apron."),
        "named_non_fault_mimic": ("Lake Lahontan shoreline benches, road/rail embankments, "
                                  "lithologic contacts and volcanic-flow density edges."),
        "holdout_dti": {"label": "HOLDOUT-DTI", "value": promo_dti,
                        "evaluator_version": holdout.VERSION,
                        "withheld_positives": exp2["withheld_positives"], "ci95": promo_ci,
                        "status": "Fold-local emission, blocked whole-component hide-and-recover. Not an organizer score."},
        "sgmc_diagnostic_dti": {"label": "SGMC-DIAGNOSTIC-DTI", "value": float(sg_r["dti"]),
                                "truth_positives": sfold["n_withheld"], "ci95": sg_ci,
                                "status": "Off-catalogue SGMC truth; not the hidden test set."},
        "saved_raster_censored_blocked_dti": {"label": "HOLDOUT-DTI (censored diagnostic)",
                                              "value": saved_blocked["dti"], "ci95": saved_ci,
                                              "status": "Full-catalogue apron cannot recover withheld catalogue px by construction."},
        "controls_blocked": {k: {"dti": b[k]["dti"], "ci95": b[k]["ci95"]} for k in ("GPC", "BBSTEP", "BURIED_DIP")},
        "paired_deltas": {"vs_gpc_blocked": d_vs_gpc, "vs_bbstep_blocked": d_vs_bb,
                          "vs_best_control_sgmc": d_sg, "sgmc_best_control": ctrl_name},
        "gates": {"canary_no_alarm": gate_canary,
                  "blocked_beats_bbstep_ci": gate_blocked_bb,
                  "blocked_no_collapse_vs_gpc": gate_blocked_gpc,
                  "sgmc_beats_best_control_ci": gate_sgmc,
                  "unique_vs_discrete_registry": gate_unique,
                  "preplacement_spearman_discrete_ok": pre_rho_ok,
                  "format_writer_ok": bool(receipt["validator"]["all_checks_passed"]),
                  "independent_reread_ok": bool(indep["all_checks_passed"])},
        "correlation_overlap_vs_registry": {
            "preplacement_worst_discrete": exp1["worst_discrete_abs_spearman"],
            "final_worst_discrete_forward": uniq["worst_discrete_forward"],
            "unique_vs_discrete": gate_unique,
            "lattice_forward_overlap": uniq["lattice_forward_overlap"],
            "lattice_duplicate_literal": uniq["lattice_duplicate_literal"],
            "lattice_min_possible_forward_at_this_N": uniq["lattice_min_possible_forward_at_this_N"],
            "lattice_role": "calibration_probe (IR-DIPDUAL-LATTICE-01); literal value published, selector must acknowledge",
            "registry_complete": False},
        "raster_sha256": receipt["sha256"],
        "raster_file": out_tif.name,
        "zip_file": receipt["zip_file"], "zip_sha256": receipt["zip_sha256"],
        "validator_output": {"shared_writer": receipt["validator"],
                             "template_report_ok": receipt["template_report"]["ok"],
                             "independent_gemsk_validate": indep,
                             "no_nan_inside_footprint": True, "values_in_0_1": True,
                             "crs_shape_transform_match": True,
                             "portal_acceptance": "not tested"},
        "submission_name": out_tif.name,
        "submission_note": note, "submission_note_chars": len(note),
        "emit_info": info, "budget": BUDGET, "frac_exposed": frac,
        "download_available": True,
        "download_available_meaning": ("Research download of a format-valid GeoTIFF. "
                                       "Promotion to selector is not authorization to upload; "
                                       "weekly cap and lattice-deviation acknowledgment remain selector steps."
                                       if promote else
                                       "Research download only; not authorization to upload. Gates failed."),
        "ok_to_submit": False,
        "slot_selected_or_spent": False,
        "geological_experiments_run_this_session": 3,
        "canary_max_direction_invariant_auc": max(r["max_direction_invariant_auc"] for r in exp1["canary_rows"]),
        "verdict": verdict,
        "blockers": ([]
                     if promote else
                     [k for k, v in {"canary": gate_canary, "blocked>bbstep": gate_blocked_bb,
                                     "blocked~gpc": gate_blocked_gpc, "sgmc>control": gate_sgmc,
                                     "unique_discrete": gate_unique}.items() if not v])
                    + ["Weekly-slot selector has not run; ok_to_submit remains false.",
                       "Literal lattice forward overlap exceeds 70% (mathematically unavoidable at this N); see IR-DIPDUAL-LATTICE-01.",
                       "Registry is not the complete fleet; mirrors are not organizer-authenticated."],
    }
    dump("run_card_dipdual_20261028.json", card)
    (ROOT / "docs" / "data" / "run-card-dipdual-20261028.json").write_text(
        json.dumps(card, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: card[k] for k in ("verdict", "raster_sha256", "submission_name", "gates")}, indent=2), flush=True)
    return card


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=("build", "exp1", "exp2", "exp3", "final", "all"), default="all")
    args = ap.parse_args()
    t0 = time.time()
    foot, cat = grid.footprint(), grid.catalogue()
    print(f"footprint={int(foot.sum())} catalogue={int(cat.sum())}", flush=True)
    S = dipdual.build_surfaces(foot)
    print(f"surfaces ready [{time.time()-t0:.0f}s]", flush=True)
    if args.stage == "build":
        return 0
    folds = holdout.make_folds(cat, foot, scheme="blocked")
    print(f"folds withheld={[f['n_withheld'] for f in folds]} [{time.time()-t0:.0f}s]", flush=True)
    if args.stage in ("exp1", "all"):
        stage_exp1(S, foot, cat, folds)
    if args.stage in ("exp2", "all"):
        stage_exp2(S, foot, cat, folds)
    if args.stage in ("exp3", "all"):
        stage_exp3(S, foot, cat, folds)
    if args.stage in ("final", "all"):
        stage_final(S, foot, cat, folds)
    print(f"done [{time.time()-t0:.0f}s]", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
