# QUARANTINED — NOT CLEARED, DO NOT DOWNLOAD FOR SUBMISSION

Moved here on 2026-10-29 from `docs/downloads/` and `docs/data/` (git history preserved).

**Why it was pulled from the public download folder**

- The committed `docs/executive-summary.html` on `main` displayed a green
  "IT IS OK TO DOWNLOAD AND SUBMIT THIS FILE" banner for this raster. That banner
  was not supported by any evidence in the repository.
- Its card (`data-card.json`, `unique-hyp-kth-therm-mask-20261028-zeros.json`) sets
  `"verdict": "promote"` while `correlation_vs_registry` and `overlap_vs_registry`
  are both empty `{}`. The lattice overlap and the pre-placement registry check
  therefore were never recorded.
- It is not covered by any saved-byte audit in `evidence/` (the test
  `test_local_and_peer_evidence_verifies_all_9_local_tifs` flags it as uncovered).
- The writer script that produced its card, `scripts/my_unique_experiment2.py`, is a
  private fork of the shared evaluator/writer path. It is now quarantined and exits with
  code 2 (`BLOCKED`).
- The card's `HOLDOUT-DTI 0.1713` cites evaluator `GEMSDOE32-HIDE-RECOVER-v3.0`, which
  does not exist in this repository. It cannot be reproduced here, so it is
  **not a verified number**. It is not an organizer score.

**Status:** NOT cleared. `ok_to_submit` is false in every repository gate. No weekly slot
was selected or spent.

Raster SHA-256 (as recorded in the card, not re-verified against an organizer receipt):
`a18e8fea158c2c53357b2d9651a6ce874b6329f1fdff690b4e17e8b0bb6a75eb`
