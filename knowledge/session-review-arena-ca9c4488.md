# Session review — `arena/ca9c4488` (2026-10-29)

**Verdict: NEGATIVE / DO NOT SUBMIT.** No new GeoTIFF was generated. No file in this repository is cleared for upload. No slot was selected or spent.

Run card: [`evidence/session_ca9c4488_run_card.json`](../evidence/session_ca9c4488_run_card.json) · Audit: [`evidence/focus_sites_audit_20261029.json`](../evidence/focus_sites_audit_20261029.json) · Script: [`scripts/audit_focus_sites.py`](../scripts/audit_focus_sites.py) · Tests: [`tests/test_focus_sites_audit.py`](../tests/test_focus_sites_audit.py)

---

## 1. Answer first: can I download and submit a file from this session?

**No.** Two independent reasons, both measured:

1. **Every focus-site file fails the literal duplicate rule, against the lattice and against the other focus sites.** Forward 3-px overlap with the 13GEMSDOE lattice is 0.9991–0.9992 for all nine. Each file also has ≥0.976 overlap with at least one other focus file (table, §2).
2. **The duplicate gate cannot be passed by a dotted file of useful size.** The lattice covers 99.87 % of the footprint within 3 px. Only 6,649 footprint cells are uncovered. A file passes the 70 % rule only if it has ≤ 22,163 dots and ≥ 30 % of them sit in those 6,649 cells (§4). That is a placement game, not a geological result, and the protocol says not to jitter dots to evade the rule. I did not do it.

A third blocker: the shared gate also needs a **complete** registry inventory, and none exists in `registry/`. The gate therefore fails closed on its own terms.

---

## 2. Executive summary table — nine focus sites

Every number below is measured on pinned mirror bytes (SHA-256 verified) unless marked. The score column is the **only** place a score appears, and it is **USER-REPORTED / UNVERIFIED**. No estimate is written as a score.

| Site | File to download | Dots | Reported score (USER-REPORTED) | New estimate | Unique vs the other 8 focus files? | Unique vs lattice (literal 70 % rule)? | OK to download & submit? |
|---|---|---:|---:|---|---|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-…-nan.tif` | 60,069 | 0.2477 | Not estimable (no holdout run) | **No** (1.000 vs GEMSDOE25) | **No** (0.9992) | **NO** |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-…-nan.tif` | 44,090 | 0.2600 | Not estimable | **No** (1.000 vs GEMSDOE24) | **No** (0.9992) | **NO** |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-…-nan.tif` | 61,328 | 0.2449 | Not estimable | **No** (0.980 vs GEMSDOE24) | **No** (0.9992) | **NO** |
| GEMSDOE28 | `gems28-h27-4-r1-solo-d2-8-…-allfinite.tif` | 40,199 | 0.2708 | Not estimable | **No** (1.000 vs GEMSDOE24; identical mask to GEMSDOE31) | **No** (0.9992) | **NO** |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-…tif` | 44,090 | 0.2600 | Not estimable | **No** (identical mask to GEMSDOE25) | **No** (0.9992) | **NO** |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-…-nan.tif` | 40,199 | 0.2708 | Not estimable | **No** (identical mask to GEMSDOE28) | **No** (0.9992) | **NO** |
| **GEMSDOE32 (B2)** | `gemsdoe32-h33-h33-2-b2-…-zeros.tif` | 37,654 | **0.2778** (highest of the nine) | Not estimable | **No** (1.000 vs GEMSDOE24/25/27/28) | **No** (0.9992) | **NO** |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-…tif` | 41,865 | 0.2632 | Not estimable | **No** (0.997 vs GEMSDOE27) | **No** (0.9991) | **NO** |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-…-zeros.tif` | 38,854 | 0.2750 | Not estimable | **No** (0.976 vs GEMSDOE27; strict superset of B2 by 1,200 dots) | **No** (0.9992) | **NO** |

**Count of files that are unique under the literal rule: 0 of 9.** The table is what the protocol says; it is not a judgement of the sites' quality.

**Where the estimate column comes from.** A new estimate needs a HOLDOUT-DTI run (evaluator version, withheld-positive count, 95 % CI) on the same folds as the incumbent. No such run was done in this session. Writing a number there would be a projection. The fitted trend in §3 is descriptive and is not an estimate for any file.

---

## 3. Why did GEMSDOE32 B2 score highest? (measured structure, causation not proven)

Verified line by line on the pinned bytes (`scripts/audit_focus_sites.py`, plus a one-off check of the subset claims):

- **B2 is an exact subset of GEMSDOE25.** 6,436 dots of GEMSDOE25 are removed; none are added (`B2 ⊂ 25`, `25 − B2 = 6,436`).
- **Every removed dot lies within 2 px of a catalogue label pixel.** 3,891 are within 1 px. 6,436 are within 2 px. **No kept B2 dot is within 2 px of a label.** Label pixels total 60,988, all inside the footprint.
- **GEMSDOE28/31 are the 1-px rung of the same ladder.** They are a subset of GEMSDOE25 with 3,891 near-catalogue dots removed. GEMSDOE28 and GEMSDOE31 have identical masks.
- **GEMSDOE36 is a superset of B2** with 1,200 extra dots, none within 2 px of a label.
- **Ladder of user-reported scores:** 44,090 dots → 0.2600; 40,199 → 0.2708; 37,654 → 0.2778. Across all seven distinct focus masks, Spearman ρ between dot count and reported score is **−1.0** (n = 7; Pearson r = −0.955, p ≈ 0.0008). This is descriptive and rests on unverified numbers.

**Mechanism (hypothesis, not demonstrated).** Under the official metric, a dot's cost depends on whether a *hidden* label lies within the 300 m kernel. Dots 1–2 px (100–200 m) from a catalogue trace are the catalogue's own edge response. They may be false positives for hidden new faults. If so, deleting them lowers α·FP more than it lowers β·FN. The official rules say the Initial round scores against new faults labelled before the competition, and the Final round rescoring then adds expert-verified faults ([problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)).

**What would falsify it.** If the halo dots are real hidden-fault hits, removing them should lower the score on a holdout with the same folds. This has not been tested.

**Can a higher score be reached?** Possibly, by further thinning, but:
- A further-thinned file is a derivative of the same B2 mask. It is not a unique submission in the sense the protocol requires.
- Any such file still fails the lattice rule (§4).
- I cannot estimate its score. A linear trend would predict a higher number for fewer dots, but that extrapolation over n = 7 is a projection, not a score, and the protocol bars writing it as one.

**The contrarian point to test.** The two rounds reward different things. The Initial round rewards predictions that avoid the catalogue neighbourhood. The Final round rewards predictions that experts later confirm as new faults. A halo-removal strategy optimises the first and may cost the second. This is a hypothesis for a future, separately preregistered experiment, not a finding.

---

## 4. The duplicate gate, in numbers

| Quantity | Value | Source |
|---|---:|---|
| Footprint cells | 5,167,373 | `data/sample_submission.tif` finite cells |
| Lattice dots (13GEMSDOE) | 206,895 | `evidence/focus_sites_audit_20261029.json` |
| Footprint cells > 3 px from any lattice dot | 6,649 (0.129 %) | same |
| Max dots that can pass the 70 % rule | **22,163** = ⌊6,649 / 0.30⌋ | same; test `test_lattice_bound_arithmetic` |
| Focus files above 22,163 dots | **9 of 9** (37,654 – 61,328) | same |

A dot inside a covered cell always overlaps. A file therefore passes only if ≥ 30 % of its dots lie in the 6,649 uncovered cells. The nine focus files have 32–47 dots there each.

**Protocol observation.** The repository's own `registry/registry_roles.json` already calls the lattice a *calibration probe* that is "never sufficient alone to declare lane drift", and says the literal rule is "mathematically unsatisfiable" for covering blankets. `registry/reference_assets.json` nevertheless lists the lattice as a registry witness. The two documents disagree. That is a protocol decision for the owner.

---

## 5. The "Predicted values must be in range [0, 1]" error

Measured facts:
- `sample_submission.tif` (the official grid) is float32, EPSG:32611, 3730 × 3292, 100 m, with **NaN outside the footprint** and 0/1 inside.
- The existing "-nan" files carry NaN outside. The "-zeros" files carry 0 outside. Our own range checks (`scripts/validate_geotiff.py`, `audit_focus_sites.py`) evaluate finite cells only, so they pass both encodings.
- Official wording: "data outside the bounds is null or nan" ([problem description, submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)).

**Hypothesis (unverified).** A portal check written as `all(0 ≤ x ≤ 1)` returns False when NaN is present. That would explain the message for a NaN-outside file. Under this hypothesis, a zeros-outside file passes. The portal's real check is not public and the rejected upload was not supplied, so this is a hypothesis to test with one receipt. It is not a fact. No slot was spent to test it.

---

## 6. Official facts checked this session (with links for manual review)

| # | Fact | Source | Status |
|---|---|---|---|
| F1 | Expert panel updates labels after the Initial round. Final round rescoring uses the expanded set. | [Problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | VERIFIED today |
| F2 | Metric: distance-weighted Tversky, α = 0.2, β = 0.8, R = 300 m | same | VERIFIED (prior register) |
| F3 | Leaderboard #1 is **0.4544** (xiaofanhu) | [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | VERIFIED today |
| F4 | 0.3195 is rank #47 | prior register `knowledge/official-sources-verified-2026-10-29.md` §C | VERIFIED in prior session; not re-fetched today |
| F5 | Rules: up to 3 submissions per week; one final submission; AI-use disclosure | [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | VERIFIED (prior register) |
| F6 | Masking of known USGS/INGENIOUS faults is pixel-exact | [Staff post, 2026-09-16](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2) | VERIFIED (prior register) |
| F7 | The 70 %/3-px duplicate rule is **not** in the official rules | prior register B1 | VERIFIED (absence, prior session) |

**Human inspection (the prompt's concern).** The only expert review named on the official problem page is the organizer's expert panel. It happens after the Initial round and updates the labels. The project cannot run that review. What the project *can* do without human intervention is format validation and the duplicate and holdout gates. Those are automated here. The expert step stays on the organizer side.

**Irregularities for review**
1. The prompt's "0.4413" and "0.3195 is the highest score" do not match the live board. The top is 0.4544.
2. No GEMSDOE score appears in the visible top 50 (cut-off 0.3167). Every GEMSDOE number is user-reported.
3. A third-party repo's summary claims DrivenData terms restrict automated monitoring. I did not verify that against DrivenData's Terms of Use. Treat it as unverified.
4. Four focus rasters (30, 31, 33, 36) were not in the restore manifest. They were fetched from pinned commits through the repo's `gh api` path, and each SHA-256 matched `registry/reference_assets.json`.
5. `raw.githubusercontent.com` is not on the sandbox allowlist. That is why the `gh api` path was used.

---

## 7. What changed on the branch

- `scripts/audit_focus_sites.py` (new): reproducible pairwise audit, lattice bound, identical-mask groups, user-reported trend. Fetches the four unmanifested pins through the repo's own fetcher and checks SHA-256.
- `evidence/focus_sites_audit_20261029.json` (new): measured output.
- `tests/test_focus_sites_audit.py` (new): six invariant tests that need no raster data.
- `evidence/session_ca9c4488_run_card.json` (new): run card, verdict negative.
- `knowledge/session-review-arena-ca9c4488.md` (this file).
- `README.md`: top banner now points here, with the one-line verdict.
- `AGENTS.md`: reading list updated.

No raster was added to Git. `data/` is gitignored and holds the restored mirror bytes.

---

## 8. Decision needed from the owner (this blocks every future file)

The duplicate rule as written makes every useful dotted file inadmissible. Three options:

- **A. Keep the literal rule.** Then no dotted file above 22,163 dots can ever be submitted. The competition would effectively be closed to the dotted approach. The fix would be to drop the dotted format or the rule.
- **B. Exclude the 13GEMSDOE lattice from the duplicate witness set.** `registry/registry_roles.json` already calls it a calibration probe. Under B, the focus-site mutual overlaps (0.976–1.0) still need a ruling, because they are not calibration probes.
- **C. Accept a documented exception** for a named file, with the overlap disclosed in the submission note. This is a risk decision for the owner.

I have not chosen. The protocol reserves that choice for its owner. Until it is made, **no file in this repository is cleared for upload.**

---

## 9. Next steps (ordered)

1. **Owner decides the duplicate gate** (§8). Nothing else can clear a file.
2. **Assign the method lane.** The protocol's "method paragraph" is still missing (`method_lane: null`).
3. **Complete the registry inventory.** A `complete_accessible_scan: true` inventory with the lattice included is required by the shared gate, and none exists.
4. **Authenticated organizer data.** The DrivenData data tab is login-walled. The restored mirrors establish byte identity only.
5. **One receipt test** of the NaN-outside versus zeros-outside encoding, using a slot the owner selects. That would turn §5 from a hypothesis into a fact.
6. **Only then:** a preregistered holdout experiment (≤ 3 experiments / 2 h), an evaluator run with a 95 % CI, and a separate selector step.

## Reproduce

```sh
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python scripts/restore_karage1_data.py --group core
python scripts/restore_karage1_data.py --group scored
python scripts/audit_focus_sites.py                 # ~80 s; writes evidence/focus_sites_audit_20261029.json
python -m pytest -q tests/test_focus_sites_audit.py # 6 passed
```
