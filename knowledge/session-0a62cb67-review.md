# Session review — 28 October 2026, `arena/0a62cb67-gemsdoekarage1`

**Decision: NEGATIVE / DO NOT SUBMIT.** No new GeoTIFF, geological experiment,
holdout score, leaderboard forecast, or weekly-slot selection was made in this
session. See the [session run card](../evidence/session_0a62cb67_run_card.json)
and active [current run card](../docs/data/run-card.json).

## Pass 1 — reproduction of prior findings and saved-byte audits

- Reviewed the standing brief, `AGENTS.md`, `README.md`, `knowledge/OWNER_BRIEF.md`,
  `knowledge/research-review.md`, `knowledge/three-pass-review-2026-10-28.md`,
  and `knowledge/parallel-candidate-audit-2026-10-28.md`.
- Verified `scripts/shared_tools.py preflight`: no assigned method lane is present
  (`"lane": null`) and the 5 required shared cache/data inputs are absent from
  the tracked checkout.
- Fetched the pinned GitHub mirror rasters into ignored `.cache/` directories
  and independently re-ran:
  - `scripts/audit_references.py --fetch` (12 pinned assets: template, labels,
    lattice, and the 9 focus sites `GEMSDOE24`, `25`, `27`, `28`, `30`, `31`,
    `32`, `33`, `36`),
  - `scripts/audit_existing_candidates.py` (committed HMAS and GPC-Z TIFFs),
  - `scripts/audit_prior_candidates.py --fetch`,
  - `scripts/audit_parallel_candidates.py --fetch` (pinned PR 20 `TD-KSCK` and
    PR 19 `CTWS-2D` TIFFs),
  - `scripts/audit_archives.py` and `scripts/audit_concurrent.py --fetch`.
- Every reproduced JSON report matched the committed evidence byte-for-byte
  (excluding execution timestamps and runtime package metadata):
  - `HMAS-SINTER`: 38,174 / 38,200 = **99.9319%** within 3 px of the registered lattice.
  - `GPC-Z`: 35,959 / 36,000 = **99.8861%** within 3 px of the registered lattice.
  - `TD-KSCK` (PR 20): 37,584 / 37,654 = **99.8141%** within 3 px of the registered lattice.
  - `CTWS-2D` (PR 19): 37,999 / 38,200 = **99.4738%** within 3 px of the registered lattice.
  - `GEMSDOE32` B2 (37,654 dots) is identically `GEMSDOE25` d2.8 (44,090 dots)
    minus the 6,436 dots within Euclidean distance ≤ 2 pixels of `labels.tif`,
    with 0 additions; `GEMSDOE25` and `GEMSDOE30` share the exact same positive
    dot mask inside the mirrored footprint.

## Pass 2 — adversarial code review and fail-closed hardening

Identified and fixed five edge cases across the validation, release-gate, and
audit tools:

1. **Duplicate registry digests & whitespace IDs in `scripts/release_gate.py`:**
   The release gate checked duplicate `row["id"]` strings, but allowed multiple
   comparison rows with distinct IDs to reuse the same `row["sha256"]` digest
   (which could pad `expected_rasters`), and did not strip whitespace-only
   `row["id"]` strings. It also did not reject `validator.template_sha256 == raster_sha256`
   (self-template validation) or require `valid_sha256(reg["candidate_sha256"])`
   when `raster_sha256` was also missing. All four conditions now fail closed.
2. **Self-template validation in `scripts/validate_geotiff.py`:**
   `diagnose(candidate, template)` previously allowed `candidate` and `template`
   to be the same file (directly or via symlink/hardlink), which would trivially
   pass grid/footprint checks against itself. It now raises `ValueError` if
   `candidate` and `template` resolve to or reference the same file.
3. **Reference distinctness and template driver check in `scripts/validate_artifact.py`:**
   Added `distinct_reference_files` (verifying `candidate` is not the same file
   as `template` or `footprint`) and `template_single_band_geotiff` (verifying
   `template` and `footprint` are single-band GeoTIFFs).
4. **Masked in-footprint candidate pixels in `src/gemskarage1/registry_audit.py`:**
   `run_full_fleet_uniqueness_gate` inspected raw `ds.read(1)` values on the
   saved candidate GeoTIFF without checking `ds.read_masks(1)` inside the
   footprint, so a finite nodata sentinel (`nodata=1.0`) or internal GDAL mask
   could hide in-footprint dots. It now requires `ds.driver == 'GTiff'` and all
   in-footprint pixels to be unmasked (`valid_mask[foot].all()`).
5. **Hardening `scripts/audit_parallel_candidates.py`:**
   Required `float32` dtype in `read_pinned`, required defined binary Spearman
   correlation in the footprint (`rho is not None`), blocked `--out` from
   overwriting any input raster (including via symlink/hardlink), switched
   `--out` to atomic `tempfile.mkstemp` + `replace`, and returned exit code 2
   on `OSError` / `ValueError` / `subprocess.SubprocessError`.

## Pass 3 — recheck against requirements and limitations

- Ran `.venv/bin/python -m pytest -q`: **245 passed** before merging concurrent
  `origin/main` updates and **295 passed**, 0 failed, 0 skipped after merging
  `origin/main`.
- Ran `.venv/bin/python scripts/build_site.py` and `scripts/reconcile_prior_decisions.py`:
  all 32 HTML pages and reconciled evidence files are deterministic and preserve
  the prominent `DO NOT SUBMIT` decision.
- All nine focus sites (`GEMSDOE24`, `25`, `27`, `28`, `30`, `31`, `32`, `33`,
  `36`) have clear executive summaries, unverified user-reported historical
  scores, measured lattice overlaps, B2 geometric/DTI analysis, and four ranked
  untried geological hypotheses with layers, physical signatures, off-catalogue
  rationales, non-fault mimics, and official data sources.
- **Remaining blockers and limitations:**
  1. No single assigned method-lane paragraph was supplied in the prompt.
  2. The dense registered lattice leaves only 6,649 of 5,167,373 mirrored
     footprint pixels outside its 3-pixel neighborhood, bounding any strictly
     compliant discrete placement to at most 22,163 dots unless the owner
     clarifies the protocol.
  3. The sandbox network allowlist permits GitHub/PyPI/npm only; direct
     DrivenData, USGS, GDR, NLR, and Dropbox downloads or portal checks are
     unavailable here, and GitHub mirrors are not organizer-authenticated.
  4. The authoritative shared template, cached feature stack, complete live
     registry, and frozen same-fold holdout baseline must be established before
     running any new experiment or invoking the separate weekly-slot selector.
