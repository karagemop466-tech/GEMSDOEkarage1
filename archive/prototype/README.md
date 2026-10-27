# Concurrent prototype — archived, DO NOT SUBMIT

Preserved from concurrent main commits through `59651647aa7bbc84d18be1b83e765d7715162de7` during integration of PR #5. This work was not present when the audit began. Its TIFFs are explicitly synthetic stand-ins with placeholder geotransform; they are NOT real geological predictions and must not be submitted. Regridding synthetic predictions cannot turn them into geological evidence.

Code and historical claims are retained unchanged for traceability, not endorsed. In particular:
- `evaluate_holdout.py` describes FN/FP weighting differently from the required shared evaluator, does not implement a real prediction-scoring CLI, and its bootstrap uses `isin`, discarding repeated-block multiplicity. It is NOT the designated shared template evaluator. No scores from it are accepted by the active dashboard.
- No scientific lane was assigned to this audit by the late arrival of another session's prototype.
- Claims that registry rasters are inaccessible without DrivenData authentication are superseded by the independently retrieved nine-site historical audit.
- The active dashboard and negative card live at repository root and `docs/data/run_card.json`.

Archived relative paths were preserved as a unit. Old instructions that assume scripts at the repository root are historical only. Do not execute this prototype as the production pipeline.
