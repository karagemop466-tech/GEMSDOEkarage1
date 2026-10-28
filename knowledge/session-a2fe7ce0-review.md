# Three-pass session review — 28 October 2026

## Decision

**DO NOT SUBMIT. No unique competition TIFF was generated, and no weekly slot was selected or spent.** The current request again says the lane is “the single method paragraph below,” but supplies no such paragraph. Inventing a lane would violate the parallel-run protocol. More importantly, an exact replay found that the pinned candidate shared template does not implement the requested buffered whole-segment holdout. A valid high-score estimate is therefore unavailable.

This is a negative deliverable, not a claim that the requested submission exists. The historical research TIFFs remain clearly labeled **DO NOT SUBMIT**.

## Pass 1 — implement the next prerequisites

1. Restored 16 core/external inputs from immutable, SHA-256-pinned GitHub mirrors: four core rasters and twelve external files. These are third-party mirrors; matching their manifest does **not** authenticate organizer origin.
2. Bootstrapped the unmodified `buffedlizard55-lab/GEMSDOE32` candidate template at reviewed commit [`e56a10a`](https://github.com/buffedlizard55-lab/GEMSDOE32/tree/e56a10a9d2f218c05ea66c5a5b7228bb780bb5a7). The local checkout stayed clean.
3. Used its unchanged feature builder to create the 35-channel float32 cache. The local ignored NPY is 1,719,082,528 bytes, shape `3730 × 3292 × 35`, SHA-256 `f95486ffa937e0237c53c5e7f59e49cc142825ae5ea56b166d64dcbfeef5bdc0`. This resolves local placement for the current runtime only; it does not resolve upstream cache provenance, the open ridge-filter defect, data authenticity, or lane assignment.
4. Added a reproducible [shared-template audit](../evidence/shared_template_audit_20261028.json), a content-bound [contract](../registry/template_contract.json), and fail-closed preflight enforcement. Tool execution now requires a non-empty lane, all required inputs, an immutable byte-matched shared checkout, and a passing contract. A report write cannot be confused with experiment or submission readiness.
5. Updated the template pin from the stale 27 October commit to the reviewed 28 October main head, which includes upstream binary-input and final-note-length protections. No shared source was copied or patched locally.

## Pass 2 — adversarial review and upstream reporting

### Buffered split does not match its claim

The unchanged shared `load_holdout_context` describes a 15-pixel (1.5 km) collar, but that dilation is around the quadrant and is used to select training components. It is not a measured buffer between withheld truth and visible catalogue context.

On the hash-pinned mirrored inputs:

- all eight cells have a minimum withheld-truth-to-visible distance of **2 pixels**, not greater than 15;
- **15,705 / 22,232** withheld-positive pixel instances lie within the claimed 15-pixel collar;
- `scipy.ndimage.label` creates 8-connected components rather than branches between intersections;
- **76** selected component instances are only partly scored because truth is clipped to an eroded quadrant domain.

These are split-geometry counts, not a performance score. The defect was reported once in the shared upstream template as [GEMSDOE32 issue 60](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/60). No private evaluator fork was made.

### Static leakage canary is mislabeled

Passing the complete mirrored `labels.tif` catalogue to the unchanged static evaluator produces a nested result labeled `HOLDOUT-DTI`, evaluator `GEMSDOE32-HIDE-RECOVER-v3.0`, 22,232 withheld-positive pixel instances, numeric output `1.0 [1.0, 1.0]`. That number is **INVALID-HOLDOUT / LEAKAGE-CANARY**, not a score: the input already contains every supposedly hidden label and has no fold-local provenance. The outer wrapper says static inputs are not promotion-eligible, but consumers can still extract the nested mislabeled result.

The classification defect was reported once upstream as [GEMSDOE32 issue 61](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/61). The audit stores the number only under `tool_numeric_output_not_a_score`; it is not used as a baseline, estimate, or promotion signal.

### Existing upstream blockers remain open

- [Issue 49](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/49): the shared Hessian ridge implementation selects the smaller eigenvalue in the known expression; affected cache channels require central correction and invalidation.
- [Issue 53](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/53): the template's canonical feature receipt does not publish obtainable bytes or a digest tied to builder and input hashes.
- [Issues 60](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/60) and [61](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/61): new split and evidence-class findings above.

The current upstream writer now rejects implicit probabilities and checks the rendered 140-character note, improvements absent from the stale prior pin. That format progress does not cure the holdout or cache defects.

## Pass 3 — original-request recheck

- The nine requested sites remain covered in the executive table and individual pages. Their historical numbers are **USER-REPORTED / UNVERIFIED**, not organizer-confirmed receipts. Every audited reference fails the literal lattice rule, so each action remains **DO NOT RESUBMIT**.
- The B2 byte relationship remains measurable: the mirrored GEMSDOE32 B2 support is the GEMSDOE25 d2.8 support minus 6,436 near-catalogue dots, with none added. This makes false-positive-mass reduction a plausible explanation for its reported advantage under distance-weighted Tversky, but does not establish causality or predict a new score.
- Four ranked hypotheses remain documented before implementation: signed magnetic/gravity offsets, local K/eTh alteration-boundary residuals, drainage asymmetry, and sampling-aware thermal residuals. No hypothesis became an assigned lane and no geological experiment was run.
- No candidate surface existed, so neither pre-placement correlation nor final-dot registry overlap was run for a new file. No candidate bytes existed, so GeoTIFF validation fields and SHA-256 are null. This is the only honest result under the stop rules.
- The static site continues to put **DO NOT SUBMIT** first, disables the submission download, shows “estimate unavailable,” and links the latest machine-readable session card and template audit.
- The exact rejected portal file and an organizer response are still unavailable. A locally finite `[0,1]` raster cannot diagnose the earlier range error or guarantee portal acceptance. The official problem description's null/NaN-outside wording and historical zero-outside practice remain separate diagnostics.

## Verification closeout

- Root suite: **248 passed**. Reviewed upstream pin: **259 passed, 10 skipped, 3 subtests passed**. Skips are the upstream suite's own optional/data-dependent skips, not suppressed failures.
- The strict shared audit intentionally exits 1 because the contract is incompatible; `--report-only` writes the negative evidence and exits 0. Two full replays of the final six-asset contract produced byte-identical audit and contract JSON.
- Final machine artifacts are strict JSON. The public evidence copies are byte-identical to their canonical files. The single site renderer rebuilt 32 decision pages and concurrent/deterministic renderer tests passed.
- Current audit SHA-256: `763d0e0c41a93924e6671331559aa3beccfa20985f734b74d4332f50f38d9208`. Current contract SHA-256: `8c2f480e420d8bab36b1ca7cdd45159302a55564f6ad62a26450c00a6d35639b`.
- Preflight rechecks exact GitHub origin, immutable commit, clean checkout, the complete audited tool set, and six content-bound runtime assets. It exits 1 for the substantive missing-lane/incompatible-contract gate, with no missing local files.

## Sources for manual review

- [DrivenData problem, metric, and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Official competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DOE/NLR competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GDR INGENIOUS compilation](https://gdr.openei.org/submissions/1391)
- [Shared template immutable source](https://github.com/buffedlizard55-lab/GEMSDOE32/tree/e56a10a9d2f218c05ea66c5a5b7228bb780bb5a7)

Only GitHub-hosted material and mirror bytes were reachable from this runtime. Links to DrivenData, NLR, USGS and GDR are official manual-review pointers; their current page contents were not fetched here.

## Remaining work, in order

1. Supply the missing single method-lane paragraph; do not infer one from the ranked research slate.
2. Resolve issues 49, 53, 60 and 61 centrally in the shared template, publish new immutable hashes, and rerun its synthetic plus real-input regression suite. Do not carry a downstream private patch.
3. Authenticate organizer sample/features/catalogue bytes and clarify why the mirror has byte-identical `labels.tif` and `existing_faults.tif`. Confirm outside-footprint encoding with the organizer.
4. Build a complete immutable registry and resolve the dense-lattice rule at protocol level rather than exempting or jittering around it.
5. Only then run every-feature leakage canaries, same-fold candidate/baseline buffered holdouts, and pre-/post-placement uniqueness checks within the three-experiment budget. A separate selector may consider a slot only after every gate passes.

Latest machine card: [`evidence/run_card_arena_a2fe7ce0_20261028.json`](../evidence/run_card_arena_a2fe7ce0_20261028.json).
