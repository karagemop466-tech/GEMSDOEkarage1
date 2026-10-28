# Independent review — 28 October 2026, session 0404f8f1

**Decision: DO NOT SUBMIT.** No new TIFF, holdout score, leaderboard estimate,
competition upload, or slot selection was produced. The protocol's single
method paragraph is not present in the request. The previously recorded
[ranked hypotheses](research-review.md) are planning ideas, not an assignment.
The known historical candidates have already failed the literal duplicate
rule; a different hash or a format-only pass cannot clear them.

## Pass 1: review, reproduce and implement

- Reviewed the starting instructions, reconstructed standing brief, prior
  reviews, site, source ledger, shared wrappers, and release gates. Verified
  that the initial checkout had neither the cached stack nor the input rasters
  required by `scripts/shared_tools.py preflight`.
- Re-ran the [pinned parallel-candidate audit](../scripts/audit_parallel_candidates.py)
  with `--fetch`, reproducing the [committed output](../evidence/session_0404f8f1_parallel_audit.json)
  exactly. TD-KSCK has 37,584 of 37,654 dots and CTWS-2D 37,999 of 38,200 dots
  within a 3-pixel Euclidean disk of the lattice. The threshold is strictly
  greater than 70%. This is one mirrored witness on a mirrored footprint, not
  proof of complete registry coverage, official provenance, or holdout quality.
- The [proposed template pin](../registry/template.json) explicitly says its
  canonical status is unresolved, but the prior preflight checked only lane and
  file presence. Added a fail-closed `canonical_template_assignment` record
  whose lane, repository and immutable commit must match the configured pin,
  and whose evidence field must be nonblank. The current record is null. The
  presence of an assignment is an assertion and **does not authenticate it**;
  independent provenance and all release gates remain necessary.

## Pass 2: adversarial review

- Synthetic regression cases check missing, malformed, and mismatched
  assignments, invalid repo/commit syntax, both blocked execution commands,
  and successful dispatch under a test-only recorded assignment. Even a
  successful preflight does not approve a submission or test data content.
- Inspected the [organizer reference README at its pinned commit](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md):
  it instructs users to obtain competition data and documents both CPU and GPU
  options. The user-supplied claim that a GPU is always required is not
  supported by this reference. A mirrored data hash does not prove it is the
  official data, and `download_competition_data.sh` restores third-party
  mirrors rather than downloading directly from DrivenData.
- Direct network requests to DrivenData and USGS failed from this restricted
  runtime; no current leaderboard, live submission limits, portal encoding, or
  official data availability was independently checked here. We cannot infer
  the cause of the user's earlier range error.

## Pass 3: original requirements and reproducibility

- The existing [dashboard](../docs/index.html), [nine-site table](../docs/nine-sites.html),
  [executive summary](../docs/executive-summary.html) and
  [research slate](research-review.md) preserve the negative decision, link
  historical reference artifacts for research, and distinguish unverified
  user-reported figures from confirmed receipts. A leaderboard score cannot
  honestly be estimated from the evidence available here; no better-than-B2
  result is established. B2's historical thinning offers a plausible
  precision/coverage explanation, not proof of causality.
- `.venv/bin/python -m pytest -q`: 252 passed, 90 Rasterio warnings (synthetic
  software tests, not geological holdout validation). `python scripts/build_site.py`
  rendered 32 pages with no tracked page differences. `git diff --check` passed.
  Audit reproduction output is saved separately from the inherited evidence.
- [Current session run card](../evidence/session_0404f8f1_run_card.json)
  records nulls for measurements not performed. No hypothesis experiment was
  run, and no shared-template implementation was privately forked.

## Next actions and access

Establish a single parallel-run lane and authoritative shared template; obtain
and authenticate official competition data and the matching cached feature
stack; establish a complete immutable registry and a same-fold baseline;
resolve the dense-lattice stop and outside-footprint portal convention without
silently exempting witnesses. Then execute the required fold-visible canaries,
pre-placement comparison, buffered segment holdout and saved-byte audit. A
separate selector must decide whether to use a weekly slot. The known shared
comparator defect remains unresolved in its actual upstream template; a local
adapter is not a shared fix. A live feed is not yet published by the scheduled
artifact-only workflow. The standing brief is a reconstruction, not a verbatim
copy of the original prompt.
