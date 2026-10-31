# Session review · `arena/8e91c377-gemsdoekarage1` · 31 Oct 2026

**Verdict: NOT CLEARED. Nothing in this repository is OK to download and submit.** The new candidate is unique against the nine focus files and format-valid, but it fails the literal lattice duplicate gate, which is an owner decision. No submission slot was selected or spent.

Evidence labels: **HOLDOUT-DTI** = our catalogue hide-and-recover proxy; **ORGANIZER-PUBLIC** = public leaderboard row from the 30 Oct snapshot (not re-fetched); **ORGANIZER-CONFIRMED** = none exists in this repository; **USER-REPORTED** = supplied in the request, no receipt; **MEASURED** = geometry on local mirror files, not a score.

## 1. Executive summary (nine focus sites)

Full table: `evidence/nine_site_executive_20261031.json` and the site front page.

| Site | File to download | Score (label) | Estimated leaderboard score | Unique vs other focus sites? | OK to submit? |
|---|---|---|---|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-…-nan.tif` | 0.2477 (USER-REPORTED) | NOT ESTIMABLE | **No**: pair overlap 100% (either direction) with GEMSDOE25 (MEASURED) | No |
| GEMSDOE25 | `d28.tif` | 0.2600 (USER-REPORTED) | NOT ESTIMABLE | **No**: exact mask match with GEMSDOE30 | No |
| GEMSDOE27 | `topo-gap-closure-…-nan.tif` | 0.2449 (USER-REPORTED) | NOT ESTIMABLE | **No**: pair overlap 100% (either direction) with GEMSDOE24 | No |
| GEMSDOE28 | `h36-1-rung30-blind-…-nan.tif` | 0.2710 (USER-REPORTED) | NOT ESTIMABLE | **No**: pair overlap 100% (either direction) with GEMSDOE24 | No |
| GEMSDOE30 | `d28-poisson300m-offcat-…tif` | 0.2600 (USER-REPORTED) | NOT ESTIMABLE | **No**: exact mask match with GEMSDOE25 | No |
| GEMSDOE31 | `h27-4-solo-d28-…-nan.tif` | 0.2708 (USER-REPORTED) | NOT ESTIMABLE | **No**: pair overlap 100% (either direction) with GEMSDOE24 | No |
| GEMSDOE32 | `GEMSDOE32_B2` (B2) | **0.2778 (USER-REPORTED, highest focus value)** | NOT ESTIMABLE | **No**: pair overlap 100% (either direction) with GEMSDOE24 and GEMSDOE25 | No (already listed; re-upload is not a new candidate) |
| GEMSDOE33 | `h33d-analog-tip-stepover-…tif` | 0.2632 (USER-REPORTED) | NOT ESTIMABLE | **No**: pair overlap 99.98% (either direction) with GEMSDOE32 | No |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-…-zeros.tif` | 0.2750 (USER-REPORTED) | NOT ESTIMABLE | **No**: pair overlap 100% (either direction) with GEMSDOE32 | No |

Reading the uniqueness column: under the protocol's >70% rule applied in **either direction**, **none** of the nine focus files is unique against the others. This is a measured fact. The table's rule is stricter than the protocol's literal one (forward only); the candidate below is checked the literal way.

**Estimated leaderboard score: NOT ESTIMABLE for every row.** There is no organizer receipt and no calibrated mapping from our holdout to the hidden labels. The holdout random-placement control is 0.0773 HOLDOUT-DTI, so the holdout scale is not the leaderboard scale.

**New candidate (research file, NOT CLEARED):** `docs/downloads/karage1-h31-visgrad-nms3px-40k-20261031-zeros.tif` (SHA-256 `4221236752e703ec035b4d4245d23dbb0cf2b1126f8cb6040e810316be1d738a`, 40,000 dots, 282,359 bytes).
- Holdout (HOLDOUT-DTI): **0.1143, 95% CI [0.0918, 0.1364]**; random control 0.0773 [0.0742, 0.0799]; paired gain +0.0371 [+0.0154, +0.0590]. Preregistered verdict PASS_HOLDOUT_ONLY.
- Post-hoc buffer-20 sensitivity (HOLDOUT-DTI, not preregistered): 0.1254 [0.1014, 0.1491]; paired gain +0.0498 [+0.0256, +0.0739].
- Leakage canary: max single-feature AUC 0.6266 (limit 0.90). Pass.
- Validator (saved bytes): pass; 0 NaN, values in [0,1], 0 dots outside footprint, 0 dots on catalogue.
- Uniqueness vs nine focus rasters: pass. Max forward 3 px overlap 0.380 (GEMSDOE27); max |phi| 0.022.
- Surface check (model surface vs every registry raster): max |Spearman| 0.0706. Pass.
- **Lattice gate: FAIL.** Forward 3 px overlap with the 13GEMS lattice probe = **0.9975** (limit 0.70).
- Independent saved-byte cross-check (`scripts/audit_h31_saved_bytes.py`): agrees with the runner to 4 decimals; all format and focus checks pass; lattice fails.

## 2. Why GEMSDOE32 B2 (0.2778, USER-REPORTED) is the highest focus value

**MEASURED:** B2 is a strict subset of D2.8 (GEMSDOE25): 37,654 dots of 44,090. The 6,436 removed dots are all within 2 px of the mirrored catalogue (3,891 at 1 px, 2,545 at 1–2 px, 0 beyond 2 px). B2 has no dot within 2 px of the catalogue. That is the whole measured difference (`evidence/focus_nine_audit_20261031.json`, `b2_vs_d28`).

**Mechanism (derived from the vendored metric; not measured against truth):** DTI = TP / (TP + 0.2·FP + 0.8·FN) with a 3 px triangular kernel. Because 1 − β = α, a dot with marginal credit k improves DTI only if **k > 0.2·DTI**. At DTI ≈ 0.28 that means the dot's nearest truth must lie within about 2.8 px. A dot 1–2 px from a mapped trace earns credit only if an unmapped fault abuts that trace. B2 removes 6,436 such dots (14.6% of D2.8). The user-reported gain of +0.018 over D2.8 (0.2600) is consistent with that trade, if the removed dots carried little hidden-truth credit.

**What we cannot say:** whether the removed dots had little credit. Hidden truth is not available, so the +0.018 is a user report, not a measurement. Our holdout buffer removes all abutting truth by design, so this repository cannot test the trade-off (see H-A1).

## 3. Can a higher score be achieved? (honest answer)

Possibly, but nothing here shows it. The only validated improvement is the H-V31 holdout gain over random, which is measured on a proxy. Its leaderboard effect is unknown. The leaderboard leader is 0.4544 (ORGANIZER-PUBLIC); the target 0.3195 (rank 48) is above every USER-REPORTED focus value (highest 0.2778), a re-upload of an existing focus file would reproduce its existing value, so reaching 0.3195 needs a new file, and no new file has an organizer score. Beating 0.3195 requires an organizer-scored submission, and the lattice gate blocks every dotted candidate from being submitted under the literal rule.

Hypotheses, ranked by expected DTI gain and cost, are in `knowledge/hypotheses-8e91c377-20261031.md`. Top: H-P1 (credit-aware dot budget, cheapest, no new data), then H-B1 (buried basin-bounding faults via depth-to-basement), then H-A1 (catalogue-adjacent truth, highest value but needs a holdout-design decision). All are **not run**: the experiment budget (3) is spent.

## 4. Multi-pass review record

**Pass 1 (implement).** H-V31 runner, preregistration written before the holdout, holdout run, final candidate build, post-hoc sensitivity run.

**Pass 2 (review for bugs and requirement fit).** Defects found and fixed in this pass:
1. `evidence/focus_nine_audit_20261031.json` contained a NaN (nodata of float32 raster), which is not strict JSON and failed `tests/test_site.py::test_evidence_strict_json`. Fixed in `scripts/focus_nine_audit.py` (NaN → null), audit re-run (exit 0), same numbers.
2. The new candidate TIF had no saved-byte audit receipt, which failed two coverage tests. Added `scripts/audit_h31_saved_bytes.py` (independent re-read, dilation-based overlap). It is a real audit, not a placeholder receipt. The existing `scripts/audit_local_tif.py` could not run (requires `.cache/gems_data`, absent) and depends on the hash-mismatched vendored uniqueness module, so it was not used.
3. The holdout scores 60,593 of 60,988 catalogue pixels. The 395 unscored pixels belong to segments whose centroid is in another quadrant. Not a leak, but an edge effect, now recorded as a deviation.
4. Fold 1 is a loss to random at both buffers (0.0637 vs 0.0759; tie at buffer 20). Recorded, not hidden.
5. The sites table uses a stricter (two-direction) uniqueness rule than the candidate check (forward only, literal). Both are reported; neither changes a verdict.

**Pass 3 (re-check against the request).** See section 5.

## 5. Requirement check

| Requirement | Status |
|---|---|
| Executive summary for 9 sites: file, estimated score per protocol, uniqueness | Done (section 1; site front page). Estimate: NOT ESTIMABLE, with reason. Uniqueness: all nine fail against siblings (measured). |
| Unique downloadable GeoTIF, not a duplicate of prior submissions | Done for the file (unique vs the nine focus files and prior candidates measured). Gate status: NOT CLEARED. |
| Obvious whether OK to submit | Yes: **NO**, on every page and in the run card (`ok_to_submit: false`). |
| Validation gates without human intervention | Scripted: validator, saved-byte audit, uniqueness, surface check, canary. Lattice gate fails and blocks. Owner decision needed (section 6). |
| Explain B2 0.2778 and whether a higher score is achievable | Section 2 and 3. Labeled. |
| 3–5 untried hypotheses, ranked by DTI gain and cost | Done: five, `knowledge/hypotheses-8e91c377-20261031.md`. |
| Validate top candidate on spatially blocked holdout before any slot | Done (H-V31, PASS_HOLDOUT_ONLY). No slot used. |
| Target beat 0.3195; ideally 0.4544 | **Not demonstrated.** No organizer receipt. Cannot be shown from this repo. |
| Prompt in README and read every session | Added to README (section below the current block). |
| Live submission page and executive summary at top of the site | Added to `index.html`, `docs/index.html`, `docs/executive-summary.html` and `docs/how-to-submit.html` (see section 7). |
| PR and merge to main | Pending (done after this review is committed). |
| Remaining work and limitations | Section 6 and 7. |
| Multi-pass review | Section 4. |
| Labels on every number | HOLDOUT-DTI / ORGANIZER-PUBLIC / ORGANIZER-CONFIRMED / USER-REPORTED / MEASURED. |
| JSON run card per parallel-run protocol | `evidence/run_card_h31_20261031.json`. Verdict: negative. |
| Stay in lane; no slot selection | Yes. |
| Budget 3 experiments or 2 hours | 3 of 3 used: E1 audit, E2 holdout, E3 buffer-20 sensitivity (post hoc). The saved-byte audit and the sites builder are verification, not experiments. |
| Keep "Maximize P(Win)" and "Own the Outcome" as focal values | Kept in the README prompt section. |
| Use modern OOXML for any Office deliverable | No Office deliverable was produced. |

## 6. Owner decision (blocks any submission)

**Lattice gate.** The literal rule says a dotted raster with more than 70% of its dots within 3 px of any registry raster is a duplicate. The 13GEMS covering lattice (206,895 dots, about 5 px spacing) is within 3 px of about 99.87% of footprint cells, so **every** dotted raster on this grid exceeds 70% against it (measured on all nine focus files; 0.9991–0.9992). Two readings:
- (a) Apply the rule literally: no dotted file can be submitted, and the protocol's stop rule holds. The candidate stays NOT CLEARED.
- (b) Treat the lattice probe as a covering grid, not a submitted raster, and decide the threshold for it explicitly. Under (b) the candidate would need its own sign-off. Dots in lattice holes must not be used to evade the rule.

No submission is made until the owner chooses. Nothing in this repository makes that choice.

## 7. Remaining work and limitations

Remaining work:
1. Owner decision on the lattice gate (section 6).
2. Organizer-authenticated data: the mirror is hash-consistent but not authenticated. The reference notebook names `numeric_features.tif`, the mirror is `training_features.tif` (see `knowledge/official-sources-20261031.md`).
3. Re-fetch the leaderboard when reachable. The 30 Oct snapshot is the only leaderboard value used.
4. Next experiment only after preregistration: H-P1 (dot-budget sweep), then H-B1.
5. Restore `submission_writer.py` and `uniqueness.py` from a source that matches their pins, or formally retire them; both are hash-mismatched.

Limitations:
- No organizer receipt for any file. No leaderboard estimate exists for any row.
- Catalogue holdout, not organizer labels. Its values are not comparable to leaderboard values.
- Random control is strong under this metric (0.0773 HOLDOUT-DTI).
- Buffer design prevents testing catalogue-adjacent truth (H-A1).
- Official DrivenData, NLR, USGS, OpenEI, EPSG and Wikipedia pages could not be fetched from the sandbox. Manual-review links are in `knowledge/official-sources-20261031.md`.

## 8. Files

- Candidate: `docs/downloads/karage1-h31-visgrad-nms3px-40k-20261031-zeros.{tif,zip,sha256}` — NOT CLEARED.
- Run card: `evidence/run_card_h31_20261031.json`.
- Evidence: `evidence/focus_nine_audit_20261031.json`, `evidence/h31_holdout_20261031.json`, `evidence/h31_holdout_20261031_buffer20_posthoc.json`, `evidence/h31_final_20261031.json`, `evidence/audit_h31_candidate_saved_bytes_20261031.json`, `evidence/nine_site_executive_20261031.json`.
- Preregistration: `knowledge/preregistration-h31-visgrad-20261031.md`.
- Hypotheses: `knowledge/hypotheses-8e91c377-20261031.md`. Sources: `knowledge/official-sources-20261031.md`.
