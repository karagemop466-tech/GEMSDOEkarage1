# Session review — `arena/dc2e4c0c-gemsdoekarage1` — 29 October 2026

## Decision

**NEGATIVE / DO NOT SUBMIT.** This was a repository review, not a geological experiment. No new candidate surface or GeoTIFF was generated, no holdout was run, no weekly slot was selected, and no organizer submission was made. No numeric estimate of competition performance is defensible from this review.

The [machine-readable run card](../evidence/session_dc2e4c0c_run_card.json) records nulls for all unmeasured scientific outputs. The historical `0.2778` attributed to GEMSDOE32 B2 remains user-reported/unverified in the existing repository analysis; it is not a directly reproduced organizer receipt. The reported `0.3195` and `0.4413` context likewise remains user-provided unless receipt-linked source evidence is added.

## Pass 1 — inspect and test

- Read the branch's `AGENTS.md`, README, standing prompt, prior review and active run card, evidence registers, focused site pages, workflow configuration, scripts, and test layout.
- Installed the declared Python requirements into ignored `.venv/` only; no generated data was added to Git.
- Ran the full suite before changes: **353 passed, 4 failed**. Two distinct defects were reproduced:
  1. `scripts/run_karage1_experiments.py` had malformed syntax at `_require_protocol_repair()` (`pass # raise RuntimeError(` followed by indented message strings). Python failed during parsing instead of the intended explicit protocol block. It was still non-executable, but did not give the designed fail-closed diagnostic or expected exit behavior.
  2. At initial inspection, `docs/downloads/unique-hyp-kth-therm-mask-20261028-zeros.tif` was not covered by either saved-byte audit inventory used by the current renderer. The old `docs/executive-summary.html` simultaneously claimed this raster was cleared for submission, quoted a holdout result without complete supporting evidence, and supplied a download button. During integration, main advanced with PR #58, which added a separate pinned-mirror retraction receipt for the raster; see the integration note below.
- `python scripts/build_site.py` renders the current negative executive summary deterministically, but the tracked legacy page had not been regenerated. The old page's claims were therefore an active false-green-light risk until corrected.

## Pass 2 — adversarial review and fixes

- Restored the explicit `raise RuntimeError(...)` in the quarantined historical runner. This preserves the intended protocol stop while producing a testable, clear failure.
- Moved the orphaned TIFF, ZIP, and sidecar out of `docs/downloads/` into `archive/quarantined-20261029/`. The artifact is preserved for provenance, but no longer exposed as a submission download.
- Replaced the misleading `docs/data/unique-hyp-kth-therm-mask-20261028-zeros.json` promotion card with a negative supersession record. The old score claim is not repeated as HOLDOUT-DTI: no evaluator/version, withheld-positive count, CI, or reproducible holdout receipt is available. During concurrent-main integration a mirror-based saved-byte audit was added and records a literal lattice duplicate (99.9017% overlap); see the integration section and receipt. This is not an organizer-authenticated complete registry.
- Rebuilt the active executive-summary page with `scripts/build_site.py`; it now says **DO NOT SUBMIT** and does not advertise the quarantined file as approved.
- Re-ran the targeted quarantine/release/audit tests: **29 passed**, 1 existing Rasterio/Affine deprecation warning.
- Rechecked the shared preflight and template integrity. Both intentionally fail closed. Required `.cache/gems_work/feature_stack.npy` and organizer training inputs are absent. Recorded vendor bytes for `submission_writer.py` and `uniqueness.py` differ from the current integrity pins; the vendored code is not thereby established as the authoritative shared template.

## Pass 3 — requirement recheck

- Ran the full repository suite after the fixes: **360 passed, 0 failed, 0 skipped** (software tests only; Rasterio/Affine emits pending-deprecation warnings).
- Confirmed all newly exposed prior TIFs are represented by committed audit scope after quarantine; no TIFF in this session is presented as approved.
- Checked that the site renders with the explicit negative decision and that the rebuild is deterministic after committing the rendered output.
- No new geology hypotheses were presented as “untried” based on a cursory name scan. README already contains a four-item ranked hypothesis slate from a prior preregistration. This checkout has no lane assignment or accessible authoritative feature stack to verify which mechanisms have been run across parallel sessions. Reusing or renaming those proposals as new would violate the user's novelty constraint.
- No official external page was freshly verified in this review. This sandbox's outbound access policy does not permit DrivenData, USGS or NLR hosts, and user-provided mirrors are not organizer authentication. Official source links already registered in the repository remain references, not fresh verification receipts.

## Scientific interpretation and next steps

The repository's B2 pixel-mask forensics are consistent with a parent D2.8 mask thinned near the mirrored catalogue; deletion could improve a precision/coverage tradeoff only if the removed dots have lower expected hidden-fault utility than false-positive penalty. Those mask relationships do not establish why the reported organizer value changed. A label-free, buffered, segment-heldout experiment with paired confidence intervals and controls would be needed to test causality; the holdout cannot be relabeled as a leaderboard projection.

The existing four-hypothesis table remains the research proposal list. To make a next candidate executable rather than speculative, obtain/record an explicit method lane and template owner, restore organizer-authenticated data and feature cache, resolve the literal registry-lattice rule with its owner, and complete a per-feature leakage canary before the maximum three allowed experiments. Every candidate must be screened against the full registry before placement and checked again on final dots; a duplicate ends that lane.

## Open limitations / handoff

1. No authenticated DrivenData data archive, scoring receipt, current leaderboard snapshot, or weekly-slot allowance is available here.
2. The method lane paragraph and canonical shared-template assignment are absent. Do not select a lane by inference.
3. Required data/cache files are missing; the vendored writer and uniqueness modules fail their immutable-byte integrity check. Do not bypass by creating a local fork.
4. Registry comparison evidence is mirror-based and incomplete. The protocol's lattice witness remains a literal duplicate stop for previously champion-sized dot sets; do not evade it by jittering, changing representation, or assuming the witness is exempt.
5. The exact rejected upload that triggered “Predicted values must be in range [0, 1]” is not identified by an organizer receipt. The archived K/Th candidate's old local format report is not portal acceptance.
6. The task requests a full verbatim prompt in README, but the repository's standing prompt explicitly says its older text was reconstructed, not preserved verbatim. This session did not silently claim that historical reconstruction is a transcript; this turn's requirements should be captured in future prompt maintenance if an exact transcript is required.

## Integration with concurrent mainline PR #58

While PR #60 was open, `origin/main` advanced through PR #58, which independently retracted the same stale false-clearance TIFF. The integration retains its pinned-mirror saved-byte receipt at `evidence/unique_hyp_kth_therm_mask_retraction_20261029.json`: it records 99.9017% directed 3-pixel overlap with the pinned lattice (literal duplicate) and <=26.54% forward overlap against the nine focus-site masks. This is a mirror-based artifact audit, not a full authenticated registry and not a score. I did not independently rerun that historical raster audit in this session. The merged evidence supersedes the earlier statement that the raster's uniqueness was unknown; the combined decision remains **DO NOT SUBMIT**.

The two concurrent PRs had both moved the same TIFF/ZIP/sidecar. Resolved by retaining the mainline path `archive/quarantined-20261029/`, preserving the exact byte hashes, retaining the mainline retraction receipt and separately storing this review's audit note. The active renderer now points to the merged path and explicitly mentions the lattice duplicate. After integration and the three new regression tests, the final suite is **360 passed, 0 failed, 0 skipped**, with 119 Rasterio/Affine pending-deprecation warnings. The suite and deterministic page build were rerun.

**Correct present-day answer:** there is no file in this session OK to download and submit, no defensible estimated score for a new artifact, and no basis to claim a score above the user-reported B2 result or current leaderboard values.
