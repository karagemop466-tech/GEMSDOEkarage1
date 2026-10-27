# Three-pass verification — 2026-10-27

## Pass 1: implement and exercise
- Inspected initial working tree: README only; no previous pipeline to continue.
- Retrieved commit-pinned READMEs and nine historical TIFFs using GitHub API.
- Computed saved-byte SHA-256, positive-pixel masks, exact mask equality, binary Spearman and directional Euclidean three-pixel overlap.
- Built nine-site executive overview, submission guide, research slate, normalized owner requirements and negative run card.
- Added strict saved-byte validation and regression tests. No new TIFF or experiment.

## Pass 2: adversarial review and fixes
- GitHub contents API omits inline content for larger files: added Git blob fallback; no raw-host assumption.
- Found ignore pattern `data/` also hid `docs/data/`; corrected to root-only `/data/`.
- Require single-band binary historical data before using binary Spearman shortcut; nonbinary source surfaces must not be treated as masks for rank correlation.
- Kept peer-derived comparison domain separate from an authenticated competition footprint.
- Checked shifted grids, invalid numeric values and empty footprints; no format pass grants submission readiness.
- Pages configuration mutation returned 403: retained existing legacy main/root deployment; scheduled workflow only produces an audit artifact. No live auto-refresh claim.
- Source snapshots are explicitly third-party assertions. No archived owner score is promoted to organizer-confirmed.

## Pass 3: original-request re-check
- Nine-site executive sections and explicit file identities present; score estimates are unavailable, not fabricated.
- Historical duplicates are research-only; no copied raster advertised as unique.
- Independent B2 subset comparison persisted in reproducible audit script.
- Local HTML links, source snapshot hashes, note length and negative run-card semantics tested.
- Four hypotheses ranked before any modeling; novelty restricted to this initially empty repo, no invented parallel lane.
- No claim to have run shared holdout, canaries or surface checks; these remain blocked. No training/slot budget spent.
- Full original transcript not reproduced: README links an explicit normalized requirements record.
- Official reference README independently retrieved/pinned; other official hosts not reachable under network policy, so no live verification claims.

Tests: `python -m pytest -q` — 9 passed at this review. Rasterio emits upstream Affine deprecation warnings, not validation failures. Complete scientific goal is not satisfied: no new unique validated TIFF or defensible leaderboard estimate is available. These are documented blockers, not silently waived requirements.

## Concurrent integration re-check
Two sessions merged onto main during PR preparation. Resolved both merges on the assigned branch. Preserved the synthetic prototype under `archive/prototype/`; retained the second review's detailed pages, independent lattice audit, pinned template helper and release gates. `scripts/build_site.py` rebuilds both dashboards without overwriting the root audit with the detailed one. Combined suite: **44 passed**. The two audits have explicitly different comparison scopes. No inherited prototype is cleared for upload.

## Additional concurrent-source irregularity
PR #7 arrived during final integration. Code inspection found CDA1 `spatially_blocked_holdout` returns a fixed dictionary, independent of the prediction, and the generator uses synthetic layers. Quarantined its scripts, TIFFs, report and promotional pages under `archive/cda1-demonstrator/` without treating reported metrics as measurements. Restored the real review's negative active card. This is an evidence-integrity issue, not a successful holdout run. See archive README for precise code locations.
