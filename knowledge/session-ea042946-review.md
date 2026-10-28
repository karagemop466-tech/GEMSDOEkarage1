# Three-pass review — 28 October 2026 — ea042946

**DO NOT SUBMIT. No new prediction raster, geological experiment, HOLDOUT-DTI measurement, score estimate, slot selection, or competition upload was made.**

## Pass 1 — review and repair

Read the README, standing prompt, AGENTS instructions and required prior reviews. Reviewed the nine-site dashboard, B2 explanation, research slate, pinned template configuration, release gate, shared-tool adapter, validator, and test/workflow configuration.

The promised single-method lane paragraph is absent from this request; `registry/template.json` records `method_lane: null`. All five shared cached inputs are absent in this checkout. The [actual preflight](../evidence/session_ea042946_preflight.json) records these blockers. Peer-mirror restoration would not supply an assigned lane, canonical template agreement, organizer provenance, or a complete registry. Rebuilding the quarantined private stack would violate the protocol.

Found and fixed a concrete automation defect: empty placeholders previously passed the shared adapter's input-presence check. Preflight now rejects empty and unreadable inputs as well as missing/nonfile inputs, reports those categories separately, and exits unsuccessfully. Evaluation and writing cannot bootstrap while these blockers remain. This changes only the local invocation adapter, not the shared evaluator or writer. No private scientific-tool fork was made.

## Pass 2 — adversarial review

Regression tests cover each required empty input, blocked preflight/evaluation/writing, read errors, directories, and dangling symlinks. A separate test makes the limitation explicit: nonempty arbitrary bytes can pass this lightweight check, but are **not** format validation, provenance authentication, scientific promotion, or permission to submit. This check deliberately does not load a large feature stack or authenticate data.

Existing duplicate decisions remain unchanged. Historical saved-byte audit evidence is inherited, not independently replayed in this session. The literal lattice rule cannot be bypassed by removing that witness, changing filenames, or selecting another encoding. No new surface exists to test.

## Pass 3 — verification and request reconciliation

- Full suite: **252 passed**, with **90 Rasterio PendingDeprecationWarnings**. These are software tests, not geological validation results.
- Targeted preflight suite: **23 passed**.
- `python scripts/build_site.py`: 32 deterministic pages; no generated-page diff.
- `git diff --check`: clean.
- Dependencies installed in ignored `.venv/`; system Python was left unchanged.
- GitHub Pages API reports the existing site uses `main`, root `/`, legacy build. This is configuration verification, not confirmation that the eventual deployment has completed.
- Organizer reference repository HEAD resolved through GitHub API to `aebe92f7c8a990f0e3443451b7a825d9afd6336b`. This verifies repository accessibility only; its code/data were not used to claim a measured result.

## Scientific decision and next work

The [existing four-candidate slate](research-review.md#ranked-candidate-hypotheses-qualitative-only) already ranks signed magnetic/gravity displacement, oriented radiometric alteration residuals, multi-catchment drainage asymmetry, and sampling-bias-corrected shallow thermal anomalies. These remain **proposals**, not proven novel fleet-wide or quantified DTI improvements. External payload accessibility is not established under this sandbox's GitHub/package-registry-only network. Do not present those external-data hypotheses as runnable.

The B2 audit records removal of redundant catalogue-collar dots from a parent prediction, not discovery of new geothermal vents. Improved prediction efficiency is a plausible DTI mechanism, not proof of the supplied result's cause. **0.2778 remains a user report, not an artifact-linked organizer receipt.** No available evidence supports estimating a new file's leaderboard score or promising to exceed it.

Before an experiment: establish the assigned lane and canonical shared template; authenticate official data/sample; provide the shared cached stack, complete registry and frozen same-fold baseline; resolve the literal lattice constraint without silent exceptions. Then run single-feature leakage checks and buffered whole-segment hide-and-recover, compare paired spatial uncertainty, audit surface and dots, and reopen saved TIFF bytes. A separate selector must check the live account quota before considering upload.

The request for a unique downloadable eligible TIFF and a validated improvement is **not fulfilled**. Manufacturing one without those gates would misrepresent its eligibility. The existing executive summary correctly keeps the submission download disabled and provides research-only links separately.

## Sources and evidence scope

- [Official reference code repository](https://github.com/drivendataorg/gems-prize-reference-solution): accessible through GitHub in this session.
- [Official competition problem and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/): reference link; not freshly accessible through the network allowlist.
- [Official competition data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/): account-gated; no authenticated download performed.
- [Prior source register](sources-2026-10-28.md): retained historical checks, not newly verified external pages.
- [Current executive summary](../docs/executive-summary.html) and [nine-site audit](../docs/data/reference-audit.json): inherited evidence, not new organizer receipts.
- [Session run card](../evidence/session_ea042946_run_card.json).
