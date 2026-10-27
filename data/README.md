# `data/` -- real competition files (NOT committed to git)

This directory is gitignored (see `.gitignore`) except for this file and
`.gitkeep`. The real competition rasters are large (~450 MB total) and must
never be committed to the repo or left sitting in a workspace snapshot --
run the restore script fresh each session:

```sh
bash scripts/restore_real_data.sh   # ~20s, hash-verified, see its header
python scripts/prepare_data.py      # confirms grid match
```

## What this restores, and why it works

The real `training_features.tif`, `labels.tif`, `existing_faults.tif`, and
`sample_submission.tif` are **not** downloadable directly from
`drivendata.org` in this sandbox (that host, and dropbox.com/gdr.openei.org/
usgs.gov, are outside the network allowlist -- see `docs/LIMITATIONS.md`).

However, a sibling project in this same GitHub organization,
`buffedlizard55-lab/GEMSDOE32`, documents in its own
`registry/data_manifest.json` and `scripts/fetch_data.py` that it restored
these exact bytes from a hash-pinned mirror on two OTHER sibling repos:
`buffedlizard55-lab/GEMSDOE` (the large `training_features.tif`, split into
5 git-sized parts) and `buffedlizard55-lab/GEMSDOE24` (`labels.tif`,
`sample_submission.tif`, and several external layers). `github.com`,
`api.github.com`, and `codeload.github.com` **are** inside this sandbox's
network allowlist, so the same mirror is reachable here. `scripts/
restore_real_data.sh` re-implements that fetch and independently
re-verifies every file's sha256 against GEMSDOE32's own pinned manifest
before use (all matched exactly on 2026-10-27 -- see
`docs/SOURCES.md`).

**This is an integrity-pinned, third-party mirror, not an
organizer-authenticated download.** Nobody in this chain (including this
session) has confirmed these bytes against a DrivenData login. Treat every
number computed from this data as `HOLDOUT-DTI(...)`, never as
`ORGANIZER-CONFIRMED`, per the project's own labeling rule in
`docs/PROJECT_BRIEF.md`.

## Files after restore

| file | bytes | sha256 |
|---|---|---|
| `training_features.tif` | 418,912,844 | `4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5` |
| `labels.tif` | 425,830 | `7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093` |
| `existing_faults.tif` | 425,830 | (byte-identical to `labels.tif`) |
| `sample_submission.tif` | 1,599,597 | `2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc` |
| `registry/scored_h19_5.tif` | 1,712,322 | `ec1f9b56b83ce33cad781ceb9f104b18fb4f2ff785263a4e89616af4aabdee8d` |

Grid (confirmed against `src/gems/grid.py::GEMS_GRID`): EPSG:32611,
3730 x 3292, transform `(100, 0, 243350, 0, -100, 4508550)`.

`training_features.tif` has 19 float32 bands, nodata
`-3.4028234663852886e+38`: `mag_anom, rtp, tmi_hg, geod_2ndinv,
iso_grav_anom_slope, tc, geod_shearrate, geod_dilaterate, tmi_vg,
deq_n100a15, iso_grav_anom_vg, det_elev, iso_grav_anom, tmi,
depth_to_base_surf, ieq_n100a15, cond_surf, iso_grav_anom_hg,
det_elev_slope`.

## What was actually done with this data this session

See `outputs/experiment_h_geod_strain/experiment_report.json` (Experiment
1: a single geological hypothesis, 2 features), `outputs/
experiment2_h_allfeatures/experiment_report.json` + `threshold_sweep.json`
(Experiment 2: all 19 features + metric-aware sparsity calibration), and
`outputs/real_data_candidate/run_card.json` (the resulting honest
submission candidate). Full narrative in `docs/LIMITATIONS.md` and the
chat summary for this session.
