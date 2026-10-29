# Standing prompt · DOE GEMS (DrivenData competition 306) · as received 2026-10-29

Read at the start of every session. This is a **condensed** record of the user's standing requirements. Duplicated passages from the pasted prompt were merged; no requirement was dropped. Source: the 2026-10-29 user message, plus the official pages it relies on.

## Objective
Maximize P(Win) and own the outcome. Produce, for the DrivenData DOE GEMS prize:
1. An executive summary for focus sites **GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36**: highest-scoring submission per site, file to download, estimated score, and whether it is unique versus all listed GEMSDOE sites. The best submission must be obvious.
2. A **unique, format-valid, single-band GeoTIFF**: values in [0, 1], EPSG:32611, shape and geotransform matching the sample. Easy to download. It must be **obvious at the top of the site** whether it is OK to download and submit. It must not copy any previous submission (learning and education only).
3. A PhD-level explanation of why `h33-h33-2-b2` (GEMSDOE32, 0.2778) scored highest among those listed, and whether it can be beaten.
4. 3–5 new geological hypotheses: layers used, physical signature, why off-catalogue, how each differs, ranked by expected DTI gain and cost. Validate the top one on a spatially blocked hide-and-recover holdout before any slot use.
5. Put this prompt into the README and read it every session. Maintain a **how-to-submit** subpage (file, unique name, note ≤ 140 characters). Keep a clean GitHub Pages site under `docs/`.
6. Work in three passes. Then create a pull request and merge it to `main`. List remaining work and limitations.

## Labels (mandatory)
- Every number is **HOLDOUT-DTI** (evaluator version, withheld positive count, 95% CI) or **ORGANIZER-CONFIRMED** (from a submission receipt).
- A projection is never written as a score. Estimated leaderboard scores are "Unavailable" unless measured under an evaluator.
- Irregularities are flagged, not hidden. Mirrors with matching hashes do not establish organizer authenticity.

## Parallel-run protocol (binding)
- One assigned lane per session.
- **Duplicate gate:** |Spearman| > 0.90, or > 70% of dots within 3 px of any registry raster → log as duplicate and stop. Check on the surface before placement and on the final dots.
- Reuse the shared template (`evaluate_holdout.py`, `submission_writer.py`, feature stack). Fix shared tools once, in the template, and report it. No private forks.
- **Hide-and-recover holdout:** withhold whole fault segments with a buffer. Derive catalogue features only from visible faults. Mask visible faults pixel-exactly. Score pooled DTI (α = 0.2, β = 0.8, 300 m triangular kernel).
- **Leakage canary:** each feature alone on the holdout. AUC > 0.90 = leakage until proven otherwise.
- **Run card (JSON), required:** hypothesis; mechanism; named non-fault mimicking process; holdout DTI with CI; correlation and overlap versus registry; raster SHA-256; validator output (no NaN in footprint, values in [0, 1], CRS / shape / transform match); submission name and note ≤ 140 characters; verdict (promote or negative). Negative results are deliverables.
- **Budget:** ≤ 3 experiments or ≤ 2 hours per session. Do not pick submissions. Slot selection is a separate selector step within the weekly cap.
- Do not upload old predictions. Do not manufacture scores.

## Official facts relied on (verified 2026-10-29; re-verify each session)
- Metric and submission format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Masking of known faults (staff, 16 Sep): https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Public leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Reference solution (Tversky α = 0.2, β = 0.8): https://github.com/drivendataorg/gems-prize-reference-solution

## Session gate for this repo
- Read `README.md`, `AGENTS.md`, `docs/standing-prompt.md`, and the latest `knowledge/session-review-*.md`.
- Never commit large data. Competition data lives under `.cache/gems_data` (restored by `scripts/restore_data.py`, SHA-256 verified, git-ignored).
- The branch name is fixed for the session. Push only to it.
