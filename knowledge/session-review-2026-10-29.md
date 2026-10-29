# Session review — arena/b0714e6b (2026-10-29)

**Verdict: NEGATIVE / DO NOT SUBMIT.** No new GeoTIFF was generated, no weekly slot was selected or spent, and no leaderboard estimate was produced.
The session's main result is a safety fix: a false "IT IS OK TO DOWNLOAD AND SUBMIT" page was committed on `main`, and it is now withdrawn.

Official-source register for this session: [`knowledge/official-sources-verified-2026-10-29.md`](official-sources-verified-2026-10-29.md) · Run card: [`evidence/session_b0714e6b_run_card.json`](../evidence/session_b0714e6b_run_card.json)

## 1. Why no new TIF was generated (plain answer)

The request asks for a unique, valid, submission-ready GeoTIFF. Four independent blockers make a *cleared* file impossible to issue honestly right now:

1. **No assigned method lane.** The Parallel-Run Protocol says "your lane is the single method paragraph below". No such paragraph is in the prompt, and `registry/template.json` records `method_lane: null`. The protocol forbids inventing one.
2. **The literal 70 % / 3-px duplicate gate cannot be passed by a dotted raster.** The pinned `13GEMSDOE` lattice covers 99.87 % of the footprint within 3 px (`evidence/conduitcrest_lattice_reaudit_20261028.json`, `registry/registry_roles.json`). Session `147b0f11` showed that a 37,654-dot raster has at least 82.34 % overlap even in the best case. This gate is **not** an official rule (see the official-sources register, B1). A decision by the protocol owner is needed; this session did not make it.
3. **No authenticated organizer data.** The DrivenData data tab is login-walled. Training features come from third-party GitHub mirrors, which establish byte identity, not organizer authenticity.
4. **The one file that looked cleared was defective** (section 2). Generating another file would repeat that failure.

A new file generated today would therefore be a research file marked DO NOT SUBMIT, the same status as the 9 existing rasters. That adds no evidence. The next session can generate one once blockers 1–3 are resolved (section 6).

## 2. Defects found and fixed (Pass 1 & 2)

| # | Defect found on `main` | Fix | Evidence |
|---|---|---|---|
| D1 | `docs/executive-summary.html` (committed) displayed a green banner **"CLEARED FOR SUBMISSION · IT IS OK TO DOWNLOAD AND SUBMIT THIS FILE"** for `unique-hyp-kth-therm-mask-20261028-zeros.tif`, with `"verdict": "promote"`, `holdout_DTI 0.1713` and **empty** overlap/correlation objects. No repository evidence supported it. | Rebuilt page from the shared renderer (`scripts/render_site.py`), which says **DO NOT SUBMIT**. Added a regression test that fails if any published page contains the clearance phrases. | `tests/test_no_false_clearance.py` |
| D2 | The same raster and its sidecar cards were in the public download folder with the "promote" card. No saved-byte audit covered it. | Moved (via `git mv`, history kept) to `archive/quarantine/unique-hyp-kth-therm-mask-20261028/` with a `QUARANTINE.md` explaining why. | `archive/quarantine/…/QUARANTINE.md` |
| D3 | The "promote" card came from `scripts/my_unique_experiment2.py`, a private fork of the shared evaluator/writer path that sets the verdict from its own gate. `scripts/my_unique_experiment.py` is the same pattern. | Both scripts now exit 2 with `BLOCKED` before doing anything. | `tests/test_no_false_clearance.py::test_private_fork_experiments_fail_closed` |
| D4 | `scripts/run_karage1_experiments.py` had its quarantine `raise` commented out (`pass # raise RuntimeError(`). It was a syntax error, so the runner failed with `IndentationError` instead of the intended `BLOCKED` message. Two tests failed on `main`. | Restored the `raise`. The runner now prints `BLOCKED` and exits 2. | `tests/test_quarantined_runners.py`, `tests/test_review_release.py` |
| D5 | The test run rewrote the tracked `docs/executive-summary.html`, so the committed page and the builder output disagreed. | Committed the builder output; no further hand edits. | `git diff` on the page |
| D6 | Two historical tests were flaky under the full suite (`test_field_site`, `test_audit`). They passed in isolation and in later full runs. | Not changed. Recorded as an order-dependence irregularity for review. | — |

Full test suite: **first run on the untouched `main` checkout = 8 failed / 349 passed**; later runs of the same tree gave 4 failures (order/state-dependent, see D6); **after fixes = 362 passed, three consecutive full runs** (357 existing + 5 new regression tests). Rasterio 1.4.4 deprecation warnings are unchanged.

## 3. Answer to "why did GEMSDOE32 B2 score 0.2778?" (PhD-level, evidence-limited)

Full analysis: [`knowledge/02_why_gemsdoe32_b2_scored_0.2778.md`](02_why_gemsdoe32_b2_scored_0.2778.md). Points verified this session:

- **Metric (official).** DTI = TP_w / (TP_w + α·FP_w + β·FN_w + ε), α = 0.2, β = 0.8, triangular kernel with R = 300 m ([problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric)). Because β > α, a missed fault costs four times as much as a false positive, so predicted mass is worth keeping in the right place.
- **Masking (official staff).** Pixels on known USGS/INGENIOUS faults are excluded from scoring ([forum post, 2026-09-16](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2)). Dots that sit *on* a known trace earn no credit and no penalty. Dots 1–3 px away still count.
- **Mask lineage (pinned mirrors, measured).** B2 = GEMSDOE25/30 parent (44,090 dots) with 6,436 dots within 2 px of known labels removed, 37,654 remaining, nothing added. This is a support-set identity, not a score.
- **Why thinning *can* help.** Deleting a set of predictions with loss L of true-positive coverage and removal c of false-positive mass raises DTI only if α·T·c > L·(α·F + β·G + ε). That is a conditional inequality, not a demonstrated effect.
- **What is not shown.** No organizer receipt for 0.2778 exists in this repository. The effect of the collar on the hidden labels is untested. The claim that "removing near-catalogue dots raises DTI" is a conjecture in the older repository notes; this session does not adopt it as fact.

**Can a new file beat 0.2778?** Possible in principle, not established. The public #1 score is 0.4544 (verified, §C of the register), so the 0.2778 figure is well below the current top. A new file must be tested by a same-evaluator, same-fold holdout before any slot is used, which is blocked (section 1).

## 4. Official-source corrections to the prompt (flagged for review)

- Top public leaderboard score is **0.4544** (#1), not 0.4413 or 0.3195. **0.3195 is rank #47.**
- None of the nine GEMSDOE scores appears in the visible top 50 (cut-off 0.3167). They remain USER-REPORTED.
- The 70 % / 3-px lattice gate is an internal protocol. The official rules do not state it.
- The official rules require a single GeoTIFF; values in [0, 1]; float32; EPSG:32611; NaN or null outside the bounds. The repository's zero-outside twins do not literally match "null or nan". Review before any future upload.
- Competition closes 2026-12-03 23:59 UTC. Up to 3 submissions per week; one final selection.

## 5. Three passes

1. **Implement and verify.** Read the repo, governance and session history. Reproduced the baseline failures (8 on the first run), traced each to a cause, fixed D1–D5, and verified the fixes with repeated full-suite runs.
2. **Adversarial review.** Looked for other places that could show a false clearance or a private fork. Scanned all HTML and JSON for `OK TO DOWNLOAD`, `CLEARED`, `promote`, `ok_to_submit: true`. Every remaining hit is a negation (`OK TO SUBMIT: NO`), a historical record with `ok_to_submit: false`, or a quoted rule. Found no other cleared file. Also checked the new regression tests fail on the old committed page (the clearance phrase is present there).
3. **Re-check against the request.** Official facts were fetched and checked line by line (register §A–C). Limitations are listed in §6 and register §D.

## 6. Limitations, blockers and next steps (for the next session)

1. **Assign the method lane.** The protocol's "single method paragraph" is missing. The owner must supply it. Do not infer it from older sessions.
2. **Decide the lattice gate.** Either accept that the 70 %/3-px rule blocks all dotted rasters (in which case no dotted file is ever submittable), or replace it with an official-rules-based definition of duplication. This is a protocol-owner decision.
3. **Authenticate organizer data.** A DrivenData login is needed to download the training features, labels and sample submission. Without it, neither the holdout nor the registry can be rebuilt from organizer bytes.
4. **Confirm the zeros/NaN outside-footprint encoding** against the official wording ("null or nan"). Use a NaN-outside file unless there is a reason not to.
5. **Obtain a real submission receipt** for the one candidate you want to test, so that a score can be labeled ORGANIZER-CONFIRMED.
6. **Only then**: run one pre-registered hypothesis (≤ 3 experiments / 2 h), produce a new TIF, run the validator and the duplicate gate, and hand a `promote` result to the separate selector. Otherwise the verdict stays NEGATIVE.

Reproduce:

```sh
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m pytest -q                      # expect 362 passed
python scripts/run_karage1_experiments.py --stage all   # expect BLOCKED, exit 2
python scripts/my_unique_experiment2.py                 # expect BLOCKED, exit 2
```
