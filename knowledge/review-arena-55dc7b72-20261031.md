# Session review — `arena/55dc7b72-gemsdoekarage1` (31 Oct 2026)

**Verdict: NEGATIVE — DO NOT SUBMIT. No file is cleared for download and upload. No weekly slot was selected or spent.**

Labels used throughout: **HOLDOUT-DTI** (our evaluator, withheld catalogue positives, 95% CI), **ORGANIZER-CONFIRMED** (from an organizer statement or a submission receipt), **ORGANIZER-PUBLIC** (public leaderboard read, not a receipt), **USER-REPORTED** (from the request, unverified), **LOCAL MEASUREMENT** (computed here on SHA-pinned mirror bytes). No projection is written as a score.

Executive page: [`docs/executive-summary-20261031.html`](../docs/executive-summary-20261031.html) · table data: [`evidence/nine_site_table_20261031.json`](../evidence/nine_site_table_20261031.json) · run card: [`evidence/run_card_arena_55dc7b72_20261031.json`](../evidence/run_card_arena_55dc7b72_20261031.json).

---

## 1. Per-site summary (nine focus sites)

Scores are USER-REPORTED. No file has an estimated leaderboard score: there is no organizer receipt for any of them, and our holdout measures a different target, so "not estimable" is the honest entry. "OK to download & submit?" is **NO** for all nine.

| Site | Highest listed file (as named in the request) | Score (USER-REPORTED) | Dots (LOCAL) | Uniqueness vs other focus sites (literal 3-px/70% gate, LOCAL) | Lattice gate (LOCAL) | Download & submit? |
|---|---|---|---|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 | 60,069 | Duplicate of 8/8 other sites (fwd 0.88–1.00) | trips (fwd 0.999) | **NO** |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 | 44,090 | Duplicate of 8/8; **dot-identical to GEMSDOE30** | trips | **NO** |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 | 61,328 | Duplicate of 8/8; Spearman 0.990 vs GEMSDOE24 | trips | **NO** |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 | 37,660 | Duplicate of 8/8 (fwd 0.955–1.00) | trips | **NO** |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 | 44,090 | Duplicate of 8/8; **dot-identical to GEMSDOE25** (Spearman 1.000) | trips | **NO** |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 | 40,199 | Duplicate of 8/8; dot-identical to scored `gems28-h27-4-r1-solo-d2-8` | trips | **NO** |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` (B2) | 0.2778 | 37,654 | Duplicate of 8/8 (fwd ≈1.00); B2 is a strict subset of 25, 30, 31, 36 | trips | **NO** (already submitted; resubmission is a copy) |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 | 41,865 | Duplicate of 8/8 (fwd 0.93–1.00) | trips | **NO** |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 | 38,854 | Duplicate of 8/8 (fwd 0.97–0.98) | trips | **NO** |

**Important finding on uniqueness.** Under the literal rule (forward 3-px overlap > 0.70 *or* |Spearman| > 0.90), the nine focus files are **mutually duplicates for almost every pair**. The rule was applied in both pair directions by `scripts/audit_nine_sites_20261031.py`. The lattice gate (13GEMS, 99.9% forward overlap) trips for every site file. Under the same rule, the new candidate in §2 is *unique* against all nine focus files; the difference is that it is dense and not a near-copy of them.

**Per-file numbers reported:** all nine values are USER-REPORTED. The user's leaderboard figures (0.4413, 0.3195) are also unverified. See §5.

---

## 2. New TIF — generated, validated, and NOT cleared

- **File:** `docs/downloads/DO-NOT-SUBMIT_karage1-catexcl-halo-r3-t0.292-20261031T010556Z-zeros.tif`
- **sha256:** `dd5d18d06c9a368d3c1aa5c14ef729547ba110e487d7363ec5717e182c0d3727` (3,132,516 bytes)
- **Method:** catalogue-free LightGBM (25 features) trained on all catalogue labels, then the holdout-best configuration (3-px halo, threshold 0.292232) applied as preregistered. Output is continuous in [0, 1]; 557,271 positive cells; float32; EPSG:32611; training shape 3730×3292 and transform.
- **Format checks (LOCAL, independent script `scripts/validate_candidate_20261031.py`):** single band, float32, EPSG:32611, shape and transform match the training grid, no NaN, values in [0, 1], zero outside footprint, dots present. **All pass.**
- **Uniqueness (LOCAL):** unique vs all nine focus files (forward 0.30–0.34, Spearman 0.035–0.043). **Fails the literal lattice gate** (13GEMS forward 0.996; the 13GEMS lattice is a scored mirror raster). This gate is non-discriminating (prior `evidence/lattice_gate_null_check_20261029.json` shows random dots also fail), and it is reported as a gate defect. It was not worked around by jittering or renaming.
- **Holdout (HOLDOUT-DTI, E2 config):** DTI **0.0869**, 95% CI ≈ [0.0699, 0.1051] (16-cell bootstrap, approximate), withheld positives 60,594. **Density-matched random control: 0.1902 ± 0.0272** (20 seeds). The candidate is **below** random by 0.10. The holdout config was selected on the same holdout (in-sample), so the 0.0869 is optimistic.
- **Why it is not cleared:** (a) it fails the literal lattice gate, (b) its holdout DTI is below a density-matched random control, (c) the protocol forbids promotion without a positive holdout margin, and (d) there is no receipt for any score.

**Answer to "is it OK to download and submit?": NO.** The file exists so the question can be checked by inspection, not so it can be uploaded.

Saved-byte receipt: `evidence/audit_catexcl_candidate_20261031.json` (schema `karage1-local-tif-audit-v1`). It records that the **shared vendored gems57 validators were not run**: the shared data stack is absent and the vendor provenance pins mismatch. The receipt is from the independent checks only.

---

## 3. Why GEMSDOE32 B2 (USER-REPORTED 0.2778) scored highest, and whether we can beat 0.3195

**What is measured (LOCAL):**
- B2 = GEMSDOE25 minus exactly the **6,436** dots within 2 px of the USGS/INGENIOUS catalogue; B2 adds no dots. B2 has 0 dots within 2 px of the catalogue and 2,171 within 3 px.
- Organizer rule (ORGANIZER-CONFIRMED, forum topic 11516, chrisk-dd, DrivenData Staff, 16 Sep 2026): known USGS/INGENIOUS fault pixels are masked and do not count toward penalty terms; re-evaluation masks existing faults too.

**Mechanism (structural, reasoning from the rule and the measurements):** a dot one or two pixels from a mapped trace is *not* on a masked pixel, so it counts as a false positive unless an active truth lies within the 3-px kernel. Removing the halo therefore reduces false positives without removing true positives that sit on active faults. This is consistent with the user's reported gain (+0.0178 over GEMSDOE25) but is **not** proven: the score is USER-REPORTED, and no receipt exists.

**Why our holdout cannot test this (important):** in the HOLDOUT-DTI proxy, the withheld catalogue segments *are* the active truth. A halo dot next to a withheld segment is therefore a **hit** in the proxy, but would be a false positive under the organizer rule, where the catalogue is masked. Consistent with that, the halo grid barely moves the proxy DTI (r=0: 0.08670; r=3: 0.08689; r=6: 0.08662). This is a limitation of the proxy, not a refutation of the halo mechanism. `tests/test_session_55dc7b72.py` records this.

**Can we beat 0.3195?** **Not demonstrated.** The best catalogue-free model has holdout AUC 0.6335 and is below random at every tested count ≥ 10,000 dots (sparse-N control, §4). The only positive margin is +0.0020 at N=5,000, which is about three random SDs but too small to act on. Beating 0.3195 would need an off-catalogue validation signal we do not have.

**Levers that could in principle move the score (none validated here):**
1. A halo-aware submission built on a positive-margin model (e.g. B2-style halo trimming applied to a model that beats random). Needs a positive-margin model first.
2. An off-catalogue truth set to validate any halo or new-fault claim (see §6, remaining work).

---

## 4. Experiments and controls (budget: 3 experiments; E2 was run twice, the second run only to add controls)

| Step | What | Result (label) | Artifact |
|---|---|---|---|
| E1 canary | Single-feature direction-free AUC, all 25 features | max 0.592 (`geod_shearrate`); ceiling 0.90; stop **not** triggered | `evidence/catexcl_e1_canary_20261031.json` |
| E2 holdout | Hide-and-recover on catalogue segments, 4 quadrants pooled, `gems57.metric.dti_exact` with organizer masking | best r=3, t=0.292: **HOLDOUT-DTI 0.0869** [≈0.070, 0.105]; random-matched **0.1902 ± 0.0272**; model AUC 0.6335 | `evidence/catexcl_e2_holdout_20261031.json` |
| E2 sparse-N | Model top-N active vs random active, DTI | N=5,000: +0.0020 (≈3 SD, marginal); N=10,000: −0.0023; N=20,000: −0.0101; N=37,652: −0.0263; N=60,000: −0.0471; N=100,000: −0.0739; N=300,000: −0.1081 | same |
| E3 build | Apply E2 config to all labels | 557,271-dot candidate (§2) | `evidence/catexcl_e3_build_20261031.json` |

Caveats recorded in the JSON: the holdout targets catalogue segments, not organizer new faults; the halo and threshold are selected on the same holdout; quadrant-boundary effects on the 3-px kernel are ignored; the 95% CI uses 16 spatial cells and is approximate. The method lane is **unassigned** in `registry/template.json` (method_lane null); "catalogue-free LightGBM" is a **proposal for the owner to confirm**.

---

## 5. Leaderboard context (ORGANIZER-PUBLIC, not receipts)

- Live read, 31 Oct 2026: #1 xiaofanhu **0.4544**; #2 cfld__ **0.3925**; #3 Batik Shirt Brothers **0.3917**; #4 BrandenKMurray 0.3860; #5 op01 0.3642 (`fetch_page` of the leaderboard, chunk 0 of 3).
- The 30 Oct snapshot (`registry/leaderboard_snapshot_20261030.json`) recorded #2 as 0.3916, and #48 as 0.3195. The live #2 differs slightly (0.3925), so the snapshot is stale. **I did not re-read chunks 1–2 this session, so rank #48 = 0.3195 and the absence of 0.4413 from the top 50 are NOT re-verified today.** Treat them as USER-REPORTED / 30 Oct snapshot.

---

## 6. Hypotheses (3–5) and status

None has a validated score. "Validated" means HOLDOUT-DTI above a density-matched random control with a positive margin. Ranking is by testability, not expected score.

1. **H-K1-CATEXCL (implemented, FAILED):** catalogue-free LightGBM on 25 features. Holdout below random (§4). Do not retry without a new feature or a different design.
2. **H4 — directional strain-transition segmentation (geod_shearrate / geod_dilaterate).** Mechanism: fault zones concentrate shear-strain transitions. Mimic: fold hinges and lithologic contacts with strain gradients. Status: untested. Overlaps the failed 25-feature set, so it needs a distinct feature combination.
3. **H3 — stratigraphic-boundary termination (cond_surf, depth_to_base_surf edge termination).** Mechanism: faults terminate against or offset stratigraphic boundaries. Mimic: unconformities and lithologic contacts. Status: untested.
4. **H2 — multi-scale curvature-polarity continuity (curv_s1/s2, ridge_s1–s3, relief5).** Mechanism: fault traces are continuous across scales with consistent curvature sign. Mimic: topographic ridge lines and erosion gullies. Status: untested; curvature features are inside the failed set.
5. **H1 — cross-field boundary displacement (tmi_hg vs iso_grav_anom, depth_to_base_surf gradient).** Mechanism: offsets in magnetic and gravity anomaly boundaries. Mimic: intrusive contacts and basin-edge gradients. Status: untested.

**Recommended first validation:** H4, with a density-matched random control and the same E2 holdout, and a feature set that excludes the 25 used in E2. **Blocker:** a holdout that measures off-catalogue truth (needed to test halo and new-fault claims) is not available in this checkout. Requesting a suitable validation set would require owner or organizer input.

---

## 7. Irregularities flagged

1. **Uniqueness failure among focus sites:** most focus pairs are duplicates under the literal rule (§1). This affects the "unique vs other listed sites" requirement for nearly every site.
2. **GEMSDOE25 = GEMSDOE30 (dot-identical, Spearman 1.000)** although the files are byte-different.
3. **GEMSDOE31 = scored `gems28-h27-4` (dot-identical).** Two different site labels share one dot set.
4. **B2 is a strict subset of 25, 30, 31, and 36** (LOCAL).
5. **Sample mirror:** `data/sample_submission.tif` has 60,988 positive cells, equal to the catalogue count, while the official sample text describes a total absence prediction. Verify against the organizer's sample.
6. **`labels.tif` and `existing_faults.tif` are byte-identical** in the mirror. Verify against organizer provenance.
7. **Footprint mismatch:** sample NaN mask 5,167,373 cells vs feature-valid 5,165,852 (1,521 cells differ).
8. **Lattice gate non-discriminating:** random dots also fail (`evidence/lattice_gate_null_check_20261029.json`). Reported as a gate defect for the owner.
9. **Vendor provenance:** the shared writer and uniqueness hashes mismatch their pins (`vendor/PROVENANCE.json`). The shared validators were not run for this session's receipts.
10. **Leaderboard snapshot staleness:** the live #2 (0.3925) differs from the snapshot (0.3916).
11. **Historical rasters** in `data/scored/` and `docs/downloads/` include retracted or unverified items (see README archive list). Do not use them as submissions.

---

## 8. Official links for manual review

- Problem, metric, submission format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Organizer masking answer (ORGANIZER-CONFIRMED): https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Public leaderboard (ORGANIZER-PUBLIC): https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Official rules (PDF): https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution (commit aebe92f): https://github.com/drivendataorg/gems-prize-reference-solution

Sources cited but not fetched this session: USGS GeoDAWN, gbcge.org INGENIOUS, epsg.io/32611.

---

## 9. Verification

- `pytest` (full, final run): **453 passed, 0 failed, 1 skipped**; the skip needs absent competition rasters. Software verification only; not model validation. This session's regression tests are in `tests/test_session_55dc7b72.py`.
- Preflight of the shared tools was not run to completion: its shared stack and data are absent, and the vendor pins mismatch (see item 9 above).
- Official-formula tests (`tests/test_official_dti_formula.py`) are included in the full run.

---

## 10. Remaining work and limitations

1. **Owner decisions:** confirm or replace the method lane (`registry/template.json`, method_lane null); decide whether to treat the lattice gate as a defect; decide whether to produce further candidates.
2. **Validation gap:** no off-catalogue holdout. Until one exists, halo and new-fault effects are untestable and B2's mechanism remains unverified.
3. **Next experiment:** H4 with a density-matched random control and a non-overlapping feature set, if the owner confirms the lane. Budget: the 3-experiment budget is used (E1, E2, E3).
4. **Organizer receipts:** none exist for any file here. Estimated scores stay "not estimable" until a submission receipt exists.
5. **Standing prompt:** the verbatim user prompt was not saved in this checkout. The README carries the normalized brief (`docs/standing-prompt.md`). Newer explicit instructions take precedence.
6. **Limitations of this review:** LOCAL measurements rely on SHA-pinned mirror bytes that are not organizer-authenticated. The holdout is a proxy. The CI is approximate. Holdout config was selected in-sample. The live leaderboard was read only for chunk 0.
