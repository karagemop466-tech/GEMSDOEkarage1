# Review: session arena/9cf124bb-gemsdoekarage1 (2026-10-31)

**Verdict: NEGATIVE / DO NOT SUBMIT. No file is cleared. No weekly slot selected or spent.**

Labels: **USER-REPORTED / UNVERIFIED** (scores typed by users or taken from the ledger), **ORGANIZER-PUBLIC** (public page or board, not a receipt for our file), **HOLDOUT-DTI** (our local hide-and-recover score, evaluator `gems57-pooled-hide-v2`), **PROXY** (SGMC-off owner-derived mirror, not organizer truth). No projection is written as a score.

## 1. Answer

1. **No file is OK to download and submit.** Every nine-site file is a third-party file with a user-reported score. Our own new candidate is labelled research-only.
2. **Best reported file:** GEMSDOE32 (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`) at 0.2778 USER-REPORTED / UNVERIFIED. It is GEMSDOE25 with 6,436 dots removed, and it is not unique. Why it scored higher, and what would be needed to beat it: `knowledge/why-gemsdoe32-b2-20261031.md`.
3. **New unique file:** we generated a candidate (E1) that meets the format rules. It is **not** unique under the literal gate, and it fails the holdout test. It stays `DO-NOT-SUBMIT_`.

## 2. Nine-site table

Source: `evidence/nine_site_verification_20261031.json` (forward 3 px dot overlap; all nine files share one grid, EPSG:32611 3730×3292, 100 m). Uniqueness threshold: ≤ 70% of a file's dots within 3 px of any other registry file. "Max overlap" is the largest value against any other focus site.

| Site | File (registry mirror, third-party) | Estimate (score label) | Uniqueness vs the other listed sites | Download / submit verdict |
|---|---|---|---|---|
| GEMSDOE32 | `registry/GEMSDOE32_B2.tif` (`h33-h33-2-b2-…-zeros`) | 0.2778 USER-REPORTED / UNVERIFIED. No estimate from us. | **No.** Max overlap 1.0 (vs GEMSDOE24); min 0.9988. Strict subset of GEMSDOE25. | Study only. **Do not submit.** Not ours to resubmit. |
| GEMSDOE36 | `registry/GEMSDOE36_…-zeros.tif` | 0.2750 USER-REPORTED / UNVERIFIED | **No.** Max 0.9758 (vs GEMSDOE27). | Study only. **Do not submit.** |
| GEMSDOE28 | `registry/GEMSDOE28_…-nan.tif` | 0.2710 USER-REPORTED / UNVERIFIED | **No.** Max 1.0 (vs GEMSDOE24). | Study only. **Do not submit.** |
| GEMSDOE31 | `registry/GEMSDOE31_…-nan.tif` | 0.2708 USER-REPORTED / UNVERIFIED | **No.** Max 1.0 (vs GEMSDOE24). | Study only. **Do not submit.** |
| GEMSDOE33 | `registry/GEMSDOE33_…-cb490425926e.tif` | 0.2632 USER-REPORTED / UNVERIFIED | **No.** Max 0.9971 (vs GEMSDOE27). | Study only. **Do not submit.** |
| GEMSDOE25 | `registry/GEMSDOE25_d28.tif` | 0.2600 USER-REPORTED / UNVERIFIED | **No.** Max 1.0 (vs GEMSDOE24); identical mask to GEMSDOE30. | Study only. **Do not submit.** |
| GEMSDOE30 | `registry/GEMSDOE30_…-91eae1ca.tif` | 0.2600 USER-REPORTED / UNVERIFIED | **No.** Max 1.0 (vs GEMSDOE24); identical mask to GEMSDOE25. | Study only. **Do not submit.** |
| GEMSDOE24 | `registry/GEMSDOE24_…-nan.tif` | 0.2477 USER-REPORTED / UNVERIFIED | **No.** Max 1.0 (vs GEMSDOE25). | Study only. **Do not submit.** |
| GEMSDOE27 | `registry/GEMSDOE27_…-nan.tif` | 0.2449 USER-REPORTED / UNVERIFIED | **No.** Max 0.9802 (vs GEMSDOE24). | Study only. **Do not submit.** |

Notes:
- The "estimate" is the reported score, not our estimate. We have no estimate for any file: the local holdout does not track the public board (section 4).
- Every site fails the 70% gate against at least one sibling, so no site has a unique file.
- The committed files are mirror copies used for measurement. Mirror pins do not authenticate organizer content (IR-S1).

## 3. Our new candidate (E1, H-O2)

- **Method:** lidar scarp `step_max` peaks, minus dots within 2 px of the visible catalogue. The halo rule is applied per fold, from visible catalogue only. Pre-registration: `knowledge/hypotheses-20261031.md` §4. Script: `scripts/run_o2_halo_prune_lidar.py`.
- **Files (research only, `DO-NOT-SUBMIT_` prefix):**
  - Download, zeros variant: [`docs/downloads/DO-NOT-SUBMIT_karage1-o2-lidar-scarp-halo-prune-37654-20261031-zeros.tif`](docs/downloads/DO-NOT-SUBMIT_karage1-o2-lidar-scarp-halo-prune-37654-20261031-zeros.tif) (sha256 `a7c24d452097f75808fb798cd42e35c1dc867619e4ddd570cd5aab39d12b0497`)
  - Zip: [`…-zeros.zip`](docs/downloads/DO-NOT-SUBMIT_karage1-o2-lidar-scarp-halo-prune-37654-20261031-zeros.zip)
  - NaN variant: [`…-nan.tif`](docs/downloads/DO-NOT-SUBMIT_karage1-o2-lidar-scarp-halo-prune-37654-20261031-nan.tif)
  - Run card: `evidence/run_card_o2_20261031.json`; experiment record: `evidence/exp_o2_halo_prune_lidar_20261031.json`
- **Dots:** 37,539 (budget 37,654; 115 short because the peak set ran out). 0 dots within 2 px of the catalogue.
- **Validator (local format/range preflight, not organizer acceptance):** all checks passed. Values in [0, 1]; no NaN inside the footprint; CRS EPSG:32611; shape 3730×3292; transform matches the registry grid. NaN twin: NaN exactly outside the footprint, all checks passed.
- **Score:** HOLDOUT-DTI, evaluator `gems57-pooled-hide-v2`, 16 cells, 45,260 withheld positives:
  - arm A (unpruned) 0.044417
  - **arm B (candidate) 0.038756**, paired 95% CI of B−A [−0.006662, −0.004001]
  - matched random, seeds 101/202/303: 0.046185 / 0.045109 / 0.046330 (mean 0.045875)
  - H-R1 raster 0.043296; GEMSDOE32 B2 0.004729 (reproduces the record); GEMSDOE25 parent 0.102267
  - Holdout is not a leaderboard estimate (IR-H1).

### Criteria (pre-registered E1 rule)

| Criterion | Result |
|---|---|
| B pooled DTI > A, with paired CI lower bound > 0 | **false** |
| B > matched random | **false** |
| Every single-feature canary DI-AUC < 0.90 | **false** (`dist_to_visible_catalogue_px` 0.9085; `lidar_step_max_surface` 0.596 passes) |
| Validator and catalogue-zero check pass | true |
| NaN twin passes | true |
| Surface Spearman ≤ 0.90 vs every local TIF | true (max 0.0719) |
| Dot forward overlap ≤ 0.70 vs every local TIF | **false** (see section 5) |
| B > best reference (H-R1) | **false** |

**Verdict: negative.**

## 4. Why the holdout and the public board disagree

- The shared holdout scores recovery of withheld **mapped-catalogue** segments. The official round scores faults not in the public USGS database (ORGANIZER-PUBLIC, DrivenData problem page). These are different targets (IR-H1).
- Ordering contradicts the public board: B2 0.004729 holdout against 0.2778 public; GEMSDOE25 0.102267 holdout against 0.2600 public. The holdout therefore cannot rank candidates for the official round.
- The canary shows catalogue continuity alone reaches DI-AUC 0.9085 (IR-H2).
- The SGMC-off PROXY supports the halo mechanism. Arm A recall 0.220 / precision 0.087; arm B 0.218 / 0.086; random 0.154 / 0.071; B2 0.218 / 0.131. Halo-class precision 0.033 against 0.091 for non-halo. This is PROXY, not truth.

## 5. Uniqueness gate: what fails, and why it is not a dot-level clone

- **Literal gate result:** the candidate fails only against **one** local raster, `karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.tif` (overlap 1.0). That file is a probability blanket with 5,106,385 positive cells, 98.8% of the footprint. Any dot set inside the footprint will be "100% within 3 px" of it, so the literal gate can never pass against it. `registry/registry_roles.json` already says blankets should be reported as diagnostics, not duplicate stops. Owner decision (IR-B1).
- **Excluding the blanket**, the candidate's highest dot overlap against any of the other 32 compared local rasters is **0.2539** (`karage1-dipdual-dualregime-dipshift-…-zeros.tif`). The nine focus files are at most 0.1634.
- **The two rasters the first run could not compare** (`gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-{dots,zeros}.tif`, archived) sit on a different origin (500000, 4500000). They were compared in metres by `scripts/check_archived_hunq1_overlap_20261031.py`, output `evidence/gate_archived_hunq1_20261031.json`. Both overlaps are **0.0**, because the candidate's maximum x (498,300 m) lies 1.85 km west of the H-UNQ-1 minimum x (500,150 m). The check was self-tested: self-overlap 1.0; a 100 m shift overlap 1.0.
- So the full local count is 35 rasters: 32 compared at ≤ 0.2539, 1 blanket at 1.0, 2 archived at 0.0. No error remains.
- **Lattice:** at budget 37,654 the minimum possible forward overlap with the registry calibration lattice is 82.34% (above 70%). No set of that size can pass the literal gate against the lattice (`registry/registry_roles.json`).

## 6. How to fix "Predicted values must be in range [0, 1]"

Source: DrivenData problem page (ORGANIZER-PUBLIC): the submission must be a single-layer float32 GeoTIFF, values in [0, 1], EPSG:32611, 100 m, same bounds, cells outside bounds null or NaN.

- Write float32, single band, shape and transform identical to the registry grid.
- Clamp or write only 0 and 1 values inside the footprint. Write NaN (or the nodata convention) strictly outside the footprint. No sentinel values such as −9999.
- Check before upload: `min ≥ 0`, `max ≤ 1`, no NaN inside the footprint. The E1 validator checks all of these.
- **Which variant:** the **zeros** file passes every shared local check, including the repo's all-finite export policy. The **NaN** file is permitted by the organizer's public spec (NaN outside the bounds) but fails the repo's stricter all-finite policy (`no_nan_anywhere`, `outside_footprint_zero`) by design. It is the fallback only if the uploader rejects zeros outside the footprint. Receipts: `evidence/audit_o2_candidate_zeros_20261031.json`, `evidence/audit_o2_candidate_nan_20261031.json`.
- This validates the format only. It does not clear uniqueness or organizer acceptance.

## 7. Irregularities (flagged for manual review, not hidden)

- **IR-H1** shared holdout scores catalogue-segment recovery, not the off-catalogue target.
- **IR-H2** catalogue-continuity leak: `dist_to_visible_catalogue_px` DI-AUC 0.9085 (fails < 0.90).
- **IR-B1** the literal 70% dot-overlap gate fails against a local probability blanket, making it unsatisfiable. Owner must decide the policy.
- **IR-V1** local `vendor/gems57/submission_writer.py` and `uniqueness.py` differ from the PROVENANCE pins (and from upstream bytes for those two files). Not reconciled. Do not re-pin silently.
- **IR-S1** the restored `sample_submission.tif` has 60,988 positive cells, equal to the labels' positives, while the official page calls the sample "total fault absence".
- **IR-L1** the reference solution and the competition terms were not reviewed beyond the problem page. Manual review of these sources is still open.
- **IR-A1** the `13GEMSDOE` calibration lattice raster named in `registry/registry_roles.json` is not in this checkout, so `scripts/audit_local_tif.py` cannot run here. The two new receipts were written by `scripts/write_o2_audit_receipts_20261031.py` with the lattice comparison set to null and the reason stated. The repo's own audit tool should be re-run once the lattice is restored.
- **IR-L2** the 0.4413 leaderboard value cited in the request is absent from the top 50 on the 30 Oct re-read (ORGANIZER-PUBLIC). The #1 score on that re-read is 0.4544; 0.3195 is at rank #48.

## 8. Next steps (for the owner)

1. Decide the policy for probability blankets in the uniqueness gate. Under the current literal rule, no dot file can be cleared while `karage1-halo-damagezone-d2p0-…-zeros.tif` stays in the registry as a comparator. Changing the gate is a decision for the owner and must not be made silently.
2. Decide whether to align the holdout with the official target (off-catalogue faults) before any further holdout run. Any holdout arm that uses catalogue information must rebuild the visible catalogue per fold.
3. Reconcile `vendor/gems57` with its PROVENANCE pins (IR-V1), or document the fail-closed edit explicitly.
4. Resolve IR-S1 with the organizer's own sample file, through a hash-pinned source, before relying on the mirror.
5. Experiment budget: 1 of 3 used (E1). Do not run a further experiment without a new pre-registration.
6. No weekly slot selection in this session. That is a separate selector step.

## 9. Limitations

- No organizer receipt for any file. All scores here are USER-REPORTED or ORGANIZER-PUBLIC. No leaderboard estimate is possible from local evidence.
- The holdout measures a different target (IR-H1). It cannot rank candidates for the official round.
- The validator is a local format check, not organizer acceptance.
- The blanket finding depends on the literal gate. It is not a clearance of any file.
- Mirror pins do not authenticate organizer content.
- DrivenData downloads, OpenEI and Dropbox links are not reachable from this sandbox. Organizer data was obtained only through hash-pinned mirrors.

## 10. Official sources for manual review

- DrivenData competition page: https://www.drivendata.org/competitions/306/competition-doe-gems/
- Problem statement (metric, format, sample): https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- NLR rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS: https://gbcge.org/current-projects/ingenious/
- EPSG:32611: https://epsg.io/32611

## 11. Core values

**Maximize P(Win)** and **Own the Outcome**. Here that means no file is cleared without the gates passing. Negative results and blocked gates are reported as they are. Irregularities are flagged rather than hidden.
