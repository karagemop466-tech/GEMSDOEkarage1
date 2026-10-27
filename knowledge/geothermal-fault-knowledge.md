# Knowledge base — competition facts and geothermal-fault geology

Each statement carries a provenance tag. **MEASURED** = computed in this repository from the pinned rasters (file named). **OFFICIAL** = organizer text (link; fetched by a sibling repo whose text was read here — re-check manually, drivendata.org/nlr.gov are unreachable from this sandbox). **SIBLING** = measured in a sibling GEMSDOE repository (link). **TEXTBOOK** = standard structural-geology/geothermal literature, cited for orientation, not used as a number.

## 1. Competition facts

| Fact | Value | Provenance |
|---|---|---|
| Metric | distance-weighted Tversky index, α = 0.2 (FP weight), β = 0.8 (FN weight), triangular kernel of 300 m (3 px) radius | OFFICIAL — https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/ |
| Consequence | a predicted pixel helps only if its realised kernel credit exceeds 0.2 × DTI; dense soft maps lose to sparse binary dots | MEASURED — `src/gemsk/metric.py`, `tests/test_metric.py` |
| Grid | 3730 rows × 3292 cols, 100 m, EPSG:32611, transform (100, 0, 243350, 0, −100, 4508550); footprint 5,167,373 valid px | MEASURED — `sample_submission.tif`, `training_features.tif` |
| Training labels | `existing_faults.tif` ≡ `labels.tif`: 60,988 fault pixels (INGENIOUS GDR 1391 Quaternary fault traces, rasterised) | MEASURED + OFFICIAL (rules PDF https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| Hidden labels | expert-mapped new faults (NLR/USGS) + USGS Qfaults; known faults are **not** masked from scoring | OFFICIAL — rules PDF; https://community.drivendata.org/t/known-faults-masking-in-the-metric/11516 |
| Implied hidden set size | ≈7,900 px (back-solved from the 0.2778 family's score ladder) | SIBLING — GEMSDOE32 docs (OWNER-REPORT scores) |
| Features | 19 float32 GeoDAWN/DEM bands: mag_anom, rtp, tmi_hg, geod_2ndinv, iso_grav_anom_slope, tc, geod_shearrate, geod_dilaterate, tmi_vg, deq_n100a15, iso_grav_anom_vg, det_elev, iso_grav_anom, tmi, depth_to_base_surf, ieq_n100a15, cond_surf, iso_grav_anom_hg, det_elev_slope; nodata −3.4028234663852886e+38 | MEASURED — band descriptions in the GeoTIFF |
| Submission format | one float32 band, same CRS/shape/transform; values in [0, 1]; null allowed outside bounds; .tif or .zip | OFFICIAL — problem description / submission page |
| Cadence and prizes | 3 submissions/week; Phase 1 $50k (withheld subset), Phase 2 $250k (expert-updated labels); finalists submit reproducible code; generative-AI use must be disclosed; U.S. eligibility | OFFICIAL — rules PDF |
| Leaderboard context | 0.4437 / 0.3916 / 0.3904 top three on 2026-10-26 | SIBLING snapshot (GEMSDOE32) — recheck https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ |

## 2. What the data say about where unmapped faults are (MEASURED here)

| Statement | Number | File |
|---|---|---|
| Withheld catalogue strands cluster next to visible ones | 67% of withheld truth within 15 px (1.5 km) of a visible strand, an area that is 26% of the footprint | `evidence/exp1b_truth_vs_distance_to_visible_interleaved.json` |
| Density lift by distance (interleaved) | 0–3 px 3.7×, 3–4 px 4.1×, 4–6 px 3.7×, 6–8 px 3.0×, 8–10 px 2.4×, 10–15 px 1.7×, 15–20 px 1.1×, 20–30 px 0.7×, 30–40 px 0.4×, >40 px ≤0.23× | same |
| Blocked-holdout artifact | with 20 km withheld blocks the prior inverts (distance to *visible* faults is large everywhere inside the block), so blocked holdouts under-rate near-field hypotheses and over-rate far-field ones | `evidence/exp1b_truth_vs_distance_to_visible.json` vs interleaved |
| Single-feature AUCs on withheld truth | all 0.35–0.57 (no feature alone carries label information; no leakage) | `evidence/leakage_canary_aucs.json` |
| Faults are *not* contour-oblique | contour-obliquity gate AUC 0.41–0.44 (worse than chance): normal-fault scarps in the Basin and Range run range-parallel, i.e. contour-parallel, like shorelines | `evidence/exp2_gpcz_holdout.json` (pre-registration note) |

## 3. Geology used by the GPC-Z lane

| Concept | Statement | Provenance |
|---|---|---|
| Basin-and-Range normal faults | Range-front normal faults dip basin-ward; the hanging wall (basin) is down-dropped, so the scarp's free face **faces the basin**. Fault damage zones and synthetic/antithetic splays occur within a few hundred metres to a few kilometres of the master trace. | TEXTBOOK (e.g., Stewart 1980 "Geology of Nevada"; Faulds & Varga 1998 on accommodation zones) |
| Gravity polarity | Basin fill is less dense than bedrock; the isostatic residual gravity gradient and the depth-to-basement surface point toward the basin depocentre. A topographic step whose downhill direction agrees with the gravity/basement deepening direction is **polarity-concordant** with a normal fault; a step facing the other way is more likely a terrace riser, shoreline berm, road cut or levee. | TEXTBOOK (Blakely 1995 "Potential Theory in Gravity and Magnetic Applications"; Jachens & Moring 1990 basin-depth maps of Nevada) |
| Why faults are off-catalogue | INGENIOUS compiled existing maps (mostly 1:250k–1:100k); short (< 2–3 km), low (< 5 m) and partly buried strands next to mapped master faults are the typical omissions found when 1 m LiDAR becomes available. Power-law fault-length scaling implies a deficit of short faults in regional compilations. | TEXTBOOK (Scholz 2019 "The Mechanics of Earthquakes and Faulting", fault-population scaling); SIBLING (19GEMSDOE power-law budget note) |
| Geothermal relevance | Great Basin geothermal systems concentrate at fault terminations, step-overs, accommodation zones and intersections where permeability is maintained; mapping missed strands near known ones is precisely the expert task described in the rules. | TEXTBOOK (Faulds et al. 2011, GRC Transactions; Faulds & Hinz 2015 play-fairway) |
| Named mimics (non-fault processes producing the same signal) | Lake Lahontan and other pluvial shoreline berms (contour-parallel steps, often basin-facing!), alluvial-fan terrace risers, piedmont roads/canals/railroad grades, playa margins. The polarity gate removes the away-facing half; the near-catalogue prior reduces exposure to isolated shorelines; **basin-facing shorelines near faults remain an unmitigated risk** (IR-K1-OBLIQ-01). | TEXTBOOK (Reheis 1999 pluvial lake maps); MEASURED (H2 falsified) |

## 4. Local-instrument limits (why no live estimate is given)

| Statement | Provenance |
|---|---|
| Catalogue-truth holdouts rank live scores weakly across detector families (best local instrument Spearman ≈ 0.51; n = 12) | SIBLING — GEMSDOE32 covariate audit |
| Within one family holdout and live agree well (ρ ≈ +0.84), so holdouts are good for *within-recipe* choices (budget, gating) | SIBLING — GEMSDOE32 |
| Files already pruned ≤2 px from the full catalogue score ≈0 on any catalogue holdout by construction | MEASURED — `evidence/exp1_field_screen.json` |
| Far-from-catalogue / blind-basin designs scored 0.0000–0.0009 live | SIBLING — owner's ledger (OWNER-REPORT) |
