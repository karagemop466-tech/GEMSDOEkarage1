# Session review — arena/09bbfea3-gemsdoekarage1 (2026-10-29)

**Verdict: NEGATIVE / DO NOT SUBMIT.** No geological experiment, candidate TIFF, HOLDOUT-DTI result, leaderboard estimate, portal validation, or slot selection occurred. This session fixed a fail-closed data-preparation defect, corrected stale user-facing status, added a carefully scoped public-leaderboard feed, and preregistered three untested hypotheses. Software tests are not geological validation.

- Session card: [`evidence/session_09bbfea3_run_card.json`](../evidence/session_09bbfea3_run_card.json)
- Verified official sources: [`knowledge/official-sources-verified-2026-10-29.md`](official-sources-verified-2026-10-29.md)
- Hypothesis slate: [`knowledge/hypotheses-20261029.md`](hypotheses-20261029.md)
- Public-only board snapshot: [`docs/data/official-leaderboard.json`](../docs/data/official-leaderboard.json)

## 1. Starting state and hard blockers

The repository started with no tracked changes in this review. The checked-out requirements test baseline was **365 passed, 119 warnings**. The scientific/data preflight did not pass:

- `registry/template.json` has `method_lane: null` and no recorded canonical shared-template assignment. The missing method paragraph cannot be inferred from historical proposals.
- `python scripts/shared_tools.py preflight` exited 1. It reported immutable vendor pin mismatches for `vendor/gems57/submission_writer.py` and `vendor/gems57/uniqueness.py`, no lane, no canonical assignment, and missing `.cache` feature/input files. The tool says execution is unauthorized.
- `data/` had zero files and `.cache/` was absent. A safe `bash scripts/download_competition_data.sh --group core --verify-only` check exited 1 with `training_features.tif` missing. That wrapper calls the owner-mirror restorer, not an organizer downloader; no data was restored or authenticated.
- The DrivenData data page redirects to login. No organizer labels, features, sample, submission receipt, or private score were available.
- The 70%-within-3-px and rank-correlation thresholds remain the user's internal literal stop gate. A prior experiment's role/separation or selector wording is not an exemption. No surface or dot comparison was run because no new candidate exists.

## 2. Three-pass review

### Pass 1 — inspect, verify, and reproduce the safety defect

1. Read `AGENTS.md`, README, the reconstructed standing brief, prior current reviews/cards, registry and template pins, preflight code, download/restore scripts, renderer, tests, workflows, and the existing official-source register.
2. Ran the existing full suite before edits: **365 passed, 119 warnings**.
3. Reproduced the `scripts/prepare_data.py` defect in a temporary directory by redirecting `GEMS_DATA_DIR` and `GEMS_CACHE_DIR`. It printed `BLOCKED`, then continued into the legacy builder; it returned 1 only after a missing sample-submission error, and the temporary cache directory had already been created. No repository data or evidence was written by this reproduction.
4. Ran the mirror wrapper in verify-only mode; it blocked on missing `training_features.tif`. It was not run in download mode because that would restore third-party mirrors, not authenticated organizer inputs.
5. Re-ran local novelty searches. Do **not** call MT conductance, heat-flow residuals, or GeoDAWN K/Th alteration novel: those subjects appear in peer/project records, including GEMSDOE28/31 and GEMSDOE32. The new slate therefore makes only limited local-record novelty claims and explicitly disclaims fleet-wide novelty.
6. Rechecked official pages. The public board snapshot fetched 2026-10-29 shows #1 `xiaofanhu` at **0.4544**, #2 `cfld__` at 0.3916, #3 `Batik Shirt Brothers` at 0.3911, and 0.3195 at rank #47 (`kpomazi`); rank #50 is 0.3167. This corrects older user-reported rankings, but is neither a project score nor a file-linked submission receipt. The data tab remains login-walled.
7. Fetched the GDR INGENIOUS page and verified the public CC BY 4.0 listing includes spring/well aqueous geochemistry. The advertised well/spring ZIP returned HTTP 500; no schema or data bytes were obtained. Official USGS Water Data API documentation lists monitoring-location, daily, continuous, and field-measurement collections; no study-area coverage was queried. The organizer reference implementation documents CPU-only support; a GPU is optional acceleration, not a data-access prerequisite.

### Pass 2 — implement bounded safety and freshness improvements

1. Replaced the legacy private `scripts/prepare_data.py` work path with an unconditional, explicit quarantine exit. It now returns 2 before feature construction, canary execution, cache creation, or evidence writes; it explains that the owner-assigned shared template must be used after the lane/provenance gates are resolved.
2. Added `test_prepare_data_quarantine_returns_before_cache_or_canary_writes`, including an old `--force` invocation, temporary data/cache paths, and a before/after canary receipt comparison.
3. Added `scripts/refresh_official_leaderboard.py`. It reads only the public DrivenData leaderboard page; requires a recognizable rank/public-Tversky table, rank 1, unique ranks, at least three rows, and scores within [0,1]; then atomically replaces the JSON snapshot. Network, parser, or validation errors return nonzero and leave the prior snapshot untouched. It does not log in, inspect submissions, choose slots, or create receipts.
4. Added parser/atomic-preservation regressions, `docs/data/official-leaderboard.json` with the dated selected-rank snapshot, and `.github/workflows/official-leaderboard.yml` for a daily check. A changed validated feed is rebuilt/tested and committed only on `main`; manual dispatch on a feature branch is non-mutating. The checked-in snapshot is partial, and the raw live HTML parser has not yet been exercised against the external page; call the automation live-verified only after a successful Actions run.
5. Updated the renderer so the home-page public-board card reads the JSON snapshot, site footers link to this session's card rather than a stale historical run card, and current status/research text identifies this session and the three proposals. Updated README and the reconstructed standing brief with the active stop rules, missing-lane status, source-access limits, and the corrected dated board values.
6. Added [`knowledge/hypotheses-20261029.md`](hypotheses-20261029.md): three qualitative, untested candidates, each with layers/data, mechanism, non-fault mimics, off-catalogue rationale, difference from checked prior records, qualitative benefit/cost, obtainability and mandatory validation. The top-ranked H1 is not an assigned lane.
7. Added a fail-closed session JSON card. Candidate-specific fields are explicitly null/NOT_RUN because no raster or experiment exists.

### Pass 3 — adversarial recheck against scope and acceptance criteria

The final review checks that:

- The new data-preparation command cannot proceed even when `--force` is supplied; the regression confirms no configured data/cache directory or canary receipt is created.
- The public-board scraper only handles a public rank/score table and cannot silently convert a malformed page into a score; it has fixture tests and atomic-write failure coverage. Live endpoint compatibility remains unverified.
- The official public leaderboard is not mislabeled `ORGANIZER-CONFIRMED` under the file-linked-receipt rule; it is a dated public-board snapshot. Historical GEMSDOE scores remain `USER-REPORTED / UNVERIFIED`.
- No lane was invented; no vendored shared tool was edited or re-pinned; no experiment was run; no TIFF or holdout result was created; no slot was selected.
- The 3-proposal slate includes explicit confounders and external-data limitations; it does not claim broad novelty. Existing MT/heat-flow/K/Th themes are not represented as new.
- README and public pages distinguish current evidence from older session artifacts. The standing brief openly says it is reconstructed rather than verbatim.

## 3. Tests and build verification

**Before this session's edits:** 365 passed, 119 warnings (23.49 s). **After implementation:** 373 passed, 119 warnings (20.77 s). The deterministic site renderer produced 32 pages with no submission authorized. These results verify software behavior only; no geological performance is established.

The new focused regression run passed: **19 passed, 1 warning** across `tests/test_official_leaderboard.py` and `tests/test_quarantined_runners.py`.

## 4. Current sources and numerical claims

- Official DrivenData problem/metric page: [competition task and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), including α=0.2, β=0.8, triangular 300 m kernel, [0,1] scores, float32 GeoTIFF, EPSG:32611, and null/NaN outside the study area.
- Official public leaderboard: [live public page](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/); this repository snapshot is dated 2026-10-29 and partial. Public board values are not private/final scores or artifact-linked receipts.
- Official DOE/NLR [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf): three submissions per week, one final selection, and generative-AI disclosure. The exact live allowance is account-specific and was not queried.
- GDR [INGENIOUS compilation](https://gdr.openei.org/submissions/1391), DOI 10.15121/1881483, CC BY 4.0: listing verified; well/spring archive failed HTTP 500; no raw schema/coverage verified.
- USGS [Water Data API collections](https://api.waterdata.usgs.gov/ogcapi/v0/collections): official interface documentation verified; no footprint query performed.
- Official [DrivenData reference implementation](https://github.com/drivendataorg/gems-prize-reference-solution), pinned at `aebe92f7c8a990f0e3443451b7a825d9afd6336b`: CPU-only support documented; no organizer score or data payload was authenticated from it.

## 5. Deliverable / submission status

| Item | Status |
|---|---|
| Per-site historical executive summaries (GEMSDOE24/25/27/28/30/31/32/33/36) | Existing pages retained; each remains a historical research reference with user-reported values and explicit no-submit language. |
| Safe submission guide | Existing guide remains fail-closed; no approved file is exposed. |
| Three geological hypotheses | Added as proposals only; H1 ranked first on qualitative benefit/cost, not validated or assigned. |
| `prepare_data.py` no-write gate | Fixed and regression-tested. |
| Official public leaderboard freshness | Dated partial snapshot plus fail-closed daily workflow; live run still required. |
| New TIFF / holdout / registry uniqueness / portal acceptance | Not produced or tested. |
| PR and merge | Not completed at time of writing; current branch remains the only work branch. Update this row only with the actual PR/merge result. |

## 6. Remaining blockers and next steps

1. Owner supplies the exact method paragraph. Do not choose a historical proposal as a substitute.
2. Shared-template owner resolves the `submission_writer.py` and `uniqueness.py` pin mismatch and records the canonical assignment. Do not edit a private fork.
3. Obtain organizer-authenticated training features, labels, sample and registry bytes. The owner-mirror wrapper is not a substitute.
4. Only after steps 1–3: run the assigned shared preflight/evaluator/writer, obtain authoritative layer metadata, perform per-feature leakage canaries, and validate a pre-registered whole-segment buffered holdout with 95% CI.
5. Compare continuous surfaces to the complete registry before placement and final dots afterward. Apply the literal stop without jitter/rename/representation/witness exceptions. No slot selection is permitted here.
6. For the external ideas, first verify GDR well/spring schema/coverage or query actual USGS Water Data site/time-series coverage. Do not download or construct rasters from an unverified schema.
7. Run `.github/workflows/official-leaderboard.yml` on the branch or wait for the scheduled main run to verify the live parser. Do not label the feed automation live-tested until it succeeds.
8. After all gates, follow the ≤3 experiment / ≤2 hour budget; end any actual run with the full JSON card and keep organizer confirmation separate from HOLDOUT-DTI.
