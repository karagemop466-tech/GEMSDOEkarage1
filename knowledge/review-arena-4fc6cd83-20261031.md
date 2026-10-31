# Repository review — `arena/4fc6cd83-gemsdoekarage1` (2026-10-31)

## Executive decision

**NEGATIVE / DO NOT SUBMIT.** No candidate is cleared for upload and no weekly slot was selected or spent. The K-PROXY-DETECT GeoTIFF below is available only as a research/audit artifact. Its local format checks passed, but technical validation, a projected score, and comparisons against nine third-party mirrors are not an organizer decision or upload authorization.

## Scope and approach

Reviewed the working tree, the standing brief in `README.md`, current/previous run cards, release and writer receipts, KP1 site renderer, main site renderer, relevant tests, and the nine-site audit. The inherited checkout contained contradictory public status: the KP1 subsite and site-wide banner said “OK TO SUBMIT,” while the writer receipt said `approved_for_weekly_slot: false` and `promoted: false`; the separate selector step was absent. We treated the fail-closed protocol as controlling and corrected the publication path rather than treating the old green card as permission.

No new geological experiment was run. The predecessor KP1 record says it used its three-experiment budget. This review performs no new scoring, does not select a slot, and does not alter the candidate raster.

## Nine focus-site comparison

Values below are the scores reported in repository/user-provided records, **USER-REPORTED / UNVERIFIED**, not organizer-confirmed receipts. The local raster audit reports every one of these masks fails the specified 70% three-pixel overlap uniqueness test against at least one other named focus-site raster. There is no defensible calibrated leaderboard estimate for any site, so the table does not present a projection as an estimate.

| Site | Highest listed file (short name) | Reported score | Score class | Unique vs the other eight? | Score estimate | Download / submit |
|---|---|---:|---|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-…-nan` | 0.2477 | USER-REPORTED / UNVERIFIED | No | Not estimable | Study only; do not resubmit |
| GEMSDOE25 | `dotted-h19-5-d2-8-…-nan` | 0.2600 | USER-REPORTED / UNVERIFIED | No; identical mask to GEMSDOE30 | Not estimable | Study only; do not resubmit |
| GEMSDOE27 | `topo-gap-closure-t-v2-…-nan` | 0.2449 | USER-REPORTED / UNVERIFIED | No | Not estimable | Study only; do not resubmit |
| GEMSDOE28 | `h36-1-rung30-blind-r1-…-nan` | 0.2710 | USER-REPORTED / UNVERIFIED | No | Not estimable | Study only; do not resubmit |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-…` | 0.2600 | USER-REPORTED / UNVERIFIED | No; identical mask to GEMSDOE25 | Not estimable | Study only; do not resubmit |
| GEMSDOE31 | `h27-4-solo-d28-…-nan` | 0.2708 | USER-REPORTED / UNVERIFIED | No | Not estimable | Study only; do not resubmit |
| GEMSDOE32 | `h33-h33-2-b2-…-zeros` | **0.2778** | USER-REPORTED / UNVERIFIED | No; overlaps the 3-px rule with GEMSDOE24 | Not estimable | Study only; do not resubmit |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-…` | 0.2632 | USER-REPORTED / UNVERIFIED | No | Not estimable | Study only; do not resubmit |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-…-zeros` | 0.2750 | USER-REPORTED / UNVERIFIED | No | Not estimable | Study only; do not resubmit |

Source of the saved-byte comparisons and score labels: `evidence/nine_site_executive_20261031.json`, `evidence/nine_site_verification_20261031.json`, and `registry/user_reported_scores_20261029.json`. Mirror files are not organizer-authenticated copies. The exact GEMSDOE32 lineage and metric caveats are in [`why-gemsdoe32-b2-20261031.md`](why-gemsdoe32-b2-20261031.md).

### GEMSDOE32 and the 0.2778 result

The repository's measured explanation is that B2 is a strict subset of GEMSDOE25's 44,090-dot mask: it removes 6,436 dots and adds none. Across the nine files, much of the geometric support is shared; score covaries with dot count and proximity/clumping in the supplied score ledger. That is a plausible mechanism for why this variant's *reported* score is highest in this set: removing low-marginal-credit predictions can improve a precision-penalizing metric. It does **not** prove that dot deletion caused the organizer score, because the scores are unverified and the private truth is unavailable. The local catalogue hide-and-recover evaluator ranks the nine in the reverse order (Spearman −1 in the recorded KP1 audit), so it cannot validate that leaderboard explanation or select a winner.

The observed USER-REPORTED / UNVERIFIED 0.2778 is not an obtainable score guarantee. The KP1 score projection 0.2789 is a small-sample, geometry-only extrapolation from nine user-reported values, not a calibrated prediction. We cannot responsibly claim that this candidate beats 0.2778, much less the public board.

## Candidate that remains downloadable for research only

- File: [`docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif`](../docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif)
- SHA-256: `30a5fc28ff060ad38681d9b721024aea5aec3b070f407537dd28354efbe0ff0d`
- Unique **against the nine focus-site mirrors only**: max absolute rank correlation 0.007607; maximum forward 3-px dot overlap 0.265281 (26.5%). A complete authenticated registry comparison is not established.
- Local saved-byte format receipt: 15/15 checks, single-band float32, EPSG:32611, 3730 × 3292, values in [0,1], finite within the footprint, outside-footprint zeros, transform matches the locally mirrored sample. This is not organizer acceptance. The portal's original range-error report is addressed by explicit [0,1] checks, but no portal receipt verifies acceptance of this particular file.
- Projection: **PROJECTED, NOT A SCORE** 0.278920; no defensible calibrated leaderboard estimate.
- Candidate-specific off-catalogue analysis: 62,122 positive cells in a state-map proxy; candidate HOLDOUT-DTI 0.076408. The paired candidate-minus-matched-random bootstrap difference is +0.010909, with 95% interval [−0.003366, +0.026039] (evidence `evidence/kp1_run_card.json`). The interval includes zero. This is PROXY/HOLDOUT evidence, not an organizer score. Do not state that the candidate statistically beats random.
- Exact submission name and note, retained for audit if a future selector chooses this artifact: `karage1-kp1-ttca-springalter-far-conduit-32000-20261031`; “KP1 thermo-tectonic conduit alignment: multi-field edge+scarp+spring+Th/K consensus, >=2px off catalogue, 4px spacing, 32k dots” (127 characters). No selection is made here.

## Hypothesis and mimic

**Hypothesis (already tested in predecessor KP1 session; no new test here):** an unlisted permeable structure is more likely where independent magnetic/gravity/basement edge responses, young geomorphic scarps, spring/well proximity, and Th/K–U/K alteration jointly agree. A geometric-mean consensus and a sparse, separated emitter reduce single-layer false positives.

**Named non-fault mimics:** pluton/caldera margins, basin-margin contact springs, broad metamorphic fabric, landslide headwalls, and fluvial cut banks. These mechanisms can produce respectively geophysical edges, spring points, persistent lineaments, or scarps without a fault of interest.

The predecessor's `docs/kp1/research.html` lists five ranked ideas: (1) thermo-tectonic multi-field + LiDAR + fluid/alteration consensus (tested; the paired proxy contrast is inconclusive); (2) along-strike fault continuation using catalogue seeds, curvature/stepovers/slip-rate gradients, with independent drainage-offset confirmation (proposed); (3) multiscale magnetic/gravity upward-continuation persistence to estimate depth extent (proposed); (4) spring/well-to-lineament intersection census against the existing edge consensus (proposed); and (5) LiDAR scarp-height/degradation classes to distinguish fresh from degraded scarps (proposed). They are hypotheses, not results. No additional idea is run because the preceding KP1 session already recorded three experiments.

## Code changes made in this review

1. Added an explicit negative selector record, bound to the candidate hash: `evidence/kp1_slot_selector_20261031.json`.
2. Integrated the strict active authorization contract in `scripts/release_authorization.py` with `evidence/active_submission_status.json`, then made the KP1 subsite and site-wide banner additionally require a positive technical gate, positive pre-registered holdout validation, matching writer receipt, and separate positive selector record bound to the same hash/name. Missing, stale, or negative authorization renders **DO NOT SUBMIT / research only**.
3. Corrected the KP1 decision and run-card records to distinguish technical preflight from model validation and upload authorization. The candidate is locally format-valid, but its candidate-minus-random proxy 95% interval includes zero; `candidate_validation_passed=false`, `ok_to_submit=false`, `selector_approved=false`, `verdict=negative`, and no slot is spent.
4. Updated regressions to forbid treating a technical pass as upload approval, and amended README's first section so it does not repeat the old contradictory green status.
5. Rebuilt the public pages. The actual download remains available with a research-only label; it is not removed or renamed.

## Three-pass review and verification

- **Pass 1 — inspect and correct:** reviewed README/standing prompt, receipt and run-card semantics, nine-site table, publisher, and tests. Found that `decision.ok_to_submit=true` was displayed as approval while the writer receipt explicitly denied weekly-slot approval. Added a fail-closed selector requirement and explicit negative selector record.
- **Pass 2 — check edge cases:** checked missing selector, mismatched raster hash/name, false technical gate, false writer approval, and absence of an organizer receipt. All missing/stale states remain red. Reviewed direct download links: they remain research artifacts, not a green CTA.
- **Pass 3 — end-to-end:** regenerated the KP1 subsite and main site. Confirmed the top-level banner says no file is authorized; the KP1 page shows “DO NOT SUBMIT · RESEARCH ONLY”; the executive summary states no file is cleared; and no positive selector record exists. Final integrated software suite after merging current `main`: **522 passed, 4 skipped, 0 failed** (`.venv/bin/python -m pytest -q -p no:cacheprovider`). `git diff --check` passed. The skips are data-dependent; these tests do not validate a leaderboard result.

## Limitations and next steps

- No DrivenData login in this environment: no authenticated data retrieval, official sample-file verification, or submission receipt.
- No organizer score for the candidate and no defensible leaderboard estimator. Do not turn the projection into a claimed score.
- Candidate proxy comparison is inconclusive (paired-difference CI includes zero) and the ordinary hide-and-recover evaluator does not represent off-catalogue private truth.
- Uniqueness is tested against the nine named mirror files, not a complete, authenticated registry of all competing submissions.
- The shared `vendor/gems57` writer/validator provenance and the competition mirrored data authenticity have previously been flagged as unresolved; this review does not claim to fix them.
- Weekly slot selection remains separate by design. No selection or upload is authorized. Next useful work is to reconcile the authoritative template/input provenance and construct a leakage-tested, spatially blocked evaluation on independent official fault truth before considering another candidate. Do not spend a slot until an eligible candidate beats a frozen, relevant comparator under a preregistered protocol.

## Official links supplied for manual review

- Competition: https://www.drivendata.org/competitions/306/competition-doe-gems/
- Problem statement/format and metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Organizer reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- NLR competition report/rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS: https://gbcge.org/current-projects/ingenious/
- EPSG:32611: https://epsg.io/32611

Links are provided as source leads; the sandbox did not authenticate the competition account or independently verify current page contents during this repository review.
