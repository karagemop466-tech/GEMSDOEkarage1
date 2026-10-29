# Session review — `arena/547a9b56-gemsdoekarage1` (2026-10-29)

**Verdict: NEGATIVE / DO NOT SUBMIT. No file is cleared for upload.**

This session did three things that earlier sessions could not: it restored the core competition inputs from pinned mirrors, verified their hashes, and ran the repo's own preflight and tests. None of that produces a new candidate. No geological experiment was run, no HOLDOUT-DTI value exists, and no weekly slot was used.

## 1. What changed in this session

| Item | Result | Label |
|---|---|---|
| Core inputs restored with `scripts/restore_data.py --group core` | 4 files restored; every SHA-256 matched its pin (`training_features`, `labels`, `existing_faults`, `sample_submission`) | Mirror pins only; **not organizer-authenticated** |
| Core-data verification script (`scripts/verify_core_data_20261029.py`) | Evidence in [`evidence/core_data_verification_20261029.json`](../evidence/core_data_verification_20261029.json) | DATA-INTEGRITY CHECK |
| Test suite (`.venv`, Python 3.11, rasterio, lightgbm installed) | **373 passed**, 119 warnings (the prior README reported 365 in an earlier environment) | Software verification only; not a model result |
| Preflight (`scripts/preflight.py`) | `verdict: negative`, `ok_to_submit: false`, 0 geological experiments | Negative |

The sandbox does not reach DrivenData. The restored files come from GitHub mirrors (allowed host), so the organizer's login-walled data was **not** downloaded.

## 2. Official facts re-verified this session (no hallucination; links for review)

- Metric and submission rules, [DrivenData problem page, page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/). Fetched 29 Oct 2026. The page states: "a single layer with datatype of 32-bit float (`float32`) with values between 0 and 1"; "data outside the bounds is null or nan"; EPSG 32611; 100 m; α = 0.2, β = 0.8, R = 300 m (3 pixels).
- The same page's sample description: "A sample submission that predicts total fault absence is provided for your reference on the data download page." **This conflicts with the restored mirror (see §4).**
- The page's "Competition structure" says the Initial Prize Round scores against a *private* set labelled before the competition, and the Final Round re-scores against an expanded label set after expert review of all submissions. A team selects one submission for both rounds.
- Leaderboard, [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), fetched 29 Oct 2026: **#1 xiaofanhu 0.4544; #2 cfld__ 0.3916; #3 Batik Shirt Brothers 0.3911.** This session's fetch covered only the top ranks. The `0.4413` and `0.3195` figures in the prompt were **not** re-checked here; prior reviews reported them absent or near rank 47 respectively. Treat those as USER-REPORTED.
- Official rules PDF: [NLR 96647](https://docs.nlr.gov/docs/fy26osti/96647.pdf) (linked from the README; the README records its contents as verified in earlier sessions; not re-fetched here).

## 3. Why no candidate is cleared

1. **No assigned method lane.** The prompt says "Your lane is the single method paragraph below", but no such paragraph appears in the prompt. The preflight records this as blocker #1. Inventing a lane would breach the protocol, so none was invented.
2. **Lattice gate.** The internal gate (≥ 70% of dots within 3 px of a registry raster) is not an official rule (the official rules do not contain it). The restored preflight still reports that a champion-sized (~37,654-dot) map has a minimum lattice overlap of 82.3% against the pinned witness, and every existing local raster fails it. The owner must decide whether this gate binds before any file can clear.
3. **No holdout run.** The shared evaluator and holdout pipeline exist under `vendor/gems57`, but there is no frozen comparable holdout best and no lane-assigned experiment. Running one now would have no protocol basis.
4. **Registry incomplete.** The preflight audits one lattice witness and nine historical rasters, not the full registry.

## 4. Irregularities flagged for owner review

1. **The mirrored `sample_submission.tif` is an answer key, not "total fault absence".** Its 60,988 pixels with value 1 coincide exactly with the 60,988 label-fault pixels (`labels.tif == 1`); none fall on background. The DrivenData page describes the sample as predicting total absence. Either the mirror was built from labels, or the page and mirror disagree. **Do not submit it or use it as a template for predictions.** The prior README already noted the same point for this mirror. This session confirms it at pixel level.
2. **Footprint mismatch.** Labels define the footprint as `labels != -1` (outside = −1, 7,111,787 px). The training-feature stack uses its own nodata `-3.4028234663852886e+38`. The two footprints disagree on **4,601 pixels** (`footprint_disagreement_label_vs_feature_band1`). Which footprint the organizer uses for "outside bounds" is not confirmed.
3. **Portal error "Predicted values must be in range [0, 1]" is still not reproduced.** Every local TIF in `docs/downloads/` is float32, single-band, EPSG:32611, shape 3730×3292, with all finite values inside [0, 1] (`values_outside_0_1 = 0` for every file). Two file conventions exist: "zeros" files with no nodata, and "nan" files with `nodata = NaN`. Neither produced out-of-range values. The portal's own parser or an undocumented nodata sentinel remains the most plausible cause, but this is unverified. Owner should attach the exact rejected file or its portal error receipt.
4. **Uniqueness label.** Prior sessions' "lattice duplicate" conclusions are reproduced by the pinned preflight only for the witness they used; this session did not run a new pairwise overlap audit.

## 5. Ranked next steps (for the owner, not executed here)

1. Owner decides whether the internal 70%/3-px gate binds submissions (it is not in the official rules). Until decided, no file clears regardless of science.
2. Owner supplies the actual assigned method paragraph (lane) in writing, or confirms there is no lane and this project proceeds only as research.
3. Owner provides the rejected TIF or portal receipt to close the range-error question.
4. Owner confirms what `sample_submission.tif` really is on the DrivenData download page (login needed). Until then, treat the mirror as label-derived.
5. Only after 1–3 are resolved: one pre-registered hide-and-recover experiment on the restored features, with a leakage canary, a 95% CI, and a separate weekly-slot selector.

## 6. Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install "rasterio>=1.3" "numpy>=1.26" "scipy>=1.11" "lightgbm>=4.0" "scikit-learn>=1.3" "scikit-image>=0.22" matplotlib pytest
.venv/bin/python scripts/restore_data.py --group core        # needs gh auth (github.com only)
.venv/bin/python scripts/verify_core_data_20261029.py         # writes evidence/core_data_verification_20261029.json
.venv/bin/python scripts/preflight.py                         # negative by design
.venv/bin/python -m pytest -q                                 # 373 passed
```

Run card: [`evidence/session_547a9b56_run_card.json`](../evidence/session_547a9b56_run_card.json).
