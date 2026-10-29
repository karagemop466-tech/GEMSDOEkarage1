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
python -m pytest -q          # 362 tests expected after this session's additions
```

## F. Re-verification added by session arena/fb1e3550 (29 Oct 2026)

Fetched again with the `fetch_page` tool the same day. Quotations are from the fetched text.

| # | Claim | Source (open to check) | Quoted text (abridged) | Status |
|---|---|---|---|---|
| F1 | Provided layers include dilatation rate, shear strain rate, second invariant of the strain-rate tensor, isostatic gravity and its slope, RTP / TMI / TMI slopes / top-of-crust magnetic source depth, conductivity, detrended elevation, density of earthquakes, and radiometric counts | [Problem description, Provided features](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | "Dilatation rate, shear strain rate, and the second invariant of the strain rate tensor" · "Magnetics including reduced-to-pole magnetic anomaly, total magnetic intensity, the vertical and horizontal slope of total magnetic intensity, and the top-of-crustal magnetic source depth estimate" | VERIFIED. Supports the bands used by H-K1-STRAINPHASE and H-K1-SIGNEDOFFSET. |
| F2 | Initial Round scores each submission against a private set labelled before the competition; expert review applies to the Final Round | same page, "Competition structure" | "each submission scored against a private set of new faults labeled by experts before the competition" · "Expert review: panel cross-references submitted faults for candidate new faults" | VERIFIED. The prompt's claim that a human must inspect submissions before scoring is **not** supported for the Initial Round. Flagged. |
| F3 | Public #1 is 0.4544 (xiaofanhu); the first page does not show 0.3195 | [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | "#1 … xiaofanhu … 0.4544" | VERIFIED (first chunk; rank 47 not re-read this session). |
| F4 | External data allowed if the participant holds a licence permitting use and sharing | same page, "External datasets" | "Participants are allowed to use any additional data sources, provided that the participants possess a license that permits the data to be used" | VERIFIED. All restored files are third-party mirrors; licence review is still required before use in a submission. |
