# Candidate geological hypotheses (ranked)

**Scope:** 3–5 hypotheses not yet tried, for the DOE GEMS Prize fault-discovery competition.
**Protocol:** validate the top candidate on the spatially-blocked holdout before touching a weekly submission slot. Do not spend a slot on an idea that hasn't beaten the current holdout best.

**Baseline to beat:** GEMSDOE32 `h33-h33-2-b2` owner-reported 0.2778 (focus-9 high; unverified, already submitted, not unique). All focus-9 leaders re-thin the H19-5 ridge skeleton and asymptote below ~0.295.

| Rank | Hypothesis (ID) | Layers involved | Physical signature targeted | Why it catches faults missing from USGS/INGENIOUS catalogue | Differs from repo / focus-9 | Expected DTI gain | Implementation cost |
|---|---|---|---|---|---|---|---|
| 1 | **H-UNQ-1** Radiometric-hydrothermal + fluvial-χ + gravity-margin off-catalogue detector (implemented: `scripts/generate_submission.py`) | 10 m 3DEP fluvial chi / channel-steepness; GeoDAWN Th/K & eU/K alteration; isostatic gravity margin edge; catalogue only for a 2 px collar | Linear hydrothermal alteration (Th/K, eU/K) co-located with gravity-margin edge + fluvial-χ knickzone/uplift anomaly — blind range-front fault | Catalogue maps only mapped/Quaternary surface faults; blind, low-relief, pre-Quaternary and hydrothermal-only faults are absent. Label-free except the collar. | Does NOT re-thin H19-5 (every focus-9 leader does). Radiometric-primary + fluvial-χ; cf. GEMSDOE33 THKCOND but swaps Th/K×conductivity for fluvial-χ + gravity margin. | Planning bracket only (not a score); +0.005–0.015 plausible vs re-thinned ceiling | Low — feature stack already cached |
| 2 | **H-UNQ-2** ASTER TIR thermal-inertia + hydrothermal alteration index | ASTER TIR (bands 10–14) thermal inertia / emissivity; GeoDAWN radiometric K, eTh, eU; DEM aspect/slope | Day/night thermal-inertia contrast + siliceous/opaline alteration (TIR spectral indices) along blind upflow zones | Blind faults with no surface scarp but active/paleo hydrothermal upflow show TIR alteration and thermal anomalies not in any fault catalogue | Not in repo; focus-9 uses LiDAR/radar/DEM morphology, not TIR thermal-inertia | +0.003–0.010 | Medium — requires ASTER TIR download (free, NASA/LPDAAC) |
| 3 | **H-UNQ-3** 10 m 3DEP curvature + ridge-closure to close LiDAR gap | 10 m 3DEP DEM (profile/plan curvature, ridge closure, fill sinks); fluvial χ | Blind range-front uplift recorded in curvature/ridge-closure where 1 m LiDAR is absent (24.63% gap) | LiDAR gap hides small scarps; 10 m 3DEP curvature captures the same range-front flexure at coarser scale, outside the catalogue | Focus-9 uses 1 m LiDAR scarp openness; H-UNQ-3 uses 10 m 3DEP curvature in the gap | +0.004–0.012 | Low — 3DEP is free (USGS) |
| 4 | **H-UNQ-4** Stage-2 spatial context / submodular consolidation of 2D halos | Any single-layer propensity (e.g. H-UNQ-1 output); submodular / spatial-context consolidation | 2D alteration / uplift halo consolidated into fault-length-scale predictions (Stage-2) | Single-pixel responses fragment real faults; consolidation recovers the full fault trace the catalogue misses | Repo computes per-pixel features; H-UNQ-4 adds a Stage-2 spatial consolidation step (cf. TCD-36 measured +0.008895) | +0.003–0.009 | Low — post-process on existing surface |
| 5 | **H-UNQ-5** Magnetotelluric resistivity + gravity joint inversion (deep blind faults) | MT (USGS/INGENIOUS or GDR #1391) resistivity; isostatic gravity; depth-to-basement | Conductive hydrothermal plume + density contrast over deep blind basement faults | Deep blind faults have no surface expression in QFaults but show MT resistivity lows + gravity margins | Not in repo; focus-9 is near-surface (LiDAR/DEM/radar); MT targets the basement | +0.002–0.008 | High — MT data coverage sparse; joint inversion non-trivial |

## Recommendation

**Validate H-UNQ-1 first.** It is implemented, label-free, deliberately unlike the focus-9 family (so it should pass uniqueness), low cost, and directly targets the mechanism the PhD synthesis identifies as the path past 0.2778 (radiometric + fluvial-χ + off-catalogue blind faults). Run it on the holdout via `scripts/evaluate_holdout.py` once DrivenData `labels.tif` is available; promote to a weekly slot only if holdout DTI beats the current best with paired 95% CI > 0.

**If H-UNQ-1 fails the holdout gate,** move to H-UNQ-2 (ASTER TIR) — obtainable free from NASA LPDAAC — and re-run the leakage canary (any single feature AUC > 0.90 = leakage) before any slot.

## Sources
- USGS 3DEP 10 m DEM: https://www.usgs.gov/3d-elevation-program
- USGS QFaults: https://www.usgs.gov/programs/earthquake-hazards/faults
- OpenEI GDR #1391 (INGENIOUS): https://gdr.openei.org/submissions/1391
- US Census TIGER/Line: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
- ASTER TIR (NASA LPDAAC): https://lpdaac.usgs.gov/products/ast_l1t/v003/
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- EPSG:32611: https://epsg.io/32611
