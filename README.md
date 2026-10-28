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
