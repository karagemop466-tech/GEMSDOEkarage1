# Review · session `arena/a0f55a6a-gemsdoekarage1` · 31 Oct 2026

Scope: GEMSDOE competition 306 (DrivenData). Nine focus sites: GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36.
Standing prompt: `README.md`, section "SESSION PROMPT — FULL TEXT". Core values: **Maximize P(Win)** and **Own the Outcome**.

Label key: **ORGANIZER-CONFIRMED** = official organizer receipt (none exists for any file here).
**HOLDOUT-DTI** = our own spatially held-out instrument, not the leaderboard metric.
**PROJECTED** = a model estimate, never a score. **USER-REPORTED** = a number the user supplied.

---

## 1. Verdict (plain)

**NO. The KP1 GeoTIFF (`docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif`) is NOT OK to download or submit.**

- Format: passes the official rules (EPSG:32611, 100 m, float32, one band, values in [0, 1], no NaN, no nodata).
- Uniqueness against the nine focus files: passes (max |Spearman| 0.0076, max 3-px overlap 26.5 %).
- Uniqueness against the listed GEMSDOE repositories: **FAILS.** The GEMSDOE13 lattice raster
  (`buffedlizard55-lab/13GEMSDOE`, `13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`, 206,895 dots)
  has **99.78 %** of KP1's dots within 3 px. The user's protocol treats more than 70 % as a duplicate.
  Thirty-two files from eight listed repositories exceed 70 %.
- The earlier `ok_to_submit: true` in `evidence/kp1_release_gate.json` was **wrong**. That gate checked only the
  nine focus files. It now requires the listed-site receipt and reports `ok_to_submit: false`.

**Expected score: not established.** The projection 0.2789 is PROJECTED, not a score. On the one off-catalogue
instrument we have, KP1 scores below all nine focus files (section 4). Nothing measured supports a score above 0.2778.

**Nothing was submitted, no weekly slot was selected or spent, and no file is cleared.**

---

## 2. Executive summary per site (table)

Best known file: **GEMSDOE32_B2.tif** (USER-REPORTED 0.2778). It is the highest known score among the nine files.
It is already listed, so the repo's action is "DO NOT RESUBMIT". A re-upload is not a new candidate.

| Site | File to download (repo `registry/`) | Score | Estimated leaderboard score | Unique vs other GEMSDOE sites? | OK to download and submit? |
|---|---|---|---|---|---|
| GEMSDOE24 | `GEMSDOE24_gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 USER-REPORTED | NOT ESTIMABLE | NO (worst pair 3-px overlap 1.00, vs GEMSDOE25) | NO (already listed) |
| GEMSDOE25 | `GEMSDOE25_d28.tif` | 0.26 USER-REPORTED | NOT ESTIMABLE | NO. Identical mask to GEMSDOE30 | NO (already listed) |
| GEMSDOE27 | `GEMSDOE27_gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 USER-REPORTED | NOT ESTIMABLE | NO | NO (already listed) |
| GEMSDOE28 | `GEMSDOE28_gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.271 USER-REPORTED | NOT ESTIMABLE | NO | NO (already listed) |
| GEMSDOE30 | `GEMSDOE30_gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91ea…tif` | 0.26 USER-REPORTED | NOT ESTIMABLE | NO. Identical mask to GEMSDOE25 | NO (already listed) |
| GEMSDOE31 | `GEMSDOE31_gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 USER-REPORTED | NOT ESTIMABLE | NO | NO (already listed) |
| **GEMSDOE32** | **`GEMSDOE32_B2.tif`** (best known, 37,654 dots) | **0.2778 USER-REPORTED** | NOT ESTIMABLE | NO (worst pair 3-px overlap 1.00, vs GEMSDOE24) | NO (already listed; DO NOT RESUBMIT) |
| GEMSDOE33 | `GEMSDOE33_GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e…tif` | 0.2632 USER-REPORTED | NOT ESTIMABLE | NO | NO (already listed) |
| GEMSDOE36 | `GEMSDOE36_gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b…tif` | 0.275 USER-REPORTED | NOT ESTIMABLE | NO (worst pair 3-px overlap 1.00, vs GEMSDOE32) | NO (already listed) |
| **New (this session)** | `karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif` | PROJECTED 0.2789 (not a score) | NOT ESTIMABLE | Nine focus files: YES. Listed sites: **NO** (99.78 % vs GEMSDOE13 lattice) | **NO** |

Sources: `evidence/nine_site_executive_20261031.json` (scores, names, flags), `evidence/kp1_release_gate.json`,
`evidence/kp1_uniqueness_vs_listed_sites_20261031.json`. Per-site scores are USER-REPORTED / UNVERIFIED with no organizer receipt.

Irregularity: GEMSDOE25 and GEMSDOE30 have identical masks (exact mask duplicates) and the same reported score (0.26).
The repo records this but does not explain it. Flagged.

---

## 3. Why GEMSDOE32 B2 (0.2778) scored highest — what we can and cannot say

Detail: `knowledge/kp1-why-gemsdoe32-scored-02778.md` (earlier session).

Verified this session by script: **B2 is a strict subset of GEMSDOE25** (`registry/GEMSDOE25_d28.tif`, 44,090 dots).
44,090 − 6,436 = 37,654, so 6,436 dots were removed and none added. B2 is the sparsest of the nine files
(37,654 dots; GEMSDOE28 has 37,660). Across the nine reported scores, lower dot counts go with higher scores
(for example 37,654 → 0.2778; 60,069 → 0.2477). That is an observed trend across nine points, not a proof.
It is a statement about the file, not a leaderboard result.

We cannot say more without an organizer receipt for each file.

---

## 4. What the measurements say (labelled)

### 4a. KP1 on the only off-catalogue instrument (`evidence/kp1_exp3_comparison.json`)

| Arm | Dots | Off-catalogue DTI | Label |
|---|---|---|---|
| KP1 candidate | 32,000 | **0.0764** | HOLDOUT-DTI |
| Uniform random, matched count (mean of 3 seeds) | 32,000 | 0.0640 | HOLDOUT-DTI |
| Uniform random at champion budget | 37,654 | 0.0740 | HOLDOUT-DTI |
| Nine focus files (range, same truth) | 37,654 to 60,069 | **0.0934 to 0.1012** | HOLDOUT-DTI |

Truth: SGMC faults inside the footprint and more than 3 px from the catalogue (62,122 cells). KP1 beats matched random
by +19.3 %. Its paired block-bootstrap CI for the **difference** (+0.0109, 95 % [−0.0034, +0.0260]) crosses zero.
The run card's "0.0764" has no CI of its own. Flagged.

Read: KP1 is below every focus file on this instrument. The instrument ranks the nine focus files against their known
scores with a negative correlation (`evidence/kp1_exp2_holdout.json`, `instrument_calibration`: −1.0). So neither of
our instruments predicts the leaderboard, and the 0.2789 projection has no measured support.

### 4b. Leakage and calibration reruns (this session, fresh sandbox, hash-verified inputs)

- Leakage canary (`scripts/kp1_exp2_holdout.py`): max mean AUC 0.5993. Matches the stored value. Below the 0.90 alarm.
- Instrument calibration: −1.0. Matches the stored value.
- Candidate arm rerun: 3,850 dots and DTI 0.001832, against 3,856 dots and 0.001849 in the committed file. About 1 % drift.
  The rerun is in `evidence/kp1_exp2_holdout_rerun_20261031.json`. The committed `kp1_exp2_holdout.json` is unchanged.

### 4c. Reproducibility of the KP1 raster (this session)

- All pinned inputs restored from the hash-pinned mirrors and their SHA-256 values matched.
- Rebuild with `scripts/kp1_build_candidate.py`: same 32,000 positives and same mean, but **90 dots differ**
  (moved 1–9 px). SHA-256 `f50c2daf…` against the committed `30a5fc28…`. The cause is not established: the
  original receipt does not record library versions or plane digests. The committed file is the one hashed in the gate.

### 4d. Independent re-check (`scripts/verify_kp1_independent_20261031.py`)

Data-free, from the saved bytes. Every number matches the gate receipt: max |Spearman| 0.007607 (GEMSDOE36), and each
per-raster 3-px overlap to six decimals. Output: `evidence/kp1_independent_verification_20261031.json`.

### 4e. Listed-site uniqueness (`scripts/uniqueness_vs_listed_sites_20261031.py`)

- 113 listed owner/repo pairs. 107 contain at least one TIF in the repository tree. 6 contain none
  (`eugboogieman123-ops/EUGGEMSDOE1-3`, `ginnymcfiner23-ux/GINNYGEMSDOE1-3`). Those 6 are NOT checked.
- 3,740 TIF paths downloaded from `codeload`/`api` with the authenticated `gh` CLI. 1,292 byte-duplicates skipped.
  **2,473 unique GeoTIFFs compared**: 2,456 on the same grid, 17 on another grid (compared by world coordinates).
- Excluded from the rule, and listed in the receipt: 10 multi-band inputs (not single-layer submissions), 16 files
  that rasterio cannot read (for example `smoke.tif`, and GEMSDOE75 `data/bridge/*.tif`, probably Git LFS pointers or
  placeholders), and 91 dense rasters with more than 1,000,000 positives (for example full-footprint "all positive" files).
  Dense rasters are excluded because almost any dot falls within 3 px of them. They are not hidden.
- **Max 3-px overlap: 99.78 %** (GEMSDOE13 lattice, `buffedlizard55-lab/13GEMSDOE`). Limit 70 %. **Fails.**
- Files over 70 %: 32, across eight origins: 13GEMSDOE 20, GEMSDOE3 3, GEMSDOE22 2, GEMSDOE50 2, GEMSDOE67 2,
  61GEMSDOE 1, 15GEMSDOE 1, GEMSDOE77 1.
- Max |Spearman| (binary same-grid files): 0.0406. Passes (limit 0.90).
- Exact duplicates of the candidate: none outside this repository. Its own `main` copy is recorded and not counted.

---

## 5. Official sources (verified this session)

- Problem and submission format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
  — one GeoTIFF; EPSG:32611; 100 m; same bounds as training data; null or NaN outside bounds; single float32 layer
  with values in [0, 1]; metric distance-weighted Tversky, α = 0.2 (FP), β = 0.8 (FN), triangular kernel R = 300 m;
  three submissions per week.
- Competition homepage: https://www.drivendata.org/competitions/306/competition-doe-gems/ — **Competition end date
  Dec. 3, 2026, 11:59 p.m. UTC.** Prize: $50k initial round (top 5 on private test set), $250k final round (top 5 on the
  re-labelled set). Dates are NOT in the rules PDF; the PDF defers to this page. The earlier repo claim "per the official
  rules PDF" was wrong and has been corrected in `scripts/build_executive_20261031.py`.
- Official Rules PDF (Sept 2026): https://docs.nlr.gov/docs/fy26osti/96647.pdf — single entry; one GeoTIFF; scoring in two
  phases; eligibility (individual competitors must be a U.S. citizen or permanent resident); the rules require
  **disclosure of generative-AI use in the narrative**. Any submission would need that disclosure. Eligibility is in section 1.3 (verified). The AI-disclosure statement is from the earlier fetch of the same PDF.
- Leaderboard (fetched): #1 0.4544; #2 0.3934; #3 0.3917; #10 0.3550; #23 0.3405; #24 0.3399; #47 0.3261.
  0.4413 does not appear in ranks #1–#47. The #50 = 0.3195 figure comes from the repo snapshot
  `evidence/leaderboard_snapshot_20261031.json` and was not re-read here.

---

## 6. Irregularities (flagged, not resolved)

1. **Stale green verdict.** Earlier, `docs/index.html`, `docs/executive-summary.html` and `docs/submission-hub.html` showed a
   green "OK TO SUBMIT" banner above body text that said "No". The merged `main` now routes every verdict through
   `scripts/release_authorization.py`, which denies KP1. The pages were regenerated and show DO NOT SUBMIT.
2. **Gate receipt was wrong.** `ok_to_submit: true` checked only the nine focus files. Fixed: the listed-site receipt is required.
3. **Close-date attribution.** The date is correct (Dec. 3, 2026, 11:59 p.m. UTC, from the homepage). It was wrongly attributed
   to the rules PDF. Fixed.
4. **Missing dependency.** `scripts/kp1_planes.py` imports pandas, which was not in `requirements.txt`. Added.
5. **Mixed nodata convention.** GEMSDOE24, 27, 28 and 31 use NaN outside the footprint (7,111,787 cells). The others use zeros.
   Both forms have user-reported scores, which conflicts with the repo's "NaN fails" statement. Not resolved.
6. **Organizer sample raster.** `data/official/sample_submission.tif` (restored, pinned) has 60,988 positive cells, the same as
   the mapped catalogue count. Our footprint is its finite cells (5,167,373), and it matches the NaN-outside registry masks
   exactly. We have not checked how the rules describe that raster.
7. **HOLDOUT-DTI 0.0764 has no CI of its own.** See 4a.
8. **Flaky legacy test.** `tests/test_field_site.py::test_legacy_builder_does_not_overwrite_current_pages` passed on one run and
   failed on another in an earlier session. In this session it ran after a site rebuild and passed. Not root-caused.
9. **The lattice rule.** The repo's generic `scripts/release_gate.py` requires a "pinned lattice witness" (`registry/reference_assets.json`).
   KP1 was never measured against it, and KP1's lattice overlap is 99.78 %.

---

## 7. What changed in the repository (this session, merged with `main`)

`main` gained three sessions of work while this branch was open (PRs #119–#124). Conflicts were resolved in favour of
`main`'s fail-closed architecture: `scripts/release_authorization.py` and `evidence/active_submission_status.json` are the
single authority for "may this be uploaded". Only the following was added on top:

- `scripts/verify_kp1_independent_20261031.py` → `evidence/kp1_independent_verification_20261031.json` (data-free re-check).
- `scripts/uniqueness_vs_listed_sites_20261031.py` → `evidence/kp1_uniqueness_vs_listed_sites_20261031.json`.
- `scripts/fetch_listed_site_tifs.py` → `evidence/listed_sites_tif_inventory_20261031.json` (bytes in git-ignored `data/peers/`).
- `scripts/kp1_release_gate.py`: requires the listed-site receipt in addition to `main`'s gates. Re-run: `ok_to_submit: false`.
- `evidence/kp1_exp2_holdout_rerun_20261031.json`: rerun receipt. The committed holdout file is unchanged.
- `evidence/run_card_arena_a0f55a6a_20261031.json`: run card (labels on every number).
- `tests/test_kp1_lane.py::test_listed_site_receipt_matches_bytes_and_gate`.
- `requirements.txt`: `pandas>=2.0` (needed by `scripts/kp1_planes.py`).
- `scripts/build_executive_20261031.py`: close-date attribution corrected.
- README current-verdict block (above `READ FIRST — ACTIVE SESSION arena/a79c8595`); AGENTS.md note.

Restoration: `scripts/restore_karage1_data.py --group core` and `--group external` were run. 16 files, all SHA-256 matched.
`data/official/` is a symlink layout that the builder expects.

**Other candidates on `main` (added by other sessions).** The same lattice test applies to them:

| File on `main` | Dots | Within 3 px of the GEMSDOE13 lattice | Limit | Result |
|---|---|---|---|---|
| `docs/downloads/gems-karage1-offcat-geophys-edge-37654dots-20261031-zeros.tif` | 37,654 | **99.76 %** | 70 % | FAILS |
| `docs/downloads/gems-karage1-geothermal-conduit-offcat-20261031T000000Z-a1b2c3d4-zeros.tif` | 20,000 | **99.87 %** | 70 % | FAILS |

Measured here against `registry/13GEMSDOE_r13-lattice-s5_v2_nan-outside.tif` only. Those sessions' own audits compared against
the nine focus files (0.0 overlap for the off-catalogue geophysics file). Their run card for the conduit file already says
`ok_to_submit: false`. Neither file is cleared. Their full listed-site receipt has not been run.

## 8. Remaining work and limitations

1. **No file is OK to submit.** Applies to KP1 and to the two `main` candidates above. Path to a unique candidate: emit dots that avoid the 3-px neighbourhood of every listed-site dot
   (2,473 unique GeoTIFFs in 107 repositories). That is the rule as written. Do not jitter dots to get past it (the repo forbids this).
   Then re-run the holdout and the cross-site check before any slot is considered. This needs a new hypothesis, not a re-run.
2. **Score estimate.** No organizer receipt exists for any file. Estimated leaderboard scores are NOT ESTIMABLE.
3. **Uniqueness coverage.** Checked against 113 listed repos (107 with TIFs in the repo tree). The 6 empty repos are not checked.
   GitHub Pages sites are not on the allowed-host list, so only repository contents were compared. Files attached to
   GitHub Releases were not checked.
4. **Dense-raster exclusion** (91 files) is a judgment: any dot is within 3 px of a dense field. Recorded, not hidden.
5. **Eligibility and disclosure.** Individual competitors must be U.S. citizens or permanent residents. The rules require
   generative-AI use to be disclosed in the narrative. The owner must confirm both before any submission.
6. **Single final selection.** Scoring uses one submission chosen for the final round. Selection is a separate owner step
   (not done here). Three submissions per week; the competition closes Dec. 3, 2026, 11:59 p.m. UTC.
7. **GitHub Pages visual design** was not redesigned in this session. The changes are verdict logic and copy.
8. **Figure 0.4413.** It appears in repo notes. It is absent from leaderboard ranks 1–47 (fetched). Not used here.

---

## 9. Re-run the checks (no human input)

```
.venv/bin/python scripts/verify_kp1_independent_20261031.py
.venv/bin/python scripts/fetch_listed_site_tifs.py          # needs gh auth; writes data/peers/ (git-ignored, ~3.5 GB)
.venv/bin/python scripts/uniqueness_vs_listed_sites_20261031.py
.venv/bin/python scripts/kp1_release_gate.py
.venv/bin/python scripts/build_site.py && .venv/bin/python scripts/build_kp1_site.py
```

## 10. Links for manual review

- Rules and format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Homepage (end date, prize): https://www.drivendata.org/competitions/306/competition-doe-gems/
- Official Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Repo receipts: `evidence/kp1_release_gate.json`, `evidence/kp1_independent_verification_20261031.json`,
  `evidence/kp1_uniqueness_vs_listed_sites_20261031.json`, `evidence/listed_sites_tif_inventory_20261031.json`,
  `evidence/kp1_exp3_comparison.json`, `evidence/kp1_exp2_holdout_rerun_20261031.json`, `evidence/nine_site_executive_20261031.json`.
