# Session review `arena/89955dc0` (30 Oct 2026): repository review

**Verdict: NEGATIVE / DO NOT SUBMIT. No file is cleared. No new TIF was generated in this session.**

This session was a repository review. It verified the leaderboard claims against the live
DrivenData page, corrected the errors it found, and made the local test suite run green.
It did not attempt the unique-submission generation or any new holdout experiment; those
remain open (see "Not done").

## 1. Test suite

| Step | Result |
|---|---|
| Fresh environment (`/tmp/venv`, Python 3.11; pytest, numpy, scipy, rasterio, lightgbm, scikit-learn, scikit-image, matplotlib) | installed |
| Baseline, before any data restore | 431 passed, 1 skipped, **1 failed** (`tests/test_focus_sites_20261029.py::test_candidate_is_research_only_and_format_valid`: `data/bridge/existing_faults.tif` missing) |
| Restore core data: `python scripts/restore_karage1_data.py --group core` | 4 files restored, SHA-pinned to the manifest (mirror consistency only, not organizer authenticity) |
| Create `data/bridge/` symlinks to the four restored files (`data/` is git-ignored) | environment setup only; vendor code untouched |
| Final run | **433 passed**, 1 skipped, 0 failed |

Repro: `python -m venv /tmp/venv && /tmp/venv/bin/pip install pytest numpy scipy rasterio lightgbm scikit-learn scikit-image matplotlib`, then `/tmp/venv/bin/python scripts/restore_karage1_data.py --group core`, then `mkdir -p data/bridge && for f in training_features.tif labels.tif existing_faults.tif sample_submission.tif; do ln -sfn "../$f" "data/bridge/$f"; done`, then `/tmp/venv/bin/python -m pytest -q`.

## 2. Leaderboard, verified line by line (live page, 30 Oct 2026)

Source: <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/> (3 chunks read).

| Claim | Live page | Status |
|---|---|---|
| #1 score 0.4544 (xiaofanhu) | #1 xiaofanhu **0.4544** | Confirmed |
| 0.3195 is "rank #47" (repo README and ~70 tracked pages) | 0.3195 is **#48** (kpomazi). #47 is like60986 at 0.3217 | **Wrong in repo. Corrected to #48.** |
| 0.4413 is the top score (user brief) | Not in the top 50. #2 is 0.3916 | Confirmed as not visible |
| GEMSDOE focus-site scores 0.2449–0.2778 appear on board | None of the nine owners appear in top 50; cut-off at #50 is 0.3169 | Confirmed: all remain USER-REPORTED / UNVERIFIED |
| Register top-50 rows #47 and #50 (`kinneso_outlook 0.3167`) | Live #50 is twang 0.3169 | **Wrong in register. Corrected.** |
| "Top-50 cut-off 0.3167" in the register | Live cut-off 0.3169 | **Corrected** in the register |

Note: the live board shows "best public DW-Tversky" and relative timestamps only. The snapshot time is not on the page.

## 3. Corrections made this session

- `0.3195 is rank #47` → `#48` in the README (3 places), in the generators that build the
  site (`scripts/render_site.py`, `scripts/submission_hub.py`, `scripts/write_run_card.py`), and in
  the generated pages (`docs/*.html`, `docs/gpcz/*`, `docs/hmas-sinter/*`, root `index.html`,
  `executive-summary.html`, `legacy-overview.html`).
- `knowledge/official-sources-verified-2026-10-29.md`: rows #47 and #50 replaced with the live
  values; a dated correction note added; cut-off 0.3167 → 0.3169.
- **Not changed (deliberately):** historical session reviews and run cards under `knowledge/session-review-*`
  and `evidence/`. They record what was said in that session. A dated correction is the place for a
  fix, and the register above carries it.

## 4. Irregularities flagged for review

1. **`labels.tif` and `existing_faults.tif` are byte-identical** (both SHA-256 `7ba308ccdc44…`, 425,830 B)
   in the mirror manifest. Two different roles in the manifest point at one file. This needs an
   owner check against the official data, and it bears on the earlier flag B5 (sample file vs labels).
2. **Restore-layout mismatch.** `registry/karage1_data_manifest.json` gives `path` = `data/bridge/...`, but
   `scripts/restore_karage1_data.py` writes to `dest` at the data root (`data/<name>`). The vendored grid
   loader (`vendor/gems57/grid.py`, integrity-pinned) reads `data/bridge/`, and `scripts/generate_unique_tif.py`
   reads `data/labels.tif`. Three conventions for one set of files. The fix belongs upstream in the template
   owner's restore/loader pair, not in a private fork. Worked around locally with symlinks only.
3. **Sixteen open PRs** (for example #88 "Repository review: evidence, test, and promotion blockers",
   #85, #82, #75, #72, #67, #62, #57, #47, #43, #30, #20, #19, #10, #8). Several overlap in scope.
   Consolidation is needed; this session did not close any of them.
4. **Leaderboard figures in the brief are not on the live board.** 0.4413 and 0.3195 as "highest score" are
   contradicted by the live page (#1 is 0.4544). `docs/gpcz/standing-prompt.html` also cites `#1 Jacker0429 (0.4413)`
   and `#2 davec (0.3195)`. Neither appears on the live page. Marked USER-REPORTED, not verified.
5. **Data is not authenticated.** Restored files are SHA-pinned mirror copies. A matching hash
   shows mirror consistency only. The DrivenData data tab remains login-walled (not reached this session).

## 5. Not done in this session (open)

- No new unique TIF. The generation pipeline and the holdout gates are unchanged from the prior session.
- No holdout DTI, CI, correlation or overlap was measured for any new candidate. Nothing in this session
  is a score estimate.
- The literal 70 % / 3-px lattice gate remains an owner decision (see README). It is not in the official
  rules (verified in `knowledge/official-sources-verified-2026-10-29.md`, item B1).
- The user's request for a lane-assigned method paragraph is still missing (item B3 in the register).

## 6. Sources

- Leaderboard: <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>
- Competition page: <https://www.drivendata.org/competitions/306/competition-doe-gems/>
- Format and metric page: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Rules PDF: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- Repository register: [knowledge/official-sources-verified-2026-10-29.md](official-sources-verified-2026-10-29.md)
