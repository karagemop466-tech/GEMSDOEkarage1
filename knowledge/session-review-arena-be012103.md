# Session review — `arena/be012103-gemsdoekarage1` — 29 October 2026

## Decision

**NEGATIVE / DO NOT SUBMIT — no file in this session is cleared for upload.**

No new GeoTIFF was generated. Reason: the sandbox cannot reach the competition data, so no candidate can be built on real features, holdout-tested, or validated against the official grid. A format-valid raster with no geophysical input would be an unscored placeholder; the repository has already retracted that kind of artifact (see `archive/quarantined-20261029/` and PR #42 in the README). No score estimate is made.

## Pass 1 — inspect, fetch, test

| Check | Result | Evidence |
|---|---|---|
| Repo state | Clean tree on `arena/be012103-gemsdoekarage1`, based on `5a6a5fb` (main). | `git status`, `git log` |
| Test suite | **365 passed**, 119 Rasterio/Affine deprecation warnings (software check only, not model performance). | `.venv/bin/python -m pytest -q` (run this session) |
| Competition data tab | **Not reachable.** Login-walled DrivenData page; no credentials in the sandbox. | `curl` returned HTTP 000 (no route) |
| Dropbox links supplied by the user (`example_submission.tif`, `existing_faults.tif`, `gems-geodawn-numerical-features.tif`) | **Not reachable** from the sandbox (HTTP 000). | `curl -L` (this session) |
| GDR/OpenEI submission 1391, NLR rules PDF | **Not reachable** from the sandbox (HTTP 000). | `curl -L` (this session) |
| GitHub reference solution | Reachable. Its README says the data must be downloaded from the GEMS website into `data/`; the repo has only a `.gitkeep`. | `git clone` of `drivendataorg/gems-prize-reference-solution` at commit `aebe92f7c8a990f0e3443451b7a825d9afd6336b` |
| Nine focus-site GitHub Pages | Not reachable by `curl` (HTTP 000). The GEMSDOE32 page was read with the page-fetch tool instead. | see below |

### Leaderboard (fetched 2026-10-29 with the page-fetch tool)

Source: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/

- **#1 xiaofanhu — 0.4544** (34 submissions)
- **#2 cfld__ — 0.3916**
- #3 Batik Shirt Brothers — 0.3911
- #45 tran.thuy.trang — 0.3231; #46 like60986 — 0.3217
- **#47 kpomazi** is listed; the score cell was cut off in my fetch chunk. The prior session recorded **0.3195** at #47 (`evidence/official_source.json` / `knowledge/official-sources-verified-2026-10-29.md`). Not re-verified to the digit here.
- **0.4413** does not appear in the chunks I read (ranks 1–47). Not found on this snapshot.

**Irregularity:** the prompt says "0.4413 is the high score" and "0.3195 is the highest score right now". The live board shows the top score is **0.4544**, and 0.3195 sits near rank #47, not #1.

### GEMSDOE32 page (fetched with the page-fetch tool)

Source: https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html

- The page labels the 0.2778 file `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` as **"0.2778 OWNER-REPORT (owner-provided submission-log claim; no submission-page receipt linking this raster hash to the score is present in this repository)"**.
- The same page says: *"already submitted - do not resubmit (a resubmission spends a slot and adds no information)"*.
- The page's status section says **"NO FILE IS CLEARED FOR SUBMISSION"** and that OK-to-submit requires an assigned method lane, leakage canaries ≤ 0.90, a fold-local holdout win with paired 95% CI > 0, literal uniqueness vs every registry raster, saved-byte validation, and a separate slot selector.

**Implication for the question "why did 0.2778 score highest?":** this session cannot answer it from primary evidence. The 0.2778 value is an owner claim without a receipt. Earlier notes in this repo (`knowledge/02_why_gemsdoe32_b2_scored_0.2778.md`) describe the file as a mask subset of GEMSDOE25 with 6,436 dots removed. That geometry is a measurement; it does not show why the score changed.

## Pass 2 — adversarial review

1. **No fabricated score.** No HOLDOUT-DTI and no competition estimate is produced. The nine-site values in the prompt are USER-REPORTED / UNVERIFIED. A projection is never written as a score.
2. **No unlabeled submission.** The answer to "is it OK to download and submit a TIF from this session?" is **NO**, because none was generated.
3. **No restoration of third-party competition data.** `scripts/restore_data.py` could pull mirror copies from other participants' repositories. I did not run it. Those copies are not organizer-authenticated, their redistribution rights are unclear, and using them as training data would conflict with the rules' original-work requirement (Official Rules Appendix A.5(1), per `knowledge/official-sources-verified-2026-10-29.md`). This is flagged for the owner to decide.
4. **Literal lattice gate.** The 70% / 3-px / |ρ|≤0.90 duplicate gate is an internal protocol, not an official rule (`knowledge/official-sources-verified-2026-10-29.md`, item B1). It still governs release here.
5. **Missing method lane.** `registry/template.json` still has `method_lane: null` and `canonical_template_assignment: null`. The "single method paragraph" from the parallel-run protocol is absent from the prompt. Without it, no lane can be assigned.

## Pass 3 — requirements recheck and handoff

| Requirement | Status this session |
|---|---|
| Executive summary per focus site with a "download this file" answer | Partly already in `README.md` (nine-site table). This session adds the correction that no file is cleared, and the GEMSDOE32 owner-report caveat. |
| Estimated score column | **Not estimable.** No organizer receipt, no holdout, no labeled data. Shown as "not estimable" rather than a number. |
| Unique TIF submission | **Not produced** (no data). |
| Holdout before slot use | **Not run** (no data, no lane). |
| Verify line by line, cite official sources | Done for what is reachable (leaderboard, reference-solution repo, GEMSDOE32 page). Unreachable sources are listed, not assumed. |
| Run card | `evidence/session_be012103_run_card.json` (verdict: negative). |

## What is needed to unblock (manual steps the owner must do)

These cannot be done from the sandbox:

1. **Place the official data into `data/`.** Log in at https://www.drivendata.org/competitions/306/competition-doe-gems/data/ and download the training features, labels, existing faults, and sample submission (plus the DEM link list) into `/home/user/GEMSDOEkarage1/data/`. Hashes are then recorded in the run card. This is the single blocker to real experiments.
2. **Name the assigned method lane.** Paste the method paragraph the parallel-run protocol refers to. Until then, the lane is `null`.
3. **Decide the lattice-gate policy.** The 70%/3-px gate blocks dense-dot rasters; it is an internal rule, not an organizer rule. Decide whether it stays a hard stop.
4. **Confirm the rules text on the submission page.** The official spec says "null or NaN" outside bounds (`knowledge/official-sources-verified-2026-10-29.md` A4). The repo's zero-outside twins do not match that wording. The "Predicted values must be in range [0, 1]" error from the portal is still unexplained in the repo.
5. **Check the live weekly slot count yourself** on the submission page. Three per week is the official rule (A6); the remaining count cannot be seen from here.

## Suggested next session (once 1–2 are done)

- Run the shared holdout (`scripts/evaluate_holdout.py` / `src/gemsk/holdout.py`) with a single-feature leakage canary on each candidate before any ranking.
- Build one candidate in the assigned lane; validate saved bytes (NaN outside footprint, values in [0,1], EPSG:32611, shape/transform identical to the sample).
- Report HOLDOUT-DTI with evaluator version, withheld-positive count, and 95% CI. Stop after three experiments or two hours.
