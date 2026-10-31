# Session review — `arena/9a378959-gemsdoekarage1` — 31 October 2026

**Verdict: PROMOTE (one file).** A new, unique, format-valid GeoTIFF was generated and passed the
release gate. No submission slot was spent by this session; uploading is the owner's action.

| item | value |
|---|---|
| file | `docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif` |
| SHA-256 | recorded in `evidence/kp1_release_gate.json` (re-hashed on every site build) |
| dots | 32,000, hard 4-px minimum separation, zero within 2 px of the mapped catalogue |
| format | 15/15 saved-byte checks pass (EPSG:32611, 3730 × 3292, float32, [0,1], no NaN, zeros outside) |
| uniqueness | max \|Spearman\| 0.0076 (limit 0.90); max 3-px overlap 26.5 % (limit 70 %); nine-file mutual median 95.4 % |
| projection | 0.2789, bootstrap 95 % [0.2757, 0.2846], Δ vs champion +0.0020 — **PROJECTED, not a score** |
| holdout | reported, and explicitly **not** used to promote (§ below) |
| slots spent | 0 |
| experiments | 3 of 3 |

## Pass 1 — build and verify

* Fetched and hash-verified all pinned inputs (`scripts/kp1_data.py` raises on any digest mismatch):
  19-band `training_features.tif` (4371c82e…), catalogue (7ba308cc…), grid template (2176d08e…),
  off-catalogue SGMC proxy (643cbe99…), 12-band LiDAR scarp product (d580bb8b…), GeoDAWN
  radiometrics (c22420f7…), GeoDAWN extensions (a35a9c6d…), and the spring/well, Qfaults and vent
  tables. All values match the digests pinned in `registry/data_manifest.json`, `vendor/gems57/
  prepare_data.py` and this repository's manifest.
* EXP1 measured all nine registry rasters and found the covariate associations in
  `knowledge/kp1-preregistration-20261031.md` §2.
* EXP2 ran the leakage canary (max AUC 0.599, no alarm), calibrated the shared evaluator against the
  nine known scores (Spearman −1.0), measured a leave-one-quadrant-out physics detector and compared
  four arms at a fixed budget.
* EXP3 built the candidate and passed the release gate.

## Pass 2 — adversarial review

* **Contradiction found and fixed in the public site.** The old landing page said “no file is
  cleared”. The banner now names the cleared file and the sentence below it was rewritten to say
  that *the 29–30 October artifacts* are not cleared. Both statements are now true simultaneously.
* **The banner cannot lie.** `scripts/render_site.kp1_banner()` re-hashes the GeoTIFF and compares
  it with the gate receipt; any mismatch, missing receipt or `ok_to_submit: false` downgrades the
  banner to a red notice. Covered by `tests/test_kp1_lane.py`.
* **The build is reproducible.** `scripts/build_kp1_site.py` refuses to publish if the gate receipt
  does not describe the file on disk; the pages are byte-identical across runs (CI checks it).
* **Operator error to be aware of:** the first run of the older `vendor/gems57/prepare_data.py`
  writes into `vendor/data` because that file expects to sit at the repository root. The session
  moved the verified bytes to `data/official/` and symlinked `data/bridge/`, which is what
  `gems57.grid` reads. This is a vendor path quirk, not a data problem.

## Pass 3 — against the original request

* Executive summary per site with an obvious best-to-submit: **yes**, `docs/kp1/executive-summary.html`
  and Table 1 (`docs/kp1/index.html`), stating that none of the nine should be resubmitted.
* Table of file / estimated score / uniqueness: **yes**, Table 1, with the estimate labelled
  PROJECTED and the uniqueness measured both against the literal rule and against its chance level.
* Unique TIF, downloadable, obvious OK/NOT-OK: **yes**, banner + `docs/kp1/index.html` + `docs/kp1/
  how-to-submit.html`.
* 3–5 named hypotheses with layers, signature, why off-catalogue, difference and mimic, ranked:
  **yes**, §5 of the preregistration and `docs/kp1/research.html`.
* Validate before touching a slot: **ran**, and the mandated instrument was found invalid for this
  purpose; that negative result is the session's most important finding and is recorded rather than
  quietly used.
* No manual intervention: the whole chain is `scripts/kp1_*.py` plus `scripts/build_site.py`.
* No hallucinations: every number on the site is read from a committed JSON receipt by the renderer.

## Irregularities flagged (no fix attempted)

1. `labels.tif` and `existing_faults.tif` are byte-identical, while the organizer page describes a
   sample submission predicting *total fault absence*. The mirror's sample carries 60,988 positives.
2. The literal 70 % / 3-px uniqueness rule is saturated for this raster family: all 36 pairs among
   the nine focus files score 97.5–100 % against a 15–18 % chance level.
3. The shared holdout evaluator is anti-correlated with the nine known scores (Spearman −1.0).
4. `vendor/gems57/prepare_data.py` pins four external files at `buffedlizard55-lab/6GEMSDOE@e2fe3f41`,
   a commit with no `data/external` tree, so the fetch fails. The proxy actually used carries the
   same SHA-256 as the first pin and was taken from `buffedlizard55-lab/GEMSDOE24`.
5. No organizer receipt exists for any score on this site; all nine are user-reported.

## What the next session should do

1. Upload the cleared file (owner action) and record the returned score with the file's SHA-256.
   That receipt is the only thing that can replace the projection with a measurement, and it is the
   first datum that could start a real calibration curve.
2. If the score disappoints, the diagnostic is already prepared: compare the returned score with the
   projection ±0.03 and with the covariate position (32,000 dots, 55.5 % > 15 px). A large miss
   falsifies the covariate model, not the gate.
3. Build hypothesis 2 (spring–lineament intersection census) and hypothesis 3 (upward-continuation
   depth series) if and when the official GeoDAWN archives become reachable — h3 is the strongest
   untested idea and is blocked only by the sandbox network allowlist.
4. Ask the protocol owner to rule on the two saturated gates (uniqueness, holdout) before any further
   parallel sessions repeat them.
