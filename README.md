# GEMSDOEkarage1 — evidence before submission

**Current decision: DO NOT SUBMIT. No new competition TIFF has been generated.**

Start every session with the [owner requirements](knowledge/OWNER_BRIEF.md), [scientific review and next steps](knowledge/REVIEW.md), and [run card](docs/data/run_card.json). Maximize P(Win) by testing claims; own the outcome by preserving negative findings rather than inventing success.

- [Executive dashboard](https://karagemop466-tech.github.io/GEMSDOEkarage1/)
- [Submission instructions](https://karagemop466-tech.github.io/GEMSDOEkarage1/executive-summary.html)
- [Nine-site source pins](docs/data/sources.json) • [independent historical-mask audit](docs/data/raster_audit.json)

The initial repository contained no pipeline. The assigned method paragraph is missing from the supplied request. No experiment or competition slot has been used. All nine audited historical files fail the requested overlap rule against at least one peer. Different filenames do not establish unique predictions. Performance estimates remain unavailable; owner reports are not organizer receipts.

## Reproduce (Python 3.11)
```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/collect_sources.py  # gh public API access; pinned snapshots
.venv/bin/python scripts/audit_rasters.py   # historical audit, not holdout scoring
.venv/bin/python scripts/build_site.py
.venv/bin/python -m pytest -q
```
The source collector downloads only historical artifacts for comparison into ignored `.research/`. Never submit these as new work. Audit files are small; raster datasets stay out of Git.

For future generated artifacts, run:
```sh
.venv/bin/python scripts/validate_artifact.py candidate.tif official_template.tif binary_footprint.tif
```
This strict read-only check rejects NaN, infinity, out-of-range values, mismatched grids and invalid footprints. It does **not** generate predictions or authorize submission. Reuse the designated template's evaluator and writer; do not substitute this format check for holdout, leakage or full-registry evidence.

GitHub Pages publishes the root site; CI tests it. The scheduled workflow refreshes public evidence into a downloadable Actions artifact without auto-promoting or submitting anything. The live site remains the last merged snapshot; changing Pages settings was denied by the GitHub integration (403), so automatic refreshed-site deployment is not claimed. Source snapshots contain unverified historical assertions and are clearly separate from our independent measurements.

## Concurrent integration
While this audit ran, another session merged a synthetic prototype onto main. It is preserved in [archive/prototype](archive/prototype/README.md), explicitly **DO NOT SUBMIT**. Those placeholder-data TIFFs are not this audit’s deliverable; regridding them does not provide real geological evidence. Their local evaluator is not the designated shared template. The active site remains this audit dashboard.

A second concurrent review (PR #3) is retained: [detailed site summaries](docs/index.html), its independent lattice audit, `registry/template.json`, shared-tool restoration helpers and release-gate tests. Root dashboard uses the pairwise nine-mask audit; the detailed dashboard additionally reports its lattice comparison. These are distinct registry scopes, not contradictory measurements. The method lane is still missing.
