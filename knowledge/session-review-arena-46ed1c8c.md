# Session review · arena/46ed1c8c-gemsdoekarage1 · 31 Oct 2026

**Verdict: DO NOT SUBMIT (HOLD). Download for owner review: yes. Submit: no.**
Run card: [`evidence/session_46ed1c8c_run_card.json`](../evidence/session_46ed1c8c_run_card.json) ·
experiment: [`evidence/exp_h_e1_euler_20261031.json`](../evidence/exp_h_e1_euler_20261031.json) ·
pre-registration: [`knowledge/preregistration-he1-euler-20261031.md`](preregistration-he1-euler-20261031.md).

Labels used below: **HOLDOUT-DTI** (our hide-and-recover evaluator, `gems57-pooled-hide-v2`), **ORGANIZER-PUBLIC** (the public leaderboard page, not a receipt for our files), **USER-REPORTED** (scores supplied by the owner, unverified). No number here is a leaderboard estimate for our files.

---

## 1. Answers to the questions asked

| Question | Answer |
|---|---|
| Is there a unique, downloadable single-band GeoTIFF (EPSG:32611, values in [0,1])? | **Yes.** `docs/downloads/karage1-he1-euler-contact-si0-37654-20261031-zeros.tif` (primary, all-finite) and a `-nan.tif` diagnostic twin. Both are float32, single band, EPSG:32611, 3,730 × 3,292, 100 m, same transform as the sample. |
| Is it OK to download and submit? | **Download: yes, for owner review only. Submit: no.** The pre-registered decision rule returns **negative** because the literal 70 % dot-overlap criterion fails (§3). |
| Why did GEMSDOE32 `h33-h33-2-b2` score highest among the nine? | Best **explanation**, not a proof. B2 is GEMSDOE25's 44,090-dot mask with 6,436 dots removed, and every removed dot lies within 2 px of a mapped fault (verified line by line, §2). The official rules mask pixels on known faults, but not the collar next to them. Removing collar dots lowers false-positive exposure. Reported score: 0.2778 (USER-REPORTED) against 0.26 for its parent (USER-REPORTED). |
| Can a score above 0.2778 (or above 0.3195, rank #48) be reached? | **Not demonstrated.** Our holdout cannot measure it (§2.4). We have no organizer-confirmed score for any of our files. |
| Estimated score for each of the nine sites? | **Not estimable** for every site. The only numbers are USER-REPORTED. |
| Is each site's best file unique against the other listed sites? | **No.** The 29 Oct lineage audit (`evidence/site_lineage_verification_20261029.json`) gives every focus site at least **97.6 %** of its dots within 3 px of one sibling (GEMSDOE24 and 25 are at 100 %. GEMSDOE25 and 30 have identical masks, GEMSDOE28 and 31 share one, and GEMSDOE32 is a strict subset of GEMSDOE25). Our new H-E1 file is different: its worst overlap with any focus-site file is **0.202** (§3.2). |

## 2. GEMSDOE32 B2 (USER-REPORTED 0.2778)

### 2.1 Mask algebra (verified this session, read-only, on the pinned mirror)
- Footprint: 5,167,373 cells. Mapped catalogue inside the footprint: 60,988 positives.
- `B2 ⊂ GEMSDOE25_d28`: **true**. B2 has 37,654 dots; GEMSDOE25 and GEMSDOE30 have 44,090 dots each and an identical mask.
- Removed by B2 from GEMSDOE25: **6,436** dots. **All 6,436** lie within 2 px of a mapped fault; **3,891** lie within 1 px.
- B2 dots on a mapped fault: 0. B2 dots within 2 px of a mapped fault: 0.

### 2.2 Official scoring rule (verified)
DrivenData staff (forum thread 11516, staff reply by `chrisk-dd`; the fetched text does not show the year): *"Pixels corresponding to known USGS/INGENIOUS faults are masked / excluded from evaluation, so they do not count towards penalty terms."* Only the mapped pixels are masked. Dots on the collar, beside a mapped fault but off it, still count as false positives unless new truth lies within 300 m. Source: https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516

### 2.3 Metric arithmetic (vendored code, `vendor/gems57/metric.py` line 19)
DTI = TP / (TP + 0.2·FP + 0.8·FN). A false positive costs one fifth of a miss. The marginal rule in the same file (lines 44–49) implies a dot raises DTI only when its hit probability exceeds α·DTI. At DTI ≈ 0.278 that is about **0.056**. So removing the 6,436 collar dots improved B2 only if they had hit rates below about 5.6 %. That is consistent with the reported gain, but it is a prediction that the holdout cannot test (§2.4).

### 2.4 Why our holdout cannot rank B2
On the same HOLDOUT-DTI evaluator, B2 scores **0.00473** (pooled; mean of cells 0.00476, 95 % CI [0.00434, 0.00516]), the lowest of our controls, yet it is USER-REPORTED at 0.2778 publicly. The holdout's truth is the withheld *mapped* catalogue (`truth_is`), which B2 avoids by construction. So the holdout penalises catalogue-avoidance and cannot evaluate catalogue-derived submissions. Any holdout number for the nine sites' files would be misleading in the same way.

### 2.5 What would be needed to beat 0.2778 (not done)
- An organizer receipt for any file. None exists in the repo.
- A dot set whose hit probability on *new* faults exceeds about 0.056 where B2 has none, measured on a truth that excludes mapped faults. The holdout does not provide that.
- Public leaderboard context (ORGANIZER-PUBLIC, live read 31 Oct 2026): #1 xiaofanhu 0.4544; #2 cfld__ 0.3925; #3 Batik Shirt Brothers 0.3917; #4 BrandenKMurray 0.3860; #5 op01 0.3642; #6 No Fault of Our Own 0.3631. Ranks 7–50 were not read. The 30 Oct snapshot has #2 at 0.3916, so the live value drifted. 0.4413 is not in the top 50 (30 Oct snapshot). Source: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/

## 3. The H-E1 experiment (one run; budget 3 experiments / 2 hours; used 1)

Hypothesis: window Euler deconvolution (11 px window, Tz = official `tmi_vg`, structural index 0 primary, index 1 secondary) of the official TMI field identifies buried magnetic contacts that are off the mapped catalogue. Mechanism and non-fault mimics are in the pre-registration. Sources: Reid et al. (2013), Table 1, magnetic SI 0 for a contact of infinite depth extent (https://www.reid-geophys.co.uk/wp-content/uploads/2017/11/Reid-et-al-2013.pdf); Zhang et al. (2000) citing Thompson (1982) for the zero-index contact (https://www.reid-geophys.co.uk/wp-content/uploads/2017/11/Zhang-et-al-2000.pdf).

### 3.1 Results against the pre-registered rule (`DECISION_RULE`, fixed before the run)

| Criterion | Result | Pass? |
|---|---|---|
| Primary (SI 0) HOLDOUT-DTI > matched random null (mean of seeds 101, 202, 303) | **0.05071** vs **0.04460** | yes |
| Primary > non-Euler `tmi_hg` baseline | **0.05071** vs **0.04867** | yes |
| Paired 95 % CI (candidate − null, per-cell bootstrap) lower bound > 0 | mean difference 0.00579, **CI [0.00336, 0.00797]** | yes |
| Leakage canary: every single feature AUC < 0.90 | max direction-invariant AUC **0.581** (tmi_hg / horizontal gradient) | yes |
| Shared validator passes (zeros-outside primary) | all 14 checks pass | yes |
| Surface Spearman ≤ 0.90 vs every local TIF | max \|ρ\| **0.018** | yes |
| Final-dot 3 px overlap ≤ 0.70 vs every local TIF | max **1.000** (three covering rasters, §3.2) | **NO** |

Verdict: **negative** under the pre-registered rule. The holdout gain is real on this evaluator and sits about +0.006 above the random null, but the uniqueness criterion fails.

Holdout detail: 16 hide-and-recover cells, 45,260 withheld positives, evaluator `gems57-pooled-hide-v2`, truth = withheld mapped catalogue segments. The 95 % CI in the evidence belongs to the mean of the 16 per-cell DTIs (0.04975, CI [0.04591, 0.05339]). **No pooled-DTI CI exists in the evidence file.** The SI 1 secondary arm gives pooled 0.05049 (paired CI [0.00225, 0.00773]) and cannot promote alone.

### 3.2 Uniqueness: what fails and why
- The literal 70 % rule trips against **three** covering rasters, each with 100 % of our dots within 3 px: `13gems_20261001_r13-lattice-s5_v2` (206,895 positives), `karage1-halo-damagezone-d2p0` (5,106,385 positives), and `gemsdoe-unique-hunq1` (prototype, 3,943,064 positives inside the footprint).
- **Lattice:** 6,649 footprint cells lie more than 3 px from any lattice positive. A 37,654-dot set placed entirely there would still overlap at least **82.34 %**. A 70 % pass needs ≤ **22,163** dots. So the literal rule cannot be passed by a set of this size, whatever the method.
- **Halo and hunq1:** no footprint cell lies outside 3 px of their positives, so any dot set trips them.
- **Against dotted rasters only** (42 rasters with ≤ 100,000 positive cells): max overlap **0.287**, max \|ρ\| **0.004**. Against the nine focus-site dotted files: max overlap **0.202** (GEMSDOE27 topo-gap). This is the basis for the owner question in §6.

### 3.3 Other flags from the run
- 472 candidate dots fall on the visible (fold-local) catalogue. The official metric masks mapped-fault pixels, so they carry no penalty and no credit.
- Depth band 50–2,000 m is applied to solutions. The unit of `tmi_vg` is **not stated** in its band description, so the nT/m-per-metre scaling is an **unverified assumption**. Sign convention of `tmi_vg` was not tested. Sensitivity was not run (budget).
- `tmi_hg` is almost perfectly correlated with the gradient magnitude of `tmi` (correlation 0.999999997 in the run's unit diagnostic; not an exact equality), so the band identities are consistent.

## 4. Three passes

### Pass 1 · Implement
- `scripts/run_he1_euler_deconvolution.py` (runner), `scripts/make_he1_run_card_20261031.py` (run card; every number read from evidence or raster bytes), `scripts/render_site.py` (status banner, nine-site table, submission subpage), `tests/test_he1_euler.py`.
- Helpers imported from `scripts/run_h_r1_kth_magedge.py` (unchanged). The evaluator and grid modules are pin-matched. `vendor/gems57/submission_writer.py` and `uniqueness.py` are **not** pin-matched, so the runner does not use them. The literal gate is re-implemented.
- Inputs: `GEMS_DATA_DIR=/tmp/gems_data` (copy of `data/` and `scored/`, `external/`). The recorded SHA-256 values match the pins: training features `4371c82e…`, existing faults `7ba308cc…`, sample submission `2176d08e…`.

### Pass 2 · Adversarial review
| Attack | Outcome |
|---|---|
| The solver is wrong. | **Tested.** Synthetic point source, T = 1/r, N = 1. Accepted windows 100; max position error 0.07 px; depth 500.7–503.7 m against a true 500 m (`tests/test_he1_euler.py`). Chunked and unchunked runs agree. |
| The holdout gain comes from catalogue proximity. | **Not resolved.** 472 candidate dots on visible catalogue; the gain is about +0.006 with a CI that excludes zero, but the truth is still mapped faults. Stated as a limitation. |
| The literal gate is misimplemented. | **Partly checked.** The rule is simple and the implementation was verified on the blanket cases; the vendored `uniqueness.py` does not match its pin, so the re-implementation is not vendored code. Flagged. |
| The writer is wrong (pin mismatch). | **Avoided.** The runner uses `grid.write_submission`, which is pin-matched. Its signature `(path, values, *, mode)` was checked. |
| `tmi_vg` unit or sign changes the answer. | **Not tested.** Unit is unverified; a sign-flip or unit sensitivity was not run. Flagged as a limitation. |
| The uniqueness scan is incomplete. | **Partly resolved.** 52 rasters scanned, including prior research archives. The registry restore log for the `external/` group is not confirmed. |
| Holdout ranks the nine sites. | **No.** B2 scores 0.00473 on the holdout (§2.4). The holdout cannot rank them. |

### Pass 3 · Requirements verification
| Requirement | Status |
|---|---|
| Unique downloadable single-band GeoTIFF, EPSG:32611, values in [0,1] | **Done** (owner-review copy). Submit: HOLD. |
| Obvious answer on download and submit | **Done.** Banner on every page; submission subpage. |
| Explain why B2 scored highest | **Done** as an explanation with verified mask algebra and official masking rule; not proven. |
| Score above 0.2778 / 0.3195 reachable? | **Not established.** |
| Holdout validation before any weekly slot; labels HOLDOUT-DTI / ORGANIZER-CONFIRMED / USER-REPORTED | **Done** for H-E1 (negative). No file is slot-eligible. |
| Nine-site executive summary: best file, estimated score, uniqueness | **Done.** Estimate column: "not estimable" for every site. |
| Portal error "Predicted values must be in range [0, 1]" addressed | **Partly.** Verified: every finite value is in [0,1]; primary has no NaN. Not reproduced: the portal is unreachable. The earlier rejected file was not supplied. |
| Submission subpage: file, unique name, note | **Done** (`docs/submit-he1-20261031.html`). Note: 121 of 140 characters. |
| One JSON run card | **Done** (`evidence/session_46ed1c8c_run_card.json`). |
| Standing prompt and core values in README | **See the README section of this PR.** |
| PR and merge | **In progress.** |
| Tests | **Done.** 449 passed, 1 skipped (§8). |

## 5. Irregularities flagged (not resolved)
1. **Official format conflict.** Page 967 says outside-bounds cells should be null or NaN. The pinned writer (`vendor/gems57/grid.py`) says zeros is "the only submission-compatible mode" and NaN is for "local diagnostics only". The primary file uses zeros; the twin is diagnostic. **Owner ruling needed.**
2. **Missing official layer.** Page 967 lists a top-of-crustal magnetic source depth estimate and radiometric counts. The restored `training_features.tif` has **19 bands**, none of which is either layer (verified this session by band description).
3. **Sample submission text.** Official text says the sample predicts total absence. The mirror `sample_submission.tif` contains 60,988 ones, equal to the catalogue positive count (carried from prior verification).
4. **Mirror authenticity.** The data are restored from pinned third-party GitHub mirrors and checked by SHA-256 only. Organizer authenticity is **not established**.
5. **Vendored provenance.** `vendor/gems57/submission_writer.py` and `uniqueness.py` do not match their pins (`scripts/audit_template_integrity.py`). Not repinned without upstream review.
6. **Prototype raster outside footprint.** `archive/prototype/docs/downloads/gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-zeros.tif` has 9,390,049 positive cells, of which 5,446,985 lie outside the footprint (not a valid encoding). It is used here only as a covering raster.
7. **Leaderboard drift.** The live #2 is 0.3925 against 0.3916 in the 30 Oct snapshot.
8. **Forum year.** The fetched thread text shows "Sep 15/16/21" without a year. Date to be confirmed on the page.
9. **Preflight.** `scripts/shared_tools.py preflight` exits 1 (feature stack and cache absent). That is consistent with the restored data; this run did not use the retired feature stack.
10. **Quarantined scripts.** `generate_unique_submission.py`, `run_bbstep_experiments.py`, `build_unique_submission.py` remain quarantined and must not be re-enabled.

## 6. Owner decision required
**Should covering rasters (more than 100,000 positive cells) be in scope of the 70 % dot-overlap rule?**
- If **yes** (literal reading): no dot set of this size can pass it, so the verdict stays negative for every method. The rule then operates as a hard ban.
- If **no** (the rule applies to discrete submissions): the H-E1 candidate passes all six criteria (max overlap 0.287 against dotted rasters, max |ρ| 0.004). Only then is the file eligible for a slot selection, which is still a separate step.
No threshold was changed after seeing results. The decision is for the owner.

## 7. Hypotheses for the next session (ranked; none tested)
1. **H-E3 · Euler depth agreement with cover thickness.** Keep the H-E1 solutions whose depth agrees with `depth_to_base_surf`. Reuses the runner. Mimic: basement topography. Cost low. Overlap with H-E1: same method, new gate.
2. **H-S1 · Conductivity edge × shear coincidence.** Co-location of `cond_surf` edges with `geod_shearrate` ridges. Mimic: lake and playa boundaries, InSAR seams. **Overlap warning:** earlier notes call a conductive-shear idea "not clearly novel"; check before use.
3. **H-G3 · Gravity and magnetic edge coincidence.** `iso_grav_anom_hg` peaks co-located with `tmi_hg` ridges. Mimic: lithologic contacts. **Overlap not checked.**
All three need the same holdout, canary and literal-gate protocol before any slot.

## 8. Remaining work and limitations
- **Not done:** sign and unit sensitivity for `tmi_vg`; organizer-authenticated data; ranks 7–50 of the live leaderboard; the registry restore completion log; a portal reproduction of the range error.
- **Limitations:** the holdout measures catalogue recovery, not new-fault skill, so it cannot rank the nine sites or any catalogue-avoiding submission. The literal gate's coverage bound makes it unpassable at this dot count, which the owner must rule on.
- **Tests:** `python -m pytest -q` in `.venv` gives **449 passed, 1 skipped** on this branch (baseline before this session: 446 passed, 2 skipped; +2 new solver tests, and one previously skipped test now runs because the restored data is present).

## 9. Links for manual review
- Competition: https://www.drivendata.org/competitions/306/competition-doe-gems/
- Problem description and submission format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Scoring clarification (forum): https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Official rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reid et al. (2013): https://www.reid-geophys.co.uk/wp-content/uploads/2017/11/Reid-et-al-2013.pdf
- Zhang et al. (2000): https://www.reid-geophys.co.uk/wp-content/uploads/2017/11/Zhang-et-al-2000.pdf
- Support contact for portal errors (listed on the forum page): info@drivendata.org
