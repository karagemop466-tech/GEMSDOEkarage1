# Repository review — `arena/3fa432c5-gemsdoekarage1` — 28 October 2026

## Decision

**Negative — do not submit.** This was a repository/code review and verification pass, not a geological experiment. No new GeoTIFF, holdout score, score projection, or weekly-slot selection was produced. The current public pages correctly state that there is no approved file. Existing downloadable historical artifacts are explicitly research-only and must not be submitted.

The machine-readable negative run card is [`evidence/session_run_card_arena_3fa432c5_20261028.json`](../evidence/session_run_card_arena_3fa432c5_20261028.json). It follows the requested run-card shape; null metrics mean not measured, not zero.

## Pass 1 — inspect and verify current state

- Read `AGENTS.md`, `README.md`, `docs/standing-prompt.md`, the current protocol/audit records, scientific research review, site generator, shared-tool adapter, and existing run cards.
- Confirmed this branch began clean at the existing main commit. Ran `python scripts/shared_tools.py preflight`: **exit 1 / blocked**. The configured template pin is `73485f27cf230af770167397c2b72cb9ce3b3f25`, but `method_lane` is null; `.cache/gems_work/feature_stack.npy` and required `existing_faults.tif`, `training_features.tif`, `sample_submission.tif`, and `labels.tif` are absent.
- Re-ran the software suite in a local ignored virtual environment: **240 passed**. Rasterio emitted 90 pending-deprecation warnings. These tests verify software behavior only, not any geological hypothesis or score.
- Ran `python scripts/build_site.py`: it rendered 32 deterministic decision pages and reported no submission authorized. `git diff --exit-code -- docs index.html executive-summary.html style.css` passed before this report was added.
- Checked the nine-site executive summary: all requested focus sites have a historical reference, score source status, unavailable forecast, uniqueness disposition, and do-not-resubmit action. It does not fabricate a future score or offer an approved download.

## Pass 2 — adversarial review / risk and issue audit

1. **No candidate can be run safely:** the task says to stay in one method paragraph, but the active prompt does not identify the paragraph. `registry/template.json` also records `method_lane: null`. Choosing from old experiments would violate the single-lane protocol.
2. **Historical candidates are blocked:** the latest checked-in saved-byte audit says the two previously promoted files violate the literal lattice 3-pixel overlap rule. The separate parallel-candidate audit reaches the same negative decision for two other candidates. These are bounded audits against pinned mirrors, not proof of complete-registry uniqueness; they do not authorize a new submission.
3. **No scoring foundation in this checkout:** there is no local cached feature stack or required raster inputs. Therefore the shared evaluator, fold-local catalogue derivations, pixel-exact masks, per-feature leakage canaries, spatially-blocked holdout, 95% interval, and pre-placement surface comparison were not run. No number is estimated as a score.
4. **Provenance limitations:** pinned GitHub mirrors and saved-byte hashes establish byte consistency against those pins, not authenticity against the organizer. The official site, login-only competition files, private labels, and submission receipts are not authenticated here. The template pin is a proposed shared source; the canonical upstream template for this parallel lane remains unresolved.
5. **Research hypotheses exist, but are not novel or validated claims:** `knowledge/research-review.md` already ranks four mechanisms: paired potential-field edge displacement; relief-asymmetry reversal; conductivity-depth boundary termination; and multiscale curvature-polarity persistence. It names layers, physical signatures, confounders, and effort. The ranking is qualitative, not a projected DTI. It does not prove those ideas are globally untried across all GEMSDOE sites. No new external source was fetched during this session, so the obtainability of third-party data has not been newly established.
6. **Current summary shows actual inability to estimate:** each focus-site table row says “Unavailable / No defensible forecast,” which is appropriate without a valid comparable holdout. The displayed historical score figures are labeled user-reported/unverified, not organizer-confirmed.
7. **Public automation is not a live leaderboard feed:** the scheduled workflow stores a refresh artifact; it does not publish a live authenticated leaderboard or new site data. README and previous reviews already flag this. The static site cannot itself access the user's DrivenData account or submission cap.

No source-code defect was demonstrated that could be fixed without the missing lane or canonical shared tool. The fail-closed behavior was preserved rather than bypassed.

## Pass 3 — requirements re-check and final verification

- **Unique submission GeoTIFF:** not generated. This is intentional: no candidate can pass the prescribed pre-placement and final uniqueness tests without the missing lane and registry-complete witnesses. Result: no download is OK to submit.
- **Nine-site executive comparison:** present; each row identifies the historical research file and reports its historical claim as unverified, with new estimate unavailable and no resubmission action.
- **GEMSDOE32 explanation:** existing research page treats the reported B2 result as unverified and offers a plausible precision/false-positive trade-off explanation, not causal proof. It does not claim a new method will beat it.
- **Three-to-five new hypotheses:** four are documented, ranked qualitatively, with layers, mechanism, rationale, confounder, and repo-level distinction. None is run because the lane is unspecified and inputs are missing.
- **Protocol controls:** no more than three experiments and no slots were used; in fact, zero experiments and zero slots. Scores are not projected. No leakage canary or holdout result is claimed.
- **Validation:** no new raster exists, so CRS/range/NaN/transform checks are not claimed to pass. Historical validator results do not transfer to a future file.
- **Software and site:** 240 tests pass; deterministic builder passes; current pages remain explicitly negative. Warnings are upstream Rasterio deprecation warnings.

## Recommended next work

1. Resolve the parallel-lane instruction and name the exact one-paragraph hypothesis to pursue; reconcile the dense lattice with the literal “any registry raster” stop rule transparently, not by excluding that witness.
2. Identify the canonical shared template and obtain authenticated organizer submission-format/data bytes through an authorized source. Build a complete immutable registry manifest, including the continuous/lattice witnesses, and document provenance for each asset.
3. Restore the designated shared cache from verified inputs; then run preflight and the shared evaluator, not the quarantined private runners. First test each feature alone for leakage, then run the pre-registered buffered whole-segment hide-and-recover folds and paired pooled DTI comparison with 95% CIs.
4. Only if the surface passes the continuous uniqueness gate, write a candidate with the shared writer, reopen its saved bytes, validate the official footprint encoding/grid/range, and re-run the exact final-dot uniqueness scan.
5. Promotion and submission-slot selection must remain separate. Check the live cap in the authenticated portal and retain an organizer receipt if a future upload is made.
6. If an up-to-date public feed remains a goal, build an explicit CI job to refresh the permitted sources and publish a timestamped artifact/site snapshot; clearly label whether it is organizer-authenticated and fail closed on stale or incomplete inputs.

## Source and access note

Manual-review links and official-source pointers are catalogued in [`knowledge/sources-2026-10-28.md`](sources-2026-10-28.md), [`docs/sources.html`](../docs/sources.html), and the official-source section of [`knowledge/research-review.md`](research-review.md). A URL is a pointer, not evidence that its contents or downloadable data were accessed in this session. This run did not access DrivenData login/private competition downloads or verify current leaderboard/weekly-slot status.
