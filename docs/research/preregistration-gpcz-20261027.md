> **Historical preregistration; superseded decision (28 Oct 2026):** The later independent saved-byte audit found the candidate duplicates the registered lattice. Prior positive uniqueness, leakage and promotion claims are not current authorization; no slot was selected. See [`evidence/candidate_audit_20261028.json`](../../evidence/candidate_audit_20261028.json) and [`docs/data/run-card.json`](../data/run-card.json). Historical scores below were not reproduced in this session.

# Pre-registration — lane GPC-Z (written before Experiment 2 was run)

**Session:** Arena `arena/e6d7804d-gemsdoekarage1` · **Date:** 2026-10-27 · **Repository:** `karagemop466-tech/GEMSDOEkarage1`

## Lane (single method paragraph)

**GPC-Z — Gravity-Polarity-Concordant scarp steps in the near-catalogue damage zone.**
A label-free topographic *step-edge* field (Canny-style NMS of the multi-scale gradient of
`det_elev`, fused by rank with |profile curvature| and the 1 m LiDAR `step_max` product) is gated by
a *polarity concordance* term — the cosine between the scarp's downslope azimuth and the
basin-deepening azimuth read from `iso_grav_anom` and `depth_to_base_surf` at 2.5 km — and then
multiplied by a *damage-zone prior* `g(d)`: the empirically measured density of withheld catalogue
strands as a function of distance `d` to the *visible* catalogue, estimated leave-one-fold-out from
the interleaved hide-and-recover holdout. Emission is greedy Poisson-disk dots (spacing 2.8 px)
with every dot within 2 px of the visible catalogue deleted. The named non-fault mimics are
basin-facing alluvial-fan terrace risers and pluvial (Lahontan) shoreline berms, which share the
facing direction but not the step geometry at 1 m, and roads/canals, which are handled by the
concordance gate only partially (flagged, see run card).

## Hypotheses fixed in advance

* **H-A (physics):** polarity concordance enriches true scarps relative to non-tectonic steps.
  *Measured before this file was written (evidence/exp1 screen):* catalogued pixels face the
  basin-deepening direction 70% vs 62% for steep non-catalogue pixels; gating `step` raised the
  blocked-holdout pooled DTI from 0.0436 to 0.0487 at 37,654 dots. **Status: supported, weak.**
* **H-B (obliquity):** fault traces cross contours obliquely over km baselines, shorelines do not.
  *Measured:* AUC 0.42 (catalogued faults are *less* oblique than background: range fronts follow
  contours). **Status: falsified — dropped.** Negative result retained as a deliverable.
* **H-C (damage zone):** new strands cluster within ~1.5 km of mapped strands; a prior `g(d)` fitted
  on visible faults transfers to withheld ones (leave-one-fold-out) and multiplies DTI by > 1.5× at
  a fixed budget on the interleaved holdout **and** does not reduce it on the blocked holdout by
  more than its CI. Canary: `g(d)` alone must stay below AUC 0.90 on withheld truth.
* **H-D (physics adds to the prior):** physics × `g(d)` beats `g(d)` × weak tiebreaker at the same
  budget (otherwise the submission is "a distance-to-catalogue look-up" and must be labelled so).

## Decision rules fixed in advance

* Promote only if GPC-Z beats the best label-free arm of Experiment 1 on the pooled interleaved
  holdout with a paired block-bootstrap 95% CI excluding zero, **and** passes uniqueness
  (rank-correlation ≤ 0.90 with every registry raster; ≤ 70% of dots within 3 px of any single
  registry raster, calibration lattice exempted and flagged), **and** the validator passes.
* Budget chosen among {30,000, 37,654, 44,090} on the holdout; if the holdout is flat, prefer the
  family's live-optimal range (37.6k–44k, OWNER-REPORT) and say so.
* Stop after 3 experiments.

## What a holdout number means here

`HOLDOUT-DTI` on catalogue truth. Across detector families this instrument ranked the owner-reported
live scores only weakly (Spearman ≈ 0.5, n = 12, sibling repository calibration). A gain is a
screen, not a leaderboard estimate; no projection is written as a score.
