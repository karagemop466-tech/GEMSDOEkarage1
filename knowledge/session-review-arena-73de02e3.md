# Three-pass review — `arena/73de02e3` — 29 October 2026

## Executive decision

**NEGATIVE / DO NOT SUBMIT. No GeoTIFF is cleared.** No raster was generated, no geological experiment or holdout was run, and no submission slot was selected or spent. The historical DIPDUAL entry point was blocked before geospatial imports because its old lattice-role exception is incompatible with the active literal protocol and no lane is currently assigned. The report is a repository/site review and saved-byte re-audit, not a performance result.

The user-requested nine-site table is in the [README executive summary](../README.md#executive-summary-nine-focus-sites) and the [site comparison table](../docs/executive-summary.html#comparison). It names the strongest supplied file per focus site, labels the score as `USER-REPORTED / UNVERIFIED`, reports available focus-site and lattice geometry, and marks every file **DO NOT RESUBMIT**. The registry inventory is incomplete and sourced from SHA-pinned GitHub mirrors, not organizer-authenticated assets.

## Current saved-byte decision

- [Current audit receipt](../evidence/local_downloads_and_peer_audit_20261029.json): **11** local `docs/downloads/*.tif` files and **9** pinned peer rasters across **22** commit-pinned GitHub-mirror repositories. Every audited local/peer raster exceeds the literal `>70%` 3-pixel lattice-overlap stop rule; `submit_authorized=false`. This is not a complete registry or organizer authentication.
- [Historical 28 October receipt](../evidence/local_downloads_and_peer_audit_20261028.json) remains unchanged at 9 local + 9 peer rasters. The generator now emits counts in its `scope` label, so the current receipt says 11 local files.
- **KTH + thermal legacy artifact:** [`unique-hyp-kth-therm-mask-20261028-zeros.tif`](../docs/downloads/unique-hyp-kth-therm-mask-20261028-zeros.tif), SHA-256 `a18e8fea158c2c53357b2d9651a6ce874b6329f1fdff690b4e17e8b0bb6a75eb`, contains 37,654 positive in-footprint pixels; 37,617 (99.9017369%) are within 3 px of the pinned lattice. The saved final dots fail the literal duplicate gate. No pre-placement surface or rank-correlation receipt is available; uniqueness is not certified.
- Its former sidecar claimed `HOLDOUT-DTI 0.1713`, evaluator `GEMSDOE32-HIDE-RECOVER-v3.0`, 27,735 withheld positives and CI `[0.1528, 0.1912]`, then labeled the candidate `promote`. These fields are preserved in [`legacy_kth_claim_quarantine_20261029.json`](../evidence/legacy_kth_claim_quarantine_20261029.json) as **LEGACY-UNVERIFIED, not a valid HOLDOUT-DTI**: the registry fields were empty, the saved runner forcibly set `gate_res['passed'] = True`, and no canonical holdout / canary receipt substantiates the claim. The current KTH card has no accepted holdout value and a negative verdict.
- Local KTH format diagnostics on the pinned mirror grid: one float32 band, EPSG:32611, shape 3730×3292, exact mirror transform match, values in `[0,1]`, no NaN/masked values inside the footprint, zeros outside. This is format-only; outside-footprint interpretation and portal acceptance remain untested.
- [`b2_forensics.json`](../docs/data/b2_forensics.json) gives a geometric relation only: GEMSDOE32's 37,654-dot mask is GEMSDOE25 minus 6,436 dots within 2 px of the mirrored catalogue, with no additions; it is also a subset of GEMSDOE36. The reported `0.2778` remains `USER-REPORTED / UNVERIFIED`; this relation does not establish a causal score explanation.

## Leaderboard and score evidence

The user prompt conflicts between `0.3195` and `0.4413`; repository material also contains an older `0.4544` snapshot. No live organizer portal value, artifact-linked receipt, or leaderboard state was authenticated. Treat these as conflicting user-reported/stale context—not current scores or a ranking. The public site displays the conflict and labels the live value **UNVERIFIED**.

No `HOLDOUT-DTI` was produced by this review (`value=null`); no score projection is offered. Historical holdout cards retain their own evaluator, withheld-positive count and CI labels, but they do not authorize any raster.

## Three requested review passes

### Pass 1 — implement and verify

- Corrected the local/peer audit's stale hard-coded scope string to derive the local, peer and repository counts from the actual audited inputs. Added current 11+9 regression coverage while asserting the older 9+9 receipt remains historical and unchanged.
- Quarantined both legacy KTH generation entry points. The second wrapper records that its previous code overrode the uniqueness gate; both now exit 2 before geospatial imports or writes. Also blocked the historical DIPDUAL runner before geospatial imports because its prior lattice-role exemption cannot satisfy the active literal gate and no current lane is assigned. Preserved the raw claim in a separate quarantine receipt and replaced the misleading `promote` dashboard card with a negative, hash-bound audit.
- Repaired `scripts/run_karage1_experiments.py`'s syntax error so it emits `BLOCKED` and exits 2. `scripts/prepare_data.py` now returns 2 immediately after its `BLOCKED` message rather than falling through to preparation.
- Updated the generated site and README with the current negative status, 11+9 audit, KTH disposition, score conflict, no-lane/no-experiment status, and a nine-row site comparison. The top-level site status provides no approved download.
- Added a targeted code-led novelty screen. Three proposals are documented in [`hypothesis-screen-2026-10-29.md`](hypothesis-screen-2026-10-29.md): multi-catchment bedrock-incision coherence; focal-mechanism-consistent microseismic lineaments; persistent InSAR deformation discontinuities. Existing gravity/depth/magnetic, K/Th/thermal, generic strain-seismic, LiDAR, and relay/bend methods are screened out as non-novel here. This is not a global novelty claim.

### Pass 2 — adversarial review and fixes

- Reviewed saved bytes rather than trusting the old KTH sidecar. The KTH file passes local mirror-grid/range checks but fails the lattice stop at 99.9017%, lacks a pre-placement surface/rank correlation, and is not submit-safe. Kept the unverified `0.1713` claim visible only as quarantined legacy evidence.
- Inspected the old script path and confirmed an explicit uniqueness-gate override. Replaced the entry points with fail-closed wrappers and added no-write regression checks. Also blocked the prior DIPDUAL runner before data imports, since its lattice-role exception conflicts with the active literal protocol and no lane is assigned. Corrected the historical runner parse error and the `prepare_data` fall-through.
- Rechecked the site renderer for false green states, incomplete score labels, and local links. The nine site rows now show historical research-only files, `USER-REPORTED / UNVERIFIED` labels, no organizer-confirmed estimate, a lattice witness, and worst available focus-site pair. The incomplete fleet scope is stated.
- The score conflict is displayed without selecting one value as current. Historical receipts were not relabeled as organizer evidence.

### Pass 3 — full requirements recheck

- **TIF requirement:** not met safely. No unique, full-protocol GeoTIFF was produced; all audited local files are blocked. This is an explicit negative outcome rather than a false release.
- **Nine-site table:** present in README and site; all nine requested GEMSDOE IDs are represented with reported-file evidence and **DO NOT RESUBMIT** status.
- **GEMSDOE32:** geometry documented; cause remains unproven; `0.2778` is not confirmed.
- **New hypotheses:** three ranked qualitative proposals include layers/signatures, off-catalogue rationale, project-method differences, confounders and official source routes. Payload access is not claimed. The top proposal was not tested because lane, template, source provenance and full-registry gates are unresolved.
- **Format/uniqueness:** format and literal duplicate gates are separately represented; local validation is not portal acceptance. No incomplete inventory is called a uniqueness certificate.
- **Protocol:** no lane was invented, no private experiment or holdout was run, no slot was selected, and no experimental budget was spent.
- **README/site:** current status is at the start of the README and visibly at the top of generated site pages. The score conflict and handoff are explicit.
- **Tests and build:** targeted tests passed (**37 passed**, one Rasterio `PendingDeprecationWarning`); the full suite passed (**362 passed**, 119 Rasterio `PendingDeprecationWarning`s). `scripts/build_site.py` rendered 32 deterministic pages with no submission authorized. Site-local link checks passed in the test suite, and `git diff --check` passed. No live organizer page or external official data payload was authenticated.

## Novelty-screened hypotheses and access limitations

1. **Multi-catchment bedrock-incision coherence — medium, uncertain benefit / medium cost.** USGS 3DEP elevation + 3D Hydrography; repeated channel-profile or knickzone response across neighboring catchments. New relative to screened pixel-level scarp features; confounders include lithology, base-level change, capture and fans. USGS official program links are supplied; exact tiles/payloads were not checked.
2. **Focal-mechanism-consistent microseismic lineaments — low–medium, spatially limited benefit / high cost.** USGS ComCat locations + moment-tensor nodal planes + uncertainty and strain orientation. Existing code uses strain × microseismicity; this proposal adds mechanism-orientation coherence. Sparse events, induced seismicity, aftershock clustering and catalog bias are major confounders. Coverage was not checked.
3. **Persistent InSAR deformation discontinuities — low/narrow benefit / very high cost.** Public Sentinel-1 time series, coherence and multi-epoch displacement gradients. No InSAR processing path was found in the screened modules. Atmosphere, vegetation, hydrologic subsidence, unwrapping and viewing geometry are confounders. NASA/ASF access route is linked; scene availability was not checked.

The ranking is qualitative and is not a score projection. Official links are supplied for review; no external provider payload was fetched/authenticated in this review. No lane, experiments, holdout, candidate file, submission slot, or organizer receipt exists from this work.

## Remaining work / next handoff

1. Obtain explicit method-lane and canonical-template assignments from the protocol owner; resolve any template-integrity issue without a private fork.
2. Authenticate the competition template and data from official sources; obtain a complete literal registry. Do not relax the 70% / 0.90 gates or treat the lattice as exempt without an authorized protocol change.
3. Reconcile the leaderboard conflict only from an authenticated live organizer page or artifact-linked receipt. Until then, do not state a current leaderboard score.
4. If assignments and provenance gates permit, preregister the top drainage-network hypothesis, verify public tile availability, run each feature alone through the canary, and use the shared whole-segment buffered holdout/writer. Observe the three-experiment / two-hour maximum.
5. Stop immediately if pre-placement `|Spearman| > 0.90` or final-dot overlap is `>70%` within 3 px against any registry raster. Do not select a slot. A separate selector and current weekly-cap check come only after all evidence and format gates pass.
6. Preserve the negative result if any gate fails. A locally valid GeoTIFF is not organizer acceptance.

## PR / merge status

Pull-request lifecycle is separate from the scientific run card and does not change the negative submission verdict. The active source branch is `arena/73de02e3-gemsdoekarage1`; the PR URL and merge result are reported in the final handoff after GitHub checks and the explicit merge operation are complete.
