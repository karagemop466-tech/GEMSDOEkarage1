# Repository review and submission decision — `arena/fd3e38cf-gemsdoekarage1` (31 Oct 2026)

## Executive decision

**NEGATIVE — DO NOT SUBMIT ANY FILE FROM THIS SESSION.** No new GeoTIFF was generated, no candidate was validated, and no weekly slot was selected or spent. This is a fail-closed decision, not a negative geological result. Generating a nominally unique TIFF without the assigned method lane, canonical shared tools, and required feature cache would violate the user's parallel-run protocol and produce an unauditable prediction. Historical research files remain in the repository; none is cleared by this review.

**No leaderboard score estimate is defensible.** The nine focus-site values below are user-supplied reports, not verified organizer receipts. A catalogue hide-and-recover holdout measures recovery of mapped-fault segments, whereas the competition target is intended to include faults absent from the catalogue. The repository itself records that the mandated local holdout reverses the observed ordering of the focus submissions. Thus neither a fitted number nor a holdout value should be presented as a forecast of the hidden leaderboard score.

## The focus-site comparison

The following rows are cross-checked against the saved-byte audit `docs/data/nine_site_executive_20261031.json` and user-reported scores supplied in the prompt. Score values are **USER-REPORTED / UNVERIFIED**. Raster dot counts, hashes, and overlap measurements are **MEASURED** on the locally pinned reference bytes; those mirrors are not organizer-authenticated. “Estimated score” is deliberately **NOT ESTIMABLE**. “File” means the historical artifact associated with the report, for study only; do not resubmit it.

| Site | Historical file (study only) | Reported value | Estimated leaderboard score | Unique vs the other eight? | Submit? |
|---|---|---:|---|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 USER-REPORTED | Not estimable | No | No |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 USER-REPORTED | Not estimable | No | No |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 USER-REPORTED | Not estimable | No | No |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 USER-REPORTED | Not estimable | No | No |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 USER-REPORTED | Not estimable | No | No |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 USER-REPORTED | Not estimable | No | No |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | **0.2778 USER-REPORTED** | Not estimable | No | No |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 USER-REPORTED | Not estimable | No | No |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 USER-REPORTED | Not estimable | No | No |

**Measured relationship:** the nine saved masks are highly overlapping members of one dotted-support family, not nine independent geological discoveries. For example, the saved audit identifies GEMSDOE32 B2 as a subset of GEMSDOE25 with 6,436 catalogue-adjacent dots removed and no added dots. The audit also records near-unity pairwise rank correlations/3-px directed overlaps. That establishes geometric similarity, not a complete search of every organizer submission. The test against a full registry cannot be certified from this checkout.

## Why GEMSDOE32 B2 is the reported leader — and what that does not prove

The reported 0.2778 is the highest of these nine owner-supplied values. The likely metric mechanism is plausible: the competition's documented fault-discovery setting values predictions of unmapped faults; reducing dots near the already mapped catalogue can reduce wasted false-positive mass while retaining dots elsewhere. The local lineage audit supports the narrow fact that B2 removes 6,436 dots from GEMSDOE25 and adds none. Across nine reported values, score is associated with fewer dots / greater distance from the catalogue, but the sample is small, the scores are unverified, and the submissions are not independent.

This is not proof that deleting catalogue-near dots caused the 0.2778, nor proof that B2 can be beaten by simply deleting more. A geometric lattice is not a fault detector; thinning it may improve a particular hidden test by chance or because of the metric's penalty structure. The key scientific opportunity is better *off-catalogue fault localization*, supported by independent evidence, not another resampling of the same support.

A score above 0.2778 is possible in principle, but **no evidence in this session demonstrates one**. In particular, the public leaderboard snapshot in this repository is not a receipt for these files and does not provide labels for forecasting. Do not state that 0.2778, 0.3195, 0.4413, or a projection is a measured score for a new file.

## Preregistered research slate (proposals, not validated)

Qualitative ranking only: expected improvement is an informed prior; no numeric score or DTI is implied. These use bands listed in the repository's band inventory for the competition-provided feature raster. Availability/authenticity of that raster is still blocked here.

| Rank | Hypothesis and layers | Target physical signature / off-catalogue rationale | Difference from checked implementations | Main non-fault mimic | Expected opportunity / cost |
|---:|---|---|---|---|---|
| 1 | **H-SPEC: cross-scale gravity–magnetic phase stability** — `iso_grav_anom` and `rtp`/`tmi` | A fault juxtaposing density and susceptibility contrasts may produce a lineament with a repeatable cross-field phase relation across adjacent wavelengths, including a buried boundary with no surface scarp. | Tests phase/coherence stability across scale, rather than another pointwise union of horizontal-gradient, tilt, or upward-continuation maxima. The source grep found no cross-wavelet/cross-spectrum implementation; this is not a claim of global novelty. | Pluton/lithologic contacts, remanent magnetization, flight-line leveling seams, gridding artifacts. | Moderate qualitative potential; medium–high cost. Chosen as first *validation* proposal, not as a submission candidate. |
| 2 | **H-CB-OFFSET: conductivity / basement paired-boundary displacement** — `cond_surf`, `depth_to_base_surf`, with a gravity or magnetic edge for orientation | A buried basin fault may offset shallow conductive cover relative to basement depth, leaving a paired, laterally displaced boundary where mapped traces and topographic scarps are absent. | Uses signed lateral offset and paired-boundary geometry; distinct from single-field conductivity-gradient or basement-ridge features. | Playa brine fronts, clay-rich sediment transitions, basin-fill thickness changes unrelated to faulting. | Low–moderate qualitative potential; low–medium cost; confounding substantial. |
| 3 | **H-TOPO-ASYM: signed paired-profile flexure** — `det_elev` and `det_elev_slope`, conditioned on an independent subsurface edge | Blind faults may create a subtle, asymmetric pair of elevation-profile breaks rather than a sharp positive ridge, making them absent from a surface-trace catalogue. | Uses a signed cross-profile shape criterion rather than unsigned ridge/curvature scores or standalone LiDAR scarp amplitude. | Drainage incision, alluvial-fan margins, shorelines, roads and rail grades. | Low–moderate qualitative potential; medium cost. |
| 4 | **H-E3: joint Euler depth-coincidence** — magnetic `tmi`/`rtp` and `iso_grav_anom` | A buried structure is considered only when independently estimated source-depth clusters from both potential fields co-locate within a preregistered tolerance. | Euler has already been tested individually (with conflicting protocol sensitivity); the *joint cross-field coincidence* is a distinct, untested combination in this checkout, not a claim that Euler itself is new. | Co-located lithologic/intrusive contacts, regional density/susceptibility bodies, correlated processing artifacts. | Low–moderate qualitative potential; medium cost. Lower priority until the conflicting single-field protocols and null are reconciled. |

All four are proposals, not results. They require no new external dataset beyond the competition's own feature raster. No external source was needed or used for these proposals. The official competition data page is login-gated according to the repository's prior access audit; the feature raster was not present in this checkout. If future work adds a new external layer, it must first name and authenticate the official source and verify coverage/access before preregistration.

## Why the top proposal was not tested

I ran `python scripts/shared_tools.py preflight` on this checkout. It returned exit 1 and `ready_for_shared_tools: false`. Specifically:

- `registry/template.json` records `method_lane: null` and `canonical_template_assignment: null`.
- `.cache/gems_work/feature_stack.npy` and the cached `existing_faults.tif`, `training_features.tif`, `sample_submission.tif`, and `labels.tif` are missing; `data/` is absent.
- `scripts/audit_template_integrity.py`, as reported by preflight, finds local `vendor/gems57/submission_writer.py` and `uniqueness.py` differ from their recorded hashes. It also reports no authorized execution template assignment.
- Python dependencies (`numpy`, `rasterio`, `scipy`, `scikit-learn`, `pytest`) were absent in the base environment. I created an ignored local `.venv` and installed the declared requirements to run software tests; this does not restore competition data or authenticate any input.

Therefore no per-feature leakage canary, spatial holdout, saved-byte validator, candidate pre-placement correlation, or final-dot overlap was run. The budget use for *this review* is zero experiments; no slot was touched. Running a private/reconstructed holdout or using stale output as new evidence would violate the reuse-the-template rule. At the start of this review the KP1 artifacts contained a stale `promote` state. During PR conflict resolution, the newer `origin/main` safety review and its fail-closed evidence were merged: the current `evidence/kp1_run_card.json` and `evidence/kp1_release_gate.json` now both say negative / not cleared. This aligns the historical receipts with the missing lane/template/cache and pinned-tool integrity blockers. The old raster is not reissued here. The merged `arena/4dffc2c6` independent recheck measured KP1 max |Spearman| 0.0136 and max 3-px overlap 26.5% **against the nine focus rasters only**; that supports narrow focus-site uniqueness but explicitly does not establish completeness of the registry. Its saved-byte format recheck also is not organizer acceptance.

Software verification after the site hardening: `.venv/bin/python -m pytest -q -rs` → **518 passed, 4 skipped, 0 failed** (126 Rasterio pending-deprecation warnings). All four skips require missing competition/reference rasters. `python scripts/build_site.py` rendered 36 deterministic decision pages plus the seven KP1 historical pages and the current decision page. `git diff --check` passed. These are code/site checks, not model validation.

## Next experiment, if blockers are resolved

First confirm and record the owner-assigned method lane and canonical upstream template commit; repair provenance only in that upstream template, not in a private copy. Restore organizer-authenticated training features, labels/catalogue, sample raster, and feature stack, then re-run preflight. Freeze H-SPEC's scales, phase statistic, fold design, matched control, emission budget, and stop criteria before seeing results. Test every input feature alone on the spatially blocked holdout; any AUC above 0.90 is a leakage alarm until explained. Use the assigned `evaluate_holdout.py` exactly as specified (whole fault-segment withholding with buffer, fold-local catalogue features, exact visible-fault masking; pooled DTI with α=0.2, β=0.8 and a 300 m triangular kernel; report withheld positives and a 95% CI). Compare against the frozen current holdout best and a matched null. Surface/registry comparison must occur before placement, and dot overlap after placement. Only if the preregistered comparable holdout beats the frozen best and all uniqueness/format gates pass may a separate selector consider a weekly slot; this session's decision does not select one.

## Trusted source links and provenance limits

- [DrivenData competition overview and rules](https://www.drivendata.org/competitions/306/competition-doe-gems/) — official competition entry point.
- [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — official task description.
- [DrivenData competition data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — login required per the repository's prior access attempt; not fetched anew in this review.
- [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — leaderboard source; repository snapshot dated 31 Oct 2026, not a newly fetched live confirmation in this review.
- [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) — official organizer-owned example repository.
- [NLR GEMS rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) — competition rule document linked by the owner; no fresh retrieval was possible under this environment's network restrictions.
- [USGS GeoDAWN survey data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) — official source identified in repository research; no new GeoDAWN download was attempted.
- [EPSG:32611](https://epsg.io/32611) — CRS reference (EPSG registry mirror).
- [Nine-site saved-byte audit](../docs/data/nine_site_executive_20261031.json) · [preflight output reproduced in the run card](../evidence/run_card_arena_fd3e38cf_20261031.json) · [full original owner prompt and standing brief](../README.md#session-prompt--full-text-read-at-start-of-every-session).

## Three-pass review record

1. **Pass 1 — inspect and implement:** inspected repository instructions, current landing-page generation, focus-site saved-byte table, experiment evidence, lane/template pin, preflight, and historical KP1 promotion artifacts. Added this review, a fail-closed session run card, and a clearer public decision page. The run card records null for every unrun measurement rather than inventing values.
2. **Pass 2 — adversarial review:** found a material inconsistency: the generated landing page could show a green "OK TO SUBMIT" button from an old KP1 card even though current shared preflight fails and the lane is unset. Corrected the site-generation path and its test to make active clearance impossible from that historical gate alone.
3. **Pass 3 — request recheck:** confirmed all nine focus sites appear; each reported score is labelled USER-REPORTED; no leaderboard estimate is invented; candidate hypotheses are explicitly qualitative; no unique TIFF is claimed; the 70% / 3-px stop, leakage canary, canonical template, format checks, budget, slot separation, and JSON run card are represented. Remaining missing inputs mean the new TIFF/holdout requirement is not safely achievable in this checkout; this limitation is surfaced prominently rather than papered over.

## Remaining work / limitations

1. Restore organizer-authenticated training data and cached stack; mirror hashes are not source authentication.
2. Resolve lane ownership and identify the single canonical shared evaluator/writer; upstream review must reconcile the writer/uniqueness hash mismatch.
3. Resolve the exact meaning/scope of the literal registry duplicate gate against the complete, authenticated registry. Do not silently exempt a raster or bypass the user's rule.
4. Resolve whether the expected holdout is a valid selector for the off-catalogue private test. A catalogue hide-and-recover proxy has known target mismatch; an organizer-approved independent truth/protocol is needed to estimate real leaderboard outcomes.
5. After all prerequisites are available: run the top H-SPEC experiment and all single-feature leakage canaries under the shared holdout, with preregistered CI; only then build a new unique TIF with the shared writer and validate it on saved bytes.
6. Do not upload any historical artifact. No slot was chosen or spent in this review.
