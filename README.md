# GEMSDOEkarage1 — DOE GEMS Prize, lane "GPC-Z"

**Site (executive summary, download, OK-to-submit status): https://karagemop466-tech.github.io/GEMSDOEkarage1/** (source in `docs/`; enable GitHub Pages → branch `main`, folder `/docs` once, if not already on).

**Standing brief — read first, every session:** [`docs/standing-prompt.md`](docs/standing-prompt.md). Core Values: *Maximize P(Win)* and *Own the Outcome*.

## Current state (2026-10-27)

| Item | Value |
|---|---|
| Submit-ready file | `docs/downloads/gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-zeros.tif` (sha256 `75ac577a…6dbd`, 36,000 dots, float32, EPSG:32611, no NaN anywhere) |
| Status | **OK TO SUBMIT** — validator passed (all 11 checks); unique vs the 15 registry rasters (max 31.7% of dots within 3 px, rank-corr ≤ 0.017); leakage canary clear (max single-feature AUC 0.78 < 0.90) |
| HOLDOUT-DTI | 0.1273 [0.1169, 0.1374] — evaluator `gemsk-hide-recover-v1` (8464ac87ec5ea4c3), 4 interleaved folds, 60,988 withheld positives total; **not a live estimate** |
| ORGANIZER-CONFIRMED | none yet for this file |
| Verdict | `promote-to-selector` (run card `evidence/run_card_gpcz.json`) |
| Experiments used | 3 of 3 (budget exhausted; next session starts a new budget) |

Hypothesis in one sentence: unmapped faults are low scarps in the damage zone of mapped ones, facing the basin like their parents; so emit label-free topographic *step edges*, gated by concordance between the scarp's downhill direction and the gravity/basement deepening direction, weighted by a near-catalogue prior g(d) measured by hide-and-recover, pruned to ≥3 px from the catalogue, 36,000 binary dots at 2.8 px spacing.

## Layout

```
docs/                 GitHub Pages site (index, how-to-submit, nine-sites, research, knowledge, sources, standing-prompt)
docs/downloads/       the shipped GeoTIFF(s), zip, receipt
docs/data/            latest-run-card.json, restore_receipt_summary.json
evidence/             every experiment's JSON (exp1 screen, exp1b prior tables, exp2 holdout, exp3 sweep, canary, run card, rejected hedge)
knowledge/            geothermal-fault knowledge base with provenance tags
registry/             data_manifest.json — SHA-256 pins for all restored rasters (competition files + 15 registry submissions)
scripts/              restore_data.py, run_experiment{1,2,3}_*.py, build_site.py
src/gemsk/            grid, metric, holdout, features, emission, prior, submission (writer+validator), uniqueness, pipeline
tests/                13 tests (metric vs brute force, emission/NMS, holdout folds & prior, submission validator)
```

## Reproduce (no manual steps)

```bash
pip install -r requirements.txt
python3 scripts/restore_data.py --group all          # from github.com mirrors, SHA-256 verified → .cache/gems_data/
PYTHONPATH=src python3 -c "from gemsk import grid; grid.prepare_bands()"
PYTHONPATH=src python3 scripts/run_experiment1_screen.py 37654
PYTHONPATH=src python3 scripts/run_experiment2_gpcz.py
PYTHONPATH=src python3 scripts/run_experiment3_build.py   # builds docs/downloads/*.tif, uniqueness audit, run card
PYTHONPATH=src python3 -m pytest -q tests
python3 scripts/build_site.py
```

## Protocol notes and irregularities

- **Template tools did not exist.** The brief says to reuse `evaluate_holdout.py` / `submission_writer.py` from the template and never fork them. This repository was empty; the shared tools were therefore ported here as `src/gemsk/holdout.py` + `src/gemsk/metric.py` (evaluator) and `src/gemsk/submission.py` (writer + validator). If a template repository appears, these modules should be upstreamed there and imported, not kept as a private fork.
- **Data access.** The sandbox can reach only github.com / pypi.org. Competition rasters were restored from the owner's github mirrors and SHA-256-pinned (`registry/data_manifest.json`). Pins prove consistency with the mirror, not organizer authentication (IR-K1-DATA-01). DrivenData, Dropbox, gdr.openei.org, USGS and nlr.gov could not be fetched; links are listed in `docs/sources.md` for manual verification.
- **Lattice impasse.** The calibration probe `r13-lattice-s5` makes the literal 70%-within-3-px rule impassable; it is exempted and reported (99.9%).
- **Holdout limits.** Files already pruned ≤2 px from the catalogue score ≈0 on catalogue holdouts by construction; the H19-5 "control" is catalogue-trained upstream and therefore leak-inflated. Both are reported as controls only.

## Remaining work / next session

1. **Selector step (human, weekly cap):** submit the file above if a slot is free; record the organizer score in `registry/score_ledger.csv` as ORGANIZER-CONFIRMED and update `docs/index.html` via `build_site.py`.
2. Obtain the owner's verbatim prompt and paste it into `docs/standing-prompt.md` (the current text is a clause-by-clause reconstruction).
3. New budget: H3 radiometric across-edge juxtaposition (data on hand); H4/H5 need egress to earthquake.usgs.gov (ComCat, Monte Cristo rupture) — ask for the data to be mirrored to github if wanted.
4. A hedge that is genuinely different from the primary (the sqrt-prior variant was 89% identical and was dropped): e.g. a 44,090-dot emission of the same field, or a polarity-gate-off variant, both already scorable with `gemsk.pipeline.build`.
5. Mitigate the shoreline mimic (IR-K1-OBLIQ-01): obtain Reheis (1999) pluvial-lake shoreline polygons (USGS MF-2323, free) and down-weight contour-parallel steps at the Lahontan highstand elevations.

## Limitations (plain language)

No number in this repository is a leaderboard estimate. The holdout measures recovery of withheld *catalogue* strands; the live hidden set is expert-mapped strands whose spatial statistics are inferred, not observed. The one structural bet — that hidden faults sit within 1.5 km of mapped ones — is measured on the catalogue (67%) and consistent with every sibling live result (far-field designs ≈0), but it is still a bet.
