# Session review `arena/23ef16f9` (2026-10-29)

**Verdict: NEGATIVE / DO NOT SUBMIT. No TIF was generated for upload.**
Nothing in this session is a leaderboard estimate. Every score below is either an
ORGANIZER-CONFIRMED value from the live leaderboard or a USER-REPORTED / UNVERIFIED value.

## 1. Why no new TIF was generated

A file is OK to download and submit only when it passes every gate. Three gates block every candidate.

1. **No holdout is possible.** The DrivenData data tab redirects to a login page
   (<https://www.drivendata.org/accounts/login/?next=/competitions/306/competition-doe-gems/data/>,
   fetched 29 Oct 2026). The sandbox cannot reach DrivenData, USGS, or ScienceBase. Without
   `training_features.tif` and the fault labels there is no feature stack, no holdout, and so no HOLDOUT-DTI.
2. **The literal 70% / 3-px duplicate gate cannot be passed at this dot count.** The recorded 13GEMSDOE
   calibration lattice (witness numbers in `registry/registry_roles.json`) leaves only 6,649 footprint pixels
   beyond 3 px of the lattice. A raster with N dots needs at least 0.3N of its dots in those pixels to pass.
   So the gate is satisfiable only for N ≤ **22,163**. Every dotted candidate in the top band (37,654–44,090 dots)
   fails. Verified by `scripts/registry_pair_check.py` →
   [`evidence/registry_pair_check_23ef16f9.json`](../evidence/registry_pair_check_23ef16f9.json).
   This is a count-driven saturation, not a uniqueness test. The official rules do not contain a 70% rule
   (checked in the sections read: §1–§3.2 of [the NLR rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
   and the metric/format section of the [problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)).
   **Owner decision required:** whether this internal gate binds at all.
3. **No method lane is assigned.** The protocol's lane paragraph is absent (`registry/template.json`: `method_lane: null`).

Generating a raster now would produce an unvalidated file with an unknown score. Under the protocol that is
a negative result, and a downloadable file would invite an accidental slot spend. So no file was
created.

**Update after merging `main` (29 Oct 2026).** `main` now contains core inputs restored from pinned GitHub mirrors (session `547a9b56`, [`evidence/core_data_verification_20261029.json`](../evidence/core_data_verification_20261029.json)). Their SHA-256 values match the pins, but the pins are not organizer authentication. This session did **not** run a holdout on them. Reasons: the lane is unassigned, the mirrors are not organizer-authenticated, and redistribution of login-walled competition data needs owner confirmation (§7.9).

## 2. Why GEMSDOE32 `h33-h33-2-b2` reported 0.2778, and whether it can be beaten

**Verified facts (checked by me on the registry bytes, not from notes):**

| Fact | Value | Check |
|---|---|---|
| Grid of both files | EPSG:32611, 3292×3730, 100 m, origin (243350, 4508550), float32, no nodata, all finite, values {0,1} | `registry/GEMSDOE25_d28.tif`, `registry/GEMSDOE32_B2.tif` |
| GEMSDOE32 dots | 37,654, sha256 `c55bafc4…7ab6fa9` (matches the repo record) | `scripts/registry_pair_check.py` |
| GEMSDOE25 dots | 44,090, sha256 `3e78737f…9cc30` | same |
| Subset relation | **Every GEMSDOE32 dot is in GEMSDOE25.** GEMSDOE25 has 6,436 extra dots. Forward overlap 100%. | same |

**Analysis (PhD-level reasoning; mechanism inferred from the metric, not measured against labels):**

- **The metric rewards recall.** With α=0.2 and β=0.8, a missed ground-truth (GT) pixel costs four times a false
  positive. The official metric is in [the problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
- **Dot pruning is the only controlled experiment in the registry.** GEMSDOE32 is GEMSDOE25 with 6,436 dots
  removed. Both scores are user-reported, so the 0.0178 gain (0.2600 → 0.2778) is unverified. If the gain is
  real, the removed dots cost more false-positive weight than they gave true-positive credit. In other words,
  they were mostly far from GT. The mechanism is pruning of low-posterior dots, which is an inference from the metric.
- **Inclusion threshold (already in the repo; re-checked here).** For a binary prediction with α+β=1, adding one
  pixel with hit-probability q changes the denominator by exactly α, so it helps iff q > α·DTI. The repo already
  states this as `breakeven_kernel_credit` in [`src/gemsk/metric.py`](../src/gemsk/metric.py) and in the docstring of
  [`src/gemsk/emission.py`](../src/gemsk/emission.py). This session did not discover it. It re-checked the rule on
  synthetic posteriors: [`scripts/metric_threshold_check.py`](../scripts/metric_threshold_check.py) →
  [`evidence/metric_threshold_check_23ef16f9.json`](../evidence/metric_threshold_check_23ef16f9.json). The best threshold was
  0.06 on all five seeds, against a rule value of 0.058–0.061. This is **synthetic evidence only**, and the official
  metric has a 300 m kernel, so the rule is approximate for the real task.
- **Public versus private split.** The leaderboard is scored on the public test set. The final prize uses a
  private set, and the rules say public and private scores may differ
  ([NLR rules §3.2](https://docs.nlr.gov/docs/fy26osti/96647.pdf)). A 0.0178 gap on the public split
  may not hold on the private split.
- **Why the catalogue gap matters.** The USGS Quaternary Fault and Fold Database is scoped to faults that are
  sources of M>6 Quaternary earthquakes, and its traces are "simplified representations"
  ([USGS faults page](https://www.usgs.gov/programs/earthquake-hazards/faults)). Smaller or
  low-displacement structures, which geothermal permeability often follows, are therefore absent from the
  training labels. That is why the hidden test faults are plausibly small. This is an interpretation, not a measured result.

**Can 0.2778 be beaten?** Possibly, but nothing in this session shows it. The live #1 is 0.4544, so the 0.2778
file is far below the leader. Beating it requires a validated holdout, which is blocked (§1).

## 3. Nine-site executive summary (verified)

The live table is in [`docs/executive-summary.html`](../docs/executive-summary.html) and is regenerated from
`scripts/render_site.py`. Scores there are USER-REPORTED / UNVERIFIED, from
[`registry/user_reported_scores_20261029.json`](../registry/user_reported_scores_20261029.json). Uniqueness is
measured on the SHA-pinned mirror rasters in `evidence/site_lineage_verification_20261029.json`. I
re-verified **only** the GEMSDOE25/GEMSDOE32 pair in this session. The other seven sites were not re-checked
here.

| Site | Best file | User-reported score | Unique vs the other 8 sites? | Submit? |
|---|---|---|---|---|
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | 0.2778 | No (subset of GEMSDOE25) | **No** (already submitted; do not resubmit) |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 | No (97.6% within 3 px of GEMSDOE27) | No |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 | No (100% within 3 px of GEMSDOE24) | No |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 | No (100% within 3 px of GEMSDOE24) | No |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 | No (99.7% within 3 px of GEMSDOE27) | No |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 | No (parent of GEMSDOE32) | No |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 | No (identical dot mask to GEMSDOE25) | No |
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 | No (100% within 3 px of GEMSDOE25) | No |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 | No (98.0% within 3 px of GEMSDOE24) | No |

No site is cleared. Every "unique" column reads No.

## 4. Live leaderboard (ORGANIZER-CONFIRMED, fetched 29 Oct 2026)

Source: [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
Leaderboard rows are participant-level only. No file names are shown, so no GEMSDOE site can be
matched to a row.

- #1 xiaofanhu **0.4544**; #2 cfld__ **0.3916**; #3 Batik Shirt Brothers **0.3911**.
- **#47 kpomazi 0.3195** (the page shows 0.3195 here).
- **0.4413 does not appear** in the top 50 rows shown. The page shows only 50 rows.

**Irregularity (corrected this session):** the previous executive-summary text said "0.3195 does not match
that page". That was wrong. It is at #47. The renderer is fixed in `scripts/render_site.py`.

## 5. Hypotheses (proposed, NOT validated, NOT submitted)

Each candidate was checked against the repo by keyword search (`grep -ril` over `src/`, `scripts/`, `docs/`, `knowledge/`).
Expected gain is not quantified because no holdout exists. Only two candidates survived the novelty check.

| Rank | Hypothesis | Layers | Physical signature | Why it could catch an off-catalogue fault | Overlap with repo | Cost / blocker |
|---|---|---|---|---|---|---|
| H1 | **Survey-resolution mask on magnetic lineaments.** Keep tilt-derivative / analytic-signal ridges only where the local flight-line spacing can resolve their wavelength. | Magnetic total field and its derivatives (GeoDAWN) | Magnetic lineament ridges, retained only where GeoDAWN coverage resolves them | GeoDAWN Area 1 is flown at 200 m line spacing and Area 2 at 400 m ([ScienceBase item](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7)). Ridges that the line spacing cannot resolve are less reliable, so the mask is expected to remove some false positives. Untested | `grep "Area 1"` returns **0** hits in the repo. The tilt derivative and analytic signal are already used, so only the survey-resolution mask is new | Needs the GeoDAWN flight-line shapefiles from ScienceBase, which the sandbox cannot reach |
| H2 | **Euler-deconvolution depth-clustered contacts.** Keep structural-index-1 contacts whose depths cluster at a reservoir-scale depth band. | Reduced-to-pole magnetics; top-of-crustal magnetic depth estimate | Depth-consistent source edges on the flanks of magnetic lows | Lithologic contacts are expected to be rejected only when their depths fall outside the reservoir-scale band. Untested | `grep -ril Euler src scripts` returns **0** hits. It appears only in notes (6 files) | Low cost. Needs the 19-band feature stack, which is blocked |

**Rejected or already covered:**
- **Metric-calibrated inclusion threshold.** Already implemented as `breakeven_kernel_credit` (`src/gemsk/metric.py`) and documented in `src/gemsk/emission.py`. Not new (§2).
- **Phase congruency edges.** Not in our code (`grep` returns 0 hits in `src/` and `scripts/`). Not pursued, because a sibling lane already tested it: GEMSDOE32 `ARENA49-H1-PCG` ([evidence/sources/GEMSDOE32.md](../evidence/sources/GEMSDOE32.md)). A third lane would be duplicating it.
- **Scarps, gravity, radon, and strain-rate ideas.** Already implemented or tested in the repo. Keyword counts in `src/` and `scripts/`: scarp 20 files, gravity/Bouguer/isostatic 19, radon 5. Strain-rate work is documented in `docs/research/hypotheses-preregistration-2026-10-27.md`.

**Non-fault mimics to test before any holdout.** For H1, flight-line striping and leveling residuals
along the E–W flight azimuth (GeoDAWN metadata gives a 90° azimuth), and the Area 1/Area 2 seam. For H2,
basalt flows and intrusive contacts.

**Recommended order:** H1 first, once the GeoDAWN flight lines are downloaded. Then H2. No candidate may spend a weekly slot until a holdout exists and a separate selector approves it.

## 6. Data and access (what is blocked, and what is needed)

| Need | Status | Source |
|---|---|---|
| `training_features.tif` (19 bands) and fault labels | **Blocked** (login) | [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) |
| Reference-solution code | Available. Its `data/` folder contains only `.gitkeep` | [github.com/drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) (codeload tarball fetched) |
| GeoDAWN magnetic/radiometric survey data | Public, but not reachable from the sandbox | DOI [10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ); [ScienceBase](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7) |
| USGS Quaternary fault database (KML and GIS) | Public. Listed on the USGS page, not downloaded | [USGS faults](https://www.usgs.gov/programs/earthquake-hazards/faults); [GIS zip](https://earthquake.usgs.gov/static/lfs/nshm/qfaults/Qfaults_GIS.zip) |
| Peer repo rasters | Not used as ground truth. Their hashes do not establish organizer authenticity | Registry files only |

**Limitation on this sandbox:** outbound access is limited to github.com, codeload.github.com,
api.github.com, registry.npmjs.org, pypi.org, and files.pythonhosted.org. The fetch tool can read
DrivenData, USGS, and ScienceBase pages as text, but it cannot download the binary rasters.

## 7. Irregularities flagged for review

1. **0.3195 mis-described** in the old renderer text (fixed; §4).
2. **Stale numbers elsewhere.** `evidence/sources/GEMSDOE32.md` and `knowledge/geothermal-fault-knowledge.md` still say #1 = 0.4437 (a 26 Oct snapshot). The 29 Oct page shows 0.4544. Not changed here.
3. **Test count mismatch.** README says 365 tests. Current run: **373 passed** (`pytest -q`, 29 Oct 2026).
4. **0.2778 has no receipt.** The GEMSDOE32 page marks it as "owner-report"; there is no DrivenData receipt.
5. **Literal lattice gate is unsatisfiable above 22,163 dots** against the recorded witness (§1). It is not in the official rules. Owner decision.
6. **Eligibility and disclosure.** The rules restrict eligibility (for example, individuals must be U.S. citizens or permanent residents, and private entities must be U.S.-incorporated) and require disclosure of generative-AI use in the narrative (NLR rules §1.3, §3.2). Both must be confirmed by the owner before any final submission.
7. **Caveat on my own analysis.** The inclusion-threshold check (§2) is a simulation on synthetic posteriors. It is not a result on competition data, and the rule itself was already in the repo.
8. **Earlier novelty claim corrected.** My first draft listed the α·DTI rule as a new hypothesis. A keyword check found it in `src/gemsk/metric.py`, so it was removed from the new candidates.

9. **Mirror provenance.** The restored `training_features` / `labels` come from third-party mirrors. The owner must confirm that using a copy of login-walled competition data complies with the DrivenData terms before any holdout uses it.
10. **Sample-submission irregularity (from `main`).** The mirrored `sample_submission.tif` has exactly the 60,988 label-fault pixels. The DrivenData page calls it "total fault absence". Do not submit it.
11. **`main` has 7 failing tests before and after this merge** (`tests/test_session_1668dda0_hardening.py::test_local_and_peer_evidence_verifies_all_9_local_tifs`, `tests/test_session_20261029.py::test_fleet_audit_covers_every_local_tif_and_blocks_all`, and 5 more). They enumerate local TIFs and do not expect the new halo file. This branch adds no new failures. Not fixed here, because the assertions belong to other sessions.
12. **Executive summary on `main` is hand-restored.** `scripts/build_site.py` regenerates `docs/executive-summary.html` with different content, so the CI check `git diff --exit-code -- docs` would fail. This branch keeps `main`'s version. The owner should decide which generator is the authority.

## 8. Next steps (owner or next session)

1. **Owner:** decide whether the internal 70% / 3-px gate binds. Without that, no dotted raster can clear.
2. **Owner:** provide `training_features.tif` and the labels, or confirm that a mirror is acceptable. The sandbox cannot fetch them. Confirm the eligibility items in §7.6.
3. Once data exists: run the existing breakeven emission on a spatially blocked hide-and-recover holdout (DTI, α=0.2, β=0.8, 300 m kernel, 95% CI, leakage canary). This is a baseline, not a new idea.
4. Download GeoDAWN flight lines from ScienceBase; test H1 with the survey-resolution mask.
5. Only then consider a weekly slot, through the separate selector step.

## Sources (all fetched 29 Oct 2026 unless noted)

- Problem page and metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Data tab (redirects to login): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- Official rules (NLR): https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution (codeload tarball, `data/` contains only `.gitkeep`): https://github.com/drivendataorg/gems-prize-reference-solution
- GeoDAWN DOI: https://doi.org/10.5066/P93LGLVQ · ScienceBase: https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7
- USGS Quaternary Fault and Fold Database: https://www.usgs.gov/programs/earthquake-hazards/faults
- Registry pair check (reproducible): `scripts/registry_pair_check.py` → `evidence/registry_pair_check_23ef16f9.json`
- Metric threshold check (synthetic): `scripts/metric_threshold_check.py` → `evidence/metric_threshold_check_23ef16f9.json`
