# Standing brief — reconstructed from user instructions

**Provenance:** The original long prompt is not preserved verbatim in this checkout. This is a normalized working brief, not a transcript. Follow newer explicit user instructions first; do not silently invent missing details.

## Core values and score labels

- **Maximize P(Win); Own the Outcome.** Prefer reproducible, scientifically defensible work. Be candid about uncertainty, missing access, failed gates and irregularities. Do not hallucinate or conceal a negative result.
- Distinguish every score-like number:
  - `HOLDOUT-DTI`: include evaluator/version, withheld-positive count and 95% CI, plus the exact run-card/evidence source. It is a local blocked-holdout result, not an organizer score.
  - `ORGANIZER-CONFIRMED`: require an artifact-linked organizer receipt or authenticated organizer result.
  - `USER-REPORTED / UNVERIFIED` or `LEGACY-UNVERIFIED`: label unsupported claims explicitly. Never present a projection, estimate, user report, or stale snapshot as a score or current leaderboard value.
- If values conflict, preserve and explain the conflict; do not select one as current without an authenticated source. A passing local format check is not organizer acceptance.

## Project requirements

1. Review and improve this auditable DrivenData DOE GEMS project/site. The aspirational goal is a genuinely new, unique, valid, submit-ready single-band GeoTIFF that can outperform the historical reported GEMSDOE32 value. Do not promise that result, copy an earlier submission, or make a new raster unless every release gate passes.
2. Highest priority is a **unique** GeoTIFF. Make its approval status unmistakable. Historical files are for research/audit only. If no candidate is cleared, display **DO NOT SUBMIT**, do not offer an approved download, and say no file is authorized.
3. Provide a nine-site executive summary for GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36. For each, identify the strongest *reported* file available, correctly classify its score evidence, report the measured uniqueness scope (focus rasters and lattice; distinguish this from a complete registry), and say whether it is safe to submit. A separate submission guide may describe the future process but is not permission to upload a historical artifact.
4. Explain GEMSDOE32's reported `0.2778` at a scientific level. Separate direct geometry from causal performance explanations. Explain what is and is not inferable from the evidence and never infer a score from mask geometry.
5. Propose **3–5 new geological hypotheses**, ranked by qualitative expected holdout-DTI benefit and implementation cost—not numeric score projections. For every hypothesis specify layers, physical signature, off-catalogue rationale, named non-fault confounder, distinction from existing project methods, and specific official/free data sources with obtainability status. Screen against existing code and known sibling methods before calling an idea new. Validate the top candidate before any submission slot **only if** all assignments, provenance and protocol gates permit; otherwise record why it is blocked.
6. State the availability and provenance limitations. No competition data login, official source, live leaderboard, peer artifact or submission receipt is assumed authenticated unless it was actually verified. Provide trusted official links for manual review; a link is not proof that a payload was obtained.

## Binding parallel-run protocol

- Use only one **explicitly assigned method lane** and the canonical shared template/cache. Do not invent a lane, run a private feature/evaluation/writer fork, or treat a third-party mirror as organizer-authenticated.
- Before placement, compare the continuous candidate surface with every raster in the complete current registry; after placement, compare final dots. `|Spearman| > 0.90` **or** `>70%` of candidate dots within 3 pixels of any registry raster is a duplicate: save the comparison, log it, and stop. Do not jitter, rename, carve holes, alter thresholds, exempt a lattice, or use incomplete inventory to claim uniqueness.
- Reuse the shared evaluator and writer. Use whole-segment buffered hide/recover; derive catalogue features from **visible faults only**; enforce pixel-exact visible masks. Evaluate pooled DTI with α=0.2, β=0.8 and a 300 m triangular kernel. Test each feature alone; AUC >0.90 is leakage until resolved. Do not use holdout truth, static full-catalogue-pruned baselines, or hidden labels in inference.
- Maximum budget: **3 experiments or 2 hours**, whichever comes first. End every experiment with a complete JSON run card and explicit `promote` or `negative` verdict. Negative results are deliverables.
- Do **not** choose a submission slot. Selection and the live weekly cap are a separate step, available only after all gates pass.

## Saved-byte format validation

Autonomously reopen the exact saved GeoTIFF and check: one band; values inside `[0,1]`; no NaN, infinity, or masked/nodata cells inside the footprint; CRS, shape and affine transform exactly match the authoritative competition template; and explicit outside-footprint encoding diagnostics. Preserve the validator output, file SHA-256 and reference hash. Local validation is not portal acceptance; never label a file submit-ready on format checks alone.

## Required JSON run card

Record the hypothesis/mechanism, named non-fault mimic, lane and template assignment, data provenance, holdout DTI (or `null` with reason), evaluator, withheld-positive count and 95% CI when valid, per-feature canaries, pre-placement and final-dot registry correlation/overlap, raster SHA-256, saved-byte validator output, submission name/note (≤140 characters if relevant), separate slot status, limitations, and explicit promote/negative verdict. A legacy claim without a reproducible receipt must be quarantined rather than copied into a valid `HOLDOUT-DTI` field.

## Work/review and handoff

- Start with this brief, `README.md`, `AGENTS.md`, the current session review and the current audit receipts. Preserve historical evidence; do not rewrite a historical receipt to make it appear current.
- Run three passes: (1) implement and verify; (2) adversarial review and fix; (3) full requirements recheck. Run the relevant regression tests and the full test suite; report exact results and failures.
- Update the site and README with current status, evidence links, score conflicts, and limitations. Create a pull request from the active work branch and merge to `main` when authorized and checks permit. Provide a next-steps handoff. Never imply a merge, upload, organizer receipt, lane assignment or slot selection that did not occur.

## Current score-context warning (29 October 2026)

Prompt passages conflict on whether the live leaderboard value is `0.3195` or `0.4413`; repository material also contains an older `0.4544` snapshot. None was authenticated against a live organizer source in this review. Treat all three as conflicting, stale or user-reported context—not current organizer-confirmed scores. GEMSDOE32 `0.2778` is likewise `USER-REPORTED / UNVERIFIED` unless an artifact-linked organizer receipt is later obtained.

## Official source routes referenced in the repository

- DrivenData competition and metric: <https://www.drivendata.org/competitions/306/competition-doe-gems/>.
- Organizer reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>.
- DOE/NLR rules: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>.
- USGS GeoDAWN (magnetic/radiometric): <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and>.
- GDR INGENIOUS: <https://gdr.openei.org/submissions/1391>.
- USGS 3DEP: <https://www.usgs.gov/3d-elevation-program>.
- USGS 3D Hydrography Program: <https://www.usgs.gov/national-hydrography/3d-hydrography-program>.
- USGS ComCat FDSN event endpoint: <https://earthquake.usgs.gov/fdsnws/event/1/>.
- NASA / ASF DAAC: <https://asf.alaska.edu/>.

These are official provider links, not evidence that any particular data payload, account, tile, receipt or current leaderboard value was fetched or authenticated.
