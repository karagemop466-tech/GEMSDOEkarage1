# Session review — 28 October 2026 (`arena/0150ae73-gemsdoekarage1`)

**Decision: DO NOT SUBMIT.** No new GeoTIFF, holdout score, geological experiment, or competition slot selection was produced in this session. `registry/template.json` has `method_lane: null`, the shared cached feature stack (`.cache/gems_work/feature_stack.npy`) is absent, the organizer-authenticated `sample_submission.tif` is not established, and the full registry inventory is incomplete. Every historical or parallel-branch candidate audited in this repository fails the literal `> 70%` 3-pixel overlap rule against the registered lattice witness (`b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2`).

## Pass 1 — baseline reproduction and execution

1. Read `README.md`, `AGENTS.md`, `docs/standing-prompt.md`, the previous session reviews, the active negative run card (`docs/data/run-card.json`), the nine-site reference audit (`docs/data/reference-audit.json`), the B2 DTI analysis, the four ranked qualitative hypotheses (`knowledge/research-review.md`), and the official source register (`knowledge/sources-2026-10-28.md`).
2. Executed `python3 scripts/shared_tools.py preflight` and `python3 scripts/prepare_data.py`: confirmed both fail closed (exit code 1 and exit code 2 respectively) because `method_lane` is `null` and the shared `.cache/gems_work/feature_stack.npy` is not present.
3. Restored and verified all 31 commit-pinned GitHub mirror files in `registry/karage1_data_manifest.json` (`bash scripts/download_competition_data.sh --data-dir .cache/gems_data --verify-only`) and all 12 reference rasters in `registry/reference_assets.json` into ignored scratch caches. Hashes confirm mirror byte identity only, not organizer authenticity.
4. Independently re-ran `scripts/audit_references.py`, `scripts/audit_existing_candidates.py`, `scripts/audit_prior_candidates.py`, `scripts/audit_current_release.py`, `scripts/audit_parallel_candidates.py`, `scripts/audit_concurrent.py`, `scripts/audit_archives.py`, and `scripts/validate_geotiff.py`. Every audit reproduced its committed JSON evidence exactly:
   - `karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif`: `38,174 / 38,200` (`99.9319%`) within 3 px of lattice -> duplicate (`DO NOT SUBMIT`).
   - `gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-zeros.tif`: `35,959 / 36,000` (`99.8861%`) within 3 px of lattice -> duplicate (`DO NOT SUBMIT`).
   - `gemsdoe-karage1-td-ksck-20261028T132000Z-37654d-f8fc20a1-nan.tif` (PR 20): `37,584 / 37,654` (`99.8141%`) within 3 px of lattice -> duplicate (`DO NOT SUBMIT`).
   - `karage1-ctws2d-crustal-20261028T124800Z-f7c2be43-zeros.tif` (PR 19): `37,999 / 38,200` (`99.4738%`) within 3 px of lattice -> duplicate (`DO NOT SUBMIT`).
   - `GEMSDOE32` (`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`, 37,654 dots, user-reported `0.2778`) equals `GEMSDOE25` (`gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif`, 44,090 dots, identical dot support to `GEMSDOE30`) minus the `6,436` dots within `<= 2 px` (`200 m`) of the mirrored known-fault catalogue, with `0` dots added.

## Pass 2 — adversarial review and fail-closed fixes

Inspected the uniqueness gate, release gate, and audit scripts for fail-closed edge cases and implemented targeted fixes with regression tests:

1. **`src/gemskarage1/registry_audit.py` (`run_full_fleet_uniqueness_gate`)**: Previously checked `ds.read(1)` on `final_tif_path` without verifying `ds.driver == 'GTiff'` or `(ds.read_masks(1)[foot] != 0).all()`. A candidate GeoTIFF whose in-footprint pixels were masked by a finite nodata sentinel (e.g. `nodata=1.0`) or an internal GDAL mask band could pass `run_full_fleet_uniqueness_gate` even though `_verify_registry_pixels` and `validate_geotiff.py` reject masked in-footprint pixels. Added explicit `ds.driver == 'GTiff'` and `valid_mask[foot].all()` enforcement.
2. **`scripts/release_gate.py` (`assess`)**:
   - Rejected duplicate `sha256` digests across `registry.comparisons` rows (`Duplicate registry raster hash`) and whitespace-only `id` strings (`not ref_id.strip()`), preventing an incomplete registry scan from padding `expected_rasters` by repeating the same reference raster hash under multiple IDs.
   - Enforced `len(submission_name) <= 140` to match `submission_writer.py`.
   - Rejected mismatched `baseline_withheld_positives != withheld_positives` when `baseline_withheld_positives` is supplied in `holdout`.
   - Rejected `validator.unmasked_inside is False` or non-zero `validator.masked_inside_count`.
3. **`scripts/audit_parallel_candidates.py`, `scripts/audit_references.py`, `scripts/audit_existing_candidates.py`, `scripts/audit_prior_candidates.py`, and `scripts/audit_current_release.py`**:
   - Hardened `scripts/audit_parallel_candidates.py` so `--out` refuses to overwrite any input raster in `args.directory` (including via symlinks/hardlinks), creates parent directories, and writes atomically via `tempfile.mkstemp`.
   - Enforced unmasked in-footprint checks (`read_masks(1)[fp] != 0` / `masked_inside_count == 0`) across `audit_references.py`, `audit_existing_candidates.py`, `audit_prior_candidates.py`, and `audit_current_release.py`.

## Pass 3 — re-check against original requirements

1. Re-ran `python3 scripts/build_site.py`: rendered 32 deterministic pages with zero diff (`git status` clean on tracked HTML/JSON).
2. Re-ran `python3 -m pytest -q`: **244 passed** (including new synthetic regressions in `tests/test_registry_literal.py`, `tests/test_release_gate.py`, and `tests/test_parallel_candidate_audit.py`).
3. Verified `git diff --check` is clean and all untracked scratch caches are removed or gitignored.

Session run card: [evidence/session_0150ae73_run_card.json](../evidence/session_0150ae73_run_card.json).
