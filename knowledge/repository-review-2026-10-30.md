# Repository review — 2026-10-30

## Executive decision
**No submission is cleared. Do not download a repository TIFF for competition upload.** This review found no basis to claim a unique, high-scoring, portal-ready prediction. The current repository already records negative release decisions, failed duplicate gates, incomplete registry coverage, and missing authenticated competition data. Treat archived/past run cards as evidence of what their sessions reported, not as current approval.

## Scope and checks performed
- Read the repository operating instructions (`AGENTS.md`), README, current executive-summary page, current run-card evidence, previous review notes, and the recorded verification-pass log.
- Inspected the tracked tree, submission/download inventory, test configuration, and current Git status/branch.
- Installed the declared `requirements.txt` into an ignored `.venv` and ran the full suite: **431 passed, 1 skipped, 1 failed**. The lone failure is `tests/test_focus_sites_20261029.py::test_candidate_is_research_only_and_format_valid`, which requires missing `data/bridge/existing_faults.tif`. Thus tests execute, but the suite is not green without the ignored/restored dataset.
- No source code, model, or TIFF was generated or modified during this review. No submission slot was used.

## Findings

### Blocking / high risk
1. **Scientific clearance is correctly negative, but prominent site content contains a temporal conflict.** `docs/executive-summary.html` presents the nine-site reported-score ranking and a 29 Oct leaderboard snapshot, while README/AGENTS and historical session files contain different dates, candidate states, leaderboard values, and lane conclusions. A reader can mistake old cards/pages for current evidence. Keep a single generated current-status source and clearly badge every historical result with its timestamp and status.
2. **The requested estimate cannot currently be supplied honestly.** The listed 0.2477–0.2778 site values are user-reported, not organizer-confirmed receipts. The active/current evidence says no artifact-linked receipt and no validated estimate. Keep estimates “not estimable”; do not convert a holdout DTI into an organizer leaderboard projection.
3. **Uniqueness is registry-bounded, not universal.** The evidence describes SHA-pinned mirrors and a subset of the wider fleet, not a complete official registry. The literal 70% / 3-pixel proximity test also rejects prior generated candidates. Never label a file globally unique or submission-ready based only on comparison with the nine focus sites.
4. **No current experiment is cleared by the documented gates.** `evidence/active_run_card_20261028.json` explicitly records a negative verdict and 98.53% lattice overlap; `AGENTS.md` additionally says later candidate lanes failed similar gates and no lane is assigned. Do not revive their TIFFs or bypass the duplicate rule. The separately archived CDA1 runner/report are explicitly quarantined; their reported metrics must not be treated as holdout measurements.
5. **The full test suite depends on ignored local data and is not green in this checkout.** After installing `requirements.txt`, 431 tests passed and one failed because `data/bridge/existing_faults.tif` is absent; one test was skipped. This is consistent with the documented data-placement blocker, but CI/local test behavior should be explicit: mark data-dependent integration tests with a clear skip when fixtures are absent, or provision authenticated/hash-verified test fixtures without silently treating missing data as a pass.
6. **The data provenance gap remains.** Repository notes distinguish hash-pinned third-party mirrors from organizer-authenticated competition data. A matching byte hash establishes mirror integrity, not official provenance. The login-walled official data and unverified local template prevent a claim of competition-ready validation.

### Medium / maintainability
- `README.md` contains a very long historical prompt and repeated session summaries; `AGENTS.md` accumulates many “latest” entries. This is useful provenance but makes the current operating decision hard to find. Keep the standing prompt in one canonical file, link it from README, and maintain a concise current-status pointer plus dated archive.
- Several old generators and candidate artifacts remain in the repository alongside quarantined code and historic promotion claims. The existing notes warn against using them; strengthen this with one fail-closed release command that checks provenance, full-format validation, canary, holdout, registry overlap, lane authorization, and selector receipt.
- The page's score table is a report of historical claims, not proof of current leaderboard status. Give each score its exact source capture date and classification in the table itself, and avoid phrases such as “best submission to submit” when the row is third-party/learning-only.

## Nine-site interpretation
Using only the score claims in the prompt/current repository table, GEMSDOE32's `h33-h33-2-b2` (reported 0.2778) is the highest of the nine focused sites. The value is **USER-REPORTED / UNVERIFIED**, not an expected score or independently confirmed organizer receipt. Historical raster audits report substantial overlap/subset relations among these sites, so these files are useful for forensic learning but are not valid new submissions. The repository provides no support for claiming a new candidate will exceed 0.2778 or the stated 0.3195; leaderboard snapshots differ by timestamp and are not evidence of generalization.

## Next work, in order
1. Resolve the parallel-run lane/template/registry policy with the designated coordinator; do not invent a method lane.
2. Provide the canonical cached feature stack and authenticated footprint/template with provenance, then audit the shared evaluator/writer in the owning template (not a private fork).
3. Repair/install dependencies and run CI; publish exact command and pass/fail result.
4. For any authorized candidate: preregister up to the stated experiment budget; single-feature leakage canaries; whole-segment buffered hide-and-recover with fold-local catalogue features and pixel-exact scoring mask; pooled DTI with CI; pre-placement surface and post-placement dot uniqueness against complete registry; saved-byte validator; then separate slot selector.
5. Until every gate passes, keep a negative run card and no active download button. Any score must be labeled HOLDOUT-DTI with evaluator version, withheld positives and CI, or ORGANIZER-CONFIRMED with the receipt.

## Pull request status
This review report is the only change; no application code, model, data, or TIFF was altered. It is suitable for a documentation-only pull request. Any merge must not be interpreted as model validation or submission clearance.
