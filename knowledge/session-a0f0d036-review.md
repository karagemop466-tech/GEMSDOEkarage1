# Follow-up review — 28 October 2026

## Decision

**DO NOT SUBMIT. No new TIFF was generated and no weekly slot was used.**
This session retained the existing nine-site executive summaries rather than
relabeling historical artifacts as new. Their scores remain user/owner reports,
not organizer-confirmed receipts. A new leaderboard score estimate is unavailable.

## Three verification passes

1. Read the standing requirements, previous review, research proposals, active
   run card, shared adapter and release gate. The prompt still omits the assigned
   single-method paragraph. The current checkout has neither the shared feature
   cache nor a comparable frozen holdout best. Existing duplicate witnesses remain
   disqualifying; no experiment was started.
2. Fixed an automation defect in `scripts/shared_tools.py`: preflight previously
   returned success with absent inputs. It now returns exit 1 when blocked,
   rejects whitespace/non-string lanes, and requires the visible fault catalogue
   as well as labels, sample, numerical features and cached stack. Evaluation and
   writing stop before bootstrap when blocked. This changes the local invocation
   adapter only, not the shared scientific evaluator or writer. Presence checks
   deliberately do not claim hash authentication or scientific validation.
3. Added regression tests for invalid lanes, missing catalogue, CLI exit status,
   and no bootstrap on blocked evaluate/write. Full suite: **216 passed**, with
   53 rasterio pending-deprecation warnings. Re-ran both preflight commands:
   each exited 1 and reported negative/not ready. No score was measured.

## Research and sources

The four ranked proposals and their confounders remain in
[research-review.md](research-review.md). They are untested proposals, not a
license to choose an unassigned parallel lane. Source-check history is retained
in [sources-2026-10-28.md](sources-2026-10-28.md); this session did not freshly
verify those external pages. Outbound network access is restricted to GitHub,
npm and PyPI hosts, preventing direct official USGS, GDR, NLR, Dropbox and
DrivenData payload retrieval here. GitHub mirror identity is not organizer
authentication. The user-supplied leaderboard benchmarks conflict and cannot be
resolved from this environment; none is used as a score estimate.

## Next actions in order

- Supply an assigned lane and authoritative upstream template/cache identity.
- Resolve the dense-lattice overlap restriction explicitly; do not silently
  exempt its raster. The existing audit gives a necessary budget bound, not a
  scientifically useful candidate.
- Restore pinned inputs when a permitted experiment becomes possible; authenticate
  organizer sample/grid and confirm complete registry membership.
- Establish whole-segment buffered folds and frozen baseline, then test each
  feature alone before at most three experiments. Only measured improvement
  and all novelty/format gates permit scientific promotion; selector remains
  separate. Do not spend a slot to discover a format or leakage failure.

Session run card: `evidence/session_a0f0d036_run_card.json` (negative, no raster).
The active historical audit card is unchanged because it describes saved bytes,
whereas this session's card describes a blocked new experiment.
