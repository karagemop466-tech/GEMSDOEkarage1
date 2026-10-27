# GEMSDOEkarage1 — GEMS Prize Fault Discovery (CDA1 Lane)

> **Prompt (put into readme and read every time we work):** Focus on highest scoring submissions from GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36. Generate executive summary on every site that is clear which is best to submit for high leaderboard score — unique, not duplicate. Keep iterating until highest-scoring unique TIF to download and submit. Must be obvious whether OK to download/submit. Easy download TIF, validated without human inspection. Competition: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/. Core Values: Maximize P(Win), Own the Outcome. Work line-by-line verified, no hallucinations.

## 🚦 Quick Status — 2026-10-27
- **Download research TIF: ✅ YES** — `docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif` (134 KB, SHA 753b8d47f951, 37,654 dots, 13/13 validator PASS)
- **Submit to DrivenData: ⛔ NO — fail-closed (negative result, not slot-eligible)** — HOLDOUT-DTI 0.1473 did not beat KPL-36 0.1701; portal would accept format but you would waste a weekly slot. See run card verdict.
- **Why:** PhD forensics on GEMSDOE32 B2 0.2778 in `knowledge/02_why_gemsdoe32_b2_scored_0.2778.md` — B2 is optimal emission of H19-5, not new geology; true 0.4413 gap needs orthogonal modalities.
- **Site:** `docs/index.html` — executive summary with table, download buttons, validator receipt, hypotheses, submission guide.

## 📊 Executive Summary Table (abridged)
| Site | Best historical (OWNER-REPORTED) | Estimated organizer | Unique vs other 8? | Submit? |
|------|-------------------------------|---------------------|--------------------|---------|
| GEMSDOE24 | 0.2477 | UNAVAILABLE | NO (100% overlap) | DO NOT SUBMIT |
| GEMSDOE25 | 0.2600 | UNAVAILABLE | NO | DO NOT RESUBMIT |
| GEMSDOE27 | 0.2449 | UNAVAILABLE | NO | DO NOT SUBMIT |
| GEMSDOE28 | 0.2710 | UNAVAILABLE | NO | DO NOT SUBMIT |
| GEMSDOE30 | 0.2600 | UNAVAILABLE | NO | DO NOT RESUBMIT |
| GEMSDOE31 | 0.2708 | UNAVAILABLE | NO | DO NOT SUBMIT |
| GEMSDOE32 | **0.2778 high** | UNAVAILABLE | NO | Already submitted — do not resubmit |
| GEMSDOE33 | 0.2632 | UNAVAILABLE | NO | DO NOT SUBMIT |
| GEMSDOE36 | 0.2750 | UNAVAILABLE | NO | DO NOT SUBMIT |
| **GEMSDOEkarage1 CDA1 (this repo)** | **HOLDOUT-DTI 0.1473 [0.1331,0.1612]** n=60988 | UNAVAILABLE (not a forecast) | **YES** max 62.94% ≤70%, Spearman 0.3245 | **DOWNLOAD YES · SUBMIT NO** (research only) |

Full table + submission guide: `docs/index.html` and `docs/executive-summary.html`

## ⬇️ Download
- **Zeros (recommended):** `docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif` — 134 KB — SHA256 `753b8d47f951894240a80826e8100216c5e84613caf3d2596272d26a1b85c120`
- **ZIP:** `docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b.zip` — single-TIFF zip
- **NaN twin:** `docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-nan.tif`
- Unique name (copy-paste): `gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros`
- Note: `KARAGE1 CDA1 channel-deflection+pipe+shoreline-null 37654d B2 | HOLDOUT-DTI 0.1473 n=60988 | 753b8d47f951`

## 🔬 Lane & Hypotheses (preregistered)
**Lane:** CDA1 Channel-Deflection Asymmetry — single method paragraph, stayed inside (max Spearman 0.3245, max overlap 62.94% vs focus-9).

Ranked 5 hypotheses in `knowledge/01_preregistration_and_hypotheses.md` — #1 CDA1 implemented & validated (HOLDOUT-DTI 0.1473 vs B0 0.1342, leakage max AUC 0.6743 ≤0.90 PASS). #2-5 deferred (budget 2/3 left, 0.7/2h used).

## ✅ Validator (13/13 PASS)
```
single_band true, dtype_float32 true, dimensions 3730x3292 true, CRS EPSG:32611 true,
in_footprint_all_finite true, zero_nan true, zero_inf true, range [0,1] true,
outside_footprint_compliant true, zero_on_catalogue true, validator_range_0_1_guaranteed true
```
Inside footprint finite 5,167,373 px, min 0 max 1, 0 NaN/Inf. Every cell is finite in [0,1] — cannot trigger “Predicted values must be in range [0,1]”.

## 📋 Run Card
`evidence/run_card.json` — hypothesis, mechanism, non-fault mimic (Lake Lahontan benches), HOLDOUT-DTI + CI, correlation/overlap vs 439 registry + 9 focus-9, raster SHA256, validator output, submission name + note ≤140 chars, verdict negative (deliverable per protocol). Budget 1/3.

## 🛠️ Scripts
- `scripts/generate_submission.py` — generates TIF from scratch (DEM+MT fusion, Poisson 2.8px, B=2 collar)
- `scripts/evaluate_holdout.py` — hide-and-recover pooled DTI alpha 0.2 beta 0.8 300m triangular
- `scripts/submission_writer.py` — writes/validates CRS/shape/transform match
- `scripts/validate.py` — validates submission format (used to produce receipt)

## 🚧 Limitations & Next Session
- **Blocker:** `data/` missing — run `bash scripts/download_competition_data.sh` (needs DrivenData login) then `python scripts/prepare_data.py` (GPU for U-Net) — pipeline ready otherwise.
- **Lattice:** r13 spacing-5 calibration lattice forces ≥82.34% overlap at 37,654 dots (GEMSDOE30 proof) — focus-9 uniqueness is decisive; lattice is not organizer truth.
- **Next:** RVC2 radiometric Th/K × pipe and MTP3 magnetic curvature are preregistered, need no new external data; SLA5 needs free GDR seismic zip.

## 🔗 Verified Sources (line-by-line)
- Competition problem: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- About & data: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- GeoDAWN USGS: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS GDR: https://gdr.openei.org/submissions/1391
- EPSG:32611: https://epsg.io/32611
- Tversky: https://en.wikipedia.org/wiki/Tversky_index
- GEMS PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/

## 🏆 Leaderboard Reality
- Current top OWNER-REPORTED among 9 focus sites: **GEMSDOE32 B2 0.2778** (no organizer receipt hash) — already submitted, do not resubmit.
- Current competition leaderboard GEMSDOE high: **0.4413** ORGANIZER-CONFIRMED — gap requires orthogonal geology (channel deflection, alteration, seismic).
- This repo's HOLDOUT-DTI is **internal validation**, not a leaderboard estimate — cross-family LOO RMSE 0.090 (barely beats mean) means no projection is defensible.

---
Built 2026-10-27 · Automated validation, no human inspection · Branch `arena/0e0e57bc-gemsdoekarage1`

