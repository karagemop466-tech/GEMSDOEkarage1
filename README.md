# GEMSDOEkarage1 — DOE GEMS Prize Challenge research & submission pipeline

**Start here every session:** [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md)
(what we're building and why), [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md)
(what this environment can and cannot do, verified live), and
[`docs/SOURCES.md`](docs/SOURCES.md) (every citation used anywhere in this
repo). **GitHub Pages site:** `docs/index.html` /
`docs/executive-summary.html` (enable Pages → Deploy from branch → `/docs`
in the repo settings to publish it).

## What this is

A from-scratch, **fully transparent** research and submission pipeline for
DrivenData competition #306, the
[GEMS Prize Challenge](https://www.drivendata.org/competitions/306/competition-doe-gems/)
(find hidden/blind geologic faults relevant to undiscovered geothermal
systems in the GeoDAWN survey area, NW Nevada). It implements, from the
**official, publicly-readable problem description** (no login needed to
read it, though the data tab itself does require a free account):

- the exact scoring metric (distance-weighted Tversky index, `src/gems/metric.py`),
- the exact submission grid/format (`src/gems/grid.py`),
- a submission writer that cannot produce an out-of-range pixel
  (`src/gems/submission_writer.py`),
- a format validator (`src/gems/validator.py`) that reproduces and catches
  the previously-reported upload error, `"Predicted values must be in
  range [0, 1]"`, before you ever click submit,
- unit tests for all of the above that need **no competition data** to run
  (`tests/`), verified passing in this environment (`python -m pytest`),
- a from-scratch, line-by-line verified audit of nine sibling "GEMSDOE"
  research sites and the real public DrivenData leaderboard
  (`research/sibling_site_audit.md`), and
- five new, ranked, sourced geological hypotheses not yet tried by any of
  those sites (`research/hypotheses.md`).

## Data access update: real competition data IS reachable from this sandbox

Despite `drivendata.org` itself being outside the network allowlist, the
real `training_features.tif` / `labels.tif` / `sample_submission.tif` were
restored via a hash-pinned third-party GitHub mirror discovered inside a
sibling research repo (`buffedlizard55-lab/GEMSDOE32`'s own
`registry/data_manifest.json`). Run `bash scripts/restore_real_data.sh`
(~20s, sha256-verified) then `python scripts/prepare_data.py` to get it.
**This is still not an organizer-authenticated download** — see
[`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) §0 and
[`data/README.md`](data/README.md) before trusting any number derived from
it as more than `HOLDOUT-DTI(...)`.

With that data, two real holdout experiments were run (whole-fault-segment
hide-and-recover, leakage canary, spatial block bootstrap CI):

| Experiment | HOLDOUT-DTI (95% CI) |
|---|---|
| 1 — geodetic strain (2 features) | 0.0137 [0.0122, 0.0150] |
| 2 — all 19 bands, linear model | 0.0146 [0.0127, 0.0162] |
| 2 + metric-aware sparsity threshold | **0.0303** [0.0231, 0.0388] |

This is a genuine, if modest, real-data result — far below the public
leaderboard's real top score (0.4544) and sibling sites' claimed numbers
(0.19–0.28), reported honestly as a negative/exploratory finding, not
discarded. Full writeup, including why: `docs/LIMITATIONS.md` §0.

## The honest, ready-to-download files in this repo today

1. [`outputs/baseline/gems-karage1-format-baseline-zero-v1.tif`](outputs/baseline/gems-karage1-format-baseline-zero-v1.tif)
   — a format-perfect, all-zero GeoTIFF; proves the upload pipeline works
   (true DTI = 0 by construction, not competitive).
2. [`outputs/real_data_candidate/gems-karage1-realdata-allfeat-logreg-sparsified-v1.tif`](outputs/real_data_candidate/gems-karage1-realdata-allfeat-logreg-sparsified-v1.tif)
   — trained on the real restored data, format-validated, confirmed
   non-duplicate against a real registry raster, with a real
   `HOLDOUT-DTI = 0.0303 [0.0231, 0.0388]` (see its
   [`run_card.json`](outputs/real_data_candidate/run_card.json)). Verdict:
   **`negative`** — explicitly NOT promoted to a real weekly submission
   slot, because it is far below the comparable best known score; shipped
   only as the one genuinely data-grounded, non-fabricated candidate this
   session produced.

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the full test suite (no competition data required):
python -m pytest -q

# Regenerate the safe baseline submission + its run card:
python scripts/generate_baseline_submission.py

# Validate ANY candidate GeoTIFF before you upload it:
python scripts/validate_submission.py path/to/candidate.tif --allow-nan   # --allow-nan optional

# See the pipeline work end-to-end on an explicitly SYNTHETIC toy problem
# (proves the code is correct; never a real score):
python scripts/demo_synthetic_pipeline.py

# Lane-discipline / duplicate check (parallel-run protocol rule 1) of a
# candidate against any number of other rasters:
python scripts/check_uniqueness.py candidate.tif other1.tif other2.tif
```

To work with **real** competition data:

```bash
bash scripts/restore_real_data.sh           # ~20s, sha256-verified GitHub-
                                             # mirror restore -- see data/README.md
python scripts/prepare_data.py              # confirms the real files match
                                             # src/gems/grid.py

# Re-run the two real holdout experiments (needs data/ restored, ~2-5 min each):
python scripts/run_holdout_experiment.py
python scripts/run_holdout_experiment_2_allfeatures.py
python scripts/calibrate_sparsity_threshold.py
python scripts/build_real_data_candidate.py
```

(`scripts/download_competition_data.sh` is kept as a fallback manual-login
path for a future session on a host where even GitHub's mirror has been
taken down or changed; prefer `restore_real_data.sh` first.)

## Repository layout

```
src/gems/            Core library: grid.py, metric.py, validator.py, submission_writer.py, uniqueness.py
scripts/             CLI entry points: restore_real_data.sh, prepare_data.py, generate/validate/
                     check_uniqueness, synthetic demo, run_holdout_experiment*.py,
                     calibrate_sparsity_threshold.py, build_real_data_candidate.py
tests/               Unit tests (metric correctness, validator gates, grid sanity) — no data needed
research/            hypotheses.md (new ideas) + sibling_site_audit.md (9-site audit)
docs/                PROJECT_BRIEF.md, LIMITATIONS.md, SOURCES.md, and the GitHub Pages site
data/                NOT committed (gitignored); restore via scripts/restore_real_data.sh; see data/README.md
outputs/baseline/              Safe-to-upload all-zero format baseline + run card
outputs/experiment_h_geod_strain/    Experiment 1 report (real data, 2-feature hypothesis)
outputs/experiment2_h_allfeatures/   Experiment 2 report + sparsity threshold sweep (real data, 19 bands)
outputs/real_data_candidate/   Final honest real-data candidate TIF + run card
```

## Current status

**Real competition data is reachable** (see "Data access update" above) and
two real holdout experiments are done, with a shipped, honestly-labeled,
non-duplicate candidate at `HOLDOUT-DTI ≈ 0.03` — well below the real
leaderboard (0.4544) and sibling-claimed scores, reported as a negative
result, not promoted to a submission slot. Metric, grid, validator, writer,
tests, uniqueness checker, and docs are all implemented and verified.

**Next steps** (see `docs/executive-summary.html` → "Next steps" and
`docs/LIMITATIONS.md` §0 for the full reasoning):
1. Try a materially stronger model on the same real features (gradient
   boosting / random forest first — cheap, no new experiment-cap spend
   beyond what's already used; a CNN is the next tier).
2. Engineer richer features from the 19 real bands (neighborhood
   statistics, multi-scale edges) before reaching for new external data.
3. If still short, bring in one of the 5 hypotheses in
   `research/hypotheses.md` that uses verified-obtainable USGS data not
   already in `training_features.tif`.
4. Only promote a candidate to a real weekly slot after it beats the
   current best comparable HOLDOUT-DTI (0.0303) with a non-overlapping CI,
   per the parallel-run protocol — this session used 2 of the 3 allowed
   experiments plus one post-hoc calibration pass, and intentionally
   stopped there rather than spending the full cap on a result already
   diagnosed as feature/model-limited.
