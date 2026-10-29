# Session review — `arena/f43e6441-gemsdoekarage1` (29 October 2026)

## Decision: NEGATIVE — DO NOT SUBMIT

No new GeoTIFF was generated. No existing TIFF is cleared by this review. No weekly submission slot was selected or used. No candidate **HOLDOUT-DTI** was measured, and no candidate score or leaderboard projection is offered. This is deliberate: the required lane is absent, the execution preflight fails closed, the approved feature cache and competition inputs are absent, and the local run card says the literal lattice witness blocks the historical 37,654-dot budget.

- Current session card: [`evidence/session_f43e6441_run_card.json`](../evidence/session_f43e6441_run_card.json)
- Current preregistered research slate: [`knowledge/hypotheses-20261029.md`](hypotheses-20261029.md)
- Latest preflight output: [`evidence/preflight_f43e6441.json`](../evidence/preflight_f43e6441.json)
- Landing page: [`docs/index.html`](../docs/index.html)

## Verified repository and execution state

This checkout is on `arena/f43e6441-gemsdoekarage1`, at the commit from which this branch was created. No restored competition data or `.cache/gems_work/feature_stack.npy` exists in the checkout. `registry/template.json` has `method_lane: null` and `canonical_template_assignment: null`. `scripts/shared_tools.py preflight` exits nonzero; `scripts/audit_template_integrity.py` reports `execution_authorized: false`, including recorded SHA drift in the vendored writer and uniqueness modules. These are local, reproducible findings, not organizer authentication.

The user's protocol says to follow one assigned method paragraph, but this prompt does not identify one; the repository's assignment is also null. Selecting a lane from an old experiment would invent an assignment. I therefore did not run feature canaries or a geological holdout, use the local/private evaluator to manufacture a candidate result, create a TIFF, or select a slot. The preflight card records no candidate, no raster hash, no validator pass, `ok_to_submit: false`, and a negative verdict.

The pinned local audit reports that the calibration-lattice witness covers 99.8713% of the mirrored footprint within the three-pixel disk. Its historical-budget geometric bound says at least 82.3418% of any 37,654 distinct in-footprint dots must be within that disk. Those are **audit geometry fractions, not scores**. This is a literal stop under the supplied protocol, until its owner resolves whether the lattice is a registry entry or an explicitly authorized calibration exception. Do not evade it by jittering, hole-filling, changing the budget silently, or comparing only to selected site masks.

A new read-only saved-byte audit was run in this session after noticing that the 2028-era inventory was labeled as nine local downloads while the checkout contains additional TIFs. [`evidence/local_and_peer_audit_f43e6441.json`](../evidence/local_and_peer_audit_f43e6441.json) checked 11 local downloads plus 9 SHA-pinned peer rasters against the pinned mirror template, lattice, labels, and focus-site masks. It found the old `unique-hyp-kth-therm-mask-20261028-zeros.tif` (`a18e8fea…`) has 37,617 of 37,654 positives (99.9017%) within 3 px of the lattice. Its zeros-outside bytes fail the official null/NaN-outside format variant. It is therefore a literal duplicate and is not submission-ready, despite the old sidecar's positive local-format wording. The current audit sets `ok_to_submit: false` for every local artifact. These mirror comparisons are not a complete organizer registry or organizer authentication.

## Nine-site executive summary

All scores below are **USER-REPORTED / UNVERIFIED**, not `HOLDOUT-DTI` and not `ORGANIZER-CONFIRMED` (no submission-page receipt tied to a file SHA-256 is available). “Estimated score” is **Unavailable** for every file: no valid, comparable holdout run was performed in this session. The comparison is based on the repository's SHA-pinned third-party mirrors and the literal lattice witness; the complete organizer registry is not available. The listed files are learning/audit references, **not download-and-submit recommendations**.

| Site | Highest reported file (reference only) | Reported score | Estimated score | Novelty / action |
|---|---|---:|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 USER-REPORTED / UNVERIFIED | Unavailable | Fails literal lattice overlap gate; DO NOT SUBMIT |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | Same binary support as GEMSDOE30; fails lattice gate; DO NOT SUBMIT |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 USER-REPORTED / UNVERIFIED | Unavailable | Fails literal lattice overlap gate; DO NOT SUBMIT |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 USER-REPORTED / UNVERIFIED | Unavailable | Related focus-site masks audited; fails lattice gate; DO NOT SUBMIT |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | Same binary support as GEMSDOE25; fails lattice gate; DO NOT SUBMIT |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 USER-REPORTED / UNVERIFIED | Unavailable | Same binary support as GEMSDOE28 `h27-4-r1`; fails lattice gate; DO NOT SUBMIT |
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.2778 USER-REPORTED / UNVERIFIED | Unavailable | Highest reported number in the supplied nine-site list; not cleared; DO NOT SUBMIT |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 USER-REPORTED / UNVERIFIED | Unavailable | Fails literal lattice overlap gate; DO NOT SUBMIT |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 USER-REPORTED / UNVERIFIED | Unavailable | Strict superset of GEMSDOE32 B2 in the audited mirror; fails lattice gate; DO NOT SUBMIT |

The exact owner-mirror paths, pinned revisions, file hashes, binary-mask relationships and nine-site audit are linked in [`evidence/nine_sites_secondary_audit_20261028.json`](../evidence/nine_sites_secondary_audit_20261028.json), [`evidence/local_downloads_and_peer_audit_20261028.json`](../evidence/local_downloads_and_peer_audit_20261028.json), and the nine individual site pages under [`docs/`](../docs/). Passing a local comparison against nine sites would not certify uniqueness against every prior or current competition raster.

## GEMSDOE32 B2: what the evidence does and does not support

The reported `0.2778` remains **USER-REPORTED / UNVERIFIED**. The site page and the pinned owner mirror are not a submission-page receipt; no actual organizer receipt bound to the raster's SHA-256 was recovered here. The audited mirror supports a specific geometric observation: B2 is the GEMSDOE25 parent mask after deleting all positive pixels within the closed two-pixel disk of the mirrored known-fault labels—6,436 deletions, no additions. GEMSDOE25 and GEMSDOE30 have identical positive-pixel support; GEMSDOE36 contains B2 plus 1,200 additional pixels. These are mask comparisons, not causal evidence.

A plausible explanation is that thinning removes redundant or low-yield prediction mass while preserving some distance-weighted coverage. Let `T` be weighted true-positive credit, `F` weighted false-positive mass, `G` withheld positives, and `ε` the evaluator stabilizer. The documented metric is `DTI = T / (T + αF + β(G − T) + ε)`, with α=.2, β=.8 and the 300 m triangular distance kernel. If an ablation loses `L` units of true-positive coverage but removes `c` units of false-positive mass, it improves the ratio only if `α T c > L(αF + βG + ε)`. Thus a collar can help when it removes enough low-yield mass relative to the true coverage it deletes; it is not automatically beneficial. This mechanism is plausible, not proved: the hidden labels are unavailable, and the reported values are not receipt-verified. A catalogue buffer is not an automatically free scoring region. No defensible calculation shows that a new candidate will exceed B2 or the current public leaderboard.

## Current public leaderboard context — separate from candidate evidence

The official public leaderboard page was fetched on 29 October 2026 UTC. Its visible top entry displayed `0.4544` (public leaderboard display, **not** an artifact-linked submission-page receipt in this repository); the visible second entry displayed `0.3916`. This is a dated public-page snapshot, not a private/final score or a score estimate for any local file. It supersedes the prompt's `0.3195` as the visible public leaderboard context at fetch time, but it does not change the negative local decision. Source: [DrivenData public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).

## Official source checks and irregularities

1. **Problem specification:** fetched [DrivenData's official problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/). It states the objective is fault mapping, the provided layers include geophysical, strain, earthquake and topographic inputs, and the submission must be one float32 GeoTIFF in EPSG:32611 on the same 100 m grid/bounds, with values in [0,1] and null/NaN outside the bounds. The page describes the distance-weighted Tversky metric with alpha .2, beta .8, and a 300 m linear triangular kernel. This is source verification, not local byte verification or portal acceptance.
2. **Official data access:** fetched the [DrivenData data-tab URL](https://www.drivendata.org/competitions/306/competition-doe-gems/data/); the unauthenticated response redirected to the DrivenData login page. No organizer inputs were downloaded. This matches the repository's missing-data preflight.
3. **USGS GeoDAWN:** fetched the [official USGS release page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and). The page identifies the 2024 release and DOI `10.5066/P93LGLVQ`, describes magnetic and radiometric products including GeoTIFF grids, and states CC0 1.0 rights. The release page is obtainable, but its payload bytes were not downloaded or authenticated in this session.
4. **USGS 3DEP:** fetched the [USGS 3DEP program page](https://www.usgs.gov/3d-elevation-program), which links to elevation data access and says 3DEP products are free of charge without use restrictions. This is not verification of specific lidar tile coverage over each study pixel. No hypothesis below depends on a new 3DEP download.
5. **Score provenance irregularity:** the public GEMSDOE site values and the user-supplied historical values do not include local organizer receipts. Treat them as user/owner reports, never as verified organizer scores.
6. **A false green executive-summary page was present in the checkout:** `docs/executive-summary.html` claimed “CLEARED FOR SUBMISSION,” offered `unique-hyp-kth-therm-mask-20261028-zeros.tif`, reported an unverified holdout and said uniqueness had passed. The fresh audit shows the TIFF is a literal lattice duplicate (99.9017% 3-px overlap) and its zero-outside values do not meet the official null/NaN-outside format. I replaced the page with the fail-closed renderer output, corrected the generator to show the active session/audit, and added regression coverage for this false-green failure mode. The file itself and its former sidecar are retained as historical audit material, not authorization.
7. **Metric/validation distinction:** the public page specifies `null or nan` outside bounds. Prior local reports tested several outside-footprint encodings, but the original rejected submission file is not retained. Its `[0,1]` error's cause remains unknown. A local format validator cannot establish DrivenData portal acceptance.
8. **Run-context drift:** README, static pages and inherited run cards contain material from several parallel sessions with different branch IDs and dates. The current branch has no `.cache` inputs; old session evidence is not a fresh experiment. The current-session card is the authoritative status for this branch.

## Top-candidate validation result

**Not run — blocked, not passed.** There is no assigned lane, the canonical shared-template assignment is null, the cache and official inputs are absent, and template-integrity checks fail closed. The candidate slate is preregistration-only. Accordingly there are no canary AUCs, no pre-placement Spearman tests, no placed dots, no final overlap measurement for a new candidate, no `HOLDOUT-DTI`, and no raster hash. The repository's protocol calls for at most three experiments or two hours; none was started and no slot was used.

## Three-pass review

### Pass 1 — Inventory, source verification, and requested hypotheses
- Read the README, standing brief, AGENTS instructions, current run card, nine-site audit, B2 analysis, source register and shared-tool wrappers.
- Replayed `scripts/preflight.py`, `scripts/shared_tools.py preflight`, and `scripts/audit_template_integrity.py`; all return the intended fail-closed negative status.
- Fetched and inspected official DrivenData problem/data/leaderboard pages and USGS GeoDAWN/3DEP source pages.
- Drafted the ranked candidate slate in `knowledge/hypotheses-20261029.md`; no model implementation or slot selection followed because gates are closed.
- Re-fetched the SHA-pinned mirror template, labels, lattice and focus-site references, then audited every local saved TIFF and peer witness. This is a read-only saved-byte audit; it does not restore official training inputs or execute a geological experiment.

### Pass 2 — Adversarial review
- Checked that no provided score was silently labelled a holdout result, no leaderboard projection was made, no old TIFF was copied, and no local validator result was represented as portal acceptance.
- Audited all 11 local TIFs and 9 pinned peer rasters from saved bytes. The result caught the uncovered K/Th + thermal TIFF with 99.9017% lattice overlap and a zero-outside encoding that fails the official null/NaN-outside requirement; it is now explicitly negative.
- Found and removed the executive summary's stale false-green submission claim. The deterministic site renderer and regression checks now show the current negative session and link to its evidence.
- Confirmed that the candidate feature list is conditional on authenticated layer metadata, that exact input bytes and shared-template identity are missing, and that registry completeness is not claimed.
- Confirmed run-card fields are explicit null/blocked values for measurements not performed and `verdict: negative`.

### Pass 3 — Requirements and software verification
- Added a current branch-scoped review and machine-readable card; linked the documents from the README, start-of-session instructions, and rendered site.
- Installed declared project dependencies into ignored `.venv`. The initial full test run exposed eight failures: a false-green handmade page bypassed renderer expectations, that page failed to preserve site-audit/download links, a legacy runner had an `IndentationError` instead of its intended quarantine, and one newer TIFF was missing from the prior saved-byte inventory. I fixed the renderer inputs and current executive page, corrected the runner to raise its explicit `BLOCKED` error, generated the expanded audit, and updated regression coverage.
- Final full suite: **358 passed, 119 pending Rasterio/Affine deprecation warnings, 0 failed**. This is a software test result, not a geological experiment or score.
- Re-ran the deterministic renderer and verified it still presents no approved download. Did not generate/download a candidate TIFF: doing so would contradict the protocol and evidence gates.

## Limitations and next work, in order

1. Obtain a written method-paragraph/lane assignment and canonical shared-template/cache identity. Resolve the recorded vendored writer/uniqueness checksum drift with the template owner; do not repin locally.
2. Obtain authenticated competition inputs via the user/team's normal DrivenData access on an authorized machine, or an explicitly approved official source. Verify SHA-256, metadata, footprint, masks and feature names; the data tab is login-walled here.
3. Obtain the protocol owner's decision on the calibration-lattice witness and literal 70% stop. Do not exempt or alter it without explicit authorization.
4. Freeze a complete registry and comparable authorized baseline. Re-run the repository audit after reconciliation, not against an assumed complete mirror set.
5. Only then preregister the assigned lane's best new hypothesis, run per-feature leakage canaries and whole-segment buffered hide-and-recover using the agreed shared evaluator/writer, exact visible-fault masking, paired confidence intervals and identical controls.
6. Pass pre-placement surface and final-dot duplicate tests, saved-byte writer validation, and an independent release gate. The validator must check [0,1] in-footprint values and null/NaN outside, plus exact CRS/shape/transform; organizer upload validation remains an additional step.
7. Promotion remains separate: do not use a weekly slot until the holdout beats the frozen best under the preregistered rule and a separate selector confirms the current allowance. Retain the file-linked organizer receipt.

## Required JSON run card

See [`evidence/session_f43e6441_run_card.json`](../evidence/session_f43e6441_run_card.json). Its verdict is negative. No score estimate or submission file is authorized.
