# Sources and data — auditable tables

Every row states how it was verified. **VERIFIED-THIS-SESSION** = fetched and read in this sandbox (github.com hosts only). **VERIFIED-BY-SIBLING** = read and quoted in sibling repositories (GEMSDOE24/32) whose text was fetched here; re-check the link manually. **OWNER-REPORT** = a number typed by the owner in the standing brief.

## Official competition sources

| Item | Link | What it establishes | Verification |
|---|---|---|---|
| Competition page | https://www.drivendata.org/competitions/306/competition-doe-gems/ | challenge, data tab (login-walled), submission page | VERIFIED-BY-SIBLING (drivendata.org is not reachable from this sandbox) |
| Problem description | https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/ | distance-weighted Tversky, α=0.2 β=0.8, 300 m triangular kernel, 100 m pixels, one float32 band, same CRS/res/bounds; "Predicted values must be in range [0, 1]" | VERIFIED-BY-SIBLING |
| Submission page | https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/ | .tif or .zip containing one GeoTIFF; note field; 3 per week | VERIFIED-BY-SIBLING + owner's own submission experience |
| Official rules PDF (NLR/DOE) | https://docs.nlr.gov/docs/fy26osti/96647.pdf | training labels from INGENIOUS GDR 1391; hidden labels include newly identified faults mapped by NLR/USGS experts + USGS Qfaults; features = GeoDAWN + USGS 1 m DEM; Phase 1 $50k top-5 on withheld subset, Phase 2 $250k on expert-updated labels; code reproducibility; generative-AI disclosure; U.S. eligibility | VERIFIED-BY-SIBLING (docs.nlr.gov not reachable here) |
| Known-fault masking thread | https://community.drivendata.org/t/known-faults-masking-in-the-metric/11516 | training faults are *not* masked out of scoring; hidden faults are additional | VERIFIED-BY-SIBLING |
| Organizer reference solution | https://github.com/drivendataorg/gems-prize-reference-solution | notebook-only U-Net baseline; no scorer | VERIFIED-THIS-SESSION (cloned) |
| Leaderboard | https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ | top entries 0.4437 / 0.3916 / 0.3904 on 2026-10-26 (sibling snapshot); owner quoted 0.3195 and 0.4413 in briefs | OWNER-REPORT / VERIFIED-BY-SIBLING — recheck |

## Official data sources (free, public)

| Dataset | Official link | Role | Obtainable from this sandbox? |
|---|---|---|---|
| INGENIOUS GDR submission 1391 (Quaternary faults, wells, geothermal systems; DOI 10.15121/1881483) | https://gdr.openei.org/submissions/1391 | training-label universe (catalogue) | NO (egress limited to github/pypi); bytes restored from owner's github mirror and SHA-256-pinned |
| USGS GeoDAWN (DOI 10.5066/P93LGLVQ) — airborne magnetics + radiometrics | https://doi.org/10.5066/P93LGLVQ · https://www.usgs.gov/centers/gggsc/science/geodawn | source of 19 feature bands + external radiometric u8 mirror | NO (usgs.gov not reachable); 19 bands restored from mirror |
| USGS 3DEP 1 m LiDAR DEM | https://www.usgs.gov/3d-elevation-program · https://apps.nationalmap.gov/downloader/ | `lidar_scarp_features_u8.tif` (12 bands) was derived by GEMSDOE24 from 1 m tiles | NO (derived mirror restored and pinned) |
| USGS Quaternary Fault and Fold Database | https://www.usgs.gov/programs/earthquake-hazards/faults | part of the hidden label universe | NO |
| USGS SGMC geologic map faults | https://doi.org/10.5066/P9WYCK2Z | off-catalogue bedrock faults (siblings: ≈0.03–0.05 live) | NO |
| USGS ComCat earthquake catalog | https://earthquake.usgs.gov/fdsnws/event/1/ | hypothesis H4 (seismicity lineaments) | NO — named access need |
| 2020 M6.5 Monte Cristo Range event | https://earthquake.usgs.gov/earthquakes/eventpage/nn00725272/ | hypothesis H5 (surface rupture) | NO — named access need |
| Dropbox competition mirror (owner-supplied) | (links held by the owner) | alternative to login-walled data tab | NO (dropbox.com not reachable) |

## Sibling repositories (learning only — never copied as submissions)

| Repo | Used for | Verification |
|---|---|---|
| https://github.com/buffedlizard55-lab/GEMSDOE32 | 0.2778 recipe, covariate audit (n=53), lattice impasse IR-49-LATTICE-01, data manifest pins | VERIFIED-THIS-SESSION (cloned) |
| https://github.com/buffedlizard55-lab/GEMSDOE24 | `data/bridge/` label and sample-submission bytes; `data/external/` LiDAR/GeoDAWN u8 mirrors | VERIFIED-THIS-SESSION (fetched via api.github.com) |
| https://github.com/buffedlizard55-lab/GEMSDOE | `training_features.tif` 5-part bridge | VERIFIED-THIS-SESSION |
| https://github.com/buffedlizard55-lab/19GEMSDOE | `src/gems/hypotheses.py` — proves H19-5 is catalogue-trained | VERIFIED-THIS-SESSION |

## Pinned restore manifest

| id | file | sha256 (first 16) | bytes |
|---|---|---|---|
| `training_features` | `training_features.tif` | `4371c82e3b8339b8…` | 418,912,844 |
| `labels` | `labels.tif` | `7ba308ccdc4418b3…` | 425,830 |
| `existing_faults` | `existing_faults.tif` | `7ba308ccdc4418b3…` | 425,830 |
| `sample_submission` | `sample_submission.tif` | `2176d08e485aa2cd…` | 1,599,597 |
| `ext_lidar_scarp_features_u8` | `external/lidar_scarp_features_u8.tif` | `d580bb8bdcdb941e…` | 36,943,606 |
| `ext_geodawn_rad_u8` | `external/geodawn_rad_u8.tif` | `c22420f75999030d…` | 26,612,970 |
| `reg_champion_02778_zeros` | `registry/GEMSDOE32_h33-h33-2-b2_e5eb6e7e_zeros.tif` | `c55bafc470054e82…` | 219,065 |
| `reg_gems36_anderson_zeros` | `registry/GEMSDOE36_anderson-geothermal-pinn-38854_zeros.tif` | `e15891020b9c5705…` | 318,190 |
| `reg_gems28_h36_rung30` | `registry/GEMSDOE28_h36-1-rung30-blind-r1_allfinite.tif` | `7c74270ad48fa0b8…` | 825,430 |
| `reg_gems28_h27_4_solo` | `registry/GEMSDOE28_h27-4-r1-solo-d2-8_allfinite.tif` | `2fc94a38d77f74d4…` | 830,036 |
| `reg_gems28_h38_hf_euler` | `registry/GEMSDOE28_h38-1-hf-euler-r30-r1_allfinite.tif` | `529d9e1bd80b5495…` | 825,790 |
| `reg_gems28_h32_1_prethin` | `registry/GEMSDOE28_h32-1-prethin-tip-euler-d2-8_allfinite.tif` | `26748e4b4721277b…` | 833,784 |
| `reg_gems31_h27_4_solo_d28` | `registry/GEMSDOE31_h27-4-solo-d28_allfinite.tif` | `acd853936e5a7170…` | 154,580 |
| `reg_gems33_h33d_tip_stepover` | `registry/GEMSDOE33_h33d-analog-tip-stepover-r30.tif` | `87f857d505e23247…` | 917,544 |
| `reg_gems25_d28_zeros` | `registry/GEMSDOE25_dotted-h19-5-d2-8_zeros.tif` | `3e78737f0da8dd2c…` | 836,982 |
| `reg_gems30_d28_poisson` | `registry/GEMSDOE30_d28-poisson300m-offcat-44090.tif` | `8cf893ead5667df2…` | 806,758 |
| `reg_gems24_d15_allfinite` | `registry/GEMSDOE24_h25-1-dotted-h19-5-d1-5_allfinite.tif` | `3e0730e8d4f7db09…` | 863,902 |
| `reg_gems27_tgc_v2_allfinite` | `registry/GEMSDOE27_topo-gap-closure-t-v2-on-d1-5_allfinite.tif` | `a9bf76b57453a5b3…` | 866,160 |
| `reg_gems27_h31_drcg_allfinite` | `registry/GEMSDOE27_h31-drcg-wl-celf28_allfinite.tif` | `2c002b0279241986…` | 825,820 |
| `reg_h19_5_source_field` | `registry/GEMS19_h19-5-powerlaw-budget-multiline-corroborated_nan.tif` | `ec1f9b56b83ce33c…` | 1,712,322 |
| `reg_lattice_s5_calibration` | `registry/13GEMSDOE_r13-lattice-s5_v2_nan-outside.tif` | `b4570b406efec198…` | 1,706,456 |

Restore receipt (what was actually downloaded and verified this session): `data/restore_receipt.json` (gitignored; summary mirrored at `docs/data/restore_receipt_summary.json`).
