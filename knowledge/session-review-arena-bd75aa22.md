# Repository review — `arena/bd75aa22-gemsdoekarage1` — 29 October 2026

## Decision

**NEGATIVE / DO NOT SUBMIT.** This review did not generate a TIF, run a geological experiment, estimate a competition score, select a weekly slot, or make an organizer submission. No new score is claimed. The existing `GEMSDOE32` 0.2778 and other site values remain user-reported/unverified unless paired with an organizer receipt. A local holdout value, if present in historical notes, is not a leaderboard estimate.

## Pass 1 — inspect and test

- Read `AGENTS.md`, `README.md`, `docs/standing-prompt.md`, the previous run card and review, the nine-site artifacts/pages, registry/template metadata, and current test tree.
- The authoritative lane assignment is absent: `registry/template.json` contains `"method_lane": null` and `"canonical_template_assignment": null`. Rule 1 of the provided parallel-run protocol forbids choosing a lane based on guesswork. No experiment was run.
- Required input data and cached feature stack are not present in the checkout (`data/` and `.cache/gems_work/feature_stack.npy` are absent). Data provenance is mirror-based in historical audits; those hashes do not prove organizer authenticity. DrivenData credentials are not available to this session.
- Registry comparisons are not complete/authenticated. Prior audits identify a dense-lattice witness that exceeds the literal 70%/3-pixel threshold for all audited champion-like dotted candidates. This is an internal protocol rule, not an official competition rule; it cannot be waived by silently treating the lattice as a different role.
- Existing writer/validator and research-runner tooling is guarded; previous reviews note vendor integrity mismatches and private-fork runners quarantined. No bypass or output was attempted.
- `python -m pytest -q` initially could not run because pytest was not installed. Created ignored `.venv/`, installed `requirements.txt`, and ran `.venv/bin/python -m pytest -q`: **365 passed, 0 failed, 0 skipped** (119 Rasterio/Affine pending-deprecation warnings). This is software verification only, not model performance.

## Pass 2 — adversarial review

1. **No arbitrary candidate invention.** The user asks for 3–5 previously untried hypotheses and an assigned single method paragraph. The prompt's lane paragraph is missing; the template explicitly has no assigned lane; previous parallel runs contain a broad hypothesis slate and competing experiments. Thus neither novelty nor a lane can be certified. Rewording the existing SBPF-PC/TRDS-Bridge/GD-MAD/3DEP-DFA slate as “new” would be misleading. Those remain prior proposals, not current-session candidates.
2. **No external-source availability claims.** This environment only permits outbound access to GitHub, codeload, api.github, npm, and PyPI hosts. DrivenData, USGS, NLR and GDR could not be independently fetched here. The existing official-source register is useful for manual review but is not a fresh verification receipt or proof that a named data package is presently obtainable.
3. **No score extrapolation.** Reported site scores and public leaderboard values are not artifacts/receipts in this review. A score cannot be inferred from a mask difference, software tests, a hypothesis, or a local validation pass.
4. **TIF must not be surfaced as approved.** Existing repository governance and audit records say prior publicly exposed candidate TIFs fail required uniqueness or other gates. This session did not recertify their saved bytes. No TIF download is labeled OK.
5. **Submission page and weekly cap.** Without a logged-in competition account, a live weekly allowance or portal acceptance cannot be checked. No selector action is made.

## Pass 3 — requirement recheck and handoff

- The requested scientific task cannot responsibly proceed until a lane and canonical shared template are explicitly assigned, authenticated competition inputs/cache are restored, and the complete registry/lattice interpretation is resolved by the protocol owner. Then preregister one candidate in the assigned lane and follow the shared holdout/writer, single-feature canary, surface-before-placement and final-dot checks; stop at three experiments or two hours.
- Keep the prior four-hypothesis table as **proposal-only and not newly established**. If its leading SBPF-PC proposal is eventually selected by the owner, obtain official source/data integrity evidence before claiming its layers/coverage are usable. No external-data-dependent candidate is called viable on the basis of inaccessible sources.
- The 0.2778 forensic argument in the existing README/session analysis is conditional: B2's audited mask is consistent with thinning the d2.8 parent around the mirrored known-fault mask. If the reported scores are correct, thinning may have traded off weak-utility near-catalogue predictions against recall, but mask algebra alone does not establish the hidden-label causal mechanism. Beating it is possible in principle, not demonstrated or numerically estimable.
- No pull-request or main-branch merge is performed automatically from this review-only change unless there are actual tracked changes; this review adds only this session record and a JSON card, not a new submission or model claim.

## Blockers / next actions

1. Supply the exact assigned method paragraph and name the canonical template/toolchain owner.
2. Restore organizer-authenticated feature, label, existing-fault, and sample-submission data; compare hashes/provenance with public mirrors.
3. Resolve the literal 70%/3-pixel lattice stop with the protocol owner, without evasion; provide a complete, immutable registry inventory.
4. Reconcile vendored tool integrity against the assigned shared template; do not maintain a private evaluator/writer fork.
5. Only after 1–4, run the single-feature leakage canary and spatially blocked buffered whole-segment holdout. Report HOLDOUT-DTI with evaluator version, withheld-positive count, and 95% CI. No score projection.
6. Validate final saved GeoTIFF bytes against the official sample template, [0,1] range, footprint encoding, CRS/shape/transform, registry gates, and hash. The previous portal error's exact causal artifact remains unidentified.
7. Ask the separate selector to check live weekly quota only after every experiment and validation gate passes.

## Official references retained for review (not freshly fetched in this session)

- Competition overview and submission format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition data tab (login required): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- Organizer reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- GDR INGENIOUS submission: https://gdr.openei.org/submissions/1391
- NLR rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf

These links are source leads only in this review. No access, current payload, or score receipt is asserted.
