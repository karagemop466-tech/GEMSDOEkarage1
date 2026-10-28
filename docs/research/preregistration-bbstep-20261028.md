# Pre-registration: H-K1-BBSTEP (28 October 2026)

Lane executed this session. Not an assigned parallel-run paragraph (none was
supplied). Stay inside this mechanism; do not jitter dots to dodge the lattice.

## Hypothesis

Buried intra-basin normal faults produce **aligned isostatic-gravity and
depth-to-basement gradient ridges where topographic slope is low**. USGS
Qfaults / INGENIOUS catalogues are scarp-based, so this signature can exist
off-catalogue.

## Layers (competition `training_features.tif` only)

- `iso_grav_anom`, `iso_grav_anom_hg`
- `depth_to_base_surf`
- `det_elev_slope` (veto, not a vote)
- optional corroboration: `rtp`

## Signature

Multiscale NMS ridges of gravity and depth-to-basement; sign-invariant
gradient alignment (`cos²`); low-slope gate ≥ 0.50–0.55; 2 px visible-catalogue
apron; Poisson packing near 2.8 px.

## Named non-fault mimic

Lithologic contacts, volcanic-flow density edges, basin-fill compaction steps.

## Difference vs this repo and the nine focus sites

H19-5 / GEMSDOE24–33 leaders are topographic ridge / scarp families.
GPC-Z requires topographic steps facing the basin. HMAS uses magnetic troughs
and sinter. BB-STEP **vetoes high slope**.

## Experiments (budget 3)

1. Leakage canary on each component. AUC > 0.90 = alarm.
2. Fold-local hide-and-recover vs GEMSDOE32 B2 on the same evaluator.
3. Slope-gate / budget sweep of the same lane.

## Stop rules

Spearman > 0.90 or > 70% of dots within 3 px of a registry raster, on the
surface and on the final dots, is a duplicate. Literal lattice inclusion is
not weakened. No weekly slot is spent here.
