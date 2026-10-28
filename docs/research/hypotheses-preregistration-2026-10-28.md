# Pre-Registered Geological Hypotheses & Forensic Audit — Session 2026-10-28 (`CTWS-2D` Lane)

**Repository:** `karagemop466-tech/GEMSDOEkarage1`  
**Branch:** `arena/e3acfc48-gemsdoekarage1`  
**Timestamp (UTC):** `2026-10-28T05:50:00Z` (written **prior** to coding any feature or model changes)  
**Lane:** `CTWS-2D` (*Crustal Tilt-Worm Zero-Crossing, 3DEP 10 m Piedmont-Toe / $\chi$-Knickpoint & Fold-Safe Crack-Tip Relay 2-D Spatial-Context Submodular Network*)

---

## 1. Line-by-Line Forensic Irregularities Caught Prior to Modeling

Before designing new hypotheses, we verified every input GeoTIFF band header (`src.descriptions`, `dtype`, `nodata`, full-footprint quantiles across all `5,167,373` active pixels) directly from restored bytes against official USGS / DOE / NLR documentation and caught **five critical irregularities** in prior `GEMSDOEkarage1` (`PR #11` / `PR #12`) code and upstream metadata:

1. **`IR-KARAGE1-BAND6-01` (`training_features.tif` Band 6 `tc` strictly positive -> `65%` of `hmas_mag_destruct_trough` in `H-K1-1` was identically zero!):**
   - Although the `training_features.tif` GeoTIFF band description labels Band 6 as `"tc - Tilt angle or total curvature - magnetic field derivative"`, full-footprint measurement across all `5,167,373` finite pixels proves `min = +2.9534`, `p01 = +7.7223`, `median = +18.4817`, `max = +88.5665`, with **`0.000%` negative pixels** (matching GeoDAWN radiometric Total Count `22103_tc` dose rate, not a zero-centered tilt angle!).
   - Because `src/gemskarage1/features.py` line 470 computed `neg_tmi_tc = _robust_pos_norm(np.maximum(-kept[6], 0.0), foot)` and weighted it at `0.65` in `hmas_mag_destruct_trough`, **`neg_tmi_tc` evaluated to `0.0` on every pixel of the entire map**.
2. **`IR-KARAGE1-BAND18-01` (`training_features.tif` Band 18 `iso_grav_anom_hg` signed directional derivative truncated at `0.0`):**
   - Full-footprint inspection proves Band 18 (`iso_grav_anom_hg`) spans `[-15.4412, +12.8561]` with **`49.096%` (`2,536,973` pixels) negative**, whereas Band 5 (`iso_grav_anom_slope`) is the true non-negative gradient magnitude (`min = +0.0014`, `median = +0.1022`, `max = +0.6517`, `0%` negative).
   - `src/gemskarage1/features.py` line 487 wrote `iso_hg = np.maximum(kept[18], 0.0)`, zeroing out nearly half of opposite-dipping Basin-and-Range basement scarps in `ppgr_grav_ortho_excess`.
3. **`IR-KARAGE1-LIDAR12-01` (Unused 1 m LiDAR scarp polarity bands, unused BLM closed lode claims, and missing 10 m 3DEP full-footprint elevation/$\chi$-knickpoints):**
   - `lidar_scarp_features_u8.tif` carries 12 bands (`lidar_scarp_features.json`), but `H-K1-1` omitted `lappos_max` (piedmont-toe concavity `+LoG(6 m)`), `cross_max` (alluvial channel-bank non-fault mimic detector), and cyclic `sin(2*strike), cos(2*strike)` spinors, while `24.7%` of the footprint has `0` 1 m LiDAR coverage and lacked any 10 m 3DEP subgrid geomorphology, drainage $\chi$-knickpoints, or true elevation above sea level (`training_features.tif` Band 12 is detrended `det_elev`, not absolute elevation). Furthermore, `blm_closed_claim_distance_m.tif` sat in `registry/karage1_data_manifest.json` completely unused.
4. **`IR-KARAGE1-RESTORE-01` (`scripts/restore_karage1_data.py` mixed-schema `KeyError` & snapshot-cap hazard):**
   - `registry/karage1_data_manifest.json` stored flat `repo`/`ref`/`path` keys on entries `0..29` and a nested `source` object on entry `30`, crashing `restore_karage1_data.py`, while `paths.data_dir()` defaulted to `REPO_ROOT / "data"` when `/tmp/gems_data` was empty. Both are now fixed.
5. **`IR-SGMC-01` (`derived_sgmc_faults_100m_u8.tif` ~1 px dilation & 260 catalogue pixels):**
   - Confirmed against un-dilated USGS SGMC (`sgmc_faults_100m.tif`, Horton et al. 2017, `https://doi.org/10.3133/ds1052`): `derived_sgmc_faults_100m_u8.tif` has `1,446` extra dilated pixels and `260` `existing_faults.tif` pixels. Both SGMC files remain **100% excluded from model features** and used strictly as blind out-of-catalogue evaluation diagnostics (`(sgmc > 0) & ~catalogue & footprint`).

---

## 2. Five Pre-Registered Novel Geological Hypotheses (Ranked by Expected DTI Gain / Implementation Cost)

### Rank 1 — `H-K1-2A`: Multi-Depth Verduzco Potential-Field Tilt-Angle Zero-Crossing Worms & Cover-Adaptive Basement-Step Concordance (`PTZW`)
- **(a) Specific layers:**
  - `training_features.tif`: `B02 rtp`, `B03 tmi_hg`, `B05 iso_grav_anom_slope`, `B09 tmi_vg`, `B11 iso_grav_anom_vg`, `B13 iso_grav_anom`, `B15 depth_to_base_surf`, `B17 cond_surf`.
  - `external/geodawn_extensions_u8.tif`: `B04 TMI_up150`.
- **(b) Physical signature / transform:**
  - Under Verduzco et al. (2004) and Blakely (1995), the potential-field tilt angle
    $$\theta_{\text{mag}} = \arctan\!\left(\frac{\partial_z M}{\max(\|\nabla_H M\|, \epsilon)}\right), \qquad \theta_{\text{grav}} = \arctan\!\left(\frac{\text{B11 } (\partial_z g_{\text{iso}})}{\max(\text{B05 } (\|\nabla_H g_{\text{iso}}\|), \epsilon)}\right)$$
    crosses **zero** ($\theta = 0$) directly above a subvertical fault contact **independently of depth attenuation**, while $\|\nabla\theta\|^{-1}$ estimates contact burial depth $z_c$.
  - We compute analytical **Tilt-Zero Worm Ridges** $W_{\text{mag}} = \exp(-|\theta_{\text{mag}}| / 0.35)\,\tanh(\|\nabla_H \text{RTP}\| / s_M)$ across surface RTP (`0 m`), upward-continued RTP (`500 m`, `1.5 km`), and isostatic gravity $W_{\text{grav}} = \exp(-|\theta_{\text{grav}}| / 0.35)\,\tanh(\text{B05} / s_G)$, plus **Cover-Weighted Basement-Throw Concordance** $\|\nabla(\text{depth\_to\_base\_surf})\| \cdot W_{\text{grav}}$ and subsurface MT electrical conductivity gradient $\|\nabla(\text{cond\_surf})\|$ along hydrothermal clay-cap / brine boundaries.
- **(c) Why it catches faults missing from USGS/INGENIOUS:**
  - Over `39%` of Great Basin geothermal systems are blind with zero Quaternary surface scarp (Faulds & Hinz 2015) because `200–2,000 m` of unconsolidated basin fill (`B15 depth_to_base_surf`) buries intrabasinal horst and step-over faults (e.g., McGinness Hills, Salt Wells, Stillwater). Tilt-angle zero-crossings normalize out the $z_c^{-2}$ amplitude decay that blinds ordinary gradient thresholds under deep valley fill.
- **(d) Difference from prior repo ideas:**
  - Never tried in `GEMSDOEkarage1`: prior `H-K1-1` scrambled `B02/B05/B09/B11/B15/B17` and never computed Verduzco $\theta=0$ potential-field worms, `depth_to_base_surf` throw gradients, or `cond_surf` MT boundaries.
- **(e) Free official verified data sources & obtainability:**
  - USGS GeoDAWN (`https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and`, DOI `10.5066/P93LGLVQ`) and DrivenData / NLR official feature stack (`https://docs.nlr.gov/docs/fy26osti/96647.pdf`). **100% obtained and SHA-256 verified locally.**
- **(f) Named non-fault mimic & mitigation:**
  - Tertiary basaltic feeder dikes, circular caldera ring margins, and pluton contacts. Mitigated by spin-2 strike concordance between gravity and magnetic worms plus 2-D multi-scale linear aspect filtering (`H-K1-2C`).
- **Expected DTI Lift / Cost:** **Very High (`+0.015` to `+0.030` HOLDOUT-DTI)** / **Low implementation cost** (vectorized 2-D potential-field operators).

---

### Rank 2 — `H-K1-2B`: Full-Footprint USGS 3DEP 10 m Piedmont-Toe Concave Flexure, Perron-Royden Drainage $\chi$-Knickpoints & Antislope Graben Scarp De-Confounding (`PTCF-CHI`)
- **(a) Specific layers:**
  - **Newly added:** `external/topo_10m_derived_100m_u8.tif` (9 bands from USGS 3DEP 10 m DEM: `slope_p90`, `slope_max`, `steep_frac`, `slope_std`, `relief_local`, `curv_prof_absmax`, `aspect_coherence`, `hs_lineament`, `dem_mean`) and `external/dem10_chi_100m_i16.tif` (5 bands: `step_max_x1000`, `step_min_x1000`, `ksn_max_m0.9`, `log10_area_m2_x1000`, `zmean_m`).
  - **Newly unlocked:** all 12 properly de-quantized bands of `external/lidar_scarp_features_u8.tif` (`lappos_max` base concavity, `upface_max` antislope graben scarp, `cross_max` channel-bank filter, `coh100`, `sin 2\psi, \cos 2\psi`, `valid` coverage mask) + `training_features.tif` `B12 det_elev`, `B19 det_elev_slope`.
- **(b) Physical signature / transform:**
  - **Piedmont-Toe Concave Flexure (`PTCF`):** Active/Quaternary-degraded normal faults trace the **concave-upward structural hinge** at the range-front piedmont toe where upslope `500–1,400 m` relief is steep (`relief_up > 120 m`, `slope_up > 12°`) while local bajada slope is moderate (`1.5°–11°`) with high profile curvature × aspect coherence (`curv_prof_absmax * aspect_coherence`) — explicitly penalizing un-faulted `>22°` eroded footwall facet crags (`300–900 m` upslope of the true fault).
  - **Lateral-Propagated Perron-Royden $\chi$-Knickpoint Corridor (`CHI-CORR`):** Channel steepness jumps $\Delta \ln k_{sn}$ (`step_max_x1000`, $\theta=0.45$, Perron & Royden 2013) record transient tectonic uplift across drainage channels even where fan deposition buried interfluve scarps, interpolated across `300–800 m` interfluve corridors across **100% of the footprint** (solving the `24.7%` 1 m LiDAR coverage hole).
  - **Antislope Graben Ratio:** `(upface_max - 0.6 * cross_max) * coh100` where `valid > 0`, isolating uphill-facing antithetic graben scarps from stream-bank incisions.
- **(c) Why it catches faults missing from USGS/INGENIOUS:**
  - Low-slip-rate (`< 0.1 mm/yr`) Basin-and-Range faults lose visible surface scarps to hillslope diffusion within `20–50 kyr` and are missed in aerial Qfaults compilations, whereas channel $\chi$-knickpoints and piedmont-toe concave hinges persist for `0.2–1.0 Myr`.
- **(d) Difference from prior repo ideas:**
  - `topo_10m_derived_100m_u8.tif`, `dem10_chi_100m_i16.tif`, and bands `6..12` of `lidar_scarp_features_u8.tif` were **never previously loaded or used** in `GEMSDOEkarage1`.
- **(e) Free official verified data sources & obtainability:**
  - USGS 3D Elevation Program (`https://www.usgs.gov/3d-elevation-program`, `https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/`, US Public Domain `17 U.S.C. § 105`). **100% obtained and SHA-256 verified locally.**
- **(f) Named non-fault mimic & mitigation:**
  - Pleistocene Lake Lahontan highstand (`~1,334 m` ASL) wave-cut shorelines, alluvial fan channel banks (`cross_max`), and resistant welded-tuff cliff ledges. Explicitly gated via absolute 3DEP elevation `|dem_mean - 1334| < 18 m` shoreline indicator, `cross_max` subtraction, and steep-crag (`slope_p90 > 22°` without geophysical support) down-weighting.
- **Expected DTI Lift / Cost:** **High (`+0.012` to `+0.025` HOLDOUT-DTI)** / **Low implementation cost**.

---

### Rank 3 — `H-K1-2C`: Anisotropic 2-D Multi-Scale Lineament Context Pyramid & Fold-Safe Crack-Tip / Relay-Ramp Strain Transfer (`ACTR-2D`)
- **(a) Specific layers:**
  - Stage-1 out-of-fold physical fault belief surface $P_1^{\text{OOF}}(y, x)$ + potential-field / 10 m hillshade lineament fields (`EXP2` blind pyramid), augmented in `EXP3` with **strictly fold-visible** fault traces `visible_faults = catalogue & ~hidden_fold` (`existing_faults.tif` masked per spatial fold; full `existing_faults.tif` at final submission emission).
- **(b) Physical signature / transform:**
  - **Catalogue-Free 2-D Multi-Scale Anisotropic Lineament Pyramid (`CTX-2D`, `EXP2`):** Directional line integrals across 8 azimuths ($0^\circ..157.5^\circ$) at $L \in \{500\text{ m}, 1.3\text{ km}, 2.9\text{ km}\}$, extracting axial continuity $\max_\theta \mu_\theta^{(L)}(P_1)$, orthogonal ridge contrast $P_1 - \mu_{\theta^\perp}^{(L)}(P_1)$, spin-2 orientation coherence, and radial background context ($\sigma \in \{2, 6, 15, 30\}\text{ px}$).
  - **Fold-Safe Visible-Only Crack-Tip & Two-Host En-Echelon Relay Anatomy (`CT-RELAY`, `EXP3`):** Reusing `vendor/gems57/{anatomy,relay_bend_anatomy,network}.py` principles strictly on `visible_faults` inside each fold:
    1. Skeleton endpoint crack-tip forward propagation lobes $K_{\text{tip}}(\mathbf{x}) = \max_i \exp(-r_i / \lambda(L_i))\max(0, \cos\phi_i)^3$,
    2. Opposing co-linear tip-to-tip gap-bridge corridors ($< 3.6\text{ km}$ separation),
    3. Two-host relay-ramp superposition (`d1`, `d2`, `relay_ratio = d1/(d1+d2)`, `relay_facing = -\nabla d_1 \cdot \nabla d_2`, cross-strike `d_perp`, along-strike `d_par_abs`, displacement proxy `log_len`),
    fitted out-of-fold **with an explicit far-field (`> 1.5 km`) basin budget floor (`>= 50%` of emitted dots)** so near-fault accommodation strands and far-field blind basin faults are both recovered without tip over-concentration.
- **(c) Why it catches faults missing from USGS/INGENIOUS:**
  - Over `75%` of Great Basin geothermal upflow zones sit in structurally complex fault terminations, horse-tail splays, and overlapping en-echelon relay ramps (Curewitz & Karson 1997; Faulds & Hinz 2015) where strain is partitioned across sub-scarp fracture swarms, while `CTX-2D` connects segmented blind intrabasinal fault traces across multi-kilometer spans.
- **(d) Difference from prior repo ideas:**
  - `H-K1-1` (`PR #12`) was a 1-pixel point GBDT (`0 m` context, `0` structural continuation); `GPC-Z` (`PR #11`) applied an uncalibrated isotropic distance decay that collapsed far-field SGMC recall to `0.08067`.
- **(e) Free official verified data sources & obtainability:**
  - DrivenData `existing_faults.tif` (`https://docs.nlr.gov/docs/fy26osti/96647.pdf`) and pinned `vendor/gems57/` modules. **100% local and leak-verified (`solo AUC <= 0.90`).**
- **(f) Named non-fault mimic & mitigation:**
  - Map-quadrangle truncation artifacts at 1:24k sheet boundaries. Mitigated by requiring Stage-1 physical/geomorphic probability interaction (`P1_OOF * K_tip`) rather than extrapolating tips across geophysical quiet zones.
- **Expected DTI Lift / Cost:** **Very High (`+0.030` to `+0.085` HOLDOUT-DTI across `all` & `detached`)** / **Moderate implementation cost**.

---

### Rank 4 — `H-K1-2D`: Paleohydrothermal Epithermal Lode-Vein Conduit Corridor (`EPITH-BLM`)
- **(a) Specific layers:**
  - **Newly unlocked:** `external/blm_closed_claim_distance_m.tif` (BLM MLRS closed mineral/lode claim Euclidean distance in meters) + `external/geodawn_rad_u8.tif` (`K`, `Th`, `U`) + `external/geodawn_extensions_u8.tif` (`ThK`, `UK`, `UTh`) + RTP magnetic demagnetization trough (`rtp - G_{\sigma=8}(\text{rtp})`).
- **(b) Physical signature / transform:**
  - Epithermal vein corridor index $E_{\text{lode}} = \exp(-d_{\text{BLM}} / 1200\text{ m}) \cdot \sigma(z(\text{K}/\text{Th}) + z(-\Delta\text{RTP}_{\text{local}}))$, capturing linear quartz-adularia / illite-altered hydrothermal breccia ribs and magnetite-destroyed fault conduits.
- **(c) Why it catches faults missing from USGS/INGENIOUS:**
  - Miocene–Pleistocene silicified fault-valve veins (Midas, Dixie Comstock, Sleeper, Humboldt House, Wonder — Vikre 1985; Coolbaugh et al. 2005) lack Holocene alluvial scarps and are omitted from Quaternary scarp catalogues, yet mark brittle basement-cutting permeable fault zones.
- **(d) Difference from prior repo ideas:**
  - `blm_closed_claim_distance_m.tif` was never loaded in `GEMSDOEkarage1`.
- **(e) Free official verified data sources & obtainability:**
  - US Bureau of Land Management MLRS (`https://mlrs.blm.gov/`, US Public Domain) + USGS GeoDAWN (`https://doi.org/10.5066/P93LGLVQ`). **100% obtained and SHA-256 verified locally.**
- **(f) Named non-fault mimic & mitigation:**
  - Creek-bottom gold placers and flat playa lithium/borate claims; suppressed by gating out closed-basin playas and requiring linear potential-field or 10 m hillshade coherence.
- **Expected DTI Lift / Cost:** **Moderate (`+0.004` to `+0.010` HOLDOUT-DTI, high SGMC bedrock lift)** / **Very Low cost**.

---

### Rank 5 — `H-K1-2E`: Playa-Detrended $^{222}\text{Rn} \to {}^{214}\text{Bi}$ (`eU/eTh`) Degassing Halo × Shallow 2 m Thermal Upflow (`RADON-FLUX`)
- **(a) Specific layers:**
  - `external/geodawn_extensions_u8.tif` (`B03 UTh`, `B02 UK`), `external/geodawn_rad_u8.tif` (`U`, `Th`, `K`), `external/2m_temperature_probe_INGENIOUS_regional_data.zip`, `external/gdr_wellspring_in_footprint.csv` (`temp_c`, `geotherm_t`, strictly excluding `dist_known_fault_px`), and `external/paleo_geothermal_regional.zip`.
- **(b) Physical signature / transform:**
  - Lithology- and playa-detrended radon fracture index $R_{\text{Rn}} = z(\text{UTh}) - 0.65\,\mathbb{I}_{\text{playa}}(\text{slope}_{10\text{m}} < 0.8^\circ \wedge \text{det\_elev} < -80\text{ m})$ fused with multi-scale (`1.5 km` / `4 km`) INGENIOUS 2 m temperature residual and chalcedonic geothermometer plumes.
- **(c) Why it catches faults missing from USGS/INGENIOUS:**
  - Active gas-advecting blind faults under zero-relief desert floors emit $^{222}\text{Rn}$ (`eU` $^{214}\text{Bi}$ excess over immobile `eTh`) and shallow conductive heat anomalies with zero topographic scarp.
- **(d) Difference from prior repo ideas:**
  - Prior `H-K1-1` used raw `U/Th` without contractor `UTh` mosaic or closed-basin uranyl-evaporite detrending.
- **(e) Free official verified data sources & obtainability:**
  - USGS GeoDAWN (`https://doi.org/10.5066/P93LGLVQ`) + DOE GDR #1391 INGENIOUS (`https://gdr.openei.org/submissions/1391`, CC BY 4.0). **100% obtained and SHA-256 verified locally.**
- **(f) Named non-fault mimic & mitigation:**
  - Uranyl-carbonate evaporite sinks in Carson Sink / Humboldt Sink playas and unwelded rhyolite tuffs; suppressed via explicit playa sink subtraction.
- **Expected DTI Lift / Cost:** **Moderate (`+0.003` to `+0.008` HOLDOUT-DTI)** / **Very Low cost**.

---

## 3. Pre-Declared 3-Experiment Budget & Automated Acceptance Protocol

Per **Parallel-Run Protocol Rule 6** (`<= 3` experiments, `<= 7200 s` wall-clock), we pre-register the exact 3-step controlled factorial ablation on the shared `gems57-pooled-hide-v2` (`all` and `detached >= 400 m`) and `GEMSDOE32-HIDE-RECOVER-v3.0` (`all` and `detached >= 600 m`) buffered spatial holdouts plus blind `SGMC-CAL-v3.0`:

1. **`EXP1_PTZW_PTCF_1D`:** Corrected 19-band `training_features` + **H1 (`PTZW`)** + **H2 (`PTCF-CHI`)** + **H4 (`EPITH-BLM`)** + **H5 (`RADON-FLUX`)** Stage-1 buffered out-of-fold LightGBM + 300 m CELF submodular DTI allocation (`0` catalogue features).
2. **`EXP2_CTX2D_BLIND`:** Stage-2 **Catalogue-Free 2-D Multi-Scale Anisotropic Lineament Context Pyramid (`CTX-2D`)** trained out-of-fold over `EXP1` physical belief + multi-scale potential-field/3DEP orientation coherence (`0` catalogue features — `100%` blind physical/geomorphic discovery).
3. **`EXP3_CTWS_RELAY_DUAL`:** Full **`CTWS-2D`** dual-regime Stage-2 ensemble combining `EXP2` blind 2-D lineament probability with **strictly fold-visible (`visible = catalogue & ~hidden_fold`) Crack-Tip Propagation Cones, Opposing-Tip Gap Bridges, and Two-Host En-Echelon Relay-Ramp / Damage-Zone Anatomy (`H-K1-2C`)**, governed by a **Far-Field Basin Allocation Floor (`>= 50%` dots at `> 1.5 km` from visible faults)** + 300 m CELF submodular DTI emitter.

**Mandatory Gates (All Must Pass Automatically):**
- **Leakage Canary:** Every feature (static physical, 2-D context, and fold-visible structural) tested solo on holdout; `max |AUC| <= 0.90` (`0.5`-centered ROC AUC `<= 0.90`).
- **Holdout Superiority:** Winning experiment must beat BOTH `BASE_35` (`0.0878` all / `0.0830` detached) AND prior session `H-K1-1` (`0.09055` all / `0.09355` detached) on `gems57-pooled-hide-v2` AND `GEMSDOE32-HIDE-RECOVER-v3.0` (`all` & `detached >= 600 m`), while simultaneously beating `GEMSDOE32` (`0.09369`) on blind off-catalogue `SGMC` bedrock fault recovery.
- **Full-Fleet Uniqueness:** Pre-placement continuous surface `max |Spearman rho| <= 0.90` AND final emitted dots `max <=3 px directed overlap <= 0.70` against **all 600+ registry & Oct 25–28 sibling rasters** (explicitly including `karage1-hmas-sinter-dualcover-sep29`, `gpcz`, and `GEMSDOE32`).
- **Format Validator:** Single-band `float32` GeoTIFF, `EPSG:32611`, `3730 x 3292`, exact geotransform `(100, 0, 243350, 0, -100, 4508550)`, all values finite and strictly inside `[0.0, 1.0]`.
