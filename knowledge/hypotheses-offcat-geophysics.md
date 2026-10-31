# Off-catalogue geophysics lane — candidate hypotheses

Ranked by expected leaderboard DTI improvement vs the nine focus-site baseline
(best owner-reported 0.2778 at GEMSDOE32; unverified) and implementation cost.
Implemented: H1 (this session). Evidence: `docs/data/offcat_run_card.json`,
`docs/data/nine_site_eval.json`, `docs/data/offcat_feature_screen.json`.

## Context (measured from restored raster bytes)

All nine focus-site rasters are catalogue-proximal dotted fields: every one has
100 % (or ~100 %) of its dots within 3 px of another focus-site raster, so none
is unique under the literal 70 % / 3-px gate. Their catalogue hide-and-recover
holdout DTI values (alpha 0.2, beta 0.8, 300 m kernel, withheld catalogue
segments) are: GEMSDOE25 0.1023, GEMSDOE30 0.1023 (identical mask to GEMSDOE25),
GEMSDOE24 0.0975, GEMSDOE27 0.0972, GEMSDOE33 0.0553, GEMSDOE28 0.0315,
GEMSDOE31 0.0327, GEMSDOE32 0.0047, GEMSDOE36 0.0049. GEMSDOE32's owner-reported
0.2778 coexists with a holdout DTI of 0.0047 — below random — because B2 is
GEMSDOE25 with catalogue-adjacent dots removed (off-catalogue shift). The
leaderboard therefore rewards dots on faults MISSING from the USGS/INGENIOUS
catalogue; the catalogue holdout measures re-finding mapped faults and does not
predict leaderboard score. Hidden organizer truth is unavailable, so NO leaderboard
estimate can be defensibly produced; every number below is a hypothesis to be
tested on the holdout and confirmed only by an organizer submission receipt.

## H1 — Off-catalogue geophysical edge composite (IMPLEMENTED)

- **Layers:** `training_features.tif` 19-band competition stack (mag_anom, rtp,
  tmi_hg, iso_grav_anom_hg, ieq_n100a15, cond_surf, det_elev_slope, plus
  catalogue and registry masks).
- **Physical signature:** blind geothermal faults — no mapped trace — marked by
  coincident hydrothermal magnetite destruction (magnetic lows), alteration /
  blind-basin gravity lows, source-edge gradients (TMI/gravity horizontal
  gradient), seismicity density, subsurface conductivity and subtle detrended
  elevation slope scarps. Each band rank-normalised, equal-weighted, sign-flipped
  so high = anomalous; low bands (rtp, tmi, iso_grav_anom, mag_anom) inverted
  because lows are the anomaly.
- **Why it catches catalogue-missing faults:** every dot is forced >5 px from the
  catalogue and outside the 3-px halo of all nine registry rasters, so it can only
  credit unmapped structure; catalogue proximity (the focus-site play) is excluded
  by construction.
- **Difference from repo:** all prior lanes dot near catalogue faults
  (catalogue collar / damage zone) or in "novel territory" with no geophysical
  input. H1 fuses multi-sensor geophysics inside the off-catalogue domain.
- **Expected DTI improvement:** holdout DTI will read ~0 (off-catalogue dots do not
  recover withheld catalogue segments — that is the point; it is NOT a leaderboard
  estimate). Leaderboard impact is unknowable without organizer truth.
- **Cost:** low — feature stack already pinned and restored; one script, ~1 min runtime.

## H2 — Euler deconvolution magnetic contact depth (NOT implemented)

- **Layers:** rtp / tmi magnetic bands + depth_to_base_surf.
- **Physical signature:** magnetic-contact depth solutions from 3-D Euler
  deconvolution cluster at blind fault contacts; shallow solutions mark near-surface
  blind structures absent from the catalogue.
- **Why off-catalogue:** Euler solutions are point estimates of source location,
  not catalogue traces.
- **Difference from repo:** repo ran Euler on TMI/gravity (H-E1b/H-E2, negative on
  catalogue holdout) but never as an off-catalogue dot-emission mask.
- **Cost:** medium — requires an Euler implementation and parameter sweep; holdout
  test possible with existing labels mirror.
- **Status:** not attempted; holdout screening needed before any slot.

## H3 — Radiometric potassium-thorium alteration halo (NOT implemented)

- **Layers:** external `geodawn_rad_u8.tif` (USGS GeoDAWN K/Th/U/TC, K low from
  illite/clay alteration destroying K-feldspar; eTh/U anomalies) + cond_surf.
- **Physical signature:** hydrothermal alteration halos around blind geothermal
  faults produce K depletion and eTh/U anomalies with no surface fault trace.
- **Why off-catalogue:** alteration halos extend beyond mapped traces into
  unmapped damage zones.
- **Difference from repo:** geodawn radiometrics exist as a pinned external mirror
  but no lane consumes them for dot emission.
- **Cost:** medium-high — external mirror restore (~27 MB) plus co-registration
  check; GeoDAWN DOI 10.5066/P93LGLVQ (official, free).
- **Status:** not attempted; source obtainable from the pinned mirror.

## H4 — Seismicity-density lineament extension (NOT implemented)

- **Layers:** ieq_n100a15 / deq_n100a15 (earthquake density/distance) + det_elev_slope.
- **Physical signature:** active blind faults cluster microseismicity; lineaments
  extrapolated from seismic clusters beyond catalogue endpoints are new-fault
  candidates.
- **Why off-catalogue:** seismicity marks currently active structures irrespective
  of map status.
- **Difference from repo:** deq_n100a15 appeared only as one band in a 58-channel
  private stack (blocked, never scored); never used alone off-catalogue.
- **Cost:** low — bands already in the restored stack.
- **Status:** not attempted.

## H5 — Conductivity-surface conduit crests (NOT implemented)

- **Layers:** cond_surf (electrical conductivity) + iso_grav_anom_vg.
- **Physical signature:** geothermal fluids raise bulk conductivity; conduit
  crests at conductivity maxima over gravity lows mark blind upflows.
- **Why off-catalogue:** conductivity responds to fluid pathways, not map lines.
- **Difference from repo:** cond_surf unused by any lane.
- **Cost:** low — bands in stack.
- **Status:** not attempted.

## Ranking (expected leaderboard DTI improvement | cost)

1. H1 — implemented; multi-sensor fusion lowers single-mimic risk; verified unique
   (0.0 % forward 3-px overlap vs all nine registry rasters) and format-valid.
2. H4 — low cost, seismicity is a direct active-fault tracer; single-sensor risk.
3. H5 — low cost; conductivity is a strong geothermal fluid indicator but can
   mimic conductive playas/sediments.
4. H3 — strong alteration signal but requires external mirror co-registration.
5. H2 — medium cost; Euler depth solutions are model-dependent and were
   catalogue-holdout negative in prior sessions.

## Go / no-go rule

No weekly submission slot is spent on any hypothesis until its holdout result
beats the frozen comparable best on the spatially blocked holdout AND a format
receipt exists. Leaderboard confirmation requires an organizer submission receipt;
this checkout holds none.
