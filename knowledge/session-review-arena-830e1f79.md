# Session review · `arena/830e1f79-gemsdoekarage1` (31 Oct 2026)

**Verdict: NEGATIVE / DO NOT SUBMIT. No file is cleared. No new GeoTIFF was generated.**

This session re-read the repository, the official rules, the live leaderboard, and the nine focus-site evidence. It did not generate a new raster, because every dotted candidate the repo has produced fails the team's own duplicate gate, and this session found no change to that gate's status (see §3). A new file that fails the gate would still be a duplicate by the protocol, so producing one would add a file, not a clearance.

## 1. Verified facts (line by line, with links)

| # | Claim | Source (checked this session) | Status |
|---|---|---|---|
| F1 | Metric is a distance-weighted Tversky index, α=0.2, β=0.8, triangular kernel R=300 m (3 px at 100 m). | [DrivenData problem page, "Performance metric"](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | VERIFIED (fetched 31 Oct 2026) |
| F2 | Submission: single-layer `float32` GeoTIFF, EPSG:32611, 100 m, same bounds as training data, **"data outside the bounds is null or nan"**, in-bounds values **"between 0 and 1"**. | [DrivenData problem page, "Submission format"](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | VERIFIED (fetched 31 Oct 2026) |
| F3 | Official rules: single GeoTIFF, single layer, 100 m, entire GeoDAWN study area; three submissions per week; one final submission chosen before the deadline. | [NLR Official Rules, §3.2 and §3.4](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | VERIFIED (fetched 31 Oct 2026) |
| F4 | The official rules and problem page contain **no uniqueness or duplicate-of-other-entrant rule**. The 70 % / 3-px gate and the 0.90 Spearman gate are the team's internal protocol. | Same two documents (read in full for the submission and scoring sections) | VERIFIED by absence; the protocol itself is the user's instruction |
| F5 | Two-round scoring: Initial Prize Round uses a private set; Final Prize Round rescoring uses an expanded label set that includes faults that experts verify from submissions. | [DrivenData problem page, "Competition structure"](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | VERIFIED |
| F6 | Official rules §3.2 requires an **indication of generative-AI use in the narrative** for any submission. | [NLR Official Rules, §3.2](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | VERIFIED. Any future submission must carry this disclosure. |
| F7 | Live leaderboard: **#1 = 0.4544**; **0.4413 does not appear in ranks 1–50**. | [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) (fetched 31 Oct 2026, all three chunks) | ORGANIZER-PUBLIC |
| F8 | Live leaderboard: **0.3195 is at #50**, not #48 as the 30 Oct snapshot says. Ranks #46 = 0.3261, #47 = 0.3244, #48 = 0.3231, #49 = 0.3217, #50 = 0.3195. | Same page, chunks 1–2 | ORGANIZER-PUBLIC · **IRREGULARITY I-1** (see §5) |
| F9 | GEMSDOE32 page: the 0.2778 score is an **"OWNER-REPORT (owner-provided submission-log claim; no submission-page receipt linking this raster hash to the score is present)"** and the file is marked "already submitted - do not resubmit". | [GEMSDOE32 site](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) (fetched 31 Oct 2026) | VERIFIED as a third-party statement; the score is NOT organizer-confirmed |
| F10 | The GEMSDOE32 site's own "OK TO SUBMIT" checklist requires: an explicitly assigned method lane; all feature-only leakage canaries ≤ 0.90; a fold-local holdout win with paired 95 % CI > 0; no SGMC regression; literal surface/dot uniqueness vs every registry raster (Spearman ≤ 0.90, ≤ 70 % within 3 px); exact saved-byte validation; separate weekly-slot selector approval. | Same page | VERIFIED. This repo's gates are the same list. |
| F11 | GEMSDOE32 (0.2778) is GEMSDOE25 with 6,436 dots removed (both within 2 px of labels). GEMSDOE25 and GEMSDOE30 have identical dot masks. | [`evidence/site_lineage_verification_20261029.json`](../evidence/site_lineage_verification_20261029.json) (checks `GEMSDOE32_vs_GEMSDOE25…removed = 6436`; `GEMSDOE25_dots = 44090`; `GEMSDOE32 child_dots = 37654`) | REPO EVIDENCE (SHA-pinned mirrors); not organizer-confirmed |
| F12 | Random-dot null: uniform random dots land within 3 px of the 13GEMS lattice at **99.9 %** for 1,000 / 5,000 / 22,163 / 37,654 dots. The lattice covers **99.87 %** of the footprint. | [`evidence/lattice_saturation_null_20261029.json`](../evidence/lattice_saturation_null_20261029.json), [`evidence/lattice_gate_null_check_20261029.json`](../evidence/lattice_gate_null_check_20261029.json) | REPO EVIDENCE (measured on this repo's rasters) |
| F13 | Test suite: **446 passed, 2 skipped** (both skips need absent competition rasters). | `python -m pytest` in a venv from `requirements.txt` (31 Oct 2026) | VERIFIED locally |

## 2. The 0.2778 question — short answer from verified facts

- **Is 0.2778 a verified score?** No. It is an owner-reported figure. The GEMSDOE32 page itself says no submission receipt links that file hash to the score (F9).
- **What is the file?** A dotted raster with 37,654 positive pixels, the same dot-count as the other focus files. It is a strict subset of GEMSDOE25 (F11): 6,436 dots were removed and 0 were added, so every remaining dot is a GEMSDOE25 dot.
- **Why might a subset score higher?** Under the DTI, removing false positives that sit far from truth lowers the 0.2·FP term, while true positives near truth keep their kernel credit. A file that drops low-value dots can raise DTI without adding new geology. This is a mechanism claim from the metric definition (F1); it is not a measured result for this file.
- **Can we beat 0.2778 with a file we can defend?** Not at present. The repo has no holdout result that would support a higher estimate, and the organizer-confirmed scores are not in the repo (see F7 and §4).

## 3. Why no file is cleared (the honest blocker)

1. **Uniqueness gate is saturated for dotted files.** The lattice null (F12) shows that any random dot set of ≤ 37,654 dots fails the literal 70 % / 3-px rule at 99.9 %. The gate therefore cannot distinguish a new idea from noise. It is a broken test, not a lane-drift test. Owner decision needed (§5, I-3).
2. **No assigned method lane.** The protocol's "method paragraph" is absent from the current prompt. Without a lane, the duplicate and lane rules cannot be applied.
3. **No organizer-authenticated data.** The restore script pulls pinned third-party GitHub mirrors of the login-walled DrivenData files (`registry/karage1_data_manifest.json`). The manifest says a hash match "proves only mirror consistency" and is "NOT organizer-authenticated". No holdout run from this session would therefore be organizer-grade.
4. **Format wording mismatch.** The repo's `-zeros` rasters write zeros outside the footprint; F2 says outside-bounds values must be null or NaN. A `-zeros` file therefore does not match the literal format, even if it passes the other gates. The `-nan` twins match F2 literally.

## 4. What was not done (and why)

- No new TIF, no HOLDOUT-DTI run, no score estimate. Reason: §3(1)–(3). A number from the repo's holdout would be a proxy, not an estimate of the leaderboard score.
- No weekly slot selected or spent. Reason: promotion is a separate selector step and no file has passed its gates.
- No merge decision was made about the upstream H-R1 research file or the older archive. Those are already labelled research-only.

## 5. Irregularities flagged for owner review

- **I-1 (leaderboard rank drift).** Today's live board puts 0.3195 at **#50**, not #48 as the 30 Oct snapshot and the README say. The leaderboard is live and changes; the repo's rank labels must be re-read each session. The prompt's claim that 0.3195 is the "highest score right now" is not supported: the top score is 0.4544.
- **I-2 (0.4413 is not on the board).** The prompt lists 0.4413 as the "current competition leaderboard GEMSDOE high score". It does not appear in the top 50. Treat it as unverified.
- **I-3 (gate saturation).** The 70 % / 3-px rule is failed by random dots (F12). The owner must either (a) replace it with a null-calibrated test, or (b) document that dotted files cannot be cleared under it. Until then no dotted file can be cleared.
- **I-4 (zeros vs NaN).** `-zeros` outputs do not match the literal "outside bounds is null or nan" text (F2). The user's reported "Predicted values must be in range [0, 1]" error is consistent with a NaN/zero-convention mismatch, but the portal's real check is not visible here. This is a hypothesis, not a diagnosis.
- **I-5 (third-party data).** Competition inputs come from third-party GitHub mirrors. Their licence and provenance are not established, and the rules (§3.3, Appendix A) require data to be used under licence. Organizer data should come from the DrivenData download page after login.
- **I-6 (GenAI disclosure).** Official rules §3.2 require a narrative disclosure of generative-AI use. The repo's submission pages should carry that disclosure before any submission. This session found it on some pages but not as a checklist item.

## 6. Next steps (for the next session, in order)

1. Owner decides I-3 (gate ruling) and I-4 (format convention). Without these, no file can be cleared.
2. Owner supplies a method lane, or the protocol's method paragraph.
3. Obtain organizer-authenticated inputs from the DrivenData data page after login. Restore the mirrors only as a fallback, labelled as such.
4. Only then run the holdout (3 experiments / 2 h budget) and the saved-byte validator.
5. Re-read the live leaderboard at the start of each session (rank changes; see I-1).

## 7. Run card

See [`evidence/session_830e1f79_run_card.json`](../evidence/session_830e1f79_run_card.json).
