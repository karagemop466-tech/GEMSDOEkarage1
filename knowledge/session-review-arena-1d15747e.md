# Session review · `arena/1d15747e-gemsdoekarage1` · 2026-10-29

**Verdict: NOT CLEARED — DO NOT SUBMIT.** One new, format-valid, unique GeoTIFF was generated and is downloadable for audit. It is not OK to submit: its holdout is indistinguishable from random dot placement, and it fails the literal 13GEMSDOE lattice rule. No weekly slot was selected or spent.

Labels used below: **HOLDOUT-DTI** (evaluator, withheld positives, 95% CI), **ORGANIZER-CONFIRMED** (none exists in this repo), **USER-REPORTED / UNVERIFIED** (scores supplied in the prompt), **OFFICIAL** (read from DrivenData or the organizer's forum this session).

## Passes

| Pass | What was done | Evidence |
|---|---|---|
| 1 · Verify | Read the official metric page, the organizer forum thread, the official reference notebook and the live leaderboard. Restored all pinned inputs and verified SHA-256 for 21 files. Checked the metric code against the official worked example. | `registry/data_manifest.json`, `data/restore_receipt.json`, sections below |
| 2 · Build and test | One lane (K1-HGRID-STRAIN), 3 experiments (E1 canary, E2 K-sweep with controls, E3 build). Shared template only: `vendor/gems57` evaluator, shared writer, shared uniqueness code. | `scripts/hgridge_strain_lane.py`, `evidence/hgridge_e{1,2}_*.json`, `evidence/hgridge_e3_build_*.json`, `evidence/hgridge_run_card_*.json` |
| 3 · Site, audit, tests | Nine-site executive audit from pinned bytes; renderer updated (top status line, nine-site table); audit tool for untracked TIFs; tests. | `evidence/nine_site_executive_20261029.json`, `scripts/render_site.py`, `scripts/audit_local_tif.py`, `evidence/audit_unique_hyp_kth_therm_20261029.json` |

## 1 · Official sources (verified this session)

- **Metric** (OFFICIAL; [competition page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)): distance-weighted Tversky, α = 0.2, β = 0.8, triangular kernel with R = 300 m (3 px). Submission: single-band float32 GeoTIFF, EPSG:32611, 100 m, same bounds as training data, values in [0, 1], "data outside the bounds is null or nan". Worked example: TP_w = 3.00, FP_w = 1.89, FN_w = 2.00 → TI = 0.60. Our `gems57.metric.dti_from_components(3.0, 1.89, 2.0)` = 0.6027 (page rounds to 0.60).
- **Masking** (OFFICIAL; [forum thread 11516, DrivenData staff, 16 Sep](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)): "Pixels corresponding to known USGS/INGENIOUS faults are masked / excluded from evaluation, so they do not count towards penalty terms." Masking is pixel-level. Predictions 300 m from a known trace but off the trace are *not* exempt.
- **Reference solution** (OFFICIAL; [drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution), notebook cells 483–484 and 572–634): Tversky with α = 0.2, β = 0.8; continuous sigmoid output; "it may be advantageous to threshold this map". The notebook reads `data/numeric_features.tif`, whereas the competition file is named `training_features.tif` in the README. Naming match not verified (flag).
- **Leaderboard** (OFFICIAL public table, read 29 Oct 2026, [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)): #1 `xiaofanhu` 0.4544; #2 `cfld__` 0.3916; #3 `Batik Shirt Brothers` 0.3911; row #47 0.3195 (name recovered from a truncated page read as `kpomazi`; treat as unverified). **Irregularity:** the prompt's "#1 0.4413 Jacker0429" and "2nd 0.3195 davec" do not match. `Jacker0429` and `davec` do not appear in the 50 rows visible. The 0.4413 value was the prior session's cached 25 Oct snapshot.

## 2 · Nine-site executive summary

Computed from pinned bytes in `evidence/nine_site_executive_20261029.json`. Overlap is directional: the fraction of a file's dots within 3 px of another file's dots (`gems57.uniqueness.dot_overlap`). Estimated score is **UNAVAILABLE** for every row. No pipeline is reproduced, and the organizer's test set is hidden.

| Site | Highest listed file (USER-REPORTED) | Score | Pinned? | Dots | Worst cross-site overlap (other focus files) | Unique vs other focus files? | Lattice overlap | Submit? |
|---|---|---|---|---|---|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-…-nan` | 0.2477 | yes | 60,069 | 1.000 (GEMSDOE25) | NO | 99.6–99.9% | NO — already listed |
| GEMSDOE25 | `dotted-h19-5-d2-8-…-nan` | 0.2600 | yes | 44,090 | 1.000 (GEMSDOE24) | NO | 99.6–99.9% | NO — already listed |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-…-nan` | 0.2449 | yes | 61,328 | 0.980 (GEMSDOE24) | NO | 99.6–99.9% | NO — already listed |
| GEMSDOE28 | `h36-1-rung30-blind-r1-…-nan` | 0.2710 | yes | 37,660 | 1.000 (GEMSDOE24) | NO | 99.6–99.9% | NO — already listed |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-…` | 0.2600 | yes | 44,090 | 1.000 (GEMSDOE24) | NO (same mask as GEMSDOE25) | 99.6–99.9% | NO — already listed |
| GEMSDOE31 | `h27-4-solo-d28-…-nan` | 0.2708 | yes | 40,199 | 1.000 (GEMSDOE24) | NO | 99.6–99.9% | NO — already listed |
| **GEMSDOE32** | `h33-h33-2-b2-…-e5eb6e7e-zeros` | **0.2778** | yes | 37,654 | 1.000 (GEMSDOE24) | NO | 99.6–99.9% | NO — already listed |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-…` | 0.2632 | yes | 41,865 | 0.997 (GEMSDOE27) | NO | 99.6–99.9% | NO — already listed |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-…-zeros` | 0.2750 | yes | 38,854 | 0.976 (GEMSDOE27) | NO | 99.6–99.9% | NO — already listed |
| GEMSDOEkarage1 (this session) | `karage1-hgridge-strain-K37654-20261029T181321Z-zeros.tif` | — | generated | 37,654 | 0.221 (GEMS19 parent mask) | YES | 99.88% (literal FAIL) | **NO** — negative |

Notes:
- **Highest listed score:** GEMSDOE32 `h33-h33-2-b2` at 0.2778 (USER-REPORTED). It is the top listed value but not independent: `B2 = D2.8 − 6,436 dots` exactly (`dots(GEMSDOE25) = 44,090`, `dots(B2) = 37,654`, and B2 ⊂ D2.8 with 0 exceptions), and GEMSDOE25 and GEMSDOE30 are pixel-identical masks.
- **Uniqueness:** only GEMSDOE27 `h31-drcg` (USER-REPORTED 0.2250, pinned, 37,654 dots) is distinct from the other pinned focus rasters (worst 57.4%). It is not any site's best file.
- **Scope limit:** only 14 pinned focus-site and lattice rasters are compared. The other listed submissions are unpinned, so "unique" means "unique vs these pinned files".
- **Re-uploading a listed file cannot change its score.** Each row's "submit" answer is NO.

## 3 · The generated TIF (this session)

- **File:** `docs/downloads/karage1-hgridge-strain-K37654-20261029T181321Z-zeros.tif` (+ `.zip`, `.json` receipt, `.validate.json`). SHA-256 `15f330343236f41c…` (full value in `evidence/hgridge_run_card_*.json`).
- **Name:** `karage1-hgridge-strain-K37654-20261029T181321Z` · **Note (108 chars):** "K1-HGRID-STRAIN label-blind TMI-crest x strain, 37654 dots. Format-valid; holdout ~ random. NOT CLEARED."
- **Format (verified from disk):** single band, float32, EPSG:32611, 3730 × 3292, transform (100, 0, 243350, 0, −100, 4508550), values in [0, 1], finite everywhere, zero outside the 5,167,373-cell footprint (`sample_check.submission_outside_is_zero = true`), 37,654 positives, 0 on the mapped catalogue. Writer: shared `gems57.submission_writer.write_submission`.
- **Encoding caveat:** the shared writer emits zero-filled outside cells (all-finite export). The organizer's example uses NaN outside. Both are plausible under "null or nan". The zero encoding is the repo's shipped convention; it is flagged, not resolved.

### Gates (literal)

| Gate | Result |
|---|---|
| Format / CRS / shape / transform / range | PASS |
| No positives outside footprint or on mapped catalogue | PASS |
| Leakage canary (max single-feature AUC, symmetric) | PASS — 0.5726 (`tc`); candidate score 0.553 |
| Forward 3-px overlap ≤ 0.70 vs 14 non-lattice pinned rasters | PASS — worst 0.2214 (GEMS19 parent), all focus sites ≤ 0.207 |
| \|Spearman\| ≤ 0.90 vs the same rasters | PASS — max 0.0014 |
| Literal 13GEMSDOE lattice, forward overlap ≤ 0.70 | **FAIL — 0.9988** |

**Lattice floor:** the pinned lattice covers all but 6,649 footprint cells within 3 px. A raster with N dots therefore has forward overlap ≥ (N − 6,649)/N, which is 82.3% at N = 37,654. Any raster with N > 22,163 dots fails the literal lattice rule regardless of method. This is a protocol-level defect, not a lane-drift finding. See irregularities.

### Holdout (HOLDOUT-DTI, `gems57-pooled-hide-v2`, vendor `holdout.py`, pixel-exact visible mask)

| Arm (K = 37,654 unless stated) | Pooled DTI | 95% CI (cell bootstrap, 2,000 draws) | Withheld positives |
|---|---|---|---|
| **Gate score, label-blind** (the lane's ranking, no catalogue used) | **0.04809** | [0.03806, 0.05575] | 22,641 |
| Crest-only (no strain gate) | 0.04818 | [0.03823, 0.05579] | 22,641 |
| **Random placement** (seeded) | **0.04487** | [0.03844, 0.05025] | 22,641 |
| Gate, K = 10,000 | 0.02594 | [0.00820, 0.03835] | 22,641 |
| Gate, K = 20,000 | 0.03603 | [0.01934, 0.04786] | 22,641 |
| Gate, K = 60,000 (capped at the 40,287-cell crest pool) | 0.04955 | [0.04149, 0.05611] | 22,641 |
| **Deliverable** (catalogue-pruned; conservative) | 0.03642 | [0.02951, 0.04180] | 22,641 |

**Reading:** the gate beats random by 0.0032, with overlapping CIs. The strain gate adds nothing measurable. The holdout is dominated by dot density and kernel coverage, not localization. The deliverable's lower score comes from its catalogue exclusion, which removes withheld truth too. The holdout therefore cannot evaluate catalogue exclusion fairly (see irregularities).

**Bar:** no same-evaluator benchmark for the nine files exists here, and the repo's earlier GPC control (0.0734) was measured with a different evaluator. The comparison is therefore against random placement under the same evaluator.

## 4 · Why 0.2778 scored highest among those listed, and whether it can be beaten

**What is established:**
1. Under the official metric (α = 0.2, β = 0.8, α + β = 1), the marginal rule for a non-redundant dot is: add it iff its kernel credit k > α · DTI. This follows from DTI = TP/(TP + αFP + βFN) when α + β = 1. At DTI ≈ 0.278 the bar is k > 0.056. A dot anywhere within about 2.9 px of a plausible trace is worth adding. The optimum is therefore dense emission along the most probable trace set, not sparse emission. That is why every listed focus-site file has 37–61k dots.
2. Predictions on known-fault pixels are excluded, so they are neither rewarded nor penalized (OFFICIAL). Predictions in the 300 m halo around a known trace, but off it, still incur (1 − k) penalties. Removing halo dots is a real lever on FP mass. B2 removes 6,436 dots from D2.8, which is exactly this kind of pruning.
3. B2 is therefore a pruned version of the GEMSDOE25/30 family, not a new method. Its listed score (0.2778) is 0.0178 above GEMSDOE25 (0.2600). That gap is USER-REPORTED, and no receipt links the bytes to any score.

**What is not established:** the hidden new-fault truth is unavailable, no organizer receipt exists, and no reproduced pipeline reproduces 0.2778. The explanation above is consistent with the metric. It is not verified against the test set.

**Can it be beaten?** Not demonstrated here. The public board's #1 (0.4544) and #2 (0.3916) show that higher scores exist. The nine listed files are near-duplicates of one H19-5 ridge family (cross-site overlaps 97–100%), so the family's ceiling is correlated across sites. Beating 0.3195 would need a different, independently-scoring localization family. This session's only new family (H1 below) showed no skill over random placement on the proxy, so it does not meet that bar.

## 5 · Hypotheses (ranked by expected DTI gain per unit cost; priors, not projections)

| Rank | Hypothesis | Layers (training_features band) | Physical signature | Why off-catalogue | How it differs from the listed family | Status |
|---|---|---|---|---|---|---|
| H2 | **Basin-basement step on a magnetic crest.** Normal faults juxtapose thick basin fill against basement. | `depth_to_base_surf` (15) gradient × `tmi_hg` (3) crest | Co-located sediment-thickness step and magnetic contrast | Small-throw or buried splays absent from USGS Quaternary maps | Uses an independent sediment-thickness variable; the listed family uses ridge geometry alone | **Top proposed; not tested.** Next experiment. |
| H3 | **Joint gravity–magnetic edge coherence.** | `iso_grav_anom_hg` (18) crest coincident with `tmi_hg` crest within 300 m | Density and susceptibility contrast at the same location | Fault zones with both contrasts missing from catalogue | Requires two independent potential-field edges | Proposed; not tested |
| H4 | **Seismicity lineation.** Earthquake-density alignments indicate active splays. | `ieq_n100a15` (16), `deq_n100a15` (10); structure-tensor orientation | Linear alignment of epicentre density | Unmapped active splays | Only hypothesis driven by a time-varying signal | Proposed; not tested. Mimic: aftershock and induced-seismicity clusters. |
| H5 | **K/Th alteration ratio gating** of crest candidates. | GeoDAWN radiometrics (external `geodawn_rad_u8`, restored; channel encoding unverified) | K-metasomatism along fault-hosted hydrothermal conduits | Alteration zones not mapped as faults | Adds an independent chemical signal | Proposed; encoding must be verified first |
| **H1 (tested)** | **TMI horizontal-gradient crest × geodetic strain coherence** (this session's build). | `tmi_hg` (3), `geod_2ndinv` (4) | Crest + active strain | Lithologic contacts and GPS-geometry artefacts | — | **Negative**: no skill over random placement (§3) |

Named non-fault mimics: lithologic and intrusive contacts (H1, H2, H3); aftershock and induced-seismicity clusters (H4); felsic plutons and alluvium (H5).

## 6 · Irregularities (flagged, not hidden)

1. **Lattice rule is unsatisfiable.** Literal 70% lattice test: floor (N − 6,649)/N. No raster with more than 22,163 dots can pass. `registry/registry_roles.json` classifies the lattice as a calibration probe ("never sufficient alone to declare lane drift"), but the run cards and AGENTS.md still treat it as blocking. **Protocol-owner decision needed.**
2. **Public leaderboard snapshot mismatch.** See §1. The user's "0.4413 Jacker0429" and "0.3195 davec" do not match the 29 Oct read.
3. **Nine best files are mutually duplicates** (cross-site overlaps 97.6–100%) under the user's own uniqueness standard.
4. **labels.tif is byte-identical to existing_faults.tif** (the mapped catalogue, per `registry/data_manifest.json`). The organizer's hidden test truth is not in this checkout. Every holdout is a catalogue-based proxy.
5. **Holdout asymmetry for catalogue exclusion.** Pruning dots on the full catalogue drops the holdout from 0.0481 to 0.0364, because the holdout truth is the catalogue. The deliverable's real effect on the organizer score is unknown.
6. **Training features come from a third-party GitHub mirror.** `restore_data.py` checks SHA-256, but the manifest states the mirror is not organizer-authenticated.
7. **Output encoding ambiguity:** zeros outside (shared writer) vs NaN outside (organizer example). Flagged.
8. **E1 changed twice** (crest threshold 80th pct → median → 0) because the earlier pools could not fill K = 37,654. Both changes are recorded in the run card and E1 was re-run each time. The threshold was not chosen on any holdout score.
9. **Shared-tool defect (noted, not fixed here):** `src/gemsk/holdout.py` dilates visible faults by 3 px instead of pixel-exact masking (per the repo's own notes). This session used the vendor evaluator, which is pixel-exact.
10. **Pre-existing repo breakage fixed:** `scripts/run_karage1_experiments.py` had a SyntaxError (`pass # raise …`) that broke the quarantine guard and three tests. The guard now raises `BLOCKED:`. The 1668dda0 hardening test flagged `docs/downloads/unique-hyp-kth-therm-mask-20261028-zeros.tif` as unaudited on `main`; it now has a receipt (`evidence/audit_unique_hyp_kth_therm_20261029.json`: 37,654 positives, 0 outside footprint, lattice 99.90% FAIL, worst focus 26.5%, not cleared).
11. **Test-invariant extension:** the hardening test now also accepts this session's receipts (`hgridge_e3_build_*.json`, `audit_*.json`). The rule is unchanged. Each new TIF needs a later receipt.
12. **Organizer clarification on NaN vs zeros** has not been requested. Ask on the forum.
13. **Concurrent-session files on `main`:** while this branch was open, `main` gained two GSE TIFs (`karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455`, `-nan` and `-zeros`) with no saved-byte receipt. Both were audited here with `scripts/audit_local_tif.py` (`evidence/audit_gse_geothermal_surface_24000_*_20261029.json`): 24,000 positives, 0 outside footprint, lattice overlap 99.91% (literal FAIL), worst focus 20.3%. The `-nan` file fails the repo's all-finite policy (7,111,787 NaN cells). Neither is cleared.

## 7 · Remaining work

1. **Protocol owner:** decide whether the 13GEMSDOE lattice is a blocking witness for dot rasters with N > 22,163 (role split vs literal rule). Without a decision, no dot raster can clear.
2. **Run H2** (basin-basement step × magnetic crest) on the same holdout with a pre-registered K sweep and a canary. Budget: 3 experiments.
3. **Validate H3–H5** as priors only; H5 needs the radiometric encoding verified.
4. **Ask the organizer** (forum) whether zeros or NaN outside is preferred, and whether known-fault masking applies to halo dots.
5. **Restore and audit the LiDAR scarp and GeoDAWN external features** (`scripts/restore_data.py --group external` already restored them; not yet used).
6. **Leaderboard receipts:** none exists for any listed file. A genuine ORGANIZER-CONFIRMED number needs a submission receipt, which requires a cleared file and a weekly slot.

## 8 · Limitations

- The holdout is a catalogue proxy. It is not the organizer's new-fault test. Relative ranking only.
- Single-feature AUCs are weak (0.55–0.57). Canary passed, but no feature is strongly informative on this proxy.
- Not re-verified this session: the DrivenData data page (login-walled per the repo); the nine focus-site repositories beyond the pinned files; any listed file not pinned here.
- No slot, no upload, no organizer submission. Nothing is cleared.
