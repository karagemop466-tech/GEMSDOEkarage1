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

## The one honest, ready-to-download file in this repo today

[`outputs/baseline/gems-karage1-format-baseline-zero-v1.tif`](outputs/baseline/gems-karage1-format-baseline-zero-v1.tif)
— a format-perfect, all-zero ("predicts no fault anywhere") GeoTIFF on the
cross-replicated competition grid. It exists to prove the upload pipeline
works and to give you a known-good template; **it is not a competitive
entry** (true DTI = 0 by construction). See
[`docs/executive-summary.html`](docs/executive-summary.html) or
[`research/sibling_site_audit.md`](research/sibling_site_audit.md) for the
full explanation of why no *competitive* candidate can be honestly generated
in this environment yet, and exactly what is needed to produce one (one
manual, credential-only step: download the real competition data).

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

To work with **real** competition data (required for any genuinely
competitive candidate):

```bash
bash scripts/download_competition_data.sh   # prints the manual steps; a
                                             # DrivenData login cannot be
                                             # automated or is not configured here
python scripts/prepare_data.py              # asserts the real files match
                                             # src/gems/grid.py, or tells you
                                             # exactly how to fix the constant
```

## Repository layout

```
src/gems/            Core library: grid.py, metric.py, validator.py, submission_writer.py, uniqueness.py
scripts/             CLI entry points (download, prepare, generate, validate, uniqueness check, synthetic demo)
tests/               Unit tests (metric correctness, validator gates, grid sanity) — no data needed
research/            hypotheses.md (new ideas) + sibling_site_audit.md (9-site audit)
docs/                PROJECT_BRIEF.md, LIMITATIONS.md, SOURCES.md, and the GitHub Pages site
outputs/baseline/    The generated, validated, safe-to-upload format baseline + its run card
```

## Current status and what's blocking a competitive submission

**Blocked on one thing:** this sandbox has no DrivenData account configured
and cannot reach `drivendata.org`'s authenticated data tab, `dropbox.com`,
or `sciencebase.gov`/`gdr.openei.org`'s binary file downloads (verified
live, see `docs/LIMITATIONS.md`). Everything *except* touching real pixel
data is done: metric, grid, validator, writer, tests, research plan, and
docs are all implemented and verified. The moment `data/training_features.tif`,
`data/labels.tif`, and `data/sample_submission.tif` exist (one person,
one login, one download), `scripts/prepare_data.py` closes the loop and the
five hypotheses in `research/hypotheses.md` are ready to implement and
holdout-test in priority order.

See `docs/executive-summary.html` → "Next steps" for the full, prioritized
list.
