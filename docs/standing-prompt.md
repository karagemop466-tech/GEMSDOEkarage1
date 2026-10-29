# Standing brief (the user's prompt) — read at the start of every session

**Provenance note:** the original prompt was not preserved verbatim in the workspace. What follows is a reconstruction from earlier session memory, not proof that every original clause or exact word was retained. Apply these requirements together with any newer explicit user instructions; do not claim this is an original transcript.

## Controlling addendum from the latest user direction (29 October 2026)

Where an older item below conflicts with this addendum, this addendum controls. The original full prompt is reconstructed, not a verbatim transcript.

- Keep **Maximize P(Win)** and **Own the Outcome**. Report negative results, blockers, uncertainty, and irregularities; never invent score projections.
- Do not copy any prior submission. Any generated TIFF must be unique under the literal registry rule and must clearly say whether it is safe to download and submit. No human-inspector fallback.
- Stay in one assigned lane. Before placement, compare the continuous surface and final dots with the complete authorized registry; stop/log when absolute Spearman exceeds 0.90 or more than 70% of candidate dots lie within 3 px. Do not exempt the lattice or evade either threshold.
- Reuse the assigned template's cached feature stack, `evaluate_holdout.py`, and `submission_writer.py`. Fix shared tools in their owning template, not in a private fork.
- The whole-segment buffered hide-and-recover holdout must derive catalogue features from visible faults only, mask visible faults pixel-exactly, and report pooled DTI with α=0.2, β=0.8, and a 300 m triangular kernel. A valid score needs the evaluator, withheld-positive count, and 95% CI; organizer results require a receipt. An incomplete or unverified legacy scalar is not a score.
- Run a single-feature leakage canary; AUC >0.90 is leakage until disproved. Stop after three experiments or two hours. Do not select or spend a weekly slot; selector and cap are separate.
- Before implementation, propose and rank 3–5 geological hypotheses. For each, name relevant layers, physical signature, off-catalogue rationale, named non-fault mimic, difference from repository methods, qualitative expected DTI potential, cost, and official/free data source. If required external data cannot be verified as obtainable, mark the idea not viable—not data-ready. Validate the top candidate on the authorized blocked holdout when prerequisites exist.
- End with a JSON run card for the actual audited or generated artifact: hypothesis, mechanism, named mimic, HOLDOUT-DTI and CI or explicit not-run nulls, registry correlation/overlap, SHA-256, validator results, submission name and note ≤140 characters, and promote/negative verdict.
- Explain the reported GEMSDOE32 B2 result from saved-mask evidence, but label any user-provided value **USER-REPORTED / UNVERIFIED** and do not present it as a validated HOLDOUT-DTI or organizer score without the required evidence.
- Keep a clean GitHub Pages site for the nine focus sites, explain the [0,1] rejection with automated validation, and keep download-versus-submit status unmistakable. Read README and this brief at session start.
- Perform three implementation/review/recheck passes, verify tests/build/links, create a PR and merge it to `main` only if the environment and gates allow, and list remaining blockers/next work. Do not run a holdout, generate a TIFF, choose a slot, or upload while lane/template authorization or shared data are missing.

## Arena Core Values (keep as focus)

- **Maximize P(Win).** Favor reproducible evidence that can raise the probability of a higher organizer-confirmed score. The prior GEMSDOE32 0.2778 is user-reported, without a verified receipt here; the owner cited multiple leaderboard benchmarks that may be stale.
- **Own the Outcome.** Negative results, blocked data, and unprovable claims are reported as such; nothing is projected as a score; irregularities are flagged for review, not hidden.

## Requirements

1. Build a project in this repository for the DrivenData DOE GEMS competition (https://www.drivendata.org/competitions/306/competition-doe-gems/) that generates a **unique, valid, submit-ready single-band GeoTIFF** (values in [0, 1]; CRS/shape/geotransform identical to the submission format, EPSG:32611) that scores higher than the previous GEMSDOE best 0.2778 and ideally above the leaderboard top.
2. **Highest urgency: a UNIQUE TIF.** Previous submissions (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36 and the wider GEMSDOE series) may be used for learning only — never copied. It must be **obvious** whether a TIF is OK to download and submit.
3. The site must show, at the very top, the download link and the OK / NOT-OK-to-submit status. An executive summary with a table for each of the nine focus sites (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36): which file to download, the estimated score, and whether it is unique versus all listed GEMSDOE submissions. A subpage must explain exactly how to submit: the file, a unique name, and a short note (≤140 characters).
4. Every score number must be labelled **HOLDOUT-DTI** (with evaluator version, number of withheld positives, 95% CI) or **ORGANIZER-CONFIRMED**. A projection is never written as a score.
5. Validation must be done autonomously by the project (no human inspector / manual step); irregularities are flagged for review. The validator must guarantee values in [0, 1] and no NaN inside the footprint — an earlier submission was rejected with "Predicted values must be in range [0, 1]".
6. Give a PhD-level explanation of why and how `h33-h33-2-b2` scored 0.2778 and whether it can be beaten; use that understanding to generate the unique TIF.
7. Propose 3–5 **new geological hypotheses** (layers used, physical signature, why the targeted faults are off-catalogue, how it differs from existing submissions), ranked by expected DTI gain and cost. Validate the top candidate on a **spatially-blocked hide-and-recover holdout** before any submission slot is used. If external data are needed, name specific free official sources and check obtainability (only free, publicly available, official/verified data).
8. Follow the **PARALLEL-RUN PROTOCOL**: stay in your lane; duplicate check against the registry (rank-correlation > 0.90 or > 70% of dots within 3 px of a registry raster = duplicate → log it and stop); reuse the template tools (`evaluate_holdout.py`, `submission_writer.py`) — fix shared tools once in the template, never keep a private fork; label every number; leakage canary (any single feature with AUC > 0.90 on withheld truth = leakage until proven otherwise); budget ≤ 3 experiments or 2 hours; do **not** pick submissions (the selector step is separate and subject to the weekly cap); end with a **JSON run card** (hypothesis, mechanism, mimicking non-fault process, holdout DTI + CI, correlation/overlap vs registry, raster SHA-256, validator output, submission name + note ≤140 chars, verdict promote / negative). Negative results are deliverables.
9. No hallucinations: verify line by line from official, trusted sources and provide links for manual review. Collect and organise the competition data and knowledge into auditable tables; store a research knowledge base in the repository.
10. State limitations and access needs. There is no DrivenData login in the sandbox (the data tab redirects to login); use the Dropbox links, https://gdr.openei.org/submissions/1391, USGS GeoDAWN and the NLR rules PDF 96647 as sources.
11. A clean, simple GitHub Pages site under `docs/`.
12. Put the full prompt into the repository README (this file) and read it at the start of every session. Work on the "next steps" left by the previous session first.
13. Run three passes: (1) implement and verify, (2) review and fix bugs, (3) recheck against the request. Then create a pull request and merge it to `main`; list the remaining work and limitations for the next session.

## Expanded Ecosystem & Leaderboard Context (28 October 2026)

- **User-reported leaderboard context (`USER-REPORTED / UNVERIFIED`):** `#1 Jacker0429` (`0.4413`) and `#2 davec` (`0.3195`). Neither GeoTIFF nor an organizer receipt is available in this sandbox.
- **Focus & broader peer families referenced in prompt (`USER-REPORTED / UNVERIFIED`, learning only — never copied):** `GEMSDOE24`, `GEMSDOE25`, `GEMSDOE27`, `GEMSDOE28`, `GEMSDOE30`, `GEMSDOE31`, `GEMSDOE32` (`0.2778`), `GEMSDOE33`, `GEMSDOE36` (`0.2750`), plus `GEMSDOE91` (`0.1823`, `0.0435`), `GEMSDOE92` (`0.2699`), `KANLERGEMSDOE1–3` (`0.2673`), `EUGGEMSDOE1–3` (`0.2449`), `WBGGEMSDOE1–3` (`0.2709`), `GINNYGEMSDOE1–3` (`0.2718`), `GEMSDOEkarage1–3`, `ApartGEMSDOE1–3` (`0.2747`), and `GEMSDOESASS1–3` (`0.2449`). Commit-pinned audits are recorded in `registry/peer_ecosystem_pins.json` and `evidence/local_downloads_and_peer_audit_20261028.json`; full session analysis is in `knowledge/session-review-arena-1668dda0.md`.

