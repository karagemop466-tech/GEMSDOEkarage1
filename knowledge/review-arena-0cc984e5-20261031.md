# Repository review — `arena/0cc984e5-gemsdoekarage1` — 31 Oct 2026

## Executive decision

**NEGATIVE — do not download or submit any repository candidate.** This review found a fail-open contradiction in the KP1 release gate: it marked a candidate `ok_to_submit: true` after comparing only nine focus-site mirrors, while the repository itself documented an incomplete registry and unresolved/failed lattice overlap. The run card also said `promote`. That did not satisfy the user's protocol, which applies its correlation/overlap stop rule to *any registry raster*. The gate and its committed receipts/tests are now fail-closed. This is a release-safety correction, not a new geological experiment or a claim of improved score.

No TIF was generated or changed, no submission slot was selected or spent, and no leaderboard score estimate is supported. The reported GEMSDOE values remain historical user-reported figures unless an organizer receipt is available. Do not confuse local format validation, holdout DTI, or an observational model projection with an organizer-confirmed score.

## Pass 1 — inspect and reconcile

- Confirmed branch `arena/0cc984e5-gemsdoekarage1`; initial worktree was clean.
- Read the README session brief, `docs/standing-prompt.md`, current KP1 run card/release receipt, nine-site executive record, release-gate implementation, and related tests.
- The nine-focus-site audit reports low candidate overlap against those nine individual masks, but it does not establish uniqueness against the wider registry. The recorded KP1 card separately reports literal lattice saturation; the gate receipt omits a complete-registry clearance condition and nevertheless sets `ok_to_submit: true`.
- The fit/projection fields in `evidence/kp1_release_gate.json` are explicitly statistical projections, not scores; no per-site score estimate is supportable from these small, user-reported comparison records.
- The checkout has no `data/` tree and the Python environment lacks NumPy, SciPy, Rasterio, scikit-learn, scikit-image, and pytest. Therefore no experiment, raster re-open/validation, or test-suite run was possible in this review.

## Pass 2 — fixes and review

1. `scripts/kp1_release_gate.py` now fails closed unless the registry is complete and authenticated, the literal lattice check passes, both configured uniqueness comparisons pass, and the catalog-corridor condition passes. The current evidence has no complete-registry proof, so release clearance remains false.
2. Updated `evidence/kp1_release_gate.json` and `evidence/kp1_run_card.json` to say negative / not cleared; the numerical projection and underlying prior measurements were preserved and not relabeled.
3. Updated `tests/test_kp1_lane.py` and `tests/test_review_release.py` to assert that incomplete registry evidence cannot produce a green submit banner.
4. No existing raster bytes or generated candidate content were touched. No private alternate evaluator or writer was introduced.

### Static checks performed

- Python syntax compilation (`python -m compileall -q scripts tests src`) — see final verification below.
- JSON parse of both edited evidence records.
- `pytest` was attempted, but could not start: pytest and the project scientific dependencies are not installed. This is an environment limitation, not a passing test result.

## Pass 3 — request re-check

- Nine requested site rows and pages already exist; those historical entries are references, not new submission recommendations. Their provided scores must remain labeled user-reported/unverified absent file-linked organizer receipts.
- B2's geometric relation to its parent mask is documented, but the 0.2778 causal explanation is not established by a controlled organizer-confirmed ablation. A higher leaderboard score cannot be predicted from catalogue holdout results.
- Existing hypothesis slates are proposals/previous-session results, not freshly validated experiments in this review. The active lane is not assigned in `registry/template.json`; respecting the prompt means no new experiment.
- A no-NaN / [0,1] / grid check alone is not enough for “OK to submit.” The unique-registry stop gate and separate weekly selector are also unresolved. Thus there is no file cleared to download and submit.
- Three experiment / two-hour limit respected: **zero new geological experiments** in this review.

## Verification record / JSON run card

```json
{
  "hypothesis": "No geological hypothesis tested; this review corrected a fail-open release decision.",
  "mechanism": "Not applicable.",
  "named_non_fault_process_that_could_mimic_it": "Not applicable; no geological candidate was evaluated.",
  "holdout_dti": {
    "label": "NOT RUN",
    "reason": "No experiment run; dependencies and authenticated input/cache unavailable in this checkout."
  },
  "correlation_overlap_vs_registry": {
    "result": "NOT CLEARED",
    "reason": "Existing comparison is limited to nine focus-site mirrors; complete registry authentication and literal lattice gate remain unresolved."
  },
  "raster_sha256": null,
  "validator_output": {
    "no_nan_inside_footprint": "NOT RE-RUN",
    "values_in_0_1": "prior receipt only; not independently re-read in this review",
    "crs_shape_transform_match": "prior receipt only; not independently re-read in this review",
    "release_status": "NOT CLEARED"
  },
  "submission_name": null,
  "submission_note": "No submission candidate cleared. Do not submit.",
  "verdict": "negative",
  "experiments_run": 0,
  "slot_selected_or_spent": false
}
```

## Limitations and next work

1. Install project dependencies and run the complete test suite; fix any failures rather than calling static checks full verification.
2. Obtain organizer-authenticated competition data and matching cache, recording hashes and provenance. Do not claim third-party mirrors are organizer-authenticated.
3. Assign the exact method lane and canonical shared template/upstream commit. Resolve evaluator/writer provenance before running holdout.
4. Provide a complete pinned registry and resolve the literal lattice-overlap protocol. Keep the stated threshold; do not waive it just because it is inconvenient.
5. Define an off-catalogue validation design that matches the private expert target; run one preregistered candidate within budget, with fold-local features, feature-alone leakage canaries, pooled DTI and 95% CI.
6. Only then may a candidate proceed to independent selection; verify the live weekly allowance and retain an organizer receipt. A holdout number is never a leaderboard estimate.

## Primary official references

- [DrivenData competition problem, target and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData data tab (authentication required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [NLR competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
