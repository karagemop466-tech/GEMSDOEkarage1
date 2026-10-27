# Executive Summary — GEMSDOE competition submission pipeline

**Repo:** `GEMSDOEkarage1`  |  **Branch:** `arena/83267592-gemsdoekarage1`  |  **Date:** 2026-10-27

**Purpose:** produce a *unique*, competition-valid single-band GeoTIFF submission for the DOE GEMS Prize Challenge (DrivenData competition 306) that can score above the current focus-site best (0.2778), with an obvious download path and an explicit **OK TO SUBMIT / DO NOT SUBMIT** status for every file.

> **No-hallucination rule:** every score below is labelled HOLDOUT-DTI (local evaluator), owner-reported/unverified, or "not estimable". No number is presented as an organizer-confirmed leaderboard score. The competition training rasters (`training_features.tif`, `labels.tif`, `sample_submission.tif`) require DrivenData login and could not be downloaded here, so no real holdout DTI or organizer-score estimate is computable in this session.

---

## 1. One-click submission (start here)

The competition requires a **single-band GeoTIFF (.tif)** (or a .zip containing one GeoTIFF) matching `sample_submission.tif` CRS / shape / geotransform, values in **[0, 1]**, no NaN inside the footprint.

### Download our generated unique submission

| | |
|---|---|
| **File to download** | [`docs/downloads/gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-zeros.tif`](downloads/gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-zeros.tif) |
| **Alternative (binary dots)** | [`docs/downloads/gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-dots.tif`](downloads/gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-dots.tif) |
| **Metadata / audit** | [`gemsdoe-unique-hunq1-...-zeros.tif.meta.json`](downloads/gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-zeros.tif.meta.json) |
| **SHA-256** | `642a6369a3a7e9a5c5761983e110c60a6abbc196abd339985e11da351d3e5c4b` |
| **Format** | Single-band float32 GeoTIFF, EPSG:32611, 3730 × 3292 (12,279,160 cells), values in [0, 1], finite, 0 NaN |
| **Estimated score** | **Not estimable** (no organizer receipt; no DrivenData labels) |
| **Unique vs focus-9 family?** | **Designed unique** (H-UNQ-1 does not re-thin H19-5), but **unverified** (no registry rasters available) |
| **OK TO DOWNLOAD?** | ✅ Yes (research / inspection) |
| **OK TO SUBMIT?** | ⛔ **NO** — placeholder geotransform; must be re-gridded to the real `sample_submission.tif` and pass holdout + uniqueness gates first |

**Submission name:** `gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b`

**Submission note (≤140 chars):**
`H-UNQ-1 radiometric-hydrothermal+fluvial-chi+gravity-margin off-catalogue fault detector | synthetic stand-in | DO NOT SUBMIT until re-gridded to sample_submission.tif and holdout-validated`

### How to make a submission into the contest

1. **Get the data** (DrivenData login required):
   - https://www.drivendata.org/competitions/306/competition-doe-gems/data/
   - Place `training_features.tif`, `labels.tif`, `sample_submission.tif` into `data/`
   - `bash scripts/download_competition_data.sh` documents this (no auto-download: verified login redirect).
2. **Prepare the stack:** `python scripts/prepare_data.py`
3. **Generate / align:** `python scripts/generate_submission.py`, then
   `python scripts/align_to_competition_grid.py --reference data/sample_submission.tif`
4. **Write + validate:** `python scripts/submission_writer.py --reference data/sample_submission.tif`
   → produces `<file>-audit.json` (format receipt).
5. **Run gates:** `python scripts/validate_submission.py` → verdict `promote` / `negative`.
6. **Upload** via the DrivenData submission page (single file, note ≤140 chars), within the weekly cap.

### Fix for `"Predicted values must be in range [0, 1]"`

This error means the GeoTIFF contains values outside [0, 1] or NaN. The pipeline guarantees:
- `np.clip(prediction, 0, 1)` and replace non-finite with `0` (the `-zeros` encoding),
- single-band float32, finite everywhere, no NaN inside the footprint.

The GEMSDOE research pages confirm the same 13/13 (or 20/20) format receipt: "0 NaNs anywhere, float32 in [0,1]".

---

## 2. Focus-site comparison (GEMSDOE 24 / 25 / 27 / 28 / 30 / 31 / 32 / 33 / 36)

All scores below are **owner-reported / unverified** (no organizer receipt linking raster hash to score). **None is unique** under the literal 70% within-3-px lattice rule, so **none may be re-submitted.** "Estimated leaderboard score" is **not estimable** for every site (no validated transfer from local holdout to the private organizer score).

| Site | Best historical submission file | Best score (owner-reported) | Best local holdout-DTI | Unique vs other focus sites? | OK to submit? |
|---|---|---:|---:|:---:|:---:|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-...` | 0.2477 | 0.1661 (S3DEP1) | ❌ No (100% within 3 px of GEMSDOE25) | ❌ No |
| GEMSDOE25 | `dotted-h19-5-d2-8-...` | 0.2600 | 0.12210 (H75 Exp3) | ❌ No (100% within 3 px of GEMSDOE24) | ❌ No |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-...` | 0.2449 | 0.04730 (h31) | ❌ No (98.02% within 3 px of GEMSDOE24) | ❌ No |
| GEMSDOE28 | `h36-1-rung30-blind-r1-...` | 0.2710 | 0.12018 (s22c) | ❌ No (100% within 3 px of GEMSDOE24) | ❌ No |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-...` | 0.2600 | 0.158162 (CSR-1) | ❌ No (100% within 3 px of GEMSDOE24) | ❌ No |
| GEMSDOE31 | `h27-4-solo-d28-...` | 0.2708 | 0.1661 (H31-X) | ❌ No (100% within 3 px of GEMSDOE24) | ❌ No |
| **GEMSDOE32** | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | **0.2778** ← 9-site high | 0.099202 (champion proxy) | ❌ No (100% within 3 px of GEMSDOE24; already submitted) | ❌ No (already submitted) |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-...` | 0.2632 | 0.10308 (fsml2-cc) | ❌ No (99.71% within 3 px of GEMSDOE24) | ❌ No |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-...` | 0.2750 | 0.194164 (TCD-36) | ❌ No (reg-052 lattice 99.35% > 70%) | ❌ No |

### Which is the best submission?

**Among the 9 focus sites, GEMSDOE32's `h33-h33-2-b2-...-zeros` at 0.2778 is the highest owner-reported historical score.** However:
- it is **already submitted** (re-submission spends a slot and adds no information),
- it is **not unique** (fails the 70% within-3-px lattice rule),
- it is **owner-reported / unverified** (no organizer receipt).

**Therefore no focus-site file is recommended for upload.** The only path to a higher score is a new, unique method that beats the holdout — see §3 and §4.

---

## 3. Why GEMSDOE32 scored 0.2778 (PhD synthesis) and how to beat it

**Metric:** DTI = Tversky index, α = 0.2, β = 0.8, 300 m triangular kernel. Because β (0.8) > α (0.2), false positives are penalised **4×** false negatives → sparse, confident dots beat dense maps.

**Why 0.2778:** every focus-9 leader re-thins the H19-5 ridge skeleton (0.1922 owner-reported):
- `d = 2.8` dotting cut false positives ~3× while preserving ~74% along-trace kernel bridge credit (+0.0678),
- `B2` excised 6,436 near-catalogue detector-echo dots at 0 < d_cat ≤ 2 px (+0.0178).

**Ceiling:** H19-5 covers only ~30–36% of hidden faults, so re-thinning it asymptotes below ~0.295.

**How to surpass 0.2778 toward public leaders (0.3195 / 0.4413 / 0.4437):**
1. close the 1 m LiDAR gap with 10 m 3DEP (24.63% gap),
2. detect blind range-front uplift via fluvial χ / ksn + hydrothermal upflow,
3. consolidate 2D halos via Stage-2 spatial context (measured Stage-2 gain +0.008895 [+0.0034, +0.0141]),
4. add off-catalogue 1:24k–1:100k pre-Quaternary bedrock faults + ASTER TIR alteration.

---

## 4. Our new hypothesis: H-UNQ-1 (unique, not an H19-5 re-thin)

| Element | H-UNQ-1 |
|---|---|
| **Layers** | fluvial chi anomaly (3DEP), GeoDAWN Th/K & eU/K alteration, gravity-margin edge; catalogue used only for a 2 px collar |
| **Signature** | hydrothermal alteration + gravity-margin edge + fluvial-chi knickzone (blind range-front fault) |
| **Catches off-catalogue faults?** Yes — blind/pre-Quaternary/hydrothermal-only faults absent from catalogue |
| **Differs from focus-9?** Yes — does not re-thin H19-5; radiometric-primary + fluvial-chi |
| **Expected DTI gain** | Planning bracket only (not a score); requires holdout validation |
| **Implementation cost** | Low (feature stack already cached in template) |

**Holdout DTI:** not computable (no labels.tif). Self-test PASS on synthetic faults.

**Verdict:** `negative` — cannot promote without DrivenData auth (no holdout, no uniqueness, no grid match). This is a deliberate negative result and a deliverable.

---

## 5. Submission gates (must all pass before upload)

| Gate | Requirement | H-UNQ-1 status |
|---|---|---|
| G1 | single-band float32, finite, values in [0, 1], no NaN | ✅ PASS |
| G2 | CRS / shape / transform == sample_submission.tif | ⚠️ UNVERIFIED (no sample_submission.tif) |
| G3 | holdout DTI beats current best, paired 95% CI > 0 | ⚠️ NOT COMPUTED |
| G4 | each feature alone AUC ≤ 0.90 (leakage canary) | ⚠️ NOT EVALUATED |
| G5 | \|Spearman\| ≤ 0.90 AND ≤ 70% dots within 3 px of every registry raster | ⚠️ NOT EVALUATED |
| G6 | within weekly slot cap; selector approval | ⚠️ NOT APPROVED |

**OK TO SUBMIT: NO** until G2–G6 pass. Download for research is OK.

---

## 6. Official verified sources

- DrivenData problem description: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- DrivenData about: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- DrivenData data (login required): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- DrivenData leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Submission rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- OpenEI GDR #1391 (INGENIOUS): https://gdr.openei.org/submissions/1391
- USGS 3DEP 10 m DEM: https://www.usgs.gov/3d-elevation-program
- USGS QFaults: https://www.usgs.gov/programs/earthquake-hazards/faults
- US Census TIGER/Line: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- EPSG:32611: https://epsg.io/32611

---

## 7. Run card

See `cards/run_card.json` (protocol rule 5): hypothesis, mechanism, named non-fault mimic, holdout DTI + CI, correlation/overlap vs registry, raster SHA-256, validator output, submission name + note (≤140 chars), verdict `promote` / `negative`.

**Current verdict: negative.**
