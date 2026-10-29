# Session review — `arena/2b7c50b3-gemsdoekarage1` (29 October 2026)

## Executive result

**NEGATIVE / DO NOT SUBMIT.** This was a repository, artifact, and website review—not a geological experiment. No holdout ran, no TIFF was generated, no weekly selector was run, no slot was selected/spent, and no upload was attempted. This session has **zero geological experiments**, so the three-experiment/two-hour experiment budget was not used.

The current dated saved-byte audit covers **all 11 local `docs/downloads/*.tif` files and 9 SHA-pinned peer rasters**. Every local TIFF and all nine peers exceed the literal 70% directed 3-px overlap threshold against the pinned lattice. A separate exact-byte reconciliation accounts for **all 15 Git-tracked TIFF paths (13 unique SHA-256 byte identities)**: 11 download-directory paths and 4 quarantined archive paths. The two archived CDA1 paths are byte-identical to already-audited download files; three distinct synthetic archive assets are verified against `docs/data/archive-review.json`. The archive files remain quarantined and none is cleared. This is a conservative disqualification witness only; the owner-authenticated organizer registry, pre-placement surfaces, and portal receipts are absent, so the audit does not certify registry completeness or acceptance.

The historical `unique-hyp-kth-therm-mask-20261028-zeros.tif` is **not eligible**. Its saved bytes are a literal lattice duplicate even though it is geometrically distinct from the nine focus-site masks under the audited criteria. The old sidecar's `promote` verdict and numeric score assertion have been superseded. No reportable HOLDOUT-DTI is claimed for this raster.

## Starting-state gates

- `registry/template.json` has `method_lane: null` and `canonical_template_assignment: null`. The active checkout does not contain an authorized lane paragraph to bind to.
- The required shared cache and organizer files are absent: `.cache/gems_work/feature_stack.npy` and `.cache/gems_data/{existing_faults.tif,training_features.tif,sample_submission.tif,labels.tif}`.
- Shared-template provenance/integrity is unresolved, including source/execution pin disagreement and vendor-byte mismatches. No private fork, local repin, or owner-template replacement was made.
- The pinned-reference TIFFs fetched from GitHub in the prior work session are mirror evidence, not organizer-authenticated model inputs. The current environment's outbound host allowlist did not permit a fresh check of DrivenData, USGS, GDR/OpenEI, or NLR payload availability. Official links are recorded in the hypothesis file for manual review; external-data hypotheses are marked not viable until access/coverage/license are confirmed.
- No valid, same-evaluator frozen holdout baseline is available for a new candidate. No holdout is authorized before lane/template/data gates pass.

## Dated local and peer raster audit

Durable receipt: [`evidence/local_downloads_and_peer_audit_20261029.json`](../evidence/local_downloads_and_peer_audit_20261029.json). The audit was run from saved bytes against the pinned mirror template, 13GEMSDOE lattice, nine focus-site masks, and nine SHA-pinned peer rasters. It records full hashes, byte sizes, format diagnostics, positive-pixel counts, overlap, and fail-closed authorization. The script now writes a dated default receipt and describes the inventory count dynamically.

| Local TIFF | Positive pixels in footprint | Within 3 px of lattice | Directed overlap | Literal result |
|---|---:|---:|---:|---|
| `gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4-zeros.tif` | 17,415 | 17,301 | 99.3454% | duplicate |
| `gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-nan.tif` | 37,654 | 37,570 | 99.7769% | duplicate |
| `gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif` | 37,654 | 37,570 | 99.7769% | duplicate |
| `gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-nan.tif` | 36,000 | 35,959 | 99.8861% | duplicate |
| `gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-zeros.tif` | 36,000 | 35,959 | 99.8861% | duplicate |
| `karage1-bbstep-buried-basement-20261028T180000Z-nan.tif` | 17,766 | 17,504 | 98.5253% | duplicate |
| `karage1-bbstep-buried-basement-20261028T180000Z-zeros.tif` | 17,766 | 17,504 | 98.5253% | duplicate |
| `karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif` | 37,654 | 37,612 | 99.8885% | duplicate |
| `karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif` | 38,200 | 38,174 | 99.9319% | duplicate |
| `karage1-unique-alteration-dots-20261028-zeros.tif` | 1,387 inside footprint | 1,385 | 99.8558% | duplicate; also has 2,113 unmasked positive pixels outside the footprint |
| `unique-hyp-kth-therm-mask-20261028-zeros.tif` | 37,654 | 37,617 | 99.9017% | duplicate |

All rows have `ok_to_submit: false`. Strict whole-array finite `[0,1]` and null/NaN-outside are separate diagnostics; they are not organizer acceptance. The full peer report has nine peers and marks each a lattice duplicate. No candidate was modified, jittered, thinned, or re-emitted to evade the gate.

## Unique-hyp sidecar retraction and replacement card

The audited file is `docs/downloads/unique-hyp-kth-therm-mask-20261028-zeros.tif`, SHA-256 `a18e8fea158c2c53357b2d9651a6ce874b6329f1fdff690b4e17e8b0bb6a75eb`.

- Against the pinned lattice, 37,617/37,654 (99.9017%) candidate dots fall within the closed 3-px disk. Binary-dot Spearman is 0.0002598; the mask is not exact-identical, but the strict directed-overlap stop is sufficient.
- Against the nine focus-site masks only, the worst directed overlap is 26.5364% (GEMSDOE27) and the maximum absolute binary Spearman is 0.0098883. That bounded result does not override the lattice witness or certify a complete registry.
- The pre-placement surface is unavailable. Full registry completeness and organizer acceptance remain unverified.
- The saved file is one-band float32 and passes the mirrored-grid/inside checks; inside values are finite and in `[0,1]`; whole-array strict finite/range diagnostics pass. The null/NaN-outside variant fails because the saved file encodes outside cells as zero. These are local diagnostics only.
- The old `docs/data/unique-hyp-kth-therm-mask-20261028-zeros.json` asserted `verdict: promote` and a numeric holdout result. The current card suppresses that scalar because this checkout did not contain a hash-bound evaluator-output/metric-term/bootstrap artifact reproducing it for these saved TIFF bytes. No holdout was run during this review. The superseding card is [`evidence/run_card_arena_2b7c50b3.json`](../evidence/run_card_arena_2b7c50b3.json); the public summary and raster receipt sidecar now both fail closed.
- Download-versus-submit status is explicit: **audit/research only; do not submit.** No submission slot or note is authorized.

The parallel Conduitcrest artifact's earlier score scalar is also absent from current public reporting. Its source run card has no 95% CI and the saved-byte lattice audit did not reproduce a holdout. The replacement public run card marks it not reportable; its original evidence file remains historical provenance, not a score source.

## Pre-implementation geological hypothesis screen

The ranked slate is in [`knowledge/hypotheses-20261029.md`](hypotheses-20261029.md) and is shown on the research page. It contains four proposals with named layers, physical signatures, off-catalogue rationale, mimics, differences from repository methods, qualitative potential/cost, and manual source links:

1. Cross-spectral phase-coherent magnetic/gravity edge junctions plus basement-depth context (top proposal; medium cost; adjacent to an older signed-offset concept).
2. Constrained joint density–susceptibility basement-interface inversion (medium qualitative potential; high cost and non-uniqueness risk).
3. Stratigraphic-contact displacement/truncation using USGS National Geologic Map Database material (not viable until exact coverage, payload, license, and registration are verified).
4. Inter-catchment area-normalized knickpoint recurrence using USGS 3DEP elevation (not viable until tile availability/access is verified; adjacent to an earlier drainage proposal).

No external-source data were fetched or validated in this session. No new feature, candidate surface, or geological conclusion is claimed. The top proposal was **not** run because lane, shared-template, data, and baseline gates fail. If later authorized, the protocol remains: a one-feature leakage canary (AUC >0.90 is leakage until disproved), then the whole-segment buffered hide-and-recover evaluator with fold-local visible-fault features, pixel-exact visible mask, pooled DTI α=0.2/β=0.8 and a 300 m triangular kernel, and paired confidence intervals against a frozen same-evaluator baseline. Stop at three experiments or two hours; no weekly selector/slot is included.

## Three implementation/review/recheck passes

### Pass 1 — requirements, prerequisites, and source inventory

- Read the current brief and prior evidence; verified lane/template nulls and absent shared data/preflight blockers.
- Fetched the small SHA-pinned mirror reference rasters through GitHub and rechecked the historical unique-hyp bytes against the lattice plus nine focus masks. This did not authenticate organizer inputs.
- Wrote the four-hypothesis pre-implementation slate before changing code. Marked external-data proposals non-viable until obtainability is checked.
- Audited all 11 current local GeoTIFFs and nine pinned peers; saved a dated, hash-bound receipt.

### Pass 2 — fail-closed fixes and claim correction

- Repaired the quarantined runner's syntax from a broken `pass # raise RuntimeError(...)` into an intentional `RuntimeError`; it now reports `BLOCKED` and exits before writing any experiment, model output, or TIFF.
- Made the local/peer audit scope and default dated output inventory-aware; regenerated the current 11+9 audit report.
- Replaced the unique-hyp false promotion/legacy score summary with a negative, hash-bound reassessment card. Suppressed incomplete Conduitcrest score reporting from public pages/run-card summaries as well.
- Updated the site renderer so the current audit counts, no-live-leaderboard status, non-download authorization, B2 mask explanation, hypothesis slate, and current run card are visible. Older 9+9 audit dates are labeled historical.
- Updated README, `AGENTS.md`, and the standing brief so the current status is read first and the user’s controlling gates are recorded.

### Pass 3 — final verification

- Final `.venv/bin/python -m pytest -q`: **359 passed, 119 warnings, 0 failed**. Warnings are Rasterio's existing `Affine` multiplication `PendingDeprecationWarning`; the additional regression test locks the DIPDUAL archive to the literal lattice duplicate stop and forbids a selector-acknowledgment waiver.
- `.venv/bin/python scripts/build_site.py`: **32 deterministic decision pages rendered**, “no submission authorized.” A repeated build is deterministic; the site tests also parse local links and page fragments.
- `git diff --check`: passed with no whitespace errors.
- `.venv/bin/python scripts/evaluate_holdout.py --hashes`: verified the pinned `gems57-pooled-hide-v2` implementation hashes; this was a hash check only, not a holdout execution.
- `scripts/preflight.py` and `scripts/shared_tools.py preflight`: both fail closed with `ok_to_submit: false`, `lane: null`, no canonical assignment, missing shared feature stack/organizer data, and template provenance/pin problems (vendored `submission_writer.py` and `uniqueness.py` mismatches; upstream assignment/repair not established). No holdout or TIFF generation was attempted.
- The site continues to render “DO NOT SUBMIT”; no live leaderboard, organizer score/receipt, or new candidate score was invented. The historical Conduitcrest scalar and unique-hyp promotion/score assertions are suppressed in current reporting.


## Remaining blockers and next work

1. Obtain the authorized method paragraph/lane and canonical upstream template assignment; resolve source/vendor/execution pin mismatch in the template owner’s repository, not here.
2. Restore the SHA-verified organizer cached feature stack and required competition data under the authorized template; distinguish every mirror from organizer-authenticated bytes.
3. Obtain the complete owner-authorized registry including pre-placement surfaces and final rasters. Apply both strict uniqueness thresholds, including the pinned lattice; no exceptions.
4. Freeze a same-evaluator baseline and confirm visible-only fold feature construction, exact mask behavior, and a single-feature leakage canary before any geological holdout experiment.
5. Verify official source coverage, format requirements, current leaderboard access, and submission-slot cap from authenticated organizer pages/receipts.
6. Only then consider a bounded holdout experiment for the assigned lane. No TIFF generation or selector step is authorized before all gates pass.

**PR/merge status:** [fill after final GitHub review; merge to `main` only if software checks and repository gates allow].
