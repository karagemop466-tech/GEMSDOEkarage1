# New geological hypotheses — GEMS fault discovery (28 Oct 2026)

Status: qualitative, ranked proposals. Ordering reflects expected promise relative to implementation cost; it is **not** a measured or predicted DTI improvement and is **never written as a score**. Per Rule 3, any holdout number would be labelled HOLDOUT-DTI (evaluator version, withheld positives, 95% CI); none has been computed because the competition training data are login-walled and absent from this checkout.

Target: unmapped faults (the GEMS label is fault presence, not direct proof of geothermal vents). Every hypothesis names the layers, the physical signature, why it should catch faults missing from the USGS/INGENIOUS catalogue, the non-fault mimic confounder, how it differs from what is already in this repo, and the specific free official source.

## H1 — Signed two-scale magnetic/gravity offset with topography (top candidate to validate)
**Layers:** USGS GeoDAWN RTP magnetic total-field, isostatic/residual gravity, 100 m DEM topography. (GeoDAWN products are public: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and ; DOI 10.5066/P93LGLVQ. Listed as obtainable; official bytes not fetched or authenticated this session.)
**Physical signature:** A buried fault displaces magnetic basement and gravity density at two scales — a broad, signed offset (regional throw) plus a narrow signed gradient edge at the trace. Testing *signed* (not unsigned amplitude) cross-profiles at two scales catches blind faults with no mapped surface expression.
**Why off-catalogue:** The USGS/INGENIOUS catalogue is trace-mapped; a blind discontinuity under cover with no surface scarp is absent by construction. A signed offset is a direct structural discontinuity test rather than a proxy amplitude.
**Mimic (non-fault process):** Lithologic contacts, volcanic flow edges, and magnetic/gravity survey acquisition-block boundaries can produce signed offsets.
**How it differs from the repo:** The repo's HMAS lane uses *unsigned* analytic-signal trough / edge magnitude channels (hmas_analytic_sig_log, hmas_mag_destruct_trough). H1 tests *signed* profile displacement and a gravity–magnetic consistency test, which is a different statistic; fleet-wide novelty is unverified.
**Expected DTI gain / cost:** Qualitative medium-high gain at medium cost (reuses bridged potential-field layers; no new external data beyond GeoDAWN).
**Validation:** validate H1 alone on the spatially-blocked hide-and-recover holdout before any slot; single-feature leakage canary (AUC must be ≤ 0.90).

## H2 — Radiometric K/eTh alteration-boundary residuals aligned with magnetic edges
**Layers:** USGS GeoDAWN potassium (K), equivalent thorium (eTh), total count (TC), and RTP magnetics.
**Physical signature:** A fault-related hydrothermal alteration halo shifts K/eTh and produces a localized radiometric boundary; co-location with an oriented magnetic edge raises confidence. Use local-background-normalized residuals (not raw plume amplitude).
**Why off-catalogue:** Alteration under alluvial cover can be geophysically expressed with no mapped fault trace, so it is absent from the trace-based catalogue.
**Mimic:** Weathering, potassium-rich intrusions, and radiometric acquisition blocks.
**How it differs from the repo:** The repo has raw radiometric plume channels (geodawn_blk_bi214_radon_ridge, geodawn_blk_kth_alteration) but H2 tests *directional background-subtracted residuals* and explicit edge co-location.
**Expected DTI gain / cost:** Qualitative medium gain at medium cost.
**Validation:** single-feature leakage canary on holdout; then joint with H1 only if H1 passes.

## H3 — Catchment drainage asymmetry conditioned on drainage area (USGS 3DEP)
**Layers:** USGS 3DEP DEM-derived flow direction, flow accumulation, and drainage-area grids (https://www.usgs.gov/3d-elevation-program; public tiles; local coverage not checked).
**Physical signature:** Repeated cross-valley drainage asymmetry among adjacent, similarly-sized catchments indicates a displaced or tilted surface controlled by a subsurface trace.
**Why off-catalogue:** A degraded or buried fault can control drainage without a mappable scarp, so it is missed by the trace catalogue.
**Mimic:** Stream piracy, alluvial-fan deposition, and differential erosion.
**How it differs from the repo:** The repo has a pixel-level LiDAR scarp/asymmetry channel (lidar_tectonic_asymm_chain); H3 is catchment-integrated and explicitly conditioned on drainage area, a different scale and statistic.
**Expected DTI gain / cost:** Qualitative low–medium gain at high cost (needs DEM hydrology processing and tile coverage checks).

## H4 — Sampling-aware thermal-probe residuals against gravity boundaries
**Layers:** GDR INGENIOUS 2 m shallow temperature-probe survey (F2mDAB; https://gdr.openei.org/submissions/1391, DOI 10.15121/1881483, CC BY 4.0) plus GeoDAWN gravity and terrain. (Attribution confirmed in the repo manifest; official raw bytes not downloaded or authenticated this session.)
**Physical signature:** Cross-fit probe temperature against terrain, solar aspect, and access bias; map residuals. Concentrated warm residuals coincident with gravity boundaries indicate concealed upflow near an unmapped structure.
**Why off-catalogue:** Concealed flow can lie adjacent to, not on, a mapped trace; the residual pattern targets the structure, not a catalogue line.
**Mimic:** Solar heating, shallow groundwater, and access-biased station siting (roads/trails).
**How it differs from the repo:** The repo's thermal plume is a raw strike-projected probe channel (ing_f2mdab_aniso_plume); H4 explicitly models sampling bias via cross-fitting before comparing to gravity.
**Expected DTI gain / cost:** Qualitative low–medium gain at high cost (requires probe cross-fit and bias modelling).

## H5 — Blind stepover relay ramps from magnetic-lineation terminations
**Layers:** USGS GeoDAWN TMI magnetic lineations plus DEM curvature.
**Physical signature:** Terminations, offsets, and relay-ramp geometry of magnetic lineations mark blind stepover faults; curvature concentrates at the ramp.
**Why off-catalogue:** Stepovers between mapped traces may be unmapped and absent from the catalogue.
**Mimic:** Intrusive contacts and dike swarm terminations.
**How it differs from the repo:** No existing repo channel tests magnetic-lineation termination/relay geometry.
**Expected DTI gain / cost:** Qualitative medium gain at medium–high cost.

## Recommended validation order
1. H1 first (best cost/gain balance; reuses bridged potential-field layers; no new external fetch required beyond GeoDAWN, already bridged as a mirror).
2. H2 if H1 passes the leakage canary.
3. H3/H4/H5 only if external data availability is confirmed (name the source, check obtainability, then fetch pinned bytes).

**Gate reminder:** a candidate may touch a weekly submission slot only after it beats the frozen same-evaluator holdout best on a spatially-blocked hide-and-recover holdout, passes the single-feature leakage canary (AUC ≤ 0.90), and passes the surface + dot registry gates. Negative results are deliverables.
