# GEMSDOEkarage1 — evidence before a leaderboard slot

## Current decision: **NO APPROVED TIFF · DO NOT SUBMIT**

[Executive summary and nine-site table](docs/index.html) · [Scientific review and hypotheses](docs/research.md) · [Submission guide](docs/submission-guide.html) · [Negative run card](evidence/run_card.json)

**Read this standing brief at the start of every session.** This checkout began with only a one-line README. There were no previous-session next steps, data, models or cached feature stack to resume. No new TIFF was generated in this review, no holdout experiment ran, and no weekly submission slot was used. We will not manufacture an unvalidated artifact to make a download button appear successful.

## Standing user brief (normalized, not a verbatim transcript)

The user supplied a long duplicated prompt. This section preserves its operational requirements; it is not a claim that the entire prompt has been archived verbatim.

- Objective: place at the top of the DOE GEMS fault-discovery leaderboard through scientifically defensible, **unique** prediction GeoTIFFs. Geothermal conduits/vents motivate the work, but fault traces are the prediction target.
- Focus sites: **GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36**. Review historical best files and explain the reported GEMSDOE32 H33 B2 result. Publish per-site executive summaries with file, estimate, uniqueness and an unmistakable submit/no-submit decision.
- Never copy, rename or slightly alter a previous submission to imply novelty. Historical files are educational evidence only. Make a one-click TIFF download prominent **only when a genuinely new file passes all gates**.
- Use the single assigned method lane. Stop on surface or final-dot absolute rank correlation above 0.90, or directed overlap above 70% within 3 pixels of any registry raster. The method paragraph is **missing from this prompt**; do not invent an assigned lane.
- Reuse the template’s cached feature stack, `evaluate_holdout.py` and `submission_writer.py`. Do not privately fork shared tools. Hide whole fault segments with a buffer, recompute catalogue-derived features only from visible faults, mask visible traces pixel-exactly, and score pooled DTI with alpha 0.2, beta 0.8 and a 300 m triangular kernel. Verify this against official current rules when accessible.
- Test each feature alone; AUC above 0.90 is a leakage warning until explained. Compare against the current holdout best using the same evaluator and split. Version disagreements are blockers, not interchangeable estimates.
- Report **HOLDOUT-DTI** only with evaluator version, withheld-positive count and 95% CI. Use **ORGANIZER-CONFIRMED** only for a submission-page receipt. A projection is never called a score. Historical numbers without receipts remain explicitly USER-REPORTED, not validated results.
- Stop at three experiments or two hours. Promotion is separate from weekly slot selection. Do not consume a slot for a failed, duplicate, leaky or holdout-inferior candidate. Read the authenticated weekly cap; do not infer it.
- Before implementation, rank 3–5 geological hypotheses by qualitative expected improvement and cost, naming layers, physical signature, missing-fault mechanism, novelty scope and non-fault confounder. Do not assert external data are obtainable without checking.
- Automated saved-byte TIFF validation must check a single band, float32, finite values in [0,1], template-exact CRS/shape/transform, and artifact SHA-256. No human inspection may substitute for failed automated gates. Format validity is not performance validity.
- Give a future submission a unique name and a note of at most 140 characters. End a run with a JSON card: hypothesis, mechanism, non-fault mimic, holdout and CI, registry correlation/overlap, saved-raster hash, validator output, submission name/note and promote/negative verdict. Missing measurements must be null, not fabricated.
- Store trustworthy sources and provenance for audit. Provide a clean GitHub Pages site, source freshness, submission instructions, known limitations, and concrete next-session work. Review in three passes; test the implementation. Open a PR and merge only after checks pass.
- **Maximize P(Win)**: prioritize valid scientific evidence over more downloads or optimistic score forecasts. **Own the Outcome**: track failures end-to-end, fix actionable issues, and make negative results useful rather than hiding them.

## What this review actually verified

- Retrieved all nine repositories’ current README files via GitHub API with exact commits and retrieval time: [source refresh](evidence/source_refresh.json). These are repository claims, **not** official science verification or organizer receipts.
- Independently fetched the nine pinned historical best TIFFs, matched SHA-256 against the upstream manifest, checked grid/value properties, and measured final-dot spatial comparisons: [byte audit](evidence/historical_byte_audit.json).
- Independently tested the pinned 13GEMSDOE lattice: its 3-pixel neighborhood covers **99.871327%** of the finite template footprint. All nine historical best files exceed the 70% overlap stop. Only **6,649** cells are outside that neighborhood; more than **22,163** distinct dots cannot pass that particular gate. This is a geometric bound, **not a score**. It does not prove that a sparse passing candidate is scientifically useful or unique against the rest of the registry.
- Identified source-reported evaluator disagreements, missing organizer receipts, and conflicting historical leaderboard figures. No current leaderboard maximum or calibrated projection is asserted.
- Reviewed the official [reference README at a pinned commit](https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b): CPU-only execution is supported. GPU is not a general prerequisite.
- Added policy gates and tests. This policy is not a cryptographic attestation service: it evaluates supplied evidence, which must be produced by trusted shared tools. It never authorizes an upload or selects a weekly slot.

## Reproduce

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
python scripts/build_site.py

# GitHub authentication uses the existing gh connection. No credentials in chat.
python scripts/shared_tools.py bootstrap
.venv/bin/python scripts/restore_audit_inputs.py
.venv/bin/python scripts/audit_historical.py
python scripts/shared_tools.py preflight

# Refresh repository publications (does not silently approve a submission):
python scripts/refresh_sources.py
python scripts/build_site.py
```

The shared upstream checkout is pinned in [registry/template.json](registry/template.json), ignored under `.work/template`. Shared metric/writer code is **not copied** into this repo. Future `shared_tools.py evaluate` / `write` invocations delegate to those original tools and fail when lane or cache prerequisites are missing. The shared writer is designed for binary masks: do not assume it preserves continuous probabilities. A blocked preflight is expected now.

Data and caches remain ignored to avoid committing hundreds of megabytes or unlicensed mirrors. Pinned mirror hashes establish byte consistency, not organizer authenticity. Audit reproduction requires GitHub connectivity and dependencies. `gh` errors require reconnecting GitHub, never pasting credentials into chat.

The site is static. It cannot train a model in the browser. Current GitHub Pages serves `main` at repository root; root `index.html` routes to `docs/`. [CI](.github/workflows/checks.yml) tests policy gates and checks deterministic site generation. Source refresh is explicit and timestamped; this is **not a real-time science/leaderboard feed**. Other owners’ sites have not been modified.

## Next session / limitations

1. Record the omitted method lane before any scientific experiment; do not choose a parallel lane arbitrarily.
2. Restore a verified **shared cached** feature stack. Raw owner-mirror data can be restored through the template’s manifest, but there is no local feature cache and privately rebuilding it violates the current protocol.
3. Reconcile holdout versions and establish a same-evaluator current best. Test each feature, use whole-segment buffered folds and visible-only catalogue processing, and record paired uncertainty.
4. Resolve the dense lattice issue explicitly. Do not drop registry members or relax thresholds silently. A sparse lane-compatible hypothesis may be tested if allowed, but the bound alone is not a model.
5. Acquire current official rules/metric, receipts and cap through permitted access. This runtime only allows GitHub, npm and PyPI hosts; DrivenData, Dropbox, USGS, INGENIOUS, NLR and other science sites are not directly accessible. No new external scientific dataset or literature conclusion is claimed verified here.
6. Only after genuine scientific promotion and separate slot selection should a new saved-byte-validated artifact be published with a prominent download, unique name and short note. The urgent TIFF/high-score request remains **unfulfilled**, transparently, until these gates can actually pass.

[Detailed ranked hypotheses, three-pass review, sources and explanation of the historical 0.2778 report](docs/research.md).


## Concurrent-main reconciliation (this review)

Before this PR could merge, another session merged a separate H-UNQ-1 prototype into `main` (merge `5965164`). That work is preserved in `cards/`, the additional legacy pipeline scripts, and `docs/downloads/`. The original branch at the start of this review still contained only the one-line README; these were concurrent additions, not inputs to this review’s experiments.

**The inherited H-UNQ-1 TIFF is a synthetic stand-in with a placeholder geotransform. It is NOT an approved submission, not a tested geological discovery, and has no measured holdout or registry clearance.** Merely regridding synthetic predictions does not make them scientifically valid. Its earlier `cards/run_card.json` is historical evidence from that session, not the current review card. The current decision is `evidence/run_card.json`. The current dashboard intentionally does not advertise that TIFF as competition-ready.

The inherited `scripts/evaluate_holdout.py`, `scripts/submission_writer.py` and generator are not the pinned shared tools required by this review’s reuse protocol. `scripts/shared_tools.py` delegates to the pinned upstream template instead. Legacy text also reverses the FP/FN coefficients; do not use it as metric authority. Audit against the official evaluator before training or promotion.
