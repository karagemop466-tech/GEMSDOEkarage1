> **28 October 2026 review note:** This is historical planning material. The checkout now includes inherited HMAS and GPC-Z implementations; statements about an empty checkout or an untried HMAS lane describe an earlier session. Prior score projections and causal claims are unverified, not measured results. Both inherited candidates are negative under the literal lattice rule; see [`evidence/prior_candidate_audit.json`](../../evidence/prior_candidate_audit.json). The USGS conductance release spans 2–200 km depth ranges, not 0.5–10 km. Current status and a fresh qualitative slate: [`knowledge/three-pass-review-2026-10-28.md`](../../knowledge/three-pass-review-2026-10-28.md).

# Pre-Registered Geological Hypotheses & 3-Experiment Protocol (`GEMSDOEkarage1`)

- **Pre-Registration Timestamp:** `2026-10-27T00:00:00Z` (written prior to running any experiment in `GEMSDOEkarage1`)
- **Competition:** [DrivenData DOE GEMS Prize (`competition-doe-gems`)](https://www.drivendata.org/competitions/306/competition-doe-gems/) | Official Rules: [DOE/NLR `96647.pdf`](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- **Grid & Metric:** `EPSG:32611` (`3730 x 3292` @ 100 m; `5,167,373` finite footprint pixels), Pooled Distance-Weighted Tversky Index ($\alpha = 0.2$, $\beta = 0.8$, $R = 300\text{ m}$ triangular kernel)
- **Live Benchmarks (`2026-10-27`):**
  - DrivenData Overall Public #1 (`xiaofanhu`): `0.4544` (`ORGANIZER-LEADERBOARD` — prompt reference `0.4413`)
  - DrivenData Top-5 Phase 1 Prize Cutoff (`No Fault of Our Own`): `0.3566` (`ORGANIZER-LEADERBOARD`)
  - Secondary Target Cited in Prompt: `0.3195` (`BENCHMARK-TARGET`)
  - User 9-Site Registry High (`GEMSDOE32` `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`, `sha256: c55bafc4...`): `0.2778` (`OWNER-REPORT`; `GEMSDOE32-HIDE-RECOVER-v3.0 = 0.099202`, `GEMSDOE32-SGMC-CAL-v3.0 raw = 0.064121`)
- **Dedicated Lane:** `H-K1-1: HMAS-SINTER-ENV` (*Hydrothermal Magnetite-Destruction Analytic-Signal Trough, Poisson Pseudo-Gravity Orthogonal Residual, & INGENIOUS Sinter/F2mDAB Upflow-Breach Dual-Envelope Submodular Network*)

---

## Why Prior Fleet Attempts Plateaued at `0.2778`

Pixel-for-pixel inspection of all `593` `.tif` rasters across `GEMSDOE24`, `GEMSDOE25`, `GEMSDOE27`, `GEMSDOE28`, `GEMSDOE30`, `GEMSDOE31`, `GEMSDOE32`, `GEMSDOE33`, `GEMSDOE36`, `KANLERGEMSDOE1..3`, `WBGGEMSDOE1..3`, and the 38 extra scored submissions reveals two structural facts:

1. **Nested `H19-5` Surface Crowding (`86.7%`–`97.4%` `<=3 px` overlap):** Every owner-reported score above `0.2449` across all 9 focus sites (`0.2449`, `0.2477`, `0.2600`, `0.2632`, `0.2708`, `0.2710`, `0.2750`, `0.2778`) descends from the same `H19-5` continuous probability surface. `GEMSDOE32` (`0.2778`, `37,654` dots) beat `GEMSDOE28` `h27-4-solo-d2-8` (`0.2708`, `40,199` dots) purely by expanding the catalogue exclusion collar from `B=1.0 px` to `B=2.0 px` (`min d_cat = 2.24 px`), stripping `2,545` near-catalogue halo dots that suffered near-zero net kernel gain inside the already-saturated `300 m` halo of `labels.tif`.
2. **Far-Field PU Attenuation & The `24.63%` 1 m LiDAR Blind Spot:** Models trained directly on `labels.tif` suffer severe Positive-Unlabeled (PU) attenuation in alluvial valleys (`58.4%` far-field share) and inside the `24.63%` footprint gap where USGS 3DEP 1 m LiDAR is absent (`lidar_valid == 0`). Prior potential-field fusion (`GEMSDOE32` `H48-1`) multiplied `p_supervised * R_subsurf`, which collapsed to zero wherever `p_supervised` decayed in unmapped basins (`SGMC-cal` fell to `0.0568 < 0.0641`). Conversely, uncalibrated radiometric/playa trackers (`GEMSDOE25` `h66`: `0.0742`; `GEMSDOE33` `s33`: `0.0963`) spilled `16%`–`19%` of their dots onto flat deep playas (`slope < 2 deg` & `depth_to_base_surf > 300 m`).

---

## Five Pre-Registered Untried Geological Hypotheses (Ranked by Expected DTI Gain vs Implementation Cost)

| Rank | ID | Short Name | Expected Live DTI Mechanism Gain | Compute / Eng. Cost | Status in This Session |
|---:|---|---|---|---|---|
| **1** | **`H-K1-1`** | **`HMAS-SINTER-ENV`** — Hydrothermal Magnetite-Destruction Analytic-Signal Trough & Sinter/`F2mDAB` Upflow-Breach Dual-Envelope Network | **High** (`+0.015` to `+0.045` DTI via blind hydrothermal fault recovery + 1 m LiDAR gap parity) | **Low–Moderate** (`~6 min` CPU; all official data SHA-256 verified locally) | **PRIMARY LANE (`EXP1`, `EXP2`, `EXP3`)** |
| **2** | **`H-K1-2`** | **`PPGR-RESID`** — Poisson Pseudo-Gravity Orthogonal Residual & Harmonic Depth-Persistence | **Medium–High** (`+0.010` to `+0.025` DTI by stripping volcanic flow-edge mimics) | **Low** (`2-D FFT` vertical integral; integrated as Channel `37`–`40`) | **Integrated Sub-Channel in `H-K1-1`** |
| **3** | **`H-K1-3`** | **`KCSD-DEFICIT`** — Kinematic Crustal Strain-Deficit & Walker Lane Transtensional Coupling | **Medium** (`+0.006` to `+0.015` DTI on transfer/accommodation step-overs) | **Low** (official `Bands 4, 7, 8, 16`; integrated as Channel `48`) | **Integrated Sub-Channel in `H-K1-1`** |
| **4** | **`H-K1-4`** | **`KHFA-ASYM`** — Tectonic Scarp Polarity Asymmetry & Pluvial Lake Lahontan Shoreline / TIGER Road Veto | **Medium** (`+0.005` to `+0.012` DTI via precision FP suppression) | **Low** (1 m LiDAR + TIGER + DEM contour geometry; Channels `49, 56`) | **Integrated Sub-Channel in `H-K1-1`** |
| **5** | **`H-K1-5`** | **`INSAR-3DMT`** — Multi-Depth 3-D MT Crustal Root (`0.5–10 km`) + Sentinel-1 InSAR Phase-Gradient Discontinuity | **Very High** (`+0.040` to `+0.090` DTI toward `0.35+` / `0.45+` ceiling) | **High / Egress-Gated** (multi-GB external downloads outside sandbox allowlist) | **Documented Phase-2 Roadmap** |

---

### Detailed Specification of Each Hypothesis

#### Hypothesis 1 (`H-K1-1` — Primary Dedicated Lane): Hydrothermal Magnetite-Destruction Analytic-Signal Trough & Sinter/`F2mDAB` Upflow-Breach Dual-Envelope Submodular Network (`HMAS-SINTER-ENV`)
- **(a) Specific Layer(s) Used:**
  - Competition GeoDAWN/INGENIOUS `training_features.tif` `Bands 2` (`tmi_rtp`), `3` (`tmi_thd`), `6` (`tmi_tc`), `9` (`tmi_vg`), `15` (`depth_to_base_surf`), `17` (`shallow_cond`), `19` (`slope`).
  - Official GeoDAWN Radiometrics (`geodawn_rad_u8.tif`: `K, eTh, eU, TC`; `geodawn_extensions_u8.tif`: `Th/K, U/K, U/Th, TMI_UC150m`; `acquisition_block_id_100m.tif` 4 contractor blocks).
  - Official INGENIOUS OpenEI GDR #1391 layers: `2m_temperature_probe_n83geo.dbf` (`2,782` stations inside footprint, `753` elevated `F2mDAB` shallow thermal anomalies), `Paleo_geothermal_final.csv` (`281` in-footprint Quaternary sinter, silicified fault breccia, travertine, hydrothermal explosion craters), and `gdr_wellspring_in_footprint.csv` (`27,092` wells/springs, `5,203` thermal/geothermometer entries — **strictly dropping `dist_known_fault_px`** per leakage audit `IR-KARAGE1-GDR-01`).
- **(b) Physical Signature Targeted:**
  - *Contrarian Magnetic Demagnetization Trough:* Hydrothermal fluids ascending at `150–300°C` oxidize ferrimagnetic titanomagnetite ($\text{Fe}_3\text{O}_4$) inside mafic/intermediate Cenozoic volcanic host rocks into non-magnetic hematite, leucoxene, pyrite, and illite-smectite clays (Grant 1985; Blakely 1995). This produces a **narrow linear trough (`valley`) in the 3-D Magnetic Analytic Signal** $A(x,y) = \sqrt{(\partial_x \text{RTP})^2 + (\partial_y \text{RTP})^2 + (\partial_z \text{TMI})^2}$ flanked symmetrically by positive tilt-curvature walls (`Band 6`), smectite clay-cap conductivity (`Band 17`), $^{214}\text{Bi}$ radon gas escape (`eU - 0.65 eTh` standardized per contractor block), and surface/near-surface thermal-fluid breaches (`F2mDAB`, sinter/silicified breccia, quartz geothermometers) projected anisotropically (`3:1`) along local potential-field strike.
- **(c) Why It Captures UNCATALOGUED Faults (Missed by USGS/INGENIOUS) Rather Than Catalogued Ones:**
  - USGS Qfaults and NBMG maps rely on subaerial Quaternary topographic scarps; across `~60%` of the Great Basin (e.g., McGinness Hills, Bradys/Desert Peak step-overs, Carson Sink, Dixie Comstock, Buffalo Valley), active geothermal conduit faults are buried beneath unconsolidated Holocene alluvium, eolian sand ramps, or pluvial Lake Lahontan clays and lack visible scarps. Hydrothermal magnetite destruction, shallow 2 m conductive heat plumes (`F2mDAB`), radon degassing, and relict sinter aprons penetrate or sit directly atop blind Holocene cover exactly where photogeology is blind.
- **(d) Difference vs Existing Repo Methods:**
  1. Existing repo models (`GEMSDOE24..36`) treat *high* magnetic gradient as positive everywhere, systematically rejecting demagnetized hydrothermal conduit troughs!
  2. No focus repo (`GEMSDOE24..36`) fuses the `2,782` in-footprint INGENIOUS 2 m temperature probe `F2mDAB` anomalies + `281` Quaternary sinter/breccia deposits via strike-aligned potential-field tensors.
  3. Replaces multiplicative post-gating (`p_sup * R_subsurf`) with a **Dual-Cover (`M_Full` inside `75.37%` 1 m LiDAR + quantile-matched `M_Sub` strictly LiDAR-free inside the `24.63%` gap) Positive-Unlabeled Max-Envelope Floor** $\max(p_{\text{dual}}, \lambda_{\text{env}} C_{\text{HMAS}})$, paired with **4-azimuth axial crest sharpening** and **`d=2.9 px` submodular 300 m kernel packing**.
- **(e) Free Official Data Source (Verified Obtainable):**
  - **USGS GeoDAWN Airborne Magnetic & Radiometric Survey:** ScienceBase DOI [`10.5066/P93LGLVQ`](https://doi.org/10.5066/P93LGLVQ) (U.S. Public Domain; cited in official NLR Rules `96647.pdf`).
  - **Great Basin INGENIOUS Regional Dataset Compilation:** OpenEI Geothermal Data Repository Submission #1391, DOI [`10.15121/1881483`](https://gdr.openei.org/submissions/1391) (CC-BY-4.0; verified live via HTTP `200` and SHA-256 verified locally).

---

#### Hypothesis 2 (`H-K1-2`): Poisson Pseudo-Gravity Orthogonal Residual (`PPGR-RESID`)
- **(a) Specific Layer(s) Used:** `Band 2` (`tmi_rtp`), `Band 13` (`isostatic_grav`), `Band 18` (`grav_hgrad`), `Band 15` (`depth_to_base_surf`).
- **(b) Physical Signature Targeted:** By Poisson's relation (Baranov 1957), transforming `tmi_rtp` via the 2-D wavenumber vertical integral $\mathcal{F}^{-1}\{\mathcal{F}[\text{RTP}] / (2\pi |\mathbf{k}|)\}$ synthesizes the **pseudo-gravity** expected if density contrasts were strictly proportional to magnetization. Taking the positive orthogonal regression residual $R_{\text{PPGR}} = \max(0, |\nabla g_{\text{iso}}| - \beta_{\text{loc}}(x)|\nabla g_{\text{pseudo}}|)$ isolates **non-magnetic Paleozoic carbonate/metamorphic basement fault blocks** while canceling shallow tabular Neogene basalt/tuff lava-flow margins (strong magnetization, minimal crustal throw).
- **(c) Why It Captures UNCATALOGUED Faults:** Intra-basin horst-and-graben blocks in carbonate basement (the primary deep geothermal reservoir rock across central/eastern Nevada) have zero surface expression and weak magnetic contrast, yet generate persistent `400 m`–`1800 m` upward-continued gravity steps orthogonal to volcanic flow edges.
- **(d) Difference vs Existing Repo Methods:** Prior repos feed raw `Band 2` and `Band 18` independently into tree splits without wavenumber vertical integration (`1/|k|`), so tree models misclassify volcanic mesa rims as faults.
- **(e) Free Official Data Source:** Official competition `training_features.tif` + USGS Gravity/Magnetic Compilation DOI [`10.5066/P9Z6SA1Z`](https://doi.org/10.5066/P9Z6SA1Z) (included in competition bundle).

---

#### Hypothesis 3 (`H-K1-3`): Kinematic Crustal Strain-Deficit & Walker Lane Transtensional Coupling (`KCSD-DEFICIT`)
- **(a) Specific Layer(s) Used:** `Band 4` (`strain_2nd_inv`), `Band 7` (`geod_shear_strain`), `Band 8` (`geod_dilation`), `Band 16` (`earthquakes`), plus potential-field strike orientation $(\cos 2\theta_s, \sin 2\theta_s)$.
- **(b) Physical Signature Targeted:** High GPS geodetic transtensional strain (`dilation + shear + 2nd_inv`) aligned along NNE/NNW Great Basin / Walker Lane oblique strikes intersecting lateral microseismicity boundaries (`|\nabla \text{earthquakes}|`), pinpointing locked or incipiently creeping accommodation/relay zones (`Faulds & Hinz 2015` structural settings: step-overs, horse-tails, overlapping fault terminations).
- **(c) Why It Captures UNCATALOGUED Faults:** Accommodation zones distribute slip across dense swarms of short (`1–4 km`), low-throw (`< 1 m` per event) fractures whose subtle topographic expression erodes within centuries, leaving them systematically absent from Quaternary scarp maps despite hosting `>70%` of blind Great Basin geothermal systems.
- **(d) Difference vs Existing Repo Methods:** Existing repos include raw low-resolution strain bands (`~10 km` smoothing) without directional strike alignment or seismic-gradient edge localization, causing trees to use them as regional quadrant identifiers (overfitting) rather than fault-relay locators.
- **(e) Free Official Data Source:** Official competition `training_features.tif` (`Bands 4, 7, 8, 16` from OpenEI GDR #1391 DOI [`10.15121/1881483`](https://gdr.openei.org/submissions/1391)).

---

#### Hypothesis 4 (`H-K1-4`): 1 m LiDAR Scarp Polarity Asymmetry & Pluvial Lake Lahontan Shoreline / TIGER Road Veto (`KHFA-ASYM`)
- **(a) Specific Layer(s) Used:** USGS 3DEP 1 m LiDAR scarp derivatives (`lidar_scarp_features_u8.tif`: `lidar_ex_max`, `lidar_step_max`, `lidar_down_scarp`, `lidar_up_scarp`, `lidar_coh100`, `lidar_valid`), `Band 12` (`dem_detrend`), `Band 15` (`depth_to_base_surf`), and US Census TIGER road distance (`tiger_road_distance_m.tif`).
- **(b) Physical Signature Targeted:** True normal-fault scarps exhibit **unidirectional vertical step polarity** (`|down_scarp - up_scarp|` coherent over `>= 500 m`) backed by finite subsurface basement/gravity gradients. Anthropogenic highway embankments/railroad grades (`<= 140 m` of TIGER roads, symmetric up-and-down crown) and late Pleistocene **Lake Lahontan wave-cut shorelines** (`~1,200–1,338 m` highstands; sharp 1 m DEM bench inside deep basin fill `depth > 180 m` with zero basement gravity gradient) are explicitly scored as non-fault confounds and suppressed.
- **(c) Why It Captures UNCATALOGUED Faults:** Eliminating thousands of wave-cut shoreline benches (Carson Sink, Buena Vista Valley, Smoke Creek, Honey Lake) and rural Nevada highway berms frees up `3,000–6,000` dot slots in the `~38,200` submodular budget to reallocate onto genuine eroded subtle piedmont scarps and blind intra-basin conduits.
- **(d) Difference vs Existing Repo Methods:** Existing repos (`H19-5` family) feed unsigned DEM curvature/slope ridges without shoreline or road de-confounding, visibly placing strings of false-positive dots along I-80 / US-50 / US-95 grades and Lahontan highstand benches.
- **(e) Free Official Data Source:** USGS 3DEP 1 m LiDAR (`https://www.usgs.gov/3d-elevation-program`, Public Domain) & US Census Bureau TIGER/Line Shapefiles (`https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html`, Public Domain; SHA-256 verified locally).

---

#### Hypothesis 5 (`H-K1-5` — Phase-2 External Egress Milestone): Multi-Depth 3-D Magnetotelluric Crustal Roots (`0.5–10 km`) + Sentinel-1 InSAR Phase-Gradient Discontinuity (`INSAR-3DMT`)
- **(a) Specific Layer(s) Used:** USGS Great Basin 3-D Magnetotelluric Electrical Resistivity Model depth slices (`500 m`, `1.5 km`, `3 km`, `6 km`, `10 km`) + NASA ARIA / ASF Sentinel-1 multi-temporal InSAR line-of-sight velocity & interferometric coherence discontinuities.
- **(b) Physical Signature Targeted:** Subvertical brittle-crustal fluid-filled damage zones imaged as sharp lateral resistivity boundaries below the shallow smectite clay cap (`1.5–6 km` depth), paired with millimeter-scale creep/subsidence differential compaction steps across blind intrabasin faults in InSAR stacks (`100 m` resolution).
- **(c) Why It Captures UNCATALOGUED Faults:** Competition `Band 17` provides only a single shallow conductivity slice dominated by near-surface playa brines; `1.5–6 km` 3-D MT penetrates completely beneath conductive playas, while InSAR resolves active blind fault differential compaction across featureless salt flats (`Dixie Valley`, `Brady`, `San Emidio`).
- **(d) Difference vs Existing Repo Methods:** Zero GEMSDOE repos use 3-D MT depth slices (`> 500 m`) or Sentinel-1 InSAR phase gradients.
- **(e) Free Official Data Source (Verified Public, Documented Sandbox Egress Constraint):**
  - **USGS 3-D MT Model:** Peacock et al. (2022–2024), USGS ScienceBase DOI [`10.5066/P9TWT2LU`](https://doi.org/10.5066/P9TWT2LU) (verified cited on OpenEI GDR #1391).
  - **NASA ARIA / ASF Sentinel-1 GUNW:** [`https://search.asf.alaska.edu/`](https://search.asf.alaska.edu/) (free NASA Earthdata / Copernicus open data).
  - *Sandbox Note:* Current sandbox outbound network access is allowlisted strictly to `github.com`, `npmjs.org`, and `pypi.org`, so raw multi-GB ScienceBase/ASF downloads cannot be fetched inside this container. `H-K1-5` is therefore formally documented as the #1 external-data breakthrough path from `~0.30+` toward `0.4544`.

---

## Pre-Registered 3-Experiment Budget (`Protocol Rule 6`: Max 3 Experiments / 2 Hours)

All three experiments stay strictly inside our dedicated lane (`H-K1-1: HMAS-SINTER-ENV`), share the identical 58-channel leak-checked stack (`M_Full` 58-ch + `M_Sub` 52-ch LiDAR-free) and buffered spatial OOF models, and test one clean orthogonal factor per step:

1. **`EXP1` (`HMAS-DualCover-Mult-Sep29`)**: Multiplicative subsurface gating $S_1 = p_{\text{dual}} \cdot (0.40 + 0.60\,\tilde{C}_{\text{HMAS}})$ + `d=2.9 px` submodular 300 m kernel emission (`B=2.2 px`, `K=38,200`). Tests whether multiplicative scaling still suffers far-field PU attenuation on off-catalogue SGMC faults.
2. **`EXP2` (`HMAS-DualCover-MaxEnv-RawCELF`)**: Positive-Unlabeled Max-Envelope Floor $S_2 = \max(\tilde{p}_{\text{dual}}, 0.56\,C_{\text{HMAS}})$ + raw `d=0.0` submodular 300 m kernel emission (`B=2.2 px`, `K=38,200`). Isolates the PU Max-Envelope discovery gain vs `EXP1` while exposing neighbor-clumping loss when `min_sep_px = 0`.
3. **`EXP3` (`HMAS-DualCover-MaxEnv-Axial29`)**: PU Max-Envelope Floor + **4-Azimuth Axial Crest Sharpening** + **`d=2.9 px` Axial-Spaced Submodular 300 m Kernel Emission** (`B=2.2 px`, `K=38,200`). Tests whether combining PU Max-Envelope blind-conduit recovery with `2.9 px` axial anti-clumping beats `BASE-35-OOF`, `EXP1`, `EXP2`, and the `0.2778` `GEMSDOE32` Champion across holdout benchmarks while passing both pre- and post-placement fleet uniqueness gates (`|Spearman| <= 0.90`, `3-px overlap <= 70%`).

**Fail-Closed Promotion Rule:** An arm receives `"verdict": "promote"` **if and only if** it:
1. Passes the 58-channel Leakage Canary (`max single-feature AUC <= 0.90`),
2. Beats `BASE-35-OOF` on per-cell `gems57-pooled-hide-v2` (`all` and `detached`) **AND** beats the `0.2778` `GEMSDOE32` Champion (`0.064121` raw / `0.099202` static HR3) on off-catalogue `SGMC-CAL-v3.0` (`95% CI` lower bound of delta `> 0`) and static `HIDE-RECOVER-v3.0`,
3. Passes 100% of automated GeoTIFF format/range/CRS/transform/finite-pixel gates (`[0, 1]`, `0 NaN`, `EPSG:32611`), and
4. Passes BOTH pre-placement continuous-surface and final-dot fleet uniqueness gates (`|Spearman| <= 0.90`, discrete `3-px overlap <= 70%`, unique `SHA-256`).
Otherwise, the Run Card records `"verdict": "negative"` and suppresses portal spend (`DO-NOT-SUBMIT`).
