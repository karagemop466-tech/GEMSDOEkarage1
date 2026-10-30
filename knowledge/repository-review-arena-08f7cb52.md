# Repository review — `arena/08f7cb52-gemsdoekarage1`

**Review date:** 2026-10-30 (UTC)  
**Scope:** source tree, submission decision pages/data, fail-closed release gate, current run-card evidence, CI and tests. This is a review-only change; no experiment, candidate raster, or submission was created.

## Decision

**NEGATIVE / DO NOT SUBMIT. No file is cleared.** The checkout does not contain an assigned method paragraph/lane, and its own binding protocol says to stop when the lane is absent. The latest governing review in `AGENTS.md`, `knowledge/session-review-arena-5ee7ef4b.md`, additionally documents that the internal catalogue holdout cannot rank off-catalogue strategy and that the recent candidate did not beat a matched random placement. A locally format-valid TIFF is not evidence of a high leaderboard score.

## Findings

### P1 — No defensible leaderboard-score estimator

The nine-site table contains user-reported scores, but the project does not have organizer labels/receipts to validate a calibration from HOLDOUT-DTI to leaderboard DTI. `docs/submission-hub.html` correctly says the holdout is not calibrated and shows the site estimate as unavailable. Keep that restriction: do not relabel holdout values, historical reported scores, or model projections as leaderboard estimates. The 0.2778 GEMSDOE32 value is user-reported, not an organizer-confirmed receipt in this checkout.

### P1 — Current protocol blocks promotion, independently of TIFF format

`src/gemskarage1/guard.py` records that there is no assigned lane and throws before inherited experiments run. `scripts/release_gate.py` is fail-closed and returns `ok_to_submit: false` even for a scientific “promote” result, requiring a separate selector. This is consistent with the instruction not to spend a weekly slot before a successful holdout/uniqueness decision. Do not bypass these controls to satisfy the request for a downloadable TIF.

### P1 — The duplicate gate cannot distinguish the historical candidate family

Saved evidence repeatedly finds extremely high proximity overlap with the pinned 13GEMSDOE lattice; a separate null audit says the literal 70%/3-pixel rule is saturated even for random placements. This is an internal protocol, not a competition rule. The decision owner must resolve whether the lattice is an exempt calibration witness or a binding registry member before this gate can authorize anything. Until then, report the literal result and do not silently exempt it.

### P1 — Tests are not runnable in this sandbox as checked out

`python -m pytest -q` fails because `pytest` is absent. A repository-local `.venv` was created (ignored by Git) and pytest installed; collection then failed across 24 modules because NumPy is absent. No test passed or failed on application behavior in this environment. CI (`.github/workflows/checks.yml`) installs `requirements.txt` before running tests, but CI results were not fetched in this review. Re-run the complete suite in an environment with the pinned project dependencies before claiming green.

### P2 — Stale and competing “current” artifacts are a maintenance risk

The repo retains many historical run cards, candidate rasters, decision pages, and session reports. `AGENTS.md` directs the reviewer to `knowledge/session-review-arena-5ee7ef4b.md` and its run card, while other files describe older sessions. A reader can mistake an older downloadable research TIFF or a prior “latest” page for a current recommendation. Continue to use one generated source-of-truth status banner and ensure the site renderer marks all superseded artifacts as historical / not cleared.

### P2 — External-data and organizer provenance remain unresolved

The tracked registry and competition-data restoration records identify third-party mirrors; hashes prove local byte identity, not organizer authenticity. The competition data tab is login-walled in the recorded project history. Thus CRS/grid checks against a mirrored sample are useful local checks but do not prove portal acceptance. Obtain organizer-authenticated data and a portal receipt before asserting acceptance or comparing private-label performance.

## Evidence checked

- `AGENTS.md` and `knowledge/session-review-arena-5ee7ef4b.md` / `evidence/session_5ee7ef4b_run_card.json`.
- `scripts/release_gate.py`, `src/gemskarage1/guard.py`, `scripts/preflight.py`.
- `docs/submission-hub.html`, `docs/data/submission-hub.json`, `docs/data/latest-run-card.json`.
- `.github/workflows/checks.yml` and the current repository test collection attempt.
- JSON syntax check passed for the two reviewed JSON artifacts above. This is not a substitute for the Python test suite.

## Recommended next work (in order)

1. Resolve and document the lane assignment and whether the lattice is a calibration-only witness; do not let code infer either decision.
2. Repair/agree the evaluator objective for off-catalogue prediction with the project/template owner. Until the holdout aligns with the competition's hidden-fault target, it cannot validate the requested strategy.
3. Restore organizer-authenticated training features, labels, and submission template (or obtain an organizer submission receipt) and record hashes/provenance.
4. Run candidate-level, feature-alone leakage checks and same-split spatial holdout with the shared template; use a random baseline and report HOLDOUT-DTI with evaluator version, withheld-positive count, and valid CI.
5. Only after those pass, run complete-registry pre-placement and saved-byte audits, validate final TIFF on disk, and request a separate selector decision. Do not present a score projection as an observed score.

## Verification passes

1. **Pass 1 — inventory:** read the standing instructions and latest governing session, checked core scripts, summary, and CI.
2. **Pass 2 — adversarial:** checked whether local format validation or a historical positive report could imply promotion; they cannot. Confirmed the protocol gate requires a lane and multiple evidence fields, and it keeps slot selection separate.
3. **Pass 3 — re-check:** checked review facts against current tracked evidence and reran JSON parsing and test collection. Test execution is blocked by missing dependencies; no new scientific or competition result is claimed.
