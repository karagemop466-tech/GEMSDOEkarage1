# Review — `arena/b2a6d9d1-gemsdoekarage1` — 31 October 2026

## 1. Decision (read this first)

- **NOT CLEARED — DO NOT DOWNLOAD OR SUBMIT ANY FILE FROM THIS CHECKOUT.** No new TIFF was generated in this session. No holdout was run. No slot was selected or spent.
- **Why no new TIFF:** the user's own parallel-run protocol requires a single assigned method paragraph. That paragraph is not in the prompt, and `registry/template.json` records `method_lane: null`. Without a lane, the registry-overlap and holdout gates cannot be run for a new candidate. A file generated anyway would be unclaimed, untested, and would fail the protocol.
- **What did get verified this session** (details below): the live leaderboard, the official submission format, the metric transcription, the restored data, a format check on all 31 TIFs in this repo, and the B2-versus-GEMSDOE25 subset relation.
- **Correction to the request:** 0.3195 is **not** the highest score. The live public leaderboard's #1 is **0.4544**. On the live page 0.3195 is rank **#50** (not #48 as the README previously said). 0.4413 does not appear in the top 50.

## 2. Verified live today (ORGANIZER-PUBLIC, read 2026-10-31)

| Claim | Status | Evidence |
|---|---|---|
| #1 = 0.4544 (xiaofanhu) | **Verified** | [leaderboard, chunk 0](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) |
| #2 = 0.3925 (cfld__) | **Verified** | same page |
| #47 = 0.3261, #48 = 0.3231, #49 = 0.3217, #50 = 0.3195 | **Verified** | same page, chunk 1–2 |
| 0.4413 in the top 50 | **Not found** (list ends at #50) | same page |
| "0.3195 is the highest score right now" (request) | **Incorrect** | #1 is 0.4544 |
| Scores 0.2778 and the nine focus-site values | **USER-REPORTED / UNVERIFIED.** Not on the public board by file name; the board lists teams, not files | — |

The leaderboard is time-sensitive: "ago" timestamps show it changes daily. Ranks are the public DW-Tversky score, not the private test score that decides the initial prize round.

## 3. Official rules (fetched and read this session)

Source: [competition problem description, page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) (fetched 2026-10-31).

- Metric: distance-weighted Tversky, α = 0.2 (false positives), β = 0.8 (false negatives), triangular kernel, R = 300 m = 3 px at 100 m.
- Format: GeoTIFF, **EPSG 32611**, **100 m** resolution, same bounds as training data; **single layer, float32**; values **between 0 and 1**; **"data outside the bounds is null or nan."**
- Initial prize round scores against a **private** set of expert-labelled new faults. The Final round rescores against an **expanded** label set that includes faults experts verify from submissions. Competitors choose **one** submission for both rounds.
- The official text does not contain the 70 % / 3-px lattice gate. That gate is an internal protocol rule of this repo and is labelled as such.
- The rules PDF named in the request ([docs.nlr.gov/docs/fy26osti/96647.pdf](https://docs.nlr.gov/docs/fy26osti/96647.pdf)) and the [Wikipedia Tversky page](https://en.wikipedia.org/wiki/Tversky_index) were **not fetched in this session**; they are listed as manual-review links only.

## 4. Upload error: "Predicted values must be in range [0, 1]"

Checked with `scripts/check_official_format.py` on all 31 TIFs in `docs/downloads/`, `registry/`, and `archive/` (evidence: [`evidence/official_format_check_20261031.json`](../evidence/official_format_check_20261031.json)).

- **No local TIF contains a value outside [0, 1]** (`out_of_range_count = 0` for every file). So the error text does not match the value content of any file in this repo.
- **Outside-footprint encoding is the difference.** The official reference (`sample_submission.tif`) uses NaN outside the footprint (7,111,787 NaN cells; 5,167,373 finite cells inside). Of 31 files, **10 use NaN outside** and pass the literal official check. **19 use 0 outside** (the repo's "zeros" variants) and fail the literal text; 2 are mixed.
- Recommendation for any upload: use the NaN-encoded variant and check it with the script before uploading.
- **Cannot reproduce the error.** The exact filename the user uploaded is unknown. Ask for it; do not assume.

## 5. Why GEMSDOE32 B2 = 0.2778 (USER-REPORTED) — analysis

**Verified facts (local, `registry/`):**
- B2 has 37,654 positive cells. GEMSDOE25 and GEMSDOE30 each have 44,090 — and **their positive masks are identical** (`G25_eq_G30 = true`). That is a duplicate pair: same mask, same reported score 0.2600. Flagged.
- B2 is a **strict subset** of GEMSDOE25: 0 B2 cells outside G25; **6,436** G25 cells removed in B2; 0 added. Evidence: [`evidence/b2_subset_check_20261031.json`](../evidence/b2_subset_check_20261031.json).
- Within the 5,167,373-cell footprint, B2 is a pure **removal**. It did not add any new location.

**Mechanism (metric arithmetic, verified in code).** With α = 0.2 and β = 0.8, a false positive costs 0.2 and a false negative costs 0.8. For a binary dot field, a new dot with kernel self-credit *k* raises DTI only when *k* > α·DTI (for a non-redundant dot). At DTI ≈ 0.28, the bar is *k* ≈ 0.056, i.e. a dot must be within about 2.8 px of a truth cell. A dot that is farther than that from every truth cell only adds false-positive cost. So removing dots with near-zero credit raises the score. That is the most plausible reading of why a pruned subset scored higher than its parent (0.2778 vs 0.2600, user-reported).

**What this does not establish:** which of the 6,436 removed cells were false positives under the private labels. That is untestable here. The gain is consistent with the metric, but the private labels are the only evidence that would show it. Labelled: **interpretation, not measurement.**

**Verification of the arithmetic:** [`scripts/verify_dti_threshold.py`](../scripts/verify_dti_threshold.py) → [`evidence/dti_threshold_check_20261031.json`](../evidence/dti_threshold_check_20261031.json). The fast EDT-based DTI matches the literal brute-force equations to 1.7e-16 on 40 random soft grids; the binary and exact paths agree to 1.1e-16; the one-dot marginal rule agrees with a recomputed DTI on 300 of 300 trials. This is software verification on random grids, not a holdout.

**Design implication (labelled PROJECTION-FREE, no score):** because the optimal bar is low (about 5–6 % expected kernel credit at DTI ≈ 0.28), a candidate should be judged by its **expected kernel credit per dot**, not by how "clean" its dots look. A candidate that is precise but sparse can lose to a broader set that clears the bar. This is a testable design rule, not a leaderboard estimate.

## 6. Data restore (done) and irregularities

- Restored the four core files with `scripts/restore_karage1_data.py --group core`. SHA-256 and byte counts matched the pins. **These are third-party GitHub mirrors, not organizer-authenticated.** The data tab on DrivenData requires login, which this sandbox does not have.
- `data/labels.tif` and `data/existing_faults.tif` are **byte-identical** (both `7ba308cc…`). The two catalogue files the manifest lists separately are the same file. Flagged; do not treat them as independent sources.
- `data/sample_submission.tif` defines the footprint by its NaN pattern. That is an inference from the sample, not a documented bound.
- The shared holdout stack (`.cache/gems_work/feature_stack.npy`) is still absent. No holdout was run.

**Irregularities for review:**
1. The request says 0.3195 is the highest score; the live #1 is 0.4544.
2. 0.3195 is rank #50 live (README says #48, a previous snapshot).
3. GEMSDOE25 and GEMSDOE30 have identical positive masks; both report 0.2600.
4. Labels and existing-faults catalogue files are byte-identical.
5. 19 of 31 local TIFs encode 0 outside the footprint, contrary to the official "null or nan" wording.
6. The upload error text is not reproducible from any local file. The exact filename is unknown.
7. The protocol's method lane paragraph is absent from the prompt.
8. The 70 %/3-px lattice gate is an internal rule, not an official one. The README already records that it saturates for dot sets above about 22,163 dots (repo claim, not re-derived here).

## 7. Candidate hypotheses (carried forward, not validated)

These come from the prior review `knowledge/review-arena-946f7668-20261031.md` (section "Candidate hypotheses") and remain proposals. None has a holdout result.

1. Cross-field boundary displacement between `tmi_hg` and `iso_grav_anom` edge ridges, conditioned on `depth_to_base_surf` gradient.
2. Multi-scale curvature-polarity continuity (`curv_s1`, `curv_s2`, `ridge_s1..3`, `relief5`).
3. Stratigraphic-boundary termination of `cond_surf` / `depth_to_base_surf` edges.
4. Directional strain-transition segmentation (`geod_shearrate`, `geod_dilaterate`) across magnetic lineaments.

**Added this session (from the verified metric arithmetic, not from new data):** rank candidates by expected kernel credit per dot against the bar α·DTI, and validate on the holdout before any slot is spent.

## 8. What is needed before any file can be cleared

1. **Owner decision:** assign the method lane (the missing paragraph), and say whether the 70 %/3-px gate applies as written.
2. **Shared stack:** build `.cache/gems_work/feature_stack.npy` with the shared tools; resolve the writer/uniqueness provenance mismatch that `scripts/shared_tools.py preflight` reports.
3. **Holdout:** run the shared hide-and-recover evaluator; report HOLDOUT-DTI with evaluator version, withheld positives, and 95 % CI.
4. **Organizer receipts:** a score can only be called ORGANIZER-CONFIRMED from a submission-page receipt. None exists in this repo.
5. **Upload packet:** NaN-encoded TIF, format check passing, unique name, and a note of at most 140 characters, produced only after items 1–4.

## 9. Sources (verification status)

- [Competition problem description, metric and format — fetched 2026-10-31](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Public leaderboard — fetched 2026-10-31, three chunks](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Competition data tab (login required) — linked, not fetched](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Reference solution — linked, not fetched this session](https://github.com/drivendataorg/gems-prize-reference-solution)
- [DOE/NLR rules PDF — linked, not fetched this session](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN data release — linked, not fetched this session](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project — linked, not fetched this session](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611 — linked, not fetched this session](https://epsg.io/32611)
- [Tversky index (Wikipedia) — linked, not fetched this session](https://en.wikipedia.org/wiki/Tversky_index)

## 10. Test status

`.venv/bin/python -m pytest -q` → **447 passed, 1 skipped, 126 warnings** (the skip needs an ignored bridge raster). Warnings are Rasterio deprecation notices. This is software verification, not model validation.
