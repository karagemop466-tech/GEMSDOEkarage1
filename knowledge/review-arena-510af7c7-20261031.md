# Review — `arena/510af7c7-gemsdoekarage1` — 31 October 2026

**Verdict: NEGATIVE — DO NOT SUBMIT.** No new TIF was generated, no file is cleared for upload, and no weekly slot was selected or spent. Every number below is labelled: **ORGANIZER-PUBLIC** (fetched from an official DrivenData or NLR page on 31 Oct 2026), **HOLDOUT-DTI** (our proxy, with evaluator, withheld count, and 95% CI), **USER-REPORTED** (copied from the request, unverified), or **LOCAL-MEASURED** (computed from files in this repository).

---

## 1. Executive summary

**What to download:** nothing from this session. No file in this repository is cleared for DrivenData upload.

**Best historical reference:** GEMSDOE32 B2 (USER-REPORTED 0.2778). It is a **copy by construction**: its 37,654 dots are exactly GEMSDOE25's 44,090 dots minus 6,436 dots that lie within 2 px of the existing fault catalogue. Resubmitting it, or a subset of it, breaks the uniqueness rule.

**Why it is not a clear win:** we cannot measure what the organizer measures. The organizer tests on **new faults that are not in the catalogue** (ORGANIZER-PUBLIC, problem description). Our only holdout re-finds catalogue segments, and on that holdout B2 scores below random (HOLDOUT-DTI 0.0047 vs 0.0446 for random placement). The holdout therefore ranks the top public file last.

| File to download | Estimated leaderboard score | Unique versus the other GEMSDOE sites? | OK to submit? |
|---|---|---|---|
| GEMSDOE32 `h33-h33-2-b2` ([registry copy](../registry/GEMSDOE32_B2.tif), sha256 `c55bafc4…`) | **Not estimable.** USER-REPORTED 0.2778. Not an organizer receipt. The catalogue holdout gives HOLDOUT-DTI 0.00473 [0.00432, 0.00515] (16 cells, 45,260 withheld positives, evaluator `gems57-pooled-hide-v2`), which says nothing about the organizer's new-fault test. | **No.** Subset of GEMSDOE25 (6,436 dots removed); 3-px overlap with GEMSDOE24 = 100%. | **NO — DO NOT RESUBMIT** |
| GEMSDOE36 `anderson-geothermal-pinn` | Not estimable. USER-REPORTED 0.2750. | **No.** Dot Jaccard 0.969 with B2; 3-px overlap with GEMSDOE27 = 97.6%. | **NO** |
| GEMSDOE28 `h36-1-rung30-blind-r1` | Not estimable. USER-REPORTED 0.2710. | **No (protocol gate).** Dot Jaccard ≤ 0.56 to any other, but 100% of its dots lie within 3 px of GEMSDOE25/27/30 dots. | **NO** |
| GEMSDOE31 `h27-4-solo-d28` | Not estimable. USER-REPORTED 0.2708. | **No.** Dot Jaccard 0.937 with B2. | **NO** |
| GEMSDOE33 `h33d-analog-tip-stepover-r30` | Not estimable. USER-REPORTED 0.2632. | **No (protocol gate).** Dot Jaccard ≤ 0.70, but 99.7% of its dots lie within 3 px of GEMSDOE24/27/30 dots. | **NO** |
| GEMSDOE25 `d28` | Not estimable. USER-REPORTED 0.2600. | **No.** Identical dot set to GEMSDOE30. | **NO** |
| GEMSDOE30 `d28-poisson300m-offcat-44090` | Not estimable. USER-REPORTED 0.2600. | **No.** Identical dot set to GEMSDOE25 (different bytes). | **NO — duplicate of GEMSDOE25** |
| GEMSDOE27 `topo-gap-closure-t-v2-on-d1-5` | Not estimable. USER-REPORTED 0.2449. | **No.** Dot Jaccard 0.980 with GEMSDOE24. | **NO** |
| GEMSDOE24 `h25-1-dotted-h19-5-d1-5` | Not estimable. USER-REPORTED 0.2477. | **No.** Dot Jaccard 0.980 with GEMSDOE27. | **NO** |

Scope of "unique": only the nine focus rasters held in this repository. The authenticated full submission registry is not available here (see blockers).

**Leaderboard context (ORGANIZER-PUBLIC, fetched 31 Oct 2026):** #1 = **0.4544** (xiaofanhu, 35 submissions); #2 = 0.3925; **#50 = 0.3195** (kpomazi). **0.4413 is not in the top 50.** No focus site appears in the visible top 50, so every USER-REPORTED focus score is below 0.3195. The request's statement that "0.3195 is the highest score" is incorrect. See §6.

---

## 2. Why did GEMSDOE32 B2 (0.2778) score highest? — evidence and judgement

**Mechanism (LOCAL-MEASURED, reproducible in `scripts/offcat_mechanism_analysis.py`):**

1. B2 ⊂ GEMSDOE25 exactly. B2 has 37,654 dots, GEMSDOE25 has 44,090, and B2 adds no dot that GEMSDOE25 lacks.
2. The 6,436 dots removed from GEMSDOE25 **all** lie within 2 px of the USGS/INGENIOUS catalogue (100%; median distance 1 px). B2 is GEMSDOE25 with its catalogue-adjacent dots deleted.
3. Across the nine focus sites, the share of dots within 3 px of the catalogue ranks the USER-REPORTED scores almost perfectly: B2 5.77% (0.2778), GEMSDOE36 5.87% (0.2750), GEMSDOE28 11.62% (0.2710), GEMSDOE31 11.73% (0.2708), GEMSDOE33 14.39% (0.2632), GEMSDOE25 and GEMSDOE30 19.52% (0.2600), GEMSDOE24 19.87% (0.2477), GEMSDOE27 19.87% (0.2449). Spearman ρ = **0.983**, n = 9, p ≈ 2×10⁻⁶. This is an **association across nine unverified scores**, not proof of cause.

**Judgement (PhD-level reasoning, not a measured result):** The metric is a distance-weighted Tversky index with α = 0.2 and β = 0.8, and a 3-px triangular kernel (ORGANIZER-PUBLIC). A dot near a mapped trace earns true-positive credit only when a *new* fault lies within 3 px of it. Because the test faults are unmapped by definition, those dots mostly add false-positive mass, at weight α = 0.2 each. Deleting them lowers FP_w and costs little TP_w. That is the most plausible reason B2 beats its parent. The mechanism explains a gain of about 0.018 (0.2600 → 0.2778), which is consistent with a precision correction rather than a new discovery method.

**Named counter-mechanism:** the rules say existing fault data "may be misaligned" from the true surface fault (ORGANIZER-PUBLIC). A catalogue-adjacent dot can therefore be a true positive, and deleting it can cost TP. The 0.018 gap cannot separate these cases.

## 3. Can we score above 0.2778? — honest answer

- **Along the B2 line: no, not without breaking uniqueness.** Further deletions from B2 (for example, the 2,171 dots still within 3 px of the catalogue; all lie beyond 2 px, so their distances fall between about 2.2 and 3 px) produce a near-copy of B2. That fails the user's "do not copy" rule and the protocol's overlap gate. Whether it would score higher is unknown.
- **Across the focus family: no, the family is one geometry.** Every focus raster's dots lie almost entirely within 3 px of GEMSDOE24's dots (B2: 100%; GEMSDOE36: 97.6% to GEMSDOE27; GEMSDOE33: 99.7%). Random dots at matched counts overlap ~17% (LOCAL-MEASURED, 200 draws). Real co-location is therefore far above chance, but it is not identity.
- **Off the family: unproven.** A genuinely different placement would show ~17% overlap, so it can pass the gate. Nothing can be validated for it yet: the only available holdout inverts the public ranking (§4), and no lane or canonical template is assigned (§5).

## 4. Holdout reproduction (HOLDOUT-DTI, not organizer)

Shared evaluator `vendor/gems57` (`holdout.evaluate`, unmodified), 16 hide-and-recover cells (2 draws × 4 quadrants × 2 modes), 45,260 withheld positives, 95% CI = percentile bootstrap over cells. Receipt: [`evidence/exp_510af7c7_shared_holdout_reproduction_20261031.json`](../evidence/exp_510af7c7_shared_holdout_reproduction_20261031.json).

| Arm | HOLDOUT-DTI | 95% CI | Dots |
|---|---|---|---|
| GEMSDOE32 B2 (0.2778 USER-REPORTED) | 0.00473 | [0.00432, 0.00515] | 37,654 |
| GEMSDOE25 d28 (0.2600 USER-REPORTED) | 0.10227 | [0.09296, 0.11431] | 44,090 |
| Random placement, matched count, mean of 3 seeds | 0.04460 | per seed 0.0420–0.0464 | 37,654 |

- The B2 value matches the peer repository's stated 0.004515 (PEER-CLAIM, see §7) and the 30 Oct receipt (0.004729) to about 0.1%.
- **Inversion:** on the holdout, GEMSDOE25 > random > B2. The public board has B2 > GEMSDOE25. This is the leakage-canary pattern the protocol warns about in reverse: the holdout rewards re-finding mapped segments, and the organizer test rewards not re-finding them. **The holdout cannot rank candidates for this competition.** Leakage canary (AUC) was not rerun this session.

## 5. Candidate hypotheses — proposals only, not validated, not ranked by DTI

These extend §5 of [review 946f7668](review-arena-946f7668-20261031.md) and skip ideas already executed (BB-STEP, H-R1, CDA1, DIPDUAL). Every layer name is verified against `data/training_features.tif` band tags (LOCAL-MEASURED). The cost and novelty judgements are qualitative.

| Rank | Hypothesis | Layers (band index in training_features.tif) | Off-catalogue signature | Named non-fault mimic | Why it differs from B2 / the repo | Cost |
|---|---|---|---|---|---|---|
| 1 | **Seismic-alignment ridge**: co-located earthquake density (band 16) and distance-to-earthquake (band 10) lineaments that run parallel to strike of magnetic edges (bands 6, 3) | 16, 10, 6, 3 | Microseismicity on unmapped active faults, which the catalogue lacks | Induced seismicity from fluid injection or mining | New evidence source; new dot positions, so it can pass the 3-px gate | Low; resolution of band 16 (100 km radius) is coarse, which is the main risk |
| 2 | **Catalogue-complement ridge**: non-maximum-suppressed tilt-angle ridges (band 6) that are ≥ 3 px from the catalogue, spaced ≥ 3 px apart | 6, 3 | Magnetic edges with no mapped trace | Unfaulted lithologic contacts, dike margins | Built from new positions, not a removal from 25 | Low–medium |
| 3 | **Soft exclusion (graded, not binary)**: scale each dot's probability by a distance-to-catalogue term instead of deleting dots | any of the above | Tests whether B2's gain survives graded output | — | A variant of B2's mechanism; still derived from GEMSDOE25 positions, so it fails the 3-px gate | Very low, but blocked by uniqueness |

Rejected: BB-STEP (depth-to-basement step, band 15) — already run in this repository and blocked by the lattice gate (98.53% overlap). Strain-only ridges (bands 4, 7, 8) — already tested in the repository's strain lanes, with weak holdout results.

**Validation path (not run):** no candidate may be validated on the catalogue holdout (§4). The only valid feedback is organizer scoring on weekly slots, which needs an owner decision (§5 below).

## 6. Leaderboard and text corrections

- The request says "0.3195 is the highest score right now" and also "0.4413 is the current GEMSDOE high score". **Both are inconsistent with the public board.** #1 = 0.4544; 0.3195 is #50 (today's snapshot). 0.4413 does not appear in the top 50.
- The README and AGENTS.md said 0.3195 was rank #48. The 31 Oct snapshot shows #48 = 0.3231 and #50 = 0.3195. The README is updated in this session.

## 7. Official sources (line-by-line verification)

| Claim | Source | How verified (31 Oct 2026) |
|---|---|---|
| Metric: DTI with TP_w, FP_w, FN_w; α = 0.2, β = 0.8; triangular kernel, R = 3 px = 300 m | [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | fetched, "Mathematical representation" section |
| Format: EPSG 32611, 100 m, same bounds, NaN/null outside, single float32 band, values in [0, 1] | same page, "Submission format" | fetched |
| Training features: 19 bands at EPSG 32611, 100 m; band list | same page, "Provided features"; band descriptions match `data/training_features.tif` tags | fetched and checked against the file |
| Training labels are existing fault data from INGENIOUS | [NLR Official Rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), §3.3 and footnote 4 (INGENIOUS DOI [10.15121/1881483](https://doi.org/10.15121/1881483)) | fetched, §3.3 |
| Test set is newly labelled faults not in the USGS database | problem description, "Competition structure" | fetched |
| Up to 3 submissions per week; choose one final submission; two-round scoring | NLR rules §3.4, §3.5, §3.6.2; problem description | fetched |
| Leaderboard: #1 0.4544; #50 0.3195; no 0.4413 in top 50 | [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | fetched, all three pages |
| Reference solution: Tversky α = 0.2, β = 0.8; labels binarised `y < 1 → 0`; output written with label CRS and transform | [reference repo](https://github.com/drivendataorg/gems-prize-reference-solution) at commit `aebe92f` (16 Jun 2026) | cloned, `unet-mc-cv-reference-solution.ipynb` cells 1, 6, 16, 19 |
| Data restored from pinned public mirrors; hashes match manifest; **not organizer-authenticated** | `scripts/restore_karage1_data.py --group core`, `registry/data_manifest.json` | run; 4 files restored, sha256 `4371c82e…` (features), `7ba308cc…` (labels = existing faults), `2176d08e…` (sample) |
| EPSG:32611 definition | [epsg.io/32611](https://epsg.io/32611) | linked on the official page; **not independently fetched this session** |
| Data download page (login) | [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) | **not re-verified this session** |
| Peer claim: B2 scores 0.004515 on the peer's static evaluator | [buffedlizard55-lab/GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32) at `c8e560f`, `docs/index.html` | cloned; PEER-CLAIM, not an organizer receipt |

## 8. Software checks

- `.venv/bin/python -m pytest -q -rs` → **453 passed, 0 failed, 1 skipped** (after merging `main`) (the skip needs an ignored bridge raster that is still absent). Before the core data was restored: 446 passed, 2 skipped.
- `scripts/shared_tools.py preflight` → exit 1. Core data is linked through `.cache/gems_data`. Still missing: `.cache/gems_work/feature_stack.npy`. Vendored `submission_writer.py` and `uniqueness.py` fail their recorded SHA-256 pins. Lane is null. **Not ready for shared tools; no experiment was authorized.**
- `scripts/validate_geotiff.py registry/GEMSDOE32_B2.tif --template data/sample_submission.tif` → single band, float32, CRS/shape/transform match the sample, no non-finite value inside the footprint, all inside values in [0, 1], outside NaN count 0. **Portal acceptance not tested.** This checks format only, not the submission's standing.

## 9. Irregularities flagged for review

1. **Missing method lane.** The request's parallel-run protocol says the lane is "the single method paragraph below". No such paragraph appears in the request. This is the same gap recorded in reviews 946f7668, 830e1f79, and cfabff7e.
2. **Leaderboard inconsistency in the request.** "0.3195 is the highest score" conflicts with #1 = 0.4544. "0.4413 is the current high" does not appear on the board.
3. **Duplicate score entries.** GEMSDOE25 and GEMSDOE30 have identical dot sets, and both are USER-REPORTED at 0.2600.
4. **labels.tif and existing_faults.tif are byte-identical** (sha256 `7ba308cc…`). This is consistent with the rules text (training labels = existing fault data). It is noted, not treated as a defect; the preflight warns "identity alone does not establish leakage."
5. **The 70%/3-px gate needs an owner decision.** Its 17% random baseline is for focus-site pairs. Against the 13GEMS lattice it fails 100% of random draws (`evidence/lattice_gate_null_check_20261029.json`), so it cannot distinguish a lattice-like raster from a non-lattice one. It is not an official rule.
6. **Hard-coded metadata in the calibration script.** `scripts/exp1_shared_holdout_calibration.py` writes date 2026-10-29 and session `arena/5ee7ef4b` into its receipt. This session re-ran it and saved the receipt under a new name. The original `evidence/exp1_shared_holdout_calibration_20261029.json` was restored from git after an accidental overwrite (no content change).
7. **Peer claims are not authoritative.** The GEMSDOE32 peer repo reports H51 "record" results and a "static re-check"; those figures are PEER-CLAIM only and are not reproduced here.

## 10. Blockers and recommended next steps

1. **Owner:** name the method lane (the missing paragraph) and the canonical shared template. Do not patch vendored writer or uniqueness modules privately.
2. **Owner:** decide the uniqueness rule. The literal 70%/3-px gate is informative for focus pairs (17% baseline) but blocks everything against the lattice. Specify which reference set it applies to.
3. **Data:** obtain organizer-authenticated copies of the four core files from the DrivenData data tab (login required). Hash-matched mirrors are not provenance.
4. **Feature stack:** build `.cache/gems_work/feature_stack.npy` only after items 1 and 3, with the template's builder unmodified.
5. **Holdout:** the catalogue holdout inverts the public ranking. Either design an off-catalogue validation that the organizer's data cannot contradict, or treat weekly slots as the only feedback and budget them under the 3-per-week cap.
6. **Owner:** decide whether to spend a weekly slot on a new candidate in the next session. None is recommended from this review.

---

Run card: [`evidence/run_card_arena_510af7c7_20261031.json`](../evidence/run_card_arena_510af7c7_20261031.json) · Mechanism receipt: [`evidence/offcat_mechanism_510af7c7_20261031.json`](../evidence/offcat_mechanism_510af7c7_20261031.json) · Reproduction receipt: [`evidence/exp_510af7c7_shared_holdout_reproduction_20261031.json`](../evidence/exp_510af7c7_shared_holdout_reproduction_20261031.json).
