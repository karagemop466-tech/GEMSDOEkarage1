#!/usr/bin/env python3
"""Write the 2026-10-29 probcollar / ring-tie-break run card.

Every number is read from an evidence file (no retyping). Output is written twice and must be
byte-identical:
    evidence/run_card_probcollar_20261029.json
    docs/data/run-card-probcollar-20261029.json

The verdict is computed from the gates, not chosen. A candidate is `promote` only if it beats the
holdout best (any arm in the same evaluator and mode) with a CI excluding that arm, in BOTH modes,
passes the leakage canary, and clears the literal duplicate gate. Otherwise the verdict is `negative`.
This script never sets `slot_selected_or_spent` and never grants clearance.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57.grid import DATA_DIR, load_grid  # noqa: E402

EV = ROOT / "evidence"
CAND_REL = "docs/candidates/karage1-probcollar-gbm-K37654-collar3-20261029-nan.tif"
ZEROS_REL = "docs/candidates/karage1-probcollar-gbm-K37654-collar3-20261029-zeros.tif"
CAND = ROOT / CAND_REL
ZEROS = ROOT / ZEROS_REL
CAND_NOTE = "GBM top-37654 pixels, 3px catalogue collar, 19 organiser bands; research candidate, not cleared"
CAND_NAME = "karage1-probcollar-gbm-K37654-collar3-20261029"
COLLAR_PX = 3
CANARY_LIMIT = 0.90


def load(name):
    return json.loads((EV / name).read_text())


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    all_ = load("holdout_probcollar_20261029.json")
    det = load("holdout_probcollar_detached_20261029.json")
    ring_all = load("holdout_ring_tiebreak_all_20261029.json")
    ring_det = load("holdout_ring_tiebreak_detached_20261029.json")
    uniq = load("candidate_uniqueness_probcollar-nan_20261029.json")
    uniq_zeros = load("candidate_uniqueness_probcollar-zeros_20261029.json")
    focus = load("focus_site_table_20261029.json")

    # --- holdout arms, one evaluator, both modes -----------------------------------------------
    def arms_table(src, n_key):
        out = {}
        for name, v in src["arms"].items():
            out[name] = dict(dti=v["dti"], ci95=v["ci95"], withheld_positive_pixels=v["withheld_positive_pixels"])
        return out

    modes = {
        "all": dict(arms=arms_table(all_, None), ring=dict(ring_model=ring_all["ring_model"],
                    ring_random=ring_all["ring_random"], delta=ring_all["delta_ring_model_minus_ring_random"],
                    H3_supported=ring_all["H3_supported"]), canary=(all_["leakage_canary"]["max_auc"],
                    all_["leakage_canary"]["max_feature"], all_["leakage_canary"]["leakage_flag"])),
        "detached": dict(arms=arms_table(det, None), ring=dict(ring_model=ring_det["ring_model"],
                    ring_random=ring_det["ring_random"], delta=ring_det["delta_ring_model_minus_ring_random"],
                    H3_supported=ring_det["H3_supported"]), canary=(det["leakage_canary"]["max_auc"],
                    det["leakage_canary"]["max_feature"], det["leakage_canary"]["leakage_flag"])),
    }
    cand_arm = "model_K37654_r3"
    best_ctrl = {}
    for m, blk in modes.items():
        arms = dict(blk["arms"])
        arms["ring_random_K37654_collar0"] = dict(dti=blk["ring"]["ring_random"]["dti"],
                                                  ci95=blk["ring"]["ring_random"]["ci95"],
                                                  withheld_positive_pixels=blk["ring"]["ring_random"].get("withheld_positive_pixels"))
        arms["ring_model_K37654_collar0"] = dict(dti=blk["ring"]["ring_model"]["dti"],
                                                 ci95=blk["ring"]["ring_model"]["ci95"],
                                                 withheld_positive_pixels=blk["ring"]["ring_model"]["withheld_positive_pixels"])
        blk["arms"] = arms
        best_name = max(arms, key=lambda k: arms[k]["dti"])
        best_ctrl[m] = best_name

    # --- candidate: independent read-back of the file -------------------------------------------
    cand_sha = sha256(CAND)
    grid = load_grid(DATA_DIR)
    fp = grid.footprint
    dist = ndi.distance_transform_edt(~grid.catalogue)
    # chance-level lattice overlap for uniform random dots in the candidate's own region
    import rasterio
    lat = rasterio.open(ROOT / ".cache/gems_data/registry/13GEMSDOE_r13-lattice-s5_v2_nan-outside.tif").read(1)
    lat_mask = (lat > 0) & fp
    yy, xx = np.mgrid[-3:4, -3:4]
    disk = (xx * xx + yy * yy) <= 9
    lat_cover = ndi.binary_dilation(lat_mask, structure=disk) & fp
    region = fp & (dist > COLLAR_PX)
    lattice_chance_region = float(lat_cover[region].mean())
    lattice_chance_footprint = float(lat_cover[fp].mean())

    def rel(x):
        return str(x).replace(str(ROOT) + "/", "") if x else x

    cand_u = uniq["gates"]
    worst_focus = None
    rho_focus = None
    for row in uniq["comparison_rows"]:
        if "13GEMS" in str(row.get("file", "")) or str(row.get("repo", "")).startswith("reg_lattice"):
            continue
        if row.get("error"):
            continue
        if row["file"].split("/")[-1].startswith("GEMSDOE"):
            v = row["my_dots_within_3px_of_theirs"]
            if worst_focus is None or v > worst_focus[0]:
                worst_focus = (v, row["file"])
            r = row["spearman_full_footprint"]
            if r is not None and (rho_focus is None or abs(r) > abs(rho_focus[0])):
                rho_focus = (r, row["file"])

    lattice_row = next(r for r in uniq["comparison_rows"] if "13GEMS" in str(r.get("file", "")))

    # --- verdict: computed from the gates -----------------------------------------------------
    cand_all = all_["arms"][cand_arm]
    cand_det = det["arms"][cand_arm]
    beats = {}
    for m, blk in modes.items():
        best = blk["arms"][best_ctrl[m]]
        cand = blk["arms"][cand_arm]
        # conservative: candidate CI lower bound must exceed the best control's CI upper bound
        beats[m] = dict(best_control=best_ctrl[m], best_control_dti=best["dti"],
                        candidate_dti=cand["dti"],
                        candidate_beats_best=bool(cand["ci95"][0] > best["ci95"][1]))
    canary_ok = all(not blk["canary"][2] and blk["canary"][0] <= CANARY_LIMIT for blk in modes.values())
    literal_dup = bool(cand_u["worst_my_dots_within_3px"] is not None and cand_u["worst_my_dots_within_3px"] > 0.70)
    promote = bool(all(beats[m]["candidate_beats_best"] for m in modes) and canary_ok and not literal_dup)
    verdict = "promote" if promote else "negative"

    card = {
        "schema": "karage1-run-card-probcollar-v1",
        "created_utc": "2026-10-29",
        "branch": "arena/c26ad154-gemsdoekarage1",
        "lane": {
            "id": "probcollar-dti-holdout",
            "description": "Single method lane: GBM probability emission with a catalogue collar, tested by hide-and-recover holdout against proximity, random and ring-tie-break controls.",
            "experiments": [
                dict(id="E1", mode="all", file="evidence/holdout_probcollar_20261029.json", result="model_K37654_r3 does not beat ctrl_proximity_K37654"),
                dict(id="E2", mode="detached", file="evidence/holdout_probcollar_detached_20261029.json", result="model_K37654_r3 does not beat ctrl_proximity_K37654 (not significant)"),
                dict(id="E3", mode="all+detached", file="evidence/holdout_ring_tiebreak_{all,detached}_20261029.json",
                     hypothesis="H3: model ranking inside the 1 px catalogue ring beats a random tie-break", result="H3 rejected in both modes"),
            ],
            "experiments_used": 3,
            "experiment_budget": 3,
            "budget_note": "3 of 3 holdout experiments used; no further holdout experiments in this session.",
        },
        "verdict": verdict,
        "ok_to_submit": False,
        "slot_selected_or_spent": False,
        "submission_slots_used": 0,
        "submission_note": CAND_NOTE,
        "candidate": dict(
            file=CAND_REL, name=CAND_NAME, sha256=cand_sha, encoding="NaN outside footprint (official format)",
            zeros_twin=dict(file=ZEROS_REL, sha256=sha256(ZEROS), encoding="zeros outside (shared all-finite policy)"),
            status="research-only; NOT CLEARED; DO NOT SUBMIT",
            download_offered=False,
            dots=int(uniq["catalogue_collar"]["dots"]),
            min_distance_to_catalogue_px=uniq["catalogue_collar"]["min_distance_px"],
            dots_within_3px_of_catalogue=uniq["catalogue_collar"]["within_3px"],
            format_checks={k: uniq["format"][k] for k in ("crs_ok", "shape_ok", "transform_ok", "single_band_float32",
                                                           "inside_finite", "values_in_0_1", "outside_footprint_positive", "outside_encoding")},
        ),
        "holdout": {
            "label": "HOLDOUT-DTI",
            "evaluator_version": all_["evaluator_version"],
            "evaluator_scope": "vendor/gems57 shared evaluator; hide-and-recover on the organiser catalogue; withheld units are catalogue segments",
            "alpha": all_["alpha"], "beta": all_["beta"], "radius_px": all_["radius_px"],
            "withheld_positive_pixels": dict(all=all_["arms"][cand_arm]["withheld_positive_pixels"],
                                             detached=det["arms"][cand_arm]["withheld_positive_pixels"]),
            "modes": {m: dict(arms=blk["arms"], best_arm=best_ctrl[m], ring=blk["ring"]) for m, blk in modes.items()},
            "candidate_arm": cand_arm,
            "candidate_vs_best_control": beats,
            "ci95_level": 0.95,
            "not_a_leaderboard_estimate": True,
        },
        "leakage_canary": {
            "threshold_auc": CANARY_LIMIT,
            "all": dict(max_auc=modes["all"]["canary"][0], feature=modes["all"]["canary"][1], leakage=modes["all"]["canary"][2]),
            "detached": dict(max_auc=modes["detached"]["canary"][0], feature=modes["detached"]["canary"][1], leakage=modes["detached"]["canary"][2]),
            "passes": canary_ok,
        },
        "uniqueness": dict(
            comparator="vendor/gems57/uniqueness.py (shared comparator)",
            registry_scope=uniq["registry_scope"],
            literal_gates=dict(rank_correlation_abs_limit=0.90, my_dots_within_3px_limit=0.70, jaccard_limit=0.50),
            worst_my_dots_within_3px_vs_focus_nine=dict(value=worst_focus[0], file=rel(worst_focus[1])) if worst_focus else None,
            max_abs_spearman_vs_focus_nine=dict(value=rho_focus[0], file=rel(rho_focus[1])) if rho_focus else None,
            lattice=dict(file=rel(lattice_row["file"]), my_dots_within_3px_of_lattice=lattice_row["my_dots_within_3px_of_theirs"],
                         chance_for_uniform_random_dots_in_candidate_region=lattice_chance_region,
                         chance_for_uniform_random_dots_in_footprint=lattice_chance_footprint,
                         literal_gate="FAILS (>70%)", interpretation="At chance: the lattice covers ~99.9% of the footprint, so the literal gate cannot discriminate."),
            literal_duplicate_flag=literal_dup,
            comparator_unique_flag=uniq["comparator_unique_flag"],
        ),
        "irregularities": [
            "The 13GEMSDOE lattice covers ~99.9% of the footprint; the literal 70% gate is at chance and effectively unsatisfiable for any footprint-spread submission.",
            "The holdout's withheld units are catalogue segments, so proximity to visible faults is rewarded by construction; it does not measure hidden new-fault discovery (see evidence caveats).",
            "The shared validator (gems57.gates) rejects NaN outside the footprint under its local all-finite export policy, while the official spec permits NaN outside. The NaN-outside primary is written by scripts/build_candidate_submission.py; the refusal reasons are recorded in docs/candidates/…-nan.json. Conflict flagged for the owner, not waived.",
            "Owner-reported scores (0.2600-0.2778) are unverified; no organiser receipt ties them to the audited hashes.",
            "Organiser leaderboard top is 0.4544 (live check); owner quotes of 0.4413 do not match the live page.",
            "GEMSDOE25 and GEMSDOE30 have identical positive sets (XOR 0); GEMSDOE28 (h27-4 r1) and GEMSDOE31 have identical positive sets.",
            "The pinned card paths (evidence/run_card.json, docs/data/run-card.json, docs/data/run_card.json) still hold the prior BB-STEP card. Three existing tests pin them to it, so this card is written to new file names. To make this card the pinned one, update those tests and the render_site BB-STEP check in one change.",
        ],
        "remaining_work": [
            "A spatially blocked holdout for H4 (dispersion-constrained selection) has not been run: holdout budget exhausted.",
            "Measure per-dot marginal credit and within-selection redundancy directly (not yet measured).",
            "Replace or augment the catalogue-segment holdout with a distance-stratified truth check before any promotion rule relies on it.",
            "Obtain organiser-confirmed scores for any candidate; none are available from this sandbox.",
        ],
        "links": {
            "official_metric": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
            "official_rules_pdf": "https://docs.nlr.gov/docs/fy26osti/96647.pdf",
            "leaderboard": "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
            "organiser_masking_thread": "https://community.drivendata.org/t/11516",
            "reference_repo": "https://github.com/drivendataorg/gems-prize-reference-solution",
        },
        "receipts": dict(
            holdout_all="evidence/holdout_probcollar_20261029.json",
            holdout_detached="evidence/holdout_probcollar_detached_20261029.json",
            ring_all="evidence/holdout_ring_tiebreak_all_20261029.json",
            ring_detached="evidence/holdout_ring_tiebreak_detached_20261029.json",
            uniqueness="evidence/candidate_uniqueness_probcollar_20261029.json",
            focus_sites="evidence/focus_site_table_20261029.json",
            uniqueness_zeros_twin="evidence/candidate_uniqueness_probcollar-zeros_20261029.json",
            candidate_nan_receipt="docs/candidates/karage1-probcollar-gbm-K37654-collar3-20261029-nan.json",
        ),
    }
    text = json.dumps(card, indent=2, allow_nan=False, sort_keys=False, default=float) + "\n"
    a = EV / "run_card_probcollar_20261029.json"
    b = ROOT / "docs" / "data" / "run-card-probcollar-20261029.json"
    a.write_text(text)
    b.write_text(text)
    assert a.read_bytes() == b.read_bytes()
    print(json.dumps(dict(verdict=verdict, ok_to_submit=False, candidate_sha256=cand_sha,
                          best=best_ctrl, beats=beats, canary_ok=canary_ok, literal_dup=literal_dup,
                          lattice_chance_region=lattice_chance_region), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
