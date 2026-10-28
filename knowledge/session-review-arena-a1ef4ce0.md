# Current review — session a1ef4ce0, 28 October 2026

**Verdict: NEGATIVE / DO NOT SUBMIT. No new TIFF was generated.** The requested unique, high-scoring, submission-cleared GeoTIFF remains **undelivered**. No geological experiment, holdout measurement, slot selection, or competition upload was made in this session. This is a verified engineering/audit improvement, not a claim of scientific progress or completion of the original request.

[Executive summary and nine-site table](../docs/executive-summary.html) · [Session JSON card](../evidence/session_a1ef4ce0_run_card.json) · [Official-code source receipt](../evidence/official_code_receipt_a1ef4ce0.json)

## 1. What was independently verified this session

### Nine-site saved-byte replay

Ran `scripts/audit_references.py --fetch --out .cache/session-a1ef4ce0/reference-audit.json`. All twelve assets (nine focus-site TIFFs, mirror sample, mirror labels, lattice) were freshly fetched from the immutable GitHub commits in [`registry/reference_assets.json`](../registry/reference_assets.json) and SHA-256 checked. The complete reproduced audit equals [`docs/data/reference-audit.json`](../docs/data/reference-audit.json) after removing only `created_utc` and `software`. This establishes repeatability of those mirror-byte measurements, **not organizer authenticity** or coverage of the full submission registry.

The existing executive summary has an individual page for every requested focus site, filenames and pinned research-download links, a historical-result column, a separate estimate column, uniqueness diagnostics, and the submission guide. The estimate column remains **Unavailable**. Historical portal results supplied by the user are preserved as **USER-REPORTED / UNVERIFIED**, not relabelled ORGANIZER-CONFIRMED. There are no receipt-backed organizer results for this session.

No other repository's website was edited. The nine individual summaries are pages of **this repository** (`docs/GEMSDOE24.html` through the nine requested names), not deployments to those nine repositories.

### B2 interpretation: geometry is proven, causation is not

On the pinned mirrored footprint, GEMSDOE25 and GEMSDOE30 have exactly equal binary support. GEMSDOE32 B2 is that parent support with all dots within two pixels of the mirrored fault catalogue removed: parent 44,090 dots, removals 6,436, child 37,654, no additions. These are **audit counts, not scores**. The user-reported historical value **0.2778 is UNVERIFIED**; no leaderboard estimate is derived from it.

Why could removal help? For the documented DTI form, let T be weighted true-positive coverage, F false-positive mass, G the number of truth pixels, and D = T + αF + β(G−T) + ε. Deleting predictions loses coverage L and removes false-positive mass c. With positive denominators, the score increases exactly when:

```
α T c > L (α F + β G + ε)
```

Thus deleting a redundant low-yield dot can help, but deleting a dot near a genuinely missing fault can hurt. The binary-mask identity cannot measure either quantity on hidden organizer truth. The claim in the newly integrated historical `session-review-arena-cf677bd7.md` that removal *raises* DTI must be read as a conjecture, not a demonstrated causal result. The record does **not** prove all near-catalogue dots have little value or that a wider collar will beat B2. The target is fault mapping; a mapped or predicted fault does not establish an active geothermal vent.

Metric/specification reference for manual review: [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric). This host was not freshly accessible in this network-restricted session; see the existing [source register](sources-2026-10-28.md). The algebra above is conditional on that documented metric, not a new organizer measurement.

### Official source code, fetched directly

Re-fetched the organizer-owned [reference repository](https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b), pinned to `aebe92f7c8a990f0e3443451b7a825d9afd6336b`. File hashes, sizes, source URLs and notebook cell locations are recorded in the [source receipt](../evidence/official_code_receipt_a1ef4ce0.json).

- The [official README](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md#choosing-gpu-vs-cpu) explicitly supports a CPU-only setup. A GPU accelerates this reference training; it is **not an absolute prerequisite**. The inherited prompt's GPU-only statement is too strong.
- The [notebook](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb) uses randomized patch splits and `TverskyLoss`. That reference is **not** the requested whole-segment, buffered hide-and-recover experiment. Its training loss is not a substitute for the required DTI evaluator.
- Its export example uses one GeoTIFF band and the label-grid CRS/transform. An export example does not verify novelty, input provenance, inference range, or portal acceptance.

No new official geological dataset was obtained. DrivenData, USGS, GDR, NLR, Dropbox and the live leaderboard are outside this sandbox's network allowlist. No live leaderboard rank, current weekly cap, current score target, successful portal submission or current official download availability is asserted.

## 2. Preregistered research slate — proposals only, not assigned lanes

The previous sessions already proposed signed offsets, texture displacement, alteration ratios, drainage asymmetry, conductivity-interface bending and basement-step ridges. Those are **not** advertised here as fresh inventions. The three more specific tests below were not found in the reviewed active `src/gemskarage1` implementations or experiment runners. This is a repository-local distinction only: fleet-wide or literature novelty is **unverified**. All are geological hypotheses and have no measured or numeric projected DTI gain.

Ranking is qualitative expected value relative to implementation cost. It is not a promise of improvement. Every proposal uses competition-feature layer names already recorded in the mirrored band audit, not a new externally acquired dataset. Raw layer semantics must still be checked against organizer metadata, and authorized shared-cache access is required. None is currently execution-ready.

| Priority / cost | Specific layers and physical signature | Why a missed fault, rather than just the catalogue? | Difference from reviewed implementations / named non-fault mimic |
|---|---|---|---|
| 1 / medium | **Magnetic texture-boundary change point**: `rtp` and `tmi`, with `det_elev_slope` as context. Remove the local planar trend, compute direction-dependent robust semivariograms in two disjoint half-windows, and test for a persistent change in correlation length or anisotropy across a candidate boundary, rather than a peak gradient. | A concealed fault might juxtapose blocks with different magnetic fabric even when the anomaly amplitudes match and there is no surface scarp. The test does not use catalogue proximity as a predictive feature. It may still preferentially recover mapped contacts; holdout decides. | Existing HMAS/BB-STEP use gradient/trough/crest strength and alignment; the earlier texture proposal measures displacement, not second-order texture statistics. **Mimics:** unfaulted lithologic contacts, volcanic texture boundaries and flight-line processing seams. Test acquisition orientation and terrain-matched control boundaries. |
| 2 / medium-high | **Paired fault-block tilt break**: `det_elev`, `det_elev_slope`, `depth_to_base_surf`, `iso_grav_anom`. Fit robust planes on either side of a candidate line, suppress regional relief, then test a coherent change in plane tilt with a compatible basement-depth kink and gravity residual. | Aggradation or erosion can soften a scarp while leaving block-scale tilting. No tip or distance features derived from the full fault catalogue are allowed. This seeks displaced blocks, not all steep terrain. | Unlike existing local Hessian/NMS ridges and basement inflection, fits two regional planes and checks relative rotation. **Mimics:** alluvial-fan dip, differential compaction, bedding dip and erosional pediments. Compare with fan-like radial slopes and an unfaulted smooth-basin null. |
| 3 / high | **Magnetic edge-network severance**: `rtp`, `tmi_hg`, `tmi_vg`, `iso_grav_anom_hg`. Extract persistent magnetic contour/edge networks, detect repeated termination of independent cross-cutting edges along a gravity-supported boundary, and compare against rotated network nulls. | A concealed fault can truncate several magnetic markers even where its own lineament is weak. Repeated cross-cutting relationships, not catalogue endpoint proximity, define the proposed feature. | Existing Euler/lineament, continuation and tip methods are adjacent prior art; the specific test is multiplicity of independent marker terminations with a null, not edge magnitude or extrapolation of mapped tips. **Mimics:** survey seams, intrusive contacts, lava-flow boundaries and interpolation gaps. Network independence and seam rejection are mandatory. |

**Availability:** the layer-name audit and mirror source pins exist, but the approved cached stack is absent. These proposals do not require new external layers; they do require authenticated competition inputs, the assigned lane and canonical shared tools. The official [competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) is the needed source for authoritative inputs, but current obtainability from this session is **not established**. No proposal relying on unverified new external data is marked viable.

**Top-candidate validation is blocked, not passed.** `registry/template.json` has no method lane or canonical assignment. Inventing a lane to run the texture proposal would violate the parallel-run protocol. No per-feature canary, surface comparison, placement or holdout is reported for it. The standing baseline also lacks a frozen, authorized, same-fold best against which a new run could be promoted.

When prerequisites are resolved, the top proposal must first pass feature-by-feature canaries; then buffered whole-segment hide-and-recover with visible-only catalogue processing and pixel-exact masking; pooled HOLDOUT-DTI with evaluator, withheld-positive count and paired spatial confidence intervals; and both registry checks. A positive paired interval and a higher same-evaluator baseline result are required by the local promotion policy. Any duplicate or leakage finding stops the run. The cap remains three experiments or two hours, and slot selection remains separate.

## 3. Why generating a TIFF now would not satisfy the request

Fresh shared preflight confirms: absent lane, absent canonical assignment, missing approved feature cache and four expected data files in the shared execution path. Restored audit inputs are deliberately in a separate audit cache; a pinned mirror is not authenticated training data. The template-integrity audit still reports modified vendored bytes and a source-template identity mismatch. No shared evaluator or writer was modified or repinned in this session.

The lattice replay independently confirms 6,649 footprint pixels are outside the closed three-pixel witness disk. At the historical B2 budget of 37,654 distinct dots, even a best-case placement must overlap at least 31,005 dots, or 82.3418%, which exceeds the literal 70% stop rule. This is a **geometric audit bound**, not a score and not proof that every smaller raster is impossible. At most 22,163 dots are not ruled out by this bound alone. Filling uncovered holes or shifting dots to evade the witness is not a scientifically defensible workaround.

No old TIFF was copied, jittered, renamed or blended into a supposedly new submission. No new score estimate is supported. The original rejected TIFF is unavailable, so the cause of the portal range error remains unknown. Existing interior-nodata findings describe a plausible mechanism only, not a confirmed diagnosis.

## 4. Implemented automatic gate fixes

In `scripts/release_gate.py`:

1. **Baseline evidence is now mandatory:** a positive, integer withheld-positive count must be supplied for both candidate and baseline, and they must match. Previously an omitted baseline count could pass, even though the card was claiming a same-fold paired improvement. Counts plus split hashes are still consistency checks, not proof that evaluation was honest.
2. **Mask evidence is now mandatory:** require `unmasked_inside: true` and an explicit integer `masked_inside_count: 0`. Previously both fields could be absent while finite/range booleans passed. Finite nodata sentinels and internal GDAL masks make finiteness insufficient. Boolean `false` and floating `0.0` are not accepted as a pixel count.
3. **Preserve source evidence:** input/output path aliases are refused before writing, including malformed JSON, symlinks, hardlinks and relative spellings. This overlaps a safeguard concurrently merged by session `400355af`; that upstream fix and its duplicate-key JSON rejection were retained, not privately reimplemented. The CLI continues to return nonzero for blocked evidence and never grants upload authorization.

The gate is a policy over supplied assertions. It does **not** re-evaluate a model, authenticate receipts, prove registry completeness or replace saved-byte validation. Even a synthetic `promote` test fixture has `ok_to_submit: false`; a selector is still required. Do not describe these software tests as geological experiments or validation scores.

## 5. Three passes and reproduction

1. **Implement and verify:** reviewed the standing requirements and active pipeline; independently fetched the twelve pinned audit assets and the organizer reference code; replayed the nine-site audit; reproduced the two omission bypasses; fixed them and added regression cases.
2. **Adversarial review:** tested absent fields, boolean/float/string/null pixel and baseline counts, good/malformed input/output aliases; integrated concurrent mainline duplicate-key and source-preservation tests; kept all existing strict thresholds and source caveats. The historical causal claim noted above is flagged, not adopted.
3. **Full recheck:** full test suite, deterministic page build, link tests, strict JSON tests, negative card, no new raster files, and no shared-template edits. Final verification: **330 software tests passed**, no failures; 119 Rasterio/Affine pending-deprecation warnings. The first full run exposed stale generated historical rejection reasons after the policy change; the reconciler regenerated those two negative receipts, and the full rerun passed. Test commands and counts are also recorded in the session JSON card. No test constitutes a holdout result.

Reproduce with a Python virtual environment and dependencies from `requirements.txt`:

```sh
python -m pytest -q
python scripts/build_site.py
python scripts/audit_references.py --fetch --out .cache/session-a1ef4ce0/reference-audit.json
python scripts/shared_tools.py preflight       # expected nonzero: blocked
python scripts/audit_template_integrity.py     # expected nonzero: not authorized
```

For comparison of replay JSON, remove only `created_utc` and `software` from the replay and `docs/data/reference-audit.json`; all remaining fields must match exactly. Use the pinned reference manifest rather than changing it to fit downloaded bytes.

## Next session: actual prerequisites, not another nominal submission

1. Record the missing assigned method paragraph and authoritative template/cache assignment; repair shared defects only in their owning template. These are coordination facts and cannot safely be inferred from filenames or prior parallel runs.
2. Resolve the dense-lattice interpretation through an explicit protocol-owner decision. Until then retain the literal stop, without exemptions or hole-stuffing.
3. Authenticate organizer data/sample bytes; establish the complete registry and a frozen same-fold holdout best. GitHub mirror hashes alone cannot do this.
4. Only then run the assigned proposal under the protocol budget, publish a new TIFF if gates permit, and hand off a promoted result to the separate selector. Authenticate the live weekly allowance before any slot selection.

The current deliverable is an honest negative decision plus hardened automated evidence gates. A uniquely named or technically valid TIFF would not substitute for the requested unique, validated high-scoring submission.
