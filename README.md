# GEMSDOEkarage1 — Fault Discovery, Evidence First

> **DO NOT SUBMIT — No candidate has been cleared for competition upload.**
> The generated research artifacts and historical references are published with full transparency for audit and learning. All historical files fail the literal lattice proximity gate (>70% overlap within 3 px), and new candidate CDA1 failed to surpass the historical holdout benchmark. A format validation pass is necessary but not sufficient for competition submission clearance.

[Decision Dashboard](docs/index.html) · [Executive Summary & Submission Guide](docs/executive-summary.html) · [Nine-Site Audit Data](docs/data/reference-audit.json) · [Two-Candidate Saved-Byte Audit](evidence/candidate_audit_20261028.json) · [Session Review](knowledge/session-review-arena-8ffb6de1.md) · [Research Hypotheses](docs/research.html) · [Official Source Register](knowledge/sources-2026-10-28.md)

---

## Executive Summary: Nine Focus Sites

The table below summarizes the highest scoring submissions across the nine focus sites (`GEMSDOE24`, `GEMSDOE25`, `GEMSDOE27`, `GEMSDOE28`, `GEMSDOE30`, `GEMSDOE31`, `GEMSDOE32`, `GEMSDOE33`, `GEMSDOE36`), along with our new candidate:

| Site | Recommended Download File | Reported / Estimated Score | Evidence Class | Uniqueness vs Peer Sites & Lattice | Recommended Action |
|---|---|---|---|---|---|
| **GEMSDOE32** | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.2778 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; subset of GEMSDOE25 (-6,436 dots) | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE36** | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; superset of B2 (+1,200 dots) | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE28** | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 | USER-REPORTED / UNVERIFIED | 99.91% vs lattice; 72 directional comparisons > 70% | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE31** | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; 59.09% vs B2 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE33** | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 | USER-REPORTED / UNVERIFIED | 99.91% vs lattice; 58.97% vs B2 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE25** | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; identical mask to GEMSDOE30 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE30** | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; identical mask to GEMSDOE25 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE24** | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; D1.5 crowded spacing | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE27** | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; 61.20% vs GEMSDOE24 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOEkarage1 (CDA1)** | `gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif` | 0.1473 [0.1331, 0.1612] | HOLDOUT-DTI (60,988 withheld positives) | **UNIQUE vs Peer 9 Sites** (max 62.94% ≤ 70%, max Spearman 0.3245 ≤ 0.90) | **DOWNLOAD FOR RESEARCH / AUDIT** (Fails literal lattice gate & primary holdout improvement) |

### Per-Site Summary Findings
- **GEMSDOE24 (0.2477):** Base H19-5 4-expert surface emitted with tight Poisson spacing $D=1.5\text{ px}$ (60,069 dots). Severely penalized by redundant clustering within the 300 m metric kernel.
- **GEMSDOE25 (0.2600):** Breakthrough widening of Poisson spacing to $D=2.8\text{ px}$ (44,090 dots), matching the 300 m triangular kernel and reducing false-positive penalty mass (+0.0123 gain).
- **GEMSDOE27 (0.2449):** Topographic gap closure on $D=1.5$ emission; penalized by scarp bridging errors across wide alluvial basins.
- **GEMSDOE28 (0.2710):** High-frequency Euler deconvolution paired with $D=2.8$ spacing; strong performance but heavily overlaps GEMSDOE25.
- **GEMSDOE30 (0.2600):** Explicit off-catalogue Poisson 300 m test; generated a positive-pixel mask byte-for-byte identical to GEMSDOE25.
- **GEMSDOE31 (0.2708):** Solo $D=2.8$ variant demonstrating cross-family leave-one-out validation stability.
- **GEMSDOE32 (0.2778):** The highest score in the peer registry. Applied a 2-pixel (200 m) exclusion collar around mapped catalogue faults to GEMSDOE25's $D=2.8$ mask, eliminating 6,436 redundant dots (37,654 dots total) and saving budget for unmapped discoveries.
- **GEMSDOE33 (0.2632):** Analog tip-stepover dilation model; suffered false positives from off-fault stress concentration artifacts.
- **GEMSDOE36 (0.2750):** Andersonian geothermal PINN; added 1,200 dots back into B2 (38,854 dots total), slightly lowering precision compared to B2.

---

## PhD-Level Forensics: Why GEMSDOE32 H33-2-B2 Scored 0.2778 and How to Beat It

### 1. The Operational Edge of H33-2-B2
Forensic analysis reveals that H33-2-B2 is **not a new geological discovery** — it is an operational optimization of the older H19-5 probability surface designed specifically around the DrivenData distance-weighted metric:
- **Tversky 300 m Triangular Kernel ($\alpha=0.2, \beta=0.8$):** The metric places a 300 m radius (3 pixels at 100 m resolution) triangular weighting disk around each hidden positive fault pixel. Any prediction within 300 m receives distance-weighted credit. However, having two or more predictions within the same 300 m disk provides zero incremental true-positive credit, while incurring a severe false-positive denominator penalty ($\beta=0.8$). The $D=2.8\text{ px}$ (~280 m) Poisson spacing near-optimally tiles the plane for this kernel.
- **Catalogue Collar ($B=2\text{ px} = 200\text{ m}$):** Because mapped USGS/INGENIOUS catalogue faults (`existing_faults.tif`) are excluded from hidden evaluation, any prediction placed on or immediately adjacent to a known fault earns zero credit but consumes limited dot budget. Deleting 6,436 near-catalogue dots freed 14.6% of the budget to hit true blind faults.

### 2. Why H33-2-B2 Plateaued Below the Leaderboard Top (0.4413)
- **Zero Subsurface Penetration in Covered Basins:** B2 relies exclusively on LiDAR topographic scarps and aeromagnetic gradients. In the Basin and Range province, over 50% of active geothermal fault systems (e.g., McGinness Hills, Bradys/Desert Peak step-overs, Carson Sink) are concealed beneath Quaternary alluvium, sand dunes, or pluvial Lake Lahontan lacustrine sediments where no surface scarp exists.
- **Lineage Saturation:** B2 correlates >0.90 with its parent H19-5; tuning emission thresholds on an existing surface cannot discover missing physical modalities.

### 3. How to Surpass 0.2778
To achieve scores >0.3195 and compete with the leaderboard top (0.4413), an orthogonal geological physics approach is required:
1. **Fluvial Drainage Deflection & Knickpoint Morphometrics:** Active blind faults deflect stream channels and create knickpoint clusters in drainage networks that persist long after surface scarps are buried by alluvium.
2. **Hydrothermal Alteration Geochemistry:** Upwelling geothermal fluids oxidize magnetite into hematite/pyrite (producing linear demagnetization troughs in the Magnetic Analytic Signal) and create potassic alteration halos (elevated K/eTh radiometric ratios).
3. **Deep Magnetotelluric (MT) Conductors:** 3D MT conductance captures deep crustal fluid pathways feeding geothermal reservoirs independent of surface cover.

---

## Pre-Registered Untried Geological Hypotheses

| Rank | Hypothesis | Target Physical Signature | Specific Layers Used | Why Off-Catalogue / Novelty | Confounder / Mimic | Implementation Cost |
|---|---|---|---|---|---|---|
| **1** | **CDA1: Drainage Deflection Asymmetry & Knickpoint Clustering** | Stream capture elbows (>90° deflection) & knickpoint second-derivative clusters along fault strike | 1 m / 10 m DEM, D8 flow-routing, detrended elevation | Identifies active blind piedmont faults buried beneath Quaternary gravels where scarps are absent | Lake Lahontan wave-cut terraces, agricultural ditches, alluvial fan risers | Low–Med |
| **2** | **H-K1-1: Hydrothermal Magnetite Destruction & K/Th Alteration Halos** | Linear demagnetization troughs in 3D Magnetic Analytic Signal coupled with high K/eTh residual ratios | GeoDAWN aeromagnetic RTP/TMI, GeoDAWN airborne radiometrics (K, eTh, eU) | Directly detects geothermal fluid pathways where ascending thermal water destroyed magnetite | Non-magnetic sedimentary interbeds, felsic vs mafic lithologic contacts | Med |
| **3** | **H-K1-3: Deep MT Conductance Conduit & Basement Step Coupling** | Steep lateral gradients in crustal electrical conductivity (15–35 km) aligned with basement depth flexure | INGENIOUS 3D MT conductance, depth-to-basement | Senses primary deep crustal fluid feeders beneath thick volcanic blankets | Conductive clay-rich basin brine layers, conductive volcanic tuffs | Med–High |
| **4** | **H-K1-4: Dilatational Step-Over Relay Curvature Polarity Reversal** | Along-strike profile curvature sign reversal across en-echelon overlapping fault segments | Detrended LiDAR DEM curvature ($\sigma=1.5, 3.0$ px) | Focuses on fault step-overs and pull-apart grabens where geothermal upflow concentrates | Erosional gully heads, road cut-and-fill embankments | Low |

---

## Unique TIF Submission & Error Resolution

### 1. Fix for DrivenData Error: `"Predicted values must be in range [0, 1]"`
- **Cause:** DrivenData's backend validator checks that every finite value in the uploaded GeoTIFF lies within $[0.0, 1.0]$. The error occurs when files include:
  1. Negative nodata sentinel values (such as `-9999.0` or `-3.4028235e+38`).
  2. Unhandled NaNs or Infs inside the footprint.
  3. Raw integer scores scaled to $0..255$.
- **Automated Fix Guaranteed in Our Artifact:**
  - Raster is written as single-band `float32`.
  - In-footprint values: strictly binary $0.0$ or $1.0$ (or continuous probabilities in $[0.0, 1.0]$).
  - Outside-footprint values: filled with $0.0$ (finite) and `nodata=None`, ensuring global `min = 0.0` and global `max = 1.0` across the entire $3730 \times 3292$ grid.
  - CRS: `EPSG:32611`, Transform: `[100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]`.

### 2. Available Artifacts for Download & Inspection
- **TIF File:** [`docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif`](docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif) (133,661 bytes, SHA-256: `753b8d47f951894240a80826e8100216c5e84613caf3d2596272d26a1b85c120`)
- **ZIP Package:** [`docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b.zip`](docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b.zip) (Contains single matching GeoTIFF)
- **Submission Name:** `gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros`
- **Submission Note (108 chars ≤ 140 chars):**
  `KARAGE1 CDA1 channel-deflection+pipe+shoreline-null 37654d B2 | HOLDOUT-DTI 0.1473 n=60988 | 753b8d47f951`
- **Zero Human Intervention:** Validation is executed autonomously via `scripts/validate_geotiff.py` and `scripts/validate_artifact.py`.

---

## Verbatim Standing Prompt — Mandatory Task Specification

The following is the full, unabridged text of the user prompt provided to this repository:

```text
Review the repo. 

I want to focus on the highest scoring submissions from the following sites, GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36. I want an executive summary on every site that is clear and obvious which is the best submission to submit to obtain a high score on the leaderboard. It should also be unique and not an exact duplicate of any previous submission that is the same as below. Keep iterating and testing until we have the highest scoring submission to download and submit.

We should be able to estimate the score for a submission. I want a table in the executive summary that clearly lists what file to download, what the estimate score is, and whether it is a unique submission unlike any of the other GEMDOE sites listed below.

THE FOLLOWING IS THE HIGHEST URGENCY AND MUST BE FOLLOWED!

MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION. IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.

There should be an easy to download submission tif file as described by the prompt. Read the entire prompt. A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.

PARALLEL-RUN PROTOCOL — read first. This session is one of several running from this same prompt.

1. LANE. Your lane is the single method paragraph below. Stay inside it. If your raster's rank-correlation with any registry raster exceeds [0.90], or more than [70%] of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.

2. REUSE, DON'T REBUILD. Use the template's cached feature stack, evaluate_holdout.py and submission_writer.py. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.

3. LABEL EVERY NUMBER as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.

4. LEAKAGE CANARY. Test each feature alone on the holdout before trusting any result. AUC above [0.90] means leakage until proven otherwise.

5. RUN CARD. End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.

6. BUDGET. Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.

The following sites should serve as a starting point for understanding how to generate TIF submissions. These websites are researched, and tested and have generated TIF submissions. But we need to generate high scoring submissions.

[https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)
h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778
Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778?
Answer the question using Phd level experience, knowledge, and judgement. Then use the answer to generate a unique TIF submission into the competition. Must be unique submission unlike any within the GEMSDOE sites above. Verify working line by line no hallucinations.
Current competition leaderboard GEMSDOE high score: 0.4413
```

---

## Remaining Work and Next Session

1. **Obtain Missing Method-Lane Paragraph:** Clarify the designated parallel lane and shared feature cache provenance with the coordinator.
2. **Resolve Dense Calibration Lattice Protocol Conflict:** Because a 5-pixel grid covers >99.8% of the footprint within 3 pixels, establish an updated distance/overlap rule that distinguishes calibration grids from peer submission clusters.
3. **Phase-2 Multimodal Modeling:** Incorporate external InSAR phase gradients and 3D MT resistivity inversion meshes once authenticated data ingress is established.

---

## Historical Session Reviews & Prior Audits

<details><summary>Expand Prior Session Records</summary>

- [Session `arena/8ffb6de1` Review](knowledge/session-review-arena-8ffb6de1.md) · [Run Card](evidence/run_card_arena_8ffb6de1.json)
- [Session `arena/0150ae73` Review](knowledge/session-0150ae73-review.md) · [Run Card](evidence/session_0150ae73_run_card.json)
- [Session `b65a5aab` Review](knowledge/session-b65a5aab-review.md) · [Run Card](evidence/session_b65a5aab_run_card.json)
- [Session `arena/43868644` Review](knowledge/session-review-arena-43868644.md) · [Run Card](evidence/run_card_arena_43868644.json)
- [Session `arena/0fb1ec81` Review](knowledge/review-arena-0fb1-20261028.md) · [Reassessment](evidence/reassessment_arena_0fb1_20261028.json)
- [Session `arena/9ad4a8a0` Review](knowledge/session-review-arena-9ad4a8a0.md) · [Run Card](evidence/run_card_arena_9ad4a8a0.json)
- [Session `0f04bfcc` Review](knowledge/session-0f04bfcc-review.md) · [Run Card](evidence/session_0f04bfcc_run_card.json)
- [Session `5b69d76e` Review](knowledge/session-5b69d76e-review.md) · [Replayed Audit](evidence/session_5b69d76e_prior_audit.json)
- [Session `a0f0d036` Review](knowledge/session-a0f0d036-review.md) · [Run Card](evidence/session_a0f0d036_run_card.json)
- [Session `470a3424` Review](knowledge/session-review-2026-10-28.md) · [Audit Record](evidence/session_review_2026-10-28_arena-470a3424.json)

</details>
