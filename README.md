# GEMS / KARAGE 1 — evidence before a submission

**DO NOT SUBMIT — no candidate is currently cleared.** The prior H-K1-1 and
GPC-Z rasters both fail the required literal uniqueness stop. There is no new
competition-ready GeoTIFF, no defensible predicted leaderboard score and no
submission slot selected. A negative result is a valid deliverable.

[Executive dashboard](https://karagemop466-tech.github.io/GEMSDOEkarage1/) ·
[Executive summary & future submission guide](docs/executive-summary.html) ·
[Current JSON run card](docs/data/run-card.json) ·
[Saved-byte reassessment](evidence/release_reassessment_20261028.json) ·
[Research slate and official sources](knowledge/research-review.md)

## Decision and evidence, reviewed 28 October 2026

| Historical raster — research only | Literal registered-lattice witness | Saved bytes | Decision |
| --- | --- | --- | --- |
| [H-K1-1 HMAS-SINTER TIFF](docs/downloads/karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif) | 38,174 / 38,200 = **99.9319%** within ≤3 pixels | Mirrored-grid and all-finite [0,1] checks pass; **null/NaN-outside diagnostic fails** | **DO NOT SUBMIT** |
| [GPC-Z TIFF](docs/downloads/gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-zeros.tif) | 35,959 / 36,000 = **99.8861%** within ≤3 pixels | Mirrored-grid and all-finite [0,1] checks pass; **null/NaN-outside diagnostic fails** | **DO NOT SUBMIT** |

The stop is **>70% directed final-dot overlap within 3 pixels of any registered
raster**. The earlier fleet report excluded the lattice and its apparent
clearance is **superseded**. A single duplicate is sufficient to stop; the new
witness is not an exhaustive certification of every other registry raster. The
surface check is separately required **before placement** and was not
independently replayed for these old outputs. Integrity pins on owner mirrors do
not authenticate them as official organizer bytes; portal acceptance is untested.

The local HMAS saved TIFF SHA-256 is
`198076f81067353c3ee41d947c7830ef11db2e8128bc5f8c5bd20ef036736f76`; its
historical ZIP SHA-256 is
`b1c8817b1037384d8d12d6c3b9077716398aa756a931978bc5e5b1f52e3d15e7`.
These artifacts are accessible for **research only**, not submission. The
prior receipt’s slot approval and previous README/dashboard promotion claims
have been withdrawn.

The inherited **HOLDOUT-DTI** was 0.093547, evaluator `gems57-pooled-hide-v2`,
22,619 withheld positives, 95% CI [0.081837, 0.105279]. It was **not independently
replayed in this reassessment**; earlier splits did not establish the requested
whole-fault buffered protocol, and other inherited counts/CIs disagree. This
value is not a leaderboard estimate or evidence that the present file should
be submitted. No new experiment or slot was spent in this review; the account’s
actual quota is unknown.

## Competition and nine-site comparison

The [nine-site table](docs/executive-summary.html#comparison) links to individual
summaries for GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31,
GEMSDOE32, GEMSDOE33 and GEMSDOE36, with artifact
identity, user-reported historical claims, measured overlap and **unavailable**
score estimates. They are not verified organizer receipts. GEMSDOE32’s reported
0.2778 for `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` is an owner report,
not ORGANIZER-CONFIRMED. On the mirrored grid its support is exactly the
GEMSDOE25 parent after deleting 6,436 dots within two pixels of the mapped-fault
catalogue; thinning might improve distance-weighted precision, but hidden
labels are unavailable and the cause is not established. Beating it is
possible in principle, not demonstrated. The [research review](knowledge/research-review.md)
contains the conditional mathematical explanation and uncertainty.

The [official live leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
was manually checked 28 October 2026: public #1 was `xiaofanhu`, 0.4544, at
that time. This aggregate board is **not** a file-linked submission receipt;
user-reported 0.4413 and 0.3195 are not silently substituted for it. The static
site does not scrape or guarantee a current leaderboard. Private labels and
account slots require an authenticated user session.

Official data and rules: [DrivenData problem and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
[GDR INGENIOUS](https://gdr.openei.org/submissions/1391),
[DOE/NLR rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf), and
[staff clarification on masking](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516).
Official download descriptions were checked; login-gated organizer bytes and
the external official data packages were not fetched in this environment.

## Reproduce the review and site

```bash
python -m venv .venv && .venv/bin/pip install -e . pytest
# Public owner mirrors, integrity checked; large files are ignored by Git.
./scripts/download_competition_data.sh --data-dir data --id sample_submission --id labels \
  --id calib_13gems_20261001_r13-lattice-s5_v2_nan-ou --id scored_gems25_d28_nan \
  --id scored/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif
.venv/bin/python scripts/audit_current_release.py \
  --champion data/scored/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif \
  --out evidence/release_reassessment_20261028.json
.venv/bin/python -m scripts.sync_review_status
.venv/bin/python scripts/build_site.py
.venv/bin/python scripts/generate_pages.py
.venv/bin/python scripts/render_site.py
.venv/bin/python -m pytest -q
```

The audit needs the pinned GEMSDOE32 champion, as shown above. The restorer accepts `--verify-only`,
`--id`, and `--group` and verifies sizes/hashes before atomic replacement. A
hash match means identical mirror bytes, not official provenance. The legacy
experiment runner deliberately exits before training or writing: its split and
release decisions are not acceptable for the standing protocol. The shared
`buffered_component_draw` exists but still needs integration with matching
fold-specific feature recomputation and out-of-fold refits. Do not choose a
lane or override the duplicate stop to create a TIFF.

The homepage automatically checks the nine public GitHub revision pins on page
load and every 30 minutes while visible; errors/rate limits show “Unavailable”,
not a pass. The scheduled GitHub Actions refresh publishes a review artifact,
not an automatic main-branch or Pages update. Neither feed checks scores or
scrapes DrivenData: check the live official site manually and respect its terms. [Further limitations and hypotheses](knowledge/research-review.md).

## Standing prompt and principles

The original verbatim text was not preserved before session compaction. This
is the faithful standing requirements record, rather than a claim to be the
verbatim prompt. The full clause-by-clause version is in
[docs/standing-prompt.md](docs/standing-prompt.md).

- **Maximize P(Win). Own the Outcome.** Improve the probability of a higher
  confirmed score; report negative results, blocked access and uncertainty.
- Generate an **original**, valid single-band [0,1] GeoTIFF on the competition
  grid, never a renamed earlier entry. Put an unmistakable download/submit
  status, executive summary, per-site nine-way comparison, file, unique name,
  ≤140-character note and clear future submission steps on GitHub Pages.
- Explain the GEMSDOE32 B2 result and whether it can be beaten; propose 3–5 new
  geological hypotheses, layers, mechanisms, mimics, differences, expected
  improvement/cost and official data obtainability. Validate the top hypothesis
  against the current best on a spatially blocked holdout before any slot.
- **Parallel-run protocol:** stay in the provided method lane; check every
  registered raster. Rank correlation >0.90 or >70% of final dots within 3 px
  is a duplicate: log and stop. Perform the surface check **before placement**.
  Reuse the shared cached stack, evaluator and submission writer; repair shared
  code once rather than forking. Hide whole fault segments plus buffer, rebuild
  catalogue features from visible faults only, mask visible fault pixels exactly,
  and use pooled DTI with α=0.2, β=0.8 and a 300 m triangular kernel.
- Label measurements **HOLDOUT-DTI** with evaluator, positive count and 95% CI,
  or **ORGANIZER-CONFIRMED** only from a file-linked receipt; projections are
  not scores. A feature-alone AUC >0.90 is leakage until disproved.
- Validate saved bytes autonomously, including no NaN inside the footprint,
  [0,1], exact grid and hash. Identify outside-encoding uncertainty; do not
  claim portal acceptance without a receipt. Verify claims against reliable
  official sources, provide review links, and use free public/verified data.
- End with one JSON run card including hypothesis, mechanism, non-fault mimic,
  holdout/CI, registry evidence, hash, validator, name, note and verdict.
  Stop within 3 experiments or 2 hours; no slot is chosen here. The selector is
  separate and subject to the live rolling quota. Negative results are valid.
- Work autonomously where technically possible, preserve past evidence, improve
  the feed and state limitations. Perform implementation, bug audit and final
  request review; create and merge a PR to main when feasible.
