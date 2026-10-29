# Official sources verified line by line — 2026-10-29

Scope: what this session fetched directly from official or organizer-controlled pages, what it found,
and what it could **not** verify. Nothing here is a score. Each row links to the page for manual review.
Fetch method: the `fetch_page` tool on 2026-10-29 (sandbox has no DrivenData login; the data tab is login-walled).

## A. Competition specification (verified)

| # | Claim | Where it is stated | Verified text (abridged) | Status |
|---|---|---|---|---|
| A1 | Metric = distance-weighted Tversky, α=0.2, β=0.8, triangular kernel, R = 300 m (3 px at 100 m) | [Problem description, "Performance metric"](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric) | "For this competition, we set α=0.2 and β=0.8" · "range R is 300 meters (i.e., 3 pixels at 100m resolution)" | VERIFIED |
| A2 | Predictions are pixel-wise probabilities in [0, 1] | same page | "fault predictions represented as pixel-wise probabilities or confidence scores between 0 and 1" | VERIFIED |
| A3 | Single layer, float32, CRS EPSG:32611, 100 m, same bounds as training data | same page, "Submission format" | "same projected coordinate reference system … EPSG 32611" · "single layer with datatype of 32-bit float (float32)" | VERIFIED |
| A4 | Data outside bounds must be null or NaN | same page, "Submission format" | "data outside the bounds is null or nan" | VERIFIED. Note: the repo's validators write outside-footprint values as NaN or zeros; the **zeros-outside twin is not what the page literally describes**. Flag for review. |
| A5 | Scoring masks known USGS/INGENIOUS fault pixels | [DrivenData forum, staff post by chrisk-dd, 2026-09-16](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2) | "Pixels corresponding to known USGS/INGENIOUS faults are masked / excluded from evaluation, so they do not count towards penalty terms." | VERIFIED (staff forum post, not the rules document). Masking is pixel-exact; the post does not mask a surrounding buffer. |
| A6 | Three submissions per week; one final submission selected before the deadline | [Official Rules PDF, §3.2 and §3.4](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | "up to three per week, as specified on the competition website" · "you must select only one set of predictions to use as your final submission" | VERIFIED |
| A7 | Generative-AI use must be disclosed in the narrative | same PDF, §3.2 | "you must indicate in the narrative … the extent to which, if any, you used generative AI technology" | VERIFIED |
| A8 | Finalists must deliver complete reproducible code and documentation | same PDF, §3.5 | "Their solution's complete code assets and documentation" | VERIFIED |
| A9 | Submission must be an original work and not include third-party content unless disclosed | same PDF, Appendix A.5(1) | "The competitor's entire submission is an original work by the competitor" | VERIFIED |
| A10 | Competition close | [Competition home](https://www.drivendata.org/competitions/306/competition-doe-gems/) | "Dec. 3, 2026, 11:59 p.m. UTC" | VERIFIED (≈35 days from 2026-10-29) |
| A11 | Two prize phases: $50k private round (top 5 × $10k), then $250k re-labeled round | [Official Rules PDF §1.1](https://docs.nlr.gov/docs/fy26osti/96647.pdf) and [Competition home](https://www.drivendata.org/competitions/306/competition-doe-gems/) | As stated | VERIFIED |

## B. What the official documents do NOT contain (irregularities for review)

| # | Item | Finding |
|---|---|---|
| B1 | "Unique / no duplicate of a registry raster" rule (70% within 3 px, |Spearman| > 0.90) | **Not found** in the Problem description, the Official Rules PDF (§§1–4, Appendix A read in full chunks 0–4 of 7), or the competition home page. The rule is the repository's internal *Parallel-Run Protocol*, not an organizer requirement. It must be treated as the project's own gate, labeled as such. |
| B2 | Hidden "lattice" registry | The 70 %-overlap check is measured against a pinned third-party raster (`13GEMSDOE`). It is not an organizer artifact. |
| B3 | Method paragraph ("your lane") | The user's Parallel-Run Protocol refers to "the single method paragraph below". No such paragraph appears in the prompt. The repo records `method_lane: null` in `registry/template.json`. Flag. |
| B4 | Submission-page wording | The live submission page could not be reached (login). The user-supplied form text is consistent with the rules: a single GeoTIFF or a ZIP holding one GeoTIFF. |

## C. Leaderboard snapshot (verified, public test set only)

Source: [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) (fetched 2026-10-29; the page shows only relative timestamps and no snapshot time).

| Rank | Participant (as shown) | Best public DW-Tversky |
|---|---|---|
| #1 | xiaofanhu | **0.4544** |
| #2 | cfld__ | 0.3916 |
| #3 | Batik Shirt Brothers | 0.3911 |
| #4 | BrandenKMurray | 0.3841 |
| #5 | op01 | 0.3642 |
| #47 | kpomazi | **0.3195** |
| #50 | kinneso_outlook | 0.3167 (last row of the top-50 list) |

Irregularities:
- The prompt says "0.4413" and, elsewhere, "0.3195 is the highest score right now". The fetched board shows the top score is **0.4544**, and **0.3195 is rank #47**. Neither 0.4413 nor 0.3195 is the top score on this snapshot.
- No top-50 entry carries a name matching the nine GEMSDOE repository owners, and every user-reported GEMSDOE score (0.2449–0.2778) lies below the rank-50 cut-off (0.3167). The reported GEMSDOE numbers therefore **cannot be confirmed on the public board**. They are treated as USER-REPORTED / UNVERIFIED throughout the repository.

## D. Things this session could not verify (limitations)

- DrivenData data tab (training features, labels, sample submission) and the submission form: login required. Not reachable from this sandbox.
- The competition-hosted "private" score: not visible to anyone before close.
- Any organizer-issued receipt for the nine GEMSDOE scores: none obtained.
- Third-party data mirrors on GitHub: pinned by SHA-256 in `registry/`, but hashes do not establish organizer authenticity.

## E. Reproduction

```sh
# fetch the official pages listed above; compare the figures in sections A and C
python -m pytest -q          # see the current session card for the final test count
```

## F. Additional official-source checks and automation design — 2026-10-29

| Source | What the official page says | What was and was not obtained |
|---|---|---|
| [GDR INGENIOUS, DOI 10.15121/1881483](https://gdr.openei.org/submissions/1391) | The page marks the collection publicly accessible under CC BY 4.0, lists nine resources (116.98 MB), and explicitly describes spring/well temperature and aqueous-geochemistry analyses. | The page was fetched and its listing checked. Direct fetch of [`wellspringdata.gdb.zip`](https://gdr.openei.org/files/1391/wellspringdata.gdb.zip) returned HTTP 500. No archive, schema, analyte fields, local coverage, or derived raster was verified/downloaded. |
| [USGS Water Data API collections](https://api.waterdata.usgs.gov/ogcapi/v0/collections) and [migration guide](https://api.waterdata.usgs.gov/docs/ogcapi/migration/) | Official API documentation lists monitoring locations, time-series metadata, daily/continuous values, and field measurements (including discharge and groundwater-level measurements). | Documentation only was checked. No study-area site query, parameter coverage, time series, or spatial coverage was obtained. |
| [DrivenData reference-solution README at pinned commit](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md) | The official reference implementation supports CPU-only and GPU execution; GPU is optional acceleration. | Repository README was inspected; no competition data or score was obtained. A GPU is not an established prerequisite for data restoration or basic validation. |
| [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) | Redirects to login in this environment. | No authenticated organizer data or submission receipt was fetched. |

The public feed implementation is `scripts/refresh_official_leaderboard.py`,
`docs/data/official-leaderboard.json`, and `.github/workflows/official-leaderboard.yml`.
It is designed to fetch only the public leaderboard once per day, parse a rank +
public-Tversky table, and atomically replace the snapshot only after validation.
A parser/layout/network failure must leave the previous snapshot untouched; a
successful workflow run is still required to verify the live HTML parser. The
checked-in snapshot was captured through the page-fetch tool on 2026-10-29 and
contains selected ranks only; its exact capture time is not exposed.

Local preflight is separate from the official-source checks: it reported no
assigned lane, no canonical assignment, two vendored SHA mismatches
(`submission_writer.py` and `uniqueness.py`), and missing organizer-input/cache
files. The owner mirror `--verify-only` check is blocked on missing
`training_features.tif`. No official or third-party data were restored in this
session. The legacy preparation runner was tested with temporary paths before
being changed to exit without writing; this is a software regression check, not
an input download.
