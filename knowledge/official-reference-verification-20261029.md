# Official reference solution — line-level verification (29 Oct 2026)

**Session:** `arena/6275e37e-gemsdoekarage1` · **Scope:** what the official DrivenData reference repository states, checked from a pinned commit.
**Verdict on use:** source facts only. Nothing here is a score, a submission, or an organizer receipt.

## 1. What was fetched, and how

| Item | Value | Evidence class |
|---|---|---|
| Repository | [drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) | official organizer repository |
| Pinned commit | `aebe92f7c8a990f0e3443451b7a825d9afd6336b` (single commit, "initial commit") | verified by `git rev-parse HEAD` on a fresh clone |
| Commit author field | `Chris Kucharczyk <chris@drivendata.org>` | a git author field is not authentication; it is recorded only |
| Notebook | `unet-mc-cv-reference-solution.ipynb` | SHA-256 `1a7622732ba00f67237058bc0efe79b45ba4e87c449fc9c1e5d6ea659de92ca0` (21 cells) |
| `README.md` | SHA-256 `cfa4d55559c9128313beb9417eae7e0a94c31677132afb1120f9e86222804239` | matches [`evidence/official_source.json`](../evidence/official_source.json) |
| `data/` | contains only `.gitkeep` | the competition data is **not** in the official repo |

How it was obtained: `raw.githubusercontent.com` is outside the sandbox allow-list; the GitHub REST API was rate-limited (HTTP 403 "API rate limit exceeded"); the public `github.com` clone succeeded. The commit SHA was then checked with `git cat-file`.

Browser-facing pages on `drivendata.org`, `docs.nlr.gov`, `epsg.io` and `pubs.usgs.gov` were **not reachable** from the sandbox (connection code `000`). Every claim about the DrivenData problem page, the leaderboard, or the NLR rules PDF in this file is therefore **carried forward from earlier sessions, not re-verified today**.

## 2. Line-level facts (cell index and line number inside the notebook)

| # | Fact | Location in notebook | Link |
|---|---|---|---|
| R1 | Feature path is `data/numeric_features.tif`; label path is `data/labels.tif` | cell 2, lines 1–2 | [permalink](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb) (search cell 2) |
| R2 | Features with values `< -1e38` are set to NaN, then each band is min–max normalised to [0, 1] | cell 5, lines 26, 32–34 | same |
| R3 | Labels are binarised: `y_orig[y_orig < 1] = 0` | cell 6, line 24 | same |
| R4 | Loss is `TverskyLoss(alpha=alpha, beta=beta, mode="binary")` with `alpha = 0.2`, `beta = 0.8` | cell 16, lines 8, 9, 67; import cell 1, line 14 | same |
| R5 | Output is `F.sigmoid(outputs)`, so each prediction is in (0, 1) | cell 16, line 97 | same |
| R6 | Writer: `y_final = y_combined[:H, :W]`; GeoTIFF with `count=1`, `dtype=y_final.dtype`, CRS and transform copied from `labels.tif`; **no `nodata` argument; no NaN masking** | cell 19, lines 1–20 | same |
| R6a | The output buffer is `y_out = np.zeros(y_patches.shape)` with **no dtype**, i.e. float64 by NumPy default; `y_combined = unpatchify(y_out, …)` (cell 16, line 155) dispatches to the 2-D helper `_unpatchify2d` (cell 11, line 53), which allocates its output with the patch dtype (line 67). Nothing casts to float32, so the reference writes **float64** | cell 16, lines 37 and 155; cell 11, lines 53 and 63–67 | same |
| R7 | Author note: "it may be advantageous to threshold this map for better scoring" | cell 17, line 2 | same |

**What R1–R7 establish:** the official reference writes a float raster whose values are all in [0, 1] and whose grid comes from `labels.tif`. It does not write NaN outside the footprint.

**What they do not establish:** the competition's distance-weighted scoring function. R4 is the per-pixel Tversky **training loss** from `segmentation_models_pytorch`, not the 300 m kernel metric in the problem statement. The local metric (`vendor/gems57/metric.py`: `ALPHA = 0.2`, `BETA = 0.8`, `RADIUS_PX = 3.0`, kernel `max(1 − d/R, 0)`) is consistent with the earlier-session reading of the official page, but that page was not re-fetched today.

## 3. Consequence for the portal error ("Predicted values must be in range [0, 1]")

- The reference's writer (R5–R6) cannot produce a value outside [0, 1].
- Local diagnostic ([`scripts/portal_range_check.py`](../scripts/portal_range_check.py), evidence [`evidence/portal_range_check_20261029.json`](../evidence/portal_range_check_20261029.json)): on all 14 local TIFs in `docs/downloads/` and `registry/`, every finite value is in [0, 1] (0 out-of-range pixels). The NaN-outside files fail a **naive whole-array** test (`np.all((a >= 0) & (a <= 1))` is false when NaN is present) but pass a NaN-aware test. The zeros-outside files pass both.
- Hypothesis H-PORTAL-1: a portal validator that applies a naive whole-array test would reject NaN-outside files. **Not established.** Earlier sessions list NaN-outside files with scores on the leaderboard (user-reported, not receipts), so NaN-outside is not shown to be the cause.
- Hypothesis H-PORTAL-2: the uploaded file had values outside [0, 1], or was a zip or multi-band file. **Not established.** Owner check: run `python scripts/portal_range_check.py <the exact uploaded file>`.

## 4. Irregularities flagged for owner review

1. **Mirror data is third-party.** The training features and labels used by earlier sessions come from GitHub repositories owned by an account that also owns the competing `GEMSDOE*` sites. They are hash-pinned but not organizer-authenticated (see [`registry/karage1_data_manifest.json`](../registry/karage1_data_manifest.json)). The user's sourcing rule requires official or verified data for third-party inputs. **Owner decision needed.**
2. **Two different DrivenData files have one hash.** The manifest pins `labels.tif` and `existing_faults.tif` to the same SHA-256 `7ba308cc…4093` and the same 425,830 bytes. The competition lists them as different files. Unverified: the official listing could not be opened from here.
3. **Filename mismatch.** The official reference reads `data/numeric_features.tif` (R1). The owner brief's Dropbox list names the feature file `gems-geodawn-numerical-features.tif`, and the mirror uses that name too. Either the reference and the brief refer to different files, or the name changed. Unverified.
4. **Holdout is not calibrated to the leaderboard.** The champion control (the 0.2778 file) scores HOLDOUT-DTI 0.00452 (95% CI 0.00382–0.00526, 22,232 withheld positives, evaluator `GEMSDOE32-HIDE-RECOVER-v3.0`) in [`evidence/template_evaluate_holdout_champion_control.json`](../evidence/template_evaluate_holdout_champion_control.json). The leaderboard value is USER-REPORTED 0.2778. Different scales. Do not compare them directly.
5. **Leaderboard figures conflict.** The user's brief gives both "0.4413" and "0.3195 is the highest score right now". The last earlier fetch recorded rank 1 = 0.4544 and 0.3195 at about rank 47 ([README](../README.md)). This session could not re-fetch the leaderboard.
6a. **Dtype conflict.** The brief and the repo's standing rules say "single-band float32 GeoTIFF". The official reference writes float64 (R6a). The reference is not a submission and its portal acceptance is unknown, so this is an irregularity, not a failure. A float64 file may be accepted; a float32 file is what the brief asks for. Owner to confirm with the organizer.
6. **Two "outside" encodings both appear on the leaderboard list** (`-nan` and `-zeros` suffixes). Both are user-reported. Neither has an organizer receipt here.

## 5. Sources (for manual review)

- Official reference repo: <https://github.com/drivendataorg/gems-prize-reference-solution> (commit `aebe92f`)
- Official competition page (not re-fetched today): <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Official data page (login-walled; not reachable from the sandbox): <https://www.drivendata.org/competitions/306/competition-doe-gems/data/>
- Official leaderboard (not reachable today): <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>
- DOE/NLR rules PDF (not reachable today): <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
