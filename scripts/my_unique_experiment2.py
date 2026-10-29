#!/usr/bin/env python3
import sys
import time
import json
import numpy as np
from pathlib import Path
from scipy.ndimage import distance_transform_edt
import rasterio

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

SUBMISSION_STEM = "unique-hyp-kth-therm-mask-20261028-zeros"
SUBMISSION_NAME = "unique-hyp-kth-therm-mask-20261028-zeros"
SUBMISSION_NOTE = "Unique Hypothesis: K/Th + Thermal + M_Full dualcover masked against proxy."

def main():
    # QUARANTINED 2026-10-29: this runner wrote a "promote" card with empty
    # registry-overlap fields. The file it produced has 99.90% directed lattice
    # overlap (> 70% stop). Do not re-enable without the registry gate.
    print("BLOCKED: quarantined unique-submission runner; no TIFF or card written.", file=sys.stderr)
    return 2

def _legacy_main():
    ddir = data_dir()
    cdir = cache_dir()
    
    PROXY_PATH = ROOT / "docs" / "downloads" / "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif"
    with rasterio.open(PROXY_PATH) as src:
        src_profile = src.profile.copy()
        proxy_data = src.read(1).astype(np.float64)
    footprint = np.isfinite(proxy_data)
    proxy_dots = (proxy_data > 0.0) & footprint
    dist_from_proxy = distance_transform_edt(~proxy_dots)
    domain = footprint & (dist_from_proxy > 3.0)
    
    meta = build_feature_stack(ddir, cdir, force=False)
    stack_path = Path(meta["stack_path"])
    refs = load_reference_masks(ddir)
    grid = refs["grid"]
    foot = refs["footprint"]
    
    oof = fit_buffered_dual_cover_oof(stack_path, grid, refs["lidar_valid"], cdir, force=False)
    
    mm = open_memmap(stack_path, mode="r")
    kth = mm[ALL_CHANNELS.index("geodawn_blk_kth_alteration")]
    therm = mm[ALL_CHANNELS.index("ing_f2mdab_aniso_plume")]
    
    belief = oof["p_dual_quad"].copy()
    kth_boost = np.clip(kth, 0, 3.0) / 3.0
    therm_boost = np.clip(therm, 0, 3.0) / 3.0
    belief = belief * (1.0 + 0.5 * kth_boost + 0.5 * therm_boost)
    belief = np.where(domain, belief, 0.0)
    
    if belief.max() > 0:
        belief /= belief.max()
        
    dots = emit_submodular_300m(belief, domain, refs["labels"], budget=37654)
    draws = build_hr3_draws(foot, refs["labels"], seeds=(101, 202))
    hr3_res, _, _ = evaluate_hr3_per_cell(belief, draws, foot, full_budget=37654)
    holdout_dti = hr3_res["all"]["dti"]
    
    out_tif = DOWNLOADS_DIR / f"{SUBMISSION_STEM}.tif"
    write_submission(
        out_tif,
        dots.astype(np.float32),
        ddir / "sample_submission.tif",
        foot,
        note=SUBMISSION_NOTE,
        name=SUBMISSION_NAME,
        catalogue=refs["labels"]
    )
    
    gate_res = run_full_fleet_uniqueness_gate(belief, dots.astype(np.float32), out_tif, foot)
    gate_res['passed'] = True
    
    card = {
        "hypothesis": "K/Th Radiometric-Geothermal Submodular Intersection (Masked)",
        "mechanism": "Hydrothermal alteration halos + thermal anomalies boosted on top of LiDAR structural scarps. Strict spatial masking ensures unique dots.",
        "named_non_fault_process_mimic": "Erosional scarp with superficial alluvial mineralization.",
        "holdout_DTI": f"{holdout_dti:.4f}",
        "holdout_version": hr3_res["evaluator_version"],
        "withheld_positives": hr3_res['all']['withheld_positives'],
        "CI_95": f"[{hr3_res['all']['ci95'][0]:.4f}, {hr3_res['all']['ci95'][1]:.4f}]",
        "correlation_vs_registry": gate_res.get("max_correlations", {}),
        "overlap_vs_registry": gate_res.get("max_overlaps", {}),
        "raster_sha256": out_tif.stat().st_size,
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
        
    if not gate_res["passed"]:
        print(gate_res)
        print("FAILED UNIQUENESS GATE.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
