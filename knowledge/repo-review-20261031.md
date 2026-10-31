# Repository review — 31 October 2026

## Executive decision

**NEGATIVE / DO NOT SUBMIT any new file based on this review.** No new TIFF was generated, no weekly slot was selected, and no competition score is asserted. This is a review of the checkout on branch `arena/da8c1e63-gemsdoekarage1`, based on `c43fe5c` (PR #111 merge).

The checkout contains a promising KP1 research raster and extensive site/evidence infrastructure, but the repository itself records an unassigned canonical lane/template, incomplete registry coverage, and a fail-closed preflight. More importantly, the root README simultaneously says one file is cleared (KP1, an older session) and that a newer review says no file is cleared. The safe, current interpretation is **not cleared** until that contradiction and the release-gate evidence are reconciled. This review does not retroactively invalidate any competition receipt; no organizer receipt is present for KP1 in the reviewed evidence.

## What was reviewed

- Root `README.md`, `AGENTS.md`, `registry/template.json`, `scripts/preflight.py` output, the KP1 run card/release receipt, and the nine-site table.
- Python sources, scripts, tests, vendored template tools, and committed evidence inventory.
- Static checks: `python -m compileall -q scripts src tests vendor/gems57 vendor/template57` passed. All 289 JSON files parsed successfully.
- The full pytest suite could **not** be run: this environment has no pytest, NumPy, SciPy, scikit-learn, or rasterio installed; `.venv/` is absent. No dependency installation or data download was attempted.

## Findings and irregularities

### 1. Conflicting clearance messaging — high severity

`README.md` begins with “PROMOTE: ONE FILE IS CLEARED” for `karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif`, but its next “CURRENT REVIEW” section states “no file is OK to download and submit” and gives a negative verdict. `AGENTS.md` also has multiple dated, parallel session instructions and branch names that do not match this checkout. A user-facing summary can therefore communicate opposite submission decisions depending on which heading is read first.

**Action taken:** added a review notice at the top of README that supersedes the stale historical clearance for this checkout and links to this review. Historical session records remain in place and are not silently rewritten.

### 2. KP1 is not cleared by the requested parallel-run protocol

The KP1 run card reports a candidate score projection of **0.2789 (PROJECTED, not a score)** and a `promote` verdict. The recorded uniqueness comparison is against the nine focus files only; it does not document a complete current registry scan. `registry/template.json` leaves both `method_lane` and `canonical_template_assignment` null. Separately, the current `scripts/preflight.py` result is `negative`, with `ok_to_submit: false`; it flags the literal pinned-lattice overlap constraint as infeasible at the historical dot budget and does not generate a candidate.

The KP1 run card's off-catalogue instrument has 62,122 positives, but its recorded confidence interval is for a **paired difference against a random control**, not a confidence interval for the candidate's HOLDOUT-DTI itself. It is a distinct external inventory protocol, not the requested withheld-whole-segment catalogue holdout. The claimed `promote` is therefore not equivalent to the request's validation-and-release gate. This review does not call the projected number an estimated leaderboard score.

### 3. Data provenance and validation scope

The release artifact has a saved-byte format receipt and SHA-256, but its provenance section identifies mirrored inputs rather than organizer-authenticated competition files. The KP1 evidence itself notes portal acceptance was not tested and no organizer receipt exists. Format validity is not proof of portal acceptance or predictive value.

### 4. Nine-site summary is useful but not a real score estimator

`docs/data/nine_site_executive_20261031.json` labels scores USER-REPORTED / UNVERIFIED and says leaderboard estimates are unavailable. The measured pairwise masks show extreme overlap (the exact D25/D30 duplicate is one clear example); thus “best reported” is a safe descriptive label, not evidence that the model generalizes or is submission-unique across the full competition registry. Existing source scores cannot be independently verified against the organizer from this sandbox.

### 5. Test and deployment verification is incomplete in this environment

Compilation and JSON parsing succeed. Pytest and raster-level validation were not re-run because required Python dependencies are missing. Existing JSON receipts and historic test counts are evidence artifacts, not substitutes for reproducing current checks. The public site build was not regenerated.

## Scientific and procedural judgment

GEMSDOE32 B2's cited 0.2778 is the highest **USER-REPORTED** value among the nine sites provided. Local forensic records say B2 is a filtered version of the densely dotted D25 family, with catalogue-adjacent points removed. That is consistent with fewer low-value false positives under the stated asymmetric DTI, but it does not establish why its private-test score was high: the private truth is unavailable, user-provided score receipts are absent, and the catalogue holdout is not the same target as off-catalogue private truth. A higher score is possible in principle; this checkout does not establish one.

The repo already holds several geological proposals and past experiments. I did not invent fresh “untried” hypotheses or run experiments: the request's parallel protocol demands a single assigned method lane, canonical shared evaluator/writer, cached feature stack, and a hard experiment budget. The lane and template assignment are null in the registry, the complete registry is unavailable, and no supported shared feature cache is available in this runtime. Proceeding would violate the explicit stop conditions. No submission selector was run.

## Next work, in order

1. Resolve the conflicting README/AGENTS clearance instructions and verify whether any organizer receipt exists for KP1. Keep all projected and locally measured values explicitly labelled.
2. Have the project owner define/confirm the one lane, canonical shared template revision, duplicate inventory and interpretation of the lattice rule. The current literal rule conflicts with prior claims of promotion.
3. Make the official input bundle and complete registry available, with hashes and provenance. Verify official sample grid CRS/shape/transform against every candidate.
4. Install pinned project dependencies and run the entire suite plus saved-byte raster validation from this checkout; then build and inspect the Pages site.
5. Only after the above, preregister a compliant spatial-block holdout, feature-alone leakage canaries, and a maximum-three-experiment plan. Report holdout DTI with evaluator version, withheld-positive count and score CI; never call it a leaderboard estimate.
6. Do not select a weekly slot until the candidate passes release gates and a separate selector confirms eligibility. Report organizer scores only from the organizer submission receipt.

## Run card for this review

```json
{
  "hypothesis": "No new geological claim tested; review whether repository evidence supports releasing a unique submission.",
  "mechanism": "Audit the existing release claim, registry completeness, lane/template assignment, provenance, and fail-closed preflight.",
  "named_non_fault_process_that_could_mimic_it": "Lithologic contacts, volcanic-flow margins, or geomorphic scarps can mimic geophysical or topographic fault signatures in existing candidate methods.",
  "holdout_dti": {"label": "HOLDOUT-DTI", "value": null, "evaluator_version": null, "withheld_positives": null, "ci95": null, "status": "not run in this review; no new experiment"},
  "correlation_overlap_vs_registry": {"value": null, "status": "not recomputed; complete registry unavailable; preflight reports only one lattice witness and nine historical rasters"},
  "raster_sha256": null,
  "validator_output": {"no_nan_inside_footprint": null, "values_in_0_1": null, "crs_shape_transform_match": null, "status": "not run; dependencies unavailable"},
  "submission_name": null,
  "submission_note": "Review only; no submission authorized.",
  "verdict": "negative"
}
```
