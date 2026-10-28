# Preregistration — DIPDUAL lane (session `arena/147b0f11-gemsdoekarage1`)

Written **before** any DIPDUAL experiment in this session: 2026-10-28T22:38Z.
Budget: ≤3 experiments. No weekly submission slot is selected or spent by this
work; promotion (if any) is to a separate selector step only.

## Lane-assignment irregularity (flagged, not hidden)

The supplied prompt's Parallel-Run Protocol refers to "the single method
paragraph below", but no method-lane paragraph is present in the prompt as
supplied to this session (the same absence is recorded in
`evidence/sources/GEMSDOE32.md`). The same prompt explicitly instructs:
generate 3–5 new geological hypotheses, rank them, and validate the top
candidate on the spatially blocked holdout before touching a slot. This
preregistration therefore (a) records the ranked slate, (b) adopts the
top-ranked hypothesis as this session's single lane, and (c) stays inside it.
No other geological lane is run this session.

## Why h33-h33-2-b2 reported 0.2778 — verified mechanism (measured this session)

All historical scores below are **USER-REPORTED / UNVERIFIED** (no
organizer receipt in this workspace). Mask identities were re-measured on
SHA-256-pinned mirrors in this session:

* H19-5 scored artifact is a **binary 121,131-px mask** (reported 0.1922).
* D2.8 parent (GEMSDOE25 ≡ GEMSDOE30 masks, 44,090 dots, reported 0.2600) is a
  2.8-px-spaced dotted subset of that mask: `parent ⊂ H19-5 mask` exactly.
* `parent − {dist_to_catalogue ≤ 1 px}` (40,199 dots) ≡ GEMSDOE31 ≡
  GEMSDOE28 h27-4-r1 masks exactly (reported 0.2708).
* `parent − {dist_to_catalogue ≤ 2 px}` (37,654 dots) ≡ GEMSDOE32
  h33-h33-2-b2 exactly (reported 0.2778).
* GEMSDOE36 (38,854, reported 0.2750) = B2 ∪ 1,200 extra dots exactly.

Interpretation (metric algebra, official DTI α=0.2, β=0.8, 300 m triangular
kernel; known-fault **pixels** masked per DrivenData staff thread 11516):
dotting removes redundant max-cover mass inside the 300 m kernel, and the
200 m collar deletes near-catalogue dots whose realised kernel credit was
below the marginal bar (≈ α·DTI for a non-redundant dot). B2's win is
therefore **emission hygiene on a multiline topographic/geophysical mask**,
not evidence that its surface is the best available geology. Deleting dots
can also *lose* coverage (new faults can lie within 300 m of known ones), so
the ladder does not prove a larger collar is better. Beating B2 requires a
surface that ranks **off-catalogue** expert-mappable traces higher, emitted
with at least B2's hygiene — while not copying B2's dots.

## Ranked candidate hypotheses (3–5, new to this repo)

| Rank | Hypothesis (layers → signature) | Why off-catalogue? | Difference vs prior art in this repo/fleet | Cost |
|---|---|---|---|---|
| **1 (LANE)** | **DIPDUAL — dip-projected dual-regime multiline.** Exposed regime: `det_elev` step-edge + profile-curvature break + 1 m LiDAR `step_max` polarity asymmetry `|down−up|/(down+up)`, gated by gravity-polarity concordance + contour obliquity, TIGER road-distance veto. Buried regime: `iso_grav_anom` + `depth_to_base_surf` multiscale gradient ridges (BB-STEP components) **shifted updip** by `clip(dtb,0,2500 m)/tan60°` (≤8 px) toward shallow basement. Regime split by label-free slope rank; split dot budget. | Exposed: sub-metre scarps visible in 1 m LiDAR post-date Qfaults airphoto compilation. Buried: basement step under alluvium has no scarp for Qfaults to map; the gravity ridge sits over the *deep* fault point, while an expert surface trace extrapolates updip — unshifted ridges are systematically offset by up to ~800 m. | BB-STEP (this repo) placed dots **on** the unshifted ridge with a low-slope veto only; GPC-Z used exposed physics only; HMAS used dual-cover by LiDAR availability, not slope regime + dip geometry. Fleet near-prior: GEMSDOE92 fixed-offset "updip50" (reported 0.0255) and GEMSDOE80/84 "two-regime" fusions (0.094/0.013) — neither used depth-proportional shift of a buried-only regime with quota emission. Novelty across the full fleet is **not** claimed beyond the audited registry. | Medium (CPU, cached bands) |
| 2 | Fold-local catalogue **tip/stepover continuation** gated by label-free ridge continuity (visible-fault vector geometry only per fold). | Mapping stops where scarp dies under alluvium; fault continues along strike. | GEMSDOE33 analog-tip (reported 0.2632) was D2.8-derived; GEMSDOE10 pure continuation reported 0.0461. Ridge-gated fold-local version untried here. Budget-limited (tips are sparse). | Medium |
| 3 | Radiometric **K/Th boundary termination** at an RTP magnetic edge (boundary geometry, not hotspot strength). Layers: GeoDAWN K, Th, U, TC + `rtp`. | Alteration boundary offset/terminated by a concealed fault. | HMAS used K/Th crests/halos; termination geometry untried. Mimics: K-rich intrusions, survey seams (acquisition-block mask available). | Medium |
| 4 | **Signed paired-edge displacement** between magnetic and gravity edge traces across scale (`rtp` vs `iso_grav_anom`). | Dipping contact juxtaposing units of different depth extent under fill. | Prior work sums unsigned edges; relative displacement untried (three-pass slate #1). Live relevance uncertain: experts rarely map from this alone. | Medium–high |
| 5 | Multi-catchment tributary asymmetry (drainage deflection) conditioned on area/elevation. | Degraded trace deflects several channels without a sharp scarp. | CDA1 archive claimed this but its evaluator was hard-coded (invalid). Real test needs stream extraction at 100 m (coarse) — deferred. | High |

External data: DIPDUAL needs **no new external data**. All inputs are the
pinned competition bands plus owner-mirrored derivatives already in
`registry/karage1_data_manifest.json` (USGS 3DEP-derived LiDAR u8, USGS
GeoDAWN DOI 10.5066/P93LGLVQ radiometrics, Census TIGER road distance).
Mirrors are hash-pinned, **not organizer-authenticated** (standing
limitation).

## Lane definition (binding for this session)

* Surfaces are **label-free**: nothing reads `labels.tif` except (i) fold
  construction, (ii) the fold-visible catalogue apron in emission, (iii)
  scoring. Final build uses the full catalogue apron only.
* Emission everywhere: `gemsk.emission` Poisson greedy, spacing 2.8 px,
  apron 2 px from visible (fold) / full (final) catalogue, binary dots.
  Per-fold budget 37,654 (matches B2/GPC arms) unless an EXP3 row says else.
* Evaluator: `gemsk-hide-recover-v1` (whole 8-connected components,
  20 km checkerboard **blocked** folds primary; α=0.2, β=0.8, 300 m kernel;
  pooled DTI; 20 km block-bootstrap 95% CI, paired).
* Second instrument (diagnostic, apron-fair): off-catalogue SGMC faults
  (`derived_sgmc_faults_100m_u8`, truth = SGMC ∧ footprint ∧ dist_to_catalogue
  > 3 px; n=62,122), static full-apron dots, same DTI arithmetic.
  SGMC is a geologic-map compilation, **not** the hidden test set.

## Experiments (≤3)

* **EXP1 — leakage canary + pre-placement gate.** Each component and fused
  surface alone: direction-invariant AUC vs withheld truth on blocked folds.
  Alarm if >0.90, non-finite in footprint, or constant. Pre-placement
  Spearman of the dual surface vs every registry raster (400 k footprint
  sample). Dip diagnostic: distance from buried-ridge top dots to withheld
  truth, shifted vs unshifted.
* **EXP2 — head-to-head holdout.** Arms (fold-local emission, identical
  budget/spacing/apron): DIPDUAL 65/35, GPC-physics-only control,
  BB-STEP-only control. Blocked pooled HOLDOUT-DTI + paired CIs; SGMC
  diagnostic for static builds of the same surfaces + static B2 (fair on
  SGMC because SGMC ≠ apron source). Static B2 on catalogue holdout is
  censored by its full-catalogue apron and is reported only as a diagnostic,
  never as the control to beat.
* **EXP3 — lane-internal sweep.** Split {50/50, 65/35, 80/20}, dip {on,off}
  at the better split neighbourhood, collar {2,3} px sensitivity. Pick the
  final configuration by EXP2/EXP3 blocked + SGMC jointly per gates below;
  no new mechanism.

## Promotion gates (fail-closed; all required for `promote`)

1. Canary: no alarm in EXP1.
2. Blocked holdout: DIPDUAL beats BB-STEP-only (paired CI lower > 0) **and**
   does not collapse vs GPC-only (paired Δ CI lower > −0.010).
3. SGMC diagnostic: DIPDUAL beats the better of {GPC-only, BB-STEP-only}
   (paired CI lower > 0). (Rationale: SGMC is the only off-catalogue fault
   truth available locally; the live test is off-catalogue by definition.)
4. Format: shared `submission_writer` + independent re-read: single-band
   float32, EPSG:32611, shape/transform = sample, finite [0,1] everywhere
   (zeros encoding), 0 dots on catalogue, 0 positive outside footprint.
5. Discrete uniqueness: forward 3-px overlap ≤0.70 **and** |Spearman| ≤0.90
   (surface pre-placement and final dots) vs every discrete registry raster
   restored this session (15 `registry/` files + scored H19-5/H19-4/H16-1 +
   local `docs/downloads` candidates). Reverse overlap + Jaccard reported.
6. Lattice handling (explicit deviation, see below).

## Lattice irregularity IR-DIPDUAL-LATTICE-01

The pinned 13GEMSDOE s5 lattice (206,895 dots) lies within 3 px of
5,160,724/5,167,373 footprint cells (99.8713%; re-measured this session).
Only 6,649 footprint cells are >3 px from it, so **any** N-dot raster has
forward lattice overlap ≥ (N−6,649)/N: ≥82.34% at B2's N=37,654. B2 itself
measures 99.915% forward (reverse: 15.06%; Spearman ≈0). The literal
forward-only rule therefore fails every competitive-budget raster including
all 21 audited focus submissions and cannot discriminate lane drift (its
intent) from blanket coverage. This session: lattice overlap is **measured
and published**, the lattice is classified `calibration_probe` (role
separation proposed as GEMSDOE32 IR-42-UNIQ-01), and the duplicate gate is
applied to discrete submissions. The run card records
`lattice_duplicate_literal` truthfully; the selector must acknowledge this
deviation. If the selector requires the literal reading, the correct verdict
for **every** candidate at N≳22,000 — including B2 — is duplicate/stop.

## Number labelling

Every number is HOLDOUT-DTI (evaluator, withheld positives, 95% CI),
SGMC-DIAGNOSTIC-DTI (defined above), or USER-REPORTED / UNVERIFIED.
No live-score projection will be written. Catalogue holdouts rank live
scores only weakly across detector families (repo-recorded Spearman ≈0.5,
n=12); a holdout win is a screen, not a leaderboard estimate.
