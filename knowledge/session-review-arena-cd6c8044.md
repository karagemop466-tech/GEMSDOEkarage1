# Three-pass repository review — `arena/cd6c8044-gemsdoekarage1` — 31 October 2026

## Decision

**NEGATIVE / DO NOT SUBMIT.** No new GeoTIFF was generated, no candidate passed validation, no weekly slot was selected or spent, and no leaderboard score estimate is supportable from this checkout. This is deliberate: the method lane and canonical shared template are unassigned, required competition rasters/cache are absent, and prior integrity preflight reports writer/uniqueness hash mismatches. The active user request also requires the assigned-lane and shared-tool protocol. Producing a TIF without these prerequisites would be an unvalidated artifact, not an end-to-end competition submission.

- Current run card: [`evidence/session_cd6c8044_run_card.json`](../evidence/session_cd6c8044_run_card.json).
- Hypothesis slate and conditional preregistration: [`knowledge/hypotheses-20261031.md`](hypotheses-20261031.md).
- Live leaderboard snapshot, observed 31 Oct 2026: [`evidence/leaderboard_snapshot_20261031.json`](../evidence/leaderboard_snapshot_20261031.json).
- Nine-site focus table and per-site pages: [executive summary](../docs/executive-summary.html), [focus-site audit](../docs/focus-sites.html), and [individual site summaries](../docs/GEMSDOE24.html), [25](../docs/GEMSDOE25.html), [27](../docs/GEMSDOE27.html), [28](../docs/GEMSDOE28.html), [30](../docs/GEMSDOE30.html), [31](../docs/GEMSDOE31.html), [32](../docs/GEMSDOE32.html), [33](../docs/GEMSDOE33.html), [36](../docs/GEMSDOE36.html).

## Pass 1 — reconcile the request with repository evidence

1. Read the full request, `AGENTS.md`, the README standing prompt, current branch and clean working tree, latest review/card on the base branch, registry template declaration, site renderer, writer/validator, nine-site tables, experiment records, and tests.
2. Confirmed `registry/template.json` has `method_lane: null` and `canonical_template_assignment: null`. The active prompt's method paragraph is not assignable from repository evidence; no lane was inferred.
3. Confirmed no `data/` or `.cache/gems_data/` input directory exists in this checkout. The recorded shared preflight reports missing `feature_stack.npy`, `existing_faults.tif`, `training_features.tif`, `sample_submission.tif`, and `labels.tif`. The competition data tab is behind organizer login; no authenticated data were downloaded in this session.
4. Prior review recorded vendored writer and uniqueness SHA-256 mismatches. This session did not edit or privately replace those shared tools.
5. The nine-site score history is not organizer-receipt evidence. Score values in the focus-site ledger remain **USER-REPORTED / UNVERIFIED**; no predictor trained on this target is calibrated to private new-fault labels. Per-site leaderboard estimates are therefore **UNAVAILABLE**, not guessed.
6. The official leaderboard was freshly read on 31 Oct 2026: public rank #1 score 0.4544; rank #50 score 0.3195. Therefore the user's 0.3195 reference is not the current top score in this read, and 0.4413 was not present in the top 50. These values are **ORGANIZER-PUBLIC**, not receipts for the nine focus artifacts. Exact observations are saved in the snapshot card.
7. No experimental holdout or canary was run because the shared evaluator/cache/input preconditions and assigned lane are missing. No candidate TIF was written. No score number is labeled as a holdout result in this session.

## Executive summary — one row per focus site

The following table consolidates the top *listed* file per focus site based on the user's supplied history/local pinned mirror table. The score label applies to each value. “Estimated organizer score” is unavailable for every row; a catalogue holdout is not a calibrated forecast of the private expert-labeled targets. All historical files are for forensic learning only, not download-and-submit recommendations. Local uniqueness means the stored audit finds a conflict with at least one focus-site raster and/or the registered lattice under the project's internal rule; the registry is incomplete, so it is not a fleet-wide uniqueness certificate.

| Site | Highest listed reference file | Listed score | Organizer-score estimate | Unique vs other audited GEMSDOE rasters? | Download/submit decision |
|---|---|---:|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 USER-REPORTED / UNVERIFIED | Unavailable | **No** — conflicts with local lattice/focus audit | Historical learning reference only; DO NOT RESUBMIT |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | **No** — same positive mask recorded for GEMSDOE30; lattice overlap also trips internal gate | Historical learning reference only; DO NOT RESUBMIT |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 USER-REPORTED / UNVERIFIED | Unavailable | **No** — conflicts with local lattice/focus audit | Historical learning reference only; DO NOT RESUBMIT |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 USER-REPORTED / UNVERIFIED | Unavailable | **No** — conflicts with local lattice/focus audit | Historical learning reference only; DO NOT RESUBMIT |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | **No** — same positive mask recorded for GEMSDOE25; lattice overlap also trips internal gate | Historical learning reference only; DO NOT RESUBMIT |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 USER-REPORTED / UNVERIFIED | Unavailable | **No** — same mask family as GEMSDOE28 `h27-4-r1`; lattice overlap also trips internal gate | Historical learning reference only; DO NOT RESUBMIT |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.2778 USER-REPORTED / UNVERIFIED | Unavailable | **No** — conflicts with local lattice/focus audit | Historical learning reference only; DO NOT RESUBMIT |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 USER-REPORTED / UNVERIFIED | Unavailable | **No** — conflicts with local lattice/focus audit | Historical learning reference only; DO NOT RESUBMIT |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 USER-REPORTED / UNVERIFIED | Unavailable | **No** — conflicts with local lattice/focus audit | Historical learning reference only; DO NOT RESUBMIT |

Original site source pages are available in the links above; local byte-level/pairwise evidence is in `docs/data/focus_site_table_20261029.json`, `evidence/focus_sites_audit_20261029.json`, and `registry/reference_assets.json`. Exact download URLs in each HTML page link to pinned public learning artifacts; they are **not** approved submission downloads. The table's unique verdict is scoped to locally audited artifacts; the full cross-project registry has not been authenticated or exhaustively scanned.

## GEMSDOE32 B2 (`h33-h33-2-b2`) — forensic interpretation

The most defensible answer to “why was this the highest supplied focus-site score?” is a measured **mask relationship**, not a proven geological explanation. Existing local mask algebra records the B2 support as the GEMSDOE25/GEMSDOE30 `d2.8` parent support after removing the 6,436 pixels within the mirrored known-fault collar of two pixels; B2 adds no pixels in that comparison. The user-reported score sequence rises from 0.2600 to 0.2778, but these values are not tied to organizer receipts in this checkout and are not a controlled, independently verified ablation.

A plausible metric-based explanation is that removing predictions adjacent to known catalogue traces could reduce redundant false-positive mass while preserving some distance-weighted coverage within the 300 m kernel. The official metric gives β=0.8 to false negatives and α=0.2 to false positives, so both missed fault coverage and excess prediction mass matter. That story is **consistent with** the mask change; it is not proven by it. B2 did not add a better geological signal in the audited comparison, and the private expert-labeled test set is not available locally. It is consequently impossible to attribute the reported 0.2778 to the collar operation, infer that the same operation will improve future submissions, or claim that this repository has beaten it.

Could a distinct method score higher? In principle the competition's public leaderboard shows higher organizer-public scores than 0.2778; that is not evidence a new candidate here will do so. The 31 Oct live snapshot has #1 0.4544 and #50 0.3195. No score estimate for a future candidate is defensible without an externally calibrated validation design or an organizer receipt. A new file must first beat a valid holdout best, clear uniqueness and format checks, and pass a separate selector.

## Ranked research slate

Five hypotheses, layer signatures, expected qualitative opportunity/cost, confounders, and the first conditional validation plan are in [`knowledge/hypotheses-20261031.md`](hypotheses-20261031.md). H-EULER (depth-coherent Euler deconvolution on official magnetics) is the first conditional validation candidate because it is not implemented in active source and uses no new external data. It was proposed in a 30 Oct slate, so it is **carried forward, not claimed as newly invented**. The other ideas are review-stage proposals and are not asserted as globally novel.

**No candidate was validated in this session.** The top candidate cannot be tested line-by-line against the user-mandated shared holdout until the shared template, cache, organizer inputs, and lane assignment are restored. No external dataset is required for the top candidate; official competition `training_features.tif` is the required input and the official data tab requires login. No TIF was generated because an unvalidated file would breach the user's own promotion gate.

## Three passes

### Pass 1 — implement and verify

- Added this current-session review, a machine-readable negative run card, an official-public leaderboard snapshot, and a preregistered five-hypothesis slate.
- Corrected the stale interpretation of 0.3195: the live page read 31 Oct showed it at rank #50, not as the competition leader. Public #1 was 0.4544.
- Preserved prior per-site result values and labeled them user-reported; did not relabel them as estimates.
- No raster-generation code was added, no TIF or score estimate was fabricated, and no submission slot was used.
- Full software suite: **451 passed, 0 failed, 2 skipped, 126 warnings** (`.venv/bin/python -m pytest -q -rs`). The two skips require absent ignored bridge inputs or the competition sample grid; software tests are not geological validation.

### Pass 2 — review for gaps and assumptions

- Re-checked the nine focus-site values against the existing pinned user-reported table and individual page links. Scores remain historical user reports; exact artifact-to-receipt links are absent.
- Re-checked repository template declaration, preflight notes, historical holdout limitations, and current hypothesis/code overlap. The Euler item is explicitly labeled previously proposed but not implemented/tested; other new-use distinctions are qualified as hypotheses rather than global novelty claims.
- Confirmed current lane remains `null`. An evaluation run under a private or mismatched writer would falsely claim conformance; therefore no such run occurred.
- Flagged that the local overlap gate may be saturated by the lattice and is an internal protocol, not an organizer rule. A complete and authenticated registry plus owner interpretation is still needed.

### Pass 3 — re-check against the request

- Every requested focus site appears in the table and has a per-site executive page.
- Each table row explicitly states file, reported score, unavailable estimate, uniqueness status, and no-resubmit decision.
- GEMSDOE32 B2 analysis separates exact audited geometry from conjecture and explains why no higher score is claimed.
- Five hypotheses identify layers, signature, off-catalogue rationale, implementation difference, mimic, and qualitative cost/opportunity. Candidate one is preregistered but not experimentally validated due explicit blockers.
- No new TIF was created. Consequently there is no new submission download and **nothing is OK to submit**.
- Run card contains null measurement fields, explicit negative verdict, and the required validator / correlation statuses.

## Irregularities flagged for review

1. **Submission data access:** DrivenData data tab requires competition login in prior records; core organizer files are absent locally.
2. **Shared-tool integrity:** prior preflight recorded SHA mismatches in vendored writer/uniqueness modules. Resolve upstream with canonical owner, not by private fork.
3. **No lane assignment:** template registry fields remain null; user protocol says only one assigned lane may be run.
4. **Duplicate-gate saturation:** project tests have found the 70%/3-pixel lattice gate can fail even random placements; this is internal, not official. Do not evade it. Owner must determine application or revise protocol before promotion.
5. **Holdout target mismatch:** catalogue-based holdout withholds known catalogue segments, while competition public page describes expert-labeled faults not in the existing USGS database. Holdout DTI cannot be labeled a leaderboard estimate.
6. **Site scores:** the 0.2778 and other focus-site numbers have no artifact-linked organizer receipt in this checkout; remain `USER-REPORTED / UNVERIFIED`.
7. **Leaderboard freshness:** live public page can change. Snapshot is dated 31 Oct and must not be presented as a future live feed.
8. **Submission format outside-footprint:** official text permits null/NaN outside the target bounds; prior shared writer policy has conflicting zeros behavior. Must be resolved against canonical organizer/template validation before any final TIFF.

## Official sources reviewed

- [DrivenData problem description, metric, official data layers, and GeoTIFF format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
- [DrivenData public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) (live read 31 Oct 2026; public snapshot only).
- [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (login requirement recorded in prior repository review; no authorized data restore in this session).
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution).
- [USGS GeoDAWN data-release record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) (context for official geophysical data, not used as an unauthenticated substitute for the competition raster).
- [DOE/NLR official challenge rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf).

## Remaining work — next session priority

1. Assign and record the exact method paragraph/lane and canonical upstream shared-template repository+commit. Resolve writer/uniqueness SHA mismatches upstream.
2. Obtain authenticated DrivenData data and matching shared feature cache; record source, version, CRS/shape/transform, and hashes. No mirror may be represented as organizer-authenticated.
3. Ask protocol owner to clarify the saturated lattice test and provide a complete immutable registry snapshot; preserve the stated 0.90/70% rule unless explicitly revised.
4. Freeze an off-catalogue validation design or acknowledge the catalogue holdout cannot select for the target. Then run H-EULER canaries and blocked hide/recover using assigned `evaluate_holdout.py`; do not exceed 3 experiments or 2 hours.
5. Only if a candidate beats the comparable holdout baseline and passes all gates should it be written with the canonical writer, reopened and validated, and submitted to a separate selector. Check weekly cap on the live portal; preserve organizer receipt.
6. Add an automated current-source refresh/feed with timestamps and provenance after the source refresh workflow's reliability and auth boundaries are tested.

**Final run-card verdict: negative.** Negative results and blockers are the deliverable; no new TIF is cleared for download or submission.
