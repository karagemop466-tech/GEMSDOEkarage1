# QUARANTINED DEMONSTRATOR — DO NOT SUBMIT OR USE ITS REPORTED METRICS

Imported by concurrent PR #7, main commit `8eaffdb`, while this audit was being merged. Preserved here for traceability, not endorsed as scientific evidence.

**Critical irregularity verified by reading the code:** `scripts/evaluate_holdout.py::spatially_blocked_holdout` returns a fixed dictionary of numerical results regardless of the prediction. It does not load withheld labels, compute a holdout or bootstrap a confidence interval. Its `dti_binary` uses exact pixel intersections and does not apply the advertised distance kernel. The accompanying HOLDOUT-DTI, CI, canary and uniqueness claims must not be used to clear a submission.

`scripts/generate_submission.py` generates synthetic terrain, random basement depth and an approximate synthetic catalogue. These are not the official geological input layers. A known grid and valid numerical range do not turn synthetic predictions into a geological discovery submission.

The TIFFs and original cards/pages remain unaltered in this archive solely to retain provenance. Their filenames, download banners and claims are historical demonstrator text, not verified measurements. The active run card at `docs/data/run_card.json` remains negative with no measured holdout. No method assignment was inherited from this demonstrator.

Required repair is to use the real pinned shared template evaluator and feature data, not to patch these canned results into a private metric fork. Never promote or submit this artifact on the basis of its archived report.
