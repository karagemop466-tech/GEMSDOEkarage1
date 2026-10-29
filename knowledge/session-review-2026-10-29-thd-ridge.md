# Session review — `arena/c65129cb-gemsdoekarage1` — 29 October 2026

**Verdict: NEGATIVE / DO NOT SUBMIT.** One unique, format-valid GeoTIFF was generated
(`docs/downloads/DO-NOT-SUBMIT_gemsdoekarage1-thd-ridge-collar-20261029-b_pct98-5734dots-zeros.tif`).
It is **not** cleared: it fails the literal 70%/3-px registry gate, and its holdout DTI is far
below the repository's best recorded holdout value. No weekly slot was selected or spent. No
leaderboard score is estimated.

Machine-readable record: [`evidence/session_thd_ridge_run_card_20261029.json`](../evidence/session_thd_ridge_run_card_20261029.json).

---

## 1. Answer: why did GEMSDOE32 B2 report 0.2778, and can it be beaten?

**What the record shows (re-derived this session from the restored mirror rasters).** B2
(37,654 dots) is a strict subset of GEMSDOE25 (44,090 dots); the 6,436 removed dots are **all**
within 2 px of the mirrored catalogue. Background: [`knowledge/02_why_gemsdoe32_b2_scored_0.2778.md`](02_why_gemsdoe32_b2_scored_0.2778.md).
The 0.2778 value is **USER-REPORTED / UNVERIFIED**: no organiser receipt is in the repo, and
a mask relationship does not establish why the score changed.

**Mechanism (judgement, from the official metric).** The official distance-weighted Tversky
index with α = 0.2, β = 0.8 and a 3-px triangular kernel is stated on the official problem
page: a false-positive term is `Σ p(x)·[1 − max_g k(d(x,g))]` over every pixel with `p > 0`, and
a true-positive term is `Σ_g max_x p(x)·k(d)` ([DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)).
Because α < β, a dot costs little when it is far from the ground truth, and every
ground-truth point must be covered by a nearby dot to earn credit. Removing a dot that sits
on a *known* trace removes its false-positive cost if the organiser does not score known
faults. Whether known faults are masked is the key open question. The repo cites a DrivenData
staff thread, which I did **not** fetch this session: [thread 11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)
(**unverified this session**).

So a catalogue collar can gain score by thinning false positives, but it can also delete true
coverage on new faults that run close to a mapped trace. That tradeoff is exactly what a
holdout must measure. A collar is not a free improvement.

**Can we beat 0.2778?** Not demonstrated. Neither this session's candidate nor any prior
candidate in the repo has a holdout result that exceeds B2's reported value, and a holdout
value cannot be converted into a leaderboard estimate (see §4). The honest answer is that
the question is open and our instrument cannot yet resolve it.

## 2. What was generated and tested

| Item | Result | Label |
|---|---|---|
| Candidate | 3×3 local maxima of `tmi_hg` (horizontal gradient of total magnetic intensity), footprint percentile threshold, 3-px collar around mapped faults | method, label-free ridge score |
| Arms (experiments 1–2) | pct 99.0: HOLDOUT-DTI 0.0046 [0.0014, 0.0075]; pct 98.0: **0.0093 [0.0042, 0.0136]** | HOLDOUT-DTI, evaluator `gems57-pooled-hide-v2`, 22,641 withheld positives, bootstrap over 8 fold cells |
| Strain-ridge hypothesis H1 (experiment 3, holdout only) | HOLDOUT-DTI **0.0129 [0.0031, 0.0201]**, 22,641 withheld positives. CIs overlap the magnetic arm; no significant gain | HOLDOUT-DTI |
| Final raster | 5,734 dots, float32, EPSG:32611, 3730×3292, 100 m, values exactly {0, 1}, zero outside footprint, zero dots on mapped catalogue | file validator |
| Exact-duplicate test | byte-unique and pixel-unique vs the 25 local registry rasters (**not** every listed submission; those without a local file were not checked) | REGISTRY-MEASUREMENT |
| Spearman (full footprint) | worst 0.0072 (limit 0.90): **pass** | REGISTRY-MEASUREMENT |
| 3-px dot overlap | worst **99.91%** vs `13GEMS` lattice (limit 70%): **literal fail**; next highest 44.72% (Hedge-v2) | REGISTRY-MEASUREMENT |
| Jaccard | worst 0.0023 (diagnostic only) | diagnostic |

**Why the tuning arm is optimistic:** I picked arm B on holdout DTI between two arms, so its
0.0093 is a selected value. The 3rd experiment (H1) was pre-registered as a single arm.

## 3. Leakage canary

Each of the 19 `training_features` bands was tested alone against the holdout truth (AUC,
averaged over the 8 `all` fold cells). The largest direction-invariant AUC is 0.565
(`tc`; `det_elev_slope` is next at 0.564). Every band passes the 0.90 threshold. This means no single band separates
withheld faults from background at all. That is a finding about the **instrument**: the
hide-and-recover holdout has very low single-feature dynamic range, so small DTI differences
(0.005 to 0.013) cannot be interpreted with confidence. See
[`evidence/thd_ridge_candidate_20261029.json`](../evidence/thd_ridge_candidate_20261029.json).

## 4. The duplicate gate is non-informative (irregularity — flagged for owner review)

The literal rule in `AGENTS.md` and the parallel-run protocol is: if more than 70% of a
candidate's dots fall within 3 px of one registry raster's dots, log a duplicate and stop.
The 13GEMS lattice raster covers **99.87%** of the footprint within 3 px
([`evidence/lattice_gate_null_check_20261029.json`](../evidence/lattice_gate_null_check_20261029.json)).
Uniformly random dot sets fail the gate in **200 of 200 draws** at 1,000, 37,654 and 60,988 dots
(mean overlap 99.86%–99.87%; the lowest single draw was 99.5%). **The gate therefore fails pure noise.** It cannot distinguish a
real candidate from a random one, so the stop decision says nothing about candidate quality.

I did not change the gate. The protocol forbids evading it, and a relaxed gate is an owner
decision. **Recommended for the owner:** (a) redefine the overlap test on a space where noise
does not saturate (for example, exact-pixel or 1-px Jaccard against each registry raster,
with the null distribution reported), or (b) retire the 13GEMS lattice as a registry member
because it is effectively a full-footprint surface rather than a dot set. Either choice must be
made by the owner before any candidate can be cleared.

## 5. Hypotheses (ranked; expected gain and cost are judgement, not measurement)

Every layer name below is read from the band descriptions in `data/training_features.tif`.
"Repo mentions" counts come from `grep` over `src/`, `scripts/`, `vendor/gems57/`,
`knowledge/` and `docs/research/`; a non-zero count means the layer is used somewhere, not that
the hypothesis was tested.

| Rank | Hypothesis | Layers | Physical signature targeted | Non-fault mimic | Why off-catalogue | Repo mentions | Status |
|---|---|---|---|---|---|---|---|
| 1 | Shear-localisation ridge | `geod_2ndinv`, `geod_shearrate` | strain-rate concentration on active structures | GNSS/InSAR interpolation artifacts at network edges; anthropogenic deformation (pumping, mining) | the signal is independent of the magnetic catalogue | 3 src/scripts, 4 docs | **Tested (H1), negative-to-inconclusive** |
| 2 | Magnetic edge-ridge (label-free) | `tmi_hg`, `tmi_vg` | lateral susceptibility contrast | lithologic and intrusive contacts; cultural magnetic noise | excludes catalogue by a 3-px collar | `tmi_vg` 4 src/scripts | **Tested (arms A/B), negative** |
| 3 | Density-contrast corridor | `iso_grav_anom_hg`, `iso_grav_anom_vg` | fault-bounded density contrast | basin-margin lithology; compensation residuals | gravity independent of magnetic catalogue | 7 src/scripts | Not tested; largely explored in repo — low novelty |
| 4 | Seismicity alignment | `ieq_n100a15`, `deq_n100a15` | hypocentre alignment | induced seismicity around fields | coarse 100-km-radius field; low spatial resolution | 3 src/scripts | Not tested; low expected gain |
| 5 | Basement step | `depth_to_base_surf` | depth-to-basement discontinuity | sedimentary-thickness changes | — | 13 src/scripts | **Already implemented (BB-STEP)** — not new |

**Recommendation.** Hypothesis 1 is the top-ranked candidate. It was tested, and it did not
show a clear gain over the magnetic arm. The next worthwhile step is a higher-resolution
strain analysis, which needs data we do not have (see §7).

## 6. Official facts verified this session (fetched in this sandbox)

- **Metric and formula**: [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — distance-weighted Tversky, α = 0.2, β = 0.8, R = 300 m (3 px at 100 m).
- **Submission format**: same page. Float32 single-band GeoTIFF, EPSG 32611, 100 m, same bounds, values in [0, 1], data outside bounds null or NaN.
- **Two-round structure and single-submission rule**: same page (Initial Prize Round then Final Prize Round). "Competitors must choose a **single** submission for scoring across both rounds before the deadline."
- **Official rules document (September 2026)**: [NLR-hosted PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) — Phase 1 pool $50,000 (top five on private test labels); Phase 2 pool $250,000 (top five on the updated label set).
- **Public leaderboard snapshot (fetched 29 Oct 2026, relative timestamps only)**: [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — #1 **0.4544**; #2 0.3916; #47 **0.3195** (confirmed); **0.4413 does not appear in the top 50**, so the user's 0.4413 figure is **unverified**. The leaderboard is the *public* split. Final ranking depends on the private split and the expanded label set.
- **Not fetched this session**: the epsg.io page and the DrivenData forum thread. Repo references to them are unverified here.

## 7. Limitations and what is needed

1. **Organiser data is not authenticated.** Restored files are hash-pinned mirrors. Sizes and hashes match the manifest; organiser authenticity is not established. Local label files: `labels.tif` and `existing_faults.tif` are **byte-identical** (SHA-256 `7ba308cc…`), consistent with labels equal to the mapped catalogue, but this must be confirmed against the organiser's own files.
2. **Hidden test faults are not available.** Every holdout score is a proxy built from the known catalogue. It is not the competition's scored set.
3. **Holdout dynamic range is low** (§3), so small differences do not resolve.
4. **Gate is non-informative** (§4). A decision needs the owner.
5. **Sentinel pixels** in `training_features`: **3,073 distinct footprint pixels** carry the `-3.4028235e+38` nodata value in at least one band (verified: [`evidence/lattice_gate_null_check_20261029.json`](../evidence/lattice_gate_null_check_20261029.json)). The candidate excluded them. The per-band sum (58,171) counts each pixel once per band and must not be read as a pixel count.
6. **No method lane is assigned**: `registry/template.json` has `method_lane: null`, so this run is not a lane result.
7. **Weekly submission cap and deadline** are not checked here. Repo notes that earlier sessions recorded them, but I did not verify them on the submission page this session.

## 8. Irregularities flagged for review

- **Gate design** (§4): a literal rule that fails pure noise.
- **Leaderboard figure 0.4413** in the request is not on the official top-50 page.
- **User-reported scores** (0.2778, 0.2750, 0.2710, 0.2708, 0.2632, 0.2600, 0.2477, 0.2449) are not in the official leaderboard view; they remain unverified.

## 9. Next steps (ordered)

1. Owner decision on the duplicate gate (§4). Until it is made, no file in this repo can be cleared.
2. Obtain the organiser-authenticated data set (the DrivenData data tab requires login) so the restored files can be checked against the organiser's own hashes.
3. Obtain a higher-resolution strain or seismicity source only if it is free and official, and verify its licence before use.
4. Stop criterion: no new candidate is generated until the holdout dynamic range is shown to resolve differences larger than the CI.
