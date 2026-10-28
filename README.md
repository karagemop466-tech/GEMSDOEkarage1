# GEMSDOEkarage1 — current decision: DO NOT SUBMIT

**No new competition submission has been cleared.** The prior H-K1-1 TIFF is retained as research evidence, not a download recommendation. Its reported registry scan excluded a lattice covering 99.932% of its dots within 3 pixels, contrary to the literal protocol. The old gate also treated a constant feature as a passing leakage canary. The historical “promote” and “OK to submit” statements are superseded, not current decisions. See [review](evidence/review_2026-10-28.json) and [findings](knowledge/review-2026-10-28.md).

Start each session with this README, [standing prompt](docs/standing-prompt.md), [AGENTS.md](AGENTS.md), [review and hypothesis slate](knowledge/research-review.md), and the current review. The owner’s values are **Maximize P(Win)** and **Own the Outcome**: make risk visible and do not manufacture scores or skip gates.

[Executive decision & nine-site table](docs/index.html) · [Submission guide](docs/submission-guide.html) · [Prior README, historical and superseded](knowledge/previous-readme-20261027.md) · [Prior experiment evidence](evidence/)

## Standing protocol

A single assigned method lane; at most three experiments or two hours. Use the shared cached stack, holdout evaluator, and submission writer. Hide whole fault segments with a buffer; derive catalogue features only from visible faults; mask visible faults pixel-exactly; pooled distance-weighted Tversky with 300 m triangular kernel, alpha 0.2 and beta 0.8. Run single-feature AUC canaries before trusting results. Stop if any registry raster has rank correlation above 0.90 or directed 3-pixel dot overlap above 70%, before placement where applicable and again on final dots. Report HOLDOUT-DTI with evaluator version, positive count and 95% CI; organizer scores require a receipt. Never label a projection as a score. Promotion and use of a weekly slot are separate decisions. The user's full project brief is preserved in [standing prompt](docs/standing-prompt.md); it must be read at the beginning of each session.

## Next steps

1. Resolve the missing assigned method paragraph and whether calibration rasters are part of the registry with the parallel-run coordinator; until then apply the literal rule and stop on the lattice witness.
2. Restore independently authenticated official competition grid, footprint, fault segments and features, pinned shared template/cache, and a complete enumerated registry. This environment cannot reach Dropbox or authenticate DrivenData, and peer mirrors do not prove organizer provenance.
3. Recompute fold-specific catalogue-derived features, feature canaries and same-fold baseline using the shared evaluator; investigate the constant feature and compare all registry rasters including calibration witnesses. Fix the shared tool once in its owning template, not in a private fork.
4. Only after a candidate beats the same-evaluator holdout best and passes exact saved-byte format and uniqueness gates may a separate selector consider the current portal allowance. No portal submissions were made here.

## Checks

`python -m pytest -q` runs the project tests after dependencies are installed. `scripts/release_gate.py` fails closed for older evidence without all-raster and exact-rank provenance. The previous HMAS pipeline and unsafe page generators are quarantined; do not bypass their guards. Prior release JSONs are historical records and not current authorization.

## Project brief (operative requirements — read at the start of every session)

**Competition:** DrivenData / U.S. DOE GEMS Prize (`competition-doe-gems`, EPSG:32611, pooled Distance-Weighted Tversky Index, alpha 0.2, beta 0.8, 300 m triangular kernel). Owner-cited best: GEMSDOE32 `h33-h33-2-b2-...-zeros` = 0.2778; leaderboard top cited 0.4413/0.4437.

**Core values:** Maximize P(Win); Own the Outcome. Negative results, blocked data, and unprovable claims are reported as such; nothing is projected as a score; irregularities are flagged for review.

**Highest urgency — a unique TIF:** Generate a unique, valid single-band GeoTIFF (values in [0,1]; CRS/shape/geotransform identical to submission format, EPSG:32611). Prior submissions (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36 and wider series) may be used for learning only — never copied. It must be obvious whether a TIF is OK to download and submit.

**Site must show, at top:** the download link and the OK / NOT-OK-to-submit status; an executive summary table for each of the nine focus sites (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36): which file to download, estimated score, uniqueness vs all listed GEMSDOE submissions; a subpage explaining how to submit (file, unique name, note ≤140 characters).

**Score labeling:** every number is HOLDOUT-DTI (evaluator version, withheld positives, 95% CI) or ORGANIZER-CONFIRMED. A projection is never written as a score.

**Validation:** autonomous (no human inspector); values in [0,1], no NaN inside footprint. Earlier submission was rejected with "Predicted values must be in range [0,1]".

**PhD analysis:** explain why/how `h33-h33-2-b2` scored 0.2778 and whether it can be beaten; use that to generate the unique TIF.

**New hypotheses:** propose 3–5 untried geological hypotheses (layers, physical signature, why off-catalogue, how different), ranked by expected DTI gain and cost; validate top candidate on a spatially-blocked hide-and-recover holdout before any submission slot; if external data needed, name specific free official sources and check obtainability.

**PARALLEL-RUN PROTOCOL:** stay in your lane; duplicate check vs registry (rank-correlation >0.90 or >70% of dots within 3 px of a registry raster = duplicate → log and stop); reuse template tools (`evaluate_holdout.py`, `submission_writer.py`); label every number; leakage canary (single-feature AUC >0.90 on withheld truth = leakage until proven otherwise); budget ≤3 experiments or 2 hours; do not pick submissions (selector step separate, subject to weekly cap); end with a JSON run card (hypothesis, mechanism, mimicking process, holdout DTI+CI, correlation/overlap vs registry, raster SHA-256, validator output, submission name+note ≤140 chars, verdict promote/negative). Negative results are deliverables.

**Current decision (fail closed):** No candidate in this checkout passes the strict lattice uniqueness gate (registry uniform-lattice raster overlaps 99.932% of the retained unique artifact's dots within 3 px > 70% limit). The retained `karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif` is a byte-unique downloadable research artifact but is **NOT OK to submit**. No weekly slot spent. No organizer receipt (no DrivenData auth in this sandbox).

**Sources (free, official):** DrivenData competition page & data tab, gdr.openei.org/submissions/1391 (INGENIOUS), USGS GeoDAWN, NLR rules PDF 96647, epsg.io/32611, Tversky index. No hallucinations: verify line by line, link for manual review.

**Site:** clean GitHub Pages under `docs/`. Three passes (implement→verify, review→fix, recheck), then create a PR and merge to `main`; list remaining work and limitations for the next session.

Full reconstructed requirement set: [docs/standing-prompt.md](docs/standing-prompt.md).
