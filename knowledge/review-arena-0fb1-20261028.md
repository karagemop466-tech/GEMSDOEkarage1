# Session review — 28 October 2026, `arena/0fb1ec81-gemsdoekarage1`

## Decision

**Negative — no new submission-ready TIFF.** No method paragraph is identified
as the lane in the current request, and the prior two candidate rasters are
already duplicate witnesses under the literal rule. The protocol requires stop,
not a switch to one of the speculative hypotheses. Zero geological experiments,
new prediction rasters, slot selections or uploads were made. See the
[session run card](../evidence/run_card_arena_0fb1_20261028.json).

## Pass 1 — reproduce prior findings and acquire inputs

* Restored and SHA-256/size checked all 31 manifest entries into ignored `data/`
  from immutable GitHub pins. This establishes mirror identity, **not** official
  origin, authorization, current licensing, completeness or portal compatibility.
  These ignored local files may not persist in another session. The official
  [competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
  and [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
  remain independent source pointers; this environment's outbound host policy
  prevents fetching those official sources directly. The prior source register
  includes earlier checks, which were not repeated here.
* Replayed [the reassessment](../evidence/reassessment_arena_0fb1_20261028.json)
  using independently pinned B2, labels, sample, lattice and parent. Replay from
  a second copy of the B2 bytes produced identical JSON. The mirrored sample is
  **not** authenticated as the organizer's grid or footprint.
* Historic HMAS has 38,174/38,200 dots within 3 px of the lattice; GPC-Z has
  35,959/36,000. Their pre-placement surfaces and complete registry remain
  unavailable. The same computation found B2 is the audited d2.8 mask minus
  6,436 pixels within 2 px of mirrored known faults, adding none. Causation and
  leaderboard improvement are not established. The 0.2778 user-reported value
  has no artifact-linked organizer receipt in this checkout. Neither it nor a
  holdout should be treated as a forecast for a new submission.
* `scripts/prepare_data.py` explicitly stops: the old private 58-channel stack
  is quarantined and is not the assigned shared feature cache. Shared preflight
  reports no lane and a missing cache. No training was attempted.

## Pass 2 — correctness and safety

* The format diagnostic previously allowed `--out` to name the candidate or
  template, replacing TIFF bytes with JSON. It now blocks direct paths, resolved
  symlink aliases and existing hard links, and uses unique atomic staging.
  Tests check input bytes remain unchanged. It still makes no upload decision.
* The release policy previously did not compare its validator section with the
  candidate digest. It now requires a matching `validator.candidate_sha256`.
  This is a **consistency check on assertions**, not independent proof that the
  validator ran, that a registry is complete, or that a template is official.
  Historical gate output was regenerated to record the new negative reason.
* B2's manifest record had no selectable ID, making `--id` fail despite a valid
  entry. It now has `scored_gems32_b2` in the scored group, without changing the
  pinned source or bytes. Added regression coverage for all changes.

## Pass 3 — recheck and limitations

* Final test suite: **212 passed**; 53 Rasterio pending-deprecation warnings.
  After the gate change, the first full pass exposed stale regenerated historical
  gate receipts; reconciling them and rerunning made the suite pass. The saved
  byte audit replay matched exactly. Deterministic page build generated 32 pages
  without altering committed site output; `git diff --check` passed. After merging
  concurrent main-branch changes into this working branch and resolving README
  and AGENTS conflicts, the combined suite passed **228 tests** with 62 Rasterio
  pending-deprecation warnings; the site build remained unchanged.
* The nine-site summaries, named files, reported (unverified) numbers, negative
  verdict, B2 discussion and four qualified research proposals already exist in
  [the dashboard](../docs/index.html) and [research review](research-review.md).
  They do not identify any safe file to submit, nor can they estimate a reliable
  organizer score. The leaderboard snapshots in earlier records are dated; this
  session did not independently query the organizer leaderboard. The user prompt
  itself contains conflicting leaderboard figures.
* The scheduled GitHub workflow produces a retained refresh artifact; it does
  **not** automatically publish a current verified Pages feed. The renderer uses
  pinned earlier evidence. Do not describe it as live. The shared comparator's
  nonfinite-reference/completeness concerns and canonical upstream identity are
  documented in [the previous review](three-pass-review-2026-10-28.md); no
  shared-template fix was made here and no private fork was introduced.
* The repository's [standing prompt](../docs/standing-prompt.md) is a marked
  reconstruction, not a verbatim copy of all current user messages. Use the actual
  current request alongside it. [Official format and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
  and [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
  are review links; this session checked GitHub access but did not re-fetch the
  DrivenData page. A prior `[0,1]` rejection cannot be diagnosed without the exact
  rejected file and organizer response; outside-footprint handling remains open.

## Next actions

1. Resolve the missing assigned lane and whether the literal registry rule applies
   to the dense lattice; do not quietly exclude it. Identify the canonical shared
   template and repair shared comparator issues at the source, if authorized.
2. Authenticate an organizer sample, labels and feature stack against the mirrored
   bytes; establish a complete pinned registry, permitted data licenses and an
   independently reproducible same-evaluator holdout baseline. Use the original
   template's buffered whole-segment folds and fold-local catalogue features.
3. Run per-feature canaries and pre-placement/final registry checks before any
   geological experiment is promoted. Only a separate selector may consider a
   weekly slot after verifying all gates and current organizer rules. Require an
   artifact-linked receipt after any submission. Implement a permission-compliant,
   provenance-stamped feed if current information can legally be obtained.
