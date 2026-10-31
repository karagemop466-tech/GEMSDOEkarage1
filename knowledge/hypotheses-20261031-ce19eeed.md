# Hypotheses — 31 Oct 2026 (session `arena/ce19eeed-gemsdoekarage1`)

> Companion to `knowledge/hypotheses-20261031.md` (another session's preregistration slate). This file records **our** experiments: H-E1b and H-E2. Our H-E1b is a different protocol from the H-E1 run in `evidence/exp_h_e1_euler_20261031.json` (session `arena/he1-euler-gemsdoe-20261031`). See the cross-session comparison below.

Status: **no file cleared; no submission slot selected or spent.** Every number below is
**HOLDOUT-DTI** (evaluator `gems57-pooled-hide-v2`, 16 cells, withheld positives 45,260, 95% CI as stated).
No ORGANIZER-CONFIRMED number exists in this session. Nothing here is a leaderboard projection.

## Ranking (expected DTI gain × implementation cost)

Expected gain is qualitative. It is not a score and is not reported as one. Cost is the
engineering effort in this repository with the shared template.

| Rank | ID | Mechanism | Field | Expected gain | Cost | Overlap with existing code (grep-verified) | Status |
|---|---|---|---|---|---|---|---|
| 1 | **H-E2** | Euler N=0 depth-cluster contacts (2.1 km windows, 300–3000 m) | `iso_grav_anom` (band 13) | Small, positive vs random | Low: reuses `euler.py` and the runner | No Euler code existed before `euler.py`. `iso_grav` appears in 9 code files, none of them as an Euler input | **Tested. Holdout-positive vs random, gate-blocked. Negative under the pre-registered rule. Not cleared.** |
| 2 | **H-E1** | Same method on the official magnetic field | `tmi` (band 14) | Negative | Low | Same as above | **Tested. Negative: holdout below random.** |
| 3 | H-E3 | Joint TMI–gravity Euler coincidence: keep solutions where both fields agree within 300 m | both | Unknown; the joint solutions are sparser | Medium: two surfaces and a coincidence join | Not checked against the bbstep/signedoffset lanes | Not implemented. Needs the overlap check first. |
| 4 | H-E4 | Euler with structural index N=1 on TMI (thin dikes/sheets) | `tmi` | Unknown; sensitivity of H-E1b | Low | Same as H-E1b | Not run. Low novelty, and it would consume a slot of the 3-experiment budget. |
| 5 | H-S1 | Earthquake-density lineaments from `deq_n100a15` / `ieq_n100a15` | seismicity features | Low: the 100 km smoothing scale is far coarser than the 300 m kernel | Low | The two features appear in 2 code files | Deprioritised. |

Carried over, not re-tested here: **H-R1** (K-th magnitude edge, `scripts/run_h_r1_kth_magedge.py`,
`evidence/exp_h_r1_kth_magedge_20261030.json`): HOLDOUT-DTI 0.0433 vs random null 0.0446, paired
difference −0.0029, CI [−0.0071, +0.0009]. Negative, not cleared. The prior strain ridge candidate
(0.0481 vs random 0.0449) was not a pass. The 30 Oct ranking placed H-R1 first.

Note on the random null: the matched-random null depends only on the footprint, the dot count and the
seeds (101/202/303). It is therefore identical (0.0446) for every 37,654-dot candidate in this
session. H-E2 (0.0479) and H-R1 (0.0433) are measured against the same null. Their difference on the
same 16 cells (+0.0046) has not been tested with a paired CI.

## H-E1b — Euler N=0 contacts on TMI, 21 px window, 300–3000 m, unsmoothed (tested, negative)

- Mechanism: the Euler homogeneity identity solved in 21×21 px windows (`half=10`), keeping solutions with 300–3000 m depth. Solutions per cell give a depth-cluster density, and the top 37,654 peaks are placed with 2.8 px spacing.
- Result: pooled HOLDOUT-DTI **0.0284** (CI [0.0245, 0.0313]). Random null mean **0.0346** (seeds 101/202/303). Paired difference **−0.0065**, CI [−0.0099, −0.0031].
- Only **25,741** of 37,654 dots were placed. The clean run places dots on real density peaks only. Dots on zero-density cells: 0.
- Verdict: negative. The candidate scores significantly below random dots.
- Artefacts: `archive/research-he1b-20261031/karage1-he1b-euler-tmi-37654-20261031-zeros.tif` (and `-nan.tif` twin). Evidence: `evidence/exp_h_e1b_euler_tmi_20261031.json`, run card `evidence/run_card_h_e1b_20261031.json`. Reproduced exactly after the merge.
- Named non-fault mimic: lithologic and intrusive contacts, basin-margin magnetic steps, and flight-line levelling seams.

## Cross-session comparison: H-E1 (other session) vs H-E1b (this session)

The two sessions pre-registered the same hypothesis (TMI, Euler N=0 contacts) with different protocols. Their holdout results disagree in sign. Both use `gems57-pooled-hide-v2`, 16 cells, 45,260 withheld positives, and the same matched random null (0.0446 for 37,654 dots; 0.0346 for 25,741 dots).

| Protocol | Window | Depth band | Density | Dots | Pooled HOLDOUT-DTI | Paired vs null (CI) | Verdict and failing criteria |
|---|---|---|---|---|---|---|---|
| H-E1 (`arena/he1-euler-gemsdoe-20261031`) | 11 px | 50–2000 m | Gaussian-smoothed S | 37,654 | 0.0507 | +0.0058 [+0.0034, +0.0080] | negative: literal 70% registry gate only |
| H-E1b (this session) | 21 px | 300–3000 m | unsmoothed peaks | 25,741 | 0.0284 | −0.0065 [−0.0099, −0.0031] | negative: below random; paired CI below zero; literal gate; league bar |

Interpretation: the Euler/TMI signal is **protocol-sensitive**. The window, depth band and density smoothing decide whether it beats random dots. Neither result should be promoted, and neither can be quoted as "the H-E1 answer". A pre-registered H-E1 must fix one protocol before a result is looked at.

## H-E2 — Euler N=0 contacts on isostatic gravity (tested, gate-blocked)

- Mechanism: the same method on `iso_grav_anom`. Gravity anomalies are potential fields, so the same Tz filter applies. Full budget: 37,654 dots, with 1,822,268 accepted solutions.
- Result: pooled HOLDOUT-DTI **0.0479** (CI [0.0430, 0.0505]). Random null mean **0.0446**. Paired difference **+0.0028**, CI **[+0.0005, +0.0051]**, so the lower bound is above zero.
- Canary: maximum direction-invariant AUC **0.586** (raw field), 0.545 (|Tz|), 0.526 (density). All below the 0.90 alarm.
- Uniqueness: surface max Spearman **0.033**. Against the nine focus sites: max dot overlap 19.6% within 3 px, max Jaccard 0.005. Against the 52 local TIFs, the literal 70% gate trips on the halo raster and 13GEMS lattice (see review items).
- Failed criteria: `beats_every_local_candidate_on_same_cells` (the catalogue-trained 0.2708 leader) and `registry_dot_overlap_le_0_70` (dense rasters). Pre-registered verdict: **negative**.
- Named non-fault mimic: basin-margin and sediment-basement density steps, intrusive density contacts, topographic-correction residuals at high-relief edges.
- Artefacts (archive only, not `docs/downloads/`): `archive/research-he2-20261031/karage1-he2-euler-gravity-37654-20261031-zeros.tif` (sha256 `830c6ddf…`) and its `-nan.tif` twin. Validator: all checks passed. Note: "H-E2 Euler on isostatic gravity (N=0, 2.1 km win, 300-3000 m) label-blind; RESEARCH ONLY; holdout-scored" (104 characters).

## Review items for the owner (not changed here)

1. **Literal 70% registry gate.** Dense registry rasters (the halo damage zone with 5.1 million positive cells, and the 13GEMS lattice at 99.996%) overlap any dot set. The runner itself notes "fail by construction". The gate should be restricted to sparse, dot-count-matched rasters, but this is an owner decision.
2. **League bar.** The bar compares against every local TIF, including catalogue-trained rasters. A label-blind candidate cannot pass it. A label-blind league should be used.
3. **Random null.** The null is uniform over the footprint. A structure-aware candidate can beat it for generic reasons, because it places dots where the magnetic or gravity signal is active. A stronger control matched to that density is needed before any positive result is trusted. The H-E2 margin is small (+0.0028) and could be explained this way.
4. **Holdout scope.** The holdout scores recovery of withheld visible catalogue segments. It does not measure new faults. A holdout positive is not a forecast of the organizer score.
5. **GEMSDOE32_B2** scores 0.0047 on the same 16 cells, below random. The holdout cannot judge B2 fairly. B2 removes dots near mapped catalogue traces, which is the very signal this holdout measures.

## Next steps (in order)

1. Owner review of items 1–3 above before any further promotion attempt.
2. If the owner approves a stronger null: rerun H-E2 against a density-matched random null. Do not rerun H-E1b or H-E2 with new parameters, because the budget is 3 experiments and 2 are used.
3. H-E3 only after the overlap check against the bbstep and signedoffset lanes.
4. No slot is selected here. Promotion is a separate selector step.
