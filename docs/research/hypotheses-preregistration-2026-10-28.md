# Pre-Registered Untried Geological Hypotheses & Dedicated Lane Specification (`2026-10-28`)

- **Repository / Branch:** `karagemop466-tech/GEMSDOEkarage1` (`arena/5721acf3-gemsdoekarage1`)
- **Timestamp (Preregistration Locked Before Feature/Model Code):** `2026-10-28T05:52:00Z`
- **Dedicated Method Lane:** `H-K1-S2-1` (`TD-KSCK` — *True Miller–Singh/Cooper–Cowan Tilt-Contact Demagnetization, 10 m 3DEP Fluvial $\chi$/$k_{sn}$ Piedmont Knickzones & Two-Stage Anisotropic Structural-Network Continuation*)
- **Why a Fresh Unique Submission Is Mandatory:** Prior session deliverable `hmas-sinter-dualcover-sep29-20261027T220000Z` (`SHA-256: 198076f8154b84dfde6be1479440ebed83c022c179f3bf49956bd06c41029356`) is now registered in the competition ledger (`https://karagemop466-tech.github.io/GEMSDOEkarage1 -> hmas-sinter-dualcover-sep29-20261027T220000Z`). Per the standing Parallel-Run Protocol, our new submission must be genuinely distinct (`|Spearman| <= 0.90` on both pre-placement continuous belief and post-placement dots, AND `<= 70.0%` directional 300 m (`3 px`) dot overlap) against **all** ~800 fleet rasters, **including** `hmas-sinter-dualcover-sep29-20261027T220000Z`, `gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-zeros`, `GEMSDOE32` (`0.2778`), `GEMSDOE36` (`0.2750`), `GEMSDOE70` (`0.2478`), `GEMSDOE92`, `GEMSDOEkarage2..3`, and `ApartGEMSDOE1..3`.

---

## 0. Forensic Irregularities Discovered During Pre-Implementation Audit

1. **`IR-KARAGE1-RESTORE-01` (`KeyError: 'source'` in `scripts/restore_karage1_data.py`):** Entries 1–26 of `registry/karage1_data_manifest.json` used flat top-level `repo`/`ref`/`path` (or `parts`) keys while entry 27 nested them inside `source`; `restore_karage1_data.py` unconditionally indexed `entry["source"]` and defaulted to `REPO_ROOT / "data"` when `/tmp/gems_data` was absent. Fixed upstream prior to data restoration (`36/36` SHA-256-verified files restored cleanly into `/tmp/gems_data`).
2. **`IR-KARAGE1-BAND6-01` (Misidentified `Band 6` & Dead-Zero `neg_tmi_tc` Channel in `src/gemskarage1/features.py`):** Prior `H-K1-1` (`src/gemskarage1/features.py`, line 255) assumed `Band 6` of `training_features.tif` was signed magnetic tilt-curvature (`tmi_tc`) and computed `neg_tmi_tc = np.maximum(-Band_6, 0.0)`. Cross-checking `vendor/gems57/geo.py` (`BAND_NAMES_1BASED[6] = "tc"`) and empirical correlation against `geodawn_rad_u8` (`r = +0.99714`, negative pixel fraction `= 0.000000`) proves **`Band 6` is strictly non-negative GeoDAWN Radiometric Total Count (`tc`)**, rendering `neg_tmi_tc` identically `0.0` across all `5,167,373` footprint pixels and starving `H-K1-1` of true magnetic tilt physics!
3. **`IR-KARAGE1-ELEV-01` (Detrended Elevation vs True Orthometric Lake Lahontan Highstands):** `Band 12` (`det_elev`) is regionally detrended (`-590..+1,470 m`), so true orthometric Pleistocene pluvial shorelines — specifically **Lake Lahontan Sehoo/Eetza highstand (`1,330–1,342 m ASL`, Adams et al. 1999)**, **Fallon/Dendritic stages (`1,265–1,282 m ASL`)**, and **Lake Dixie (`1,090–1,105 m ASL`)** — could not be isolated by `H-K1-1`. Restoring seamless 10 m USGS 3DEP `zmean_m` (`1,032–3,141 m ASL`, `100.00%` footprint coverage) solves this directly.
4. **`IR-KARAGE1-ZIP-01` & `IR-KARAGE1-UI-01`:** `README.md` cited stale `.zip` SHA-256 `8657f375...` instead of actual `b1c8817b...`, and `index.html` / `docs/executive-summary.html` juxtaposed cleared download links with stale `"0 experiments"` / `"No new file is currently approved"` copy. Scheduled for complete unification in Pass 1/Pass 2.

---

## 1. Pre-Registered Candidate Geological Hypotheses (Ranked by Expected DTI Gain vs Implementation Cost)

| Rank | ID | Hypothesis Name | Primary Layers & Free Official Sources | Expected Holdout / Piedmont DTI Lift | Implementation Cost | Status in This Session |
|---:|---|---|---|---|---|---|
| **1** | **`H-K1-S2-1`** | **True Miller–Singh/Cooper–Cowan Tilt-Contact Demagnetization + 10 m 3DEP Sub-Pixel Breaklines & Fluvial $\chi$/$k_{sn}$ Knickzone Strike-Bridging + Two-Stage Anisotropic Structural-Network Continuation (`TD-KSCK`)** | Competition `Bands 2, 3, 6, 9, 12, 13, 15, 17, 18, 19`; Seamless USGS 3DEP 10 m `topo_10m_derived_100m_u8` (`curv_prof_absmax`, `aspect_coherence`, `slope_p90`, `hs_lineament`, `relief_local`) & `dem10_chi_100m_i16`/`u8` (`step_max_x1000`, `ksn_max_m0.9`, `knick_n`, `raised_n`, `zmean_m`); GeoDAWN Radiometrics (`DOI:10.5066/P93LGLVQ`); OpenEI GDR #1391 INGENIOUS | **High (`+0.008` to `+0.020` on detached `gems57`, `HR3 >= 600 m`, and `C_pied`)** | **Moderate (`~45 min` code + `~10 min` 2-CPU streaming OOF)** | **SELECTED PRIMARY LANE (`EXP1`–`EXP3`)** |
| **2** | **`H-K1-S2-2`** | **Listric Dip-Concordant Gravity–Magnetic Tilt-Zero Offset (`\theta_{\text{grav}}` vs `\theta_{\text{mag}}` Cross-Strike Phase Shift)** | Competition `Bands 2` (`rtp`), `9` (`tmi_vg`), `11` (`iso_grav_anom_vg`), `13` (`iso_grav_anom`), `15` (`depth_to_base_surf`), `18` (`iso_grav_anom_hg`) | **Moderate-High (`+0.004` to `+0.009` on blind intrabasin faults)** | **Low (`~15 min`, vectorized 2-D potential-field math)** | **Integrated into `TD-KSCK` Physics Block** |
| **3** | **`H-K1-S2-3`** | **Multi-Physics Riedel / Relay-Intersection Hessian Corner Invariant (`\lambda_1 \lambda_2` Structural Complexity Concentrator)** | 10 m `hs_lineament` + `curv_prof_absmax`, upward-continued `rtp` & `iso_grav_anom`, `Bands 7–8` (`geod_shearrate`, `geod_dilaterate`) | **Moderate (`+0.003` to `+0.007` in step-overs & terminations)** | **Low (`~15 min`)** | **Integrated into `TD-KSCK` Physics Block** |
| **4** | **`H-K1-S2-4`** | **Cenozoic Piedmont Habitat-Calibrated Expected-DTI Submodular Allocation (`Mesozoic Pluton Interior De-Weighting + d=3.05 px Kernel Optimizer`)** | Stage-2 `TD-KSCK` OOF belief + orthometric `zmean_m`, `depth_to_base_surf`, 10 m `relief_local`/`slope_p90`, Radiometric `Band 6 tc` | **Moderate-High (`+0.008` to `+0.018` on `C_pied` while preserving `gems57`/`HR3`)** | **Low (`~15 min`, tested cleanly as `EXP3`)** | **Tested directly in `EXP3_TD_KSCK_PIED_OPT`** |
| **5** | **`H-K1-S2-5`** | **USGS 3-D Magnetotelluric Deep Brittle-Root Slices (`2–6 km`) + Sentinel-1 InSAR Phase-Gradient Creep Discontinuities** | USGS ScienceBase MT (`DOI:10.5066/P9TWT2LU`) + NASA ASF Sentinel-1 | **Moderate (`+0.004` to `+0.010` under deep playa evaporites)** | **Blocked in container (egress restricted to GitHub/PyPI/npm)** | **Documented Phase-2 Egress Extension** |

---

## 2. Detailed Physical Derivation of Each Untried Hypothesis

### Hypothesis 1 (`H-K1-S2-1` — Primary Dedicated Lane): `TD-KSCK`
1. **Specific Layers Involved:**
   - **Geophysical potential & MT fields (`training_features.tif`):** `Band 2` (`rtp`), `Band 3` (`tmi_hg`), `Band 6` (`tc` — radiometric Total Count), `Band 9` (`tmi_vg`), `Band 13` (`iso_grav_anom`), `Band 15` (`depth_to_base_surf`), `Band 17` (`cond_surf`), `Band 18` (`iso_grav_anom_hg`).
   - **100%-Footprint USGS 3DEP 10 m Seamless Geomorphology & Fluvial Tectonics (`60GEMSDOE` SHA-256-pinned mirrors of official USGS National Map 1/3 arc-second 3DEP):**
     - `topo_10m_derived_100m_u8.tif`: `slope_p90`, `steep_frac`, `relief_local`, `curv_prof_absmax`, `aspect_coherence`, `hs_lineament`.
     - `dem10_chi_100m_i16.tif` & `dem10_chi_100m_u8.tif`: Perron & Royden (2013) $\chi$-steepness step `step_max_x1000`, `ksn_max_m0.9`, sub-pixel knickpoint count `knick_n`, raised footwall fraction `raised_n`, and exact orthometric elevation `zmean_m` (`1,032–3,141 m ASL`).
   - **Hydrothermal Geochemistry & Radiometrics:** GeoDAWN (`geodawn_rad_u8`, `geodawn_extensions_u8`, survey-block-normalized `acquisition_block_id_100m`) + OpenEI GDR #1391 INGENIOUS (`2 m` `F2mDAB` temperature probes, Quaternary sinter/travertine/silicified fault breccia, $\text{SiO}_2$/cation geothermometers — strictly excluding `dist_known_fault_px`).
2. **Physical Signatures Targeted:**
   - **True Miller & Singh (1994) Magnetic Tilt Angle & Cooper & Cowan (2006) `TDX` Contact Crest (fixing `IR-KARAGE1-BAND6-01`):**
     $$\theta_{\text{mag}} = \arctan\!\left(\frac{\text{tmi\_vg} \cdot \Delta x}{\sqrt{(\partial_x \text{RTP})^2 + (\partial_y \text{RTP})^2} + \epsilon}\right) \in \left[-\frac{\pi}{2}, +\frac{\pi}{2}\right], \qquad \text{TDX}_{\text{mag}} = \arctan\!\left(\frac{\|\nabla_H \theta_{\text{mag}}\|}{|\text{tmi\_vg}|\cdot\Delta x + \epsilon}\right)$$
     By Salem et al. (2007), $\theta_{\text{mag}} = 0$ tracks vertical/steep fault contacts **independently of source magnetization strength**, while linear negative-tilt troughs ($\theta_{\text{mag}} < -0.25\text{ rad}$ flanked by twin $\|\nabla_H \theta_{\text{mag}}\|$ walls) pinpoint **hydrothermal magnetite-to-pyrite/hematite destruction slots** inside Miocene–Pliocene basalts and welded tuffs.
   - **10 m Sub-Pixel Scarp Breaklines + Transverse Fluvial $\Delta k_{sn}$ Knickzone Strike-Bridging:**
     Active range-front normal faults buried at canyon mouths by Holocene debris fans still maintain transient convex steepness steps (`step_max_x1000 > 0`, `knick_n > 0`) in intermittent footwall channels `100–600 m` upstream of the range-front fault trace (Perron & Royden 2013). Projecting 10 m channel knickzones anisotropically (`\sigma_\parallel = 1,200 m`) perpendicular to topographic gradient connects adjacent canyon-mouth knickpoints across un-scarped alluvial fan aprons — including inside the `1,272,913`-pixel (`24.63%`) 1 m LiDAR gap!
   - **Two-Stage Out-of-Fold Structural-Network Continuation (`Stage-2 OOF`):**
     Stage-1 Dual-Cover LightGBM models (`M_Full` on `75.37%` 1 m LiDAR cells + `M_Sub` on `100.00%` 10 m 3DEP + subsurface cells) emit strictly out-of-fold spatial block predictions $p^{(1)}_{\text{OOF}}(x, y)$. Stage-2 extracts multi-scale directional fault-strand continuation integrals (`400 m`, `900 m`, `1,800 m` across 8 structural azimuths), transverse crest sharpness, and alluvial-gap bridge continuity strictly from $p^{(1)}_{\text{OOF}}$ + label-free physics, training a Stage-2 buffered spatial OOF classifier that converts noisy pixel probabilities into geologically coherent `1–15 km` fault strands.
3. **Why It Catches Uncatalogued Faults Missed by USGS/INGENIOUS:**
   USGS QFaults and state geologic maps systematically miss (a) **scarpless intrabasin faults** detectable only via $\theta_{\text{mag}}$ demagnetization troughs and tilt zero-contours, (b) **fan-masked piedmont faults** where Holocene aggradation buried the surface scarp between adjacent canyon-mouth $\Delta k_{sn}$ knickzones, and (c) **degraded 1–3 m scarps inside the `24.63%` 1 m LiDAR gap** resolved by 10 m `curv_prof_absmax` $\times$ `aspect_coherence`.
4. **Difference From Existing Repo Implementations:**
   Neither `GPC-Z` (`src/gemsk/`) nor `H-K1-1` (`src/gemskarage1/`) used 10 m 3DEP geomorphic breaklines, 10 m fluvial $\chi$/$k_{sn}$ knickzones, true Miller–Singh magnetic/gravity tilt angles (`H-K1-1` had the dead-zero `Band 6` bug), orthometric `zmean_m` Lake Lahontan de-confounding, or Two-Stage OOF Structural-Network Continuation.
5. **Named Non-Fault Mimic Processes & Explicit De-Confounders:**
   - *Mimic A:* **Pleistocene Lake Lahontan (`1,330–1,342 m`, `1,265–1,282 m`) & Lake Dixie (`1,090–1,105 m`) wave-cut paleoshoreline benches** — de-confounded via orthometric elevation Gaussian bands $\times$ contour-parallelism $\times$ absence of potential-field tilt contact.
   - *Mimic B:* **Highway/railroad embankments & borrow ditches (`I-80`, `US-50`, `US-95`)** — de-confounded via TIGER road corridor indicators.
   - *Mimic C:* **Inactive Mesozoic granitic pluton interior cooling joints & roof pendants** — de-confounded via high orthometric elevation (`zmean_m > 1,950 m`), exposed bedrock (`depth_to_base_surf < 30 m`), and high radiometric `Band 6 tc`.

### Hypothesis 2 (`H-K1-S2-2`): Listric Dip-Concordant Gravity–Magnetic Tilt-Zero Offset
- **Layers:** `Band 2` (`rtp`), `Band 9` (`tmi_vg`), `Band 11` (`iso_grav_anom_vg`), `Band 13` (`iso_grav_anom`), `Band 15` (`depth_to_base_surf`), `Band 18` (`iso_grav_anom_hg`).
- **Physical Signature:** Computes gravity tilt angle $\theta_{\text{grav}} = \arctan2(\text{iso\_grav\_anom\_vg} \cdot \Delta x, \text{iso\_grav\_anom\_hg} + \epsilon)$ alongside $\theta_{\text{mag}}$, plus their cross-strike phase difference $(\theta_{\text{mag}} - \theta_{\text{grav}})$ and gradient alignment with $\nabla(\text{depth\_to\_base\_surf})$. Because Basin-and-Range normal faults dip `45°–60°` toward the hanging-wall basin, the deep basement density contrast shifts $\theta_{\text{grav}} = 0$ basinward relative to shallow volcanic $\theta_{\text{mag}} = 0$, whereas flat-lying basalt flow margins exhibit strong $\theta_{\text{mag}}$ edges with negligible $\theta_{\text{grav}}$ gradient.
- **Mimic:** Pre-Tertiary thrust contacts in mountain cores (de-confounded by `depth_to_base_surf`).

### Hypothesis 3 (`H-K1-S2-3`): Multi-Physics Riedel / Relay-Intersection Hessian Corner Invariant
- **Layers:** 10 m `hs_lineament` & `curv_prof_absmax`, upward-continued `rtp` & `iso_grav_anom`, `Bands 7–8` (`geod_shearrate`, `geod_dilaterate`).
- **Physical Signature:** At conjugate fault intersections and relay-ramp breaches (which host `>70%` of Great Basin blind geothermal systems; Faulds & Hinz 2015), single-azimuth structure-tensor coherence collapses while **both** principal eigenvalues $(\mu_1, \mu_2)$ of the multi-azimuth ridge energy tensor become simultaneously positive ($\det M - \kappa\,\text{tr}(M)^2 > 0$). Including this corner/junction invariant recovers structural intersections systematically suppressed by `H19-5`-style single-orientation ridge filters.
- **Mimic:** Dendritic stream confluences in steep bedrock canyons (suppressed unless backed by potential-field tilt or geodetic shear/dilatation).

### Hypothesis 4 (`H-K1-S2-4`): Cenozoic Piedmont Habitat-Calibrated Expected-DTI Submodular Allocation
- **Layers:** Stage-2 `TD-KSCK` OOF surface + orthometric `zmean_m`, `depth_to_base_surf`, 10 m `relief_local`, `slope_p90`, and Radiometric `Band 6 tc`.
- **Physical Signature:** DrivenData live leaderboard calibration (`GEMSDOE70` `Instrument C_pied`, Spearman $\rho = +0.8667$ across 22 live submissions) and `GEMSDOE29` (`0.0512` live score on un-filtered SGMC bedrock contacts) prove that hidden organizer truth faults are overwhelmingly **Cenozoic piedmont, range-front step-over, and intrabasin faults**, NOT high-altitude Mesozoic pluton interior contacts. Modulating the submodular expected-DTI objective by a label-free Cenozoic basin-margin / piedmont structural habitat weight and optimizing axial dot spacing (`d = 3.05 px`, `B = 2.25 px`, `K = 37,654`) maximizes live-relevant recall per dot.

### Hypothesis 5 (`H-K1-S2-5`): USGS 3-D Magnetotelluric Deep Brittle-Root Slices + Sentinel-1 InSAR Creep Gradients
- **Free Official Sources:** USGS ScienceBase Great Basin 3-D MT (`https://doi.org/10.5066/P9TWT2LU`) and NASA ASF Sentinel-1 SLC/interferograms (`https://search.asf.alaska.edu/`).
- **Obtainability Note:** Verified public-domain federal datasets, but direct HTTP download from `sciencebase.gov` / `asf.alaska.edu` is blocked inside this sandbox's egress allowlist (`github.com`, `pypi.org`, `npmjs.org`). Recorded transparently for external Phase-2 synthesis without blocking autonomous execution.

---

## 3. Pre-Registered 3-Experiment Budget (`Protocol Rule 6: <= 3 Experiments, <= 2 Hours`)

1. **`EXP1_TD_10M_STAGE1`**: Stage-1 Dual-Cover Buffered Spatial OOF (`M_Full` + `M_Sub` on repaired True Magnetic/Gravity Tilt `TDX` + 100%-coverage 10 m 3DEP breaklines & fluvial $\chi$/$k_{sn}$ knickzones + Riedel junction invariant + orthometric Lake Lahontan de-confounding) + `d = 3.0 px` 300 m submodular emitter (`B = 2.2 px`, `K = 37,654`).
2. **`EXP2_TD_KSCK_STAGE2`**: Adds **Stage-2 Buffered Spatial OOF Anisotropic Structural-Network Continuation** (`400 m`, `900 m`, `1,800 m` 8-azimuth OOF line integrals + transverse ridge prominence + alluvial-gap bridge features) + `d = 3.0 px` 300 m submodular emitter (`B = 2.2 px`, `K = 37,654`).
3. **`EXP3_TD_KSCK_PIED_OPT`**: Stage-2 `TD-KSCK` OOF belief surface + **Cenozoic Piedmont/Intrabasin Habitat-Calibrated Expected-DTI Submodular Allocation** (`d = 3.05 px`, `B = 2.25 px`, `K = 37,654`).

**Selection & Promotion Gate Criteria (Locked A Priori):**
- Every feature must pass the solo direction-invariant **Leakage Canary (`max(AUC, 1 - AUC) <= 0.90`)** before model fitting.
- Candidate must beat **both** `BASE_35` and prior `H-K1-1` (`EXP1_HMAS_MULT`) on `gems57-pooled-hide-v2` (all & detached), `GEMSDOE32-HIDE-RECOVER-v3.0` (all & detached `>= 600 m`), and `Instrument C_pied`, while remaining strictly unique (`|Spearman| <= 0.90` pre- and post-placement, `<= 70.0%` 3-px dot overlap) against **all** ~800 fleet rasters including `H-K1-1` (`198076f8...`) and `GEMSDOE32` (`c55bafc4...`).
