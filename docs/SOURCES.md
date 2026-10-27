# Source register — every link here was fetched live on 2026-10-27

Each row: what we verified, the live quote/fact we pulled, and whether it is
official (organizer / federal government) or third-party. Re-fetch any link
to re-verify.

## Official competition sources

| # | Link | What we verified live | Class |
|---|---|---|---|
| 1 | <https://www.drivendata.org/competitions/306/competition-doe-gems/> | Prize pool $300,000 ($50k Initial Round top-5 @ $10k, $250k Final Round top-5 @ $100k/$70k/$40k/$25k/$15k); end date **Dec 3, 2026, 11:59pm UTC**; external data allowed "provided you... possess the necessary licenses... and shareable with the challenge organizers" | **Official** |
| 2 | <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/> | Full problem description, dataset description (channel list), and the **exact DTI metric formula** with alpha=0.2, beta=0.8, R=300 m triangular kernel, and the worked example TPw=3.00/FPw=1.89/FNw=2.00→DTI=0.60. Submission format: EPSG:32611, 100 m, float32, single band, values in [0,1], same bounds as training data (outside = null/NaN) | **Official** |
| 3 | <https://www.drivendata.org/competitions/306/competition-doe-gems/data/> | Unauthenticated request redirects to `/accounts/login/` — **confirms login is required**, matching the task brief's own finding | **Official** |
| 4 | <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/> | **Live public leaderboard**, no login required. Top 5 on 2026-10-27: xiaofanhu 0.4544, cfld__ 0.3916, Batik Shirt Brothers 0.3911, BrandenKMurray 0.3724, No Fault of Our Own 0.3566 | **Official, organizer-confirmed** |
| 5 | <https://github.com/drivendataorg/gems-prize-reference-solution> | Reference U-Net + Monte Carlo cross-validation solution by Prof. John Lipor (Portland State). Confirms: features normalized per-channel to [0,1] with `np.nanmin`/`np.nanmax`, `TverskyLoss(alpha=0.2, beta=0.8, mode="binary")` from `segmentation_models_pytorch`, output written with `rasterio` using `fault_dataset.crs`/`.transform` taken directly from `labels.tif`. The repo's own `data/` folder is empty (`.gitkeep` only) — the reference authors also do not ship the real data in git | **Official (DrivenData org GitHub)** |
| 6 | <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and> | GeoDAWN = "Geoscience Data Acquisition for Western Nevada," airborne magnetic + radiometric survey, NW Great Basin, Nevada | **Official (USGS)** |
| 7 | <https://epsg.io/32611> | EPSG:32611 = WGS 84 / UTM zone 11N | **Official (EPSG registry)** |
| 8 | <https://en.wikipedia.org/wiki/Tversky_index> | Generic Tversky index definition, consistent with the competition's TI(alpha,beta) formula | Reference |

## Free, official, external geoscience data (for new hypotheses — see `research/hypotheses.md`)

All items below are published by the **U.S. Geological Survey** and the
**Great Basin Center for Geothermal Energy's INGENIOUS project** (DOE award
DE-EE0009254), the same two institutions the competition itself draws its
official `training_features.tif` layers from. All are **CC BY 4.0** licensed
and require **no login** for the landing page (we did not attempt the actual
multi-megabyte binary downloads from this sandbox — see `docs/LIMITATIONS.md`
§1 — but the pages, prices ($0), and licenses are independently confirmed).

| # | Dataset | Link | License | Size |
|---|---|---|---|---|
| 9 | INGENIOUS — Great Basin Regional Dataset Compilation (index page) | <https://gdr.openei.org/submissions/1391> | CC BY 4.0 | 9 files, 116.98 MB total |
| 10 | Shapefile for slip tendency and dilation tendency, Quaternary faults, Great Basin (Siler, USGS data release) | <https://doi.org/10.5066/P9YL58W6> → <https://www.sciencebase.gov/catalog/item/6296974dd34ec53d276bb33d> | Public domain / USGS | Shapefile + KMZ, ~34 MB full study |
| 11 | Heat flow maps and supporting data for the Great Basin (DeAngelo et al., USGS data release) | <https://doi.org/10.5066/P9BZPVUC> → <https://www.sciencebase.gov/catalog/item/6297d2fad34ec53d276c5b28> | Public domain / USGS | 124 MB zip, 3 maps + well-residual point coverage |
| 12 | Electrical Conductance Maps (MT), Great Basin | <https://doi.org/10.5066/P9TWT2LU> | Public domain / USGS | via ScienceBase |
| 13 | Regional geophysical maps (gravity & magnetics), Great Basin | <https://doi.org/10.5066/P9Z6SA1Z> | Public domain / USGS | via ScienceBase |
| 14 | Elevation Trend and Detrended Elevation, Great Basin | <https://doi.org/10.5066/P9MQRCBY> | Public domain / USGS | via ScienceBase |
| 15 | Quaternary Volcanics (vents + flows shapefiles) | <https://gdr.openei.org/files/1391/great_basin_q_volcanics.zip> (linked from #9) | CC BY 4.0 | 9.44 MB |
| 16 | Paleo Geothermal Features (sinter/tufa deposits) | <https://gdr.openei.org/files/1391/paleo_geothermal_regional.zip> (linked from #9) | CC BY 4.0 | 82 KB |
| 17 | Well and Spring Temperature and Chemistry (geodatabase) | <https://gdr.openei.org/files/1391/wellspringdata.gdb.zip> (linked from #9) | CC BY 4.0 | 19.85 MB |
| 18 | Earthquake Density Models (Nevada Seismological Lab) | <https://gdr.openei.org/files/1391/seismicity_INGENIOUS_regional_data.zip> (linked from #9) | CC BY 4.0 | 22.98 MB |
| 19 | Geodetic Shear and Dilation Models (Nevada Geodetic Laboratory) | <https://gdr.openei.org/files/1391/geodetics_INGENIOUS_regional_data.zip> (linked from #9) | CC BY 4.0 | 51.99 MB |
| 20 | INGENIOUS project site | <https://gbcge.org/current-projects/ingenious/> | — | background only |

## Task-brief-supplied, third-party-hosted mirrors (NOT independently verified by us)

The project brief also supplied Dropbox links claimed to mirror the official
competition data (`GEMS_96647.pdf`, `example_submission.tif`,
`existing_faults.tif`, `gems-geodawn-numerical-features.tif`,
`Digital-elevation-model-links-JSON.pdf`) and a document at
`docs.nlr.gov/docs/fy26osti/96647.pdf`. We could not reach `dropbox.com` or
`docs.nlr.gov` from this sandbox at all (see `docs/LIMITATIONS.md` §1), so we
have **not** verified these are genuine, unaltered organizer files. Treat
them as **unverified-by-us, use at your own risk**, and always prefer the
authenticated DrivenData data tab (#3 above) as the primary source.

## Irregularities flagged

1. The task brief states two different "current leaderboard high score"
   values at different points (**0.4413** and, later, **0.3195**). Neither
   matches the live public leaderboard top score we fetched (**0.4544**,
   #4 above). We report the number we could verify ourselves and flag the
   discrepancy rather than silently picking one of the brief's numbers.
2. The nine "GEMSDOE" sibling sites' own pages state their headline numbers
   (0.2449–0.2778) have "no submission-page receipt" / are "USER-REPORTED" —
   i.e., by the sites' own admission, these are not organizer-confirmed.
   See `research/sibling_site_audit.md`.
3. This repository (`GEMSDOEkarage1`) contained only a 1-line README before
   this session; it is not a continuation of the sibling sites' codebases,
   contrary to what a literal reading of the brief's "next steps from the
   previous session" language might suggest.
