# GEMS / KARAGE 1 — evidence before submission

**Decision, 28 October 2026: NEGATIVE — DO NOT SUBMIT.** There is no newly cleared competition GeoTIFF or reliable leaderboard-score estimate. This review did not train a model, generate dots, submit to the portal, or select a weekly slot. The weekly allowance was not checked.

[Executive summary and submission guide](docs/executive-summary.html) · [Nine per-site reviews](docs/index.html) · [Research and official sources](docs/research.html) · [Current JSON run card](evidence/run_card.json) · [Saved-byte audit](evidence/prior_candidate_audit.json)

## Why the previous clearance was withdrawn

The inherited HMAS-SINTER and GPC-Z artifacts were compared **from their saved TIFF bytes** with a SHA-pinned registered lattice, using the literal closed Euclidean disk of radius three pixels. The protocol says stop when **more than 70%** of a candidate's dots are within three pixels of *any* registered raster. No exemption was supplied for a dense or calibration raster.

| Historical candidate | Lattice witness | Outcome |
|---|---:|---|
| HMAS-SINTER-ENV | 38,174 / 38,200 = **99.931937%** | Duplicate under the literal rule; stop |
| GPC-Z | 35,959 / 36,000 = **99.886111%** | Duplicate under the literal rule; stop |

The old 611-raster release claim excluded the lattice and other classes from its overlap gate; it is superseded. This is a **proximity failure**, not a claim that the files are exact pixel copies. Their TIFFs remain in Git history and the repository for audit/research, not as approved downloads. We did not adjust predictions to evade the witness. **No submission slot was selected or spent.**

The lattice's three-pixel neighborhood covers 5,160,724 of 5,167,373 cells in the peer-mirrored footprint, leaving 6,649. At GEMSDOE32's 37,654-dot count, at least 31,005 dots (82.3418%) necessarily overlap the lattice. That geometry makes the literal rule nonspecific for dense predictions; only an explicit protocol decision could change it, not a private exemption. The original pre-placement surfaces, an authoritative complete registry and the assigned method paragraph are not available. Do not re-run the inherited lane after this stop.

Both old TIFFs have one float32 band, finite in-footprint values in [0, 1], and the same shape, CRS and transform as the pinned **peer mirror**, which is not an authenticated organizer template. Both are all-finite and contain **no null/NaN cells outside** the mirror footprint. The [organizer's published format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) describes null/NaN outside the bounds, while our inherited strict validator rejects NaNs anywhere. This is an unresolved compatibility issue: neither encoding was portal-tested in this session. The original rejected file was not provided, so the cause of “Predicted values must be in range [0, 1]” is unknown.

The current card records the old HMAS detached **HOLDOUT-DTI** of 0.093547, evaluator `gems57-pooled-hide-v2`, 22,619 withheld positives, 95% CI [0.081837, 0.105279]. That is an **inherited report not rerun here**, not a leaderboard estimate; the old leakage-canary implementation also counted a constant footprint feature as a pass. The card's `verdict` is `negative` and `ok_to_submit` is `false`.

## Nine-site comparison

These are the highest historical numbers supplied for the nine focus sites, **USER-REPORTED / UNVERIFIED**, without file-bound organizer receipts. Each site link opens its executive review and pinned historical filename. All nine audited historical files fail the literal lattice rule and must not be resubmitted. Estimated scores for any new candidate are unavailable.

| Site review | Reported historical result | Unique under protocol? | Upload? |
|---|---:|---|---|
| [GEMSDOE24](docs/GEMSDOE24.html) | 0.2477 | No | No |
| [GEMSDOE25](docs/GEMSDOE25.html) | 0.2600 | No | No |
| [GEMSDOE27](docs/GEMSDOE27.html) | 0.2449 | No | No |
| [GEMSDOE28](docs/GEMSDOE28.html) | 0.2710 | No | No |
| [GEMSDOE30](docs/GEMSDOE30.html) | 0.2600 | No | No |
| [GEMSDOE31](docs/GEMSDOE31.html) | 0.2708 | No | No |
| [GEMSDOE32](docs/GEMSDOE32.html) | **0.2778** | No | No |
| [GEMSDOE33](docs/GEMSDOE33.html) | 0.2632 | No | No |
| [GEMSDOE36](docs/GEMSDOE36.html) | 0.2750 | No | No |

For H33-B2, the prior byte audit reports that its 37,654-dot support equals the 44,090-dot GEMSDOE25 d2.8 support after removing 6,436 points at most two pixels from the mirrored fault catalogue, with no additions. Thinning redundant predictions can improve the distance-weighted precision/coverage tradeoff, but can also lose true-positive coverage. Known fault pixels are excluded from scoring according to [DrivenData staff](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516); that statement does not justify a buffer. Hidden labels and a submission receipt are unavailable, so the reason for the reported 0.2778 is **plausible, not proven**. A higher score is possible in principle but has not been demonstrated here.

## Research record

The target is **unmapped fault traces**, not direct proof of a geothermal vent. The [current research review](knowledge/three-pass-review-2026-10-28.md) records four untested, qualitatively ranked ideas, the potential non-fault mimics, prior-work distinctions, and data availability. No score projection is assigned to them. The [prior preregistration](docs/research/hypotheses-preregistration-2026-10-27.md) and [historical review](docs/research.md) are retained with their original context; historical proposals and results are not current approval. The detailed superseded lane pages are preserved as [plain-text research archives](knowledge/archive/2026-10-27-superseded/README.md) and in Git history.

Sources reviewed include [DrivenData problem and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [organizer reference implementation](https://github.com/drivendataorg/gems-prize-reference-solution), [USGS GeoDAWN airborne data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [USGS 3DEP](https://www.usgs.gov/3d-elevation-program), [USGS magnetotelluric conductance release](https://www.usgs.gov/data/electrical-conductance-maps-great-basin-usa) and [GDR INGENIOUS](https://gdr.openei.org/submissions/1391). The USGS conductance product spans **2–200 km depth ranges**, not the 0.5–10 km mistakenly claimed in prior material. Official source pages do not authenticate an owner mirror. Competition data redirected to login; no official competition-data file was authenticated or fetched this session.

## Reproduce the audit and project checks

Python 3.11 is supported; restore only the selected pinned GitHub-mirror inputs rather than assuming the whole data cache is present. These commands do not generate a prediction or spend a submission slot:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/restore_karage1_data.py --id sample_submission --data-dir .cache/restore-test
.venv/bin/python scripts/audit_prior_candidates.py --fetch
.venv/bin/python scripts/reconcile_prior_decisions.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_site.py
```

The sample mirror was restored and hash-verified; the full feature cache and fault-segment data were **not** restored. `audit_prior_candidates.py` checks one pinned lattice witness, not the complete registry. The adapter fails closed for incomplete inventories, unreadable/nonfinite references, undefined correlations, a missing or mismatched pre-placement receipt, and changed saved bytes. The vendor shared comparator itself still sanitizes nonfinite reference values; report/fix that once in the actual shared template rather than maintaining a private fork. The old experiment and dashboard generators have been stopped to prevent stale approval.

The [source monitor](index.html#source-feed) checks pinned peer GitHub revisions. A changed revision requires another audit; it does not update a score or authorize a file. CI rebuilds the static pages and tests their stability.

## Standing project brief (normalized)

**Maximize P(Win). Own the Outcome.** Continue the DOE GEMS Prize project autonomously, with a clean, navigable GitHub Pages executive summary for GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36. Investigate previous high-performing work and the reported GEMSDOE32 H33-B2 result; use historical submissions for learning, never simply rename and resubmit them. Record the best known per-site historical file, reported/validated scores and uniqueness, the actual submit decision, artifact name, and a note of at most 140 characters. Link reliable official sources; preserve research and disclose uncertainties. No new leaderboard score may be invented from a holdout.

Before any future experiment, propose and rank 3–5 distinct geological hypotheses by expected benefit and cost; specify exact layers, fault mechanisms, departure from prior methods, non-fault mimics and verified availability of free official data. Remain within the **one assigned method lane**. A missing assigned paragraph is not permission to invent a lane. Reuse the shared cached feature stack, `evaluate_holdout.py`, and `submission_writer.py`; fix shared tooling in the canonical template rather than in private copies. Do not spend more than three experiments or two hours.

Use buffered whole-fault-segment hide-and-recover; derive all catalogue-dependent features from visible faults in each fold; mask visible fault pixels exactly. Use pooled distance-weighted Tversky, α=0.2, β=0.8 and a 300 m triangular kernel. Test each feature alone for leakage: AUC >0.90 is a stop pending an explanation; constant, nonfinite or otherwise untestable features fail closed. Report every valid performance measurement as `HOLDOUT-DTI` with evaluator version, withheld positives and 95% CI, or `ORGANIZER-CONFIRMED` only from a file-bound submission-page receipt. Unverified owner reports remain explicitly labeled.

Check the surface **before** placement and the final saved dots against a complete registry. Rank correlation >0.90 with any raster or >70% of dots within three pixels of any raster means duplicate and stop; do not exempt convenient references. Scientific promotion requires a same-evaluator improvement over the comparable best, a passing single-feature canary, uniqueness, provenance, and saved-byte TIFF validation. Scientific promotion is not weekly-slot selection. An independent selector may authorize a slot only after verifying the current allowance; this repository must not upload or claim a slot automatically.

Produce one current JSON run card with hypothesis, mechanism, named non-fault mimic, holdout and CI, registry correlation/overlap, TIFF SHA-256, footprint/range/grid validator, submission name, short note and `promote`/`negative` verdict. Carry out implementation/verification, adversarial review/fixes, and a full requirements recheck; document the three passes, run tests and static builds, create and merge a PR, and report remaining blockers honestly. User-provided Dropbox links and official sources should be accessed where permitted; do not treat a GitHub mirror as organizer-authenticated.
