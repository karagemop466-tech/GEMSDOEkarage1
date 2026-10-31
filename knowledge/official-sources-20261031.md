# Official source register — verified line by line where the sandbox allows (31 Oct 2026)

Each row gives: the source, what this session could check, and the manual-review link. **The sandbox allows outbound access only to github.com, api.github.com, codeload.github.com, registry.npmjs.org, pypi.org and files.pythonhosted.org.** Every other official host returned no response (curl HTTP 000) during this session, so those rows are **NOT VERIFIED HERE**. They remain listed for manual review by the owner.

| # | Source | Used for | Checked this session | Result | Manual-review link |
|---|---|---|---|---|---|
| S1 | DrivenData competition page (problem, metric, data, format) | Target, metric definition, data access | curl to drivendata.org (4 paths) | **Not reachable (HTTP 000)** | https://www.drivendata.org/competitions/306/competition-doe-gems/ |
| S2 | DrivenData leaderboard | #1 and #48 scores | curl | **Not reachable.** Values come from the 30 Oct snapshot `registry/leaderboard_snapshot_20261030.json` (ORGANIZER-PUBLIC, from an earlier session's fetch) | https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ |
| S3 | DrivenData forum post on masking known USGS/INGENIOUS faults (chrisk-dd, 16 Sep 2026) | Pixel-exact masking of known faults; no buffer | curl | **Not reachable.** Row A5 in `knowledge/official-sources-verified-2026-10-29.md` (VERIFIED on 29 Oct, by an earlier session) is the only record | https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2 |
| S4 | DOE / NLR submission-rules PDF | Submission limits, eligibility | curl | **Not reachable** | https://docs.nlr.gov/docs/fy26osti/96647.pdf |
| S5 | USGS GeoDAWN magnetic/radiometric data | Raw source of feature bands | curl | **Not reachable.** Local mirror in `data/` is hash-consistent but not organizer-authenticated | https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and |
| S6 | USGS 3DEP elevation | H-D1 data source | curl | **Not reachable** | https://www.usgs.gov/3d-elevation-program |
| S7 | GDR / OpenEI INGENIOUS submission 1391 | Thermal and geology compilation | curl | **Not reachable** | https://gdr.openei.org/submissions/1391 |
| S8 | EPSG:32611 (WGS 84 / UTM 11N) | CRS definition used by every raster | curl | **Not reachable.** The CRS string is taken from the restored rasters (`EPSG:32611`) | https://epsg.io/32611 |
| S9 | Tversky index (Wikipedia) | Background for the DTI form | curl | **Not reachable.** The DTI form is taken from the vendored `metric.py`, not from this page | https://en.wikipedia.org/wiki/Tversky_index |
| S10 | DrivenData reference solution, GitHub repo `drivendataorg/gems-prize-reference-solution` | Reference notebook behaviour, output CRS and transform | git clone (depth 1); GitHub API reachable | **VERIFIED.** HEAD `aebe92f7c8a990f0e3443451b7a825d9afd6336b` (commit date 16 Jun 2026, Chris Kucharczyk). Notebook cell 16: `alpha = 0.2`, `beta = 0.8`, a `TverskyLoss`, and `F.sigmoid(outputs)`. Cell 2: `FEATURE_DATA_PATH = Path("data/numeric_features.tif")`, `FAULT_LABELS_PATH = Path("data/labels.tif")`. Cell 19: writes the prediction with the labels CRS and transform. The notebook has **no scoring function** | https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb |
| S11 | Vendored metric (`vendor/gems57/metric.py`, sha pinned in `vendor/PROVENANCE.json`) | DTI definition: alpha 0.2, beta 0.8, 3 px kernel | local hash check this session | **MATCHES provenance pin.** It is a transcription of the organizer definition, so it is secondary to S1 | `vendor/gems57/metric.py` |
| S12 | PyPI `rasterio` package page | Library version only | curl | Reachable (HTTP 200); not used for any claim | https://pypi.org/project/rasterio/ |

## Irregularities to review

1. **Feature-file name.** The reference notebook reads `data/numeric_features.tif`, while the mirror in this repo is `data/training_features.tif`. The mirror's file is not organizer-authenticated, so the name difference cannot be resolved here. Owner check against the organizer's data listing (S1) is needed.
2. **Leaderboard snapshot age.** Scores are from 30 Oct 2026. Earlier standing notes (`docs/standing-prompt.md`) give #1 0.4413 and #2 0.3195; the snapshot gives #1 0.4544 and rank 48 = 0.3195. The snapshot is the one used here. The standing note is flagged as conflicting.
3. **USER-REPORTED focus scores** (for example GEMSDOE32 0.2778) have no organizer receipt in this repository. They are not verified.
4. **Metric labels.** The 3 px kernel and the alpha/beta values are consistent between S10 (alpha/beta) and S11 (metric). The DrivenData page (S1) that would be the primary source for the kernel could not be checked.

## Verification status summary

- Verified in this session: S10 (reference repo, commit pinned), S11 (provenance pin matches).
- Carried forward from 29 Oct, not re-verified: S3 (forum masking rule, row A5).
- Not reachable from the sandbox: S1, S2, S4, S5, S6, S7, S8, S9. Each has a manual-review link above.
