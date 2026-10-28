# Repository review — 28 October 2026 (final pass)

## Decision

**NEGATIVE / DO NOT SUBMIT.** This review generated no GeoTIFF, ran no geological experiment, computed no new score, made no leaderboard prediction, and used no competition slot. This is an evidence-based stop, not a claim that the scientific objective is complete.

## Pass 1 — baseline inspection and execution

- Read `README.md`, `docs/standing-prompt.md`, the latest session reviews, the current run card, data/template manifests, holdout/writer adapters, format validator, release gate, site pages and test workflow.
- The canonical template pin in `registry/template.json` identifies a peer repository and commit, but its `method_lane` is `null`; the brief says to stay within one assigned method paragraph, which is not specified in the checkout. The wrapper preflight reports `ready_for_shared_tools: false` and missing `feature_stack.npy`, `existing_faults.tif`, `training_features.tif`, `sample_submission.tif`, and `labels.tif` under `.cache/`.
- No `data/` or `.cache/` inputs are present. The current tracked historical TIFFs are not eligible substitutes: prior saved-byte audit records show >70% three-pixel overlap with the pinned lattice. That audit was **not re-run in this review**, and its inventory is not the complete live organizer registry.
- The host Python lacked pytest. Installed repository requirements into ignored `.venv/` (not the system Python), then ran `.venv/bin/python -m pytest -q`: **218 passed**, with 53 Rasterio/Affine pending-deprecation warnings.
- Ran `.venv/bin/python scripts/build_site.py`: “Rendered 32 deterministic decision pages; no submission authorized.” `git status` remained clean after the build, so generated pages are deterministic in this checkout.

## Pass 2 — adversarial review

- Confirmed fail-closed preflight returns exit code 1 and explicitly does not authorize submission. It cannot distinguish an authentic source from a byte-identical peer mirror; absence/presence is not provenance.
- Confirmed the release gate deliberately leaves `ok_to_submit` false even for a scientific promotion; the separate selector is not run by this repo review. The run-card schema requires a named lane, buffered whole-segment holdout, visible-only features, leakage canaries, per-raster registry checks and TIFF-format evidence.
- Confirmed format validation can diagnose [0,1], grid, and outside-footprint encoding variants only against the supplied template. It expressly does not prove the template is organizer-authenticated or that the portal will accept the file. The earlier “Predicted values must be in range [0, 1]” rejection therefore remains undiagnosed; the rejected bytes and an authenticated sample/portal result are unavailable.
- Checked the user-supplied GEMSDOE32 score claim and peer score ledger: it is labelled user-reported/unverified, with no organizer receipt in the repository. No score estimate is defensible from the available holdout evidence, and holdout DTI must not be conflated with organizer leaderboard score.
- Checked the historical proposal slate: the latest research review labels four items as unexecuted and qualitative. None has verified source-byte availability in this runtime; do not represent source descriptions as an obtainability test or an experiment result.

## Pass 3 — original requirements re-check

- Nine focus-site pages and the executive summary already state historical file identities, user-reported scores, uniqueness failure against the lattice witness, and “unavailable” for new score estimates. They do not recommend historical files for submission.
- The home and executive-summary pages show a prominent **DO NOT SUBMIT** status and provide no active candidate download button. The historical research TIFF files remain in the repository for audit; their existence is not approval.
- The submission guide separates format validation, scientific promotion and weekly slot selection. No human-inspection placeholder is being used as a passed gate.
- No new submission was created because the required lane and shared cached stack are missing, and the extant TIFFs have recorded duplicate witnesses. Creating a different TIFF anyway would violate the lane/duplicate stop rules and would fabricate validation.
- The requested official-source live refresh and organizer confirmation could not be performed: network access in this environment is restricted to GitHub and package hosts; DrivenData, USGS, GDR, Dropbox and NLR are not reachable here. The linked pages in the repository remain review pointers, not new verification performed in this pass.

## Known irregularities / limitations

1. `registry/template.json` has no assigned lane and points to a peer lineage; the authoritative shared template/cache owner is unresolved.
2. The actual organizer dataset is login-walled. Restored peer mirrors, even hash-pinned, are not organizer authentication.
3. There is no current full registry inventory, no current feature surfaces for pre-placement comparison, and no documented authenticated sample file.
4. The literal lattice overlap rule is severe. Existing artifacts fail it; no rule exemption, density workaround, jitter or renamed copy is appropriate.
5. Historical experiment reports in the repo are not fresh results in this review. In particular, do not cite a prior-session HOLDOUT-DTI as a current measurement.
6. There is no automated connection to the DrivenData leaderboard, account, submission receipt, or weekly selector. The static site is not an up-to-date live feed.

## Next actions, in order

1. Obtain and record the explicitly assigned method paragraph and canonical shared template/cache identity; settle the lattice-as-registry interpretation with the protocol owner without changing the threshold silently.
2. Obtain organizer-authenticated competition inputs and a complete, dated registry with provenance. Restore the agreed cached stack through the shared owner’s tools.
3. Repair any evaluator/uniqueness defects in the authoritative template once, with tests; do not keep a private fork.
4. Freeze the spatial whole-segment buffered holdout and baseline; test every feature alone for leakage before a maximum of three experiments / two hours.
5. Compare pre-placement surfaces and final saved dots against every registry raster. Validate saved TIFF bytes against the authenticated submission template, then let the separate weekly selector decide whether a slot is available.
6. Build an authenticated source/leaderboard refresh mechanism only where allowed by organizer terms and credentials; otherwise clearly timestamp manually supplied facts as unverified, rather than describing the page as a live feed.

## Post-integration recheck

While this PR was being prepared, `origin/main` advanced with an independent
release-gate consistency check, a stricter local masked-pixel diagnostic, and
associated tests/reviews. Those changes were merged into this working branch
before the PR merge. After the first integration, 221 tests passed. The base
advanced again during PR preparation, so it was merged a second time; the latest
full suite then passed: **228 passed, 62 Rasterio/Affine pending-deprecation
warnings**. `scripts/build_site.py` again rendered 32 deterministic pages
without authorizing a submission, and `git diff --check` passed. Earlier 218- and
221-test runs are historical counts; 228 is the latest post-integration result.

## Run card (this review)

```json
{
  "hypothesis": "No new geological hypothesis was tested; assigned lane is unspecified.",
  "mechanism": "No model or raster was generated. Prior registered lattice overlap is a recorded duplicate witness for existing candidate files.",
  "named_non_fault_process": "Not applicable: no experiment was run.",
  "holdout_dti": {
    "label": "HOLDOUT-DTI",
    "evaluator_version": null,
    "withheld_positives": null,
    "dti": null,
    "ci95": null,
    "status": "Not measured in this review; no projection reported."
  },
  "correlation_overlap_vs_registry": {
    "preplacement_surface": "not measured",
    "final_dots": "No new raster; prior saved-byte reports record >70% overlap for the existing candidates versus the lattice.",
    "registry_completeness": "incomplete / not authenticated"
  },
  "raster_sha256": null,
  "validator_output": {
    "no_nan_inside_footprint": "not applicable: no new raster",
    "values_in_0_1": "not applicable: no new raster",
    "crs_shape_transform_match": "not applicable: no new raster",
    "template_authenticity": "not established"
  },
  "submission_name": null,
  "submission_note": null,
  "verdict": "negative"
}
```
