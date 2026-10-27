# Limitations of this environment — read before trusting any number here

Verified live on 2026-10-27 by direct tool calls (not assumed). Re-run the
same checks yourself any time; the commands are given so this is auditable,
not a claim you have to take on faith.

## 1. Network access actually available in this sandbox

| Host | Reachable from `bash`/`curl` in this sandbox? | Reachable from the `fetch_page` tool? | Evidence |
|---|---|---|---|
| `github.com`, `codeload.github.com`, `api.github.com` | **Yes** | Yes | `git clone` of `drivendataorg/gems-prize-reference-solution` succeeded |
| `pypi.org`, `files.pythonhosted.org` | **Yes** | n/a | `pip install numpy scipy rasterio` succeeded |
| `www.drivendata.org` | **No** (`curl` → exit 35, TLS blocked) | **Yes** (text only) | Leaderboard, problem description, and data-tab pages were readable via `fetch_page`; `curl -sI https://www.drivendata.org` from bash timed out/blocked |
| `www.dropbox.com` / `*.dropboxusercontent.com` | **No** | Partially — resolves the direct-download redirect URL, but returns **no binary content** (the tool extracts page text, not raw bytes) | `curl -sI` blocked from bash; `fetch_page` returned an empty body for the `.tif` redirect target |
| `gdr.openei.org`, `www.sciencebase.gov`, `doi.org` | **No** | Yes (text only) | Same pattern as above |

**Net effect: this project cannot itself download any binary GeoTIFF, shapefile,
or ZIP file from the competition or from USGS/OpenEI/INGENIOUS.** We can read
*web page text* describing those files (titles, summaries, byte sizes, DOIs,
licenses) through `fetch_page`, which is how every citation in
`docs/SOURCES.md` and `research/hypotheses.md` was verified — but we cannot
pull the pixels. There is no way around this from inside the current sandbox
network allowlist; it must be done on a machine with normal internet access
(see `scripts/download_competition_data.sh`).

## 2. No DrivenData account is configured

`https://www.drivendata.org/competitions/306/competition-doe-gems/data/`
redirects unauthenticated requests to `/accounts/login/` (verified live).
We have not been given, and do not request, any DrivenData username,
password, or API token. Consequently:

- We have never opened the organizer's real `training_features.tif`,
  `labels.tif`, or `sample_submission.tif`.
- The exact grid in `src/gems/grid.py` (shape `3730×3292`, transform
  `(100, 0, 243350, 0, -100, 4508550)`, EPSG:32611) is **cross-replicated**
  from JSON receipts published by multiple independent third-party research
  logs (the "GEMSDOE" sibling sites), each of which claims to have read it
  from its own locally cached copy of `sample_submission.tif`. It is
  internally consistent across more than five unaffiliated sources and is
  geographically plausible for the GeoDAWN survey area, but it is **not
  organizer-confirmed** by us. `scripts/prepare_data.py` is the one-line
  check that promotes it to confirmed the moment real data is available.
- We cannot compute a single genuine `HOLDOUT-DTI` number, because that
  requires the real labeled fault raster. Anything in this repo that looks
  like a score is either (a) copied with an explicit `OWNER-REPORT` /
  `USER-REPORTED` / `UNVERIFIED` label from a third-party site, (b) an
  analytic identity (e.g. "an all-zero raster scores exactly 0"), or (c) a
  result on a clearly-marked **synthetic** toy dataset
  (`scripts/demo_synthetic_pipeline.py`) that exists only to prove the code
  is wired correctly, never to claim a research result.

## 3. The real, verifiable leaderboard

The public leaderboard **is** reachable (no login required) and was read
live on 2026-10-27:
<https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>

Top of the **real, organizer-run** public leaderboard at that time:

| Rank | Participant | Public DW-Tversky |
|---|---|---|
| 1 | xiaofanhu | **0.4544** |
| 2 | cfld__ | 0.3916 |
| 3 | Batik Shirt Brothers | 0.3911 |
| 4 | BrandenKMurray | 0.3724 |
| 5 | No Fault of Our Own | 0.3566 |

This contradicts two different "current high score" figures given in the
originating project brief (0.4413 and, separately, 0.3195) — **neither
matches the live leaderboard we fetched**. This is flagged as an
**irregularity** in `docs/SOURCES.md`; we report the number we could
ourselves verify (0.4544, live-fetched) rather than either unverified
figure from the brief.

## 4. The "GEMSDOE" sibling sites are not the competition leaderboard

Every one of the nine sites this task asked us to focus on
(GEMSDOE24/25/27/28/30/31/32/33/36) **explicitly states on its own page**
that its best historical number (0.2449–0.2778) is an **owner-reported /
user-reported claim with no linked organizer submission-page receipt**, and
as of 2026-10-27 every one of them has independently reached a **"DO NOT
SUBMIT"** state for all newer candidates, because their shared sparse
"binary-dot" placement strategy collides at >70% pixel-overlap with other
sites' rasters under their own duplicate-detection rule. See
`research/sibling_site_audit.md` for the full, cited breakdown. **None of
these numbers should be treated as ground truth about what scores well on
the real DrivenData leaderboard** (whose real top scores, 0.33–0.45, are
50–100% higher and were almost certainly produced by dense, continuous
probability models like the official U-Net reference solution, not sparse
dot placement).

## 5. What this repo starts from

This specific checkout (`GEMSDOEkarage1`) contained a single-line `README.md`
and no other files before this session. References in the task prompt to
"previous sessions," existing scripts, or prior downloads describe a
*different* simulated multi-agent exercise (the sibling GEMSDOE sites above),
not prior work in this repository. Flagging this explicitly so nobody
assumes capabilities or artifacts exist here that do not.
