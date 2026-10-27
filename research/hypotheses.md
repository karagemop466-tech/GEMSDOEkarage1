# Five candidate geological hypotheses (untried in this repo and, as far as
we could verify, not already implemented by the nine sibling "GEMSDOE"
sites)

**Status of every number below: PROJECTION, not HOLDOUT-DTI, not an
organizer score.** None of these have been run against real data in this
environment (see `docs/LIMITATIONS.md`). Per the parallel-run protocol, no
hypothesis here may be spent as a weekly submission slot until it beats the
current holdout best on `evaluate_holdout.py`/`submission_writer.py` using
**real** competition data placed in `./data/` (see
`scripts/download_competition_data.sh`).

Each entry names: the specific layer(s), the physical transform, why it
should recover a fault that is *missing* from the USGS/INGENIOUS catalogue
rather than one already in it, the named non-fault mimic the detector must
reject, how it differs from this repo's (currently empty) prior art and from
the documented sibling-site attempts (`research/sibling_site_audit.md`), the
exact free external dataset required, and confirmation that the dataset is
obtainable (checked live, see `docs/SOURCES.md` items 10–19).

---

## Rank 1 — H-A: Coulomb slip/dilation-tendency filter on potential-field lineaments

- **Layers.** Official `training_features.tif` bands: isostatic gravity
  anomaly + its slope; reduced-to-pole (RTP) magnetic anomaly + its vertical
  and horizontal slope. External: USGS *Shapefile for slip tendency and
  dilation tendency calculated for Quaternary faults in the Great Basin*
  (Siler, 2022; `docs/SOURCES.md` #10).
- **Physical signature.** Extract curvature-ridge lineaments from gravity +
  magnetics (standard potential-field edge detection). For each lineament
  pixel, estimate its local strike from the ridge tangent. Using the *already
  mapped, nearby* faults' slip/dilation-tendency values (which encode the
  regional principal-stress orientation Siler et al. computed for the Great
  Basin), compute the Coulomb dilation tendency `Td` a fault of that same
  strike *would have* at that location under the locally calibrated stress
  tensor. Keep only lineament pixels in the top quantile of `Td`.
- **Why it should catch missing, not catalogued, faults.** A structural
  lineament in gravity/magnetics is ambiguous — it could be a lithologic
  contact, an intrusive margin, or a genuine blind/buried fault. Nearly
  every sibling-site hypothesis we reviewed used raw curvature magnitude or
  orientation *concordance between two potential fields* as the filter.
  None used a *mechanical* argument: only lineaments whose strike is
  favorably oriented for slip/dilation under the real regional stress field
  are kept. Lithologic contacts have no reason to respect regional stress
  orientation; genuine faults statistically do (Anderson's theory of
  faulting). This is a fundamentally different evidence class (stress-based
  mechanics) from every curvature/concordance detector already tried.
- **Named non-fault mimic.** Stratigraphic/lithologic contacts and intrusive
  margins with strikes uncorrelated to the regional sigma_1 — explicitly
  suppressed by the `Td` quantile filter, which is strike-selective, not
  magnitude-selective.
- **Differs from sibling sites.** Sibling sites used *geodetic* (present-day,
  kinematic) dilation rate from the INGENIOUS "Geodetic Shear and Dilation
  Models" product (a GPS-derived strain-rate field) directly as a feature
  weight (e.g. GEMSDOE26 "dilcond-oof"). H-A instead uses the *Quaternary
  fault slip/dilation-TENDENCY database* — a distinct, Coulomb/Mohr
  mechanics-based data product computed from fault geometry + an
  independently estimated ambient stress tensor, not a strain-rate
  observation — as a per-orientation favorability filter applied to
  *unmapped* lineaments, not as a weight on already-mapped faults.
- **External data needed and obtainable?** Yes — `docs/SOURCES.md` #10,
  USGS ScienceBase item `6296974dd34ec53d276bb33d`, public domain, no login,
  confirmed live 2026-10-27 (shapefile + KMZ, ~34 MB).
- **Expected DTI improvement:** Medium-high. **Implementation cost:**
  Medium (stress-tensor interpolation + per-pixel strike estimation).

---

## Rank 2 — H-C: RANSAC vent-chain alignment cross-checked against magnetic feeder-dike anomalies

- **Layers.** External: INGENIOUS *Quaternary Volcanics* shapefile (vent
  points + flow polygons; `docs/SOURCES.md` #15). Official: RTP magnetic
  anomaly band of `training_features.tif`.
- **Physical signature.** Many Great Basin monogenetic volcanic vents erupt
  along dikes that exploit pre-existing extensional faults. For every
  cluster of 3-5 spatially proximate vents, fit a robust line (RANSAC, to
  reject off-trend vents) and keep the alignment only if a co-located
  magnetic Analytic Signal ridge (a standard dike-detection transform)
  confirms a linear feeder source beneath it.
- **Why it should catch missing, not catalogued, faults.** A fault that
  fed a now-extinct monogenetic vent chain can be entirely buried by its own
  eruptive products or by subsequent basin fill, leaving no surface scarp —
  exactly the class of fault the competition's problem description says is
  "not contained within the current public USGS database." The vent
  alignment plus magnetic coincidence is independent evidence that doesn't
  require any surface expression at all.
- **Named non-fault mimic.** En-echelon eruption centers along a diffuse
  volcanic field margin without a continuous feeder, or vents that happen to
  fall in a line by chance in a dense vent field — rejected by requiring the
  co-located magnetic linear anomaly, which a coincidental alignment would
  not have.
- **Differs from sibling sites.** One sibling hypothesis (`GEMSDOE25`, lane
  H75-3 "VVAC") explicitly *planned* to use
  `gdr_volcanic_vents_in_footprint.csv` with "Analytic Signal & mid-crustal
  MT phase tensor" but recorded it as **deferred / never implemented**
  (see `research/sibling_site_audit.md`). H-C completes that gap with a
  concrete, specific algorithm (RANSAC multi-vent alignment + magnetic
  cross-check), which is a genuine, specified implementation rather than an
  unexecuted placeholder.
- **External data needed and obtainable?** Yes — `docs/SOURCES.md` #15,
  GDR OpenEI submission 1391, CC BY 4.0, no login, confirmed live
  2026-10-27 (9.44 MB).
- **Expected DTI improvement:** Medium-high (high precision, likely low
  recall — few vent chains exist, but each is a strong, specific signal).
  **Implementation cost:** Low-medium.

---

## Rank 3 — H-E: Thermal-conductivity-corrected residual heat flow as a direct advective-pathway detector

- **Layers.** External: USGS *Heat flow maps and supporting data for the
  Great Basin* (`docs/SOURCES.md` #11), which explicitly ships a
  **well-level residual attribute** ("the well's departure from estimated
  background heat flow conditions... may be useful in identifying
  hydrothermal or groundwater influence"). Official: detrended elevation
  band (to reject topographic-refraction artifacts, which the organizers
  already compute for exactly this purpose).
- **Physical signature.** Positive heat-flow residuals (observed minus
  modeled background conductive heat flow) that are *spatially linear and
  compact*, not isolated points, mark advective fluid pathways — i.e.
  faults acting as conduits. The heat-flow data release's own background
  model already removes "hydrothermal convective influence," so its
  *residual* is, by the originating USGS team's own stated purpose, a
  pre-built fault/conduit indicator.
- **Why it should catch missing, not catalogued, faults.** This is the only
  hypothesis in this list that is a **direct thermal measurement** rather
  than a structural-geometric proxy. A fault can be thermally active
  (hosting present-day upflow) while having no clear surface scarp (e.g. if
  covered by young alluvium) — this is precisely the scenario the
  competition's prize structure rewards most (faults confirmed by the
  Final Prize Round's expert panel from candidate predictions).
- **Named non-fault mimic.** Topographic refraction of heat flow in
  high-relief terrain, and shallow groundwater advection in unconfined
  alluvial aquifers unrelated to any fault — guarded against by requiring
  (a) correction against the official detrended-elevation band and (b)
  linear/compact spatial geometry of the residual, not a diffuse plume.
- **Differs from sibling sites.** Every reviewed sibling hypothesis used
  gravity, magnetics, radiometrics, DEM/LiDAR, seismicity, or MT as the
  *primary* signal and treated "geothermal/thermal" language only as a
  narrative framing (e.g. "anderson-geothermal-pinn", "geotherm-tilt-axial").
  None used the INGENIOUS/USGS *heat flow residual data product itself* as
  the primary detection signal.
- **External data needed and obtainable?** Yes — `docs/SOURCES.md` #11,
  USGS ScienceBase item `6297d2fad34ec53d276c5b28`, public domain, no
  login, confirmed live 2026-10-27 (124 MB zip including a point coverage
  with the residual attribute).
- **Expected DTI improvement:** Medium (coarse native resolution of
  kriged heat-flow surfaces vs. the competition's 100 m grid is a real risk;
  needs careful regridding/uncertainty propagation). **Implementation
  cost:** Medium.

---

## Rank 4 — H-B: Paleo-upflow corridor projection from sinter/tufa and well/spring thermal anomalies

- **Layers.** External: INGENIOUS *Paleo Geothermal Features* (sinter/tufa
  point deposits, `docs/SOURCES.md` #16) and *Well and Spring Temperature
  and Chemistry* geodatabase (`docs/SOURCES.md` #17). Official: detrended
  elevation (for local hydraulic gradient).
- **Physical signature.** Sinter/tufa deposits and present-day thermal
  springs/wells mark a *known* past or present fault-controlled upflow
  point. Project a narrow corridor along the local up-gradient azimuth
  (computed from the DEM-derived hydraulic gradient) from each anomaly; a
  blind conduit segment is hypothesized to exist, and is confirmed, only
  where a potential-field curvature ridge coincides with that narrow,
  hydrologically-motivated corridor (not searched over the whole image).
- **Why it should catch missing, not catalogued, faults.** The upflow point
  itself is already known (it is a mapped spring, well, or deposit) but the
  *fault* that channels it is frequently not — especially where the
  conduit is capped by younger sediment away from the spring itself.
- **Named non-fault mimic.** Thermal springs fed by deep regional
  carbonate-aquifer flow (karst discharge) rather than a discrete fault —
  guarded by requiring potential-field curvature coincidence within the
  corridor, which a purely stratigraphic aquifer discharge would not have.
- **Differs from sibling sites.** `GEMSDOE25`'s H75-1 lane used a
  *K-on-Th radiometric* "sinter emergence" proxy (a remotely-sensed mineral
  alteration signature, not the actual catalogued point locations) blended
  broadly across the whole image; it did not use the literal sinter/tufa
  point dataset or the well/spring temperature geodatabase as hydrologic
  anchors with gradient-projected corridors restricting the search area.
- **External data needed and obtainable?** Yes — `docs/SOURCES.md` #16/#17,
  GDR OpenEI submission 1391, CC BY 4.0, no login, confirmed live
  2026-10-27 (82 KB + 19.85 MB).
- **Expected DTI improvement:** Medium (point-sparse datasets — likely only
  a handful of anchors fall inside the specific GeoDAWN AOI, limiting
  recall). **Implementation cost:** Medium-high (requires a hydraulic
  gradient model, not just a static raster lookup).

---

## Rank 5 — H-D: Seismicity-anisotropy vs. nearest-catalogued-fault strike mismatch

- **Layers.** External: Nevada Seismological Laboratory *Earthquake Density
  Models* (independent + dependent density GeoTIFFs, `docs/SOURCES.md`
  #18). Official: none directly, but cross-referenced against the USGS
  Quaternary fault vector layer's strike attribute (provided as competition
  labels).
- **Physical signature.** Where earthquake density is locally elevated and
  anisotropic (its spatial gradient has a strong preferred azimuth, a weak
  but free proxy for a nodal-plane orientation when real focal mechanisms
  are not readily available), but the nearest catalogued fault's strike
  does not match that azimuth, flag the cell as a candidate blind fault
  with a different orientation than the mapped structure nearby.
- **Why it should catch missing, not catalogued, faults.** By construction
  it only fires where the *existing* catalogue entry fails to explain the
  observed seismic anisotropy — i.e., it specifically targets a structure
  the catalogue does not already represent at that location/orientation.
- **Named non-fault mimic.** Mining-induced or geothermal-injection-induced
  seismicity swarms unrelated to tectonic structure, and short-lived
  aftershock sequences — guarded by requiring the anisotropy to be
  persistent across the density model's full time window rather than an
  isolated swarm.
- **Differs from sibling sites.** Reviewed sibling names referencing
  seismicity (`h51-km-faultzone`, `seisdil-strain-seismicity`) used density
  or depth clustering alone; none implemented an explicit strike-mismatch
  test between seismicity anisotropy and the nearest catalogued fault's own
  strike attribute.
- **External data needed and obtainable?** Yes — `docs/SOURCES.md` #18,
  GDR OpenEI submission 1391, CC BY 4.0, no login, confirmed live
  2026-10-27 (22.98 MB).
- **Expected DTI improvement:** Lowest/most uncertain of the five (sparse
  seismicity catalogs inside a single AOI, and density-anisotropy is a weak
  nodal-plane proxy). **Implementation cost:** Medium.

---

## Mandatory next step before any of these touches a submission slot

1. Obtain the real `training_features.tif` / `labels.tif` /
   `sample_submission.tif` via `scripts/download_competition_data.sh`
   (requires a human to log in to DrivenData once — not possible from this
   sandbox).
2. Run `python scripts/prepare_data.py` to confirm the real grid matches
   `src/gems/grid.py::GEMS_GRID` (or correct the constant if not).
3. Implement H-A (rank 1) first. Score it with
   `src/gems/metric.distance_weighted_tversky_index` under a spatially
   blocked, whole-segment, buffered hide-and-recover holdout (never a
   random pixel split — see the parallel-run protocol's holdout definition
   and `research/sibling_site_audit.md` for why several sibling sites'
   holdouts were later invalidated for leaking catalogue support into fold
   placement).
4. Run the leakage canary: score H-A's *single* new feature alone; if its
   standalone AUC against held-out positives exceeds 0.90, treat it as
   leakage until proven otherwise (parallel-run protocol rule 4) — most
   likely cause would be the stress-tensor interpolation accidentally using
   held-out fault geometry to build the stress field.
5. Only promote to a weekly submission slot if H-A's paired 95% CI vs. the
   current holdout-best excludes zero, and its final-dot/surface uniqueness
   against the real DrivenData submission history (not the sibling sites'
   self-reported registries) is independently confirmed.
