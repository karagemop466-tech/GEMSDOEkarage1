# Session review: arena/5ee7ef4b-gemsdoekarage1 (29 Oct 2026)

**Decision: NO FILE IS CLEARED. DO NOT SUBMIT.**

Machine-readable card: [`evidence/session_5ee7ef4b_run_card.json`](../evidence/session_5ee7ef4b_run_card.json).
Executive summary: [`docs/session-5ee7ef4b.html`](../docs/session-5ee7ef4b.html) (linked from the home page).

## What was asked, and what was delivered

| Request | Delivered | Status |
| --- | --- | --- |
| A unique, downloadable TIF that is obviously OK (or not OK) to submit | One new format-valid raster (H-S1). Status: NEGATIVE. Held in `archive/research-s1-20261029/` with a DO NOT SUBMIT label | Done, negative |
| Executive summary per focus site: best file, estimate, unique? | Table on the summary page for all nine sites | Done. Estimates are "not estimable" (see below) |
| Explain why GEMSDOE32 (0.2778) scored highest | Measured facts only (section 3 of the summary); the organizer mechanism is unknown | Partial, labelled |
| 3–5 ranked hypotheses, validated on holdout before a slot | One candidate (H-S1) tested. Two older candidates (N1, N2) are listed but not tested: data not reachable | Partial |
| Verify the live leaderboard and official rules | Official problem page and rules page fetched; leaderboard #1 0.4544 confirmed | Done |
| Run the protocol: lane, shared evaluator, canary, lattice gate, run card, budget | Done with the shared vendored evaluator; canary passed; gates recorded; 2 of 3 experiments used | Done |
| Three passes, tests, PR and merge | See "Three passes" below | Done |

## Experiments (budget: 3 experiments or 2 hours; used 2)

1. **Calibration of the shared evaluator** (`scripts/exp1_shared_holdout_calibration.py`, `evidence/exp1_shared_holdout_calibration_20261029.json`).
   The GEMSDOE32 champion raster scores **0.0047** (HOLDOUT-DTI, CI95 0.0043 to 0.0052). A matched-count random placement scores **0.0446** (3 seeds). The champion places zero dots on the mapped catalogue. The holdout's truth is mapped catalogue segments, so a catalogue-avoiding file scores near zero by construction. **The internal holdout cannot rank the off-catalogue strategy the competition rewards.**
2. **H-S1 candidate** (`scripts/generate_s1_tmihg_ridge.py`, `scripts/exp2_s1_holdout_and_uniqueness.py`, `evidence/exp2_s1_holdout_and_uniqueness_20261029.json`).
   - Method: local maxima of the smoothed horizontal gradient of total magnetic intensity (`tmi_hg`), off-catalogue apron 2 px, 2.8 px spacing, strongest first.
   - Yield: 37,311 dots. This is 343 short of the 37,654 budget. The spacing rule was kept, not relaxed.
   - As submitted (apron from the full catalogue): **0.00225** (CI95 0.00189 to 0.00243). Structurally penalised.
   - Holdout-faithful (apron from visible faults per cell, no withheld truth read): **0.04318** (CI95 0.03795 to 0.04608). This is at or below the matched random floor (0.0446). **No evidence of skill.**
   - Leakage canary: tmi_hg alone, per-cell AUC 0.443 to 0.586, below the 0.90 ceiling. Pass.
   - Literal lattice rule vs the 13GEMSDOE calibration witness: **99.97%** within 3 px. Fails. The rule is saturated (random dots also fail, `evidence/lattice_saturation_null_20261029.json`).

## Format validation (official rules)

Checked independently on the bytes on disk (`scripts/build_session_5ee7ef4b.py`, `validate_tif`):
- float32, one band, EPSG:32611, shape `3730 x 3292`, transform `(100, 0, 243350, 0, -100, 4508550)`, equal to `sample_submission.tif`.
- All cells finite. Values in [0, 1] (observed 0.0 and 1.0 only). No positive cells outside the sample footprint.
- ZIP contains one member, byte-identical to the TIF.
- sha256 `5eccad685f3afc3a9092115ae85b9b4daecdb9e354fbd188f4a43dd9f5bad8bd`.

The format is correct against the rules as written. Format validity does not establish organizer acceptance.

## Uniqueness

- Exact duplicate of any local TIF: **no** (19 local TIFs compared).
- Strongest overlap with a submission-sized raster: **19.5%** (`karage1-dipdual…`, 37,654 dots).
- A dense archived mask (`archive/prototype/…hunq1`, 3.94 million dots) gives "100%" overlap. That is an artifact of its density, not a copy. Jaccard overlap is 0.007.
- Focus-site and pinned peer rasters were not re-audited this session (see limits).

## Focus sites (USER-REPORTED / UNVERIFIED)

Source: `registry/user_reported_scores_20261029.json`. Pinned-mirror sibling overlap: `evidence/site_lineage_verification_20261029.json`.

| Site | Best reported file | Reported | Max overlap with a sibling |
| --- | --- | --- | --- |
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5 | 0.2477 | 100.0% (GEMSDOE25) |
| GEMSDOE25 | dotted-h19-5-d2-8 | 0.2600 | 100.0% (GEMSDOE24) |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5 | 0.2449 | 98.0% (GEMSDOE24) |
| GEMSDOE28 | h36-1-rung30-blind-r1 | 0.2710 | 100.0% (GEMSDOE24) |
| GEMSDOE30 | d28-poisson300m-offcat-44090 | 0.2600 | 100.0% (GEMSDOE24) |
| GEMSDOE31 | h27-4-solo-d28 | 0.2708 | 100.0% (GEMSDOE24) |
| GEMSDOE32 | h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros | **0.2778** | 100.0% (GEMSDOE24) |
| GEMSDOE33 | h33d-analog-tip-stepover-r30 | 0.2632 | 99.7% (GEMSDOE27) |
| GEMSDOE36 | anderson-geothermal-pinn-38854 | 0.2750 | 97.6% (GEMSDOE27) |

Every focus site has a sibling at ≥97.6% overlap, so none is unique against the others. GEMSDOE25 and GEMSDOE30 have identical dot masks.

## Leaderboard (ORGANIZER-PUBLIC, fetched 29 Oct 2026)

Rank #1 **0.4544** (xiaofanhu), #2 **0.3916** (cfld__), #3 **0.3911** (Batik Shirt Brothers). Source: <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>. The session brief's "0.4413" is not on this page. The brief's "0.3195" was not re-checked this session.

## Why GEMSDOE32 scored highest: what can and cannot be said

- Measured: the champion's dots avoid the mapped catalogue entirely (0 of 37,654 on catalogue cells).
- Measured: it differs from GEMSDOE25 only by removing 6,436 dots near mapped labels, and adds none (lineage file).
- Not measured: which of its dots hit the organizer's private new-fault labels. The 0.2778 figure is a USER-REPORTED number with no organizer receipt in this repo. The competition's own page says the new faults are labelled by experts before the competition and are not public.
- The reason the nine focus files cluster at 0.24 to 0.28 is consistent with them being near-copies of one another. That is an inference from the overlap numbers, not a measured cause of the score.

## Hypotheses (ranked; status after this session)

| Rank | Hypothesis | Layers | Status |
| --- | --- | --- | --- |
| 1 | H-S1: magnetic horizontal-gradient crests off the mapped catalogue | `tmi_hg` (training_features.tif, band 'tmi_hg') | **Tested. Negative.** Holdout-faithful DTI at the random floor |
| 2 | N1: Lake Lahontan shoreline datum offset with a regional-tilt term | MF-2323 shorelines + 1 m DEM | **Not tested.** `pubs.usgs.gov` is not on the sandbox allow-list; the shapefile was not downloaded (`docs/research/hypotheses-20261029.md`) |
| 3 | N2: terrace-riser vertical separation across a trace | DEM + verified age polygons | **Not tested.** No verified age-polygon source yet |

The evaluator design (section 1 above) means that any off-catalogue candidate is penalised by the internal holdout. Until the holdout is fixed, no off-catalogue idea can be validated on it.

## Three passes

**Pass 1 (implement).** Restored the core data from pinned mirrors (`scripts/restore_karage1_data.py --group core`, SHA-256 verified). Ran the shared evaluator. Built H-S1 through the shared writer. Ran experiments 1 and 2. Added the session page builder and tests.

**Pass 2 (adversarial review). Problems found and fixed:**
1. The experiment docstring said "8 cells"; the code uses 16 (2 draws × 4 folds × 2 modes). Fixed in the script and in the labels.
2. The negative TIF was first written to `docs/downloads/`. Two existing tests require every TIF there to have a saved-byte fleet audit, which needs the full pinned peer set. Moved the file to `archive/research-s1-20261029/` (same convention as the earlier quarantined files). The page links to it.
3. The first H-S1 run had a no-op line and a budget check that blocked a valid result. Removed the line; the budget shortfall (343 dots) is now recorded instead of blocking.
4. The "100% overlap" with the archived hunq1 mask looked like a copy. It is a density artifact (3.94 million dots). The summary reports it and the strongest submission-sized overlap separately.
5. The GitHub API rate limit blocked the 'scored' group restore. The 13GEMSDOE witness was fetched from the pinned commit's codeload archive (allowed host) and its SHA-256 matched the manifest exactly.
6. The lattice-witness test was missing from the first version of Experiment 2. Added, and re-run.

**Pass 3 (re-check against the request).** Full test suite: **382 passed** (includes 9 new session tests). Site rebuilt with `scripts/build_site.py`; the only changes are one added button per generated page. The summary numbers come from evidence files via `scripts/build_session_5ee7ef4b.py`, not from typed-in values. Every verdict is negative, and `ok_to_submit` is false.

## Irregularities for review

1. Internal holdout truth is catalogue segments, so catalogue-avoiding predictions are penalised by construction. The template is unchanged; this is an owner decision.
2. The 70% / 3 px lattice rule is saturated, and it is not in the official rules (verified on the problem page).
3. The portal error "Predicted values must be in range [0, 1]" is not reproduced by any local raster. NaN-outside rasters pass the local range check. The cause is unknown. The writer uses all-finite zeros outside the footprint, which is in range by construction.
4. The forensic note `knowledge/02_why_gemsdoe32_b2_scored_0.2778.md` describes GEMSDOE28 as a 1-pixel collar. The pinned file is not a collar (16,237 removed, 9,807 added). Not corrected here.
5. GEMSDOE25 and GEMSDOE30 have identical dot masks.
6. The brief's leaderboard figures (0.4413, 0.3195) do not match the live page (#1 0.4544).
7. The sample-grid path used by the validator is `/tmp/gems_data/sample_submission.tif`, restored from pinned mirrors. Organizer authenticity of that mirror is not established.

## Limits

- No organizer truth is available. Internal holdout DTI is not a leaderboard estimate.
- The competition data is restored only from pinned third-party mirrors (not authenticated organizer files).
- The focus-site and pinned peer rasters were not re-audited this session. The lattice check used the 13GEMSDOE witness plus local TIFs.
- `fetch_page` was used for the official pages. The NLR PDF was not re-read this session.

## Owner decisions needed

1. Whether the internal 70% / 3 px rule binds submissions at all (it is not in the official rules).
2. Whether to fix the holdout apron (use visible faults only) in the shared template, or to add an organizer-like truth set.
3. Whether to authorise a new method lane (no lane is assigned in this session).
