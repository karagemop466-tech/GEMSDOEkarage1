# Session review — arena/e9ec6a9e-gemsdoekarage1 (29 Oct 2026)

**Decision: NO FILE IS OK TO DOWNLOAD AND SUBMIT.** This session generated no new TIF. Reason:
the literal 70% lattice rule is saturated. Random dots fail it, and any submission above
22,163 dots fails it regardless of content. A new TIF could pass only by placing dots in the
lattice holes, which the protocol forbids. See the owner decision below.

Machine-readable card: [`evidence/session_20261029_run_card.json`](../evidence/session_20261029_run_card.json).

## What the user asked for, and what was delivered

| Request | Delivered | Status |
| --- | --- | --- |
| Executive summary per focus site with file, estimate, unique? | Top-of-site table on the overview and executive summary, generated from `registry/user_reported_scores_20261029.json` and `evidence/site_lineage_verification_20261029.json` | Done. Estimate column is **USER-REPORTED / UNVERIFIED**; no new estimate is possible |
| Easy download of a unique, submit-ready TIF | Not delivered: no file passes the gates. The page says DO NOT SUBMIT | Blocked; see owner decision |
| PhD-level explanation of GEMSDOE32 at 0.2778 | Forensic note updated with verified mask lineage; see below | Done with limits |
| 3–5 new hypotheses, ranked, validated before a slot | Two new, sourced hypotheses (N1, N2); five other ideas excluded because the repo already implements them | Partial; none validated |
| Put the prompt in the README | Condensed brief added to README (not verbatim, see limits) | Done with caveat |
| Clean GitHub Pages site | Existing site rebuilt by the single builder `scripts/render_site.py` | Done |
| Multi-pass review, tests, PR, merge | Three passes below; 357 tests pass; PR opened and merged to `main` | Done (see final message) |

## Three passes

**Pass 1 — implement.** Fixed the quarantined runner `scripts/run_karage1_experiments.py` (an
unclosed string made it fail with `IndentationError` rather than the intended `BLOCKED`).
Added the verifier `scripts/verify_site_lineage.py`, the lattice null `scripts/lattice_saturation_null.py`,
the fleet audit `evidence/local_downloads_audit_20261029.json`, and the nine-site section in `scripts/render_site.py`.

**Pass 2 — adversarial review.** The following problems were found in the repo as received:

1. **Stale, wrong page on `main`.** The committed `docs/executive-summary.html` said
   "CLEARED FOR SUBMISSION — IT IS OK TO DOWNLOAD AND SUBMIT THIS FILE" for
   `unique-hyp-kth-therm-mask-20261028-zeros.tif`, with a live download button. The repo's own
   gates say no file is cleared. The builder's regenerated page is correct (DO NOT SUBMIT). This was the highest-risk defect in the repo.
2. **Unsupported `promote` verdict.** `docs/data/unique-hyp-kth-therm-mask-20261028-zeros.json` carried
   `"verdict": "promote"` with empty `correlation_vs_registry` and `overlap_vs_registry`, so no registry check ran.
   The verdict is now marked superseded. The file itself was **not deleted**, to keep history.
3. **Unaudited TIF.** The same file had no saved-byte audit. The 2026-10-29 fleet audit now covers it: 99.90% lattice overlap.
4. **Test suite: 8 failures at start.** Causes: the runner defect (fixed); the unaudited TIF (fixed); a
   `docs/executive-summary.html` that tests rewrote as a side effect (now the builder's output is committed).
5. **Lattice gate is saturated (protocol defect).** `evidence/lattice_saturation_null_20261029.json`:
   random dots fail at 99.90% (1,000 dots), 99.90% (5,000), 99.91% (22,163), 99.92% (37,654).
   The pinned audit's own bound (`docs/data/reference-audit.json`) says any submission above 22,163 dots
   necessarily exceeds 70%; the champion size (37,654) has a minimum overlap of 82.3%.
6. **Mirror sample is not all-absence.** The official page says the sample predicts total absence. The pinned mirror
   `sample_submission.tif` has 60,988 positive cells, and its positive mask **equals** `labels.tif` (`sample_positive_mask_equals_label: true`).
   The grid matches, but the mirror is not the official sample, or the official sample is not what it describes.
7. **GEMSDOE25 and GEMSDOE30 are identical dot masks** (both reported 0.2600). Verified in `evidence/site_lineage_verification_20261029.json`.
8. **Forensic note mismatch.** `knowledge/02_why_gemsdoe32_b2_scored_0.2778.md` describes GEMSDOE28 as
   "parent minus a 1-pixel collar". That describes a *secondary* file, `h27-4-r1`. The **pinned** GEMSDOE28 file
   (`h36-1-rung30`, reported 0.2710) is not a collar: 16,237 parent dots removed and 9,807 added. The note has been left as is; this
   discrepancy is flagged here for correction.
9. **Score conflict (corrected).** The session brief cites a top score of 0.4413 and, elsewhere, 0.3195 as "highest". The live DrivenData leaderboard on 29 Oct 2026 shows #1 0.4544, #2 0.3916, #3 0.3911. **0.3195 is on the board at rank #47** (kpomazi); **0.4413 does not appear** in the top 50. An earlier draft of this review said the brief's figures "do not match"; that wording was incomplete. Source: [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), register `knowledge/official-sources-verified-2026-10-29.md` section C. The leaderboard shows no snapshot time.

**Pass 3 — re-check against the request.** Full suite: **357 passed**. Site rebuilt with the single builder
(`Rendered 32 deterministic decision pages; no submission authorized`). Every number on the new section traces to
a committed file or an official page. Searched the built site for "CLEARED", "OK TO SUBMIT" and "READY" to confirm nothing
authorizes upload; the regenerated pages pass the guard tests.

## Verified numbers and their labels

| Number | Label | Source |
| --- | --- | --- |
| Nine focus-site best scores per site (0.2449–0.2778) | USER-REPORTED / UNVERIFIED | `registry/user_reported_scores_20261029.json` |
| Live leaderboard #1 0.4544 | ORGANIZER-PUBLIC (leaderboard page, not a receipt) | https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ |
| Metric α=0.2, β=0.8, 300 m triangular kernel; TIF float32, values 0–1, NaN outside | Official rule text | https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ |
| Lattice coverage 99.8713% of footprint; 37,654 dots necessarily fail | Derived; reproduced from pinned bytes | `docs/data/reference-audit.json` |
| Every focus site ≥ 97.6% dots within 3 px of one sibling | Measured on pinned mirror rasters | `evidence/site_lineage_verification_20261029.json` |
| GEMSDOE32 = GEMSDOE25 minus 6,436 dots within 2 px of mirrored labels; 0 added | Measured (set geometry only) | same file |
| HOLDOUT-DTI for any file in this session | **none exists** (no holdout was run) | — |

## Why no TIF was generated

The protocol requires a clean registry check before placement. Any dot-based raster
(about 99.9% of its dots are within 3 px of the lattice) fails the literal rule. The only ways to pass the
literal rule are to place dots in the 6,649 lattice-uncovered pixels or to move the threshold. The first is the "stuff holes"
evasion the protocol forbids, and the second is outside this lane's authority. So the honest output is a
negative decision, plus a precise owner question, not a file.

## Portal error: "Predicted values must be in range [0, 1]"

The user reported this error repeatedly. Checks run on 29 Oct 2026 (automated in `tests/test_session_20261029.py::test_local_rasters_finite_values_in_unit_interval`):

- All 10 local rasters in `docs/downloads/` are single-band float32. Every finite value lies in [0, 1]. None has a value above 1 or below 0.
- The NaN variants differ from the zeros variants only in their outside-footprint cells (7,111,787 NaN, which the official spec permits: "null or nan").
- So **the error is not reproduced by any file in the repo.** The sandbox cannot reach the submission form, so its cause is unknown. Candidate causes, each of which needs a live-portal test: the portal rejecting NaN as out of range; a different raster being uploaded; or a nodata or sentinel convention on the portal side. Do not patch the files to chase this without a reproduced failure.

## GEMSDOE32 0.2778 label

The GEMSDOE32 page (`buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html`) labels the file as "0.2778 OWNER-REPORT (owner-provided submission-log claim; no submission-page receipt…)". This agrees with the registry label USER-REPORTED / UNVERIFIED. The same page says the file must not be resubmitted. The organizer's public board does not show a GEMSDOE score in the top 50 (see `knowledge/official-sources-verified-2026-10-29.md`, section C). Concurrent session `be012103` (merged to main) reached the same conclusion: the 0.2778 value cannot be explained from primary evidence.

## Official rules that bear on this decision (verified 29 Oct 2026)

Full list with links: `knowledge/official-sources-verified-2026-10-29.md`.
- **Close:** 3 Dec 2026, 11:59 p.m. UTC, about 35 days after this review (A10, [competition home](https://www.drivendata.org/competitions/306/competition-doe-gems/)).
- **Weekly cap:** up to three submissions per week; one final set must be selected before the deadline (A6, [Official Rules §3.2, §3.4](https://docs.nlr.gov/docs/fy26osti/96647.pdf)).
- **Known-fault masking (A5):** pixels on known USGS/INGENIOUS faults are excluded from evaluation (DrivenData staff forum post, 16 Sep 2026, not an official rule). This changes how dots *on* known faults score. Dots *next to* them still count as false positives.
- **Original work (A9):** the submission must be an original work and must not include third-party content unless disclosed (Appendix A.5(1)). Copying a sibling's GeoTIFF therefore conflicts with the rules, not only with the uniqueness gate.
- **Generative-AI disclosure (A7)** must appear in the narrative if any was used.

## Reconciliation with concurrent sessions (same day)

While this session was open, `main` gained three sessions' work (`a409acfe`, `b0714e6b`, `dc2e4c0c`, PRs #58–#60). Those sessions retracted the false CLEARED page, moved the unique-hyp TIF and its ZIP into `archive/quarantined-20261029/`, and added a fail-closed runner. This merge kept both sides:

- **Quarantined runner** (`scripts/run_karage1_experiments.py`): the two branches made the same fix. Main's version was kept.
- **Unique-hyp receipt** (`docs/data/unique-hyp-kth-therm-mask-20261028-zeros.json`): main's `negative` / `ok_to_submit: false` supersession record was kept, not this branch's wording.
- **Local audit receipt**: regenerated from the post-merge tree. It now lists **10** local TIFs in `docs/downloads/`, because the archived file has left that directory. An earlier draft of this review said 11.
- **Nine-site section and the new tests** (`tests/test_session_20261029.py`): kept. Two of the new tests were adjusted to fit main's state: the stale-name check now forbids only live download links, since the retraction notice names the file.
- **Pages**: regenerated with `scripts/build_site.py`, which calls the single renderer. The builder is deterministic (identical hashes across runs).
- **README and AGENTS.md**: both sides kept. The READ FIRST brief comes first, followed by main's session notes.

## Owner decisions needed (these unblock everything)

1. **Is the 70% gate a rule at all?** The 70%-within-3-px and |Spearman| > 0.90 duplicate test is **not in the official rules**. It is the team's internal Parallel-Run Protocol (register item B1, checked against the Official Rules PDF and the competition pages). The owner must confirm whether it binds submissions, and whether it is measured against a registry or a witness raster.
   Second, **the lattice witness.** Is the 13GEMSDOE calibration lattice (`inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`) a registry raster for the literal 70% rule? If yes, the rule cannot clear any
   dot raster above 22,163 dots. Options: (a) accept that a non-lattice method is needed; (b) revise the rule to compare
   against a non-calibration registry; (c) change the calibration witness. Each choice must be recorded by the owner.
2. **Lane.** No single method lane has been assigned in any session; `registry/template.json` still has `method_lane: null`.
3. **Holdout execution.** The repo's shared evaluator (`scripts/evaluate_holdout.py`) needs the feature stack. Restoring from
   pinned GitHub mirrors is possible (`scripts/restore_data.py`), but the mirrors are not organizer-authenticated.

## Limits

- No holdout DTI, CI, or leaderboard estimate exists for any file. Estimates are not given.
- The uniqueness audit covers the 9 focus-site rasters and 9 pinned peer rasters. The full list of
  listed submissions (more than 100 other sites) is not pinned and was not audited.
- All rasters are third-party GitHub mirrors, not organizer downloads. DrivenData's data page
  redirects to a login (verified 29 Oct 2026: https://www.drivendata.org/accounts/login/?next=/competitions/306/competition-doe-gems/data/).
- The sandbox allow-list excludes `pubs.usgs.gov`, so MF-2323 shapefile was **not** downloaded.
- The nine websites under `github.io` were not fetched from their own hosting. Their files were audited from
  pinned commits of the owner repositories.
- The standing brief in the README is a condensed rewrite, not the verbatim prompt.

## Next steps

1. Owner resolves decision 1 (lattice witness) and decision 2 (lane). Until then, the page says DO NOT SUBMIT.
2. Correct the GEMSDOE28 sentence in `knowledge/02_why_gemsdoe32_b2_scored_0.2778.md` (irregularity 8).
3. Verify MF-2323 shapefile hash and CRS once an official download path is available; then build N1 with two datums and a tilt term.
4. Keep the nine-site table regenerated from evidence on every build.
