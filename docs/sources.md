# Sources and data — reviewed 28 October 2026

**DO NOT SUBMIT:** the current candidates failed the literal registry gate.
Official pages support the descriptions below; they are not organizer receipts
for any candidate. Owner mirrors are integrity-pinned, not authenticated.

| Source | Checked claim | Limitation |
|---|---|---|
| [DrivenData problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | 100 m grid, EPSG:32611, float32 confidence [0,1], pooled distance-weighted Tversky with α=.2, β=.8 and 300 m triangular kernel. | Data/submission tabs require login; portal acceptance not tested. |
| [Staff: known-fault masking](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) | Known-fault pixels are excluded; nearby new faults can still matter. | There is no blanket 300 m exclusion. |
| [Staff: submission limit](https://community.drivendata.org/t/submission-amount-question/11553) and [rolling reset](https://community.drivendata.org/t/weekly-submissions/11524) | The platform's displayed limit prevails; allowance uses a rolling window. | Account-specific remaining slots are unknown. |
| [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | Public #1 `xiaofanhu` was 0.4544 on 2026-10-28. | This is a dated public-board snapshot, not a file-linked receipt or a live feed. |
| [DOE/NLR official rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | Eligibility and prize conditions. | Recheck the latest rules and account status. |
| [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) | Airborne magnetic/radiometric grids are advertised, DOI 10.5066/P93LGLVQ, CC0. | Official-host bytes and local derivatives were not fetched or authenticated here. |
| [GDR INGENIOUS](https://gdr.openei.org/submissions/1391) | Public compilation includes 2 m probes and fault-related data; DOI 10.15121/1881483, CC BY 4.0. | Official download and local coverage not checked; attribution required. |
| [USGS 3DEP](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services) | Elevation products are publicly available. | Tiles and study-area coverage not downloaded/checked. |
| [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) | Organizer's starter U-Net notebook. | Does not certify local predictions or supply hidden labels. |

The shell can restore GitHub-hosted owner mirrors: selected sample, label,
feature and historical raster bytes were verified against the
[manifest](../registry/karage1_data_manifest.json). GitHub hashes establish
mirror identity, **not** organizer provenance. The official external-data
hosts are outside the shell allowlist; official web descriptions were reviewed
through page retrieval. A [prior receipt](data/restore_receipt_summary.json)
is dated 2026-10-27, not a claim that all listed files were fetched today.
See the [full research slate](../knowledge/research-review.md) and
[current run card](data/run-card.json).
