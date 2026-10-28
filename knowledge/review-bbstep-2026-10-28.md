# BB-STEP session review — 28 October 2026

> **Integration correction, session `5c261093`:** The material below is an
> inherited parallel-session record, not an approved or protocol-compliant
> experiment. No owner-assigned lane was identified; the run used local
> `gemsk` rather than the agreed shared evaluator/writer, and performed the
> reported surface comparison after placement. EXP2's fold-local result used
> different parameters from the saved EXP3 raster, and the B2 control used a
> fixed full-catalogue-thinned raster while the candidate was emitted fold
> locally. Its sampled uniqueness code also substitutes zero for a non-finite
> rank correlation, which is not a passing canary. Therefore the reported
> comparison does not establish that the saved TIFF beats B2. Of 60,988 assigned withheld positives, 60,625 contributed
> after the active mask in the recorded pooled terms. The third "experiment"
> was a four-setting sweep whose budget interpretation is unresolved. An
> independent [saved-byte replay](../evidence/bbstep_independent_audit_5c261093.json)
> confirms both TIFF variants fail the lattice stop. The runner is quarantined;
> do not rerun or submit either file.

## Decision

**NEGATIVE. DO NOT SUBMIT.** Generated
`karage1-bbstep-buried-basement-20261028T180000Z-zeros.tif`
(SHA-256 `72312302675d65cd1983239dd436412b5db1118a7c08f2a5807ef436b5536d6a`,
17,766 dots). Unique versus the nine focus sites; literal lattice duplicate.

## Why GEMSDOE32 B2 reported 0.2778

USER-REPORTED / UNVERIFIED. On the mirrored grid, B2 is GEMSDOE25 d2.8 with
6,436 dots within 2 px of the catalogue removed; no dots added. GEMSDOE25 and
GEMSDOE30 have identical positive masks. Thinning near known (masked) pixels
can reduce false-positive mass in the [distance-weighted Tversky](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric)
(α=0.2, β=0.8, 300 m). [Staff](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)
say known pixels are masked, not a free 300 m buffer. Causation is unproven.

## Can we beat 0.2778?

Not established. BB-STEP hunts buried low-slope basement steps, the opposite
population of the H19-5 scarp family. Catalogue hide-and-recover is a negative
control for this hypothesis (canary AUC 0.44 on the combined surface). Live
expert labels may still be scarp-like. No organizer receipt exists here.

## Experiments

1. Canary: max AUC 0.53, no alarm, no label reads.
2. Fold-local HOLDOUT-DTI 0.03179 [0.02714, 0.03627] vs B2 0.00485 on
   `gemsk-hide-recover-v1`, n=60,988. Not an organizer score.
3. Sweep best: slope gate 0.55 + RTP corroboration, fold-local DTI 0.03398.

## Irregularities

- No method-lane paragraph was supplied; BB-STEP was preregistered as the
  working lane for this session.
- Lattice covers 99.87% of the footprint within 3 px; any dense map fails
  uniqueness unless dots are placed in 6,649 uncovered cells (evasion, refused).
- Owner mirrors are not organizer-authenticated.
- Official format wants NaN outside bounds; zeros twin also written because a
  prior portal message said values must be in [0,1]. Cause of that rejection
  remains unknown.
