# Repository review — `arena/6607d952-gemsdoekarage1` (2026-10-31)

## Executive decision

**NEGATIVE / DO NOT SUBMIT.** There is no submission file cleared for download-and-upload in this review. The request's own run-card protocol requires a single assigned method lane, a validated holdout with confidence interval, leakage canaries, and registry uniqueness before considering any upload. No lane assignment is present in the current instructions/records, and `data/` is absent in this checkout. No new TIFF, estimate, or leaderboard claim is produced. No submission slot is used.

The requested task asks for novel research while also saying to work in a single assigned lane. Since no specific method paragraph/lane assignment is supplied, inventing a method would violate the parallel-run protocol. The prior registered Lahontan shoreline-offset hypothesis is a proposal only (see `docs/research/hypotheses-20261029.md`); its official USGS shapefile is not locally available and the README records that the sandbox cannot fetch its host. Do not represent it as validated.

## Nine focus sites: best *reported* artifacts, not recommendations to submit

The table below transcribes the highest user-provided score per site from this task. The score classification is **USER-REPORTED / UNVERIFIED**: no artifact-linked organizer receipt was available in this checkout. Filenames are learning/lineage references only. An `n/a` estimate means no defensible estimate; a leaderboard projection is not a score.

| Site | Highest listed artifact | Reported score | Estimate for a new candidate | Unique vs these nine? | Upload decision |
|---|---|---:|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 USER-REPORTED / UNVERIFIED | n/a | No; substantial shared thinning family | Do not resubmit |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 USER-REPORTED / UNVERIFIED | n/a | No; same dot support as GEMSDOE30 in repo's mirror audit | Do not resubmit |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 USER-REPORTED / UNVERIFIED | n/a | No; overlaps with sibling masks | Do not resubmit |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 USER-REPORTED / UNVERIFIED | n/a | No; highly related thinning family | Do not resubmit |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 USER-REPORTED / UNVERIFIED | n/a | No; same dot support as GEMSDOE25 in repo's mirror audit | Do not resubmit |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 USER-REPORTED / UNVERIFIED | n/a | No; same support as a GEMSDOE28 secondary in repo's audit | Do not resubmit |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | **0.2778 USER-REPORTED / UNVERIFIED** | n/a | No; a strict subset in the repo's mirror audit | Do not resubmit |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 USER-REPORTED / UNVERIFIED | n/a | No; substantial shared thinning family | Do not resubmit |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 USER-REPORTED / UNVERIFIED | n/a | No; superset of GEMSDOE32 in repo's mirror audit | Do not resubmit |

Site URLs, historical score claims, exact mirrored raster identities, and caveats are indexed in [`docs/executive-summary.html`](../docs/executive-summary.html), [`docs/data/focus_site_table_20261029.json`](../docs/data/focus_site_table_20261029.json), and [`knowledge/02_why_gemsdoe32_b2_scored_0.2778.md`](02_why_gemsdoe32_b2_scored_0.2778.md). Those audits use third-party mirrored bytes, not organizer-authenticated rasters. The literal 70%/3-pixel rule is a user-specified internal duplicate stop, not an official contest rule; the documented focus-site rasters fail this rule against the 13GEMSDOE lattice witness (the saved audit reports approximately 99.9% lattice proximity, partly reflecting lattice density). This stringent gate needs owner/coordinator confirmation before any future experiment, but must not be bypassed under the present protocol.

### What explains the GEMSDOE32 report?

The strongest measured clue is lineage, not a demonstrated geological causal mechanism. Repository byte-mask audits say the GEMSDOE32 B2 mask has 37,654 positives and is the GEMSDOE25 mask after removing 6,436 dots within the closed two-pixel radius of mirrored known labels; the audit reports no additions. It is also a subset of GEMSDOE36, which adds 1,200 dots. If the reported scores are accurate, a plausible explanation is that removing low-yield predictions reduced weighted false-positive cost under the asymmetric distance-weighted Tversky metric. But absent receipt-linked scores and a paired, fold-local holdout ablation, this is **not established causation**. In particular, a 0.2778 report is not evidence that its geological hypothesis is superior, and does not support a numerical prediction for a new file.

The cited `0.3195` and `0.4413` in the request are not reliable targets without a dated official leaderboard capture; README's previous live review instead recorded a different current top score/rank snapshot. These are time-dependent external values and are not repeated here as current scores.

## Novel candidate shortlist (proposals, no experiments run)

The ranking is by potential information gain per implementation cost, not expected score gain. Existing repo keyword/research checks show extensive testing of topography, potential fields, Lahontan mimics, strain, thermal and standard multi-feature models. A specific lane assignment is still required before execution.

| Rank | Candidate / layer and physical signature | Why it might find an omitted fault | Main non-fault mimic | Cost / data viability | Difference from existing repo |
|---|---|---|---|---|---|
| 1 | **Two-datum Lahontan shoreline displacement:** USGS MF-2323 shoreline traces plus DEM; measure paired shoreline elevation steps and difference out regional tilt | A displaced paleo-horizontal datum could expose low-relief/buried traces without depending on a visible scarp | Regional uplift/tilt, lake-loading deformation, wave reworking, fan burial | Medium; official USGS metadata is linked in `docs/research/hypotheses-20261029.md`; shapefile was not obtained/hashed here and data-host access is blocked | Repo currently uses Lahontan shoreline information as a confound/veto, not as an explicit paired displacement measurement |
| 2 | **Quaternary surface differential displacement:** DEM plus mapped/dated terrace or alluvial-fan surfaces; compare riser elevation across linear candidate corridors | Correlated surfaces can retain cumulative displacement after scarps are muted | Channel incision, avulsion, fan progradation, erosional breaks | High; no verified official age-polygon dataset is identified locally, so this candidate is not viable until such source is identified and downloadable | Existing code discusses terraces as mimics; no verified same-surface displacement feature recorded |
| 3 | **Paleolake shoreline continuity/warping residual:** independently digitized same-age shoreline segments from a free official map plus DEM; anomaly in residual from local shoreline datum | Tests distributed deformation rather than ridge/scarp morphology | Shoreline facies transitions, wave-cut benches, differential compaction | Medium-high; depends on same verified MF-2323 product and defensible shoreline-age attribution | Distinct from current point/ridge predictors but closely related to candidate 1; do not run both as independent discoveries without preregistered separation |

The official competition's own numerical features and DEM must first be used under the authorized cached stack. No new external layer is proposed as viable until provenance, access, CRS, spatial coverage, and licensing are checked. Candidate 1 is the best *research priority* only; it is **not** authorized for implementation or submission without the lane assignment and data.

## Verification and blockers

- `data/` is absent, so no fresh hide-and-recover evaluation or leakage canary is possible here.
- `pytest` is not installed in the current environment (`pytest: command not found`); therefore no test pass result is claimed. Prior session test outcomes in dated reviews are historical, not rerun here.
- No completion claim is made for all competition-source verification, current live leaderboard refresh, organizer receipt validation, or complete fleet-registry uniqueness.
- No new TIFF was created. Existing downloadable TIFFs are historical artifacts and are not cleared for submission.
- The current README already contains the standing objective and prompt history. This review adds a concise dated assessment rather than duplicating the very long original request.

## Sources for independent review

- Official DrivenData competition and format/metric: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Official DrivenData leaderboard (time-varying): <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>
- DOE/NLR competition rules PDF: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- USGS GeoDAWN data release: <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and>
- USGS MF-2323 Lahontan metadata link documented in the repo: <https://geo-nsdi.er.usgs.gov/metadata/map-mf/2323/metadata.faq.html>
- INGENIOUS compilation: <https://gdr.openei.org/submissions/1391>
- Reference implementation: <https://github.com/drivendataorg/gems-prize-reference-solution>

## Run card (negative; no new experiment)

```json
{
  "hypothesis": "No candidate tested. Research priority only: paired two-datum Lahontan shoreline displacement may expose low-relief or buried faults.",
  "mechanism": "Estimate shoreline vertical offsets at two paleo-horizontal datums and separate constant displacement from regional tilt; not implemented or evaluated.",
  "named_non_fault_mimic": "Regional uplift/tilt or non-tectonic lake loading; also shoreline reworking and alluvial-fan burial.",
  "holdout_dti": {"label": "HOLDOUT-DTI", "evaluator_version": "not run", "withheld_positives": null, "ci95": null},
  "correlation_overlap_vs_registry": {"preplacement_surface": "not run", "final_dots": "not run", "reason": "No candidate raster generated; current instructions lack lane assignment and data/ is absent."},
  "raster_sha256": null,
  "validator_output": {"no_nan_inside_footprint": "not run", "values_in_0_1": "not run", "crs_shape_transform_match": "not run"},
  "submission_name": null,
  "submission_note": "No candidate produced; do not submit any historical file.",
  "verdict": "negative"
}
```
