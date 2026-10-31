# Preregistration — H-V31 visible-only gradient discriminator (session 2026-10-31)

Written **before** the experiment script was run. Any change after the run must be reported as a deviation.

## Experiment budget

Experiment 1 of 3 (geometry audit of the nine focus rasters, `scripts/focus_nine_audit.py`, no score) is already complete. This document preregisters Experiment 2 (the holdout below). One experiment slot remains unspent.

## Hypothesis

A discriminator trained only on **visible** catalogue fault pixels, using magnetic, gravity, geodetic-strain, and topographic channels from the restored 19-band stack, ranks off-catalogue pixels whose signature resembles fault-related gradients. Its top-N, 3-px-spaced dots should earn more pooled DTI on withheld catalogue segments than (a) uniform random dots, (b) the best single gradient channel, and (c) catalogue-proximity dots built from visible faults only.

## Mechanism

Faults in the sedimentary cover produce linear maxima of horizontal gradient and tilt/curvature in magnetic data, gravity-gradient lineaments, and small strain-rate contrasts. The model learns the multi-channel signature of such edges from visible segments and applies it to a region whose segments were withheld.

## Named non-fault mimics

Lithologic contacts (volcanic and intrusive margins), basin-margin gravity steps, topographic slope and relief artifacts (the detrended-elevation channels), acquisition stripes in magnetic data, and cultural magnetic sources. A positive result that concentrates along basin margins or topographic breaks is an artifact, not a fault.

## Data and provenance

- `data/training_features.tif`: 19 float32 bands, 3292 x 3730, EPSG:32611, 100 m. Restored from a SHA-pinned third-party mirror (`buffedlizard55-lab/GEMSDOE`); **not organizer-authenticated**.
- `data/labels.tif` = `data/existing_faults.tif` (byte-identical mirror files): catalogue fault pixels used as the truth source. **Not** the organizer's hidden new-fault labels.
- Footprint = finite cells of `data/sample_submission.tif` (5,167,373 cells). Mirror file; used only as grid and footprint template.

## Holdout design (hide-and-recover, spatially blocked)

1. Catalogue segments = 8-connected components of the catalogue pixel set.
2. Four folds = quadrants of the footprint split at its median column and row. A segment belongs to the quadrant containing its centroid.
3. For fold k: withheld truth = pixels of segments in quadrant k, restricted to quadrant k. Visible = all other catalogue pixels (masked pixel-exact in scoring).
4. Buffer = 10 px (1 km). Training positives exclude visible pixels within 10 px of withheld truth. Training negatives are footprint cells farther than 10 px from **any** catalogue pixel.
5. Model: LightGBM binary classifier on the 19 bands (NaN handled natively). Fixed hyper-parameters, set in the script before running: 300 trees, learning rate 0.05, 63 leaves, 200,000 sampled negatives, random seed 20261031.
6. Emission per fold: score every footprint cell in quadrant k, take the top N_k cells greedily with 3-px minimum spacing, where N_k is proportional to the fold's footprint cell count. Total budget N = 40,000 dots (family range of the nine focus files: 37,654 to 44,090).

## Controls (same folds, same N_k, same evaluator)

- **C1 random:** uniform random footprint cells, 3-px spacing.
- **C2 single-channel:** top-N_k cells by the `tmi_hg` channel (band 3), 3-px spacing, no model.
- **C3 catalogue-proximity (visible only):** random cells at 1–2 px from visible catalogue pixels, the B2-style rule applied without any withheld information.

## Leakage canary (protocol rule 4, before trusting any result)

For each fold and each of the 19 channels alone: ROC AUC of the raw channel value at withheld-truth pixels versus background (footprint cells in quadrant k farther than 10 px from any catalogue pixel). **AUC > 0.90 in any fold is treated as leakage until proven otherwise.** A failed canary stops the experiment as a negative result.

## Evaluator

Vendored `vendor/gems57/metric.py` (`dti_exact`, `max_cover`) and `vendor/gems57/evaluate_holdout.py` (`evaluate`, `pooled_summary`, evaluator version `gems57-pooled-hide-v2`), imported unchanged. These are reused directly. The gated `scripts/shared_tools.py` pipeline is **not** run because its preflight blocks on the unassigned lane and canonical template (`registry/template.json`). This deviation is recorded in the run card. Metric: alpha 0.2, beta 0.8, triangular kernel with radius 3 px (300 m).

Labels: every number is **HOLDOUT-DTI** with evaluator version, withheld positive pixel count, and a paired 95% percentile CI from 20 km spatial clusters (`pooled_summary`, 1000 draws).

## Decision rule (fixed in advance)

- **Promote to "selector-eligible":** candidate pooled DTI exceeds C1 and C2 with a paired-difference CI lower bound above 0, AND the canary passes in every fold, AND the uniqueness gate holds against the nine focus rasters.
- **Negative:** any failure of the above. A negative is a valid deliverable.

Promotion never spends a weekly slot. Slot selection is a separate step, subject to the cap on the submission page (not accessed from this sandbox).

## Explicitly not claimed

- No leaderboard estimate. A catalogue holdout is a proxy; prior calibration in this repository found catalogue truth does not rank catalogue-avoiding submissions reliably (`knowledge/session-review-arena-cfabff7e.md`).
- The lattice gate (13GEMS covering probe) is reported as measured. Its outcome is not waived here.
