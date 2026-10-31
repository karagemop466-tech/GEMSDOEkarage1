# Why GEMSDOE32's B2 scored 0.2778 — and what it would take to beat it

Short answer: **because it is the smallest member of a one-parameter family, not because it
contains a different geological idea.** Everything below is measured in
`evidence/kp1_exp1_forensics.json` and derived in `evidence/kp1_metric_analysis.json`.

## 1. The nine are one family

All 36 pairs among the nine focus rasters overlap 97.5–100 % on the literal 3-px rule, against
a chance level of 15.3–18.5 %. Expressed as enrichment over chance that is 5.3–6.5×, and the
same support appears at every dot count from 37,654 to 61,328. Nine rasters built by nine
different prompts land on the same lines because they are all built by the same lineage of
methods: catalogue anatomy, then Poisson sampling along the resulting lineament lattice.

Once that is understood, the only thing left that can differ is **how many dots** are spent,
and that is almost perfectly monotone in the reported score:

| | dots | reported |
|---|---|---|
| GEMSDOE27 | 61,328 | 0.2449 |
| GEMSDOE24 | 60,069 | 0.2477 |
| GEMSDOE25 / 30 | 44,090 | 0.2600 |
| GEMSDOE33 | 41,865 | 0.2632 |
| GEMSDOE31 | 40,199 | 0.2708 |
| GEMSDOE36 | 38,854 | 0.2750 |
| GEMSDOE28 | 37,660 | 0.2710 |
| **GEMSDOE32 (B2)** | **37,654** | **0.2778** |

Spearman −0.967, OLS slope −0.00119 per 1,000 dots. The one inversion (28 below 36) is the
file with 42 % of its dots clumped, which the clumping covariate explains (Spearman −0.92).

## 2. Why fewer dots won

For a binary dot field the metric is exactly

    DTI = T / (alpha·(n − M) + beta·|G| + T),  alpha = 0.2, beta = 0.8.

Adding one dot with truth credit `dT` and self-credit `m` raises the score iff

    dT > alpha·(1 − m)·s / (1 − s),

which at s = 0.2778 is **0.0769**. A dot must therefore be within 300 m of a truth cell about
7.7 % of the time to pay for itself. Inside this family the marginal dot — the one the emitter
adds last, after the lineament lattice is already covered — falls *below* that bar. Deleting
such dots raises the score. That is precisely what the B2 lineage did to its 44,090-dot parent:
it removed 6,436 dots and gained about +0.018.

So 0.2778 is not a discovery about faults. It is the point where the family's last dot is
closest to break-even. The same argument predicts that deleting a few thousand more of B2's
dots would raise the score slightly — and that a genuinely better *surface*, not a smaller
file, is the only way to move much further.

## 3. What the leaderboard numbers actually require

Inverting the metric at each reported score (three assumptions about the unknown truth size,
because the private truth size is not published):

| target | credit needed per dot at n = 37,654 | hit rate needed | multiple of B2 |
|---|---|---|---|
| 0.2778 | ~0.53 | 0.21 (|G| = 61k) | 1.00 |
| 0.3195 | ~0.62 | 0.28 | ~1.33 |
| 0.4413 | ~0.90 | 0.39 | ~1.86 |
| 0.4544 | ~0.93 | 0.40 | ~1.91 |

And the format's ceiling is `1/(1 + beta) = 0.5556`, reached only when every truth cell is
covered by a dot. 0.4544 is 82 % of that ceiling; 0.2778 is 50 %.

## 4. So can it be beaten?

**Yes, but not by geometry.** Two things can move the score:

1. **A better surface.** Raise the per-dot truth rate above the bar. The candidate in this
   session emits 32,000 dots instead of 37,654, so it needs to be 13.5–15.3 % more accurate
   than B2 just to draw level, and 1.3–1.9× more accurate to reach the leaderboard numbers.
   That is a modelling problem, and this repository has never demonstrated it.
2. **A better truth guess.** The private truth is *not* in the catalogue. Anything that
   supplies independent expert fault traces (state compilations, other national databases,
   published maps) places dots where the truth actually is, and that is the only route to a
   step change rather than a percent. The candidate's reference inventory
   (`derived_sgmc_faults_100m_u8.tif`) exists precisely because that route is real — 79,615
   of its cells are more than 4 px from anything in the catalogue.

What will *not* work: another pass of the same lattice with a different dot count. That is what
produced 0.2449 → 0.2778, and it has ~0.03 of headroom in total.

## 5. Where the new candidate sits

| | B2 | this session |
|---|---|---|
| dots | 37,654 | 32,000 |
| clumped (≥3 within 3 px) | 0.26 % | 0.115 % |
| ≤2 px from catalogue | 0.00 % | 0.00 % |
| >15 px from catalogue | 58.4 % | 55.5 % |
| area covered | 15.1 % | 14.3 % |
| max 3-px overlap with the other eight | ~98 % | 26.5 % |
| projected score | 0.2778 (measured) | 0.2789 (projected) |

The overlap row is the one that matters for the uniqueness question: the candidate is the only
raster in the set that is not a member of the family.
