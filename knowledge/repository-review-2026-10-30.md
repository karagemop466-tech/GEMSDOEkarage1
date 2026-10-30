# Repository review — 2026-10-30

## Scope and method

Three review passes were completed against the checked-out `arena/f4437f72-gemsdoekarage1` tree. Pass 1 mapped the documented entry points, evidence/run cards, validators, release gate, registry assets, and generated Pages. Pass 2 checked cross-file consistency and attempted the test suite. Pass 3 confirmed the review conclusions against current files and recorded limits. No candidate raster was generated and no competition slot was used.

## Findings (highest severity first)

### High — user-facing executive summary is stale and internally inconsistent

`docs/executive-summary.html` still presents `arena/fb1e3550` as its session status (the page text labels itself reviewed 28 Oct), while the README and `knowledge/session-review-arena-5ee7ef4b.md` document a later 29 Oct session. That later record tests H-S1 and gives a different candidate status and holdout results. Consequently the prominent page must not be treated as a current release decision; a user landing on it may see obsolete claims. Regenerate the page from the current evidence source before presenting it as current, and add a test that the rendered session ID/date matches the latest run card.

Evidence: `docs/executive-summary.html`; `README.md`; `knowledge/session-review-arena-5ee7ef4b.md`; `evidence/session_5ee7ef4b_run_card.json`.

### High — prescribed literal 70% / 3-pixel gate is non-discriminating on the supplied lattice

The committed diagnostic reports that 99.8713% of the competition footprint is within 3 px of the lattice witness, and 200/200 random placements at each tested count fail the 70% rule. This gate cannot distinguish a scientifically derived submission from random placement in this setup. The gate is part of the session protocol, not competition rules; do not quietly claim a candidate is cleared if the protocol remains literal. It needs a transparent owner/policy decision or an alternative preregistered duplicate metric with a null model, before any candidate can receive a positive verdict.

Evidence: `evidence/lattice_gate_null_check_20261029.json`; source implementation `scripts/release_gate.py`.

### High — no defensible estimate of organizer leaderboard score

The repo correctly labels historical scores as user-reported/unverified and states that holdout DTI measures recovery of mapped catalogue faults, not the competition's hidden off-catalogue target. The session's own control shows that the champion raster is near zero on that holdout while random placement is much higher, exposing a target mismatch. Do not call an internal holdout value a projected leaderboard score or promise that any file beats 0.2778/0.3195. An organizer receipt or a defensible independent truth set is required.

Evidence: `evidence/session_5ee7ef4b_run_card.json`; `knowledge/session-review-arena-5ee7ef4b.md`; `evidence/nine_site_executive_20261029.json`.

### Medium — user standing prompt is explicitly a reconstruction, not a verbatim prompt

`docs/standing-prompt.md` expressly says the original prompt was not preserved verbatim. That conflicts with the request to keep the full prompt in README and makes the record unsuitable as an exact user-instruction transcript. Do not represent it as verbatim; next maintenance should preserve an actual supplied prompt snapshot and make README link it as the required session-start checklist.

Evidence: first paragraph of `docs/standing-prompt.md` and the README's repeated “read first” instructions.

### Medium — no test result can be claimed for this checkout environment

`python -m compileall -q scripts src tests vendor` succeeded. `pytest` was absent from the system interpreter. A repository-local ignored virtual environment was created and pytest installed, but collection stopped with 24 import errors because NumPy is not installed. Thus the suite was not executed; these are environment/dependency collection failures, not demonstrated test failures in project logic. Install the declared requirements in a suitable environment and rerun the full suite before merging code changes.

Evidence: direct commands run during this review; `requirements.txt` and `pyproject.toml` declare NumPy and geospatial/scientific dependencies.

### Medium — focus-site table establishes pinned-subset comparison, not global uniqueness

The reports correctly limit comparisons to pinned local raster files and say the wider registry is incomplete. Therefore “unique” can only mean unique within that enumerated inventory. It cannot prove uniqueness against every site/submission mentioned in the user's long list. Keep that scope visible in any download/status table.

Evidence: `evidence/nine_site_executive_20261029.json`, `registry/` and corresponding scope notes.

## What is working well

- Fail-closed release validation distinguishes validation from selection/authorization (`scripts/release_gate.py`, `scripts/validate_geotiff.py`).
- Evidence uses explicit labels for holdout versus user-reported scores and preserves negative decisions.
- New files are not automatically treated as submit-ready; local format validation does not claim portal acceptance.
- Prior bad/unsupported artifacts and runners have quarantine conventions and regression tests.
- The build is syntactically valid across scripts, sources, tests, and vendor code (`compileall` passed).

## Three-pass conclusion

1. **Pass 1:** reviewed project architecture and current evidence; confirmed no newly justified candidate or score estimate.
2. **Pass 2:** identified stale top-level page, non-informative duplicate gate, holdout/leaderboard target mismatch, non-verbatim prompt caveat, and inability to collect tests without dependencies.
3. **Pass 3:** rechecked the cited evidence and source files. No scientifically valid or policy-cleared TIF can be recommended from this checkout. Verdict: **NEGATIVE — DO NOT SUBMIT a repository artifact based on this review.**

## Recommended next actions

1. Regenerate executive summary and index from a single current run-card/evidence source; enforce freshness with tests.
2. Obtain a documented owner decision on the 70% lattice gate. Preserve its null-model failure and do not weaken it silently.
3. Fix the target mismatch in the shared evaluator only with an organizer-justified truth/validation design; do not use mapped catalogue recovery as a proxy for hidden-fault DTI without qualification.
4. Restore authenticated competition input files if possible; current mirrors do not establish organizer provenance. Preserve hashes and provenance.
5. Run tests in a provisioned Python environment (`pip install -r requirements.txt` plus the test runner) and record the complete result.
6. Only then test preregistered hypotheses within the three-experiment/two-hour cap, and only generate an upload candidate after all scientific, registry, saved-byte, and independent selector gates pass.
7. Archive the exact user-provided standing prompt as an unmodified source snapshot, then reference it from README; clearly distinguish exact source from any concise checklist.

## Limitations

This review did not access DrivenData authentication, private labels, or an organizer submission receipt; did not fetch/verify remote current pages; did not rerun the numerical holdout; and did not regenerate static pages. The checked-in evidence describes prior sessions and must not be interpreted as a live leaderboard or portal confirmation.
