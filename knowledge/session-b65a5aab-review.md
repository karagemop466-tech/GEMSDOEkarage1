# Session b65a5aab — 28 October 2026

## Outcome

**Negative; DO NOT SUBMIT.** No new method paragraph was supplied, and no new
prediction, geological experiment, holdout measurement, or slot selection was
made. The goal of a new high-performing TIFF remains unmet. The existing nine-site
executive summaries and ranked four-hypothesis research slate remain planning
and historical evidence, not an approved candidate or a forecast.

## Pass 1 — restore and review

Read README, AGENTS, the standing brief and prior handoffs first. Restored all
31 files in `registry/karage1_data_manifest.json` to `.cache/gems_data`, using the
existing restorer. Every file met its manifest size and SHA-256. These are peer
mirrors, not organizer-authenticated files. The shared feature cache remains
absent; do not rebuild a private feature stack to evade Rule 2.

Inspected the organizer's public reference repository through GitHub:
https://github.com/drivendataorg/gems-prize-reference-solution . The README blob
`a8814f99c395d12a8e1c3731c738e61d7dca06b5` supports CPU training as well as GPU;
therefore the user's inherited claim that a GPU is strictly required is not
supported by that source. The notebook blob
`d45bf7bdb1d31a22caa38371ad195c2f6eb965ae`, cell 5, records a 19-band float32
3730-row by 3292-column EPSG:32611 grid with 100 m pixels. Cell 6 records int32
labels with nodata -1. The peer label mirror here is **int8**, not int32: matching
geometry and description does not authenticate the mirror's bytes. Cell 5's
Band 6 description is ambiguous ('Tilt angle or total curvature'); the mirror
has values approximately +2.95 to +88.57. Do not claim it is a signed tilt angle
in radians without authoritative units. Band 18 is signed in the mirror.
These diagnostics are not geological evidence or score estimates.

Listed current GitHub trees for the nine focus repositories and found the
21 historical submission names supplied for those sites (including later
low-reported-result variants). This only establishes published file paths, not
scores, novelty or organizer receipts. A raw-file download via a GitHub redirect
failed with TLS EOF; no complete new 21-file byte comparison was performed.
The existing hash-pinned nine-reference audit remains the scope of published
comparisons. No live leaderboard or submission quota was authenticated here.

## Pass 2 — integrity defect and fix

The inherited `vendor/README.md` claims unchanged 57GEMSDOE source, while
`vendor/PROVENANCE.json` names GEMSDOE31 and `registry/template.json` names
GEMSDOE32. A read-only audit additionally finds **two file-pin mismatches**:
`vendor/gems57/submission_writer.py` and `vendor/gems57/uniqueness.py`. Preserve
both the manifest and source bytes rather than rewriting hashes to make them
look pristine. No vendor source was edited in this session.

Added `scripts/audit_template_integrity.py` with exact SHA-256 checks, safe-path
handling, explicit source-pin conflict reporting and no inferred authorization.
The diagnostic CLI exits nonzero when blocked; the JSON receipt is
`evidence/template_integrity_20261028.json`. `shared_tools.py` now reports this
state and refuses evaluator/writer execution even if lane/cache are later
populated. This is a local execution interlock, **not an upstream repair**.
The canonical shared template still needs agreement and repair in its owner
repository once, for every parallel lane. Added synthetic regression tests for
missing/changed files, traversal paths, missing manifests, and blocked tools.

Open PRs #19 and #20 advertise additional promoted candidates on other session
branches. Their descriptions are not validation evidence and were not merged or
endorsed. Concurrent main-branch reviews subsequently audited those candidates
and recorded duplicate lattice witnesses; those reviews were integrated without
approving either artifact. This session edits only its assigned branch.

## Pass 3 — request reconciliation

- Preserve the literal duplicate stop, no approved-download badge, and separate
  weekly selector. No fabricated TIFF, score projection or organizer receipt.
- Publish the new provenance warning in the main decision panel and all
  generated executive-summary aliases; preserve historical research downloads.
- Run the complete test suite, deterministic site build, link/fragment tests,
  integrity receipt replay and `git diff --check` before the PR.
- New scientific validation cannot start until a lane, authoritative shared
  cache/tools, authenticated grid, complete registry and comparable frozen
  holdout best are established. Do not solve the dense-lattice conflict by
  exemptions or lattice-avoiding dot placement.

## Next actionable work

Resolve the canonical shared-template assignment and source discrepancies,
including units/band semantics and whole-component buffered splits; repair it
upstream rather than forking locally. Authenticate organizer data and the full
registry. Then run the highest-ranked lane-compatible hypothesis within the
three-experiment/two-hour cap, requiring paired holdout improvement before a
separate slot selector. Until then, the submission decision is automatically
negative, not a request for a human inspector to approve an unsafe file.

## Final verification and integration

Replayed the full nine-reference plus lattice audit using the existing fetcher
and independently reopened both saved candidate TIFFs. The resulting audit is
identical to `evidence/candidate_audit_20261028.json` after excluding its run
timestamp: HMAS 38,174/38,200 and GPC-Z 35,959/36,000 within 3 px of the lattice.
This is a disqualifying witness, not registry completeness or a new score.

Integrated concurrent main changes through `e297b7e` on this session branch,
preserving catalogue-input checks, nonzero blocked-preflight exit status,
parallel candidate audits and stricter release/format validation. Extended the
new provenance interlock with a regression proving valid lane plus present
inputs cannot bypass missing authorization. After integration: **249 tests
passed**, 90 rasterio pending-deprecation warnings, no skipped tests. The
deterministic renderer rebuilt 32 pages; link/fragment and repeat-build checks
passed in that suite. `git diff --check` passed. No new vendor code was changed.

GitHub Pages is already enabled from `main` at `/` according to the repository
Pages API. Its public URL is https://karagemop466-tech.github.io/GEMSDOEkarage1/ .
A successful merge is not itself proof that the asynchronous Pages build has
finished. The current authenticated submission allowance is still unknown.
