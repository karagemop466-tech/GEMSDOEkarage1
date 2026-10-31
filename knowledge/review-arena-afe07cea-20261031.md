# Repo review — session `arena/afe07cea-gemsdoekarage1` (31 Oct 2026)

**Verdict: NO FILE CLEARED. No new TIF generated. No submission slot selected or spent.**
This review found one format risk that explains the user's rejection, one clearance contradiction that must be resolved by the owner, and one file (KP1) whose uniqueness is now independently confirmed.

Labels used below: **MEASURED** = computed on bytes checked in this session · **ORGANIZER-PUBLIC** = read from a public DrivenData page · **PROJECTED** = a model projection, not a score · **USER-REPORTED** = supplied by the user, no receipt · **HOLDOUT-DTI** = our catalogue proxy (not the organizer metric).

---

## 1. Executive table — what to download, estimate, uniqueness, OK to submit

| File to download | Estimated leaderboard score | Unique vs the nine GEMSDOE focus files? | OK to submit? |
|---|---|---|---|
| `docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif` (zeros outside) | **PROJECTED 0.2789** (not a score; working range 0.24–0.31, `evidence/kp1_run_card.json`). **Below** the current 0.3195 target and far below the #1 score 0.4544. | **Yes — MEASURED.** Share of its dots within 3 px of a focus file: 23.2% (GEMSDOE32 B2), 24.6% (GEMSDOE25), 25.9% (GEMSDOE24). Spearman < 0.02 vs all three. | **NOT CLEARED by this review.** The repo's own pages contradict each other (§3, item A). Owner ruling required. |
| `…-nan.tif` twins of the focus-style files (7,111,787 NaN cells) | Not estimable | Not the question | **NO.** NaN sits *inside* the raster extent, which the official text does not allow (§2). This is the likeliest cause of the "must be in range [0, 1]" rejection. |
| GEMSDOE24 / 25 / 27 / 28 / 30 / 31 / 32 / 33 / 36 (listed) | NOT ESTIMABLE. USER-REPORTED values only (see §4). | No: all nine share one lineament support (pairs overlap 97.5–100%, per the existing `evidence/kp1_run_card.json` and `docs/index.html`). | Listed on the leaderboard already. **Do not resubmit.** |

**Uniqueness is the one claim verified end-to-end this session.** The three focus rasters were downloaded through `api.github.com` and their bytes were compared with the cited hashes. Receipt: `evidence/review_afe07cea_20261031.json`.

---

## 2. Format check against the official text (ORGANIZER-PUBLIC)

Official source: DrivenData competition page 967, "Submission format":
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format

Quoted requirements:
- "same projected coordinate reference system … EPSG 32611"
- "same resolution … (100m)"
- "same bounds as the training data, and **data outside the bounds is null or nan**"
- "a single layer with datatype of 32-bit float … with values **between 0 and 1**"

Official rules PDF (Section 3, same wording), for manual review: https://docs.nlr.gov/docs/fy26osti/96647.pdf

Reading the wording literally:
- "Outside the bounds" means outside the raster extent. The extent is the full 3,730 × 3,292 grid. It does not mean "outside the GeoDAWN footprint".
- So a `-zeros` file (every cell finite, 0 where there is no prediction) satisfies the literal rule: every in-extent value is in [0, 1].
- A `-nan` file (NaN wherever the footprint is absent, inside the extent) puts NaN *inside* the bounds. NaN is not in [0, 1]. That matches the user's error.

**Correction to the repo.** Several repo notes (`README.md` lines 309 and 395; `knowledge/session-review-arena-1d15747e.md`) say NaN-outside is "permitted" by the organizer's spec. That reading treats the footprint as if it were the bounds. The literal text does not support it. The repo's own `knowledge/official-sources-verified-2026-10-29.md` already flags this as "the zeros-outside twin is not what the page literally describes". That flag and the stronger NaN reading point in opposite directions, and only a portal test can settle the question. **Not portal-tested; no organizer receipt exists for any file in this repo.**

Encoding census (MEASURED, `docs/downloads/*.tif`, script `scripts/verify_review_20261031.py`):
- 7 files with NaN cells (NaN-inside-extent)
- 19 files with values in [0, 1] and no NaN
- 0 files with out-of-range values

---

## 3. Irregularities flagged for owner review

**A. The homepage says "OK TO SUBMIT" for KP1, while the rest of the site and the README say "NOT CLEARED".**
- `docs/index.html` top banner: "OK TO SUBMIT: K-PROXY-DETECT GeoTIFF — the only file on this site cleared for upload."
- Same page, executive section: "Is anything OK to download and submit? **No.** DO NOT SUBMIT · NOT CLEARED."
- `README.md`, CURRENT REVIEW blocks from several sessions: "no file cleared".
- `AGENTS.md` (header still names session `arena/9a378959`): "Verdict: PROMOTE one file", and the run card `evidence/kp1_run_card.json` says `"verdict": "promote"` but also `"portal_acceptance": "not tested - no organizer receipt exists for this file"`.

The user asked that it be obvious whether a file is safe to submit. Right now the answer depends on which block a visitor reads first. **This review does not change any clearance.** The owner must pick one rule and make every page say it.

**B. The "promote" run card does not clear the file for upload.** A PROJECTED 0.2789 is below the 0.3195 target the user set, and the holdout DTI (0.0764, 95% block-bootstrap CI −0.0034 to 0.0260) is HOLDOUT-DTI on an off-catalogue proxy, not the organizer metric. The same proxy ranks the nine known scores in reverse (ρ = −1.0 on the mandated instrument; −0.34 on the independent inventory), so the repo itself says it cannot be used as a promotion gate.

**C. Score figures disagree with the live leaderboard (ORGANIZER-PUBLIC).** Leaderboard page, fetched 31 Oct 2026: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- #1 xiaofanhu **0.4544**
- #2 cfld__ **0.3934**
- #7 herculesschonfeldt6 **0.3568**
- #10 raulcbrooks0909 **0.3550**
- #22 DARD **0.3407**

The user's statements — "0.4413 is the high score" and "0.3195 is the highest score right now" — do not match this page. The repo's own notes give 0.3195 at about #48 or #50, so "highest" is not right. The page shows relative times, not a snapshot date, so the owner should re-read it before planning.

**D. The user's own error message points at NaN.** The rejection text "Predicted values must be in range [0, 1]" would be raised by a NaN cell. That is an inference from the wording. The portal was not tested from here (no login), and which file the user uploaded is unknown.

**E. The repo's `sample_submission.tif`** is flagged in the repo as carrying the known-fault set, while the official text says the sample "predicts total fault absence" (repo irregularity B5). Not re-checked here (the file is not in `docs/`).

---

## 4. Focus-site mechanism check (MEASURED on the downloaded bytes)

- GEMSDOE32 B2 (`gemsdoe32-…-zeros.tif`, SHA-256 `c55bafc4…7ab6fa9`, matching the value printed in `docs/GEMSDOE32.html`) has **37,654 dots**.
- GEMSDOE25 zeros (SHA-256 `3e78737f…9bcc30`, matching `docs/index.html`) has **44,090 dots**.
- B2 is a **strict subset** of GEMSDOE25: 37,654 of B2's dots lie inside GEMSDOE25, and 0 lie outside it. The 6,436 dots removed are the 6,436 GEMSDOE25 dots that B2 lacks.

The repo's explanation for 0.2778 (removed dots lay within 2 px of catalogue faults, which the organizer's new-fault test may not reward) is consistent with this subset. It remains a **mechanism, not a measurement**. The score effect cannot be measured from here.

---

## 5. Tests and checks run in this session

- `pytest` on the repo suite: **515 passed, 4 skipped** (`.venv-karage`, numpy 2.4.6, rasterio 1.4.4). No code in the repo was changed.
- Format check on all `docs/downloads/*.tif` and other local TIFs (script run in this session): EPSG 32611, 3730×3292, float32, one band. Results in §2.
- Independent re-check: `scripts/verify_review_20261031.py` → `evidence/review_afe07cea_20261031.json`.

---

## 6. What was **not** done (honest scope)

- No new TIF was generated. The user asked for a unique file that beats 0.3195. Nothing in this session produced a candidate that meets that bar, and the repo's own analysis finds no demonstrated route to it. Any new file would be unvalidated and would have needed the owner's clearance ruling first.
- No holdout experiment was run. The repo's budget rule allows 3 experiments or 2 hours per session. Nothing here supports spending it before the format question in §2 is settled.
- No leaderboard estimate was produced for any file. The repo's estimates are PROJECTED, and the organizer's rescoring is unavailable.
- The three-to-five hypothesis list and the "Phd-level" explanation requested in the prompt are not repeated here. The current hypothesis set is in `knowledge/hypotheses-8e91c377-20261031.md` and the earlier review files; they should be checked against §2 before anyone builds on them.
- No DrivenData login was used. The `data/` directory is absent here, so the holdout and the registry could not be re-run from raw inputs.

---

## 7. What the owner needs to decide (in order)

1. **Encoding.** Accept the literal reading in §2, under which zeros outside the extent is compliant and NaN inside the extent is not, and retire the "NaN-outside is permitted" note. Or record the portal test that says otherwise.
2. **Clearance.** Choose one rule, and make the homepage banner, the executive summary, and the README say the same thing about KP1. Until then, nothing is OK to submit on this site.
3. **Score re-read.** Re-check the leaderboard and record the snapshot date. The user's 0.4413 and 0.3195 figures need a source.
4. **Next experiment.** Only after 1–3, and only inside the budget.

## 8. Limitations and access needed

- No DrivenData login from this sandbox, so no organizer receipt. Required: a portal test with one zeros file and one NaN file, with the portal's response recorded.
- Official pages were read through the fetch tool, not bash; `raw.githubusercontent.com` and DrivenData are not on the bash allowlist. Focus files were fetched via `api.github.com`.
- The `data/` inputs (training features, labels) are not in this checkout. Holdout and the registry cannot be re-run without them.

## 9. Links for manual review

- Competition problem page (metric, submission format): https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Official rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Focus files (GitHub, pinned commits — cited in `docs/index.html`): GEMSDOE32 B2 `73485f27…`, GEMSDOE25 zeros `5a60fb47…`, GEMSDOE24 nan `a73f9ffb…`
- Receipts: `evidence/review_afe07cea_20261031.json`, `evidence/kp1_run_card.json`, `evidence/kp1_release_gate.json`
