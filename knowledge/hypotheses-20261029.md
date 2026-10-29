# Pre-implementation hypothesis slate — 2026-10-29

**Status: proposals only; no lane assigned, no experiment run, no score estimated.**
This slate is a bounded review of ideas to consider only after the owner supplies
the exact single-method paragraph, the shared template provenance is repaired,
and authenticated inputs become available. It is not permission to select or
implement a method outside that lane.

## Novelty and scope

I searched the current repository's hypothesis/research notes and the available
source records for GEMSDOE24/25/27/28/30/31/32/33/36. The exact operators below
were not found as executed, validated methods in those checked records. This is
**not** proof of novelty across every peer repository, private submission, or
organizer entry. Broad neighboring themes are already present: strain plus
positive seismicity, geochemistry/geothermometry, and thermal/hydrologic data.
The most defensible difference is the specific preregistered contrast described
below, not a claim that the underlying data or geology are new.

| Rank | Candidate | Named layers / data | Physical signature; why a fault may be off-catalogue | Non-fault mimics | Difference from checked prior work | Qualitative DTI upside / cost |
|---|---|---|---|---|---|---|
| **1** | **Completeness-conditioned seismic-shadow at loaded strain gradients** | Shared `training_features.tif` only, conditional on authoritative band metadata confirming semantics: `geod_shearrate`, `geod_dilaterate`, `geod_2ndinv`, and the two earthquake-density layers `deq_n100a15` / `ieq_n100a15`. The exact band definitions, units, event window, and completeness corrections must be verified before use; do not infer abbreviations. | A locked or slowly slipping buried segment can accommodate geodetic strain while producing a local deficit in independent seismicity. Test a spatially coherent *negative event-density residual conditional on strain and catalog completeness*, not a raw low-density patch; require a localized boundary/edge, not a broad smooth basin. Distributed deformation under young cover may leave no continuous scarp for the existing-fault catalogue. | Uneven seismic-network detection, event-catalogue completeness changes, aseismic creep, interpolation/smoothing of the geodetic model, geothermal production, and lithologic variation. | Checked prior proposals (`TRDS-Bridge`, `BERB-STC`, and GEMSDOE33 `seisdil`) emphasize positive strain/seismicity or relay-tip corridors. The proposed falsifiable contrast is a completeness-adjusted seismic *deficit* at high strain. This is a narrow local-record distinction, not global novelty. | **Medium, uncertain upside; low-to-medium implementation cost.** No external download if authenticated shared inputs contain the described bands; feature-by-feature canary and spatially blocked whole-segment holdout are essential. |
| **2** | **Aqueous-geochemistry mixing residuals along blind structural corridors** | GDR INGENIOUS well/spring geodatabase: raw aqueous-analyte observations and locations, only after a schema/units/coordinate audit. The official page says the compilation includes spring/well aqueous-geochemistry analyses and is CC BY 4.0. Do not assume any particular analyte or ratio exists until the data bytes are available. | A concealed permeable fault may connect deep fluids to shallow aquifers, producing spatially coherent mixing/non-equilibrium residuals relative to local lithology and evaporative concentration. A buried structure can leak fluid without a mapped Quaternary surface trace. | Playa evaporation, water-rock reactions unrelated to a fault, seasonal recharge, wells selected for geothermal exploration, sparse/access-biased sampling, mixed laboratory methods, and duplicated source records. | Peer records already discuss thermal probes, geothermometers, and aqueous chemistry. The candidate is specifically raw-sample mixing residuals with lithology/evaporation controls, not a temperature plume, K/Th raster, or another geothermometer threshold. Peer-method novelty is **unverified**. | **Medium potential if coverage is adequate; medium-high data/engineering cost.** The public listing and license are verified; the 19.85 MB well/spring ZIP returned HTTP 500 when fetched, so its schema and actual study-area coverage are not verified. No local chemistry data were inspected. |
| **3** | **Fault-focused hydrograph and groundwater-level anomalies** | USGS Water Data for the Nation modern API: `monitoring-locations`, `time-series-metadata`, and (where present) `daily`, `continuous`, or `field-measurements` for stream discharge, water temperature, or groundwater levels. Study-area coverage, site types, periods of record, and parameter availability have **not** been queried. | A hydraulically connected blind fault may focus groundwater or geothermal discharge and create a persistent seasonal amplitude/phase residual relative to nearby catchments or wells. The residual/contrast—not the existence of a sampled gage—would be the hypothesized signal. Faults beneath basin fill may affect flow without a mapped scarp. | Reservoir/irrigation operations, pumping, precipitation/snowmelt, basin geometry, sensor changes, site-placement bias, and aquifer boundaries unrelated to faults. | The checked nine-site records mention thermal and geochemical points but contain no hydrograph/groundwater-level residual method. This is only a repository-record search; it is not a fleet-wide novelty claim. | **Low-to-medium, speculative upside; high cost and coverage risk.** USGS API documentation is public, but no actual observations were queried or downloaded. Sparse, irregular points may not support the competition's 100 m grid. |

The ordering is a qualitative **expected-benefit-per-cost** judgment, not a numeric
DTI estimate. No score, probability of winning, or leaderboard projection is
claimed. Candidate 1 is ranked first because it can be tested without adding an
unverified external raster, not because its effect has been demonstrated.

## Mandatory validation if and only if the gates are resolved

1. Obtain the exact assigned lane paragraph. Do not infer it from these ideas or
   older session proposals.
2. Restore the canonical owner-assigned shared template, resolve the recorded
   vendor/source hash mismatch, and use its `evaluate_holdout.py` and
   `submission_writer.py`. Do not edit or privately fork the vendored tools.
3. Authenticate organizer inputs. Recompute catalogue-derived features from
   visible faults only; withhold complete fault segments with a spatial buffer;
   mask visible faults pixel-exactly. Use pooled DTI α=0.2, β=0.8, and the
   300 m triangular kernel.
4. Test each feature by itself first. Any single-feature AUC >0.90 is leakage
   until resolved. For H1, pre-register the completeness model and sign of the
   seismic-deficit contrast before opening the held-out labels.
5. Hide and recover whole fault segments, not random pixels. Record HOLDOUT-DTI
   only with evaluator version, withheld-positive count, and 95% CI. Do not
   translate it into an organizer score.
6. Compare candidate surfaces to the complete registry before placement, then
   compare final dots. Stop if absolute rank correlation >0.90 or >70% of
   candidate dots are within 3 px of a registry raster. Do not jitter, rename,
   change representation, or exempt a calibration/witness file to evade this
   gate.
7. Stop after at most three experiments or two hours. Do not select a live
   submission slot. A separate selector must check the authenticated portal's
   current allowance.
8. Finish any actual run with a JSON card containing the hypothesis, mechanism,
   non-fault mimic, holdout result/CI, registry correlation/overlap, saved-raster
   SHA-256, validator output, filename/note (≤140 characters), and promote or
   negative verdict. No raster means hashes, validation, and submission fields
   must be null/not-run, not invented.

## Sources and obtainability

- [GDR INGENIOUS regional dataset](https://gdr.openei.org/submissions/1391),
  DOI [10.15121/1881483](https://doi.org/10.15121/1881483): page states public
  access, CC BY 4.0, and lists well/spring aqueous geochemistry. The advertised
  [well/spring ZIP](https://gdr.openei.org/files/1391/wellspringdata.gdb.zip)
  returned HTTP 500 during this review; no local bytes, attributes, or coverage
  were verified.
- [USGS modernized Water Data API collections](https://api.waterdata.usgs.gov/ogcapi/v0/collections)
  and [migration guide](https://api.waterdata.usgs.gov/docs/ogcapi/migration/):
  documentation lists monitoring locations, time-series metadata, daily and
  continuous values, and field measurements. This verifies an official public
  interface, **not** the presence of usable sites in the competition footprint.
- Competition feature definitions and access are governed by the
  [official DrivenData problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
  Its data tab redirects to login in this environment.

**Decision for this session:** all three candidates remain proposals. The
active blocker is administrative/provenance/data access, not lack of additional
hypothesis prose. No slot, TIFF, experiment, holdout score, or submission was
produced.
