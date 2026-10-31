# Repository review — 31 October 2026

## Executive decision

**Verdict: NEGATIVE / DO NOT SUBMIT from this review. Do not spend a competition slot.** The repository contains a locally format-validated candidate GeoTIFF, but the evidence does not establish organizer acceptance, a trustworthy leaderboard score estimate, or clearance under the prompt's literal duplicate rule. The earlier README banner saying “OK TO SUBMIT” conflicts with later review sections and with the candidate's own evidence; it has been corrected to fail closed.

The existing candidate is `docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif` (SHA-256 recorded in `evidence/kp1_run_card.json`). It was not generated in this review. Local format validation reported 15/15 checks, including single-band float32, EPSG:32611, 3730×3292, matching transform, finite values in [0,1], and zero outside the footprint. This is **local validation only** and not organizer acceptance.

## What the evidence supports

- **USER-REPORTED / UNVERIFIED:** the highest listed focus-site score is GEMSDOE32 B2 at 0.2778. The prompt also gives 0.3195 and 0.4413 as leaderboard values, but these are not substantiated by an organizer receipt in the repository's current review evidence.
- **MEASURED (repo analysis, not leaderboard score):** the nine focus-site rasters are highly overlapping variants. The earlier measured analysis records a median pairwise 3-pixel overlap of 95.42%, and B2 is a subset of GEMSDOE25 with 6,436 dots removed. See `evidence/nine_site_executive_20261031.json` and the referenced audit scripts for the exact methods.
- **HOLDOUT-DTI:** the KP1 candidate has pooled DTI 0.076408 on the SGMC off-catalogue instrument (62,122 withheld positive cells; 4 spatial folds; evaluator `gems57-pooled-hide-v2` extended with independent off-catalogue truth). The reported block-bootstrap 95% interval in `evidence/kp1_run_card.json` is [-0.00337, 0.02604] for the candidate-minus-random difference, not a CI for the raw candidate DTI. Its sign uncertainty and the documented reverse/weak calibration with focus-site scores prevent using it to predict leaderboard performance.
- **PROJECTED, NOT A SCORE:** the run card's 0.27892 is an extrapolative fit from nine user-reported score/raster pairs. The card itself warns of model-form uncertainty and out-of-range extrapolation. It must not be presented as a reliable estimate and does not establish superiority over 0.2778.
- **Uniqueness:** the KP1 card reports max absolute Spearman 0.007607 and maximum 3-pixel overlap 0.265281 against its nine focus rasters, which clears the focus-site-only thresholds. But the prompt says compare against “any registry raster.” The same card says `literal_gate_saturated: true`; other repo reviews document overlap with a dense 13GEMS lattice/blanket that trips this literal rule. Therefore the evidence does not support a global “unique / OK” verdict.

## Nine-site executive table

Scores below are **USER-REPORTED / UNVERIFIED** from the supplied prompt. Leaderboard score estimates are **NOT ESTIMABLE** from repository holdouts: the internal holdout is not shown to calibrate to organizer scoring, and there is no receipt for these files. “Unique” here means only unique against the other eight named focus-site rasters, not against every registry raster.

| Site | Highest listed submission | Reported score | Focus-set uniqueness | Score estimate | Download/submit verdict |
|---|---|---:|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 | No; near-identical family | Not estimable | No; historical file, no clearance |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 | No; B2 is a subset and peers heavily overlap | Not estimable | No; historical file, no clearance |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 | No; heavily overlapping family | Not estimable | No; historical file, no clearance |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 | No; heavily overlapping family | Not estimable | No; historical file, no clearance |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 | No; same dot pattern as GEMSDOE25 per repo audit | Not estimable | No; historical file, no clearance |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 | No; heavily overlapping family | Not estimable | No; historical file, no clearance |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | 0.2778 | No; subset of GEMSDOE25, not independently unique | Not estimable | No; highest listed focus value, but do not resubmit |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 | No; heavily overlapping family | Not estimable | No; historical file, no clearance |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 | No; heavily overlapping family | Not estimable | No; historical file, no clearance |

The table's entries are sourced from the user-provided list; repository measurements/lineage are described separately above and in `evidence/nine_site_executive_20261031.json`. These do not prove that every historical file was submitted under that exact name or score.

## Conflicts and protocol findings

1. The README had contradictory top-level statuses: one older section promoted KP1 while newer session sections said no file was cleared. Fail-closed resolution is now used pending evidence.
2. KP1's file is distinct from the nine focus-site rasters under the reported pairwise checks, but the global registry duplicate gate is not passed or resolved. The run card explicitly marks its literal gate saturated.
3. The prompt requires exactly one assigned method paragraph/lane, but the lane paragraph is not present in the supplied text. Previous repo notes explicitly flag the method lane as unassigned. This review does not invent a lane or run another experiment.
4. The required experimental budget is already recorded as 3/3 in the KP1 run card. No further experiment was run; doing so would breach the stated cap. The shared holdout tools are present, but the latest candidate-specific scientific evidence has calibration limitations.
5. The requested official-source verification cannot be asserted from repository content alone. No live external pages or organizer receipt were fetched in this review. The official/manual-review URLs are collected in `knowledge/official-sources-20261031.md` and `docs/sources.md`.
6. The prompt calls for candidate hypotheses before implementation. Existing hypothesis documents in `knowledge/` provide prior slates; no new hypothesis was implemented because the session lane and remaining experiment budget are unresolved.

## Three-pass review

- **Pass 1 — inspect:** reviewed README status, recent evidence/run cards, the focus-site evidence references, available scripts/tests, and candidate artifact presence. Identified conflicting submit verdicts and the distinction between local format validation, holdout DTI, projection, and organizer result.
- **Pass 2 — adversarial review:** checked the literal registry gate, holdout calibration warning, experiment budget, and absence of an organizer receipt. Corrected the conclusion to avoid equating focus-set uniqueness or local validator success with permission to submit.
- **Pass 3 — request fit:** preserved the existing candidate and research records, made the top README verdict explicit, and recorded the scope/limitations and next actions. No weekly slot was selected and no new experiment was performed.

## Next actions

1. Resolve the global registry overlap policy (including dense blanket/lattice rasters) and identify the intended assigned lane in writing.
2. Obtain a valid organizer receipt or authorized held-out scoring protocol; do not call any projection a score.
3. Reconcile the current official submission format/rules against an authenticated organizer sample and record the source/retrieval date.
4. Only after a valid lane and a fresh experiment budget are established, pre-register at most three experiments and run the shared canary + blocked holdout before considering a candidate.
5. Keep the existing TIF marked research-only until the duplicate gate and score validation are resolved. No slot is selected by this review.

## JSON run card

```json
{
  "hypothesis": "No new geological hypothesis tested; review is limited to auditing the existing KP1 candidate and repo evidence.",
  "mechanism": "Not applicable: no new candidate or experiment was built.",
  "named_non_fault_process_that_could_mimic_it": "Not assessed for a new candidate; KP1's prior run card lists buried pluton/caldera margins, alluvial contact springs, regional fabric, landslides, and fluvial cut banks as mimics.",
  "holdout_dti": {
    "label": "HOLDOUT-DTI (existing evidence, not rerun)",
    "value": 0.07640846770050778,
    "evaluator": "gems57-pooled-hide-v2 extended with SGMC off-catalogue truth",
    "withheld_positive_cells": 62122,
    "folds": 4,
    "95_percent_ci": null,
    "ci_note": "The existing [−0.00337, 0.02604] interval is for candidate-minus-random difference, not raw candidate DTI."
  },
  "correlation_overlap_vs_registry": {
    "label": "MEASURED (existing evidence)",
    "focus_raster_max_abs_spearman": 0.007607,
    "focus_raster_max_3px_overlap": 0.265281,
    "global_registry_gate": "unresolved/fails literal gate; run card marks literal_gate_saturated true"
  },
  "raster_sha256": "30a5fc28ff060ad38681d9b721024aea5aec3b070f407537dd28354efbe0ff0d",
  "validator_output": "Existing evidence reports 15/15 local format checks; not organizer acceptance. Not rerun in this review.",
  "submission_name": "karage1-kp1-ttca-springalter-far-conduit-32000-20261031",
  "submission_note": "Research artifact; local format checks pass; global uniqueness/organizer score not established. DO NOT SUBMIT.",
  "verdict": "negative"
}
```
