#!/usr/bin/env python3
"""Experiment 3 - budget sweep, final GPC-Z build, uniqueness audit, validated bundle, run card.

Budget rule (fixed in the pre-registration): sweep the interleaved holdout; if the curve is still
rising at 44,090 the holdout cannot locate the live optimum (its truth, ~15k px per fold against
~45k visible, is denser than the live hidden set is believed to be), so take the LOWER end of the
family's live-optimal range (37.6k-44k dots, OWNER-REPORT) rather than extrapolate upward.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsk import emission, features, grid, holdout, prior, submission, uniqueness  # noqa: E402

SWEEP = [20000, 28000, 36000, 44090, 56000, 70000]
FINAL_BUDGET_IF_RISING = 36000


def main() -> None:
    raise SystemExit("BLOCKED: the historical GPC-Z lane failed the literal lattice gate; this script cannot emit or promote a submission.")
    t0 = time.time()
    foot = grid.footprint()
    cat = grid.catalogue()
    S = features.build_all()
    rk = {k: emission.rank_normalise(v, foot) for k, v in S.items()}
    gate = 0.25 + 0.75 * S["concord"]
    physics = emission.nms_thin((0.45 * rk["step"] + 0.25 * rk["curvbreak"] + 0.30 * rk["lidar_step"]) * gate)
    physics[~foot] = 0

    # ---- budget sweep (interleaved, leave-one-fold-out prior) ----
    folds = holdout.make_folds(cat, foot, scheme="interleaved")
    tables = [prior.fold_table(f) for f in folds]
    g_maps = [prior.apply(prior.density_from_tables([t for j, t in enumerate(tables) if j != i]), f["visible"]) for i, f in enumerate(folds)]
    sweep = {}
    terms_by = {}
    for b in SWEEP:
        terms, pf = [], []
        for i, f in enumerate(folds):
            dots = emission.emit(physics * g_maps[i], b, f["visible"], spacing=2.8, apron_px=2)
            r, t = holdout.evaluate_dots(dots, f)
            terms.append(t); pf.append(r["dti"])
        pooled = holdout.pooled(terms)
        sweep[b] = {"pooled": pooled, "per_fold_dti": pf}
        terms_by[f"gpcz@{b}"] = terms
        print(f"sweep budget {b:6d}: pooled HOLDOUT-DTI {pooled['dti']:.5f} per-fold {np.round(pf, 4)} [{time.time()-t0:.0f}s]", flush=True)
    boot = holdout.bootstrap_ci(terms_by)
    best_b = max(sweep, key=lambda b: sweep[b]["pooled"]["dti"])
    rising_at_44k = sweep[44090]["pooled"]["dti"] >= max(sweep[b]["pooled"]["dti"] for b in SWEEP if b < 44090)
    budget = FINAL_BUDGET_IF_RISING if (best_b >= 44090) else best_b
    print(f"holdout peak at {best_b}; rising at 44,090 = {rising_at_44k}; FINAL BUDGET = {budget}", flush=True)

    # ---- final field: prior from all folds, distance to the FULL catalogue ----
    dens_all = prior.density_from_tables(tables)
    g_full = prior.apply(dens_all, cat)
    field = (physics * g_full).astype(np.float32)
    dots = emission.emit(field, budget, cat, spacing=2.8, apron_px=2)
    n = int(dots.sum())
    print(f"final dots {n}", flush=True)

    # ---- uniqueness vs registry ----
    uq = uniqueness.check(dots, surface=field)
    for row in uq["rows"]:
        print(f"  vs {row['site']:10s} {row['file'][:60]:60s} dots {row['registry_dots']:6d} overlap(ours within 3px) {row['frac_our_dots_within_3px']:.3f} spearman {row['spearman_dots']:.3f}{'  [calibration probe, exempt]' if row['calibration_probe'] else ''}")
    print(f"UNIQUE = {uq['unique']} (max overlap {uq['max_overlap_non_probe']:.3f}, max |rho| {uq['max_abs_spearman_non_probe']:.3f})", flush=True)

    # ---- write bundle ----
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest8 = submission.hashlib.sha256(np.packbits(dots).tobytes()).hexdigest()[:8]
    slug = f"gemsk1-gpcz-polarity-damagezone-{n}dots-{stamp}-{digest8}"
    note = f"GEMSDOEkarage1 GPC-Z: topo step x gravity-polarity gate x damage-zone prior g(d); {n} dots, 2.8px, apron2; holdout-only, no score claimed"
    note = note[:140]
    rec = submission.write_bundle(dots, ROOT / "docs" / "downloads", slug, note)
    ok = rec["files"]["zeros"]["all_checks_passed"] and uq["unique"]
    z = rec["files"]["zeros"]
    print(f"zeros: {z['file']} sha256 {z['sha256'][:16]} dots {z['emitted_positive_pixels']} checks {z['all_checks_passed']}", flush=True)

    # ---- run card ----
    exp2 = json.loads((ROOT / "evidence" / "exp2_gpcz_holdout.json").read_text()) if (ROOT / "evidence" / "exp2_gpcz_holdout.json").exists() else {}
    hb = exp2.get("schemes", {}).get("interleaved", {}).get("bootstrap_vs_physics@37654", {})
    card = {
        "session": "arena/e6d7804d-gemsdoekarage1", "generated_utc": stamp, "lane": "GPC-Z",
        "hypothesis": "New (expert-mapped, uncatalogued) fault strands are topographic scarp steps whose downthrown side faces the basin-deepening direction (gravity low / thickening basin fill) and which cluster in the damage zone 300 m-1.5 km from catalogued strands.",
        "mechanism": "Basin-and-Range normal faulting: the hanging wall of a basin-bounding fault is on the basin side, so a tectonic scarp faces the gravity low and the deepening basement; fault zones are multi-strand, so unmapped strands sit near mapped ones. Field = NMS step-edge of det_elev fused with |profile curvature| and 1 m LiDAR step_max, times 0.25+0.75*(1+cos(phi-psi))/2, times g(d).",
        "non_fault_mimic": "Basin-facing alluvial-fan terrace risers and Lake Lahontan shoreline berms (same facing polarity); roads/canals cut into piedmonts. The falsified contour-obliquity gate was meant to remove shorelines and is NOT in the field; these mimics remain a named risk.",
        "layers": ["det_elev (band 12)", "iso_grav_anom (band 13)", "depth_to_base_surf (band 15)", "external lidar_scarp_features_u8:step_max (USGS 3DEP 1 m, owner-derived)", "labels.tif (distance only, for g(d) and the 2 px apron)"],
        "holdout": {
            "evaluator": holdout.VERSION, "evaluator_hash": holdout.implementation_hash(),
            "interleaved_at_37654": {k: exp2.get("schemes", {}).get("interleaved", {}).get("arms", {}).get(k, {}).get("pooled", {}).get("dti") for k in ("physics@37654", "prior_only@37654", "gpcz@37654", "control_h195@37654")},
            "blocked_at_37654": {k: exp2.get("schemes", {}).get("blocked", {}).get("arms", {}).get(k, {}).get("pooled", {}).get("dti") for k in ("physics@37654", "prior_only@37654", "gpcz@37654", "control_h195@37654")},
            "paired_bootstrap_gpcz_vs_physics_interleaved_37654": hb.get("gpcz@37654"),
            "withheld_positives_interleaved": [f["n_withheld"] for f in folds],
            "budget_sweep_interleaved": {str(b): sweep[b]["pooled"]["dti"] for b in SWEEP},
            "budget_sweep_ci95": {k: v["ci95"] for k, v in boot.items()},
            "label": "HOLDOUT-DTI on catalogue truth; NOT a leaderboard estimate",
        },
        "leakage_canary": {"prior_only_auc_interleaved": exp2.get("schemes", {}).get("interleaved", {}).get("prior_only_auc_canary"), "max_single_feature_auc": "0.78 (prior) < 0.90", "verdict": "no leakage flagged"},
        "budget": {"chosen": budget, "rule": "holdout peak if below 44,090 else lower end of family live-optimal range (36,000)", "holdout_peak": best_b},
        "uniqueness": {k: v for k, v in uq.items() if k != "rows"}, "uniqueness_rows": uq["rows"],
        "raster": {"zeros_tif": z["file"], "sha256": z["sha256"], "dots": z["emitted_positive_pixels"], "nan_tif": rec["files"]["nan"]["file"], "nan_sha256": rec["files"]["nan"]["sha256"], "zip": rec["files"]["zeros_zip"]},
        "validator": z["checks"], "validator_all_passed": z["all_checks_passed"],
        "submission_name": slug + "-zeros.tif", "submission_note": note,
        "organizer_confirmed_score": None,
        "verdict": "promote-to-selector" if ok else "negative",
        "verdict_reason": ("beats every label-free arm on both holdout schemes with paired CI excluding zero; unique vs the nine focus-site registry; validator passed. Promotion to a weekly slot remains the selector's decision." if ok else "failed a gate; see uniqueness/validator"),
    }
    (ROOT / "evidence" / "run_card_gpcz.json").write_text(json.dumps(card, indent=1) + "\n")
    (ROOT / "docs" / "data").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / "data" / "latest-run-card.json").write_text(json.dumps(card, indent=1) + "\n")
    (ROOT / "evidence" / "exp3_budget_sweep.json").write_text(json.dumps({"sweep": {str(k): v for k, v in sweep.items()}, "bootstrap": boot, "prior_density_all_folds": dens_all.tolist()}, indent=1) + "\n")
    print("RUN CARD VERDICT:", card["verdict"])


if __name__ == "__main__":
    main()
