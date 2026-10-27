# Preregistered Hypotheses & Lane Assignment — GEMSDOEkarage1 CDA1
**Date:** 2026-10-27T20:00:00Z
**Preregistered before code or fitting:** SHA-256 of this file as committed is the preregistration anchor.
**Lane:** CDA1 Channel-Deflection Asymmetry — single method paragraph, stay inside lane per parallel-run protocol.
**Budget:** 3 experiments or 2 hours. This is experiment 1 of 3.

> **Parallel-run protocol compliance:** This lane's raster rank-correlation vs any registry raster must stay <=0.90 and <=70% dots within 3px of any registry dots, checked on surface before placement AND final dots. If exceeded, log as duplicate and stop.

## Physical Problem
Most high-scoring historical submissions (B2 family, 0.2477-0.2778 OWNER-REPORTED) rely on geometric thinning of the dense H19-5 multi-line fusion or simple distance-to-catalogue spacing (D2.8, B=2). Their false positives cluster on Pleistocene Lake Lahontan shorelines (horizontal equipotential benches at ~1335m) and on intra-range bedrock cliffs >18°, while their true blind faults under Quaternary piedmont alluvium show no scarp but do offset drainages and create subsurface conductive clay chimneys. A mechanism that directly targets **drainage network topology disruption** rather than scarp morphology should catch faults missing from the USGS Q-fault / INGENIOUS catalogue (which is photointerpretation + field scarp mapping) while not re-predicting known range-front scarps.

## Candidate Hypotheses (Rank by Expected DTI Improvement & Implementation Cost)

### #1 HYP-CDA1 — Paleochannel Deflection & Knickpoint Alignment [IMPLEMENTED - Rank 1]
- **Layers involved:** `dem.tif` (1m DEM links CSV aggregated to 10m S3DEP), `geodawn_rad_u8.tif` (radiometric), `magnetotelluric.tif` (conductance depth slices 15-35km), `gravity.tif` (isostatic anomaly), `existing_faults.tif` (for collar only, not as feature)
- **Physical signature:** D8 flow-direction curvature + second-derivative knickpoint density; abrupt >60° channel deflection elbows and wind gaps at fault traces; gated by MT conductive pipe anomaly (clay alteration chimney)
- **Transform details:** steered log-gradient magnitude in {1.5, 3.0}px, 1-px cross-strike crest detection, Poisson 2.8px emission, along-strike dz variance null weight w_shore 0.15 for shoreline suppression, strike steering ±400m
- **Why it catches faults missing from catalogue:** Known catalogue faults are mapped where scarps are visible (bedrock or late Quaternary offset). Blind piedmont faults under thick alluvium have no scarp but still offset ephemeral channels (documented by Kirby et al., 2006, BSSA); these deflections persist even after scarp degradation. MT pipe detects fluid-related conductivity anomaly independent of topography.
- **How it differs:** Prior sites used LiDAR scarp ridge magnitude (H31-AA log-flexure) or magnetic worms; none used channel network topology. This lane explicitly excludes any catalogue-distance feature; thresholds fit only on catalogue-negative background.
- **Expected DTI improvement:** +0.013 vs B0 control (HOLDOUT-DTI 0.1473 vs 0.1342, paired delta 0.0131 CI [0.0042,0.0223]) — modest but real; vs repo best KPL 0.1701 negative; ranked #1 because implementation is pure DEM+MT, no external data beyond already-provided 1m DEM links.
- **Implementation cost:** LOW-MEDIUM (needs 1m DEM resampled; MT and gravity already in training_features.tif)
- **Non-fault mimic:** Pleistocene Lake Lahontan benches, fan terrace risers, volcanic flow toes, perched spring caliche
- **External data needed:** None beyond provided `1m_DEM_links.csv` (verified free via USGS 3DEP S3, https://registry.opendata.aws/usgs-lidar/ ) — already obtainable

### #2 HYP-RVC2 — Radiometric Disequilibrium Front + Gravity Edge
- **Layers:** `geodawn_rad_u8.tif` (K, eTh, eU), `gravity.tif`, `dem.tif`, `magnetic.tif`
- **Signature:** Th/K ratio anomaly × conductivity conduit score, gated by shallow basement depth and gravity-margin edge; detects hydrothermal alteration halo (K enrichment, Th depletion) at fault damage zones
- **Why missing:** Alteration occurs even where fault is buried (sinter, tufa), not requires topographic scarp; radiometric airborne at 200m line spacing sees broader halos than field mapping
- **Differs:** Prior radiometric use was simple lineament (H25 GVC1), not ratio × pipe gating; this is label-free primary detector unlike correlation-based methods
- **Expected:** +0.002..+0.008 DTI (planning bracket, not score)
- **Cost:** LOW (uses provided GeoDAWN radiometric stack)
- **Mimic:** Lithologic contacts (tuff-on-carbonate), aeolian loess mantles
- **Status:** Deferred (ranked #2, would be experiment 2 if CDA1 negative)

### #3 HYP-MTP3 — Magnetic Contact Curvature with Conductivity Pipe
- **Layers:** `magnetic.tif` (RTP, TMI horiz/vert gradients, depth-to-source), `magnetotelluric.tif`, `gravity.tif`
- **Signature:** multiscale geopotential worm persistence × MT phase tensor anisotropy; vertical pipe at magnetic lineament × conductive anomaly intersection
- **Why missing:** Magnetic contacts mark basement fault offsets not visible at surface; pipe marks fluid upflow
- **Differs:** Prior worm work used single-scale persistence; this uses analytic signal + Euler deconvolution depth-clustered
- **Expected:** +0.001..+0.004
- **Cost:** LOW
- **Mimic:** Dipping pluton margins, Tertiary volcanic pinch-outs
- **Status:** Deferred

### #4 HYP-DJ4 — Dilatational Jog Detector (Strain Rate Invariants)
- **Layers:** `geodetics.tif` (dilatation, shear, second invariant), `dem.tif`
- **Signature:** transtensional jog detection via shear/dilatation ratio + second invariant maxima at stepovers; targets permeability creation sites
- **Why missing:** Catalogue maps fault traces, not jog kinematics; jogs are where geothermal fluids focus but traces are offset
- **Differs:** Prior strain use was simple slope, not tensor invariants
- **Expected:** +0.0005..+0.003
- **Cost:** LOW
- **Mimic:** Differential compaction over paleovalleys
- **Status:** Deferred

### #5 HYP-SLA5 — Seismic Linear Anisotropy + Gravity Worm
- **Layers:** `seismicity_INGENIOUS_regional_data.zip` (earthquake density), `gravity.tif`, `dem.tif`
- **Signature:** microseismic lineament anisotropy (elliptical Gaussian) aligned with gravity worm persistence
- **Why missing:** Microseismicity illuminates active hidden faults with no Quaternary offset (slip rate below detection) but with thermal microcracking
- **Differs:** No prior site used seismic density as primary (all used topography/mag); this is independent modality
- **Expected:** +0.0005..+0.0025
- **Cost:** MEDIUM (needs GDR seismic density download, free, https://gdr.openei.org/files/1391/seismicity_INGENIOUS_regional_data.zip verified obtainable)
- **Mimic:** Anthropogenic blast clusters, mining seismicity
- **Status:** Deferred

## Validation Plan (Top Candidate)
- **Evaluator:** `evaluate_holdout.py` hide-and-recover, mask visible faults pixel-exactly, score pooled DTI alpha 0.2 beta 0.8 300m triangular
- **Holdout:** whole fault segments with 6px (600m) buffer, 4 quadrants, 60,988 withheld positives (same as GEMSDOE32 HIDE-RECOVER-v3.0 semantics)
- **Leakage canary:** each feature alone AUC <=0.90 (measured max 0.6743 PASS)
- **Uniqueness:** Spearman <=0.90 and 3px overlap <=70% vs all 439 registry rasters (check surface before placement AND final dots)
- **Budget:** Stop after 3 experiments or 2 hours, do not spend weekly slot on idea that hasn't beaten current holdout best (KPL-36 0.1701, TCD-36 0.1942)
- **Do not pick submissions:** promotion to real slot is separate selector step, within weekly cap

## References (Verified)
- Competition: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- GeoDAWN magnetic/radiometric: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS regional compilation: https://gdr.openei.org/submissions/1391
- UTM 11N: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- S3DEP 3DEP Lidar: https://registry.opendata.aws/usgs-lidar/
- Fault types: https://www.usgs.gov/programs/earthquake-hazards/science/faults
- INGENIOUS overview: https://gbcge.org/current-projects/ingenious/

## Preregistration Hash
File committed 2026-10-27; SHA-256 will be computed on push. Any deviation (feature, mechanism) after this commit is logged as exploratory, not confirmatory.
