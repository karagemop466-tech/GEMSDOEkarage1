# Repository review — 2026-10-28, fafb84ff

## Outcome

**NEGATIVE / DO NOT SUBMIT.** No new TIFF, score estimate, slot selection or upload. The current prompt does not identify its promised single method paragraph; `registry/template.json` has `method_lane: null` and says the canonical template is unresolved. Current [preflight](../evidence/preflight-fafb84ff.json) also finds all five required shared-cache inputs missing. This is independent of prior sessions' ignored mirror downloads: those are not present shared inputs here. No private stack was rebuilt and no evaluator was forked.

## Pass 1 — inspect and implement

Read the repository instructions and prior review material. Existing nine-site summaries and research slate remain available in [the executive summary](../docs/executive-summary.html) and [research review](research-review.md). The slate contains four qualified hypotheses, not proven fleet-wide novelty, assigned lanes or measured improvements. Do not relabel historical claims as organizer-confirmed scores. The supplied leaderboard figures conflict and were not independently verified here.

Fixed a concrete preflight gap: zero-byte files previously passed the input-presence check. The shared-tool adapter now reports `empty` paths, fails readiness and refuses execution before bootstrap. This is an orchestration fix, not a change to the shared evaluator or writer. Nonempty arbitrary bytes still pass this limited presence gate; it is expressly not a format, provenance or scientific validator.

The first test attempt found no pytest installed. System pip correctly refused an externally managed environment; created an ignored `.venv` instead and installed test dependencies. A collection error identified missing lightgbm; after installation, the complete suite passed.

## Pass 2 — adversarial review

Added one regression for each of the five required inputs, asserting both negative readiness and no bootstrap/execution for empty bytes. Updated existing synthetic fixtures to use nonempty placeholders without pretending they are valid data. Targeted preflight tests: **16 passed**. Full suite: **245 passed**, with 90 Rasterio pending-deprecation warnings. Missing inputs and invalid lanes remain blocked; output is not submission authorization.

## Pass 3 — requirements and reproducibility

Rebuilt all 32 decision pages: no committed page changes, no submission authorized. `git diff --check` passed. The organizer reference repository was reachable through the GitHub API and reports default branch `main`; this checks repository availability, not the competition portal, latest rules, eligibility, licenses or data provenance. No official-source geological claim was newly verified. Sources outside the permitted GitHub/Python/npm hosts cannot be directly retrieved with the sandbox network policy. Existing official links are review pointers, not claims of fresh verification:

- [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Official problem and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official prize rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

The B2 geometry explanation is already in the research review: audited mirror support equals d2.8 minus a known-fault collar. That is not proof of causal leaderboard gain or a basis for forecasting a new score. Historical saved-byte lattice failures remain negative; this session did not rerun their raster audits. No experimental number, CI, hash or validator result is invented for a nonexistent candidate. Zero geological experiments consumed the budget.

## Next work and limitations

1. Establish the assigned lane and canonical shared template; preserve the literal lattice stop rule unless explicitly revised. This cannot be inferred from an unspecified paragraph.
2. Restore and authenticate official inputs into the canonical cache, including feature schema, units, footprint and fold assignment. Owner-mirror hashes alone do not establish organizer origin.
3. Establish the complete registry and same-evaluator holdout baseline. Run feature canaries, fold-local catalogue features, buffered segment recovery and pre-placement checks before writing a candidate.
4. Only promote measured improvements that pass every saved-byte gate; a separate selector checks the current weekly cap. No automatic competition upload is implemented or authorized.

The README's stored standing prompt is explicitly reconstructed rather than a verbatim transcript. This review does not claim to have completed the requested unique TIFF or established a new high score. The current site already makes the negative outcome prominent; adding a download button for a failed candidate would misrepresent its eligibility.
