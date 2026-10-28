#!/usr/bin/env python3
"""Master H-K1-1 (HMAS-SINTER-ENV) 3-Experiment Pipeline, Full-Fleet Uniqueness Gate & Run Card Generator."""
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from numpy.lib.format import open_memmap

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57 import evaluate_holdout as eh57
from gems57.submission_writer import write_submission
from gemskarage1.emitter import compute_spatial_forensics, emit_submodular_300m
from gemskarage1.features import build_feature_stack
from gemskarage1.holdout_eval import (
    build_hr3_draws,
    compose_arm_surface,
    evaluate_gems57_holdout_suite,
    evaluate_hr3_per_cell,
    evaluate_sgmc_off_catalogue,
    fit_buffered_dual_cover_oof,
    load_reference_masks,
    run_leakage_canary,
)
from gemskarage1.paths import DOCS_DATA_DIR, DOWNLOADS_DIR, EVIDENCE_DIR, cache_dir, data_dir
from gemskarage1.registry_audit import run_full_fleet_uniqueness_gate

SUBMISSION_STEM = "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros"
SUBMISSION_NAME = "karage1-hmas-sinter-dualcover-sep29-zeros"
SUBMISSION_NOTE = (
    "H-K1-1 HMAS mag-trough + PPGR + F2mDAB/sinter DualCover GBDT + d=2.9px 300m submodular"
)
assert len(SUBMISSION_NOTE) <= 140


def run_stage_fit(force: bool = False) -> None:
    from gemskarage1.guard import stop_inherited_driver
    stop_inherited_driver()
    t0 = time.time()
    ddir = data_dir()
    cdir = cache_dir()
    meta = build_feature_stack(ddir, cdir, force=False)
    refs = load_reference_masks(ddir)
    fit_buffered_dual_cover_oof(
        Path(meta["stack_path"]),
        refs["grid"],
        refs["lidar_valid"],
        cdir,
        force=force,
    )
    print(f"[stage=fit] Completed in {time.time() - t0:.1f}s")


def run_stage_eval_and_package() -> int:
    from gemskarage1.guard import stop_inherited_driver
    stop_inherited_driver()
    t0 = time.time()
    ddir = data_dir()
    cdir = cache_dir()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    meta = build_feature_stack(ddir, cdir, force=False)
    stack_path = Path(meta["stack_path"])
    refs = load_reference_masks(ddir)
    grid = refs["grid"]
    foot = refs["footprint"]
    labels = refs["labels"]
    sgmc_off_cat = refs["sgmc_off_cat"]
    lidar_valid = refs["lidar_valid"]

    # 1. Load or run 58-channel Leakage Canary
    canary_path = EVIDENCE_DIR / "leakage_canary_58ch.json"
    if canary_path.is_file():
        canary = json.loads(canary_path.read_text())
    else:
        canary = run_leakage_canary(stack_path, foot, labels)
        canary_path.write_text(json.dumps(canary, indent=2) + "\n")
    assert canary["all_passed"], f"Leakage canary failed: {canary['leaking_features']}"

    # 2. Load buffered OOF surfaces
    oof = fit_buffered_dual_cover_oof(stack_path, grid, lidar_valid, cdir, force=False)
    p_base_quad = oof["p_base_quad"]
    p_dual_quad = oof["p_dual_quad"]
    p_dual_prod = oof["p_dual_prod"]
    c_hmas_cal = oof["c_hmas_cal"]

    mm = open_memmap(stack_path, mode="r")
    depth_base = mm[14].astype(np.float32, copy=True)
    slope_deg = mm[18].astype(np.float32, copy=True)
    del mm

    # 3. Compose 4 quadrant-OOF surfaces (`BASE_35` control + 3 preregistered `H-K1-1` experiments)
    quad_arms: dict[str, tuple[np.ndarray, float]] = {
        "BASE_35": compose_arm_surface("BASE_35", p_base_quad, c_hmas_cal, foot),
        "EXP1_HMAS_MULT": compose_arm_surface("EXP1_HMAS_MULT", p_dual_quad, c_hmas_cal, foot),
        "EXP2_HMAS_MAXENV_RAW": compose_arm_surface("EXP2_HMAS_MAXENV_RAW", p_dual_quad, c_hmas_cal, foot),
        "EXP3_HMAS_MAXENV_AXIAL29": compose_arm_surface("EXP3_HMAS_MAXENV_AXIAL29", p_dual_quad, c_hmas_cal, foot),
    }

    print("[eval] Running official shared template `gems57-pooled-hide-v2` per-cell evaluation (`all` & `detached`)...")
    gems57_raw = evaluate_gems57_holdout_suite(
        quad_arms,
        grid,
        full_budget=38_200,
        b_collar_px=2.2,
        candidate_arm="EXP1_HMAS_MULT",
    )

    print("[eval] Running per-cell `GEMSDOE32-HIDE-RECOVER-v3.0` (`all` n=22,232 & `detached >= 600m` n=15,504)...")
    hr3_draws = build_hr3_draws(foot, labels, seeds=(101, 202))
    base_hr3, base_hr3_all_blks, base_hr3_det_blks = evaluate_hr3_per_cell(
        quad_arms["BASE_35"][0],
        hr3_draws,
        foot,
        full_budget=38_200,
        min_sep_px=quad_arms["BASE_35"][1],
        b_collar_px=2.2,
    )
    hr3_by_arm: dict[str, dict] = {"BASE_35": base_hr3}
    for arm_name in ("EXP1_HMAS_MULT", "EXP2_HMAS_MAXENV_RAW", "EXP3_HMAS_MAXENV_AXIAL29"):
        surf_q, sep_q = quad_arms[arm_name]
        hr3_res, _, _ = evaluate_hr3_per_cell(
            surf_q,
            hr3_draws,
            foot,
            full_budget=38_200,
            min_sep_px=sep_q,
            b_collar_px=2.2,
            ref_blocks_all=base_hr3_all_blks,
            ref_blocks_det=base_hr3_det_blks,
        )
        hr3_by_arm[arm_name] = hr3_res
        print(
            f"  [HIDE-RECOVER-v3.0] {arm_name:26s} -> all={hr3_res['all']['dti']:.6f} "
            f"(vs BASE_35: {hr3_res['all']['delta_vs_ref_mean']:+.6f}), "
            f"det600m={hr3_res['detached']['dti']:.6f} (vs BASE_35: {hr3_res['detached']['delta_vs_ref_mean']:+.6f})"
        )

    # 4. Evaluate static `.tif` reference (`GEMSDOE32` 0.2778 Champion) + static full-map emissions on SGMC-CAL-v3.0
    champ_path = ddir / "scored" / "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    with rasterio.open(champ_path) as ds_ch:
        raw_ch = ds_ch.read(1)
        champ_arr = np.where(foot & np.isfinite(raw_ch), raw_ch.astype(np.float32), np.float32(0.0))

    champ_sgmc, champ_sgmc_blks = evaluate_sgmc_off_catalogue(champ_arr, foot, labels, sgmc_off_cat)
    champ_forensics = compute_spatial_forensics(champ_arr >= 0.5, foot, labels, lidar_valid, slope_deg, depth_base)
    print(
        f"[eval] Reference Champion (0.2778 OWNER-REPORT): "
        f"SGMC_raw={champ_sgmc['sgmc_raw_pooled_dti']:.6f} (n=62,703 off-catalogue bedrock fault px), "
        f"dots={champ_forensics['dots']}, far_field={champ_forensics['far_field_gt_1p5km_frac']:.4f}, "
        f"lidar_gap={champ_forensics['lidar_gap_frac']:.4f}, flat_basin={champ_forensics['flat_deep_basin_frac']:.4f}"
    )

    prod_arms_spec = {
        "BASE_35": compose_arm_surface("BASE_35", p_base_quad, c_hmas_cal, foot),
        "EXP1_HMAS_MULT": compose_arm_surface("EXP1_HMAS_MULT", p_dual_prod, c_hmas_cal, foot),
        "EXP2_HMAS_MAXENV_RAW": compose_arm_surface("EXP2_HMAS_MAXENV_RAW", p_dual_prod, c_hmas_cal, foot),
        "EXP3_HMAS_MAXENV_AXIAL29": compose_arm_surface("EXP3_HMAS_MAXENV_AXIAL29", p_dual_prod, c_hmas_cal, foot),
    }

    static_results: dict[str, dict] = {
        "CHAMPION_GEMSDOE32_02778": {
            "arm_id": "CHAMPION_GEMSDOE32_02778",
            "owner_reported_live_dti": 0.2778,
            "evidence_label": "OWNER-REPORT (live submission receipt not committed in repo) + HOLDOUT-DTI",
            "sgmc": champ_sgmc,
            "forensics": champ_forensics,
        }
    }
    emitted_maps: dict[str, np.ndarray] = {}

    for arm_name, (surf_prod, min_sep) in prod_arms_spec.items():
        t_em = time.time()
        dots_bool = emit_submodular_300m(
            surf_prod,
            foot,
            labels,
            38_200,
            b_collar_px=2.2,
            min_sep_px=min_sep,
            max_candidates=420_000,
        )
        pred_f32 = np.where(foot & dots_bool, np.float32(1.0), np.float32(0.0)).astype(np.float32)
        emitted_maps[arm_name] = pred_f32

        sgmc_res, _ = evaluate_sgmc_off_catalogue(
            pred_f32, foot, labels, sgmc_off_cat, ref_blocks=champ_sgmc_blks
        )
        foren = compute_spatial_forensics(dots_bool, foot, labels, lidar_valid, slope_deg, depth_base)

        g57_all = gems57_raw["all"]["scores"][arm_name]
        g57_det = gems57_raw["detached"]["scores"][arm_name]

        static_results[arm_name] = {
            "arm_id": arm_name,
            "emit_seconds": round(time.time() - t_em, 2),
            "gems57_per_cell_all": g57_all,
            "gems57_per_cell_detached": g57_det,
            "hide_recover_v3_per_cell": hr3_by_arm[arm_name],
            "sgmc": sgmc_res,
            "forensics": foren,
        }
        print(
            f"[eval] {arm_name:26s} ({foren['dots']} dots, {time.time()-t_em:.1f}s) | "
            f"gems57_all={g57_all['dti']:.6f} | gems57_det={g57_det['dti']:.6f} | "
            f"SGMC_raw={sgmc_res['sgmc_raw_pooled_dti']:.6f} (delta={sgmc_res['delta_vs_champion_raw']:+.6f}, CI={sgmc_res['delta_vs_champion_ci95']}) | "
            f"far={foren['far_field_gt_1p5km_frac']:.4f}, gap={foren['lidar_gap_frac']:.4f}, basin={foren['flat_deep_basin_frac']:.4f}, clump3={foren['clump_ge3_in_3px_frac']:.4f}"
        )

    # 5. Select holdout winner among EXP1..EXP3 on detached fault recovery + off-catalogue SGMC bedrock recovery
    exp_arms = ["EXP1_HMAS_MULT", "EXP2_HMAS_MAXENV_RAW", "EXP3_HMAS_MAXENV_AXIAL29"]
    best_arm = max(
        exp_arms,
        key=lambda a: (
            static_results[a]["gems57_per_cell_detached"]["dti"]
            + static_results[a]["sgmc"]["sgmc_raw_pooled_dti"]
        ),
    )
    print(f"[select] Winning holdout arm: {best_arm}")

    # Recompute exact paired bootstrap differences with `candidate=best_arm`
    gems57_suite = {
        "all": eh57.pooled_summary(gems57_raw["all_raw_terms"], draws=1000, seed=520810, candidate=best_arm),
        "detached": eh57.pooled_summary(gems57_raw["detached_raw_terms"], draws=1000, seed=520810, candidate=best_arm),
    }

    win_surf = prod_arms_spec[best_arm][0]
    win_dots = emitted_maps[best_arm]

    # 6. Write & atomically double-validate unique GeoTIFF + single-TIFF ZIP via shared `submission_writer.py`
    out_tif = DOWNLOADS_DIR / f"{SUBMISSION_STEM}.tif"
    for p_old in DOWNLOADS_DIR.glob("karage1-*"):
        p_old.unlink()

    writer_receipt = write_submission(
        out_tif,
        win_dots,
        ddir / "sample_submission.tif",
        foot,
        note=SUBMISSION_NOTE,
        name=SUBMISSION_NAME,
        catalogue=labels,
        metadata={
            "lane_id": "H-K1-1-HMAS-SINTER-ENV",
            "winning_arm": best_arm,
            "evaluator_version": eh57.VERSION,
        },
    )
    print(f"[writer] Wrote & validated {out_tif.name} (sha256={writer_receipt['sha256'][:16]}..., bytes={writer_receipt['bytes']})")

    # 7. Run Full-Fleet Duplication & Uniqueness Gate (pre-placement surface AND final dots)
    print("[uniqueness] Scanning full fleet (pre-placement continuous surface + final dots)...")
    uniq_report = run_full_fleet_uniqueness_gate(
        win_surf,
        win_dots,
        out_tif,
        foot,
    )
    (EVIDENCE_DIR / "fleet_uniqueness_593.json").write_text(json.dumps(uniq_report, indent=2) + "\n")
    print(
        f"[uniqueness] Scanned {uniq_report['total_fleet_rasters_scanned']} rasters "
        f"({uniq_report['unique_pixel_rasters_scanned']} unique pixel maps) | "
        f"max_surface_spearman={uniq_report['max_pre_placement_surface_spearman']:.5f} | "
        f"max_dot_spearman={uniq_report['max_final_dot_spearman']:.5f} | "
        f"max_discrete_3px_overlap={uniq_report['max_discrete_submission_3px_overlap']:.5f} "
        f"({uniq_report['max_discrete_submission_ref']}) | passed={uniq_report['passed']}"
    )

    # 8. Fail-closed Promotion Decision (matching pre-registered gates in docs/research/hypotheses-preregistration-2026-10-27.md)
    win_res = static_results[best_arm]
    beats_base_gems57_all = win_res["gems57_per_cell_all"]["dti"] > static_results["BASE_35"]["gems57_per_cell_all"]["dti"]
    beats_base_gems57_det = win_res["gems57_per_cell_detached"]["dti"] > static_results["BASE_35"]["gems57_per_cell_detached"]["dti"]
    beats_base_gems57_det_ci = gems57_suite["detached"]["paired_differences"]["BASE_35"]["ci95"][0] > 0.0
    beats_base_hr3_all = (
        win_res["hide_recover_v3_per_cell"]["all"]["dti"]
        > static_results["BASE_35"]["hide_recover_v3_per_cell"]["all"]["dti"]
    )
    beats_champ_sgmc = win_res["sgmc"]["sgmc_raw_pooled_dti"] > champ_sgmc["sgmc_raw_pooled_dti"]
    beats_champ_sgmc_ci = win_res["sgmc"]["delta_vs_champion_ci95"][0] > 0.0
    validator_ok = bool(writer_receipt["validator"]["all_checks_passed"] and writer_receipt["template_report"]["ok"])

    promote_ok = (
        canary["all_passed"]
        and validator_ok
        and uniq_report["passed"]
        and beats_base_gems57_all
        and beats_base_gems57_det
        and beats_base_gems57_det_ci
        and beats_base_hr3_all
        and beats_champ_sgmc
        and beats_champ_sgmc_ci
    )
    verdict = "promote" if promote_ok else "negative"

    receipt_json_path = out_tif.with_suffix(".json")
    rec_disk = json.loads(receipt_json_path.read_text())
    rec_disk["promoted"] = bool(promote_ok)
    rec_disk["approved_for_weekly_slot"] = bool(promote_ok)
    rec_disk["uniqueness_gate_passed"] = bool(uniq_report["passed"])
    rec_disk["verdict"] = verdict
    receipt_json_path.write_text(json.dumps(rec_disk, indent=2) + "\n")

    # 9. Emit Parallel-Run Protocol JSON Run Card (`evidence/run_card.json`) & Experiment Ledger
    ledger = {
        "schema_version": 1,
        "generated_at_utc": "2026-10-27T22:00:00Z",
        "lane_id": "H-K1-1-HMAS-SINTER-ENV",
        "winning_arm": best_arm,
        "verdict": verdict,
        "gates": {
            "leakage_canary_passed": canary["all_passed"],
            "validator_ok": validator_ok,
            "uniqueness_gate_passed": uniq_report["passed"],
            "beats_base35_gems57_all": beats_base_gems57_all,
            "beats_base35_gems57_detached": beats_base_gems57_det,
            "beats_base35_gems57_detached_95ci_gt_zero": beats_base_gems57_det_ci,
            "beats_base35_hr3_all": beats_base_hr3_all,
            "beats_champion_sgmc_raw": beats_champ_sgmc,
            "beats_champion_sgmc_95ci_gt_zero": beats_champ_sgmc_ci,
        },
        "gems57_pooled_hide_v2": gems57_suite,
        "arms": static_results,
    }
    (EVIDENCE_DIR / "experiments_summary.json").write_text(json.dumps(ledger, indent=2) + "\n")

    run_card = {
        "hypothesis": (
            "H-K1-1 (HMAS-SINTER-ENV): Blind hydrothermal conduit faults missed by Quaternary scarp catalogues "
            "exhibit linear negative magnetic tilt-curvature / 3-D analytic-signal demagnetization troughs "
            "(titanomagnetite -> hematite/pyrite/clay oxidation), positive Poisson pseudo-gravity orthogonal "
            "basement steps, 4-block standardized GeoDAWN 214Bi radon & K/Th alteration crests, and strike-projected "
            "INGENIOUS 2m temperature probe (F2mDAB), Quaternary sinter/breccia, and quartz-geothermometer plumes; "
            "fusing Dual-Cover (M_Full inside 75.37% 1m LiDAR + quantile-matched LiDAR-free M_Sub inside the 24.63% "
            "gap) with hydrothermal conduit modulation and d=2.9px axial-spaced submodular 300m kernel allocation "
            "recovers detached & off-catalogue faults without neighbor clumping."
        ),
        "mechanism": (
            "150-300C hydrothermal upflow along permeable Great Basin normal/transtensional fault damage zones "
            "destroys host-rock magnetite while depositing silica sinter/breccia and shallow conductive clay caps, "
            "creating contrarian magnetic troughs paired with upward-continued (400-1800m) non-magnetic basement "
            "gravity gradients and strike-elongated F2mDAB thermal & 214Bi radon anomalies under Holocene fill."
        ),
        "mimic_process": (
            "Late Pleistocene Lake Lahontan wave-cut shoreline benches (sharp 1m DEM steps inside deep basin fill "
            "with zero basement gravity gradient), US Census TIGER highway/railroad embankments (<=140m symmetric "
            "berms), tabular Neogene basalt/ash-flow lava margins (removed via 2-D FFT 1/|k| Poisson pseudo-gravity "
            "orthogonal regression), and flat conductive evaporite playas (vetoed where slope < 1.8 deg and cover > 320m)."
        ),
        "holdout_dti": {
            "gems57_pooled_hide_v2_all": {
                "label": "HOLDOUT-DTI",
                "evaluator_version": eh57.VERSION,
                "dti": round(win_res["gems57_per_cell_all"]["dti"], 6),
                "ci95": [round(x, 6) for x in win_res["gems57_per_cell_all"]["ci95"]],
                "withheld_positives": win_res["gems57_per_cell_all"]["withheld_positive_pixels"],
                "delta_vs_base35": round(
                    gems57_suite["all"]["paired_differences"]["BASE_35"]["delta"], 6
                ),
                "delta_vs_base35_ci95": [
                    round(x, 6) for x in gems57_suite["all"]["paired_differences"]["BASE_35"]["ci95"]
                ],
            },
            "gems57_pooled_hide_v2_detached": {
                "label": "HOLDOUT-DTI",
                "evaluator_version": eh57.VERSION,
                "dti": round(win_res["gems57_per_cell_detached"]["dti"], 6),
                "ci95": [round(x, 6) for x in win_res["gems57_per_cell_detached"]["ci95"]],
                "withheld_positives": win_res["gems57_per_cell_detached"]["withheld_positive_pixels"],
                "delta_vs_base35": round(
                    gems57_suite["detached"]["paired_differences"]["BASE_35"]["delta"], 6
                ),
                "delta_vs_base35_ci95": [
                    round(x, 6) for x in gems57_suite["detached"]["paired_differences"]["BASE_35"]["ci95"]
                ],
            },
            "hide_recover_v3_per_cell": win_res["hide_recover_v3_per_cell"],
            "sgmc_off_catalogue_bedrock_faults": win_res["sgmc"],
        },
        "registry_correlation_overlap": {
            "total_fleet_rasters_scanned": uniq_report["total_fleet_rasters_scanned"],
            "unique_pixel_rasters_scanned": uniq_report["unique_pixel_rasters_scanned"],
            "exact_hash_matches": uniq_report["exact_hash_matches"],
            "max_pre_placement_surface_spearman": uniq_report["max_pre_placement_surface_spearman"],
            "max_pre_placement_surface_ref": uniq_report["max_pre_placement_surface_ref"],
            "max_final_dot_spearman": uniq_report["max_final_dot_spearman"],
            "max_final_dot_spearman_ref": uniq_report["max_final_dot_spearman_ref"],
            "max_discrete_submission_3px_overlap": uniq_report["max_discrete_submission_3px_overlap"],
            "max_discrete_submission_ref": uniq_report["max_discrete_submission_ref"],
            "non_competing_lattice_or_overdense_blankets": uniq_report[
                "non_competing_lattice_or_continuous_rasters_gt_70pct_cov"
            ],
            "spearman_ceiling": 0.90,
            "overlap_3px_ceiling": 0.70,
            "passed": uniq_report["passed"],
        },
        "raster_sha256": writer_receipt["sha256"],
        "zip_sha256": writer_receipt["zip_sha256"],
        "validator_output": writer_receipt["validator"],
        "submission_name": SUBMISSION_NAME,
        "submission_file": out_tif.name,
        "submission_zip": out_tif.with_suffix(".zip").name,
        "submission_note": SUBMISSION_NOTE,
        "verdict": verdict,
    }
    (EVIDENCE_DIR / "run_card_hmas_sinter.json").write_text(json.dumps(run_card, indent=2) + "\n")
    print(f"[done] Run card written to evidence/run_card_hmas_sinter.json | VERDICT = {verdict.upper()} | elapsed={time.time()-t0:.1f}s")
    gc.collect()
    return 0


def main() -> int:
    from gemskarage1.guard import stop_inherited_driver
    stop_inherited_driver()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=("fit", "eval", "all"), default="all")
    ap.add_argument("--force-fit", action="store_true")
    args = ap.parse_args()

    if args.stage in ("fit", "all"):
        run_stage_fit(force=args.force_fit)
    if args.stage in ("eval", "all"):
        return run_stage_eval_and_package()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
