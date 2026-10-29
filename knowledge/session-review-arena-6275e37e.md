# Session review — `arena/6275e37e-gemsdoekarage1` (29 Oct 2026)

**Verdict: NEGATIVE. No file is OK to download and submit.** No new raster was built. Nothing was uploaded, and no weekly slot was used.

Run card: [`evidence/session_6275e37e_run_card.json`](../evidence/session_6275e37e_run_card.json).

## 1. The short answers

| Question | Answer | Evidence class |
|---|---|---|
| Is there a file OK to download and submit? | **No.** The holdout is not run (no authorized official data in the sandbox). The 70% / 3 px lattice rule saturates: random dots fail it too. No assigned method lane. | verified (repo gates) |
| Why did GEMSDOE32 B2 score 0.2778? | Pixel-mask lineage: B2 = GEMSDOE25's 44,090-dot parent with 6,436 dots within 2 px of the mirrored catalogue removed; none added. The metric gives the threshold below for when that removal helps. Whether it helped on the hidden labels is **not established**. | the lineage is measured; the 0.2778 is USER-REPORTED |
| Can we beat 0.2778? | **Not established.** No candidate has a holdout result. The internal holdout does not match the leaderboard scale (champion control 0.00452 vs 0.2778). | unverified |
| What is the rule for a dot to help? | A non-redundant dot improves DTI iff its expected truth credit **k > α · DTI** (α = 0.2). At DTI = 0.2778 the bar is **k > 0.0556**. | **verified algebra** (see §3) |
| Why does the portal say "must be in range [0, 1]"? | Not reproduced. Every local TIF is inside [0, 1]. Some NaN-outside files fail a naive whole-array check; the portal's rule is unknown. | not established |

## 2. Official source check (what was and was not verified today)

- **Verified today:** the official reference repo at pinned commit `aebe92f` (notebook SHA-256 `1a762273…ca`). Its alpha = 0.2 is the false-positive weight and beta = 0.8 the false-negative weight (cell 16, lines 8–9); its writer emits sigmoid values in [0, 1] with no NaN masking (cell 19). Its output buffer is float64 by NumPy default (cell 16, line 37), not float32 as the brief says: flagged. Full table: [`knowledge/official-reference-verification-20261029.md`](official-reference-verification-20261029.md).
- **Not verified today:** the DrivenData problem page, data page, leaderboard, NLR PDF, USGS, and EPSG pages. The sandbox cannot reach them (connection code `000`). Earlier-session statements about them are carried forward and labelled as such.
- **Leaderboard conflict:** the brief gives 0.4413 as the high score and also says 0.3195 is the highest. The last earlier fetch recorded rank 1 at 0.4544 and 0.3195 near rank 47. **Flagged for owner review.**

## 3. Why the 0.2778 result is plausible (mechanism, not a measured effect)

Let T = weighted true-positive credit, F = weighted false-positive mass, G = hidden positive pixels. The repo's metric (`vendor/gems57/metric.py`) gives `DTI = T / (T + αF + β(G − T) + ε)`. Because α + β = 1, this equals `T / (α(T+F) + βG)`.

Adding one non-redundant dot with credit k (so T → T + k and F → F + (1 − k)) changes the denominator by `α·(k + 1 − k) = α`. The new DTI is larger exactly when `k·D > α·T`, which is `k > α·DTI`.

I checked this numerically: 20,000 random cases, 0 mismatches. A regression test now guards it: [`tests/test_marginal_rule.py`](../tests/test_marginal_rule.py).

**Consequence for B2:** removing dots helps only if their average realised credit is below about α·DTI. Near-catalogue dots are the natural candidates for low credit under hidden-fault scoring, but the hidden labels are not available here, so this is a testable prediction, not a finding. The prediction is: *mean credit of the 6,436 removed dots < 0.0556 (at DTI 0.2778)*. This cannot be tested without organizer labels.

**Why thinning alone is not a path to 0.45:** the rule sets a bar on expected credit. It does not add credit. The large gap to the leaderboard leader therefore has to come from better expected-credit calibration (where the hidden faults are), not from removing more dots. This is the same conclusion as the earlier forensic note [`knowledge/02_why_gemsdoe32_b2_scored_0.2778.md`](02_why_gemsdoe32_b2_scored_0.2778.md).

## 4. The unique-TIF requirement

- **Constraint 1 — data.** The competition training data is login-walled. The only restorable copy is a third-party mirror (see §6). Holdout and training need the data. Earlier sessions restored their training inputs from that mirror (see the restore manifest), so their holdout numbers are research evidence, not organizer evidence.
- **Constraint 2 — lane.** The brief has no assigned method paragraph, and the protocol says not to pick one silently. This session did not pick one.
- **Constraint 3 — lattice rule.** The 3 px disks around the registry lattice cover **99.87%** of the 5,167,373-pixel footprint ([`evidence/lattice_saturation_null_20261029.json`](../evidence/lattice_saturation_null_20261029.json)). Random dots with no fault information score 99.9% overlap. The rule therefore blocks every dotted raster, whatever its science. This is an owner decision, not something a new file can fix.
- **Uniqueness by hash** is necessary but not sufficient, per the protocol.

Result: a new file would fail the protocol gates before it could be a candidate. It was not produced, so the page does not offer a download that looks cleared.

## 5. Portal error diagnostic (new tool)

`scripts/portal_range_check.py` reports, for one file: band count, dtype, CRS, shape, NaN and inf counts, finite min/max, out-of-range count, and two range tests. It is a diagnostic only. The 14 local TIFs give:

- Out-of-range finite pixels: **0** in all 14.
- Fail the naive whole-array test: the 4 NaN-outside files (`cda1-nan`, `gpcz-nan`, `bbstep-nan`, `gse-nan`). Pass the NaN-aware test.
- Zeros-outside files pass both tests.

Owner action: run the script on the **exact file that failed upload**. If it reports out-of-range values or more than one band, that is the cause. If it reports only NaN-outside, the portal's rule is the question to ask the organizer. Evidence: [`evidence/portal_range_check_20261029.json`](../evidence/portal_range_check_20261029.json).

## 6. Irregularities flagged for review

1. Third-party mirror used as training data (not organizer-authenticated; sourcing rule requires official data).
2. `labels.tif` and `existing_faults.tif` share one SHA-256 (`7ba308cc…4093`, 425,830 bytes) in the mirror manifest.
3. The reference notebook reads `numeric_features.tif`; the brief's Dropbox list names `gems-geodawn-numerical-features.tif`.
4. Holdout champion control 0.00452 [0.00382, 0.00526] vs leaderboard 0.2778 (USER-REPORTED). Not calibrated.
5. Leaderboard figures conflict (0.4413 / 0.3195 / 0.4544).
6. Portal error not reproduced; cause unknown.
6a. Official reference writes float64 (no cast), while the brief says float32 (verification record, R6a).
7. Two outside encodings (`-nan`, `-zeros`) appear on the list; neither has an organizer receipt.

## 7. Parallel-run protocol status

- **Lane:** none assigned. Not chosen by this session.
- **Experiments:** 0 of 3. No holdout run, because the authorized data is missing.
- **Budget:** well under the 2-hour cap; the session was dominated by source retrieval.
- **Promotion selector:** not invoked. No slot spent.

## 8. Three passes

- **Pass 1 (implement and verify):** wrote `scripts/portal_range_check.py` and tests; ran the diagnostic on 14 local TIFs; read the official reference notebook at its pinned commit; verified the marginal rule numerically.
- **Pass 2 (adversarial review):** found and fixed a crash on missing or corrupt files (now fail closed, with tests); confirmed that NaN-outside files fail the naive test and not the NaN-aware one; confirmed the reference's α/β comment lines before citing them; corrected a filename claim to match the brief's own Dropbox list; re-ran the diagnostic and confirmed identical output.
- **Tests:** `pytest -q` → **384 passed** (373 existing + 11 new). Software checks only.
- **Pass 3 (requirements check):** checked each user question against §1; every number is labelled (verified / USER-REPORTED / holdout / not established); no raster or score was produced; the note in the run card is 107 characters (limit 140).

## 9. What is needed to move forward (access and decisions)

**Access:** DrivenData data page (login), the competition leaderboard and problem page, the NLR PDF, the USGS GeoDAWN/INGENIOUS downloads, and the EPSG page. None are reachable from the sandbox. The GitHub REST quota was exhausted during this session (both `curl` and authenticated `gh api` returned rate-limit errors), but a plain `git clone` from `github.com` worked.

**Owner decisions:**
1. Use the third-party mirror for research-only holdouts, or have the owner download the DrivenData files from the [official data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) into `data/`. Note: `scripts/download_competition_data.sh` restores third-party mirrors only; it does not download from DrivenData.
2. Does the 70% / 3 px lattice rule bind submissions? It is not in the official rules and saturates on any dotted raster.
3. Assign a method lane (the brief has none).
4. Which file failed the portal, and what does `portal_range_check.py` report on it?

**Next session (if decisions arrive):** restore or place the authorised data (`scripts/restore_karage1_data.py` for the mirror, or the owner's official download); run the shared evaluator on the champion control to confirm the 0.00452 figure; then test one candidate from [`docs/research/hypotheses-20261029.md`](../docs/research/hypotheses-20261029.md) against it, with the leakage canary and the marginal rule as the first check.
