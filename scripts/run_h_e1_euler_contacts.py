#!/usr/bin/env python3
"""Experiment E1 of session arena/ce19eeed (31 Oct 2026): hypothesis H-E1.

Hypothesis (ranked #1 in knowledge/hypotheses-20261031.md):
    Magnetic contacts (structural index N = 0) whose Euler-deconvolution depth
    solutions agree on a shallow, reservoir-scale depth band mark buried
    fault-bounded magnetic juxtapositions that have no mapped trace.

Label-blind method (the mapped catalogue is NOT used to build the surface):
    1. field  = official ``tmi`` band (training_features.tif band 14) minus its
       footprint mean; zero outside the valid footprint.
    2. Tx, Ty, Tz = FFT derivatives (Tz positive down; see src/gemskarage1/euler.py).
    3. Windowed Euler, N = 0, 21 x 21 px windows (2.1 km), solutions kept when the
       source lies inside its window and depth is in [300, 3000] m.
    4. S = count of accepted solutions per cell, 3x3 box-smoothed (depth clustering).
    5. Dots = local maxima of S (3x3), strongest first, >= 2.8 px spacing, up to
       the 37,654-dot budget used by every other lane (same as H-R1).

Scoring (shared, unmodified template): vendor/gems57 holdout.build_holdout / evaluate,
evaluator ``gems57-pooled-hide-v2`` (alpha 0.2, beta 0.8, 3 px kernel, 16 cells).
Truth = withheld MAPPED catalogue segments (not the competition's new-fault set).

Controls: matched-count uniform random dots (3 seeds); every local candidate raster
scored on the SAME 16 cells (a holdout league table); the registry GEMSDOE32_B2 raster.

The DECISION_RULE below is fixed before the run and is not edited afterwards.

Usage:  python scripts/run_h_e1_euler_contacts.py
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
DATA = ROOT / "data"
os.environ.setdefault("GEMS_DATA_DIR", str(DATA))
for p in (ROOT, ROOT / "src", ROOT / "vendor"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from gems57 import evaluate_holdout as EH57  # noqa: E402
from gems57 import grid as G57  # noqa: E402
from gems57 import holdout as H57  # noqa: E402
from gems57 import submission_writer as SW57  # noqa: E402
from gems57 import uniqueness as U57  # noqa: E402
from gems57.validate import validate  # noqa: E402
from gemskarage1 import euler as EU  # noqa: E402
from scripts import run_h_r1_kth_magedge as HR1  # noqa: E402  (shared helpers only)

SESSION = "arena/ce19eeed-gemsdoekarage1"
DATE = "2026-10-31"
NAME = "karage1-he1-euler-contacts-37654-20261031-zeros"
NAME_NAN = "karage1-he1-euler-contacts-37654-20261031-nan"
ARCHIVE = ROOT / "archive" / "research-he1-20261031"
NOTE = ("H-E1 Euler contacts (N=0, 2.1 km win, 300-3000 m) label-blind; RESEARCH ONLY; "
        "holdout-scored; do not submit unless gates pass")
EVIDENCE = ROOT / "evidence" / "exp_h_e1_euler_20261031.json"
RUN_CARD = ROOT / "evidence" / "run_card_h_e1_20261031.json"
LEAGUE = ROOT / "evidence" / "holdout_league_20261031.json"

BUDGET_DOTS = 37654
SPACING_PX = 2.8
SEEDS = (101, 202, 303)
N_INDEX = 0.0            # structural index: contact
HALF = 10                # 21 x 21 px window (2.1 km)
DEPTH_BAND_M = (300.0, 3000.0)
DENSITY_SMOOTH = 3
SGMC_PROXY = DATA / "external" / "derived_sgmc_faults_100m_u8.tif"

DECISION_RULE = dict(
    primary_metric="HOLDOUT-DTI pooled, gems57-pooled-hide-v2, 16 cells",
    promote_requires=[
        "candidate pooled DTI > matched-random-null pooled DTI (mean of 3 seeds)",
        "paired per-cell bootstrap 95% CI lower bound of (candidate - null) > 0",
        "leakage canary: every single feature's per-cell direction-invariant AUC < 0.90",
        "shared validator passes on the zeros-outside primary",
        "literal registry gate: surface Spearman <= 0.90 AND final-dot 3 px overlap <= 0.70 vs every local TIF",
        "holdout league: candidate pooled DTI > pooled DTI of EVERY other local TIF scored on the same 16 cells",
    ],
    note=("A promote verdict would still NOT select a weekly slot; slot selection is a separate step. "
          "Dots placed on any registry-overlapping geometry fail the literal gate by construction."),
)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# Field under test. E1 = official TMI (band 14). E2 overrides this (see run_h_e2_euler_gravity.py).
FIELD = dict(name="tmi", band=14)
HYP_ID = "H-E1"
EXP_LABEL = "E1 / H-E1"
CARD_TEXT = dict(
    hypothesis=("Magnetic contacts whose Euler (N=0) depth solutions agree on a 300-3000 m band mark "
                "buried fault-bounded magnetic juxtapositions with no mapped trace."),
    mechanism=("Euler homogeneity identity x.Tx + y.Ty + N.T = x0.Tx + y0.Ty + z0.Tz + N.B solved in 2.1 km "
               "windows; solutions counted per cell (depth-cluster density)."),
    mimic=("Lithologic and intrusive contacts, basin-margin magnetic steps, and flight-line "
           "levelling seams produce the same Euler contact geometry."),
)


def build_surface(foot: np.ndarray) -> dict:
    with rasterio.open(DATA / "training_features.tif") as ds:
        assert ds.descriptions[FIELD["band"] - 1].split(" - ")[0] == FIELD["name"], ds.descriptions[FIELD["band"] - 1]
        raw = ds.read(FIELD["band"]).astype(np.float64)
    valid = foot & np.isfinite(raw) & (raw > -1e30)
    field = np.where(valid, raw - raw[valid].mean(), 0.0)
    tx, ty, tz = EU.fft_derivatives(field, dx_m=100.0, pad=64)
    tx, ty, tz = (np.where(valid, a, 0.0) for a in (tx, ty, tz))
    sol = EU.euler_solutions(tx, ty, tz, field, valid, n_index=N_INDEX, half=HALF,
                             dx_m=100.0, depth_band=DEPTH_BAND_M)
    dens = EU.solution_density(sol, valid, 100.0, smooth=DENSITY_SMOOTH)
    dens = np.where(foot, dens, 0.0)
    s_max = float(dens.max())
    s_norm = (dens / s_max).astype(np.float32) if s_max > 0 else dens.astype(np.float32)
    z = sol["z0"][sol["ok"]]
    return dict(raw=np.where(valid, raw, 0.0), abs_tz=np.abs(tz) * valid, dens=dens, s_norm=s_norm,
                valid=valid, tz=tz, n_solutions=sol["n_solutions"], n_windows=sol["n_windows"],
                depth_median=float(np.median(z)) if z.size else None,
                depth_p10=float(np.percentile(z, 10)) if z.size else None,
                depth_p90=float(np.percentile(z, 90)) if z.size else None,
                s_max=s_max, valid_cells=int(valid.sum()),
                field_valid_fraction_of_footprint=float(valid.sum() / max(foot.sum(), 1)))


def canary_arrays(feats: dict, ctx) -> dict:
    """Per-feature, per-cell AUC of withheld-truth vs other active pixels (label-blind check)."""
    out = {}
    for name, arr in feats.items():
        aucs = {}
        for c in ctx.cells:
            a = np.asarray(arr)[c.bbox]
            act = c.active & np.isfinite(a)
            truth = np.zeros(c.active.shape, bool)
            truth[c.truth_yx] = True
            y = truth[act]
            if y.sum() == 0 or y.sum() == y.size:
                continue
            auc = float(roc_auc_score(y, a[act]))
            aucs[c.key] = dict(auc=auc, direction_invariant=max(auc, 1.0 - auc))
        di = [v["direction_invariant"] for v in aucs.values()]
        out[name] = dict(cells=len(aucs), mean_direction_invariant_auc=float(np.mean(di)) if di else None,
                         max_direction_invariant_auc=float(np.max(di)) if di else None,
                         passed=bool(di and max(di) < 0.90), per_cell=aucs)
    return out


def registry_files() -> list[dict]:
    """Every local GeoTIFF that could be an earlier submission (this run's archive excluded)."""
    seen, rows = set(), []
    patterns = ["registry/*.tif", "docs/downloads/*.tif", "docs/candidates/*.tif",
                "archive/**/*.tif", "data/scored/*.tif"]
    for pat in patterns:
        for f in sorted(glob.glob(str(ROOT / pat), recursive=True)):
            p = Path(f).resolve()
            if p in seen or ARCHIVE.resolve() in p.parents:
                continue
            seen.add(p)
            rows.append(dict(repo="local-repo", submission=p.name, file=str(p)))
    return rows


def league(ctx, foot: np.ndarray, files: list[dict]) -> list[dict]:
    """Holdout DTI of every local raster on the SAME 16 cells (positive pixels = dots)."""
    rows = []
    for rec in files:
        p = Path(rec["file"])
        try:
            with rasterio.open(p) as ds:
                if (ds.height, ds.width) != foot.shape:
                    rows.append(dict(file=str(p.relative_to(ROOT)), skipped="grid mismatch"))
                    continue
                a = ds.read(1).astype(np.float64)
            a = np.nan_to_num(a, nan=0.0)
            emit = (a > 0) & foot
            sc = HR1.score(emit, ctx)
            rows.append(dict(file=str(p.relative_to(ROOT)), emitted=int(emit.sum()),
                             pooled_dti=sc["pooled_dti"], on_visible_catalogue=sc["on_visible_catalogue"],
                             withheld_positives=sc["withheld_positives"]))
        except Exception as exc:  # noqa: BLE001 - recorded, not hidden
            rows.append(dict(file=str(p.relative_to(ROOT)), error=f"{type(exc).__name__}: {exc}"))
    rows.sort(key=lambda r: -(r.get("pooled_dti") or -1))
    return rows


def main() -> None:
    grid = G57.load_grid(DATA)
    foot, cat = grid.footprint, grid.catalogue
    ctx = H57.build_holdout(grid)
    print(f"holdout cells={len(ctx.cells)} withheld={sum(c.n_truth for c in ctx.cells)}", flush=True)

    surf = build_surface(foot)
    print(f"surface valid={surf['valid_cells']} solutions={surf['n_solutions']} "
          f"windows={surf['n_windows']} depth p10/med/p90={surf['depth_p10']}/{surf['depth_median']}/"
          f"{surf['depth_p90']} s_max={surf['s_max']}", flush=True)

    dots = HR1.place_dots(surf["dens"], foot, BUDGET_DOTS, SPACING_PX)
    n_dots = int(dots.sum())
    # Integrity check: every dot must sit on a real depth-cluster peak (count > 0).
    dots_on_zero_density = int((dots & (surf["dens"] <= 0)).sum())
    assert dots_on_zero_density == 0, dots_on_zero_density
    print(f"dots placed={n_dots} (budget {BUDGET_DOTS}); dots on zero-density cells={dots_on_zero_density}",
          flush=True)

    cand = HR1.score(dots, ctx)
    print(f"candidate pooled DTI={cand['pooled_dti']:.5f}", flush=True)

    foot_idx = np.flatnonzero(foot.ravel())
    null_runs = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        nd = np.zeros(foot.size, bool)
        nd[rng.choice(foot_idx, size=n_dots, replace=False)] = True
        sc = HR1.score(nd.reshape(foot.shape), ctx)
        null_runs.append(sc)
        print(f"null seed={seed} pooled DTI={sc['pooled_dti']:.5f}", flush=True)
    keys = [c.key for c in ctx.cells]
    null_cell = np.mean([[r["per_cell_dti"][k] for k in keys] for r in null_runs], axis=0)
    cand_cell = np.array([cand["per_cell_dti"][k] for k in keys])
    delta = cand_cell - null_cell
    d_lo, d_hi = HR1.paired_ci(delta)
    null_pooled = float(np.mean([r["pooled_dti"] for r in null_runs]))

    can = canary_arrays({f"{FIELD['name']} (label-blind raw field)": surf["raw"],
                         "|Tz| vertical derivative": surf["abs_tz"],
                         "euler_depth_cluster_density": surf["dens"]}, ctx)
    for k, v in can.items():
        print(f"canary {k}: max DI-AUC={v['max_direction_invariant_auc']}", flush=True)

    # Holdout league: every local candidate on the same 16 cells.
    files = registry_files()
    lg = league(ctx, foot, files)
    best_other = next((r for r in lg if r.get("pooled_dti") is not None
                       and not r["file"].endswith(NAME + ".tif")), None)
    league_out = dict(schema="holdout-league-v1", evaluator=EH57.VERSION, cells=len(ctx.cells),
                      rows=lg, top=lg[:10], note=("Binary emission = positive pixels. Rasters built from "
                      "the full mapped catalogue (e.g. the nine focus submissions) are NOT label-blind "
                      "and their holdout values are leakage-prone; they are listed for transparency."))
    LEAGUE.write_text(json.dumps(league_out, indent=2, sort_keys=True, default=float) + "\n")
    print(f"league rows={len(lg)} best other={best_other and best_other['file']} "
          f"{best_other and round(best_other['pooled_dti'], 5)}", flush=True)

    # Secondary proxy (informational only).
    with rasterio.open(SGMC_PROXY) as ds:
        sgmc = (ds.read(1) > 0) & foot
    d_cat = ndi.distance_transform_edt(~cat)
    sgmc_off = sgmc & (d_cat > 3.0)

    def random_mask(seed):
        rng = np.random.default_rng(seed)
        m = np.zeros(foot.size, bool)
        m[rng.choice(foot_idx, size=n_dots, replace=False)] = True
        return m.reshape(foot.shape)

    proxy = dict(candidate=HR1.proxy_recall(dots, sgmc_off),
                 random_null_mean=float(np.mean([HR1.proxy_recall(random_mask(s), sgmc_off)["recall_within_3px"]
                                                 for s in SEEDS])))

    # Artefacts: shared writer (zeros outside, the gated primary) + NaN-outside twin.
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    values = dots.astype(np.float32)
    note = NOTE
    assert len(note) <= 140 and len(NAME) <= 140
    tif_path = ARCHIVE / f"{NAME}.tif"
    receipt = SW57.write_submission(tif_path, values, DATA / "sample_submission.tif", foot,
                                    note=note, name=NAME, catalogue=None,
                                    metadata=dict(session=SESSION, hypothesis=HYP_ID, date=DATE))
    v_zero = validate(tif_path, foot, None)
    nan_vals = np.where(foot, values, np.float32("nan")).astype(np.float32)
    nan_path = ARCHIVE / f"{NAME_NAN}.tif"
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

    # Uniqueness: pre-placement surface and final dots, vs every local TIF.
    reg = files
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

    surface_worst, dot_worst = worst(surface_rows), worst(dot_rows)
    dot_rows_ok = [r for r in dot_rows.get("rows", []) if "error" not in r]
    over_gate = [dict(file=r["file"], my_dots_within_3px=r["my_dots_within_3px_of_theirs"],
                      their_dots=r["their_dots"]) for r in dot_rows_ok
                 if r["my_dots_within_3px_of_theirs"] > 0.70]
    focus = [r for r in dot_rows_ok if Path(r["file"]).parent == ROOT / "registry"]
    gate_rho = surface_worst.get("max_spearman") is not None and surface_worst["max_spearman"] <= 0.90
    gate_ov = dot_worst.get("max_my_dots_within_3px") is not None and dot_worst["max_my_dots_within_3px"] <= 0.70

    best_other_dti = best_other["pooled_dti"] if best_other else None
    crit = dict(
        candidate_beats_null_pooled=bool(cand["pooled_dti"] > null_pooled),
        paired_ci_lower_bound_gt_zero=bool(d_lo > 0),
        canary_all_below_0_90=all(v["passed"] for v in can.values()),
        validator_passed=bool(v_zero["all_checks_passed"]),
        registry_surface_rho_le_0_90=bool(gate_rho),
        registry_dot_overlap_le_0_70=bool(gate_ov),
        beats_every_local_candidate_on_same_cells=bool(best_other_dti is not None and cand["pooled_dti"] > best_other_dti),
    )
    promote = all(crit.values())
    verdict = "promote-to-selector" if promote else "negative"

    out = dict(
        schema="karage1-exp-he1-v1", session=SESSION, date_utc=DATE, field=FIELD["name"],
        evaluator=dict(module="vendor/gems57 evaluate_holdout/holdout (unmodified)", version=EH57.VERSION,
                       label="HOLDOUT-DTI", alpha=0.2, beta=0.8, kernel_px=3.0, cells=len(ctx.cells),
                       withheld_positives=sum(c.n_truth for c in ctx.cells),
                       truth_is="withheld MAPPED catalogue segments (not the competition's new-fault test set)",
                       implementation_hashes=EH57.implementation_hashes()),
        decision_rule=DECISION_RULE,
        inputs=dict(data_dir=str(DATA), data_status="pinned third-party mirrors; organizer authenticity NOT established",
                    training_features_sha256=sha256(DATA / "training_features.tif"),
                    sample_submission_sha256=sha256(DATA / "sample_submission.tif"),
                    grid_footprint_cells=int(foot.sum())),
        hypothesis_parameters=dict(structural_index=N_INDEX, window_px=2 * HALF + 1, window_m=(2 * HALF + 1) * 100,
                                   depth_band_m=list(DEPTH_BAND_M), density_smooth_px=DENSITY_SMOOTH,
                                   spacing_px=SPACING_PX, budget=BUDGET_DOTS),
        surface=dict(valid_cells=surf["valid_cells"], euler_solutions_accepted=surf["n_solutions"],
                     windows_with_full_support=surf["n_windows"], depth_p10_m=surf["depth_p10"],
                     depth_median_m=surf["depth_median"], depth_p90_m=surf["depth_p90"], s_max=surf["s_max"]),
        candidate=dict(dots=n_dots, budget=BUDGET_DOTS, shortfall_vs_budget=BUDGET_DOTS - n_dots,
                       dots_on_zero_density_cells=dots_on_zero_density,
                       on_visible_catalogue=cand["on_visible_catalogue"], holdout=cand),
        controls=dict(random_null_matched_count=dict(seeds=list(SEEDS),
                                                     pooled_dti_per_seed=[r["pooled_dti"] for r in null_runs],
                                                     pooled_mean=null_pooled),
                      best_other_local_candidate=best_other, league_file=str(LEAGUE.relative_to(ROOT))),
        paired_vs_null=dict(mean_delta=float(delta.mean()), ci95=[d_lo, d_hi],
                            per_cell_delta=dict(zip(keys, delta.tolist()))),
        leakage_canary=can,
        proxy_sgmc_offcatalogue=proxy,
        artefacts=dict(zeros_primary=dict(file=str(tif_path.relative_to(ROOT)), sha256=receipt["sha256"],
                                          bytes=receipt["bytes"], name=NAME, note=note, note_chars=len(note),
                                          validator_checks=v_zero["checks"],
                                          validator_all_passed=v_zero["all_checks_passed"],
                                          submission_slots_used=0, approved_for_weekly_slot=False),
                       nan_outside_twin=dict(file=str(nan_path.relative_to(ROOT)), sha256=sha256(nan_path),
                                             checks=nan_checks)),
        uniqueness=dict(registry_rasters_scanned=len(reg), surface_pre_placement=surface_worst,
                        final_dots=dot_worst, dot_gate_trips_70pct=over_gate,
                        registry_focus_rasters_compared=len(focus),
                        rows_surface=surface_rows.get("rows"), rows_dots=dot_rows.get("rows")),
        criteria=crit, verdict=verdict,
        ok_to_submit=bool(promote and nan_checks["all_passed"]),
        slot_selected_or_spent=False,
    )
    EVIDENCE.write_text(json.dumps(out, indent=2, sort_keys=True, default=float) + "\n")
    card = dict(
        schema="karage1-run-card-v1", session=SESSION, date_utc=DATE, experiment=EXP_LABEL,
        hypothesis=CARD_TEXT["hypothesis"], field=FIELD["name"],
        mechanism=CARD_TEXT["mechanism"],
        named_non_fault_mimic=CARD_TEXT["mimic"],
        holdout=dict(evaluator=EH57.VERSION, pooled_dti=cand["pooled_dti"], withheld_positives=cand["withheld_positives"],
                     ci95_cell_bootstrap_of_mean_cell_dti=cand["ci95_cell_bootstrap_of_mean"],
                     random_null_pooled_mean=null_pooled, paired_delta_ci95=[d_lo, d_hi],
                     label="HOLDOUT-DTI (withheld mapped catalogue segments; not organizer-confirmed)"),
        registry_overlap=dict(surface_max_spearman=surface_worst.get("max_spearman"),
                              final_dots_max_3px_overlap=dot_worst.get("max_my_dots_within_3px"),
                              max_overlap_file=dot_worst.get("max_overlap_file"),
                              rasters_compared=dot_worst.get("rows_compared")),
        raster=dict(file=str(tif_path.relative_to(ROOT)), sha256=receipt["sha256"], name=NAME, note=note,
                    note_chars=len(note)),
        validator=dict(all_passed=v_zero["all_checks_passed"], checks=v_zero["checks"]),
        verdict=verdict, ok_to_submit=out["ok_to_submit"],
        criteria=crit,
    )
    RUN_CARD.write_text(json.dumps(card, indent=2, sort_keys=True, default=float) + "\n")
    print(f"verdict={verdict}; ok_to_submit={out['ok_to_submit']}; wrote {EVIDENCE.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
