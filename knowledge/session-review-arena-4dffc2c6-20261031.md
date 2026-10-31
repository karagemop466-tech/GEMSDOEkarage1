# Session review — `arena/4dffc2c6-gemsdoekarage1` (31 Oct 2026)

## 1. Answer first: can the kp1 file be downloaded and submitted?

**NOT YET. The KP1 file is on HOLD: DO NOT SUBMIT until the owner decides.** File: `docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif` (SHA-256 `30a5fc28…0efbe0ff0d`). It passes the format and the nine-file uniqueness checks (mechanical pass), but the owner-clearance step is not met: (a) the holdout has not shown KP1 beating the current holdout best on a valid instrument; (b) global-registry uniqueness is open; (c) the projection 0.2789 is below the 0.3195 target. The gate was changed from `ok_to_submit: true` to `false` in this session (`evidence/kp1_release_gate.json`, `scripts/kp1_release_gate.py` `OWNER_CLEARANCE = False`) so every page says the same thing. To clear it, the owner sets `OWNER_CLEARANCE = True` in writing and rebuilds.

Download page (held, for review): [docs/kp1/index.html](../docs/kp1/index.html). Other files: all DO NOT SUBMIT.

- Download page with the one-click file and a live hash check: [docs/kp1/index.html](../docs/kp1/index.html)
- Direct download: [GeoTIFF](../docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif) · [zip](../docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.zip)
- Name: `karage1-kp1-ttca-springalter-far-conduit-32000-20261031` · Note (127 chars): "KP1 thermo-tectonic conduit alignment: multi-field edge+scarp+spring+Th/K consensus, >=2px off catalogue, 4px spacing, 32k dots"
- Projected leaderboard value **0.2789 — PROJECTED, not a score**. Organizer-confirmed value: none exists.
- Clearance is an owner decision. This repository did not select or spend a weekly slot.

What this does and does not establish:

| Question | Answer | Evidence |
|---|---|---|
| Format valid on the saved bytes? | Yes (local checks) | §3 |
| Unique vs the nine focus rasters under your stated rules (|rho| ≤ 0.90, ≤ 70 % of dots within 3 px)? | Yes | §2 |
| Would the organizer accept it? | Not proven. No organizer receipt for this file. | §4 |
| Owner clearance met (holdout beat + global uniqueness)? | **No** (open) | §4 |
| Will it top the leaderboard? | Unknown. Projected 0.2789 is close to the 0.2778 user-reported B2 value and far below the reported top values. | §5 |

## 2. Independent uniqueness recheck (this session)

Script: `scripts/verify_uniqueness_independent.py` · receipt: `evidence/uniqueness_recheck_kp1_20261031.json`.

- Max |Spearman| vs the nine registry rasters: **0.0136** (sampled, 2,000,000 footprint pixels, fixed seed) — limit 0.90.
- Max share of kp1 dots within 3 px of any one registry raster: **26.5 %** (GEMSDOE27) — limit 70 %.
- The per-raster rows are in the receipt. The run card's earlier values (0.0076 and 26.5 %) agree with this recheck on the overlap; the Spearman figure differs only because a different pixel sample was used.

Limit of this check: it compares against the nine focus rasters in `registry/` only, not against every GEMSDOE site listed in the prompt. Those other sites are not in the sandbox.

## 3. Format check (saved bytes)

- `scripts/validate_geotiff.py` run with a NaN-outside registry raster as the reference grid: exit 0. Checks: single band, float32, EPSG:32611, 100 m, unrotated, 3730 × 3292, no NaN or infinite values, values in [0, 1] (min 0.0, max 1.0), outside-footprint cells are 0.
- Encoding: kp1 has no NaN anywhere and writes 0 outside the footprint. Measured on the registry rasters: GEMSDOE25/30/32/33/36 contain no NaN at all, while GEMSDOE24/27/28/31 contain 7,111,787 NaN cells each (NaN outside). The user reports GEMSDOE32 B2 (no NaN, all finite) as scored 0.2778, so the portal accepted a no-NaN file.
- **Irregularity:** no organizer `sample_submission.tif` exists in this sandbox (the competition data requires DrivenData login). The grid is matched to the nine registry rasters, which all share EPSG:32611, 100 m, 3730 × 3292. This matches the grid stated in the existing `evidence/kp1_run_card.json`, but it is not checked against the organizer file.
- The user's portal error "Predicted values must be in range [0, 1]" comes from a file we do not have. kp1 has no values outside [0, 1].

## 4. What was not verified (limitations)

- **No organizer receipt** for any file. Scores in this repo are USER-REPORTED or PROJECTED.
- **Holdout (HOLDOUT-DTI) not re-run.** kp1's value is copied from `evidence/kp1_run_card.json`: DTI 0.0764, block-bootstrap 95 % CI [-0.0034, +0.0260], evaluator `gems57-pooled-hide-v2` extended with an SGMC off-catalogue truth, 62,122 withheld positive cells. **The CI includes zero.**
- **The holdout instrument is anti-correlated with known scores.** Its calibration Spearman against the nine known scores is **-1.0** (see `evidence/kp1_exp2_holdout.json`). The run card uses it only to compare kp1 with random dots (+19.3 % off-catalogue coverage at equal dot count). It cannot rank candidates.
- **The repo's 13GEMS lattice gate is non-informative.** Uniform random dots fail it in 200 of 200 draws at every count tested (mean 99.87 %, threshold 70 %; `evidence/lattice_gate_null_check_20261029.json`). kp1 was not gated on it. This is an owner decision, not a blocker here.
- **Leaderboard values conflict across sources** (flag, see §6).

## 5. Can kp1 beat 0.3195 or 0.2778?

Not demonstrated. The projection 0.2789 is only 0.0011 above 0.2778. Reaching 0.3195 would need about 1.31× the champion surface's per-dot accuracy (the card's own multiple, `evidence/kp1_run_card.json` → `metric_analysis`). Nothing in this session tested a new hypothesis, so no new estimate was produced. Budget used: **0 of 3 experiments**.

## 6. Irregularities for owner review

1. **Leaderboard conflict.** The prompt gives "0.4413" as the GEMSDOE high and "0.3195 is the highest score right now". The repo records #1 = 0.4544 and 0.3195 at #50 (30 Oct snapshot) vs #48 (another 31 Oct read). This sandbox cannot reach drivendata.org (outbound allow-list: github.com, codeload, api.github.com, registry.npmjs.org, pypi.org, files.pythonhosted.org), so none of these values was re-read. **Owner: check the live leaderboard page:** https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
2. **Site contradiction (fixed this session).** Before this session, the home page and the executive summary showed "OK TO SUBMIT" for kp1 and "NOT CLEARED / DO NOT SUBMIT · HOLD" for everything else in the same top bar, and the 31 Oct summary answered "No". The status bar and the 31 Oct and H-V31 headings were corrected in `scripts/render_site.py`, and two tests that pinned the old wording were updated. The clearance guard (`FORBIDDEN` phrases) still passes on every page.
3. **Holdout instrument is anti-correlated with known scores** (ρ = -1.0). Not a gate.
4. **Lattice gate is non-informative** (random dots fail it). Not a gate.
5. **Parallel-session records disagree** on H-E1 (TMI Euler) results: one protocol passes the null, another fails it (`README.md`, CURRENT REVIEW block). Left as recorded.
6. **Old pages still say "No approved .tif to download"** in places (`tests/test_site.py` asserts this phrase on `docs/index.html`). It still passes but is now stale relative to kp1. Owner: decide whether to remove it.

## 7. Verification log (commands and results)

| Step | Command | Result |
|---|---|---|
| Repo state | `git status` / `git log` | Clean; branch `arena/4dffc2c6-gemsdoekarage1` at `c43fe5c` (main, PR #111 merged) |
| kp1 hash | `sha256sum docs/downloads/…tif` | `30a5fc28ff060ad38681d9b721024aea5aec3b070f407537dd28354efbe0ff0d` = card value |
| Format | `scripts/validate_geotiff.py … --template registry/GEMSDOE24_…-nan.tif` | exit 0 |
| Uniqueness | `scripts/verify_uniqueness_independent.py` | max |rho| 0.0136; max 3-px 26.5 %; passes literal gate |
| Site build | `scripts/build_site.py` (before edits) | reproduced committed pages byte-for-byte |
| Tests (after edits) | `pytest -q` | 515 passed, 4 skipped |

## 8. Remaining work (next session)

1. Owner: re-read the live DrivenData leaderboard and resolve §6.1; decide the lattice gate (§4) and whether kp1 is the file you want to upload.
2. Obtain the organizer `sample_submission.tif` (requires DrivenData login) to confirm the grid and NaN/zeros encoding for kp1 directly.
3. Re-run the kp1 holdout with a replacement instrument whose calibration is not reversed (§4); until then the holdout cannot rank candidates.
4. Only if a new idea is wanted: pre-register one hypothesis (budget 3 experiments), test it on the holdout, and only then consider a new file.
5. Retire stale "No approved .tif" wording (§6.6).
