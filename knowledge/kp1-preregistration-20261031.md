# Lane H-KP1 — preregistration and analysis record (31 Oct 2026)

Session `arena/9a378959-gemsdoekarage1`. Three experiments, no submission slot spent.
Every number below is read from a committed receipt in `evidence/`; nothing here is
estimated from memory.

---

## 1. What is being predicted, precisely

The scored quantity is the DrivenData **DTI** on a *private* set of faults that the expert
panel mapped and that is **absent from the training catalogue**. For a prediction field `p`
on the 100 m grid, with `k(d) = max(1 − d/300 m, 0)`, `alpha = 0.2`, `beta = 0.8`,

    DTI = TP_w / (alpha·FP_w + beta·FN_w)

`TP_w` sums, over every truth cell, the single best covered credit; `FP_w` sums the prediction
mass **everywhere** that is not credited by a truth cell. For a binary dot field this is an
identity:

    DTI = T / (alpha·(n − M) + beta·|G| + T)

with `n` dots, `T` the covered truth credit, `M` the dots' own self-credit and `|G|` the size
of the truth. `evidence/kp1_metric_analysis.json` records the derivation and the ceiling.

Three consequences that the whole lane is built on:

1. a dot that lands **on** a truth cell is free (its own credit cancels its false-positive
   mass) and adds up to 1.0 to `T`;
2. a dot that misses costs exactly 0.2, whatever else is true;
3. one more dot helps iff its expected truth credit clears `alpha·(1 − m)·s/(1 − s)`, which
   depends only on the current score. At 0.2778 the bar is **0.0769**; at 0.4413 it is 0.158.

## 2. Why the nine focus sites score what they score (EXP1)

`evidence/kp1_exp1_forensics.json`. Measured on the saved bytes in `registry/`, with
`existing_faults.tif` as the catalogue (60,988 cells inside the footprint).

| site | reported | dots | ≤2 px from catalogue | >15 px | median distance | clumped | area covered |
|---|---|---|---|---|---|---|---|
| GEMSDOE32 | 0.2778 | 37,654 | 0.00 % | 58.4 % | 19.6 px | 0.26 % | 15.1 % |
| GEMSDOE36 | 0.2750 | 38,854 | 0.00 % | 58.7 % | 19.6 px | 42.1 % | 15.8 % |
| GEMSDOE28 | 0.2710 | 37,660 | 0.00 % | 57.9 % | 19.2 px | 0.27 % | 15.1 % |
| GEMSDOE31 | 0.2708 | 40,199 | 0.00 % | 58.0 % | 19.0 px | 0.26 % | 16.1 % |
| GEMSDOE33 | 0.2632 | 41,865 | 0.00 % | 58.0 % | 18.8 px | 0.30 % | 16.8 % |
| GEMSDOE25 | 0.2600 | 44,090 | 3.86 % | 56.0 % | 17.9 px | 0.33 % | 17.7 % |
| GEMSDOE30 | 0.2600 | 44,090 | 3.86 % | 56.0 % | 17.9 px | 0.33 % | 17.7 % |
| GEMSDOE24 | 0.2477 | 60,069 | 10.43 % | 51.4 % | 15.4 px | 0.55 % | 24.0 % |
| GEMSDOE27 | 0.2449 | 61,328 | 13.35 % | 49.7 % | 14.4 px | 0.82 % | 24.4 % |

Rank correlation of reported score with each measured covariate:

* dot count: **−0.967** (slope −0.00119 per 1,000 dots)
* fraction of dots more than 15 px from the catalogue: **+1.000**
* clumping (≥3 neighbours within 3 px): **−0.92**
* fraction of dots within 2 px of the catalogue: **−1.000**
* area covered: −0.95

All 36 pairs among the nine score 97.5–100 % on the literal 3-px overlap rule, against a
chance level of 15.3–18.5 %. They are one covering of one support, sampled nine times.

**Conclusion.** The nine are not nine geological ideas. They are nine points on a
one-parameter family whose only free variable is how many dots are spent, and GEMSDOE32's B2
is the smallest member with the cleanest spacing. That is why 0.2778 is the best of the nine
— and it is a position, not an insight.

## 3. Why two local instruments disagree with the leaderboard (EXP2)

`evidence/kp1_exp2_external.json`. The mandated instrument (hide part of the catalogue,
recover it from features) ranks the nine **exactly backwards**: Spearman −1.0, because it
rewards recovering traces that are already in the catalogue while the competition scores
faults that are *not*. That inversion was measured in an earlier session and is recorded, not
hidden.

This session built a *positively oriented* replacement: `derived_sgmc_faults_100m_u8.tif` is
an independent state-compilation fault inventory in the same footprint with only 3,978 cells
coinciding with the catalogue; after removing the 3-px catalogue corridor, **62,122 cells**
remain. Four arms, leave-one-quadrant-out, emissions through the same allocator and budget
ladder:

| arm | DTI @ 5k | @ 40k | ranking AUC (held-out) |
|---|---|---|---|
| uniform random dots | 0.0372 | 0.1432 | — |
| trained on catalogue faults | 0.0027 | 0.0197 | 0.495 |
| trained on off-catalogue faults | 0.0098 | 0.0546 | **0.749** |
| trained on both | 0.0070 | 0.0482 | 0.718 |

Two things fall out, and they matter more than any single score:

1. A model with real held-out ranking skill (AUC 0.749) still **loses to random dots** at the
   same budget, because the metric pays for coverage and charges only 0.2 per dot. Precision
   must be very high before targeting beats spreading. This is the mechanism that produced
   the "dotted" submission family in the first place.
2. A catalogue-trained detector scores **three times worse than random** on off-catalogue
   faults (0.0027 vs 0.0372). Training on the catalogue actively teaches the detector where
   the truth is *not*.

Leakage canary: max AUC after label permutation 0.55; no alarm.

## 4. The lane: K-PROXY-DETECT

Hypothesis. Faults that are missing from the catalogue are thermo-tectonic conduits:
structures that satisfy four independent conditions at once —

1. **multi-field structural consensus**: magnetic horizontal gradient, tilt derivative,
   upward-continued-to-150 m gradient, isostatic-gravity horizontal gradient and basement step
   all see a boundary;
2. **geomorphic freshness**: a scarp in the 1 m LiDAR roughness/step metrics and in the
   detrended DEM slope;
3. **fluid conduit**: proximity to mapped springs and water wells (hydrothermal alteration
   follows permeability, and permeability here is fault-controlled);
4. **alteration halo**: low Th/K and low U/K, the potassium-metasomatism signature of a
   damage zone.

The surface is the geometric mean of the four terms, so a cell cannot be carried by one field
alone. Named non-fault mimics each break at least one term: buried pluton margins are round and
dry, alluvial contact springs have no structural edge, metamorphic fabric is broad and has no
scarp, landslides have a scarp but no edge consensus.

Extras over the prior lanes: the consensus is multiplicative rather than additive; the
catalogue corridor is excluded rather than used as a prior; the deep-basin floor is suppressed;
and the dots are forced to a 4-px minimum separation so each dot buys new truth credit instead
of re-buying a neighbour's.

## 5. The candidate

`docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif`

* 32,000 dots, hard 4-px separation, 0.00115 clumped, 0.00 % within 2 px of the catalogue,
  55.5 % more than 15 px away, 14.3 % of the footprint covered.
* Format: 15/15 saved-byte checks (`vendor/gems57/validate.py`), 12,279,160 finite cells,
  values in [0,1], zeros outside the footprint, zero positive pixels on mapped catalogue cells.
* Uniqueness: max |Spearman| 0.0076 (limit 0.90), max 3-px overlap 26.5 % (limit 70 %).
* Projection: 0.2789, LOO [0.2762, 0.2816], parameter bootstrap [0.2757, 0.2846],
  +0.0020 versus the champion. **PROJECTED — not a score.**
* Off-catalogue instrument: 0.0764 versus 0.0640 for matched random dots (+19.3 %), with a
  block bootstrap of the difference of +0.0109 [−0.0034, +0.0260], 92 % of draws positive.

## 6. What would beat 0.2778, and what would beat 0.4413

At *fixed* surface quality more dots is always better, so nobody wins on dot count alone. What
the nine files show is that their last dots carry a lower hit rate, which is why deleting them
helped. The candidate therefore has to be a better *surface*, not just a smaller one:

* matching 0.2778 with 32,000 dots instead of 37,654 requires a surface **13.5–15.3 % more
  accurate** than the champion's, depending on the (unknown) size of the private truth;
* 0.3195 requires **1.31–1.35×** the champion's hit rate;
* 0.4413 requires **1.84–1.87×** it; 0.4544 slightly more.

The theoretical ceiling of the submission format is 0.5556, because `beta = 0.8` taxes every
uncovered truth cell. So 0.4544 is 82 % of the maximum and 0.2778 is 50 %.

## 7. Limits, stated plainly

1. **No organizer receipt.** The projection is an OLS on nine user-reported scores, n = 9,
   associational, and collinear in its two predictors; the defensible working range is
   0.24–0.31 and the model cannot see surface quality at all.
2. **The projection interval is not a predictive interval.** LOO RMSE of 0.0014 measures
   internal fit on nine points that lie almost exactly on a plane, not the chance of the
   private truth resembling the catalogue.
3. **The external instrument does not reproduce the leaderboard.** It ranks the nine at
   rho −0.34 (p 0.36), so it can only be used to compare a surface with matched random dots.
4. **The literal uniqueness rule is saturated** for this raster family (all 36 pairs ≥ 97.5 %).
   The candidate passes it at 26.5 %, but a reader should know that the rule cannot distinguish
   "different work" from "same method" here.
5. **The private truth size is unknown**, which is why every metric inversion is reported at
   three assumptions instead of one.
6. **Data provenance.** The competition data available in this checkout is hash-pinned and
   byte-verified but was obtained from a public mirror, not from the authenticated competition
   page; the official sample grid was therefore not available for a cross-check.
