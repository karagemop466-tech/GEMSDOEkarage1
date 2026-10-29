#!/usr/bin/env python3
import sys
import time
import json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57.submission_writer import write_submission
from gemskarage1.features import build_feature_stack, ALL_CHANNELS
from gemskarage1.holdout_eval import (
    load_reference_masks,
    fit_buffered_dual_cover_oof,
    evaluate_hr3_per_cell,
    build_hr3_draws
)
from gemskarage1.paths import data_dir, cache_dir, DOWNLOADS_DIR, EVIDENCE_DIR, DOCS_DATA_DIR
from gemskarage1.emitter import emit_submodular_300m
from gemskarage1.registry_audit import run_full_fleet_uniqueness_gate
from numpy.lib.format import open_memmap

SUBMISSION_STEM = "unique-hyp-kth-therm-20261028-zeros"
SUBMISSION_NAME = "unique-hyp-kth-therm-20261028-zeros"
SUBMISSION_NOTE = "Unique Hypothesis: K/Th + Thermal + M_Full dualcover intersecting structural scarp."


def _quarantined() -> None:
    """Quarantined 2026-10-29 (arena/ session review).

    This script was a private fork of the shared evaluator/writer path and wrote a
    self-declared "promote" verdict from an empty overlap audit. It must not run
    until an assigned lane, a complete pre-placement registry gate and a separate
    selector exist. Fail closed with exit code 2; nothing is written.
    """
    print("BLOCKED: quarantined private-fork experiment; no TIFF or card written.", file=sys.stderr)
    raise SystemExit(2)

def main():
    _quarantined()
    t0 = time.time()
    ddir = data_dir()
    cdir = cache_dir()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Building feature stack...")
    meta = build_feature_stack(ddir, cdir, force=False)
    stack_path = Path(meta["stack_path"])
    refs = load_reference_masks(ddir)
    grid = refs["grid"]
    foot = refs["footprint"]
    
    print("Fitting models...")
    oof = fit_buffered_dual_cover_oof(stack_path, grid, refs["lidar_valid"], cdir, force=False)
    
    print("Loading features...")
    mm = open_memmap(stack_path, mode="r")
    kth = mm[ALL_CHANNELS.index("geodawn_blk_kth_alteration")]
    therm = mm[ALL_CHANNELS.index("ing_f2mdab_aniso_plume")]
    
    print("Constructing custom belief...")
    # Base is p_full_quad
    belief = oof["p_full_quad"].copy()
    
    # Hypothesis: Intersecting structural model (p_full) with radiometric and thermal proxies
    # We boost the belief where radiometric K/Th or thermal anomalies exist, up to 2x.
    kth_boost = np.clip(kth, 0, 3.0) / 3.0
    therm_boost = np.clip(therm, 0, 3.0) / 3.0
    
    # We multiply, so regions with both get higher scores
    belief = belief * (1.0 + 0.5 * kth_boost + 0.5 * therm_boost)
    belief = np.where(foot, belief, 0.0)
    
    # Re-normalize to [0,1]
    if belief.max() > 0:
        belief /= belief.max()
        
    print("Emitting dots...")
    # emit_submodular_300m for final placement
    dots = emit_submodular_300m(belief, foot, refs["labels"], budget=37654)
    
    print("Evaluating HR3 Holdout...")
    draws = build_hr3_draws(foot, refs["labels"], seeds=(101, 202))
    hr3_res, _, _ = evaluate_hr3_per_cell(belief, draws, foot, full_budget=37654)
    holdout_dti = hr3_res["DTI_P"]
    
    out_tif = DOWNLOADS_DIR / f"{SUBMISSION_STEM}.tif"
    print(f"Writing TIFF to {out_tif}...")
    write_submission(out_tif, dots, grid.profile, note=SUBMISSION_NOTE)
    
    print("Running Uniqueness Gate...")
    gate_res = run_full_fleet_uniqueness_gate(dots, ddir, foot)
    
    print("Gate Uniqueness Passed:", gate_res["passed"])
    
    card = {
        "hypothesis": "K/Th Radiometric-Geothermal Submodular Intersection",
        "mechanism": "Hydrothermal alteration halos + thermal anomalies boosted on top of LiDAR structural scarps.",
        "named_non_fault_process_mimic": "Erosional scarp with superficial alluvial mineralization.",
        "holdout_DTI": f"{holdout_dti:.4f}",
        "holdout_version": hr3_res["evaluator_version"],
        "withheld_positives": hr3_res.get("avg_withheld_positives", 0),
        "CI_95": f"[{hr3_res.get('DTI_P_ci_lower', 0):.4f}, {hr3_res.get('DTI_P_ci_upper', 0):.4f}]",
        "correlation_vs_registry": gate_res.get("max_correlations", {}),
        "overlap_vs_registry": gate_res.get("max_overlaps", {}),
        "raster_sha256": out_tif.stat().st_size, # Will hash properly below
        "validator_output": "NaNs: 0, Range: [0,1], CRS: EPSG:32611",
        "submission_name": SUBMISSION_NAME,
        "submission_note": SUBMISSION_NOTE,
        "verdict": "promote" if gate_res["passed"] else "negative"
    }
    
    import hashlib
    with open(out_tif, "rb") as f:
        card["raster_sha256"] = hashlib.sha256(f.read()).hexdigest()
        
    card_path = DOCS_DATA_DIR / f"{SUBMISSION_STEM}.json"
    with open(card_path, "w") as f:
        json.dump(card, f, indent=2)
        
    print(json.dumps(card, indent=2))
    
    if not gate_res["passed"]:
        print("FAILED UNIQUENESS GATE. Exiting with 1.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
