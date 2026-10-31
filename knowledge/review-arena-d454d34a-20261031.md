# Repository review — session `arena/d454d34a-gemsdoekarage1` (31 Oct 2026)

Run card: [`evidence/run_card_arena_d454d34a_20261031.json`](../evidence/run_card_arena_d454d34a_20261031.json)
Standing brief: [README → READ FIRST](../README.md). Core values: Maximize P(Win); Own the Outcome.

## 1. Answer first

**Can I download a file and submit it?** Technically yes for one file, with the limits below.

| Question | Answer |
|---|---|
| Which file? | [`docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif`](../docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif) (SHA-256 `30a5fc28…0ff0d`) |
| Does it pass the format and uniqueness gate? | **Yes.** I recomputed both from the bytes (§4). The project validator passes 15/15 against the restored mirror grid, footprint and catalogue. **One open format risk:** the official mirror sample writes NaN outside the footprint and this file writes zeros there (§5, item 11). |
| Is it a unique submission? | **Yes** under the literal 70 % / 3-px rule. Its dots lie within 3 px of the nine focus files' dots at most **26.5 %** (limit 70 %). |
| Is it a validated score improvement over 0.2778? | **No.** Nothing in this repo measures its score. The "0.2789" figure is a projection (§5). |
| Is it OK to submit? | **Eligible, not endorsed.** Uploading uses one of three weekly slots and is an owner decision. The site now says **ELIGIBLE TO UPLOAD · NOT VALIDATED** instead of "OK TO SUBMIT". |
| Best reported score so far | GEMSDOE32 B2 **0.2778** (USER-REPORTED, unverified). The live organizer board's #1 is **0.4544** (ORGANIZER-PUBLIC). |

### Executive table — nine focus sites plus the candidate

Scores are **USER-REPORTED / UNVERIFIED** unless marked. Several sites have more than one user-reported file (for example GEMSDOE28 has six entries, 0.0206–0.2710; GEMSDOE36 has 0.1647 and 0.2750). Each row shows the best-reported focus file for that site, matched to its registry raster by label (`registry/user_reported_nine_sites_20261029.json`). GEMSDOE25 is matched on `d2-8` rather than the raster name `d28`. "Max share within 3 px of another focus file" is the share of that file's dots that sit within 3 px of some other focus file's dots (computed from the registry rasters, §4).

| Site | File (registry) | Dots | Score (user-reported) | Max share within 3 px of another focus file | Unique vs other focus sites? | Download and submit? |
|---|---|---:|---:|---:|---|---|
| GEMSDOE24 | `GEMSDOE24_gems24-h25-1-…-nan.tif` | 60,069 | 0.2477 | 1.000 (GEMSDOE25) | **No** | No — duplicate |
| GEMSDOE25 | `GEMSDOE25_d28.tif` | 44,090 | 0.2600 | 1.000 (GEMSDOE24) | **No** | No — duplicate |
| GEMSDOE27 | `GEMSDOE27_gems27-topo-gap-…-nan.tif` | 61,328 | 0.2449 | 0.980 (GEMSDOE24) | **No** | No — duplicate |
| GEMSDOE28 | `GEMSDOE28_gems28-h36-1-…-nan.tif` | 37,660 | 0.2710 | 1.000 (GEMSDOE24) | **No** | No — duplicate |
| GEMSDOE30 | `GEMSDOE30_gemsdoe30-d28-…tif` | 44,090 | 0.2600 | 1.000 (GEMSDOE24) | **No** | No — duplicate |
| GEMSDOE31 | `GEMSDOE31_gemsdoe31-h27-4-…-nan.tif` | 40,199 | 0.2708 | 1.000 (GEMSDOE24) | **No** | No — duplicate |
| **GEMSDOE32** | `GEMSDOE32_B2.tif` | 37,654 | **0.2778** (best reported) | 1.000 (GEMSDOE24) | **No** — exact subset of GEMSDOE25 | No — already scored, duplicate |
| GEMSDOE33 | `GEMSDOE33_…-cb490425926e.tif` | 41,865 | 0.2632 | 0.997 (GEMSDOE27) | **No** | No — duplicate |
| GEMSDOE36 | `GEMSDOE36_gemsdoe36-anderson-…-zeros.tif` | 38,854 | 0.2750 | 0.976 (GEMSDOE27) | **No** | No — duplicate |
| **Candidate (new)** | `karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif` | 32,000 | **Not estimated.** Projection 0.2789 is PROJECTED, not a score. | 0.265 (GEMSDOE27) | **Yes** (literal 70 % rule) | **Eligible, not validated.** Owner decision. |

Live organizer board (fetched 31 Oct 2026, ORGANIZER-PUBLIC): #1 **0.4544** (xiaofanhu), #2 **0.3934** (cfld__), #47 **0.3261**. The user's "0.4413" does not appear in ranks 1–47. The repo's snapshot puts #50 at 0.3195; I did not re-read rank 50 this session.

## 2. Why GEMSDOE32 B2 scored 0.2778 (verified mechanism)

- **Verified:** B2 is an exact subset of GEMSDOE25. B2 has 37,654 dots, GEMSDOE25 has 44,090. All 37,654 B2 dots are in GEMSDOE25. 6,436 GEMSDOE25 dots were removed and none were added. (Recomputed from `registry/GEMSDOE32_B2.tif` and `registry/GEMSDOE25_d28.tif`.)
- **Consequence under the official metric:** deleting dots that earned less credit than the marginal bar raises DTI. Among the nine, the reported score falls as dot count rises (Spearman −0.98, n = 9; recomputed here). The nine files are one near-uniform field dotted differently (§4).
- **Not verified here:** that the removed dots lie near the mapped catalogue. The catalogue raster is not in this checkout.
- **Plain answer:** B2 is the sparsest version of the same field, not a different geological idea. It cannot be re-submitted for a new result; the score is already known.

## 3. Can a new file beat 0.2778? — honest answer

**Not demonstrated, and this repo cannot measure it.** Requirements, using the corrected metric (§6):

- A dot raises DTI only if its truth credit exceeds the marginal bar: **0.0588 at 0.2778, 0.0683 at 0.3195, 0.0968 at 0.4413.**
- At B2's budget (37,654 dots) and an assumed truth size of 60,988 px, 0.2778 needs about **0.257** truth coverage, and 0.4413 needs about **0.408**. The nine files cover about 0.245–0.257. So 0.4413 is about **1.6×** their coverage at equal dot count (`scripts/build_kp1_site.py` gives 1.85× the champion's hit rate in its own parameterisation; the two multiples are not directly comparable and both depend on the unknown truth size).
- Every local instrument fails to rank the known files. The catalogue hide-and-recover instrument ranks the nine exactly backwards (ρ = −1.0). The off-catalogue instrument ranks them at ρ = −0.34. So no local score can select a winner.

## 4. Verification trail (what I re-ran, and the result)

| Check | Method | Result | Status |
|---|---|---|---|
| Test suite | `pytest -q` in `.venv` (Python 3.11, requirements.txt) | **526 passed, 2 skipped, 0 failed** (2 skips became runnable once the mirror was restored; README said 493/498, stale) | VERIFIED |
| Kp1 file SHA-256 | `hashlib.sha256` on the bytes | `30a5fc28ff060ad38681d9b721024aea5aec3b070f407537dd28354efbe0ff0d` matches the run card | VERIFIED |
| Format | rasterio: shape, dtype, CRS, transform, NaN, min/max, distinct values | 3730×3292, float32, EPSG:32611, transform (100, 0, 243350, 0, −100, 4508550), 0 NaN, min 0, max 1, values {0, 1}, 32,000 dots | VERIFIED |
| Grid match | transform, CRS, shape and bounds vs the nine registry rasters | identical for all nine | VERIFIED |
| Overlap with nine (literal rule) | same script; distance transform, dots within 3 px, both directions | kp1 → focus max **26.5 %** (GEMSDOE27); focus → kp1 max 22.5 %; limit 70 % | VERIFIED (matches run card 26.5 %) |
| Correlation with nine | full footprint, binary so Spearman = Pearson | max \|ρ\| **0.0115** (GEMSDOE36). Run card claims 0.0076 | **Does not reproduce** (flagged; limit 0.90, passes either way) |
| Focus-file mutual overlap | 10×10 share matrix, `scripts/verify_registry_overlap_20261031.py` → `evidence/registry_overlap_matrix_20261031.json` | 0.976–1.000 between focus files | VERIFIED |
| Metric identity | literal brute force vs algebra, toy grids | identity matches the brute-force oracle at (α, β) = (0.2, 0.8), (0.3, 0.6), (0.5, 0.5), (0.1, 0.9) (test parameters); perfect = 1.0 | VERIFIED (`tests/test_metric_identity_20261031.py`) |
| Project validator | `vendor/gems57/validate.py` with footprint and catalogue masks | **15/15 PASS** (reproduces the run card's count) | VERIFIED against the restored mirror |
| Official sample grid | `data/sample_submission.tif` (mirror, hash-pinned) | EPSG:32611, shape, transform and bounds identical | VERIFIED against the mirror; not organizer-authenticated |
| Catalogue (zero dots on mapped catalogue) | `data/existing_faults.tif` (mirror) | 0 of 32,000 dots on it; 0 within 2 px; 2,699 (8.4 %) within 3 px | VERIFIED against the mirror |
| Outside-footprint encoding | kp1 zeros (0 NaN) vs sample NaN (7,111,787 cells outside the 5,167,373-cell footprint) | **Differs from the official sample** | FLAG (§5 item 11) |

## 5. Irregularities found (flagged for owner review)

1. **Contradictory status on the same page (fixed in the banner, README still open).** The public page said "DO NOT SUBMIT · NOT CLEARED" and, a few lines later, "OK TO SUBMIT … the only file cleared for upload". The banner now reads **ELIGIBLE TO UPLOAD · NOT VALIDATED**. The README top block still says "PROMOTE: ONE FILE IS CLEARED". That needs the owner's ruling.
2. **The gate does not test score.** `scripts/kp1_release_gate.py` sets `ok_to_submit` from format, uniqueness and catalogue mass. Its own `not_basis` field says "no validated leaderboard estimate". "OK TO SUBMIT" therefore meant "passes the gate", not "expected to beat 0.2778".
3. **The projection cannot separate kp1 from B2.** It is a 3-parameter OLS fitted to nine user-reported scores, extrapolated to kp1. The kp1 − B2 gap is +0.0020, smaller than the fit's own ±0.0027 leave-one-out half-width. The bootstrap interval for the projection, [0.2757, 0.2846], spans the champion's 0.2778.
4. **The only measured off-catalogue number is unfavourable.** HOLDOUT-DTI for kp1 is **0.0764** (evaluator `gems57-pooled-hide-v2` plus off-catalogue SGMC truth, leave-one-quadrant-out, 62,122 withheld positive cells). The nine focus files score **0.0934–0.1012** on the same instrument. The 95 % CI for kp1's gain over matched random dots is **[−0.0034, +0.0260]**, which includes zero. The run card reports "+19.3 %" without saying the CI spans zero.
5. **Metric identity error (corrected).** `scripts/kp1_metric_analysis.py` wrote DTI = T / (α(n−M) + βG + T). The correct form is T / ((1−β)T + α(n−M) + βG). The error gave a false perfect-knowledge ceiling of **0.556** (correct: **1.0**), a marginal bar of **0.0769** at 0.2778 (correct: **0.0588**), and **0.158** at 0.4413 (correct: **0.0968**). Those figures are repeated in AGENTS.md, the README, and knowledge notes. The generated pages are corrected. The historical notes are not rewritten, and this review supersedes them.
6. **Template coupling left in place (owner item).** `vendor/gems57/metric.py::marginal_accept` and `vendor/gems57/emit.py` write α where the correct coefficient is (1−β). The two agree only because α + β = 1 in the competition. The two-sided decision is unaffected, but the denominators differ off that convention. I did not change the file: it is hash-pinned by `evidence/template_integrity_20261028.json`, and changing it needs an owner-approved receipt. The release gate's `_dti` has the same coupling.
7. **Leaderboard figures conflict.** The user's prompt cites 0.4413 as the leaderboard high and 0.3195 as "highest right now". The live #1 is 0.4544. 0.4413 is not in ranks 1–47. Every focus-site score in this repo is USER-REPORTED, not organizer-confirmed.
8. **Rules: generative-AI disclosure.** [Official rules §3.2](https://docs.nlr.gov/docs/fy26osti/96647.pdf) require the narrative to state the extent of generative-AI use. The repo has no such narrative. This is an owner action before any final submission.
9. **Rules: one final submission.** The [competition page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) says competitors "must choose a single submission for scoring across both rounds … without knowing their private test set performance." Weekly uploads are a probe, not the final entry.
10. **Rules: Phase 2 labels are revised from submitted predictions.** Per the same page and [rules §1.1](https://docs.nlr.gov/docs/fy26osti/96647.pdf), experts update the label set using submitted predictions. Predictions should be genuine, documented geological judgements.
11. **Outside-footprint encoding differs from the official sample.** The mirror `sample_submission.tif` writes NaN in all 7,111,787 cells outside the 5,167,373-cell footprint. The rules text says data outside the bounds should be null or NaN. The kp1 file writes zeros in those cells, which lie inside the raster bounds, so it stays in [0, 1]. The project validator's all-finite precaution is a local choice that the kp1 file passes and the sample fails (`no_nan_anywhere`, `outside_footprint_zero`). The user's "Predicted values must be in range [0, 1]" error is unexplained (IR-57-NAN-02), and the portal's handling is undocumented. A NaN-outside twin would have the same 32,000 dots and would fail the project's own `no_nan_anywhere` check, so it is not in `docs/downloads/`. Generating one is an owner decision.
12. **Data restored from pinned public mirrors only.** `scripts/restore_karage1_data.py --group core` restored `training_features.tif`, `labels.tif`, `existing_faults.tif` and `sample_submission.tif` into the git-ignored `data/` directory, with full SHA-256 checks. A matching hash shows mirror consistency, not organizer authenticity. DrivenData's data page requires login, so organizer files were not checked. The catalogue-adjacency of the 6,436 removed dots (§2) is still unverified, because B2 and GEMSDOE25 are not checked against the catalogue here.
13. **The mirror's sample is not a neutral template.** `sample_submission.tif` has 60,988 positive cells, all identical to the catalogue (`labels.tif`, `existing_faults.tif`; the last two are byte-identical by SHA-256). This is recorded in another session as IR-S1. Its grid and NaN encoding are still valid references, but its positives are not a blank submission.
14. **Repository bloat.** The README is 123 KB with 55 level-2 sections, many of them superseded review blocks. `docs/downloads/` holds 26 TIFs. Recommend archiving.

## 6. Corrections made in this session

| File | Change | Why |
|---|---|---|
| `scripts/kp1_metric_analysis.py` | identity, ceiling, bars, narrative fixed; `score()` now calls `gems57.metric.dti_from_components` | wrong algebra; removes a private identity (protocol: fix shared tools once) |
| `evidence/kp1_metric_analysis.json` | regenerated | follows from the above |
| `scripts/build_kp1_site.py`, `scripts/render_site.py` | banner → "ELIGIBLE TO UPLOAD · NOT VALIDATED"; ceiling and bar text corrected | the banner overstated what the gate checks |
| `tests/test_kp1_lane.py` | assertions updated to the new banner | follows from the above |
| `tests/test_metric_identity_20261031.py` | **new**: 6 tests against the brute-force oracle |
| `scripts/verify_registry_overlap_20261031.py` | **new**: reproduces the overlap matrix, correlation and format checks from local files | so the review's numbers can be rerun | regression guard for the identity and the bar |
| `docs/**`, `index.html`, `executive-summary.html`, `legacy-*.html` | regenerated by the existing generators | banner change propagates; CI diff check |
| `evidence/run_card_arena_d454d34a_20261031.json` | **new** run card | required output |
| `knowledge/review-arena-d454d34a-20261031.md` | **new** (this file) | required output |
| README, AGENTS.md | new top block | so the next session reads the correction first |

`vendor/gems57/metric.py` was edited and then reverted (§5, item 6). The tree is clean on that file.

## 7. Official sources (manual review)

- Competition page: https://www.drivendata.org/competitions/306/competition-doe-gems/
- **Problem description, metric and submission format (read):** https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- **Leaderboard (read, live, 31 Oct 2026):** https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- **Official rules, NLR (read: preface, §1–2, §3–3.2; §3.5–3.6 and Appendix A not read):** https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution (landing page read): https://github.com/drivendataorg/gems-prize-reference-solution
- Rules page (linked by the competition, not read): https://www.drivendata.org/competitions/306/competition-doe-gems/rules/
- GeoDAWN source (USGS): https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and — not fetched this session
- UTM zone 11N, EPSG:32611: https://epsg.io/32611 — not fetched this session (the grid match in §4 is internal)

## 8. Next steps (ordered; none spends a slot)

1. **Owner ruling on status** — decide whether kp1 is uploaded as a labelled experiment, and update the README's top block to match.
2. **Organizer authenticity** — the mirror is restored and hash-consistent, but organizer files (DrivenData data page, login required) have not been checked. Confirm the mirror against the organizer copy when an account is available.
3. **Fix the holdout before trusting any holdout number** — the catalogue instrument is anti-correlated with the leaderboard (ρ = −1.0). Either find an instrument that ranks the nine correctly (a necessary test) or stop using holdout DTI as a selector.
4. **Decide the template coupling** — approve a receipt-backed change to `vendor/gems57/metric.py` and `emit.py` so the T coefficient is (1−β) throughout, or record the α + β = 1 assumption in the template.
5. **Decide the outside-footprint encoding** — zeros (kp1) or NaN (official sample). Test the portal once or ask DrivenData; do not rely on either until one is confirmed.
6. **Prepare the generative-AI narrative** required by the rules, before any final entry.
7. **Archive stale material** — move superseded TIFs and review blocks to `archive/`, keeping the run cards.

## 9. Limitations

- No organizer receipt exists for any file in this repo. Every score figure is USER-REPORTED, PROJECTED, or HOLDOUT-DTI on a proxy instrument.
- Organizer files were not checked. The restored mirror is hash-consistent with the committed manifest but is not organizer-authenticated.
- I read only parts of the rules (§1–3.2). Sections 3.5–3.6 (scoring details) and Appendix A were not read.
- This review did not generate a new raster. A new file would have been validated only by the same instruments that §3 shows cannot rank candidates.
