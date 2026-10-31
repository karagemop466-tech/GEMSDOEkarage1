# Hypotheses and pre-registration — session `arena/9cf124bb-gemsdoekarage1` (31 Oct 2026)

Written **before** any new candidate was scored. Every number labelled HOLDOUT-DTI, PROXY, or
USER-REPORTED / UNVERIFIED. Nothing here is ORGANIZER-CONFIRMED.

## 1. What the official rules say (verified, fetched 31 Oct 2026)

Source: DrivenData competition 306, problem description
<https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>

* Metric: distance-weighted Tversky index, alpha = 0.2, beta = 0.8, triangular kernel with R = 300 m (3 px).
* Initial prize round: truth = "new faults … not contained within the current public USGS database",
  labelled by experts before the competition and held private. Final round rescoring uses the expanded label set.
* Submission: single-band float32 GeoTIFF, EPSG:32611, 100 m, same bounds, values in [0, 1], outside bounds null or NaN.
* The page says the sample submission "predicts total fault absence". The restored mirror of
  `sample_submission.tif` instead has **60,988 positive cells identical to the catalogue** (irregularity IR-S1, see §5).

## 2. Verified facts that shape the hypotheses

* The 9 focus rasters share one grid (EPSG:32611, 3730 x 3292, 100 m). The footprint is 5,167,373 cells.
* Forward 3-px dot overlap is saturated: every focus raster has 88–100% of its dots within 3 px of GEMSDOE24's dots
  (`evidence/nine_site_verification_20261031.json`). The 9-raster union covers only 19.6% of the footprint.
* **GEMSDOE32 B2 is exactly GEMSDOE25 with every dot within 2 px of the mapped catalogue removed**
  (`np.array_equal` = True, 37,654 dots). See `knowledge/why-gemsdoe32-b2-20261031.md`.
* The shared holdout (`gems57-pooled-hide-v2`) scores against withheld *catalogue* segments. The official initial round
  scores against *non*-catalogue faults. Those objectives are not the same (see §5, IR-H1).

## 3. Candidate hypotheses (ranked by expected DTI gain per unit of cost, qualitative)

| Rank | ID | Layers (documented bands) | Physical signature | Why it could catch an unmapped fault | Difference from repo | Named non-fault mimic | Cost | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | **H-O2 halo-prune on a label-free scarp ridge** | `lidar_scarp_features_u8` band 3 `step_max` (USGS 3DEP 1 m, owner-derived) | Sub-metre vertical steps; peaks give dots on scarp crests | Scarps post-date the Qfaults compilation; a label-free surface cannot inherit catalogue bias | Halo rule applied *per fold* from visible catalogue only (leak-free). Used by GPC-Z/HMAS as a fused term, never as a halo-pruned plain ridge | Fan-head or terrace edges, road cuts (TIGER veto not applied here) | Low (CPU, cached) | **Tested this session (E1): NEGATIVE.** HOLDOUT-DTI arm B 0.038756 vs arm A 0.044417 (CI of B−A [−0.006662, −0.004001]); below matched random (0.045875); canary `dist_to_visible_catalogue_px` DI-AUC 0.9085 fails; registry dot overlap 1.0 vs the local halo blanket. Not validated. See `evidence/exp_o2_halo_prune_lidar_20261031.json`. |
| 2 | H-O3 curvature-polarity continuity | `training_features` band 6 `tc`, band 3 `tmi_hg` at two scales | Persistent opposite-sign flanks across scales | Subtle flexure persists where surface scarp is absent | Repo has curvature/ridge families; no polarity-continuity test | Erosional terrace edge, paleoshoreline | Medium | Not run (budget) |
| 3 | H-O4 cross-field boundary displacement | `tmi_hg` and `iso_grav_anom_hg` edges, `depth_to_base_surf` gradient | Signed offset between magnetic and gravity edges | Basin-fill masks surface traces; offset may be diagnostic | **Already tested** as H-K1-SIGNEDOFFSET (session fb1e3550, lost to GPC control) | Intrusive contact | Medium | Not run: near-duplicate of a tested lane |
| 4 | H-O5 stratigraphic-termination | `cond_surf`, `depth_to_base_surf` edge terminations | Edge that stops where lineament continues | Cross-structure truncates a subsurface boundary | Termination topology is new in this repo; untested | Pinch-out or inversion artifact | Medium–high | Not run |

**Top candidate for validation: H-O2** (rank 1: the layer is official, its mechanism is independent of the catalogue,
and the halo rule has an exact precedent in the best-scoring file).

## 4. Pre-registered experiment E1 (= H-O2)

Surface S: `lidar_scarp_features_u8` band 3 (`step_max`), divided by its 98th percentile inside the footprint, clipped to [0, 1],
normalised-convolution smoothed (sigma 1.5 px). Peaks: 3 x 3 local maxima, strongest first, greedy minimum spacing 2.8 px
(same placement as the H-R1 runner's `place_dots`), budget 37,654 dots.

Arms (identical holdout cells, `gems57-pooled-hide-v2`, 16 cells):

* **A (unpruned)**: the top 37,654 peaks.
* **B (halo-pruned, leak-free)**: for each cell, peaks within 2 px of that cell's **visible** catalogue are excluded
  before greedy placement. The visible set is `labels & ~hidden_by_cell[cell]`, so withheld truth never reaches the emission.
* **C (matched random)**: 3 seeds, 37,654 uniform footprint cells, scored on the same cells.
* Reference controls (full-grid evaluate, not fold-specific): H-R1 research raster (previous best under this evaluator),
  B2 and GEMSDOE25 registry rasters. B2 and GEMSDOE25 are built with full-catalogue knowledge, so they are **reference
  only, not valid holdout arms**.

Decision rule (fixed before running):

1. B pooled DTI > A pooled DTI, and the paired cell-bootstrap 95% CI of (B - A) has lower bound > 0.
2. B pooled DTI > matched-random mean (C).
3. Leakage canary: per-cell direction-invariant AUC of each single feature, including `dist_to_visible_catalogue`, is < 0.90.
4. Shared validator passes on the zeros-outside primary, and the catalogue-zero check passes.
5. Literal registry gate: surface Spearman <= 0.90 AND forward dot overlap <= 0.70 against every local TIF.
6. B pooled DTI > the best reference control measured under the same evaluator (H-R1 raster, re-measured here).

A **promote** verdict still does NOT clear a weekly slot: slot selection is a separate step, and the holdout
measures catalogue recovery (§5). Any failed criterion gives **negative**.

Competing hypothesis (what would falsify B's advantage): GPC-Z's own mechanism says unmapped strands sit near mapped ones
in multi-strand zones. If so, the halo pruning removes real strands and B will lose to A.

## 5. Irregularities flagged for review

* **IR-S1** `sample_submission.tif` restored from the mirror has 60,988 positive cells, identical to `labels.tif`
  positives. The official page describes the sample as "total fault absence". Either the mirror differs from the
  organizer file or the page wording is stale. Not resolved; needs owner check against the DrivenData download.
* **IR-H1** The shared holdout measures recovery of withheld catalogue segments, but the official initial round scores
  new non-catalogue faults. B2 is last on the holdout and first on the public board (see the B2 note). A holdout "best"
  is therefore not a reliable proxy for the initial round.
* **IR-U1** The vendored `vendor/gems57/uniqueness.py` and `submission_writer.py` in this checkout do not match the
  upstream bytes at the pinned commit. Upstream `submission_writer.py` matches its pin; the local file differs. Local
  `uniqueness.py` is a fail-closed hardening that differs from upstream. Reported, not silently patched.
* **IR-L1** The reference solution and competition terms were not reviewed in this session beyond the problem page.
