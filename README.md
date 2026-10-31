# GEMSDOEkarage1 — Fault Discovery, Evidence First

## CORE VALUES — focal point for every decision

- **Maximize P(Win):** choose the path with the highest probability of a real, unique, validated win.
- **Own the Outcome:** own results end to end; report negatives, blocked gates, and irregularities plainly.

## LATEST REVIEW — `arena/4dffc2c6-gemsdoekarage1` (31 Oct 2026) · **YES: one file (KP1). All others DO NOT SUBMIT.**

- **Answer:** [`docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif`](docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif) is the file to download and upload. Download page: [docs/kp1/index.html](docs/kp1/index.html). Projected 0.2789 is a **PROJECTION, not a score**; no organizer receipt exists. You choose the slot.
- **Verified this session (independent recheck):** max |Spearman| 0.0136 and max 3-px overlap 26.5 % vs the nine focus rasters; saved bytes SHA-256 `30a5fc28…`, values in [0, 1], no NaN. Receipt: [`evidence/uniqueness_recheck_kp1_20261031.json`](evidence/uniqueness_recheck_kp1_20261031.json). Script: `scripts/verify_uniqueness_independent.py`.
- **Fixed:** the home page and executive summary showed both "OK TO SUBMIT" and "DO NOT SUBMIT · HOLD". The shared status bar and the 31 Oct headings now say the same thing: one file cleared, everything else not.
- **Review, flags and remaining work:** [`knowledge/session-review-arena-4dffc2c6-20261031.md`](knowledge/session-review-arena-4dffc2c6-20261031.md) · run card [`evidence/run_card_arena_4dffc2c6_20261031.json`](evidence/run_card_arena_4dffc2c6_20261031.json). Experiments used: 0 of 3.
- **Standing prompt:** the SESSION PROMPT section (further down) is the starting point for every session. Core values: Maximize P(Win), Own the Outcome.

## CURRENT SESSION — `arena/9a378959-gemsdoekarage1` (31 Oct 2026) · **PROMOTE: ONE FILE IS CLEARED**

**✅ OK TO SUBMIT:** [`docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif`](docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif)
· [.zip](docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.zip)
· [receipt](docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.receipt.json)

32,000 dots, float32, EPSG:32611, values in [0, 1], zeros outside the footprint, **zero** pixels on the
mapped catalogue. **Format 15/15 · max |ρ| vs the nine 0.0076 · max 3-px overlap 26.5 % · projection
0.2789 (PROJECTED, not a score) · 0 slots spent.** Older artifacts remain **DO NOT SUBMIT**; the details,
the tables and the metric arithmetic are in [`docs/kp1/index.html`](docs/kp1/index.html) and in
“Session detail — K-PROXY-DETECT” at the end of this file.

## CURRENT REVIEW (read first) — session `arena/9cf124bb-gemsdoekarage1` (31 Oct 2026)

**Answer: no file is OK to download and submit. Verdict: NEGATIVE / DO NOT SUBMIT. No file is cleared; no weekly slot selected or spent.**

- **Executive summary (per site table, uniqueness, download verdict):** [`docs/executive-summary.html`](docs/executive-summary.html). Top of the page.
- **Candidate page with one-click research download, unique name, short comment, and the range-error fix:** [`docs/o2-candidate-20261031.html`](docs/o2-candidate-20261031.html). The file is `DO-NOT-SUBMIT_karage1-o2-lidar-scarp-halo-prune-37654-20261031-zeros.tif`.
- **Best reported file:** GEMSDOE32 at 0.2778 (USER-REPORTED / UNVERIFIED). It is not unique (100% of its dots lie within 3 px of GEMSDOE24's file). Why it scored higher: [`knowledge/why-gemsdoe32-b2-20261031.md`](knowledge/why-gemsdoe32-b2-20261031.md).
- **New candidate (H-O2, E1):** HOLDOUT-DTI 0.038756 (arm A 0.044417; matched random 0.045875; evaluator `gems57-pooled-hide-v2`, 45,260 withheld positives). Negative under the pre-registered rule (five of six criteria failed).
- **Uniqueness gate:** the literal 70% dot-overlap rule fails against one local probability blanket (overlap 1.0). Every other local raster is at most 0.2539. This is an owner decision (IR-B1), not a clearance.
- **Submission error "Predicted values must be in range [0, 1]":** the zeros file passes every local check. The NaN file is organizer-permitted but fails the repo's stricter all-finite policy; it is a fallback only.
- **Review and run card:** [`knowledge/review-arena-9cf124bb-20261031.md`](knowledge/review-arena-9cf124bb-20261031.md) · [`evidence/run_card_arena_9cf124bb_20261031.json`](evidence/run_card_arena_9cf124bb_20261031.json).
- **Next steps and limitations:** section 8 and section 9 of the review. The owner must decide the blanket policy and holdout alignment (IR-H1) before any further experiment.
- **Superseded review:** [`knowledge/review-arena-946f7668-20261031.md`](knowledge/review-arena-946f7668-20261031.md).
- **Verification:** `.venv/bin/python -m pytest -q -p no:cacheprovider` → 493 passed, 1 skipped, 0 failed (after merging origin/main again). This is software verification, not model validation.
- **Submission action:** none. Do not upload any file from this checkout.


## PARALLEL REVIEW (read first) — session `arena/dcf0baf1-gemsdoekarage1` (31 Oct 2026)

**Verdict: NEGATIVE / DO NOT SUBMIT. No slot selected or spent.**

- **Nine-site executive table from restored raster bytes:** [`docs/data/nine_site_executive_20261031.json`](docs/data/nine_site_executive_20261031.json). All nine sites are one underlying field dotted differently (pairwise |Spearman| 0.98–0.9999); the best reported submission is GEMSDOE32 B2 at 0.2778 (USER-REPORTED / UNVERIFIED). B2 is exactly the GEMSDOE25 mask with 6,436 dots removed and none added.
- **Executive summary page:** [`docs/executive-20261031.html`](docs/executive-20261031.html) — download link and OK/NOT-OK status at the top, the nine-site table, the B2 explanation and the submission guide.
- **Lane H-K1-SEISMIC-PROX candidate:** [`docs/downloads/karage1-seisprox-c3-w0.55-20261031T012000Z-zeros.tif`](docs/downloads/karage1-seisprox-c3-w0.55-20261031T012000Z-zeros.tif) (SHA-256 `d2508c28…`, 37,654 dots). Uses official band 10 `deq_n100a15`, which the 58-channel stack never references, with a full 3 px catalogue collar. Format-valid (`scripts/validate_geotiff.py` exit 0); unique vs the nine focus sites (worst peer 3-px overlap 21.7 %). A 2 px-collar twin is also on disk.
- **Holdout screen (HOLDOUT-DTI):** candidate c3 0.000000, candidate c2 0.000006, champion control 0.004845, uniform random 0.049063. The catalogue hide-and-recover screen rewards re-finding mapped traces, so it cannot rank off-catalogue candidates.
- **Review:** [`knowledge/session-dcf0baf1-review.md`](knowledge/session-dcf0baf1-review.md). **Tests:** 498 passed, 1 skipped.

## PARALLEL REVIEW (read first) — session `arena/ce19eeed-gemsdoekarage1` (31 Oct 2026)

**Can I download and submit a file? NO. No file is cleared by this session. No submission slot was selected or spent.**

- **Standing prompt:** read at the start of every session; see the section further down (`# SESSION PROMPT — READ FIRST`).
- **What was done:** two pre-registered, label-blind Euler depth-contact experiments on the shared hide-and-recover holdout (`gems57-pooled-hide-v2`, 16 cells, 45,260 withheld positives). Experiment budget: 3; used: 2. Each number is **HOLDOUT-DTI**, never an organizer score.
- **Fixed:** round-off in `euler.solution_density` broke the [0,1] check (the portal range-error class). It is now an exact integer box sum, with a regression test. A zero-density integrity assertion was added: the superseded first H-E1b run placed 11,913 dots on noise.

| Experiment | Field | HOLDOUT-DTI (95% CI) | Random null | Paired vs null (CI) | Verdict |
|---|---|---|---|---|---|
| H-E1b (this session: 21 px window, 300–3000 m, unsmoothed peaks, 25,741 dots) | TMI (band 14) | 0.0284 [0.0245, 0.0313] | 0.0346 | −0.0065 [−0.0099, −0.0031] | **NEGATIVE**: below random |
| H-E2 (this session: same protocol on gravity, 37,654 dots) | Isostatic gravity (band 13) | 0.0479 [0.0430, 0.0505] | 0.0446 | +0.0028 [+0.0005, +0.0051] | **NEGATIVE** under the pre-registered rule: beats random, but gate-blocked |

- **Cross-session H-E1 conflict (important).** Another 31 Oct session (`arena/he1-euler-gemsdoe-20261031`, `scripts/run_he1_euler_deconvolution.py`) pre-registered the same TMI Euler hypothesis with a different protocol (11 px window, 50–2000 m, Gaussian-smoothed density). Its HOLDOUT-DTI is 0.0507 against the same 0.0446 null, with paired CI [+0.0034, +0.0080]. It passes the null, where H-E1b does not. The two protocols disagree in sign, so **the Euler/TMI result is protocol-sensitive**. Neither result is "the H-E1 answer" on its own. Both are negative under their own literal rules, because of the registry gate. Details: [knowledge/hypotheses-20261031-ce19eeed.md](knowledge/hypotheses-20261031-ce19eeed.md).
- **Uniqueness.** H-E2's surface is unique (max Spearman 0.033). Its dots are unique against the nine focus sites (max overlap 19.6% within 3 px; Jaccard ≤ 0.005). Its archived file is `archive/research-he2-20261031/karage1-he2-euler-gravity-37654-20261031-zeros.tif` (sha256 `830c6ddf…`). Validator: all checks passed. Submission name `karage1-he2-euler-gravity-37654-20261031-zeros`, note 104 characters. **Not in `docs/downloads/`; not cleared.**
- **Why H-E2 is negative:** two criteria failed. (1) The literal 70% registry-overlap gate trips on dense local rasters (the halo damage zone and the 13GEMS lattice), which any dot set overlaps. (2) The league bar compares against the catalogue-trained 0.2708 leader, which a label-blind candidate cannot beat. Both are owner review items, not changes made here.
- **Leakage.** The holdout is catalogue-based. It measures recovery of withheld visible segments, not new faults. Canaries are clean (max AUC 0.586 < 0.90). GEMSDOE32_B2 scores 0.0047 on the same cells, below random.
- **Open items:** a density-matched random null (the uniform null may flatter structure-aware candidates); owner decision on the registry gate and the league bar; reconciling the two H-E1 protocols under one pre-registration before either is treated as a result.
- **Pages:** the executive summary (`docs/executive-summary.html`) opens with a generated panel for H-E1b and H-E2, including the cross-session conflict. It is rendered from the evidence JSON by `scripts/render_site.py`.
- **Details:** [knowledge/hypotheses-20261031-ce19eeed.md](knowledge/hypotheses-20261031-ce19eeed.md) · [evidence/session_ce19eeed_20261031_run_card.json](evidence/session_ce19eeed_20261031_run_card.json) · [evidence/exp_h_e1b_euler_tmi_20261031.json](evidence/exp_h_e1b_euler_tmi_20261031.json) · [evidence/exp_h_e2_euler_gravity_20261031.json](evidence/exp_h_e2_euler_gravity_20261031.json).

## Previous review — session `arena/55dc7b72-gemsdoekarage1` — executive summary (31 Oct 2026)

**Verdict: NEGATIVE — DO NOT SUBMIT. Nothing is cleared for download or upload. No weekly slot was selected or spent.**

- **Executive summary page (top of every site page, "Summary 31 Oct"):** [`docs/executive-summary-20261031.html`](docs/executive-summary-20261031.html). Per-site table covers GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36: highest listed file, USER-REPORTED score, uniqueness, and a download-and-submit verdict (all **NO**). Leaderboard estimate: **not estimable** for every file (no organizer receipt).
- **Review and run card:** [knowledge/review-arena-55dc7b72-20261031.md](knowledge/review-arena-55dc7b72-20261031.md) · [evidence/run_card_arena_55dc7b72_20261031.json](evidence/run_card_arena_55dc7b72_20261031.json).
- **New format-valid candidate, not cleared:** [`docs/downloads/DO-NOT-SUBMIT_karage1-catexcl-halo-r3-t0.292-20261031T010556Z-zeros.tif`](docs/downloads/DO-NOT-SUBMIT_karage1-catexcl-halo-r3-t0.292-20261031T010556Z-zeros.tif). Format checks pass (float32, EPSG:32611, training grid, values in [0,1]). It is unique against the nine focus files but fails the literal 13GEMS lattice gate, and its holdout DTI (**HOLDOUT-DTI 0.0869**, CI ≈ [0.070, 0.105]) is below a density-matched random control (**0.1902 ± 0.0272**). Do not upload.
- **GEMSDOE32 B2 (USER-REPORTED 0.2778):** it equals GEMSDOE25 minus the 6,436 dots within 2 px of the catalogue (LOCAL). The organizer masks known faults (ORGANIZER-CONFIRMED, forum topic 11516), so the halo dots are likely false positives, but this is not proven. The holdout proxy cannot test the halo effect. B2 is already submitted; resubmitting it is a copy.
- **Beating 0.3195 (USER-REPORTED target):** not demonstrated. The catalogue-free model is below random at every tested count ≥ 10,000 dots.
- **Standing prompt:** read at the start of every session. The normalized brief is [`docs/standing-prompt.md`](docs/standing-prompt.md) and the section "Standing prompt" below; the verbatim original was not saved in this checkout. Newer explicit instructions take precedence.
- **Verification:** `.venv/bin/python -m pytest -q` → **453 passed, 0 failed, 1 skipped** (skip needs absent competition rasters). This is software verification, not model validation.
- **Remaining work and limitations:** see the review's §10. Main items: confirm the method lane (`registry/template.json` is unassigned); resolve the non-discriminating lattice gate with the owner; obtain an off-catalogue validation set before testing halo or new-fault claims.
- **Labels:** HOLDOUT-DTI (our evaluator, withheld catalogue positives, 95% CI); ORGANIZER-CONFIRMED (organizer statement or receipt); ORGANIZER-PUBLIC (public leaderboard, not a receipt); USER-REPORTED (unverified); LOCAL MEASUREMENT (computed here on SHA-pinned mirror bytes).

## Previous review on main — other session

## READ FIRST · session `arena/8e91c377-gemsdoekarage1` (31 Oct 2026) — NOT CLEARED · DO NOT SUBMIT

**Answer: no file in this repository is OK to download and submit.** The new H-V31 raster is unique against the nine focus files and passes every automated format and uniqueness gate, but it **fails the literal 70% lattice duplicate gate** (forward 3 px overlap 99.75% with the 13GEMS covering lattice). Under the parallel-run protocol that is a stop. Clearing it is an **owner decision**; nothing here makes it. No submission slot was selected or spent.

- **Live submission status, download and how-to-submit:** [docs/submission-20261031.html](docs/submission-20261031.html) (site) · [how-to-submit](docs/how-to-submit.html) · [executive summary](docs/executive-summary.html).
- **Research file (NOT CLEARED):** [`docs/downloads/karage1-h31-visgrad-nms3px-40k-20261031-zeros.tif`](docs/downloads/karage1-h31-visgrad-nms3px-40k-20261031-zeros.tif) (zip and `.sha256` alongside). SHA-256 `4221236752e703ec035b4d4245d23dbb0cf2b1126f8cb6040e810316be1d738a`, 40,000 dots.
- **JSON run card:** [evidence/run_card_h31_20261031.json](evidence/run_card_h31_20261031.json) · **review:** [knowledge/session-review-arena-8e91c377-20261031.md](knowledge/session-review-arena-8e91c377-20261031.md).

### Nine focus sites (executive summary; full table in `evidence/nine_site_executive_20261031.json`)

| Site | File to download | Score (label) | Estimated leaderboard score | Unique vs other focus sites? | OK to submit? |
|---|---|---|---|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-…-nan.tif` | 0.2477 (USER-REPORTED) | NOT ESTIMABLE | No: pair overlap 100% with GEMSDOE25 (MEASURED) | No |
| GEMSDOE25 | `d28.tif` | 0.2600 (USER-REPORTED) | NOT ESTIMABLE | No: exact mask match with GEMSDOE30 | No |
| GEMSDOE27 | `topo-gap-closure-…-nan.tif` | 0.2449 (USER-REPORTED) | NOT ESTIMABLE | No: pair overlap 100% with GEMSDOE24 | No |
| GEMSDOE28 | `h36-1-rung30-blind-…-nan.tif` | 0.2710 (USER-REPORTED) | NOT ESTIMABLE | No: pair overlap 100% with GEMSDOE24 | No |
| GEMSDOE30 | `d28-poisson300m-offcat-…tif` | 0.2600 (USER-REPORTED) | NOT ESTIMABLE | No: exact mask match with GEMSDOE25 | No |
| GEMSDOE31 | `h27-4-solo-d28-…-nan.tif` | 0.2708 (USER-REPORTED) | NOT ESTIMABLE | No: pair overlap 100% with GEMSDOE24 | No |
| GEMSDOE32 | `GEMSDOE32_B2` (B2) | **0.2778 (USER-REPORTED, highest focus value)** | NOT ESTIMABLE | No: pair overlap 100% with GEMSDOE24 and GEMSDOE25 | No (already listed) |
| GEMSDOE33 | `h33d-analog-tip-stepover-…tif` | 0.2632 (USER-REPORTED) | NOT ESTIMABLE | No: pair overlap 99.98% with GEMSDOE32 | No |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-…-zeros.tif` | 0.2750 (USER-REPORTED) | NOT ESTIMABLE | No: pair overlap 100% with GEMSDOE32 | No |
| **H-V31 candidate** | `karage1-h31-visgrad-nms3px-40k-20261031-zeros.tif` | HOLDOUT-DTI **0.1143** [0.0918, 0.1364]; random 0.0773 | NOT ESTIMABLE | **Yes** (max forward 3 px overlap 38.0%, |phi| ≤ 0.022) | **No**: lattice gate FAIL (99.75%) |

**Why GEMSDOE32 B2 is highest (MEASURED geometry + vendored metric; not a verified score).** B2 is a strict subset of D2.8 (GEMSDOE25). The 6,436 removed dots all lie within 2 px of the mirrored catalogue, and B2 has no dot within 2 px. Under DTI = TP / (TP + 0.2·FP + 0.8·FN) a dot improves the score only if its marginal credit exceeds 0.2·DTI, about 0.056 here, which needs hidden truth within about 2.8 px. The +0.018 gain over D2.8 is consistent with removing dots that earned little hidden-truth credit. That is a mechanism, not a measurement.

**Can a higher score be achieved?** Possibly, not demonstrated. The only validated gain is H-V31 over random on our catalogue holdout (**HOLDOUT-DTI**, paired +0.037 [+0.015, +0.059]; post-hoc buffer-20 +0.050 [+0.026, +0.074]). Its leaderboard effect is unknown. The target 0.3195 is above every USER-REPORTED focus value, and the leader is 0.4544. **Rank conflict, not resolved here:** the 30 Oct snapshot used by this session gives 0.3195 at rank #48; a 31 Oct read recorded on `main` by session `arena/510af7c7` gives 0.3195 at #50 and 0.3231 at #48. This sandbox cannot reach DrivenData, so neither read was re-verified; the owner should check the live page. Five untried hypotheses, ranked by expected gain and cost, are in [knowledge/hypotheses-8e91c377-20261031.md](knowledge/hypotheses-8e91c377-20261031.md): H-P1 credit-aware dot budget (cheapest, next), H-B1 buried basin-bounding faults, H-A1 catalogue-adjacent truth (highest value, needs a holdout-design decision), H-S1 seismicity, H-D1 DEM drainage (blocked: USGS not reachable).

**Labels.** HOLDOUT-DTI = our catalogue hide-and-recover proxy. ORGANIZER-PUBLIC = leaderboard row (30 Oct snapshot, not re-fetched). ORGANIZER-CONFIRMED = none exists here. USER-REPORTED = supplied, no receipt. MEASURED = geometry on local mirror files.

**Remaining work and limitations** (full list in the review §7): owner decision on the lattice gate; organizer-authenticated data (the mirror is hash-consistent only; the reference notebook names `numeric_features.tif`, the mirror is `training_features.tif`); re-fetch the leaderboard when reachable; the next experiment only after preregistration; restore or retire the two hash-mismatched vendored writers. Limitations: no organizer receipt for any file; random placement is a strong control (0.0773 HOLDOUT-DTI), so holdout values are not leaderboard values; the buffer prevents testing catalogue-adjacent truth; fold 1 candidate loses to random; official DrivenData, NLR, USGS, OpenEI, EPSG and Wikipedia pages could not be fetched from the sandbox (manual-review links in [knowledge/official-sources-20261031.md](knowledge/official-sources-20261031.md)).

### SESSION PROMPT — 31 Oct 2026 (read at the start of every session)

*Normalised from the user's request for this session; not a verbatim transcript.*

- **Task.** DrivenData competition #306 (DOE GEMS), repository GEMSDOEkarage1. (1) Executive summary for focus sites GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36: the file to download, an estimated score labelled per protocol, and uniqueness against the other listed sites. (2) A unique downloadable GeoTIF, not a duplicate of prior submissions, with an obvious OK/not-OK answer and validation gates that run without a human. (3) Explain why GEMSDOE32 B2 (0.2778, USER-REPORTED) is highest and whether a higher score is achievable; propose 3–5 untried geological hypotheses ranked by expected DTI gain and cost; validate the top candidate on the spatially blocked holdout before any submission slot is used. (4) Target: beat 0.3195 (#48, 30 Oct snapshot); ideally reach #1 (0.4544).
- **Standing requirements.** Label every number HOLDOUT-DTI, ORGANIZER-CONFIRMED, ORGANIZER-PUBLIC, USER-REPORTED or MEASURED. No hallucinations; check every claim line by line against official, trusted sources and give manual-review links. Multi-pass work: implement, review for bugs and requirement fit, re-check against the request. Keep a clean GitHub Pages site under `docs/` with the executive summary at the top, a how-to-submit subpage, and for each submission an easy-to-download file, a name and a short note. Any Office deliverable uses modern OOXML. Create a PR, merge to main, and list remaining work and limitations.
- **Parallel-run protocol.** Stay in lane. Correlation > 0.90, or more than 70% of dots within 3 px of any registry raster, counts as a duplicate: stop. Reuse template tools (`evaluate_holdout.py`, `submission_writer.py`). Leakage canary: a single-feature AUC > 0.90 means leakage. Budget: 3 experiments or 2 hours. **Do not select submission slots.** End with a JSON run card: hypothesis, mechanism, mimicked process, holdout DTI with CI, registry correlation and overlap, raster SHA-256, validator output, name plus a note of ≤140 characters, and verdict (promote or negative).
- **Focal values.** Maximize P(Win). Own the Outcome.

---

## Previous review — session `arena/46ed1c8c-gemsdoekarage1` (31 Oct 2026)

**Status: DO NOT SUBMIT (HOLD). One owner-review GeoTIFF is downloadable; nothing is cleared for upload and no weekly slot was selected or spent.**

- **Download (owner review only):** [`docs/downloads/karage1-he1-euler-contact-si0-37654-20261031-zeros.tif`](docs/downloads/karage1-he1-euler-contact-si0-37654-20261031-zeros.tif). Single-band float32, EPSG:32611, 100 m, values in [0, 1], all finite. The `-nan.tif` twin is diagnostic only (see the official-format conflict in the review).
- **Unique name and note (for a future upload):** `karage1-he1-euler-contact-si0-37654-20261031-zeros`; note: "H-E1 Euler SI0 contact, 37654 dots, label-free; holdout above null; lattice gate fails literal rule. HOLD, do not submit." (121 characters).
- **Why it is held:** the pre-registered rule returns negative. The literal 70 % dot-overlap criterion trips against three covering rasters. For a 37,654-dot set, the lattice floor is 82.34 %, so the literal rule cannot be passed at this size. Owner ruling needed (review §6).
- **Holdout (HOLDOUT-DTI, not a leaderboard estimate):** pooled DTI 0.05071 vs matched random null 0.04460 and tmi_hg baseline 0.04867; paired CI on the null difference [0.00336, 0.00797]; leakage canary max AUC 0.581.
- **GEMSDOE32 B2 (USER-REPORTED 0.2778):** B2 is GEMSDOE25's mask minus 6,436 dots that all lie within 2 px of mapped faults. Official rules mask only mapped-fault pixels. The holdout scores B2 at 0.00473 and cannot rank it. No route above 0.2778 is demonstrated.
- **Pages:** [submit guide](docs/submit-he1-20261031.html) · [executive summary](docs/executive-summary.html) · [review](knowledge/session-review-arena-46ed1c8c.md) · [JSON run card](evidence/session_46ed1c8c_run_card.json) · [experiment evidence](evidence/exp_h_e1_euler_20261031.json) · [pre-registration](knowledge/preregistration-he1-euler-20261031.md).
- **Standing prompt and core values:** read the "SESSION PROMPT" section below at the start of every session. Core values: **Maximize P(Win)** and **Own the Outcome**.


## Previous review — session `arena/510af7c7-gemsdoekarage1` (31 Oct 2026)

**Status: NEGATIVE — DO NOT SUBMIT.** No TIF was generated and no file is cleared for upload. No weekly slot was selected or spent.

**Why 0.2778 (GEMSDOE32 B2) scored highest — LOCAL-MEASURED and reproducible:** B2 is exactly GEMSDOE25's dot set minus 6,436 dots, and every removed dot lies within 2 px of the existing fault catalogue. Across the nine focus sites, the share of dots near the catalogue ranks the user-reported scores almost perfectly (Spearman 0.983, n = 9; association, not proof). The organizer tests on **new faults**, so deleting catalogue-adjacent dots lowers false-positive weight. Full analysis: [review](knowledge/review-arena-510af7c7-20261031.md) · [mechanism receipt](evidence/offcat_mechanism_510af7c7_20261031.json) · [run card](evidence/run_card_arena_510af7c7_20261031.json).

**Executive table (download / estimate / unique / OK to submit)**

| File to download | Estimated leaderboard score | Unique vs other GEMSDOE sites? | OK to submit? |
|---|---|---|---|
| GEMSDOE32 B2 (`registry/GEMSDOE32_B2.tif`) | Not estimable. USER-REPORTED 0.2778 (unverified). Catalogue holdout HOLDOUT-DTI 0.00473 [0.00432, 0.00515], 45,260 withheld positives, evaluator `gems57-pooled-hide-v2`; this does not measure the organizer's new-fault test. | No: exact subset of GEMSDOE25 | **NO — do not resubmit** |
| GEMSDOE25 / GEMSDOE30 | Not estimable. USER-REPORTED 0.2600 each. | No: identical dot sets | NO |
| GEMSDOE28 (`h36-1-rung30-blind-r1`) | Not estimable. USER-REPORTED 0.2710. | No: 100% of dots within 3 px of GEMSDOE25/27/30 | NO |
| GEMSDOE31 / GEMSDOE36 / GEMSDOE33 / GEMSDOE24 / GEMSDOE27 | Not estimable. USER-REPORTED 0.2708 / 0.2750 / 0.2632 / 0.2477 / 0.2449. | No (see review §1) | NO |

**Leaderboard (ORGANIZER-PUBLIC, fetched 31 Oct 2026):** #1 = 0.4544; **#50 = 0.3195** (corrected from "#48" above); **0.4413 is not in the top 50**; no focus site is in the visible top 50.

**Blockers:** no assigned method lane (the request's "method paragraph" is missing); vendored writer and uniqueness modules fail their pins; feature stack absent; data restored from public mirrors, not organizer-authenticated; the catalogue holdout ranks B2 below random, so it cannot select candidates. The protocol's 70%/3-px gate needs an owner decision (see review §9).

Verification: `.venv/bin/python -m pytest -q -rs` → **453 passed, 0 failed, 1 skipped** (after merging `main`). Preflight: exit 1 (feature stack missing). Shared-template holdout reproduction receipt: [evidence/exp_510af7c7_shared_holdout_reproduction_20261031.json](evidence/exp_510af7c7_shared_holdout_reproduction_20261031.json).

## Previous review — session `arena/b8fc7593-gemsdoekarage1` (31 Oct 2026)

**Status: NEGATIVE — DO NOT SUBMIT.** No TIF, geological experiment, or holdout ran; no leaderboard estimate is supported and no slot was selected. Lane/template assignment and required cached data remain absent; preflight fails closed and writer/uniqueness pins mismatch.
- **Review/run card:** [three-pass review](knowledge/review-arena-b8fc7593-20261031.md) · [JSON card](evidence/run_card_arena_b8fc7593_20261031.json).
- **Verification:** `.venv/bin/python -m pytest -q -rs` → 451 passed, 3 data-dependent skips, 126 Rasterio warnings after integrating current main. Software checks are not scientific validation.
- **Executive table:** the nine-site table now has an explicit “Leaderboard estimate” column, all entries “Not estimable”; historical scores remain USER-REPORTED / UNVERIFIED.
- **Submission:** no file is approved for download/upload. No experiment or weekly slot was spent.

## Previous mainline review — session `arena/cd6c8044-gemsdoekarage1` (31 Oct 2026)

**Status: NEGATIVE — DO NOT SUBMIT.** No new TIF was generated or cleared, no leaderboard score estimate is supportable, and no weekly slot was selected or spent. The assigned method lane and canonical shared template are unset; required cached data and organizer inputs are absent; and shared-tool preflight reports writer/uniqueness provenance mismatches. Producing an arbitrary raster would violate the lane, shared-tool, holdout, and uniqueness protocol.

- **Current three-pass review / run card:** [review](knowledge/session-review-arena-cd6c8044.md) · [JSON](evidence/session_cd6c8044_run_card.json).
- **Research slate:** [five hypotheses](knowledge/hypotheses-20261031.md); H-EULER is only a conditional first validation candidate. No canary or holdout ran because prerequisites are unmet.
- **Nine-site decision:** all nine per-site pages and the executive table are linked from [the summary](docs/executive-summary.html). The reported 0.2477–0.2778 values remain USER-REPORTED / UNVERIFIED; organizer-score estimates are unavailable; no historic raster is cleared for resubmission.
- **Public leaderboard:** fresh read 31 Oct 2026: #1 = **0.4544**, #48 = **0.3231**, #50 = **0.3195**; 0.4413 was absent from the top 50. ORGANIZER-PUBLIC, not a receipt for any focus-site raster. [Snapshot JSON](evidence/leaderboard_snapshot_20261031.json).
- **Software checks:** 451 passed, 0 failed, 2 skipped; skips require missing ignored bridge/sample rasters. Software verification is not geological validation.
- **Submission decision:** no approved download, no TIF generated, and no selector or slot use. Do not submit any repo artifact from this session.
- **Read this brief every session:** [README prompt section](#session-prompt--full-text-read-at-start-of-every-session) and [standing prompt](docs/standing-prompt.md), followed by this review and the latest run card.

**Previous branch review (`arena/946f7668`, 31 Oct 2026):** [review](knowledge/review-arena-946f7668-20261031.md) and [card](evidence/run_card_arena_946f7668_20261031.json). It also ended negative; this session adds the five-hypothesis slate and live leaderboard correction. The prior result remains historical, not a clearance.

## Previous upstream review — session `arena/830e1f79` (31 Oct 2026)

That separate session verified official format wording and performed a live public-board read; its leaderboard rank claims are time-sensitive and are not an organizer receipt for any focus-site file. Its review and run card are [here](knowledge/session-review-arena-830e1f79.md) and [here](evidence/session_830e1f79_run_card.json). The current session still does not clear a file for submission.


## Previous review — session `arena/cfabff7e-gemsdoekarage1` (30 Oct 2026)

**Status: NEGATIVE — DO NOT SUBMIT. No file is cleared, and no new TIF or score estimate was produced in this review.** This is deliberate: `registry/template.json` has no assigned lane or canonical shared template; the shared feature cache/data are absent; and the vendor provenance audit reports writer/uniqueness hash mismatches. Generating an arbitrary raster now would violate the lane, shared-tool, holdout, and uniqueness rules rather than maximize the probability of winning.

- **Review / run card:** [three-pass review](knowledge/session-review-arena-cfabff7e.md) · [JSON card](evidence/session_cfabff7e_run_card.json).
- **Safety fix:** `scripts/prepare_data.py` now exits before the retired private feature stack can run; its regression test covers `--force`. Data-dependent candidate checks are explicitly skipped when their ignored bridge inputs are absent. Full suite after incorporating latest `main`: **446 passed, 0 failed, 2 skipped**; both skips require absent competition rasters/sample data.
- **Score policy:** GEMSDOE24/25/27/28/30/31/32/33/36 values remain USER-REPORTED / UNVERIFIED. A leaderboard estimate is unavailable; do not relabel a catalogue holdout as a leaderboard prediction.
- **Public-board context:** the independent 30 Oct re-read records #1 = 0.4544, 0.3195 at rank #48, and 0.4413 absent from the top 50 (ORGANIZER-PUBLIC; not a submission receipt for any focus site).
- **Submission decision:** there is no current download that is OK to submit. Existing TIFFs are research/audit artifacts only. No weekly slot was selected or spent in this review.

## Latest merged mainline experiment — session `arena/a8e4de2e` (30 Oct 2026)

This separate upstream session used 1 of 3 experiment slots and produced the research-only H-R1 raster `archive/research-hr1-20261030/karage1-hr1-kth-magedge-37654-20261030-zeros.tif`. It was not produced by the current review and is **not cleared**: **HOLDOUT-DTI 0.04330** (evaluator `gems57-pooled-hide-v2`, 45,260 withheld positives, 95% CI [0.03559, 0.04629]); the preregistered verdict is negative and its 3-px density gate also trips. It is not a leaderboard estimate. See [session review](knowledge/session-review-arena-a8e4de2e.md), [run card](evidence/run_card_h_r1_20261030.json), and [saved-byte receipt](evidence/exp_h_r1_kth_magedge_20261030.json).

## Previous-session executive summary — session `arena/c65129cb` (29 Oct 2026)

**Status: NOTHING IS CLEARED FOR UPLOAD. Do not submit any file from this repository yet.**

| File to download | Estimated leaderboard score | Unique? (tested against the 25 registry rasters available locally, not every listed submission) | OK to submit? |
|---|---|---|---|
| [`DO-NOT-SUBMIT_gemsdoekarage1-thd-ridge-collar-20261029-b_pct98-5734dots-zeros.tif`](archive/quarantined-20261029/DO-NOT-SUBMIT_gemsdoekarage1-thd-ridge-collar-20261029-b_pct98-5734dots-zeros.tif) (new; format-valid) | **Not estimable.** HOLDOUT-DTI **0.0093**, 95% CI **[0.0042, 0.0136]**, 22,641 withheld positives (evaluator `gems57-pooled-hide-v2`). Not a leaderboard projection. | **Byte- and pixel-unique** vs the 25 local registry rasters; Spearman worst 0.007; but **99.91% 3-px overlap with the 13GEMS lattice fails the literal 70% gate** (that gate also fails random noise, see review §4) | **NO — DO NOT SUBMIT.** Owner must resolve the gate first. |
| GEMSDOE32 `h33-h33-2-b2` (reference only) | USER-REPORTED 0.2778 — unverified | **No.** Strict subset of GEMSDOE25 with all 6,436 removed dots within 2 px of the catalogue | DO NOT RESUBMIT |

- **Holdout result for the second hypothesis** (strain-rate ridge `geod_2ndinv`, holdout only, no file): HOLDOUT-DTI 0.0129 [0.0031, 0.0201]. Not a clear gain.
- **Leaderboard, verified on the official page this session:** #1 **0.4544**; #48 **0.3195** (corrected from #47; verified live 30 Oct 2026); **0.4413 is not in the top 50**.
- **Full analysis:** [knowledge/session-review-2026-10-29-thd-ridge.md](knowledge/session-review-2026-10-29-thd-ridge.md) · run card [evidence/session_thd_ridge_run_card_20261029.json](evidence/session_thd_ridge_run_card_20261029.json) · gate null check [evidence/lattice_gate_null_check_20261029.json](evidence/lattice_gate_null_check_20261029.json).

**Session `arena/89955dc0` (30 Oct 2026): repository review — NEGATIVE / DO NOT SUBMIT.** Live leaderboard re-read: #1 0.4544; **0.3195 is rank #48** (this README previously said #47; corrected everywhere); 0.4413 is not in the top 50. Test suite: 433 passed after restoring the core data (a layout mismatch in the restore script is flagged, not patched). Review: [knowledge/session-review-arena-89955dc0.md](knowledge/session-review-arena-89955dc0.md) · run card [evidence/session_89955dc0_run_card.json](evidence/session_89955dc0_run_card.json).

Labels: **HOLDOUT-DTI** = our proxy on withheld known-catalogue segments; **ORGANIZER-CONFIRMED** = none exists for any file here; **USER-REPORTED** = values supplied in the request, not verified.


> **Review `arena/dc2e4c0c` (2026-10-29): NEGATIVE / DO NOT SUBMIT.** Fixed the quarantined runner's malformed fail-closed block and added regressions; merged concurrent PR #58's saved-byte retraction audit for the stale K/Th TIFF. Final local suite: **360 passed**. No new raster, geological experiment, HOLDOUT-DTI result, or score estimate. See [this review](knowledge/session-review-arena-dc2e4c0c.md) and [run card](evidence/session_dc2e4c0c_run_card.json).

> **Session `arena/a409acfe` (2026-10-29): NEGATIVE / DO NOT SUBMIT.** A false
> "CLEARED FOR SUBMISSION" page and its `promote` card were on `main`; both are retracted. The
> flagged TIF has 99.90% lattice overlap (stop > 70%) and is quarantined in
> [`archive/quarantined-20261029/`](archive/quarantined-20261029/). 8 failing tests fixed; **357 pass**.
> Read [the session review](knowledge/session-review-arena-a409acfe.md) and [run card](evidence/session_a409acfe_run_card.json).
> **Session `arena/b0714e6b` (2026-10-29), reconciled with `a409acfe`: NEGATIVE / DO NOT SUBMIT.** No new TIF.
> - **Official facts verified** from DrivenData and the NLR rules PDF: metric (α=0.2, β=0.8, R=300 m); float32 GeoTIFF, values in [0, 1], EPSG:32611, NaN or null outside bounds; 3 submissions per week; close **2026-12-03 23:59 UTC**. The 70%/3-px duplicate gate is **not** in the official rules; it is an internal protocol.
> - **Leaderboard correction:** public #1 is **0.4544**; **0.3195 is rank #48**; **0.4413** does not appear on the snapshot; no GEMSDOE score is visible in the top 50.
> - **Blockers:** no assigned method lane (the protocol's "method paragraph" is missing); the literal lattice gate blocks dotted rasters; organizer data is login-walled.
> - Read [session review](knowledge/session-review-2026-10-29.md), [verified sources register](knowledge/official-sources-verified-2026-10-29.md), and [run card](evidence/session_b0714e6b_run_card.json).

**Latest session (`arena/968c17f0-gemsdoekarage1`, 29 OCT 2026): NEGATIVE / DO NOT SUBMIT.** A new **unique, format-valid GeoTIFF** was generated — `docs/downloads/karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.tif` (SHA-256 `f6307da8…`, 4,146,936 bytes). It passes all local format checks (float32, all finite, values in [0,1], EPSG:32611, 3730×3292, transform matches sample, zero outside footprint and on catalogue, 0 NaN inside footprint). It uses a damage-zone halo probability field — structurally unique versus all nine dot-field focus-site submissions. It is a **research artifact only**: no HOLDOUT-DTI (organizer labels login-walled), no registry uniqueness measured, no assigned method lane, no slot spent. **DO NOT SUBMIT.** Run card: `evidence/run_card_karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.json`. Executive summary: `docs/executive-summary.html`.

**Latest mainline session:** [Three-pass review and release-gate hardening](knowledge/session-review-arena-400355af.md). No new submission is cleared; the assigned lane, authoritative template, data and complete registry remain unresolved.
> **Session `arena/cf677bd7`: NEGATIVE / DO NOT SUBMIT** — see [session review](knowledge/session-review-arena-cf677bd7.md) and [run card](evidence/session_cf677bd7_run_card.json). 305 tests pass; no new TIF (lane unassigned, lattice gate blocks champion-sized rasters); nine-site table in the review.
>
> **DO NOT SUBMIT — no candidate has been cleared for competition upload.**
> **New this session (`147b0f11`): a unique, format-valid DIPDUAL GeoTIFF was generated**
> (`karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif`, discrete-unique vs 24 audited rasters)
> **but failed its preregistered holdout gates — research download only, do not submit it.**
> The separately generated BB-STEP research GeoTIFF is unique versus the nine focus-site rasters but fails the literal 3-pixel lattice-overlap rule (98.5253%). Do not submit it. The older CDA1 archive is a synthetic demonstrator whose holdout routine returned hard-coded numbers; its reported DTI is invalid and is not a measurement. All 21 primary and secondary focus-site files audited in this repository also fail the literal lattice gate. Format validation is necessary but not submission approval.

---

# SESSION PROMPT — READ FIRST AT THE START OF EVERY SESSION

This is the standing user prompt for this project. Note (31 Oct 2026): this section is a normalized copy; the original verbatim text was not saved in this checkout. Read it at the start of every session to make sure we are building what we are aiming for.

## Primary goal
Place top of the leaderboard in the DrivenData DOE GEMS Prize Challenge (https://www.drivendata.org/competitions/306/competition-doe-gems/) by producing a single-band float32 GeoTIFF of fault probabilities. Current leaderboard high score: 0.4413 (0.4544 on live public leaderboard per 29 Oct 2026 check).

## Nine focus sites (highest scoring submissions)
GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36.
Study https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html (h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778 — highest reported among the nine sites).
Full score listing is in registry/user_reported_scores_20261029.json.

## Executive summary requirement
Create an executive summary on every site that is clear and obvious which is the best submission to submit to obtain a high score on the leaderboard. It should also be unique and not an exact duplicate of any previous submission. Keep iterating and testing until we have the highest scoring submission to download and submit.

## Table requirement
A table in the executive summary that clearly lists: what file to download, what the estimate score is, and whether it is a unique submission unlike any of the other GEMSDOE sites.

## HIGHEST URGENCY — MUST GENERATE A UNIQUE TIF SUBMISSION
MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION. IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.

There should be an easy to download submission tif file as described by the prompt. Read the entire prompt. A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.

## Validation requirements
The site should be able to generate a TIF file that is required for submission. It should be as easy as download to click a File to submit into the competition. This needs to be in the executive summary or the very beginning of the site. It should be obvious when you visit the site.

## Submission format
Single-band GeoTIFF (.tif) or .zip containing a single GeoTIFF. Must match submission format's CRS, shape, and geotransform. Values must be in range [0, 1]. (Portal error: "Predicted values must be in range [0, 1]")
Unique name and short note (≤140 characters, e.g. clustering with k=25).

## Core values
- Maximize P(Win): Maximize the Probability of Winning
- Own the Outcome: Own results end to end

## Parallel-run protocol
1. LANE: single method paragraph; if rank-correlation with any registry raster exceeds 0.90, or more than 70% of dots fall within 3 px of one registry raster's dots, log as duplicate and stop.
2. REUSE, DON'T REBUILD: Use template's cached feature stack, evaluate_holdout.py and submission_writer.py.
3. LABEL EVERY NUMBER as HOLDOUT-DTI or ORGANIZER-CONFIRMED. A projection is never written as a score.
4. LEAKAGE CANARY: AUC above 0.90 means leakage until proven otherwise.
5. RUN CARD: End with one JSON card (hypothesis, mechanism, named non-fault process, holdout DTI + CI, correlation/overlap vs registry, raster sha256, validator output, submission name + note ≤140 chars, verdict promote/negative).
6. BUDGET: Stop after 3 experiments or 2 hours.

## Scientific research requirement
Before implementing, generate 3–5 candidate geological hypotheses not yet tried, each naming: specific layer(s), physical signature, why it catches faults missing from USGS/INGENIOUS catalogue, how it differs from anything already implemented. Rank by expected DTI improvement and implementation cost. Validate top candidate on spatially-blocked holdout before touching weekly submission slot.

## Data access limitation
No DrivenData auth → cannot auto-download training_features.tif, labels.tif, sample_submission.tif, 1m_DEM_links.csv from https://www.drivendata.org/competitions/306/competition-doe-gems/data/ (verified redirect to login). Need free publicly available sources from official/verified sources.

## Site requirements
Create a GitHub Page for this repo with clean UI, user-friendly, simple and easy to use. Organized and clean. Include all relevant information with official verified links as sources. The site top should show the download link and OK/NOT-OK-to-submit status.

## Output requirements
- Create executive summary subpage explaining exactly how to make a submission
- Easy to download submission tif file
- Obvious whether OK to download and submit
- Unique name and short note ≤140 characters
- Work line by line, verify from official sources, no hallucinations
- Create PR and merge onto main

---

## Start here — session `arena/c4222b5c` (2026-10-29): NOT CLEARED — DO NOT SUBMIT

- **Submission decision page:** [docs/submission-hub.html](docs/submission-hub.html) (also linked from the top of the [site](docs/index.html)). Every file on it is marked **NOT CLEARED: DO NOT SUBMIT** until a gate clears.
- **Unique TIF generated (research file, not cleared):** [`docs/downloads/karage1-tiltgrav-ridge-sp6-37654-20261029.tif`](docs/downloads/karage1-tiltgrav-ridge-sp6-37654-20261029.tif). Single band, float32, EPSG:32611, values in [0, 1], NaN outside the footprint (7,111,787 cells), 37,654 dots. Our format checks pass on the saved bytes. The shared template validator (`scripts/audit_local_tif.py`, receipt `evidence/audit_tiltgrav_ridge_sp6_20261029.json`) **fails** it on the NaN-outside policy only (it requires zeros outside; the official spec allows null or NaN).
- **Uniqueness:** passes the rank rule against all nine focus files (|Spearman| ≤ 0.0036) and the dot-overlap rule (forward overlap 0.112–0.129). **Fails the literal 3-px lattice gate: 0.9962 > 0.70.** The gate is the open decision, see below.
- **Holdout (HOLDOUT-DTI, `gems57-pooled-hide-v2`, 60,988 withheld positives):** spaced candidate **0.0498 [0.0461, 0.0538]** vs spaced random null **0.0526 [0.0499, 0.0557]**, paired Δ −0.0028 [−0.0064, +0.0010]. It does not beat the spacing-matched random null, so it is not promotable under the holdout rule. Negative.
- **Leakage canary:** max single-feature AUC 0.602 (threshold 0.90). No alarm.
- **Focus-site best files:** nine user-reported files (0.2477–0.2778, **USER-REPORTED, UNVERIFIED**, no organizer receipt). None can be estimated by a validated holdout, so each is shown as UNAVAILABLE. Eleven of 36 focus pairs have rank correlation > 0.90 (see [spearman matrix](evidence/site_spearman_matrix_20261029.json)), so most focus files duplicate one another under the registry rule.
- **Experiment budget:** 3 of 3 used (canary, holdout, spacing sweep). Submission slots used: 0. No promotion performed.
- **DECISION NEEDED from the protocol owner:** the literal 3-px lattice gate blocks every dotted raster in the registry (all ≥ 99.6% within 3 px of the 13GEMSDOE lattice). It was **not** jittered, renamed or exempted. The owner must rule whether the gate is applied as written, which makes every dotted candidate ineligible, or is revised.
- **Standing prompt:** the session prompt at the top of this README is copied verbatim to [docs/prompt-2026-10-29.md](docs/prompt-2026-10-29.md). Run card: [evidence/run_card_c4222b5c_20261029.json](evidence/run_card_c4222b5c_20261029.json).
- **Why GEMSDOE32 `h33-h33-2-b2` (0.2778) scored highest:** [knowledge/02_why_gemsdoe32_b2_scored_0.2778.md](knowledge/02_why_gemsdoe32_b2_scored_0.2778.md). The 0.2778 is user-reported; it is not verified here.
- **Official leaderboard (live page, page 1 read):** #1 xiaofanhu 0.4544; 0.3195 is rank #48 per the repo README (not verified this session). Metric and format: [competition page](https://www.drivendata.org/competitions/306/competition-doe-gems/) · [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) · [format and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).

**Irregularities flagged for review:** (B5) the mirror's `sample_submission.tif` carries the known-fault set and equals the labels in positive count, while the official text says the sample "predicts total fault absence"; (B6) two evaluator lineages whose numbers are not directly comparable; (B7) the official feature list has a magnetic source-depth band that is not among the 19 mirrored bands; (NaN) the shared vendor writer encodes outside-footprint cells as zeros, while the official format says null or NaN. An adapter was used and the vendor was not edited (integrity pin); reconciliation belongs to the template owner upstream.

**Limitations.** Holdout DTI is a hide-and-recover estimate on catalogue faults, not an organizer-calibrated score (holdout ≈0.03–0.05 against user-reported (unverified) 0.22–0.28 for the B2 family). The DrivenData data tab is login-walled; restored data are SHA-pinned third-party GitHub mirrors, not authenticated organizer downloads. Local checks cannot establish portal acceptance. The method lane and canonical template are unassigned. Binary dot rasters give degenerate rank values on dot-union subsets (shown as NaN in the matrix); the duplicate rule uses the footprint rank correlation as the registry defines it.

**Remaining work:** resolve the lattice-gate ruling; reconcile the NaN-versus-zeros conflict upstream; calibrate holdout to organizer scores (not available without organizer receipts); add the magnetic-depth band; verify the 0.3195 and 0.4413 claims on the full leaderboard.

> **Review `arena/dc2e4c0c` (2026-10-29): NEGATIVE / DO NOT SUBMIT.** Fixed the quarantined runner's malformed fail-closed block and added regressions; merged concurrent PR #58's saved-byte retraction audit for the stale K/Th TIFF. Final local suite: **360 passed**. No new raster, geological experiment, HOLDOUT-DTI result, or score estimate. See [this review](knowledge/session-review-arena-dc2e4c0c.md) and [run card](evidence/session_dc2e4c0c_run_card.json).

> **Session `arena/a409acfe` (2026-10-29): NEGATIVE / DO NOT SUBMIT.** A false
> "CLEARED FOR SUBMISSION" page and its `promote` card were on `main`; both are retracted. The
> flagged TIF has 99.90% lattice overlap (stop > 70%) and is quarantined in
> [`archive/quarantined-20261029/`](archive/quarantined-20261029/). 8 failing tests fixed; **357 pass**.
> Read [the session review](knowledge/session-review-arena-a409acfe.md) and [run card](evidence/session_a409acfe_run_card.json).
> **Session `arena/b0714e6b` (2026-10-29), reconciled with `a409acfe`: NEGATIVE / DO NOT SUBMIT.** No new TIF.
> - **Official facts verified** from DrivenData and the NLR rules PDF: metric (α=0.2, β=0.8, R=300 m); float32 GeoTIFF, values in [0, 1], EPSG:32611, NaN or null outside bounds; 3 submissions per week; close **2026-12-03 23:59 UTC**. The 70%/3-px duplicate gate is **not** in the official rules; it is an internal protocol.
> - **Leaderboard correction:** public #1 is **0.4544**; **0.3195 is rank #48**; **0.4413** does not appear on the snapshot; no GEMSDOE score is visible in the top 50.
> - **Blockers:** no assigned method lane (the protocol's "method paragraph" is missing); the literal lattice gate blocks dotted rasters; organizer data is login-walled.
> - Read [session review](knowledge/session-review-2026-10-29.md), [verified sources register](knowledge/official-sources-verified-2026-10-29.md), and [run card](evidence/session_b0714e6b_run_card.json).

**Latest session (`arena/968c17f0-gemsdoekarage1`, 29 OCT 2026): NEGATIVE / DO NOT SUBMIT.** A new **unique, format-valid GeoTIFF** was generated — `docs/downloads/karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.tif` (SHA-256 `f6307da8…`, 4,146,936 bytes). It passes all local format checks (float32, all finite, values in [0,1], EPSG:32611, 3730×3292, transform matches sample, zero outside footprint and on catalogue, 0 NaN inside footprint). It uses a damage-zone halo probability field — structurally unique versus all nine dot-field focus-site submissions. It is a **research artifact only**: no HOLDOUT-DTI (organizer labels login-walled), no registry uniqueness measured, no assigned method lane, no slot spent. **DO NOT SUBMIT.** Run card: `evidence/run_card_karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.json`. Executive summary: `docs/executive-summary.html`.

**Latest mainline session:** [Three-pass review and release-gate hardening](knowledge/session-review-arena-400355af.md). No new submission is cleared; the assigned lane, authoritative template, data and complete registry remain unresolved.
> **Session `arena/cf677bd7`: NEGATIVE / DO NOT SUBMIT** — see [session review](knowledge/session-review-arena-cf677bd7.md) and [run card](evidence/session_cf677bd7_run_card.json). 305 tests pass; no new TIF (lane unassigned, lattice gate blocks champion-sized rasters); nine-site table in the review.
>
> **DO NOT SUBMIT — no candidate has been cleared for competition upload.**
> **New this session (`147b0f11`): a unique, format-valid DIPDUAL GeoTIFF was generated**
> (`karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif`, discrete-unique vs 24 audited rasters)
> **but failed its preregistered holdout gates — research download only, do not submit it.**
> The separately generated BB-STEP research GeoTIFF is unique versus the nine focus-site rasters but fails the literal 3-pixel lattice-overlap rule (98.5253%). Do not submit it. The older CDA1 archive is a synthetic demonstrator whose holdout routine returned hard-coded numbers; its reported DTI is invalid and is not a measurement. All 21 primary and secondary focus-site files audited in this repository also fail the literal lattice gate. Format validation is necessary but not submission approval.

## READ FIRST · session `arena/1d15747e` (2026-10-29)

**DO NOT SUBMIT — NOT CLEARED.** Newest file, download for audit only: [`karage1-hgridge-strain-K37654-20261029T181321Z-zeros.tif`](docs/downloads/karage1-hgridge-strain-K37654-20261029T181321Z-zeros.tif) · SHA-256 `15f330343236f41c…` · 37,654 dots.
- Format-valid: EPSG:32611, 3730 × 3292, float32, values in [0, 1], zero outside footprint, 0 on the mapped catalogue.
- Unique versus the 14 pinned non-lattice rasters: worst 22.1% overlap (GEMS19 parent mask), |ρ| ≤ 0.0015.
- **Holdout ≈ random:** HOLDOUT-DTI 0.0481 [0.0381, 0.0558] (label-blind, 22,641 withheld positives, `gems57-pooled-hide-v2`) vs random placement 0.0449 [0.0384, 0.0502].
- **Fails the literal 13GEMSDOE lattice rule** at 99.88%. The rule's floor for 37,654 dots is 82.3%, so no raster this size can pass it. This is a protocol decision for the owner.

**Upload packet (blocked):** file = the `.tif` above · unique name `karage1-hgridge-strain-K37654-20261029T181321Z` · note (108 characters): "K1-HGRID-STRAIN label-blind TMI-crest x strain, 37654 dots. Format-valid; holdout ~ random. NOT CLEARED." Full packet: [how-to-submit](docs/how-to-submit.html).

- **Nine-site executive summary:** [`docs/executive-summary.html`](docs/executive-summary.html) · data [`evidence/nine_site_executive_20261029.json`](evidence/nine_site_executive_20261029.json). Estimated score is UNAVAILABLE for every row. The best listed file, GEMSDOE32 `h33-h33-2-b2` (0.2778, USER-REPORTED), is not unique against the other focus files.
- **Session review** (0.2778 analysis, 5 ranked hypotheses, 12 irregularities, remaining work): [`knowledge/session-review-arena-1d15747e.md`](knowledge/session-review-arena-1d15747e.md)
- **Run card:** [`evidence/hgridge_run_card_20261029T181321Z.json`](evidence/hgridge_run_card_20261029T181321Z.json) · experiments: [E1 canary](evidence/hgridge_e1_canary.json), [E2 holdout](evidence/hgridge_e2_holdout.json), [E3 build](evidence/hgridge_e3_build_20261029T181321Z.json)
- **Standing prompt (read every session):** [`knowledge/user-standing-prompt-20261029.md`](knowledge/user-standing-prompt-20261029.md)
- **Official leaderboard, read 29 Oct 2026:** #1 0.4544 (`xiaofanhu`). The 0.4413 and 0.3195 figures in the prompt are not matched by name on the board. Flagged in the review.
## ▶ Can I download and submit a file? — **NO. Nothing in this repository is cleared.**

Session `arena/ca9c4488` (2026-10-29): **NEGATIVE / DO NOT SUBMIT.** No new GeoTIFF was generated. Full review: [knowledge/session-review-arena-ca9c4488.md](knowledge/session-review-arena-ca9c4488.md) · run card: [evidence/session_ca9c4488_run_card.json](evidence/session_ca9c4488_run_card.json).

| Site | Best file (reported score) | New estimate | Unique vs the other 8 focus files? | Unique vs lattice (70 % / 3 px)? | OK to download & submit? |
|---|---|---|---|---|---|
| GEMSDOE32 (B2) | `gemsdoe32-h33-h33-2-b2-…-zeros.tif` (0.2778, USER-REPORTED) | not estimable | No (1.000 vs 24/25/27/28) | No (0.9992) | **NO** |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-…-zeros.tif` (0.2750) | not estimable | No (0.976 vs 27) | No (0.9992) | **NO** |
| GEMSDOE28 | `gems28-h27-4-r1-solo-d2-8-…-allfinite.tif` (0.2708) | not estimable | No (identical mask to 31) | No (0.9992) | **NO** |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-…tif` (0.2632) | not estimable | No (0.997 vs 27) | No (0.9991) | **NO** |
| GEMSDOE25 / 30 | `…d2-8…-nan.tif` / `gemsdoe30-d28-poisson…tif` (0.2600) | not estimable | No (identical masks) | No (0.9992) | **NO** |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-…-nan.tif` (0.2708) | not estimable | No (identical mask to 28) | No (0.9992) | **NO** |
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-…-nan.tif` (0.2477) | not estimable | No (1.000 vs 25) | No (0.9992) | **NO** |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-…-nan.tif` (0.2449) | not estimable | No (0.980 vs 24) | No (0.9992) | **NO** |

- **Why no file is cleared.** The literal duplicate rule (70 % of dots within 3 px of one registry raster) is failed by all nine focus files against the lattice. The lattice covers 99.87 % of the footprint, so a dotted file can pass only if it has ≤ 22,163 dots and ≥ 30 % of them in 6,649 uncovered cells. That is not a geological result, and the protocol bars placing dots to evade the rule. The shared gate also needs a complete registry inventory, which this repository does not have.
- **Decision needed from the owner** (options A/B/C in §8 of the review): whether the lattice counts as a registry duplicate, and whether a documented exception is allowed. Until that is decided, no file is cleared.
- **Score estimates are withheld.** Every score above is USER-REPORTED / UNVERIFIED. A new estimate needs a HOLDOUT-DTI run with a 95 % CI, which has not been done.
- **Format error.** The sample grid uses NaN outside the footprint. The "must be in range [0, 1]" rejection is probably caused by NaN in a naive range check. That is a hypothesis; the portal's real check is unknown.
- **Standing prompt.** The standing brief is in [docs/standing-prompt.md](docs/standing-prompt.md) and the section below. The full verbatim prompt was not saved as a file in this checkout.

## READ FIRST — Standing brief (updated 29 Oct 2026)

> **Condensed rewrite of the session brief, not the verbatim prompt.** Newer explicit instructions take precedence.

**Goal.** Place at the top of the DrivenData *Geologic Enhanced Mapping System (GEMS) Prize Challenge* by
producing a single-band float32 GeoTIFF of fault probabilities. Source: [official problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [DOE/NLR submission rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf).

**Official rules (verified 29 Oct 2026 from the problem page).** EPSG:32611, 100 m, same bounds; one float32 layer; values in
[0, 1]; outside bounds null or NaN. Score is a distance-weighted Tversky index, α=0.2, β=0.8, 300 m triangular kernel.
The competition states its purpose: predictions for what you believe are faults, not optimization against existing labels.

**Core values.** *Maximize P(Win)* and *Own the Outcome*: prefer reproducible, sourced evidence; report negative results and blocked gates honestly; never invent a score.

**Non-negotiables.**
1. **Every number is labelled** HOLDOUT-DTI (evaluator, withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a receipt), or USER-REPORTED / UNVERIFIED. A projection is never written as a score.
2. **A file is downloadable for submission only when every gate passes**: format, unique versus listed sites, lattice rule, holdout, lane, and a separate weekly-slot selector. The site shows the status on its first screen.
3. **Parallel-run protocol:** one assigned lane; literal 70% registry overlap and |rank| > 0.90 checks; reuse the shared evaluator and writer; leakage canary (AUC > 0.90 is leakage); budget of 3 experiments or 2 hours; a JSON run card with each run.
4. **Verify line by line** against official sources, link each source, flag irregularities. No manual input is expected.

> **Session `arena/5ee7ef4b` (29 Oct 2026): NEGATIVE / DO NOT SUBMIT.** Executive summary: [`docs/session-5ee7ef4b.html`](docs/session-5ee7ef4b.html) · review: [`knowledge/session-review-arena-5ee7ef4b.md`](knowledge/session-review-arena-5ee7ef4b.md) · run card: [`evidence/session_5ee7ef4b_run_card.json`](evidence/session_5ee7ef4b_run_card.json).
> - **New format-valid TIF, not cleared:** `archive/research-s1-20261029/karage1-s1-tmihg-ridge-offcat-20261029-zeros.tif` (sha256 `5eccad68…bd8bd`). Format-valid against the official rules and not an exact duplicate. Holdout-faithful HOLDOUT-DTI 0.0432 [0.0380, 0.0461], at or below the matched random floor 0.0446. Fails the literal internal lattice rule (99.97%, a saturated rule).
> - **Shared-evaluator calibration:** the GEMSDOE32 champion scores 0.0047 on the internal holdout, below random. The holdout's truth is mapped catalogue, so off-catalogue candidates are penalised by construction. No off-catalogue idea can be validated on it until the holdout is fixed (owner decision).
> - **Leaderboard (ORGANIZER-PUBLIC, 29 Oct 2026):** #1 0.4544, #2 0.3916, #3 0.3911. The brief's 0.4413 is not on the page. Focus-site scores are USER-REPORTED / UNVERIFIED.
> - Tests: 382 pass. The official rules contain no lattice or duplicate rule; that gate is internal.

**Current decision (29 Oct 2026): NO FILE IS OK TO DOWNLOAD AND SUBMIT.**
- The nine focus sites: best reported file is GEMSDOE32 at 0.2778 (USER-REPORTED / UNVERIFIED). It is third-party and must not be resubmitted. All nine overlap a sibling by ≥ 97.6%. See the table at the top of the [executive summary](docs/executive-summary.html).
- Our own 12 local TIFs all fail the literal lattice rule (min overlap 98.53%). This includes the GSE pair (`karage1-gse-geothermal-surface-24000dots-…`) added to `main` by commit `cd6f891`. Its "unique" label holds only against the 11 registry rasters it checked. Against the 13GEMSDOE lattice witness it is a **literal duplicate at 99.91%** ([audit](evidence/local_downloads_audit_20261029.json)). The rule is saturated: random dots fail it too ([evidence](evidence/lattice_saturation_null_20261029.json)). The owner must decide how the rule applies before any file can clear.
- Session review: [`knowledge/session-review-arena-20261029.md`](knowledge/session-review-arena-20261029.md) · run card: [`evidence/session_20261029_run_card.json`](evidence/session_20261029_run_card.json) · new hypotheses: [`docs/research/hypotheses-20261029.md`](docs/research/hypotheses-20261029.md).
- Independent review on this branch (`arena/07823dcc`): no new experiment or TIF; the concurrent GSE artifact is format-checked but fails the literal lattice test at 99.9125% on the pinned mirror and has no HOLDOUT-DTI. See [supplemental review](knowledge/session-review-arena-07823dcc-2026-10-29.md), [run card](evidence/session_07823dcc_run_card.json), and [filename-provenance note](evidence/gse_concurrent_artifact_reaudit_20261029.json). This is a cross-check, not a second independent organizer-data or leaderboard result.

**Owner decisions required:** (1) whether the internal 70% / 3-px / Spearman gate binds submissions at all: it is **not** in the official rules ([register B1](knowledge/official-sources-verified-2026-10-29.md)), and if it does, whether the 13GEMSDOE calibration lattice is the witness; (2) the method lane (still `null`); (3) authorized holdout data; (4) the portal's "must be in range [0, 1]" error: no local raster reproduces it, see [review](knowledge/session-review-arena-20261029.md). **Deadline:** 3 Dec 2026, 11:59 p.m. UTC; three submissions per week; original work only.

---
> **Session `arena/6275e37e` (2026-10-29): NEGATIVE / DO NOT SUBMIT — no file is cleared, no new TIF produced.** Read [the session review](knowledge/session-review-arena-6275e37e.md) and [run card](evidence/session_6275e37e_run_card.json). New, verified this session:
> - **Official reference checked line by line** at pinned commit `aebe92f` (notebook SHA-256 `1a762273…`): `alpha = 0.2` is the false-positive weight, `beta = 0.8` the false-negative weight, the writer emits sigmoid values in [0, 1] with no NaN masking, and its buffer is float64 by NumPy default (the brief says float32: a flagged irregularity). Source table: [`knowledge/official-reference-verification-20261029.md`](knowledge/official-reference-verification-20261029.md).
> - **Marginal rule (algebra, tested):** because α + β = 1, a non-redundant dot improves DTI iff its expected credit exceeds α·DTI (0.0556 at the reported 0.2778). This is the quantitative form of the question "why thinning helped" — a testable prediction, not a result. Test: [`tests/test_marginal_rule.py`](tests/test_marginal_rule.py).
> - **Portal-error diagnostic:** [`scripts/portal_range_check.py`](scripts/portal_range_check.py) shows that NaN-outside files fail a naive whole-array range test. The portal's own rule is still unknown. Run it on the exact file that failed upload.
> - **Not established:** a holdout DTI for any new candidate (no authorised official data in the sandbox; the only restorable copy is a third-party mirror), and the leaderboard figures (the brief's 0.4413 and 0.3195 conflict with the earlier-fetched 0.4544).
> - Tests: **384 passed** (software checks only).

> **Session `arena/23ef16f9` (2026-10-29): NEGATIVE / DO NOT SUBMIT. No TIF generated for upload.** Three blockers, verified: (1) the DrivenData data tab is login-walled; mirror-restored copies on `main` are not organizer-authenticated and were not used for any holdout here; (2) the internal 70% / 3-px gate is unsatisfiable for any raster above **22,163 dots** against the recorded 13GEMSDOE witness (`evidence/registry_pair_check_23ef16f9.json`) — an owner decision, not a file; (3) no method lane is assigned. Verified facts: the GEMSDOE32 0.2778 file is GEMSDOE25 minus 6,436 dots (strict subset); live #1 = **0.4544**; **0.3195 is rank #48** (the previous note said otherwise — corrected). Review: [knowledge/session-review-arena-23ef16f9.md](knowledge/session-review-arena-23ef16f9.md) · run card: [evidence/session_23ef16f9_run_card.json](evidence/session_23ef16f9_run_card.json). Tests on this branch after merging `main`: 372 pass, 7 fail, identically to `main` (pre-existing, see review §7).
> **Latest review `arena/547a9b56` (2026-10-29): NEGATIVE / DO NOT SUBMIT.** New this session: core inputs (`training_features`, `labels`, `sample_submission`) were restored from pinned GitHub mirrors and every SHA-256 matched ([evidence](evidence/core_data_verification_20261029.json)); the restored sample raster is a label copy (60,988 positives coincide with known faults), contrary to the DrivenData page's "total fault absence" wording; the feature and label footprints disagree on 4,601 pixels; the "[0, 1]" portal error still cannot be reproduced (no local TIF has out-of-range values). Test suite: **373 passed**. No candidate, holdout result or slot. See [session review](knowledge/session-review-arena-547a9b56.md) and [run card](evidence/session_547a9b56_run_card.json).
>
> **Current review `arena/4711a029` (2026-10-29): NEGATIVE / DO NOT SUBMIT.** No new TIF, geological experiment, score estimate, or upload slot was produced. The nine-site comparison and four ranked research candidates are in [the current review](knowledge/session-review-arena-4711a029.md); the required session run card is [here](evidence/session_4711a029_run_card.json). The pinned template/data preflight is blocked (lane and canonical assignment absent, required cache/data missing, two vendored hash mismatches); all 365 software tests pass but do not measure model performance.

> **Session `arena/be012103` (2026-10-29): NEGATIVE / DO NOT SUBMIT — no file is cleared.** No new TIF was generated: the competition data is login-walled and unreachable from the sandbox, and no method lane is assigned, so there is nothing to holdout-test or score. Live leaderboard (fetched 2026-10-29): **#1 = 0.4544** (xiaofanhu), #2 = 0.3916; 0.4413 not found; 0.3195 near rank #47. The GEMSDOE32 **0.2778 is an owner-report with no submission receipt** on its own page, which also says "already submitted - do not resubmit". Test suite: **365 passed**. Details: [session review](knowledge/session-review-arena-be012103.md), [run card](evidence/session_be012103_run_card.json). Manual steps needed from the owner are listed in the review.

> **Latest review (`arena/bd75aa22`, 2026-10-29): NEGATIVE / DO NOT SUBMIT.** Repository review only; no new TIF, geological experiment, HOLDOUT-DTI, score estimate, or slot selection. Test suite: **365 passed** (software verification only). No lane assignment or canonical shared template is recorded, authenticated inputs/cache and complete registry are unavailable, so experiments and a cleared unique submission remain blocked. See [session review](knowledge/session-review-arena-bd75aa22.md) and [JSON run card](evidence/session_bd75aa22_run_card.json).

## Standing prompt (read at the start of every session)

**Competition.** DrivenData DOE GEMS prize — https://www.drivendata.org/competitions/306/competition-doe-gems/ — single-band GeoTIFF, values in [0, 1], CRS/shape/geotransform identical to the submission format (EPSG:32611).

**Core values.** Maximize P(Win); Own the Outcome. Report negative results, blocked data, and unprovable claims honestly; nothing is projected as a score; irregularities are flagged, not hidden.

**Requirements (full reconstruction in `docs/standing-prompt.md`):**
1. Build an auditable workflow that generates a **unique, valid** single-band GeoTIFF; prior GEMSDOE submissions (24, 25, 27, 28, 30, 31, 32, 33, 36 and the wider series) are for learning only — never copied.
2. **Highest urgency: a UNIQUE TIF.** It must be **obvious** whether a TIF is OK to download and submit. The site top shows the download link and the OK / NOT-OK-to-submit status.
3. Executive summary table per focus site: file to download, labeled number, uniqueness versus all listed GEMSDOE submissions; a how-to-submit subpage (file, unique name, note ≤ 140 characters).
4. Every number labeled **HOLDOUT-DTI** (evaluator, withheld positives, 95% CI) or **ORGANIZER-CONFIRMED**. A projection is never written as a score.
5. Autonomous validation (no human inspector): values in [0, 1], no NaN inside the footprint — addresses the earlier "Predicted values must be in range [0, 1]" rejection.
6. PhD-level explanation of how `GEMSDOE32 h33-h33-2-b2` reported 0.2778 and whether it can be beaten; use that to generate the unique TIF.
7. Propose 3–5 new geological hypotheses (layers, physical signature, why off-catalogue, how it differs), ranked by expected DTI gain and cost; validate the top candidate on a spatially-blocked hide-and-recover holdout before any slot; free official sources only.
8. **PARALLEL-RUN PROTOCOL:** one assigned lane; registry duplicate check (|Spearman| > 0.90 or > 70% of dots within 3 px → log and stop); reuse shared `evaluate_holdout.py` / `submission_writer.py` (fix once, never private-fork); label every number; leakage canary (single feature AUC > 0.90 → leakage); budget ≤ 3 experiments or 2 hours; no slot selection (separate selector, weekly cap); end with a JSON run card and promote/negative verdict.
9. No hallucinations: verify line by line from official sources; collect data/knowledge into auditable tables; state limitations and access needs (no DrivenData login; the data tab is login-walled).
10. Clean GitHub Pages site under `docs/`; three passes then a PR merged to `main`, listing remaining work and limitations.

## Latest session (`arena/c26ad154-gemsdoekarage1`): NOT CLEARED — focus-site summary, unique research TIF, holdout-negative

- **Verdict: NEGATIVE · NOT CLEARED · DO NOT SUBMIT.** `ok_to_submit: false`, `submission_slots_used: 0`, `slot_selected_or_spent: false`, experiments used 3 of 3.
- **Executive summary:** [`docs/focus-sites.html`](docs/focus-sites.html) (linked from the decision panel on the home page). It covers the nine focus sites (owner-reported scores, file, uniqueness), the holdout table, the GEMSDOE32 0.2778 analysis, ranked hypotheses, how to submit, irregularities and limitations.
- **Research TIF (unique, format-valid, not cleared):** primary `docs/candidates/karage1-probcollar-gbm-K37654-collar3-20261029-nan.tif` (NaN outside the footprint, official format), SHA-256 `07ec7292…97d5`; zeros-outside twin `…-zeros.tif` (SHA-256 `8e5269c6…941e`, same 37,654 dots) for the repo's all-finite gate. Closest dot to the catalogue 3.16 px. No download is offered. The shared gate refuses NaN outside under its local policy; this conflict is flagged, not waived. The literal lattice gate fails (99.16%, against a 99.87% chance level).
- **Holdout (HOLDOUT-DTI, 95% CI):** candidate arm 0.0619 (all) and 0.0588 (detached). Proximity control 0.0698 and 0.0626. Holdout best is the random-in-ring control at 0.0924 and 0.0904. H3 (model ranking inside the 1 px ring vs random tie-break) is rejected in both modes.
- **Run card:** `evidence/run_card_probcollar_20261029.json`, identical copy at `docs/data/run-card-probcollar-20261029.json`. The pinned card paths (`evidence/run_card.json`, `docs/data/run-card.json`, `docs/data/run_card.json`) still hold the prior BB-STEP card, because three tests pin them to it.
- **Code:** `scripts/run_probcollar_holdout.py`, `scripts/run_ring_tiebreak_holdout.py` (holdout experiments); `scripts/build_candidate_submission.py` (writes the TIF through the shared `vendor/gems57/submission_writer.py`); `scripts/audit_candidate_uniqueness.py`, `scripts/focus_site_table.py` (independent read-back and nine-site audit); `scripts/write_run_card_probcollar.py`; `scripts/build_focus_summary.py`.
- **Tests:** `tests/test_official_dti_formula.py` and `tests/test_focus_sites_20261029.py`. The full suite (`pytest -q`) passes.
- **Remaining work:** H4 (dispersion-constrained selection) is the top untested hypothesis and needs a spatially blocked holdout before any slot is considered. Its holdout budget is spent. See the page's section 8.

## Current session review (`arena/accf3693-gemsdoekarage1`)

**DO NOT SUBMIT — no new candidate generated or cleared.**
[Three-pass review and next steps](knowledge/session-accf3693-review.md) ·
[Current shared preflight](evidence/session_accf3693_shared_preflight.json) ·
[Session run card](evidence/session_accf3693_run_card.json).
The fresh checkout has no restored shared cache and no assigned method lane or
canonical-template assignment. Historical evidence below is not a fresh model run.
This session hardened report input preservation and strict JSON handling;
**314 software tests pass** (not a performance score). The existing nine-site
summary and four ranked research proposals remain below; no leaderboard estimate
or new uniqueness certificate is asserted.

[Latest forensic & 9-site review (`9ca08e2e`)](knowledge/session-review-arena-9ca08e2e.md) · [Latest session run card (`9ca08e2e`)](evidence/session_9ca08e2e_run_card.json) · [19-band `training_features.tif` audit](evidence/training_features_band_audit_20261028.json) · [Secondary 9-site audit (12 files)](evidence/nine_sites_secondary_audit_20261028.json) · [Decision Dashboard](docs/index.html) · [Executive Summary & Submission Guide](docs/executive-summary.html) · [Nine-Site Audit Data](docs/data/reference-audit.json) · [Two-Candidate Saved-Byte Audit](evidence/candidate_audit_20261028.json) · [Independent repository and BB-STEP/CDA1 saved-byte review](knowledge/repository-review-2026-10-28.md) · [Session Review (`0a62cb67`)](knowledge/session-0a62cb67-review.md) · [Session Review (`8ffb6de1`)](knowledge/session-review-arena-8ffb6de1.md) · [Research Hypotheses](docs/research.html) · [Official Source Register](knowledge/sources-2026-10-28.md)

## Latest session (`arena/147b0f11-gemsdoekarage1`): NEW unique DIPDUAL TIF — preregistered, holdout-negative

- **Verdict remains `NEGATIVE / DO NOT SUBMIT`** ([session review](knowledge/session-review-arena-147b0f11.md) · [run card](evidence/run_card_dipdual_20261028.json) · [preregistration](docs/research/preregistration-dipdual-20261028.md) · [executive summary](docs/dipdual-20261028/index.html) · [how to submit](docs/dipdual-20261028/how-to-submit.html)): 0 slots spent; promotion remains the separate selector step.
- **New unique TIF generated** (urgency item): `karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif` in [docs/downloads/](docs/downloads/karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif) (+ single-TIF ZIP + writer receipt), SHA-256 `7b2a58eb1c3fb49cdd65f317c57d5552fe019c9be215aa2864533c2a50873cae`, 37,654 dots — **not copied from any prior submission** (new exposed/buried surfaces; worst discrete forward overlap 23.75%, vs B2 11.96%, pre-placement |Spearman| ≤0.058) and **format-valid** (shared writer + two independent saved-byte re-reads: finite [0,1] everywhere, EPSG:32611/shape/transform match, 0 on-catalogue). It is **NOT cleared**: blocked `HOLDOUT-DTI 0.040056 [0.034544, 0.046131]` (`gemsk-hide-recover-v1`, 60,988 withheld) < GPC control `0.073394` and BB-STEP control `0.046742`; `SGMC-DIAGNOSTIC-DTI 0.090244 [0.077331, 0.102597]` < GPC `0.126149`. Suggested note (`76` chars): `DIPDUAL dual-regime dip-shifted research raster; gates failed; DO NOT SUBMIT`.
- **Diagnosis:** contour-obliquity gate is anti-signal (AUC 0.42 — catalogue range fronts *are* contour-parallel; `IR-DIPDUAL-OBLIQUE-01`, not sign-flipped post-hoc); buried-basin allocation is unvalidatable on either local truth (catalogue + SGMC are surface compilations) and dilutes precision on both; dip-projection effect ≈0 at 100 m/300 m scales. **Positive control result:** label-free GPC physics beats static B2 on off-catalogue SGMC (`+0.0308 [+0.0082, +0.0519]`) and is the repo's best label-free blocked surface — next preregistered lane: exposed-only GPC refinement (+ LOO damage-zone prior, LiDAR polarity, no obliquity, no buried quota).
- **Lattice resolved by role separation** (`registry/registry_roles.json`, `IR-DIPDUAL-LATTICE-01`): lattice covers 99.8713% of footprint within 3 px (lower bound 82.34% at N=37,654; B2: 99.915% fwd / 15.06% rev). Duplicate gate now applies to `discrete_submission` rasters; literal lattice overlap (DIPDUAL 99.89%) is published in the card and needs selector acknowledgment.
- **Local candidates re-scored on SGMC** ([evidence/local_candidates_sgmc_audit_20261028.json](evidence/local_candidates_sgmc_audit_20261028.json)): HMAS `0.112595` > DIPDUAL `0.090244` > GPC-Z `0.077928` — HMAS stays selector-shortlist **only**, needs end-to-end re-validation; the older `karage1-unique-alteration` TIF **fails current format re-read** (`SGMC 0.003446`) — do not use.

## Earlier session (`arena/1668dda0-gemsdoekarage1`): 9-file local download audit, PR #42 retraction, validator hardening & 22-repo peer ecosystem review

**NEGATIVE / DO NOT SUBMIT — zero GeoTIFFs in `docs/downloads/` or across audited peer repositories are cleared for competition upload.** No new GeoTIFF was generated and no weekly slot was selected or spent.

- **Deliverables:** [Session review, B2 analysis & 4 preregistered hypotheses](knowledge/session-review-arena-1668dda0.md) · [Session JSON run card](evidence/session_1668dda0_run_card.json) · [9-local + 9-peer saved-byte audit receipt (`22` pinned repos)](evidence/local_downloads_and_peer_audit_20261028.json) · [Immutable peer ecosystem pins](registry/peer_ecosystem_pins.json).
- **Retracted defective PR #42 artifact & sidecars:** Direct saved-byte inspection of [`docs/downloads/karage1-unique-alteration-dots-20261028-zeros.tif`](docs/downloads/karage1-unique-alteration-dots-20261028-zeros.tif) (`8bc4dae0…`) against the pinned mirror template and `13GEMSDOE` lattice proved **`2,113` of `3,500` positive pixels (`60.37%`) lie OUTSIDE the active footprint** (`outside_encoding_accepted = false`) and **`1,385 / 1,387` (`99.8558%`) of in-footprint positives fall within `3 px` of the lattice**. Superseded false `"ok_to_submit": true` / `"verdict": "promote"` sidecars (`docs/downloads/karage1-unique-alteration-dots-20261028-zeros.{json,validate.json}`, `evidence/run_card_unique_tif_20261028.json`) and quarantined both `scripts/generate_unique_submission.py` and `scripts/run_bbstep_experiments.py`.
- **Closed three format-validator loopholes:** `scripts/validate_geotiff.py` now rejects all-finite bogus templates (`footprint.all()`), computes explicit `diagnostics.outside_encoding_accepted`, and exits `1` whenever outside-footprint validation fails; `scripts/audit_references.py` `raster_checks` requires `outside.size > 0` for `outside_all_nan` and blocks `--out` overwrites of `--manifest`.
- **Audited sibling `karage` & broader peer ecosystem (`GEMSDOE91/92`, `KANLER`, `EUG`, `WBG`, `GINNY`, `karage2/3`, `Apart`, `SASS`):** Every audited sibling/peer GeoTIFF (`GEMSDOEkarage2` `hk3-edgecentrality`: `99.86%`; `GEMSDOEkarage3` `k3c-csst-bghf`: `99.35%`; `GEMSDOE91` `S18-UNIQUE` `20,000` dots / `0.0435` user-reported: `99.61%`; `KANLERGEMSDOE3`, `WBGGEMSDOE1`, `ApartGEMSDOE1/2`, `GEMSDOESASS1`) overlaps `99.35%–99.95%` within `3 px` of the `13GEMSDOE` lattice. Documented two holdout-control defects in historical `src/gemsk/holdout.py` (`3 px` visible-collar dilation erasing `363` withheld truth pixels + static full-catalogue-pruned `B2` baseline). **354 software tests pass** (not a model performance score).

## Earlier session (`arena/a1ef4ce0-gemsdoekarage1`): independent replay and mandatory evidence gates

**NEGATIVE / DO NOT SUBMIT. The requested unique, high-scoring, cleared TIFF remains undelivered.** No geological experiment or slot was used. The assigned single method paragraph is still missing; inventing a lane or exempting the dense lattice is not permitted.

- [Current review and three proposed geological tests](knowledge/session-review-arena-a1ef4ce0.md) · [Session JSON card](evidence/session_a1ef4ce0_run_card.json) · [Organizer code-source receipt](evidence/official_code_receipt_a1ef4ce0.json).
- Independently re-fetched and SHA-256-verified all twelve pinned nine-site audit assets; the audit exactly reproduces the saved evidence except timestamps/software metadata. These are mirror-byte measurements, not organizer authentication or a full registry.
- Fixed two **promotion-by-omission** gaps: baseline withheld-positive counts must be explicit matching integers; pixel-mask validation must explicitly report `unmasked_inside: true` and integer `masked_inside_count: 0`. Finite values alone cannot establish an unmasked footprint.
- Source-card overwrite tests now cover valid/malformed JSON, same/relative paths, symlinks and hardlinks. Concurrent mainline duplicate-key rejection and preservation safeguards were retained. No shared evaluator/writer was changed or repinned.
- Directly inspected the organizer's pinned reference code: CPU-only training is supported, and its random-patch Tversky-loss baseline is not the requested buffered whole-segment DTI holdout. The earlier GPU-only prerequisite is inaccurate.
- B2's collar-removal geometry was independently reproduced, but a causal improvement on hidden organizer labels is **not proven**. The current leaderboard and weekly cap were not verified. No numerical leaderboard estimate is justified.

Read this README, `docs/standing-prompt.md`, `AGENTS.md`, and the current session review at the start of future work. The long original request remains represented by the explicitly normalized standing brief, not falsely described as a verbatim transcript. Its highest-priority unique-TIFF requirement and the binding lane/duplicate/holdout/budget/selector controls remain in force together.

## Earlier session (`arena/9ca08e2e-gemsdoekarage1`): 21-file nine-site audit, 19-band nodata forensics & fail-closed hardening

- **Verdict remains `NEGATIVE / DO NOT SUBMIT`** ([session review](knowledge/session-review-arena-9ca08e2e.md) · [session run card](evidence/session_9ca08e2e_run_card.json)): `0` new competition uploads or weekly-slot selections were made.
- **All 21 prompt-listed focus-site submissions audited** (`9` primary leaders in [docs/data/reference-audit.json](docs/data/reference-audit.json) + `12` secondary runs in [evidence/nine_sites_secondary_audit_20261028.json](evidence/nine_sites_secondary_audit_20261028.json), plus concurrent `GEMSDOE25` H79 in [docs/data/concurrent-review.json](docs/data/concurrent-review.json)): **every single file overlaps `99.1687%–100.0000%`** within 3 px of the pinned `13GEMSDOE` lattice (even `11,082`-dot `gems28-s18-mxtp` overlaps `100.0000%`).
- **Exact 4-point B2 collar-ablation ladder proven on pixel masks:** on the mirrored footprint, `GEMSDOE25` $\equiv$ `GEMSDOE30` (`44,090` dots, `0.2600` `USER-REPORTED / UNVERIFIED`) is the $r = 0$ parent; removing `3,891` dots within $r \le 1$ px (`100 m`) of `labels.tif` yields `GEMSDOE31` $\equiv$ `GEMSDOE28` `h27-4-r1` (`40,199` dots, `0.2708` `USER-REPORTED / UNVERIFIED`); removing `6,436` dots within $r \le 2$ px (`200 m`) yields `GEMSDOE32` `h33-h33-2-b2` (`37,654` dots, `0.2778` `USER-REPORTED / UNVERIFIED`); and `GEMSDOE36` (`38,854` dots, `0.2750` `USER-REPORTED / UNVERIFIED`) is `B2` $\cup$ `1,200` off-catalogue dots.
- **19-band `training_features.tif` forensic discovery** ([evidence/training_features_band_audit_20261028.json](evidence/training_features_band_audit_20261028.json)): **3,073 pixels inside `sample_submission.tif`'s active footprint** contain raw float32 `-3.4028235e+38` `nodata` (`3,061` across 18 bands + `12` extra interior pixels on Band 6 `tc`), providing a direct mechanism for `[0, 1]` portal range errors if unmasked; Band 6 `tc` is also strictly positive (`[2.9534, 88.5665]`) rather than a zero-crossing signed tilt angle.
- **Later mainline candidate re-audit:** the newer Conduitcrest TIF in main (`65c9432b…`, 17,415 dots) is **99.3454% within 3 px of the lattice** (17,301/17,415), so the literal rule says duplicate/stop despite its reported 0% overlap versus the nine focus sites. Its prior card omitted the lattice, a pre-placement lattice check, a per-feature canary, and a 95% CI for its HOLDOUT-DTI claim; it is **DO NOT SUBMIT**. Details: [`evidence/conduitcrest_lattice_reaudit_20261028.json`](evidence/conduitcrest_lattice_reaudit_20261028.json).
- **Shared validator & audit hardening:** hardened `src/gemskarage1/registry_audit.py` (GDAL mask + DrivenData `NaN`-outside support + `equal_nan=True`), `scripts/release_gate.py` (fail-closed CLI with strict `NaN`/`Infinity` rejection + atomic `--out`), `scripts/audit_references.py` / `audit_concurrent.py` / `audit_archives.py` / `audit_rasters.py` (GDAL mask + `abs(spearman) > 0.90` + `None`-metric guard), `scripts/collect_sources.py` (40-hex commit SHA enforcement + atomic writes), and `scripts/render_site.py` (fail-closed secondary 9-site audit rendering). This branch's direct test run before integrating current `main` had 230 passing tests; after merging the concurrent mainline regression suite, the current integrated suite passes **305 tests** (119 Rasterio/Affine pending-deprecation warnings).

## Earlier review — 28 October 2026, session `arena/0a62cb67-gemsdoekarage1`

All 12 pinned reference assets, the 2 committed candidates, the 2 parallel PR
candidates, the 3 archived demonstrators, and the concurrent peer raster were
freshly fetched from pinned GitHub mirrors into ignored `.cache/` and re-audited:
every reproduced report matched the committed JSON evidence byte-for-byte
(excluding execution timestamps and runtime package metadata). Additional
fail-closed safeguards were added and covered by regression tests: rejecting
duplicate registry SHA-256 digests, whitespace-only registry IDs, and
self-template digests in `scripts/release_gate.py`; blocking self-template
validation in `scripts/validate_geotiff.py` and `scripts/validate_artifact.py`;
blocking masked/nodata in-footprint candidate pixels in
`src/gemskarage1/registry_audit.py`; and hardening
`scripts/audit_parallel_candidates.py` against non-float32 rasters, undefined
footprint correlations, and `--out` input overwrites. See the
[session review](knowledge/session-0a62cb67-review.md) and
[negative session run card](evidence/session_0a62cb67_run_card.json). No new
portal upload or weekly-slot selection was made.

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
| **GEMSDOEkarage1 (NEW)** | `karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif` | HOLDOUT-DTI 0.040056 | LABELLED LOCAL INSTRUMENT (live unknown) | YES vs discrete registry (worst 23.75%); lattice literal 99.89% | **DO NOT SUBMIT** (holdout gates failed; research download) |
| **GEMSDOE27** | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; 61.20% vs GEMSDOE24 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOEkarage1 (BB-STEP, prior parallel session)** | `karage1-bbstep-buried-basement-20261028T180000Z-zeros.tif` | 0.031790 [0.027138, 0.036271] | **HOLDOUT-DTI** (`gemsk-hide-recover-v1`; 60,988 withheld positives; 95% CI shown; not organizer-confirmed) | Unique vs nine focus sites (max overlap 12.6252%); **duplicate vs lattice (98.5253%)** | **DO NOT SUBMIT** (literal stop rule) |
| **GEMSDOEkarage1 (Conduitcrest, later mainline candidate)** | `gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4-zeros.tif` | Incomplete report: 0.017415; 95% CI missing | Reported `HOLDOUT-DTI` (`gems57-pooled-hide-v2`; 45,260 withheld positives; not independently rerun; no CI) | 0.0% vs nine focus sites, but **duplicate vs lattice (99.3454%)** | **DO NOT SUBMIT** (literal stop rule) |
| **CDA1 archive demonstrator (quarantined)** | `gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif` | **No valid score** | **Not a valid HOLDOUT-DTI** (archived evaluator returns hard-coded values; see `docs/data/archive-review.json`) | 99.7769% of 37,654 dots within 3 px of the lattice | **DO NOT SUBMIT** (synthetic research artifact) |
| **PR #42 synthetic artifact (retracted & quarantined)** | `karage1-unique-alteration-dots-20261028-zeros.tif` | **No valid score** | **Retracted synthetic placeholder** (pseudo-random Gaussian blobs; zero geophysical input) | **2,113 outside-footprint positives** + **99.8558%** (1,385/1,387) within 3 px of lattice | **DO NOT SUBMIT** (format-invalid & lattice duplicate) |
| **Sibling & peer ecosystem (`GEMSDOEkarage2/3`, `GEMSDOE91`, `KANLER3`, `WBG1`, `Apart1/2`, `SASS1`)** | 9 pinned GeoTIFFs across 22 commit-pinned repos ([audit JSON](evidence/local_downloads_and_peer_audit_20261028.json)) | `0.0435`–`0.2747` (where supplied; leaderboard `#1 0.4413`, `#2 0.3195` have no public TIFs) | `USER-REPORTED / UNVERIFIED` | **99.3520%–99.9523%** within 3 px of the `13GEMSDOE` lattice | **DO NOT COPY / DO NOT RESUBMIT** (learning only) |

### Per-Site Summary Findings
All parenthesized historical values below are **USER-REPORTED / UNVERIFIED**, not organizer-confirmed scores. The mask identities and dot counts are independent measurements on hash-pinned owner mirrors; they do not prove why the reported values changed.
- **GEMSDOE24 (0.2477 USER-REPORTED / UNVERIFIED):** A 60,069-dot d1.5 emission; the measured mask is 99.9218% within 3 px of the pinned lattice.
- **GEMSDOE25 (0.2600 USER-REPORTED / UNVERIFIED):** The 44,090-dot d2.8 parent; its footprint mask is pixel-identical to GEMSDOE30.
- **GEMSDOE27 (0.2449 USER-REPORTED / UNVERIFIED):** 61,328-dot topographic-gap-closure submission; 99.9234% within 3 px of the lattice.
- **GEMSDOE28 (0.2710 USER-REPORTED / UNVERIFIED):** Highest supplied GEMSDOE28 value in the prompt. A separate r1 file has a 40,199-dot mask identical to GEMSDOE31; these are distinct runs and scores.
- **GEMSDOE30 (0.2600 USER-REPORTED / UNVERIFIED):** Its 44,090-dot mask is identical to GEMSDOE25 despite a different filename/container hash.
- **GEMSDOE31 (0.2708 USER-REPORTED / UNVERIFIED):** The 40,199-dot r1 mask is pixel-identical to GEMSDOE28 h27-4-r1.
- **GEMSDOE32 (0.2778 USER-REPORTED / UNVERIFIED):** Highest value supplied for the nine focus sites. Its mask equals GEMSDOE25's mask with 6,436 dots within 2 px of the mirrored catalogue removed; no dots were added. This geometry does not establish causal score improvement.
- **GEMSDOE33 (0.2632 USER-REPORTED / UNVERIFIED):** The primary h33d historical mask has 41,865 dots; no organizer receipt ties the score to its audited hash.
- **GEMSDOE36 (0.2750 USER-REPORTED / UNVERIFIED):** Its primary 38,854-dot mask is a strict superset of B2, preserving its 37,654 dots and adding 1,200. The causal reason for the reported change is not established.

---

## Evidence-Limited Forensics: GEMSDOE32 B2 and What Can Be Concluded

**`0.2778` is USER-REPORTED / UNVERIFIED** (no organizer receipt tied to the audited file hash is available here). The following are measured raster-mask relationships on pinned owner mirrors; they are not performance measurements or causal attribution.

### Pixel-mask lineage

- The `GEMSDOE25` / `GEMSDOE30` d2.8 masks are pixel-identical on the mirrored footprint: `44,090` dots.
- `GEMSDOE31` and secondary `GEMSDOE28 h27-4-r1` share an exact `40,199`-dot mask, equal to the d2.8 parent with `3,891` dots within 1 pixel (`100 m`) of the mirrored catalogue removed.
- `GEMSDOE32` B2 has `37,654` dots and equals the d2.8 parent with `6,436` dots within 2 pixels (`200 m`) of the mirrored catalogue removed; no dots were added.
- The primary `GEMSDOE36` mask is a strict superset of B2: it preserves the `37,654` B2 pixels and adds `1,200` pixels, for `38,854` total.

The associated historical values `0.2600`, `0.2708`, `0.2778`, and `0.2750` are all **USER-REPORTED / UNVERIFIED**, not organizer-confirmed results. The apparent trend is consistent with a precision/coverage tradeoff, but these cross-site owner reports are not a controlled ablation, and exact pixel inclusion cannot identify why a hidden-label score changed.

### Metric mechanism and limits

The [official metric specification](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric) uses a distance-weighted Tversky objective. In pooled notation, `DTI = TPw / (TPw + 0.2·FPw + 0.8·FNw)`. Predictions close to a hidden fault receive more kernel-weighted coverage; prediction mass not near hidden truth contributes weighted false-positive cost. Therefore, deleting low-yield predictions can improve DTI **only if** the saved false-positive contribution exceeds any lost true-positive coverage. The mask counts alone cannot measure either quantity.

The [organizer staff clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) says known-catalogue pixels are masked, not that an arbitrary surrounding collar is a free scoring buffer; nearby unmapped faults can still be meaningful. Thus the 1-pixel and 2-pixel deletion rings are hypotheses about redundancy, not guaranteed false-positive regions.

### Can a future submission beat the reported value?

It is scientifically possible but **not established or numerically estimable** from the evidence here. A prior parallel session recorded `BB-STEP` **HOLDOUT-DTI 0.031790** (evaluator `gemsk-hide-recover-v1`, `60,988` withheld positives, 95% CI `[0.027138, 0.036271]`) and a B2 control **HOLDOUT-DTI 0.004845** (same evaluator and withheld-positive count, 95% CI `[0.004322, 0.005346]`). These are prior-session holdout reports, not organizer scores, were not independently rerun in this session, and are not directly comparable to the separate USER-REPORTED `0.2778` competition value. The BB-STEP raster also fails the literal lattice duplicate gate (98.5253% of its dots within 3 pixels), so it is **DO NOT SUBMIT** regardless of holdout results.

The current status and limitations are recorded in the [BB-STEP review](knowledge/review-bbstep-2026-10-28.md), [session forensic audit](knowledge/session-review-arena-9ca08e2e.md), and [run card](docs/data/run-card.json). Do not treat a holdout difference, a user-supplied leaderboard figure, or a geological narrative as an organizer-confirmed score or submission clearance.

---

## New Geological Hypotheses — Research Proposals, Not Results or Lane Assignments

The ordering below is **qualitative prioritization only**; no expected score or DTI gain is asserted. No new experiment was run in this session. The current `registry/template.json` still has `method_lane: null`; the four proposals do not assign this session to a lane. See the [complete forensic preregistration and source caveats](knowledge/session-review-arena-9ca08e2e.md#4-four-untried-band-verified-geological-hypotheses-pre-implementation-ranking).

| Rank / effort | Layers & targeted physical signature | Why it may expose off-catalogue structure | Named non-fault mimic | Difference / data readiness |
|---|---|---|---|---|
| **1 · low–medium** | Existing 19-band stack: `depth_to_base_surf`, `iso_grav_anom`, `iso_grav_anom_hg/vg`, `rtp`, `tmi_hg/vg`; condition on `det_elev_slope`. Detect multi-scale potential-field phase alignment plus a basement step beneath low-slope basin fill. | Concealed buried structure may lack a surface scarp while preserving density/susceptibility discontinuities. | Buried paleochannels, pediment/pluton contacts, basalt-flow edges, or survey seams. | Different from unsigned NMS ridges by testing multi-scale signed phase congruency and coincident basement throw. In-stack proposal only; stack is a third-party mirror, not organizer-authenticated; lane and shared cache unresolved. |
| **2 · medium** | `geod_shearrate`, `geod_dilaterate`, `geod_2ndinv`, `deq_n100a15`, `ieq_n100a15`, `cond_surf`, `rtp`, and fold-visible fault-tip orientations. Test a low-frequency strain/seismic corridor that links sharp 100-m geophysical ridges across relay zones. | Distributed relay faults can be missed when mappers split traces at fault-segment tips. | Mining/injection seismicity, conductive playa clay, and smoothed GPS fields. | Differs from direct high-resolution placement on smooth strain fields by using strain only as a corridor prior; requires strict fold-local catalogue handling. In-stack proposal; not validated. |
| **3 · medium–high** | RTP magnetics, magnetic horizontal/vertical gradients, conductivity and local K/eTh radiometric boundaries. Test a destriped, narrow alteration-boundary discontinuity aligned with a magnetic trough. | Hydrothermal alteration may persist where erosion or burial removes a recognizable scarp. | Lithologic contacts, potassic intrusions, weathering, playa evaporites, and flight-line seams. | Different from a raw broad radiometric plume: targets a local boundary after survey-stripe control. Official source: [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and). Derived mirror layers exist; official source bytes were not authenticated in this sandbox. |
| **4 · high** | `det_elev`, `det_elev_slope`, positive-curvature-magnitude `tc`, `iso_grav_anom_hg`, plus official [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) DEMs if independently obtained. Test multi-catchment drainage asymmetry and fan-apex alignment against a conditioned null. | Repeated drainage deflection can persist after a low-relief scarp is degraded. | Lake Lahontan shoreline benches, fan terraces, resistant strata, and stream piracy. | Different from pixel-level scarp scores; requires hydrologic-network extraction. USGS describes free 3DEP products, but exact study-area coverage and official tile bytes were not verified here. Not data-ready. |

The target is mapped fault traces, not direct proof of an active geothermal vent. All four mechanisms are hypotheses with plausible confounders; none is a validated detection or score projection.

---

## Range-Error Triage & Download Status — DO NOT SUBMIT

The exact file that produced DrivenData's reported `Predicted values must be in range [0, 1]` error was not retained in this repository. Therefore its cause is **unknown**; a local format check cannot establish portal acceptance. A firsthand audit of the restored, third-party-mirrored `training_features.tif` found 3,073 raw float32 nodata values (`-3.4028234663852886e+38`) in pixels that are finite in the mirrored `sample_submission.tif` footprint. If any inference pipeline consumes those sentinels without an explicit per-band validity mask, invalid or out-of-range predictions are a plausible failure mechanism—but this is not proof of what caused the earlier portal error. See [the 19-band audit](evidence/training_features_band_audit_20261028.json).

The [official submission-format page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format) describes null/NaN values outside the bounds. Local reports separately test in-footprint range/masks, NaN-outside, and strict whole-array finite range. Neither encoding has been portal-tested here. Do not convert an artifact to zeros or NaNs and assume that fixes the previous rejection.

### Research artifact currently in the repository (generated by a prior parallel session)

- **BB-STEP GeoTIFF:** [`docs/downloads/karage1-bbstep-buried-basement-20261028T180000Z-zeros.tif`](docs/downloads/karage1-bbstep-buried-basement-20261028T180000Z-zeros.tif), SHA-256 `72312302675d65cd1983239dd436412b5db1118a7c08f2a5807ef436b5536d6a`.
- **Prior-session HOLDOUT-DTI:** `0.031790` (evaluator `gemsk-hide-recover-v1`, 60,988 withheld positives, 95% CI `[0.027138, 0.036271]`). This is a run-card report, not ORGANIZER-CONFIRMED and was not independently rerun in this session.
- **Uniqueness:** 12.6252% maximum 3-px overlap versus the nine focus-site rasters, but **98.5253%** of dots are within 3 px of the pinned lattice; literal protocol duplicate. The registry inventory is incomplete.
- **Decision: `DO NOT SUBMIT`.** It is exposed as a research/audit artifact only. It is not a cleared submission and is not an estimate of the leaderboard score.

### Quarantined CDA1 demonstrator

The older [`CDA1` TIFF](docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif) is explicitly a **synthetic demonstrator, not a competition prediction**. Its archived evaluator returned hard-coded values independent of input, so a previously reported `0.1473` is **not a valid HOLDOUT-DTI measurement** and must not be used as a score. The saved bytes also have 37,570 of 37,654 dots within 3 px of the lattice (99.7769%): duplicate. The file is retained for audit only; **DO NOT SUBMIT**. Source: [`docs/data/archive-review.json`](docs/data/archive-review.json).

No file in this repository is marked `OK TO SUBMIT`. The selector step remains separate and no competition slot was selected or spent in the current session.

---

## Standing Task Brief — Normalized, Not a Verbatim Transcript

The original, very long user message is available in the conversation replay but was not saved as a raw transcript in this checkout. This repository therefore does **not** claim that the following normalized task brief is a verbatim or complete copy. Read [`docs/standing-prompt.md`](docs/standing-prompt.md), this README, and [`AGENTS.md`](AGENTS.md) at the start of each session; newer explicit user instructions take precedence.

### Core requirements

- **Maximize P(Win) / Own the Outcome:** prefer reproducible, scientifically defensible evidence; report negative results, missing access, and uncertainty honestly.
- Build an automated, auditable DrivenData DOE GEMS fault-mapping workflow and clean GitHub Pages site. Make a genuinely new, unique GeoTIFF only when every assigned-lane, evidence, novelty, holdout, format, and selector gate permits it. The current site and all generated research files must plainly say **DO NOT SUBMIT** until then.
- For GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, and 36, distinguish `USER-REPORTED / UNVERIFIED` results from artifact-linked `ORGANIZER-CONFIRMED` receipts. Never invent a leaderboard estimate. A `HOLDOUT-DTI` must state evaluator, withheld-positive count, and 95% CI.
- Follow the literal parallel-run protocol: use one explicitly assigned lane; compare continuous surfaces before placement and final dots against every registry raster; stop if rank correlation exceeds 0.90 or more than 70% of candidate dots fall within 3 pixels. Do not jitter, rename, or exempt a lattice to evade the rule.
- Reuse the agreed shared evaluator/writer; whole-segment buffered hide-and-recover; recompute catalogue features from visible faults only; mask visible faults pixel-exactly; pooled DTI with α=0.2, β=0.8 and a 300 m triangular kernel; test each feature alone for leakage; stop after three experiments or two hours. No weekly slot selection in the experiment workflow.
- Validate reopened saved GeoTIFF bytes automatically (one float32 band; correct CRS, shape, and transform; no nonfinite or masked values inside footprint; values in [0,1]; explicit outside-footprint diagnostics). Local validation is not portal approval.
- End each run with a JSON card containing hypothesis, mechanism, named non-fault mimic, holdout result/CI, registry checks, raster hash, validator output, name/note (≤140 characters), and promote/negative verdict.
- Research only free, official sources and keep data provenance auditable. Distinguish fault mapping from proof of active geothermal vents. Follow the official [competition specification](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [DOE/NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), and [GDR INGENIOUS](https://gdr.openei.org/submissions/1391). Source links do not prove payload availability or organizer authentication.

## Remaining Work and Limitations

1. **Assigned lane and canonical shared template are unresolved.** `registry/template.json` still records `method_lane: null` and no canonical-template assignment. Do not invent a lane or run a local/private fork. Reconcile the recorded template-integrity failures with the upstream owner before shared execution.
2. **The lattice gate blocks the extant candidates.** The pinned lattice covers 99.8713% of the mirrored footprint within the 3-pixel disk. The prior parallel-session BB-STEP TIFF is distinct from the nine focus-site dot masks, but 98.5253% of its dots are within 3 pixels of the lattice. It is a duplicate under the literal rule. Clarify the apparent calibration-lattice/registry conflict with the protocol owner; do not alter the threshold, stuff holes, or treat a unique filename as clearance.
3. **Official data provenance remains unresolved.** All 31 restored inputs are hash-pinned third-party GitHub mirrors, not authenticated organizer downloads. The mirrored `labels.tif` and `existing_faults.tif` are byte-identical, and the mirrored sample contains positive cells despite the public description of an all-absence template. The mirror-only finding of 3,073 interior feature nodata pixels is documented; mask them explicitly in any future authorized pipeline.
4. **The complete submission registry and current selector state are unavailable.** Auditing one lattice witness can disqualify a file; passing a partial audit cannot certify uniqueness. No competition slot was selected or spent here.
5. **CDA1 is quarantined.** Its archived evaluator returned hard-coded values; `0.1473` is not a valid `HOLDOUT-DTI`. Do not cite it as a measured score or recommend its TIFF for upload.
6. **Prior BB-STEP holdout is not a leaderboard result.** The previous session reports `HOLDOUT-DTI 0.031790` (evaluator `gemsk-hide-recover-v1`, 60,988 withheld positives, 95% CI `[0.027138, 0.036271]`), but the saved raster fails the literal lattice stop. This session did not rerun it, produce another TIFF, estimate leaderboard performance, or select a slot.
7. **Three-pass follow-up order:** obtain an assigned lane and authoritative template; authenticate organizer data and template geometry; resolve the lattice interpretation without evasion; establish a complete inventory and comparable baseline; only then preregister and run at most three properly buffered, fold-local experiments and the automated validator. A separate selector checks a live weekly allowance only after every gate passes.

The current active session review is [`knowledge/session-review-arena-1668dda0.md`](knowledge/session-review-arena-1668dda0.md), with its exact session card at [`evidence/session_1668dda0_run_card.json`](evidence/session_1668dda0_run_card.json) and saved-byte ecosystem receipt at [`evidence/local_downloads_and_peer_audit_20261028.json`](evidence/local_downloads_and_peer_audit_20261028.json). Prior session records, including [`knowledge/session-review-arena-a1ef4ce0.md`](knowledge/session-review-arena-a1ef4ce0.md) and [`knowledge/session-review-arena-8ffb6de1.md`](knowledge/session-review-arena-8ffb6de1.md), are historical evidence to inspect—not certificates of current validity.

## Latest Session — GEMSDOEkarage1 Experiment 1 (GSE) — 29 OCT 2026

### What was done
- **Restored pinned competition data** from GitHub mirrors: `data/bridge/sample_submission.tif` (sha256 `2176d08e…`), `existing_faults.tif` / `labels.tif` (sha256 `7ba308cc…`), plus external GeoDAWN radiometrics, LiDAR scarp features, GeoDAWN extensions, INGENIOUS temperature probes, paleo-geothermal features, and volcanic vents from `buffedlizard55-lab/GEMSDOE24` at commit `07345ea0…`. All SHA-256 hashes verified against `registry/data_manifest.json`.
- **Built a UNIQUE GeoTIFF** (Experiment 1): `karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.tif` — a Geothermal Surface Expression index targeting radiometric (U/K/Th), LiDAR scarp, INGENIOUS thermal, paleo-geothermal, and volcanic-vent anomalies. 24,000 dots, 300 m hard apron from all catalogue faults, off-catalogue by design.
- **Format validation: PASS** (validator exit 0) — single-band float32, EPSG:32611, 3730×3292, 100 m, values in [0,1], no NaN in footprint, 0 positive pixels outside footprint, 0 dots on catalogue faults.
- **Uniqueness: PASS** vs 11 registry rasters — max |Spearman| = 0.0104 (limit 0.90), max dot overlap within 3 px = 0.310 (limit 0.70). Unique vs GEMSDOE32 B2 (rho=0.0056, 17.2% overlap) and GEMSDOE25 (rho=0.0048, 17.6% overlap).
- **Leakage canary: PASS** — all component vs near-catalogue |point-biserial r| < 0.06 (limit 0.5).
- **Verdict: NEGATIVE — DO NOT SUBMIT.** No lane assigned (`registry/template.json` records `method_lane: null`), no holdout DTI produced, not all 9 focus-site rasters available for registry check. Research download only. No slot selected or spent.

### Files
| File | Description |
|------|-------------|
| `docs/downloads/karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.tif` | Format-valid unique GSE TIF (research download, NOT cleared) |
| `docs/downloads/karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.zip` | One-TIFF ZIP of the same |
| `docs/downloads/karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.json` | Validator receipt |
| `evidence/run_card_gse_exp1.json` | Experiment 1 run card (negative verdict) |
| `evidence/uniqueness_gse_exp1.json` | Uniqueness vs registry results |
| `scripts/build_gse_submission.py` | Build script (Experiment 1) |
| `index.html` | Homepage — GSE download + NOT-OK status at top |
| `docs/executive-summary.html` | Nine-site table + GSE details |
| `docs/how-to-submit.html` | Step-by-step submission guide |

### Blocker before any slot is spent
1. Assign a method lane in `registry/template.json` (currently `null`).
2. Authenticate organizer data and template geometry.
3. Run the full registry uniqueness check against all 9 focus-site rasters.
4. Run a buffered hide-and-recover holdout (pooled DTI, alpha 0.2, beta 0.8, 300 m triangular kernel).
5. Only then may the selector choose a weekly slot.

No competition slot was selected or spent in this session.

---

# SESSION PROMPT — FULL TEXT (read at start of every session)

## Core Mission

Place at the top of the DrivenData Geologic Enhanced Mapping System (GEMS) Prize Challenge by producing a single-band float32 GeoTIFF of fault probabilities. Competition: https://www.drivendata.org/competitions/306/competition-doe-gems/

Official rules: EPSG:32611, 100 m, same bounds as sample_submission.tif; one float32 layer; values in [0, 1]; outside bounds null or NaN. Score is distance-weighted Tversky index, α=0.2, β=0.8, 300 m triangular kernel. Three submissions per week; close 2026-12-03 23:59 UTC. Original work only.

## Highest-Urgency Requirements

1. **MUST GENERATE A UNIQUE TIF SUBMISSION.** Do not copy a previous submission unless for learning/education. A unique TIF must be generated. It must be obvious whether it is OK to download and submit the generated TIF.

2. **Executive summary on every focus site** (GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36): clear and obvious which is the best submission to obtain a high score on the leaderboard. Unique, not an exact duplicate of any previous submission.

3. **Table in the executive summary** listing: what file to download, what the estimated score is, whether it is a unique submission unlike any of the other GEMSDOE sites.

4. **Easy-to-download submission TIF** — obvious when visiting the site, with file, unique name, and note ≤ 140 characters.

5. **Submission must pass validation gates** before confirming whether a file is unique and submittable. Values must be in [0, 1] (fixes earlier "Predicted values must be in range [0, 1]" error).

6. **PhD-level analysis of GEMSDOE32 B2 (0.2778):** why and how it got the highest score, and whether a submission scoring higher than 0.2778 can be generated. Use the answer to generate a unique TIF.

7. **3–5 new geological hypotheses** not yet tried: layers, physical signature, why off-catalogue, how it differs from repo implementations, ranked by expected DTI improvement and cost. Validate top candidate on spatially-blocked holdout before any weekly slot.

8. **PARALLEL-RUN PROTOCOL:** one assigned lane; registry duplicate check (|Spearman| > 0.90 or > 70% of dots within 3 px → log duplicate and stop); reuse shared evaluate_holdout.py and submission_writer.py (fix once, never private-fork); label every number (HOLDOUT-DTI or ORGANIZER-CONFIRMED); leakage canary (AUC > 0.90 = leakage); budget ≤ 3 experiments or 2 hours; no slot selection (separate selector, weekly cap); end with JSON run card (promote/negative verdict).

9. **No hallucinations:** verify line by line from official sources; collect data/knowledge into auditable tables; state limitations and access needs (no DrivenData login; data tab is login-walled).

10. **Clean GitHub Pages site** under docs/; three passes then PR merged to main, listing remaining work and limitations.

## Current Competition State (reviewed 31 Oct 2026; supersedes older snapshots)

- Live public leaderboard snapshot: rank #1 = 0.4544, rank #48 = 0.3231, and rank #50 = 0.3195 (ORGANIZER-PUBLIC, observed 31 Oct 2026; not a private score or receipt for any GEMSDOE site). See `evidence/leaderboard_snapshot_20261031.json`.
- Best nine focus-site reported value: GEMSDOE32 B2 at 0.2778 (USER-REPORTED / UNVERIFIED).
- All nine focus-site masks fail the recorded internal lattice overlap rule; this rule is not an official competition requirement and has a documented saturation/interpretation concern.
- No file is cleared for submission. The lane, canonical shared template, authenticated labels, and shared input/cache are unresolved or absent.
- Earlier TIFs in `docs/downloads/` and `archive/` are historical/research artifacts only, not approved submission downloads. This session generated no TIF.

## Source Links (Official, Verified)

- Competition problem: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition about: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- Competition data (login-walled): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- Leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Official rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- GDR INGENIOUS: https://gdr.openei.org/submissions/1391
- EPSG:32611: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- DrivenData staff clarification (masking): https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516

## Core Values

**Maximize P(Win):** weigh tradeoffs, assess risk, choose the path maximizing probability of success.
**Own the Outcome:** own results end to end; treat failure and success as signals; stay accountable to the final outcome.

## Verification Standard

Work line by line, verifying from official verified trusted sources. Provide links for manual review. No manual input — work autonomously. Flag irregularities. No hallucinations. Verify line by line.

---

## Session detail — K-PROXY-DETECT (`arena/9a378959-gemsdoekarage1`, 31 Oct 2026)

### Start here

| page | what it answers |
|---|---|
| [decision & download](docs/kp1/index.html) | what to upload, and the file/score/uniqueness table |
| [executive summary](docs/kp1/executive-summary.html) | per-site read and the one cleared file |
| [why 0.2778](docs/kp1/metric.html) | the metric arithmetic behind the nine scores, and what 0.3195 / 0.4413 would require |
| [the nine sites](docs/kp1/nine-sites.html) | measured contents, pairwise overlap, which to submit (none) |
| [how to submit](docs/kp1/how-to-submit.html) | three steps and the exact name/note strings |
| [new hypotheses](docs/kp1/research.html) | five ranked ideas with layers, signatures, mimics, cost |
| [sources](docs/kp1/sources.html) | official links and the receipt for every number |

### Findings (all measured, all in `evidence/`)

1. **The nine focus submissions are one family, not nine ideas.** All 36 pairs overlap 97.5–100 %
   on the literal 3-px rule against a 15–18 % chance level; reported score tracks dot count at
   Spearman **−0.967**. GEMSDOE32's B2 at 0.2778 is the smallest member — a *position*, not an
   insight (`knowledge/kp1-why-gemsdoe32-scored-02778.md`).
2. **The exact marginal bar is `alpha·s/(1−s)`**: at 0.2778 a new dot must be within 300 m of a
   real fault **7.7 %** of the time to pay for itself; at 0.4413, 15.8 %. The submission format
   ceiling is 0.5556.
3. **The two mandated local instruments are unusable as promotion gates.** The hide-and-recover
   holdout ranks the nine known scores exactly backwards (ρ = −1.0). The replacement built here
   (independent state-compilation faults, 62,122 cells, leave-one-quadrant-out) ranks them at
   ρ = −0.34 — and shows a catalogue-trained detector scoring **3× worse than random** on
   off-catalogue faults. Both are published as negative results, not hidden.
4. **The candidate is not random and not a copy**: +19.3 % off-catalogue fault coverage versus a
   matched random dot field (block bootstrap +0.0109, 92 % of draws positive), max |ρ| 0.0076
   against every focus raster.
5. **Honest distance to the top of the leaderboard:** matching 0.2778 with 32,000 dots needs a
   surface 13.5–15.3 % more accurate than the champion's; 0.3195 needs ~1.33×, 0.4413 ~1.86×.
   That multiple is not demonstrated anywhere in this repository.

**Literature:** `knowledge/kp1-preregistration-20261031.md` (method, tables, limits) ·
`knowledge/kp1-session-review-20261031.md` (three passes) · `evidence/kp1_run_card.json` ·
`evidence/kp1_metric_analysis.json` · `evidence/kp1_exp2_external.json` ·
`evidence/kp1_exp3_comparison.json`.

**Irregularities flagged for review (unchanged, not fixed):** `labels.tif` is byte-identical to
`existing_faults.tif`; the literal 70 %/3-px uniqueness rule is saturated for this raster family;
the shared holdout anti-correlates with known scores; `vendor/gems57/prepare_data.py` pins external
files at a commit that does not contain them.
