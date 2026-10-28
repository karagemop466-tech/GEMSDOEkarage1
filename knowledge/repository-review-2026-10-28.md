# Repository review and official-reference forensics — 28 October 2026

**Decision: negative / DO NOT SUBMIT.** This is a review and source-code audit, not a model experiment. No candidate surface was generated, no holdout was run, no competition slot was selected, and no organizer upload or receipt exists. The protocol's duplicate stop and missing lane/template prerequisites remain binding.

## Scope and reproducibility

Reviewed the current branch after fast-forwarding it to `origin/main` at `1efeef6` (PR 29). Read the starting briefs, current README/run cards, nine-site audit, peer-candidate audit, shared-tool preflight, release gate, writer, validator, source manifests, and current site renderer. The independent local environment restored the 31 commit-pinned GitHub mirror files into ignored `.cache/gems_data` and fetched the 12 references required by the historical comparison. SHA-256 verification succeeded for those pinned files. This establishes identity with those public GitHub blobs only; it does **not** authenticate them as organizer downloads.

Replayed the existing historical-artifact audit using:

```sh
.venv/bin/python scripts/audit_references.py --fetch --cache .cache/references --out .cache/reference-audit-recheck.json
.venv/bin/python scripts/audit_existing_candidates.py --cache .cache/references --out .cache/candidate-audit-recheck.json
```

Results exactly reproduced the stored overlap counts for the two previously promoted files:

| Existing file | Lattice witness: dots within closed 3-pixel disk / candidate dots | Directed overlap | Decision |
|---|---:|---:|---|
| HMAS-SINTER historical TIFF | 38,174 / 38,200 | 99.9319% | Duplicate under literal protocol; do not submit |
| GPC-Z historical TIFF | 35,959 / 36,000 | 99.8861% | Duplicate under literal protocol; do not submit |

The lattice audit covers 5,167,373 pixels in the **mirrored** footprint. Its 3-pixel dilation covers 5,160,724 pixels, leaving 6,649 uncovered. This is a geometry measurement, not a score estimate. It means a large candidate footprint close to earlier dot budgets is severely constrained by the specified overlap rule; it does **not** prove every smaller candidate impossible. The denominator is candidate dots, and the rule must not be weakened or evaded by changing dot count, jittering or representation.

The nine-site summary remains historical only: values reported for GEMSDOE24/25/27/28/30/31/32/33/36 are owner/user reports, not organizer-confirmed receipts. The reviewed files are each negative against the lattice witness. No numeric estimate for a new candidate is defensible because there is no qualifying holdout experiment. One negative witness is enough to block a candidate; it is not evidence that the entire registry inventory is complete.

## Official reference solution: verified implementation, not a winning-score claim

The organizer's public [reference-solution repository](https://github.com/drivendataorg/gems-prize-reference-solution) was read at immutable commit [`aebe92f7c8a990f0e3443451b7a825d9afd6336b`](https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b). The reviewed notebook is [`unet-mc-cv-reference-solution.ipynb`](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb), SHA-256 `1a7622732ba00f67237058bc0efe79b45ba4e87c449fc9c1e5d6ea659de92ca0`. It is an upstream baseline, not evidence that any local or peer result is official.

The notebook implements a five-repeat U-Net workflow with 128-pixel patches, a random half-split of positive-containing patches, Tversky loss parameters α=0.2 and β=0.8, and a test-loss-selected model. These details are read directly from notebook cells 12 and 16. Its output cell saves `y_combined` directly as a raster using the label grid; it does not visibly perform an in-notebook submission-format range/nodata check. The notebook therefore explains a baseline workflow, but not the reported peer-site leaderboard values.

**Important validation distinction:** the notebook's held-out patches are selected randomly, rather than as buffered whole connected fault segments in spatial blocks. Its reported validation quantity is Tversky loss, not the official pooled 300 m distance-weighted Tversky index. Test patches are drawn only from blocks containing labels, so their sampling is not an unbiased representation of the full mapped footprint. Consequently, those validation losses are neither comparable HOLDOUT-DTI measurements nor leaderboard score estimates.

The notebook also uses `pad = patch_size - shape % patch_size`; when a dimension is already divisible by patch size this adds an entire patch rather than zero padding. The later crop to the original shape may make that extra border irrelevant to the saved dimensions, but it wastes computation and deserves correction upstream if the official reference is reused. The label-loading cell replaces every value below 1—including the `-1` nodata code shown in its saved output—with 0. This can expose outside-footprint nodata as negative labels unless the data handling/masks exclude it later. The reference notebook's loss and test split should therefore not be treated as a protocol-compliant benchmark without a careful upstream correction and an identical, spatially blocked evaluator.

The report at the pinned source declares a five-member Monte Carlo evaluation and describes random train/test splits. The claim that this proves model reliability or superiority is **not** made here: random spatial patches can share strong local autocorrelation, and a loss value does not establish official DTI. All observations in this section concern the identified pinned source version; re-check the upstream repository if its commit changes.

## Pipeline and blocker assessment

- `scripts/shared_tools.py preflight` correctly fails closed: the lane is null and `.cache/gems_work/feature_stack.npy` is absent. Cached source rasters alone are not a prepared shared stack.
- `registry/template.json` points at a peer repository commit, not the organizer reference implementation, and its `method_lane` is null. `vendor/PROVENANCE.json` identifies vendored `gems57` code as a copy from another peer. The vendored evaluator/writer are not the unresolved canonical shared template named by the user's parallel-run instruction.
- Current inventory is incomplete and mirror-based. A full public peer scan would still not certify private, unlinked, inaccessible or later submissions without independent inventory authority.
- The stored current run card's validator checks do not mean upload authorization. The two historical files use zeros outside the mirrored footprint, whereas the official format description says outside-boundary values should be null/NaN. Neither is portal-tested here. The specific cause of the earlier `[0, 1]` portal error is unknown because the rejected artifact and portal response context were not supplied.
- `scripts/release_gate.py` checks assertions in a run card; it does not independently authenticate the truth of those assertions or determine current portal slot capacity. Keep the process fail-closed and retain the selector step as separate.
- The public GitHub Pages source is currently configured for the repository's `main` branch root. The tests confirm the generated `docs/` pages and local links, but only a successful Pages deployment can confirm the live site after a new merge.

## Required three-pass closeout

### Pass 1 — implementation / review
Read all designated start-of-session documents, inspected the full tracked tree and workflow set, checked the active branch and upstream PR history, restored pinned inputs and replayed the saved-byte historical audit. Read the organizer reference notebook at a pinned commit and traced its patch selection, loss, padding and output cells. No implementation experiment was permissible because the assigned lane was not provided and the user's protocol requires stopping on duplicate witnesses.

### Pass 2 — adversarial review
Checked whether a passing format result could be mistaken for a unique or accepted submission; whether a site-reported score could be misrepresented as an organizer receipt; whether the baseline patch split could be called a spatial hide-and-recover holdout; and whether the source/cache pins establish official provenance. They do not. Reproduced counts agree with existing evidence. No historical TIFF is a suitable new submission.

### Pass 3 — request recheck and tests
Confirmed the site identifies a file and historical score claim for each focus site, states new score estimates as unavailable rather than inventing a projection, describes why B2's thinning could help without claiming causation, and exposes a future upload guide without a green clearance. Immediately after sync to `main` at `1efeef6`, **240 tests passed**. After integrating the subsequent `main` update at `64cc63c`, the suite passed **260 tests, 0 failed, 0 skipped**; 90 Rasterio pending-deprecation warnings. The local deterministic site renderer and HTML link checks are exercised by the suite. This is software verification, not geological validation.

## Next actions, in safe order

1. Obtain the actual assigned method paragraph and identify the authoritative shared template/cache. Do not substitute this repository's peer-derived vendor copy or the official reference notebook for that assignment.
2. Resolve, with the protocol owner, the literal registry rule's treatment of the published calibration lattice. Do not unilaterally exempt it. Build an authenticated, complete registry inventory; if the rule remains literal, the audit must honestly enforce its consequence.
3. Authenticate organizer-provided data and template bytes against allowed sources. The 31 mirror hashes are not that authentication. Confirm outside-footprint encoding and range behavior through official documentation or a permitted test artifact; do not infer the cause of the rejected file.
4. Only after 1–3, preregister one lane-specific hypothesis; fix any shared evaluator defect in its owning template; run the required whole-segment buffered hide-and-recover, fold-local catalog-derived features, exact visible-fault masking, per-feature canaries and paired pooled HOLDOUT-DTI with CI. Keep within three experiments/two hours.
5. Run surface-rank and final-dot comparisons against every registry raster. Stop on any literal threshold breach. A separate selector checks the weekly cap only after every scientific and format gate passes.

## Post-sync inherited BB-STEP artifact check

While this review PR was open, `origin/main` advanced and added a separately generated BB-STEP raster. It is not an artifact generated by this review, and its reported score results are not adopted as this review's measurements. To assess the safety of the merged repository state, I reopened the exact saved TIFF bytes and compared them with the previously fetched, hash-pinned mirror template, the nine focus-site masks, and the pinned lattice. The candidate SHA-256 is `72312302675d65cd1983239dd436412b5db1118a7c08f2a5807ef436b5536d6a`; it contains 17,766 positive in-footprint cells. These are registry/format measurements on third-party mirrors, not organizer-authenticated inputs.

| Saved-byte comparison | Dots within the closed 3-pixel disk / candidate dots | Directed overlap | Interpretation |
|---|---:|---:|---|
| GEMSDOE24 | 2,158 / 17,766 | 12.1468% | Under 70% for this reference only |
| GEMSDOE25 | 2,037 / 17,766 | 11.4657% | Under 70% for this reference only |
| GEMSDOE27 | 2,243 / 17,766 | 12.6252% | Under 70% for this reference only |
| GEMSDOE28 | 1,917 / 17,766 | 10.7903% | Under 70% for this reference only |
| GEMSDOE30 | 2,037 / 17,766 | 11.4657% | Under 70% for this reference only |
| GEMSDOE31 | 1,956 / 17,766 | 11.0098% | Under 70% for this reference only |
| GEMSDOE32 | 1,890 / 17,766 | 10.6383% | Under 70% for this reference only |
| GEMSDOE33 | 2,033 / 17,766 | 11.4432% | Under 70% for this reference only |
| GEMSDOE36 | 1,929 / 17,766 | 10.8578% | Under 70% for this reference only |
| Pinned lattice witness | 17,504 / 17,766 | **98.5253%** | **Duplicate; stop; do not submit** |

The nine focus-site comparisons support only a limited statement about those nine saved historical rasters. The lattice witness independently fails the user's literal overlap rule and controls the decision. The claimed low final-raster rank correlation cannot cancel the dot-overlap failure. No complete registry, pre-placement surface or organizer template was re-audited in this post-sync check.

The newly merged `evidence/exp2_bbstep_holdout.json` records a **HOLDOUT-DTI** claim of 0.0317904496, evaluator `gemsk-hide-recover-v1`, 60,988 withheld positives, 95% CI [0.0271378953, 0.0362712033]. This is copied from the repository's report, **not independently rerun here**, is not an organizer-confirmed score and is not a leaderboard forecast. The source run card itself says the selected local surface differs from the saved-raster holdout diagnostic and that the saved artifact fails the lattice rule. The report's stated advantage over a B2 control cannot override that stop or establish an organizer result.

The public README and executive summary now visibly identify the new TIFF as research-only / **DO NOT SUBMIT**. Its presence as a downloadable audit artifact is not a greenlight. After integrating `origin/main` at `761c74d`, the full local suite passed **287 tests, 0 failed, 0 skipped**, with 90 Rasterio pending-deprecation warnings; the deterministic site build rendered 32 pages without changes. The current answer remains **no TIFF OK to download and submit**.

No submission file is marked OK to download. Negative status is the current correct result.
