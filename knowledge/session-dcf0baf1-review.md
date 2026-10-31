# Session review — `arena/dcf0baf1-gemsdoekarage1` (31 Oct 2026)

Branch: `arena/dcf0baf1-gemsdoekarage1` (from `b9ac876776a13d37e1df4a1324c5a1a7f4952359` of `main`).
Verdict: **NEGATIVE — DO NOT SUBMIT.** No file is cleared. No weekly slot spent.

## 1. What this session produced

| Item | Path | Notes |
| --- | --- | --- |
| Nine-site executive table | `docs/data/nine_site_executive_20261031.json` | built from restored raster bytes by `scripts/build_nine_site_executive.py` |
| Executive summary page | `docs/submission-20261031.html` | self-contained, download link + OK/NOT-OK status at the top |
| Candidate generator | `scripts/generate_karage1_submission.py` | lane H-K1-SEISMIC-PROX, greedy max-coverage |
| Holdout screen | `scripts/holdout_screen_20261031.py` → `evidence/holdout_screen_seisprox_20261031.json` | `src/gemsk/holdout.py` evaluator |
| Candidate c3 (3 px collar) | `docs/downloads/karage1-seisprox-c3-w0.55-20261031T012000Z-zeros.tif` | 37,654 dots, SHA-256 `d2508c28accfeca7f9b5bd15e40bcdadec98f28b6800bc305f7b90199f6cc86d` |
| Candidate c2 (2 px collar) | `docs/downloads/karage1-seisprox-c2-w0.55-20261031T013500Z-zeros.tif` | 37,654 dots, SHA-256 `1ea94432c1d09cd5968443d793455f6cfcae908aec671b5b9febccd2a6281e4d` |
| Saved-byte receipts | `evidence/audit_karage1-seisprox-20261031.json`, `evidence/audit_karage1-seisprox-c2-20261031.json` | `scripts/audit_local_tif.py`, schema `karage1-local-tif-audit-v1` |
| Run cards | `evidence/run_card_karage1-seisprox-c{2,3}-w0.55-20261031T01{35,20}00Z.json` | `ok_to_submit: false`, `slot_selected_or_spent: false` |

## 2. Nine focus sites — measured lineage

Rebuilt from the restored raster bytes (registry TIFs, not the mirrored third-party HTML):

| Site | dots | within 3 px of catalogue | reported score | unique vs other eight? |
| --- | --- | --- | --- | --- |
| GEMSDOE24 | 60,069 | 11,938 (0.2477) | 0.2477 | no |
| GEMSDOE25 | 44,090 | 8,607 (0.2600) | 0.2600 | no |
| GEMSDOE27 | 61,328 | 12,187 (0.2449) | 0.2449 | no |
| GEMSDOE28 | 37,660 | 4,377 (0.2710) | 0.2710 | no |
| GEMSDOE30 | 44,090 | 8,607 (0.2600) | 0.2600 | no |
| GEMSDOE31 | 40,199 | 4,716 (0.2708) | 0.2708 | no |
| GEMSDOE32 B2 | 37,654 | 2,171 (0.2778) | 0.2778 | no |
| GEMSDOE33 | 41,865 | 6,024 (0.2632) | 0.2632 | no |
| GEMSDOE36 | 38,854 | 2,281 (0.2750) | 0.2750 | no |

* **All nine scores are USER-REPORTED / UNVERIFIED** (owner brief; no organizer receipt tied to the raster SHA-256 exists in this repository).
* **All nine sites are one underlying field dotted differently.** Every one of the 36 pairs has
  Spearman 0.98–0.9999 and Jaccard 0.34–1.0. Every site fails the literal 70 % / 3 px directed-overlap
  gate against at least one peer (worst forward overlap 0.867–1.000).
* Measured subset relations: GEMSDOE24 ⊂ GEMSDOE25 (fwd 1.000); GEMSDOE32 ⊂ GEMSDOE36 (fwd 1.000,
  Jaccard 0.969); GEMSDOE32 vs GEMSDOE31 Jaccard 0.937.
* **GEMSDOE32 B2 is exactly the GEMSDOE25 `dotted-h19-5-d2-8` mask with 6,436 dots removed** (every dot
  within the closed 2 px disk of the mirrored known-fault catalogue) and 0 added. GEMSDOE25 and
  GEMSDOE30 share the same positive-pixel mask. The collar order is monotone: B2 (2 px, 37,654) >
  GEMSDOE36 (superset, 38,854) > GEMSDOE31 (1 px, 40,199) > GEMSDOE25/30 (0 px, 44,090).

## 3. Why B2 reports 0.2778 — and whether it can be beaten

The official metric is a distance-weighted Tversky index,
`DTI = T / (T + α·F + β·(G − T))`, α = 0.2, β = 0.8, R = 300 m triangular kernel.

DrivenData staff clarified that **known catalogue fault pixels are masked from the scored truth**.
A dot whose only nearby fault is a *mapped* one therefore earns no true-positive credit and a full
unit of false-positive cost. Thinning the field near mapped faults raises the ratio — which is the
mechanism consistent with the reported collar order. **The receipt is absent, so the causal claim is
not proven.** The official rules also contain **no uniqueness rule**; the 70 % / 3 px and |Spearman|
0.90 gates are the team's own protocol.

Can a new result beat 0.2778? **Possible in principle, not established here.** Two levers remain
untested by this repository: (1) a full 3 px (300 m) collar, which removes every dot capable of
earning FP cost from a masked known fault, and (2) a genuinely different posterior field. Lane
H-K1-SEISMIC-PROX uses official training band 10 `deq_n100a15` (distance-to-earthquake), which the
repository's 58-channel stack **never references** — only band 16 enters channel 48 — together with
the 3 px collar. **No leaderboard estimate is produced**, because the hidden labels are unavailable.

## 4. Lane H-K1-SEISMIC-PROX — implementation

Self-contained (band 2/3/10/13/18 of `training_features.tif`), no private fork:

* `F = 0.55·robust_norm(|∇rtp|) + 0.25·robust_norm(iso_grav_anom_hg) + 0.20·robust_norm(iso_grav_anom)`
* `F *= (1 − w + w·robust_norm(exp(−deq/2500)))`, `w = 0.55`
* gate = footprint & ~{collar px} catalogue collar
* dots = exact greedy max-coverage on the **official triangular kernel**, radius 3 px

**Bug found and fixed during this session** (run 2 emitted a single dot):

1. **NaN poisoning.** `robust_norm` computed `(x−lo)/(hi−lo)` on non-finite input, and `rtp` is
   deliberately NaN outside the footprint, so the field was NaN over a large region; `np.argmax`
   returned the first NaN index and `W` became NaN everywhere. Fixed with
   `np.where(np.isfinite(x), (x−lo)/(hi−lo), 0.0)` and `np.nan_to_num` before the astype.
2. **Wrong coverage kernel.** Coverage was subtracted with the separation kernel instead of the
   official metric kernel, so picked pixels were not zeroed and were re-picked. Fixed by using
   `r = ceil(kernel_px) = 3` and the triangular kernel for both coverage subtraction and the exact
   `W` recomputation.

Verified with `--budget 2000` (2000 dots, validator all-pass, worst peer overlap 0.3215, lattice
diagnostic 1.0000), then the full 37,654-dot run.

## 5. Holdout screen (HOLDOUT-DTI) — and its limit

`scripts/holdout_screen_20261031.py` uses `src/gemsk/holdout.py` (whole-segment withholding, 200 px
blocks, 3 px buffer, 4 folds, pooled DTI, paired block bootstrap):

| Raster | HOLDOUT-DTI (pooled) | 95 % CI |
| --- | --- | --- |
| candidate c3 (3 px collar) | 0.000000 | 0.000000 – 0.000000 |
| candidate c2 (2 px collar) | 0.000006 | 0.000002 – 0.000010 |
| control: GEMSDOE32 B2 | 0.004845 | 0.004322 – 0.005346 |
| null control: uniform random | 0.049063 | 0.046072 – 0.051055 |

The candidates score ~0 because the collar places every dot outside the catalogue kernel. **This is a
property of the screen, not of the candidate.** The truth here is the *mapped* catalogue, whereas the
competition scores only *new* faults — so the screen rewards re-finding mapped traces and penalises
off-catalogue placement by construction. It **cannot rank off-catalogue candidates** and is **not a
leaderboard estimate**.

## 6. Blockers (unchanged)

1. **No hidden labels.** No organizer score and no defensible leaderboard estimate can be produced.
2. **No assigned method lane.** `registry/template.json` has `method_lane: null`; the protocol's
   single-method paragraph is still missing and must not be invented.
3. **No organizer receipt.** No file here has a submission-page receipt tying a leaderboard score to
   its SHA-256.
4. **Catalogue holdout mismatch** (see §5).
5. **Lattice gate.** The dense 13GEMSDOE lattice covers ~99.9 % of the footprint within 3 px, so the
   literal forward-overlap rule is unsatisfiable against it; it is published as a diagnostic only.

## 7. Irregularities flagged for owner review

* **I-7.** `registry/karage1_data_manifest.json` records the `sample_submission` SHA-256 as a
  **63-character** string; the restored bytes hash to the 64-character
  `2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc`. The prefix matches; the pin
  length is wrong. `scripts/validate_geotiff.py --template-sha256` therefore refuses the pin.
* **I-8.** `scripts/audit_local_tif.py` reads peer rasters from `.cache/gems_data/registry/`, which
  `scripts/prepare_data.py` (a fail-closed stub) does not create. This session populated it as a
  directory of symlinks to the repo `registry/` TIFs plus a lattice symlink. That cache layout is a
  local build artifact, **not** committed.

## 8. Tests

`PYTHONPATH=src:. .venv-karage/bin/python -m pytest tests/ -q` → **439 passed, 1 skipped**.
Adding a new download TIF required a `karage1-local-tif-audit-v1` receipt (§1); without it
`test_fleet_audit_covers_every_local_tif_and_blocks_all` and
`test_local_and_peer_evidence_verifies_all_9_local_tifs` correctly fail.
