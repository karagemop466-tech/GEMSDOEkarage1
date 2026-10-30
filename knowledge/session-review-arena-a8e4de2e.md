# Session review · `arena/a8e4de2e` · 30 Oct 2026

**Verdict: NEGATIVE. Nothing is cleared. No file may be uploaded.** One experiment used of three allowed; no weekly slot spent; `ok_to_submit: false`.

Read with: `docs/session-a8e4de2e.html` (executive summary and per-site table), `evidence/run_card_h_r1_20261030.json` (run card), `evidence/exp_h_r1_kth_magedge_20261030.json` (raw receipt), `knowledge/hypotheses-20261030.md` (ranked hypotheses).

## 1. Executive summary

- **Can a file be downloaded and submitted? No.** The new unique file, `karage1-hr1-kth-magedge-37654-20261030-zeros.tif` (archive, research only), fails the pre-registered rule. Its pooled HOLDOUT-DTI is 0.04330 (cell-bootstrap 95% CI [0.03559, 0.04629]). Random placement with the same dot count scores 0.04460 (seeds 0.04638, 0.04199, 0.04542). The paired difference is −0.0029, CI [−0.0071, +0.0009].
- **Best reported file:** GEMSDOE32 `h33-h33-2-b2`, USER-REPORTED 0.2778. Not unique: strict subset of GEMSDOE25, with 6,436 catalogue-adjacent dots removed and nothing added.
- **Official leaderboard, read 30 Oct 2026:** #1 = 0.4544; 0.4413 is not in the top 50; #48 = 0.3195.
- **Why no file is clearable:** (a) the holdout is below random; (b) the literal 70 % dot gate trips on two dense rasters, which is a density artifact and not a copy; (c) the format conflict and the target mismatch below remain unresolved.

## 2. Pass 1 — build and measure

1. Restored `core` and `external` data groups (`scripts/restore_karage1_data.py`), then `scored`. All hashes matched `registry/karage1_data_manifest.json`. Mirror consistency only, not organizer authentication.
2. Baseline test suite: 431 passed, 1 failed, 1 skipped. The failure was `test_focus_sites_20261029` reading a hard-coded `data/bridge` path. Fixed with a git-ignored symlink, `data/bridge -> /tmp/gems_data`, not a code change (see §5). After the fix: 432 passed, 1 skipped. After adding 13 regression tests (`tests/test_session_a8e4de2e.py`) and fixing two of my own link and audit-rule errors caught by the existing suite: 445 passed, 1 skipped.
3. Read the shared template (`vendor/gems57/holdout.py`, `evaluate_holdout.py`, `submission_writer.py`, `validate.py`, `uniqueness.py`, `grid.py`). Did not modify it. `vendor/PROVENANCE.json` pins its file hashes.
4. Chose H-R1 because `knowledge/session-review-arena-fb1e3550.md` named K/eTh residuals as the recommended next experiment. Grep showed channel 44 (`geodawn_blk_kth_alteration`) is already a weighted term of a composite (`src/gemskarage1/features.py:668`), but it was never scored standalone. The GSE run card records `holdout_dti: not run`.
5. Pre-registered H-R1 in `knowledge/hypotheses-20261030.md`, with the decision rule fixed as `DECISION_RULE` in `scripts/run_h_r1_kth_magedge.py` before any result.
6. Ran `scripts/run_h_r1_kth_magedge.py`. Deterministic (fixed seeds). A first run was discarded and re-run after adding the owner's scored mirrors to the registry scan (35 → 50 rasters) and the gate-trip listing. Candidate, null and canary numbers were identical in both runs; only the uniqueness scan changed.
7. Built the nine-site table from `registry/user_reported_scores_20261029.json` and `evidence/site_lineage_verification_20261029.json`, via `scripts/build_session_a8e4de2e.py`. No number on the page is typed in by hand.
8. Changed the home-page strip in `scripts/submission_hub.py` (it was stale, pointing at a 29 Oct file). Re-rendered with `scripts/render_site.py`, which is deterministic. Only `index.html`, `docs/index.html` and the strip changed.

## 3. Pass 2 — adversarial review

| Concern | Check | Result |
|---|---|---|
| Leakage: could the surface see the catalogue? | Read `build_surface`: uses only GeoDAWN K/Th/TC, block ids, and official `tmi_hg`. Catalogue is used only for the diagnostic on-catalogue count and the SGMC proxy. | No leakage in the surface. |
| Canary | Per-cell AUC of each feature alone, withheld truth vs active pixels. | Max direction-invariant AUC 0.633 (zK). All below 0.90. |
| Is the holdout the right target? | Read `holdout.build_holdout`: truth = withheld mapped catalogue segments. The official problem page says the test set is expert-labelled **new** faults not in the USGS database. | **Mismatch.** The holdout rewards re-finding mapped traces. Its CI and null still hold for what it measures. |
| Null fairness | Same 16 cells, same dot count, 3 seeds, paired per cell. | Fair. Candidate is below null. |
| Champion control | GEMSDOE32 raster on the same cells: 0.00473 (CI [0.00434, 0.00516]). | Reproduces the earlier session's 0.0047 value. |
| Dot-gate trips | Listed both: halo surface (5.1 M positive cells, 100 % trivially within 3 px) and 13GEMS lattice witness (207 k positive cells, 99.78 %). Reverse overlap 19 % in both; Jaccard < 0.01. | Gate fails **on density**; not waived. The rule is internal, not official. |
| Proxy (SGMC off-catalogue) | Candidate 12.8 %, random 19.2 %, champion 21.8 %. | Below random on the proxy too. Informational; cannot promote. |
| Validator | Shared validator passes (zeros primary). Independent check: 37,654 dots, float32, EPSG:32611, shape 3730×3292, transform equals sample, no NaN, values {0,1}. NaN-outside twin: NaN exactly outside footprint, same dots. | Passes both readings of the format. |
| Rule integrity | `DECISION_RULE` written before the run. Criteria are computed, not edited. | Verdict follows the rule. |
| Budget | 1 experiment of 3. Wall-clock time was not logged precisely; the session stayed within the 2-hour cap by estimate. | Within budget (estimate). |

## 4. Pass 3 — line-by-line verification (claim → source → status)

| Claim | Source | Status |
|---|---|---|
| Official metric: DTI, α = 0.2, β = 0.8, 300 m triangular kernel | <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/> (fetched 30 Oct 2026) | ORGANIZER-PUBLIC text, verified this session |
| Test set = expert-labelled **new** faults not in USGS catalogue | same page | Verified this session |
| Format: float32, values in [0,1], EPSG:32611, 100 m, outside bounds null or NaN | same page | Verified this session. The "null or NaN" wording conflicts with the repo's zeros-only writer. |
| #1 = 0.4544 | leaderboard, chunk 0 | Verified this session |
| 0.4413 absent from top 50 | leaderboard, chunks 0–2 (ranks 1–50) | Verified this session |
| 0.3195 = rank #48 (not #47) | leaderboard, chunk 2 | Verified this session; the repo's earlier "#47" note is off by one |
| GeoDAWN DOI 10.5066/P93LGLVQ, CC0 | <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and> | Verified this session |
| GeoDAWN uint8 K/Th/U/TC grids | `external/geodawn_rad_u8.tif`, owner-derived mirror, bands read: K, Th, U, TC | Mirror only; quantisation not independently checked |
| Official band names `rtp`, `tmi_hg`, `tmi`, `tmi_vg` | band descriptions inside `training_features.tif` | Verified against the file |
| GEMSDOE32 = GEMSDOE25 mask minus 6,436 within 2 px, 37,654 dots | `evidence/site_lineage_verification_20261029.json` | Measured by a prior session; re-read this session |
| Nine-site sibling overlap ≥ 97.6 % | same file, pairwise fields | Re-read this session |
| Scores 0.2477–0.2778 | `registry/user_reported_scores_20261029.json` | USER-REPORTED / UNVERIFIED. Not checked against an organizer receipt. |
| Euler deconvolution has no code in the repo | `grep -ril euler scripts src vendor` (30 Oct 2026) | Verified |
| Channel 44 is a weighted composite term | `src/gemskarage1/features.py:668` | Verified by reading |

## 5. Irregularities flagged

1. **Leaderboard figures conflict.** The user's 0.4413 is not in the official top 50. 0.3195 is #48 in this snapshot, not #47. Leaderboards move; re-fetch before quoting.
2. **Format conflict.** The official text says data outside bounds is "null or nan". The shared writer accepts all-finite zeros only and labels NaN as diagnostic. Both readings are provided; the owner must resolve. The portal error "Predicted values must be in range [0, 1]" is not reproduced locally with either file.
3. **Target mismatch.** The internal holdout truth is mapped catalogue; the competition's test set is new faults. Results from the holdout cannot rank off-catalogue candidates, which the repo already showed (the champion scores below random).
4. **Lattice rule.** The 70 % / 3 px rule is internal and not in the official problem page. It fails on dense rasters regardless of copying (this session's two trips), and it fails random uniform dot sets (`evidence/lattice_gate_null_check_20261029.json`).
5. **Template path bug.** `vendor/gems57/grid.py` hard-codes `data/bridge` and ignores the restore location. A template fix (honour `GEMS_DATA_DIR`) would change a hash-pinned vendor file, so it is left for an owner decision. Workaround: git-ignored symlink.
6. **Stale home strip.** The home page pointed at an older 29 Oct file. Updated this session. The hub page `docs/submission-hub.html` still describes the 29 Oct file (its facts come from a separate evidence chain); it is internally consistent with "not cleared" but out of date. Flagged in §6.
7. **Data provenance.** All restored data are owner-mirrored, pinned by hash. Organizer authenticity is not established.
8. **Unverified user figures.** The nine-site scores (0.2477–0.2778) remain USER-REPORTED. Not reproduced.

## 6. Remaining work (ordered)

1. **Owner decisions** (blocking any clearance): NaN vs zeros outside; whether the 70 % lattice rule binds; whether the internal holdout target should change to new faults, or a labelled proxy be used as the primary instrument.
2. **H-E1 (Euler deconvolution, depth-clustered).** Ranked second, untested, no code exists. Needs an implementation (window and structural-index sweep), then one holdout experiment (2 of 3 slots).
3. **Hub page refresh.** Regenerate `docs/submission-hub.html` facts from this session's evidence, or mark it superseded.
4. **Template fix** for `grid.py` data-dir resolution, once the owner approves changes to hash-pinned vendor files.
5. **Re-fetch the leaderboard** before the next session quotes any rank.

## 7. Limitations

- Holdout numbers are HOLDOUT-DTI with a 16-cell bootstrap CI. They measure re-finding mapped traces. They are not organizer scores.
- The SGMC recall is a PROXY built from an owner-derived mirror. It is not the competition's truth.
- Only one hypothesis was tested. The "3 to 5 ranked hypotheses" are ranked, not all tested.
- The NLR rules PDF (96647) and the DrivenData data page were not re-read this session. The data page is login-walled.
- Local format checks are not organizer acceptance. Uniqueness is measured only against the 50 rasters available locally and mirrored, not every listed submission.
- No file is cleared; no weekly slot was spent; no promotion decision was made.
