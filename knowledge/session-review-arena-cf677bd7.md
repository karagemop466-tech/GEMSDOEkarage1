# Session review — arena/cf677bd7 (2026-10-28)

Verdict: **NEGATIVE / DO NOT SUBMIT.** No new GeoTIFF was generated, no
competition slot was selected or spent, and no leaderboard estimate was
produced. This follows the binding parallel-run protocol in `AGENTS.md`:
`registry/template.json` still records `method_lane: null`, so no lane may
be invented, and the literal lattice gate blocks every extant candidate.

## Pass 1 — Review of the nine focus sites (saved-byte audit already in repo)

Source: `docs/data/reference-audit.json` (audit `karage1-reference-audit-v1`,
2026-10-28) + `registry/score_ledger.csv`. All scores below are
**USER-REPORTED / UNVERIFIED** — no organizer receipt is in this repo.
A projection is never written as a score (protocol rule 3).

| Site | Leader file (dots) | Reported no. | Lattice 3-px overlap | Unique? | Action |
|---|---|---|---|---|---|
| GEMSDOE32 | h33-h33-2-b2 e5eb6e7e-zeros (37,654) | 0.2778 | 99.92% | NO | DO NOT RESUBMIT |
| GEMSDOE36 | anderson-geothermal-pinn 9b9ea4e6-zeros (38,854) | 0.2750 | 99.92% | NO | DO NOT RESUBMIT |
| GEMSDOE28 | h36-1-rung30 b531dae0 (37,660) | 0.2710 | 99.91% | NO | DO NOT RESUBMIT |
| GEMSDOE31 | h27-4-solo-d28 8acb75e1 (40,199) | 0.2708 | 99.92% | NO | DO NOT RESUBMIT |
| GEMSDOE33 | h33d-analog-tip-stepover cb490425 (41,865) | 0.2632 | 99.91% | NO | DO NOT RESUBMIT |
| GEMSDOE25 | dotted-h19-5-d2-8 e56ea318 (44,090) | 0.2600 | 99.92% | NO | DO NOT RESUBMIT |
| GEMSDOE30 | d28-poisson300m-offcat 91eae1ca (44,090) | 0.2600 | 99.92% | NO | DO NOT RESUBMIT |
| GEMSDOE24 | h25-1-dotted-h19-5 989f5950 (60,069) | 0.2477 | 99.92% | NO | DO NOT RESUBMIT |
| GEMSDOE27 | topo-gap-closure-t-v2 5512495c (61,328) | 0.2449 | 99.92% | NO | DO NOT RESUBMIT |

Why GEMSDOE32 scored highest (from `knowledge/02_why_gemsdoe32_b2_scored_0.2778.md`
and the exact collar-ablation ladder in README): the B2 raster is the
44,090-dot GEMSDOE25/30 parent with 6,436 dots within 200 m (r≤2 px) of
`labels.tif` removed. Removing near-catalogue dots raises pooled DTI
(α=0.2, β=0.8) because those dots earn little distance-kernel credit while
costing precision-like penalty. That is a catalogue-collar effect, not
evidence of new fault discovery, and copying it would be a duplicate.

**Estimated leaderboard score for any new file: UNAVAILABLE.** The only
labelled numbers this repo may publish are HOLDOUT-DTI (evaluator,
withheld n, 95% CI) or ORGANIZER-CONFIRMED receipts. Neither exists for a
new candidate, so the executive-summary table lists "Unavailable" — that
is deliberate, not an omission.

## Pass 2 — Why no unique high-scoring TIF can be issued this session

1. **No assigned lane.** `registry/template.json`: `method_lane: null`,
   `canonical_template_assignment: null`. Protocol: do not invent a lane.
2. **Lattice arithmetic.** The pinned 13GEMSDOE lattice covers 99.8713%
   of the mirrored footprint within 3 px; only 6,649 footprint pixels are
   uncovered. A champion-sized 37,654-dot raster therefore has ≥82.34%
   of dots within 3 px of the lattice even in the best case — above the
   70% stop rule (`reference-audit.json` → `champion_sized_budget_bound`).
   Stuffing the 6,649 uncovered pixels to evade this would be gaming the
   gate, which `AGENTS.md` explicitly forbids.
3. **Holdout gate unmet.** No candidate this session was run through
   hide-and-recover; the best prior HOLDOUT-DTI on record (BB-STEP,
   0.0318, `gemsk-hide-recover-v1`, n=60,988, 95% CI [0.0271, 0.0363])
   is far below what the collar-ablation family achieves and its raster
   is itself a literal lattice duplicate (98.53%).

## Pass 3 — Verification performed this session

- Full test suite in a fresh venv (`/tmp/venv`, requirements installed
  from PyPI): **305 passed** (119 rasterio PendingDeprecationWarnings).
- Re-read `docs/data/reference-audit.json`: all nine rows confirmed
  (dots, SHA-256 prefixes, lattice overlap 99.91–99.92%).
- BB-STEP download SHA-256 re-computed:
  `72312302675d65cd1983239dd436412b5db1118a7c08f2a5807ef436b5536d6a` — matches README.
- Hypotheses: 5 ranked, pre-registered candidates already exist in
  `knowledge/hypotheses-20261028.md` (H1 signed two-scale potential-field
  offset is top; each names layers, signature, off-catalogue rationale,
  non-fault mimic, and free official source). None may be executed until
  a lane is assigned and organizer data are authenticated.

## Irregularities flagged (unchanged, for protocol owner)

- Mirrored `labels.tif` ≡ `existing_faults.tif` byte-identical; mirrored
  sample template contains 60,988 positive cells despite the public
  all-absence description; 3,073 interior `training_features.tif` nodata
  pixels (`-3.4028235e+38`) inside the footprint — a plausible mechanism
  for the reported "Predicted values must be in range [0, 1]" portal
  error, not a proven cause.
- All focus-site scores are user-reported with no organizer receipts.

## Next steps (selector/owner, separate from experiments)

1. Assign a method lane + canonical template in `registry/template.json`.
2. Authenticate organizer data (DrivenData login) instead of peer mirrors.
3. Resolve the lattice-vs-registry interpretation with the protocol owner
   — do not lower the 70% threshold locally.
4. Only then: preregister H1, run ≤3 hide-and-recover experiments with
   per-feature leakage canaries (AUC ≤ 0.90), validate saved bytes, and
   let a separate selector check the weekly cap.
