# Session review — arena/fb1e3550 (29 Oct 2026)

**Verdict: NEGATIVE · NO FILE CLEARED TO DOWNLOAD OR SUBMIT.** No GeoTIFF was rasterised for placement, no weekly slot was selected or spent, and no leaderboard estimate was produced.

Run card: [`evidence/session_fb1e3550_run_card.json`](../evidence/session_fb1e3550_run_card.json) · Hypotheses: [`knowledge/hypotheses-20261029.md`](hypotheses-20261029.md) · Official-source register: [`knowledge/official-sources-verified-2026-10-29.md`](official-sources-verified-2026-10-29.md) (section F, added this session).

## 1. Direct answers

**Can I download a TIF and submit it now?** No. Neither new candidate beat the holdout best, and the repository's gates (pre-placement correlation/overlap, holdout, validator) are the only basis for clearance. A grep this session found no `ok_to_submit: true` in `docs/downloads/*.json` or `docs/data/*.json`, and no "OK TO DOWNLOAD" phrase in the published HTML.

**Why no new TIF?** The protocol says a candidate must beat the current holdout best before any placement. Both candidates tested this session lost to the reproduced GPC control by a wide margin (paired CIs exclude zero). Rasterising a losing candidate would produce a file that looks submittable and is not, which is the failure mode the page now guards against.

**Which GEMSDOE file is best?** By reported score, GEMSDOE32 (0.2778, USER-REPORTED / UNVERIFIED). It is a lattice duplicate (99.92% within 3 px of the pinned lattice), so it is not eligible for re-submission under the project's protocol.

**Estimated leaderboard score for any candidate?** None is produced. The holdout is a screen, not a forecast (see §4).

## 2. Results (all HOLDOUT-DTI, evaluator `gemsk-hide-recover-v1`, blocked 4-fold, budget 37,654 dots/fold, 60,988 withheld positives)

| Candidate | HOLDOUT-DTI | 95% CI | Paired difference vs GPC control | Verdict |
|---|---|---|---|---|
| GPC control (reproduced) | 0.073394 | [0.064520, 0.082481] | — | baseline |
| H-K1-STRAINPHASE | 0.055931 | [0.042938, 0.067869] | −0.017929 [−0.031426, −0.004555] | NEGATIVE |
| H-K1-SIGNEDOFFSET | 0.056536 | [0.050257, 0.062695] | −0.017001 [−0.028237, −0.006394] | NEGATIVE |

Evidence: [`exp2_strainphase_holdout.json`](../evidence/exp2_strainphase_holdout.json), [`exp2_signedoffset_holdout.json`](../evidence/exp2_signedoffset_holdout.json). The control reproduces the recorded value in [`exp2_dipdual_holdout.json`](../evidence/exp2_dipdual_holdout.json) to 0.0 difference (`abs_difference`).

Leakage canary (`exp1_*_canary.json`, each feature alone, blocked folds): maximum direction-invariant AUC 0.505–0.574. No feature reached the 0.90 alarm.

Pre-placement surface check (`surface_registry_overlap_20261029.json`, 15 restored registry rasters): worst |Spearman| 0.0067 (STRAINPHASE) and 0.0102 (SIGNEDOFFSET). Worst share of registry dots within 3 px of the surface's top-budget pixels 10.2%. Neither surface is a duplicate. Their problem is detection skill, not uniqueness. **Limit:** this registry is 15 of the 31 pinned rasters in the manifest, so it is partial.

## 3. What was built and what was reused

- **Shared tools, not forks:** `gemsk.holdout` (folds, `evaluate_dots`, `pooled`, `bootstrap_ci`, `auc_on_fold`), `gemsk.emission.emit`, `gemsk.grid` (band access), `gemskarage1.dipdual.build_surfaces` (GPC control), `gemskarage1.features._hessian_ridge`, `vendor/gems57.uniqueness` primitives.
- **New code:** `scripts/run_strainphase_experiment.py` (two lanes, three stages), `scripts/surface_registry_overlap.py` (pre-placement check), `scripts/render_site.py::session_panel` (fail-closed public panel), `tests/test_session_fb1e3550_strainphase.py` (7 tests). Together with the existing `tests/test_no_false_clearance.py` (5 tests) the two files run 12 tests, all passing.
- **Data:** the four core files and the 12 external files were restored from pinned GitHub mirrors (`scripts/restore_karage1_data.py`); the scored group (15 files) too. All hashes matched the manifest. These are not organizer-authenticated.

## 4. Limits of the holdout (why a holdout gain is still not a score)

- `gemsk/holdout.py` states that catalogue-truth holdouts rank owner-reported live scores only weakly (Spearman about 0.5, n = 12). A holdout gain is a screen.
- The holdout best (0.0734) sits far below the reported GEMSDOE scores (0.2449–0.2778). The two scales are not comparable, so this session cannot say how a holdout gain would map to the leaderboard.
- The holdout uses a catalogue-derived split. It cannot test blind faults the catalogue lacks, which is what the competition's private set rewards.

## 5. Irregularities flagged for review

1. **Leaderboard facts.** The prompt says 0.4413 and 0.3195 are the top scores. The public board I re-fetched on 29 Oct 2026 shows **#1 xiaofanhu 0.4544**, and 0.3195 is rank #47 (register §C). The GEMSDOE scores are not in the visible top 50 and remain USER-REPORTED / UNVERIFIED.
2. **Human-inspection claim.** The prompt says submissions need a human inspector. The official problem page says each submission in the Initial Prize Round is scored against a private set of faults labelled before the competition. It does not describe a human check before scoring. Expert-panel review enters only in the Final Prize Round, when verified new faults are added to the labels ([problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#competition-structure)).
3. **Method lane.** The protocol refers to a "single method paragraph below" that is not in the prompt. I assigned the two lanes myself from `knowledge/hypotheses-20261028.md` (H1, plus a new strain-polarity idea). Owner review needed.
4. **Lattice gate.** The 70%/3-px rule is an internal protocol, not an organizer rule (register B1). It was applied as written.
5. **Re-run disclosure.** The first STRAINPHASE run used an earlier script version with upper-case arm keys. I re-ran it with the final script; the DTI is identical (`0.055930591939032395` both times). The re-run is not a new experiment. The canary JSON was regenerated with the renamed declaration field; its AUCs are unchanged.
6. **Declaration vs measurement.** The canary field `declared_label_free_by_code_review` is set by the script after code review. It is not a runtime check.
7. **Outside-footprint encoding.** The official page says outside-bounds values are "null or nan". This session did not write any raster, so it did not test that. The earlier zeros-outside twins remain a flagged issue.
8. **Local symlink.** `.cache/gems_data` points to `data/` (both git-ignored) to match `gemsk.grid`'s hard-coded path.
9. **Partial registry.** The uniqueness check uses 15 restored rasters, not the full 31-raster manifest or the complete fleet (register D).
10. **Experiment count.** Two lanes were tested, using two of the three allowed experiment slots. The third was not used: the repo's ranked list points to H2, which is the recommended next experiment. Time used: about 1 hour 20 minutes of the 2-hour cap.

## 6. What I need from you (blockers, in priority order)

1. **Decide the lattice rule.** Either accept that dotted rasters can never pass the 70%/3-px gate, or give a written definition that the organizer uses. Without this, no dotted file can be cleared.
2. **Give me a method lane.** The protocol's method paragraph is missing.
3. **Authenticate the organizer data (optional but important).** A DrivenData login would let us check the restored mirrors against organizer bytes and check the submission-page wording, including the null/NaN encoding.
4. **Decide the next experiment.** I recommend H2 (radiometric K/eTh residuals), which needs no new data. H4 needs bias modelling. H3 needs USGS DEM hosts, which this sandbox cannot reach.

## 7. Next steps (for the next session)

1. Run H2 as the one remaining experiment slot. Pre-register it in `knowledge/hypotheses-20261029.md` first.
2. If H2 beats 0.073394 with a paired CI above zero, rasterise, validate, and run the complete registry comparison before any slot is considered.
3. Otherwise record it as negative and move to H5 (after checking `vendor/gems57/relay_bend_anatomy.py` for overlap) or H4.
4. Keep the executive summary as is: it must show NOTHING CLEARED until a file passes every gate.
