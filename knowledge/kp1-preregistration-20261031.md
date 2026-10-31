# H-KP1 — K-PROXY-DETECT · preregistration and analysis record

Session `arena/9a378959-gemsdoekarage1`, 31 October 2026.
Everything below was written from measurements made in this repository during this session.
Receipts: `evidence/kp1_exp1_forensics.json`, `evidence/kp1_exp2_holdout.json`,
`evidence/kp1_release_gate.json`, `evidence/kp1_run_card.json`.

---

## 1. The metric, re-derived exactly

Official definition (DrivenData #306, page 967):

```
k(d)  = max(1 - d/300 m, 0)
TP_w  = sum_{g in G} max_x p(x) k(d(x,g))
FP_w  = sum_{x: p(x)>0} p(x) [1 - max_g k(d(x,g))]
FN_w  = sum_{g in G} [1 - max_x p(x) k(d(x,g))]  =  |G| - TP_w
DTI   = TP_w / (TP_w + a*FP_w + b*FN_w),   a = 0.2, b = 0.8
```

Because **a + b = 1 exactly**, substituting `FN_w = |G| - TP_w` gives the identity used
throughout this session:

```
DTI = TP_w / ( a*(TP_w + FP_w) + b*|G| )
```

Consequences that drive every design choice:

1. `|G|` is set by the organizer and is not under the submitter's control.
2. Only two quantities are controllable: `TP_w` (kernel-weighted credit on the private truth)
   and `FP_w` (mass that earns no credit). Both are **increasing in the number of emitted
   dots**, so every dot must buy more `TP_w` than it costs in `0.2 * FP_w`.
3. For a binary dot field, `FP_w = n - M` where `M = sum over dots of max_g k`. Two dots inside
   one another's kernel can spend the same truth cell's credit twice while each adds a full unit
   of `FP_w` — clumping is a pure loss.
4. `TP_w` saturates at 1 per truth cell, so extra dots over an already-covered cell are pure
   cost. This is why spacing matters and why a lattice-like minimum separation is not a stylistic
   choice.

The identity is implemented in `vendor/gems57/metric.py` and re-verified against a brute-force
transcription in `tests/test_metric.py`; this session's own test file adds the algebraic check.

## 2. Why GEMSDOE32 `h33-h33-2-b2` (0.2778) was the highest of the nine — measured, not narrated

All nine registry rasters were re-read from `registry/*.tif` and measured
(`evidence/kp1_exp1_forensics.json`). Association between geometry and the **user-reported**
scores (n = 9, permutation p over 20,000 draws):

| covariate | Spearman vs score | p | reading |
|---|---:|---:|---|
| fraction of dots > 15 px (1.5 km) from the catalogue | **+1.000** | 0.0000 | further out is better |
| median distance to the catalogue | **+1.000** | 0.0000 | same signal |
| fraction of dots ≤ 2 px from the catalogue | −0.894 | 0.0019 | catalogue-adjacent mass is wasted |
| dot count | −0.983 | 0.0001 | fewer dots are better |
| 3-px clumping (≥ 3 neighbours) | −0.916 | 0.0008 | redundancy costs |
| kernel coverage of the footprint | −1.000 | 0.0000 | more coverage = more FP mass |

The two highest-scoring files (**GEMSDOE32 0.2778** and **GEMSDOE36 0.2750**) both place
**exactly 0.0 %** of their dots within 2 px of the mapped catalogue and 58 % beyond 15 px;
the three lowest-scoring files (GEMSDOE24 0.2477, GEMSDOE27 0.2449, and GEMSDOE25/30 0.2600)
place 14.5 % in the corridor and carry 44k–61k dots. This is exactly what the algebra predicts:
the scored truth is a set of faults that is *absent from the catalogue*, so corridor mass is
paid for and never credited.

**Caveat, stated up front.** These are associations on nine points with strongly collinear
covariates. They are consistent with the metric algebra but are not an identified causal model,
and the 0.2778 itself is user-reported with no organizer receipt.

## 3. The finding that unblocked this lane: the holdout instrument is inverted

The standing protocol requires a spatially blocked holdout before any slot is spent, using
`vendor/gems57/evaluate_holdout.py` (evaluator `gems57-pooled-hide-v2`, 60,988 withheld
positives, four fixed quadrants, catalogue segments of the held quadrant withheld from training).

That instrument was run on all nine registry rasters. Result
(`evidence/kp1_exp2_holdout.json → instrument_calibration`):

| file | HOLDOUT-DTI | known user-reported score |
|---|---:|---:|
| GEMSDOE24 | 0.17183 | 0.2477 |
| GEMSDOE25 | 0.16163 | 0.2600 |
| GEMSDOE27 | 0.17264 | 0.2449 |
| GEMSDOE28 | 0.04618 | 0.2710 |
| GEMSDOE30 | 0.16163 | 0.2600 |
| GEMSDOE31 | 0.04906 | 0.2708 |
| GEMSDOE32 | 0.00671 | **0.2778** |
| GEMSDOE33 | 0.08641 | 0.2632 |
| GEMSDOE36 | 0.00693 | 0.2750 |

**Spearman = −1.0.** The instrument ranks the nine files *exactly backwards*.

The reading is not subtle: the instrument rewards recovering withheld **mapped** traces, and the
competition scores prediction of faults **absent** from the mapped catalogue. A submission that
maximises catalogue recovery minimises the leaderboard score. Prior sessions used this instrument
as a promotion gate; under that gate the highest-scoring file available (0.2778) is inadmissible
and every candidate that passed it was, by construction, one that places mass near mapped traces —
which is why the project's holdout-best candidates (0.056–0.073) never beat the champion.

**Recommendation to the protocol owner:** retire catalogue-recovery DTI as a promotion gate for
this competition, or calibrate any replacement instrument on known (raster, score) pairs before it
is used. This session therefore reports HOLDOUT-DTI but does **not** promote on it; promotion rests
on the saved-byte gates plus the geometry evidence in §2.

A second, independent check points the same way. On the off-catalogue proxy truth
(`derived_sgmc_faults_100m_u8.tif` minus the catalogue, 79,615 px), the nine engineered rasters
score *below* a uniform-random dot field of the same size (0.0625–0.0796 vs 0.0723 at n = 37,654;
`evidence/kp1_exp1_forensics.json → per_file → proxy_reference_dti`). That proxy is a different
population (bedrock compilation faults), so it is reported as a control, not used for selection.

## 4. Lane definition (the single method paragraph required by the protocol)

> **H-KP1 K-PROXY-DETECT — thermo-tectonic conduit alignment.** A cell's fault likelihood is the
> geometric mean of five percentile-ranked, *physics-only* terms — (i) multi-field edge agreement
> between the TMI horizontal gradient, the tilt derivative, the horizontal gradient of TMI
> upward-continued to 150 m, the isostatic-gravity horizontal gradient and the depth-to-basement
> step; (ii) geomorphic scarp evidence from detrended-elevation slope and curvature plus the 1 m
> LiDAR `step_max` and `coh100` metrics; (iii) thermal-spring and well conduit density from 27,092
> records; (iv) potassium-metasomatism alteration proxied by low Th/K and low U/K on the GeoDAWN
> contractor ratio grids; (v) geodetic strain-rate second invariant. No catalogue-derived quantity
> enters the surface. Dots are selected highest-score-first with a hard 4-px exclusion disc, are
> forbidden within 2 px of the mapped catalogue and are suppressed over flat, deep basin fill,
> with the budget set below the champion's. Validation uses the shared spatially blocked evaluator
> plus a calibrated-covariate projection; the evaluator is reported and explicitly *not* used as a
> promotion gate because it is anti-correlated with known scores (§3).

## 5. Hypotheses considered, ranked by expected gain ÷ cost

| # | Mechanism | New layers | Why it catches an unmapped fault | Non-fault mimic | Cost | Status |
|---|---|---|---|---|---|---|
| 1 | **TTCA** — multi-field edge + scarp + conduit + alteration consensus | TMI up-150 m gradient, Th/K, U/K, U/Th, 12-band 1 m LiDAR, spring/well density | upward continuation sees deeper basement structure under basin fill; alteration halos and springs are not in the catalogue at all | playa clays, basalt flows, continuation ringing, basin-fill contact springs | low | **built and validated here** |
| 2 | Spring–lineament **intersection** census | spring density × trace topology | intersections/tips of mapped faults are frequently unmapped | permeable contacts at range fronts | medium | proposed |
| 3 | **Upward-continuation depth series** (50/150/300/500 m) | 300/500 m levels derived from the official GeoDAWN grids | separates shallow volcanic texture from deep fabric | continuation ringing | medium | **not obtainable in this sandbox** — the needed archives (`22103_area1_tiffs.zip`, `22103_area2_tiffs.zip`, USGS sciencebase item 657e1d85d34e23d3533209f7) are outside the network allowlist |
| 4 | Fault-tip **damage-zone extrapolation** from Qfaults kinematics | `gdr_qfaults_traces.csv` slip rate / recency / sense | catalogue traces stop where mapping stopped | depositional pinch-out | high | overlaps sibling-repo lanes (relay/stepover), deprioritised |
| 5 | **Relocated-earthquake alignment** across mapped gaps | raw seismicity catalogue | independent of mapping | mining blasts, geothermal pumping | high | raw catalogue not pinned here |

## 6. What was built

`scripts/kp1_data.py` (pinned loaders), `scripts/kp1_planes.py` (29 cached planes, all
physics-only), `scripts/kp1_exp1_forensics.py`, `scripts/kp1_exp2_holdout.py`,
`scripts/kp1_build_candidate.py`, `scripts/kp1_release_gate.py`,
`scripts/build_kp1_site.py` (deterministic pages).

Artifact: `docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif`
(32,000 dots, float32, EPSG:32611, 3730 × 3292, values in [0, 1], zero outside the footprint,
zero pixels on the mapped catalogue).

Gates passed: format preflight 15/15 checks; max |Spearman| 0.0076 (< 0.90); max 3-px overlap
26.5 % (< 70 %); zero mass in the 2-px catalogue corridor.

## 7. Limits — what this session cannot claim

1. **No leaderboard estimate is measurable.** The scored truth is private. The 0.2789 figure is a
   projection from nine user-reported points, with parameter-only bootstrap uncertainty; the
   defensible working range is 0.24–0.31.
2. **The surface is not validated against the target population**, because no public data on the
   organizer's expert-identified new faults exists. The physics planes are individually weak
   predictors of mapped faults (best single-feature AUC 0.599), which is expected: surface traces
   are mapping artefacts as much as physical edges.
3. **The transfer assumption is untested.** The candidate assumes that what makes a boundary
   visible in magnetic/gravity/scarp/alteration data also made it identifiable to the expert
   panel. That is a geological argument, not a measurement.
4. **Nine points is nine points.** The covariate model has no power to detect a broken assumption.
5. **Existence of a better surface elsewhere is not excluded.** Only the nine focus sites plus the
   pinned fleet rasters mentioned in the prompt were compared.
