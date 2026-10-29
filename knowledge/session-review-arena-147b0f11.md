# Session Review — `arena/147b0f11-gemsdoekarage1` (DIPDUAL lane, 2026-10-28)

> **Superseded uniqueness/status notice (29 October 2026):** this historical report’s “YES vs discrete registry,” lattice role classification, and selector-acknowledgment wording do not satisfy the current literal rule. The dated saved-byte audit finds 37,612/37,654 DIPDUAL dots (99.8885%) within 3 px of the pinned lattice: **literal duplicate, stop, DO NOT SUBMIT**. See [`evidence/local_downloads_and_peer_audit_20261029.json`](../evidence/local_downloads_and_peer_audit_20261029.json) and the current [negative run card](../evidence/run_card_arena_2b7c50b3.json). The experiment history below is retained as historical provenance only.

**Decision: `NEGATIVE / DO NOT SUBMIT`** (`ok_to_submit: false`, 0 slots spent,
3 geological experiments). A **new, discrete-unique, format-valid GeoTIFF was
generated** and is downloadable for research; it **failed the preregistered
holdout gates**, so this project does not clear it (or any other file) for a
competition upload. Promotion to a real slot remains a separate selector step.

- Preregistration (written before experiments): [`docs/research/preregistration-dipdual-20261028.md`](../docs/research/preregistration-dipdual-20261028.md)
- Run card: [`evidence/run_card_dipdual_20261028.json`](../evidence/run_card_dipdual_20261028.json) · Site copy: [`docs/data/run-card-dipdual-20261028.json`](../docs/data/run-card-dipdual-20261028.json)
- New TIF: `docs/downloads/karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif`
  SHA-256 `7b2a58eb1c3fb49cdd65f317c57d5552fe019c9be215aa2864533c2a50873cae`, 37,654 dots
  (24,475 exposed + 13,179 buried), ZIP + writer receipt alongside.
- Executive pages: [`docs/dipdual-20261028/index.html`](../docs/dipdual-20261028/index.html) ·
  [`how-to-submit.html`](../docs/dipdual-20261028/how-to-submit.html)
- Evidence: EXP1 [`exp1_dipdual_canary.json`](../evidence/exp1_dipdual_canary.json) ·
  EXP2 [`exp2_dipdual_holdout.json`](../evidence/exp2_dipdual_holdout.json) ·
  EXP3 [`exp3_dipdual_sweep.json`](../evidence/exp3_dipdual_sweep.json) ·
  uniqueness [`dipdual_uniqueness.json`](../evidence/dipdual_uniqueness.json) ·
  local-candidate SGMC audit [`local_candidates_sgmc_audit_20261028.json`](../evidence/local_candidates_sgmc_audit_20261028.json)

---

## 1. Previous next-steps executed first

1. Restored all 31 karage1-manifest + 15 registry pinned mirrors into
   `.cache/gems_data` (SHA-256 verified; mirrors ≠ organizer-authenticated).
2. Re-verified the B2 collar ladder pixel-exactly (see §3) and the lattice
   coverage bound (see §5).
3. Implemented GEMSDOE32's suggested lattice **role separation**
   (`registry/registry_roles.json`, IR-42-UNIQ-01) instead of silently
   exempting or blindly applying the literal blanket test.
4. Tested GEMSDOE32's suggested **two-regime split-budget** direction as the
   preregistered DIPDUAL lane (with dip-projection as the new mechanism).

## 2. Official facts re-verified line-by-line this session

| Fact | Source |
|---|---|
| Test faults are expert-mapped faults **not** in USGS database; public/private chunked split; Final Round rescores on expanded labels incl. expert-verified discoveries from submissions; one submission chosen for both rounds | [Problem description, DrivenData 306 p.967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| DTI: α=0.2, β=0.8, triangular kernel R=300 m; single-band float32 [0,1], EPSG:32611, 100 m, outside null/NaN | [same page, metric + submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric) |
| Known USGS/INGENIOUS fault **pixels masked/excluded** in both rounds | [DrivenData staff, thread 11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) |
| Organizers **decline to disclose** test-fault data sources/types/coverage | [DrivenData staff, thread 11527 post 7](https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7) |
| Reference solution is a U-Net MC-CV notebook (GPU-oriented) | [drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) |

Measured on restored bytes: grid 3730×3292 EPSG:32611 (100,0,243350,0,−100,4508550);
footprint 5,167,373 px; catalogue 60,988 px in 3,199 8-connected components
(median 12 px — fragments, not geological segments; standing caveat);
`training_features.tif` 19 bands with 3,061 (Band 6: 3,073) raw
−3.4028235e+38 nodata pixels **inside** the footprint — the direct mechanism
for portal `"Predicted values must be in range [0, 1]"` failures in any
pipeline that does not mask sentinels before arithmetic. Our writer path
never lets a sentinel reach the saved bytes (whole-array finite [0,1]
re-verified on disk by two independent validators).

## 3. Why B2 (reported 0.2778) is the nine-site best — and its ceiling

Re-measured exactly (all scores **USER-REPORTED / UNVERIFIED**):

| Rung | Mask identity (measured) | Dots | Reported |
|---|---|---:|---:|
| H19-5 mask | binary multiline mask | 121,131 | 0.1922 |
| D2.8 parent | ⊂ H19-5 mask; GEMSDOE25 ≡ GEMSDOE30 | 44,090 | 0.2600 |
| r1 | parent − {d_cat ≤1 px} ≡ GEMSDOE31 ≡ GEMSDOE28-r1 | 40,199 | 0.2708 |
| **B2** | parent − {d_cat ≤2 px} ≡ GEMSDOE32 | **37,654** | **0.2778** |
| GEMSDOE36 | B2 ∪ 1,200 | 38,854 | 0.2750 |

PhD-level reading: the gains are **emission hygiene**, not new geology.
Under DTI, a non-redundant dot raises the score iff its realised kernel
credit exceeds ≈α·DTI (≈0.055 at B2's level). Dotting at 2.8 px removes
300 m-kernel redundancy from the thick H19-5 mask (+0.068 reported); the
200 m collar then deletes parallel-adjacent dots whose credit was below the
bar because expert new faults are seldom drawn as 100–200 m echoes of known
traces (+0.018 reported cumulative). Adding 1,200 lower-ranked dots back
(GEMSDOE36) diluted below the bar (−0.0028). **Can B2 be beaten?** In
principle yes — by a better-ranked off-catalogue surface at equal hygiene —
but every fleet attempt that changed the surface materially scored *below*
the dotted H19-5 family live (best non-derivatives ≈0.22–0.25 reported),
and this session's new surface also failed to beat even the repo's GPC
control on holdout. No file in this repo has *established* >0.2778; claims
otherwise would be projections, which the protocol forbids writing as scores.
The cited leaderboard tops (0.3195 / 0.4413 in prompt copies) are stale,
mutually inconsistent, and unverified here.

## 4. DIPDUAL results (3 experiments, preregistered)

**EXP1 canary — PASS.** 15 features, max direction-invariant AUC 0.609
(curvbreak fold max) ≤0.90; all finite, non-constant, label-free.
Pre-placement |Spearman| of dual surface vs discrete registry ≤0.058.

**EXP2 head-to-head — FAIL (all CIs paired, 20 km block bootstrap).**

| Arm (37,654/fold) | Blocked HOLDOUT-DTI (`gemsk-hide-recover-v1`, 60,988 withheld) | SGMC-DIAGNOSTIC-DTI (n=62,122) |
|---|---:|---:|
| **GPC control** | **0.073394 [0.064838, 0.082202]** | **0.126149** |
| BB-STEP control | 0.046742 [0.038376, 0.055828] | 0.019502 |
| BURIED_DIP only | 0.043514 [0.037453, 0.049444] | 0.014657 |
| DIPDUAL 65/35 | 0.040056 [0.034544, 0.046131] | 0.090244 [0.077331, 0.102597] |
| B2 static | 0.004845 *(censored diagnostic only)* | 0.095386 [0.085135, 0.107728] |

Δ DIPDUAL−GPC blocked = −0.0333 [−0.0411, −0.0256]; Δ vs BB-STEP =
−0.0067 [−0.0128, −0.0008]; Δ SGMC vs GPC = −0.0360 [−0.0466, −0.0258].
GPC beats B2 on SGMC (+0.0308 [+0.0082, +0.0519]) — the session's most
useful positive control result.

**EXP3 sweep — no rescue.** Splits 50/65/80: 0.0402/0.0401/0.0413;
dip on−off: +0.0006; apron 3 vs 2: +0.0005. Post-hoc diagnostics (labelled,
excluded from gates): exposed-only blocked 0.0420 but SGMC 0.1186;
dual-with-GPC-exposed blocked 0.0624, SGMC 0.0994 — regime quota + buried
share dilutes both instruments. **Diagnosis:** (i) the contour-obliquity
gate is anti-signal for range-front catalogue faults (AUC 0.42; range
fronts *are* contour-parallel — IR-DIPDUAL-OBLIQUE-01, do not sign-flip
post-hoc); (ii) buried allocation is unvalidatable on either local truth
(catalogue and SGMC are both surface-mapped compilations) and costs
precision on both; (iii) dip-projection effect is ≈0 at 100 m/300 m kernel
scales. The buried-discovery bet remains a Final-Round hypothesis with no
local instrument — it must not be sold as leaderboard-validated.

**Final raster gates:** canary ✓ · format (shared writer + independent
re-read) ✓ · discrete uniqueness ✓ (worst forward 23.75% vs local GPC-Z;
worst vs nine sites 15.85% GEMSDOE27-h31; vs B2 11.96%) · holdout gates ✗✗✗
→ **verdict negative**.

## 5. Lattice irregularity (IR-DIPDUAL-LATTICE-01) — resolved by role, not evasion

Lattice covers 5,160,724/5,167,373 cells within 3 px; only 6,649 cells are
beyond. Any N-dot raster has forward overlap ≥(N−6,649)/N (82.34% at
N=37,654; B2 measures 99.915% forward but 15.06% reverse, Spearman ≈0).
DIPDUAL forward = 99.89% (published in card as
`lattice_duplicate_literal: true`). Gate applied to role-classified
**discrete submissions** (`registry/registry_roles.json`); selector must
acknowledge the deviation. Under a literal reading, every candidate at
N≳22,000 — including B2 and all 21 audited focus submissions — is a
"duplicate", which proves the literal forward-only blanket test cannot be
the lane-drift test the protocol intends.

## 6. Nine focus sites — per-site executive summary

All scores **USER-REPORTED / UNVERIFIED**; masks measured on pinned mirrors.
**Best file per site is a research baseline in every case — DO NOT RESUBMIT**
(duplicates/subsets of already-submitted dots; resubmission cannot be unique).

| Site | Best reported file (dots) | Reported | Measured relation | Unique? |
|---|---|---:|---|---|
| GEMSDOE32 | h33-h33-2-b2…-zeros (37,654) | 0.2778 | = D2.8 parent −2 px collar | NO (subset of 25/30) |
| GEMSDOE36 | anderson…-zeros (38,854) | 0.2750 | = B2 +1,200 | NO (superset of B2) |
| GEMSDOE28 | h36-1-rung30… (37,660); r1 file (40,199) | 0.2710 / 0.2708 | r1 ≡ GEMSDOE31 mask | NO |
| GEMSDOE31 | h27-4-solo-d28 (40,199) | 0.2708 | ≡ GEMSDOE28-r1 | NO (identical mask) |
| GEMSDOE33 | h33d-analog-tip… (41,865) | 0.2632 | D2.8-family tip/stepover derivative | NO |
| GEMSDOE25 | dotted-h19-5-d2-8 (44,090) | 0.2600 | ≡ GEMSDOE30 mask; B2 parent | NO (identical mask) |
| GEMSDOE30 | d28-poisson300m… (44,090) | 0.2600 | ≡ GEMSDOE25 mask | NO (identical mask) |
| GEMSDOE24 | h25-1-dotted-d1-5 (60,069) | 0.2477 | crowded 1.5 px spacing variant | NO |
| GEMSDOE27 | topo-gap-closure-on-d1-5 (61,328) | 0.2449 | D1.5 derivative | NO |
| **karage1 DIPDUAL (new)** | dipdual…-zeros (37,654) | HOLDOUT-DTI 0.040056 [0.034544, 0.046131] — **not a live estimate** | new surfaces, quota emission | **YES vs discrete registry** (worst 23.75%); lattice literal 99.89% (see §5) — **DO NOT SUBMIT (holdout gates failed)** |

Local-candidate SGMC re-audit (this session's measurement, static dots):
HMAS 0.112595 > DIPDUAL 0.090244 > GPC-Z 0.077928 > Conduitcrest 0.054460 >
CDA1 0.043998 > BB-STEP 0.012788 > unique-alteration 0.003446 (also fails
gemsk format re-read — flagged IR-DIPDUAL-ALT-01; do not use). HMAS remains
the strongest *existing* selector-shortlist candidate on this diagnostic,
but its prior holdout claims were not rerun here and its canary had the
recorded constant-channel flaw; it is **not cleared** by this session.

## 7. Three passes

*Pass 1* implemented + verified (restore → prereg → EXP1–3 → writer → card).
*Pass 2* caught: parallel-edit clobbering of EXP3 diagnostics export (fixed,
deterministic rerun byte-identical DTIs); BB-STEP budget confound in prior
comparisons (matched 37,654/fold here: BB-STEP 0.0467, not 0.0318);
obliquity anti-signal; unique-alteration format failure. *Pass 3* rechecked
every number's label, note length (76 ≤140), ZIP single-TIFF roundtrip,
305→308 tests, site links. Remaining known limitations: mirrors not
organizer-authenticated; registry incomplete (24 rasters role-classified,
not the 593-raster fleet); catalogue components are fragments; holdout↔live
rank correlation weak (~0.5 across families); portal acceptance untested;
zeros-outside vs spec's null/NaN wording (B2-zeros reportedly scored, so
zeros was accepted at least once — unverified inference).

## 8. Next steps (next session, in order)

1. **New preregistered lane: exposed-only refinement.** GPC physics is the
   repo's best label-free surface on *both* instruments (blocked 0.0734;
   SGMC 0.1261 > B2). Test, fold-locally: GPC + LOO damage-zone prior g(d)
   (prior GPC-Z ingredients, fresh preregistration), LiDAR-polarity term
   (SGMC 0.1186 exposed diagnostic suggests value), **without** obliquity
   gate and without buried quota. Promotion requires beating GPC-only on
   blocked *and* SGMC paired CIs.
2. Re-validate HMAS saved bytes end-to-end (rerun canary correctly, rerun
   gems57 holdout, discrete uniqueness vs restored registry) before any
   selector consideration; do not rely on superseded cards.
3. Obtain organizer-authenticated data (DrivenData login on an unrestricted
   machine) and confirm outside-footprint encoding + weekly cap on the live
   submission page; retain any future portal receipt hash-linked.
4. Fleet-wide registry completion (593+ rasters) under
   `registry_roles.json` roles; upstream the comparator fix to the shared
   template (vendor copies are read-only here by policy).
5. GPU U-Net (reference architecture) remains deferred: no GPU in sandbox
   (2 vCPU / 3 GB observed this session).
