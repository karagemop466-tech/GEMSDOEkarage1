# Owner brief — 27 October 2026

Read this file and README before every session. This is a **normalized requirements record**, not a verbatim transcript of the very long, repeated request. Historical owner-supplied scores remain claims, preserved in the linked source snapshots; they are not organizer receipts.

## Outcome and core values
Maximize P(Win): prefer reproducible scientific evidence over optimistic leaderboard projections. Own the Outcome: automate checks, fix defects, preserve negative findings, and report obstacles rather than manufacturing a successful artifact.

## Mandatory operating requirements
- Focus on GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36; review their highest owner-reported historical submissions and explain H33-B2's apparent advantage.
- Generate a scientifically distinct, unique single-band GeoTIFF only within the assigned method lane; do not copy old predictions, jitter dots, or rename old files as new work.
- The supplied request refers to a single assigned method paragraph but includes none. Do not silently pick a lane for a parallel run.
- Reuse the designated template's cached features, evaluate_holdout.py and submission_writer.py. Fix any defect upstream once, not in a private evaluator fork.
- Whole-segment buffered hide-and-recover; recompute every catalogue-dependent feature using visible faults only; mask visible faults pixel-exactly. Pooled DTI: alpha .2, beta .8, triangular kernel 300 m. Record evaluator version, withheld positives, spatial bootstrap 95% CI.
- Test every feature alone. AUC above .90 is a leakage alarm until resolved. No random-pixel CV or all-catalogue distance feature may be sold as spatial validation.
- Check source surface before placement AND final dots against the entire registry. Spearman above .90 OR directional dot overlap above .70 within Euclidean 3 px means duplicate: log and stop. Hash uniqueness alone is insufficient.
- Before implementation propose and rank 3–5 geological hypotheses with layers, signatures, off-catalogue rationale, novelty, cost and non-fault mimics. Verify obtainability before calling new external data viable.
- Stop after 3 experiments or 2 hours. Do not spend a weekly slot. A separate selector may promote only after beating the comparable current holdout best and passing all gates.
- Numerical performance must be HOLDOUT-DTI with its provenance or ORGANIZER-CONFIRMED with a submission receipt. Never present a projection as a score. No fabricated leaderboard estimate.
- Validate saved TIFF bytes: finite within footprint, values [0,1], single band, exact CRS/shape/transform. The official page says outside-bounds data must be null/NaN; historical zero-outside and strict all-finite interpretations conflict, so report both diagnostics and resolve with the organizer before claiming acceptance. The earlier range-error cause is not established. Format validity is not scientific readiness or portal acceptance.
- Publish a clear executive summary, nine-site comparison, safe download status, unique name and note no longer than 140 characters. No manual scientific inspection required: missing evidence fails closed.
- End with a JSON run card: hypothesis, mechanism, non-fault mimic, holdout and CI, registry correlations/overlaps, raster SHA, validator, name/note, promote/negative verdict.
- Research free official sources and preserve provenance. Distinguish fault mapping from direct vent discovery. Never label an owner mirror organizer-authenticated solely because its hash matches.
- Three passes: implementation, adversarial review/fixes, original-requirements verification. Create PR and merge; report remaining work.

## Explicit irregularities in the request
Conflicting live leaderboard maxima; no official receipt attached; no lane paragraph; references to earlier scripts and a completed training pipeline that do not exist in this initial repository; no supplied cached stack. The goal of generating a TIFF does not override the explicit stop/uniqueness/holdout gates.

## Official starting points (links, not claims of retrieval)
- https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- https://github.com/drivendataorg/gems-prize-reference-solution
- https://docs.nlr.gov/docs/fy26osti/96647.pdf
- https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- https://gdr.openei.org/submissions/1391
- https://gbcge.org/current-projects/ingenious/
