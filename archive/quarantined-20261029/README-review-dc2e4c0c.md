# Quarantined research raster: K/Th + thermal candidate

**Status: NEGATIVE / DO NOT SUBMIT.** This historical raster is retained for audit and learning only. It is not an approved download and is intentionally absent from `docs/downloads/`.

- GeoTIFF SHA-256: `a18e8fea158c2c53357b2d9651a6ce874b6329f1fdff690b4e17e8b0bb6a75eb`
- ZIP SHA-256: `30946e3c3d894ac81312d1c350099a21d0e28cbb4fa4ec8650a54e1db056a2c6`
- Historical local format sidecar reports one band, float32, EPSG:32611, the expected mirrored dimensions/transform, and finite values in `[0,1]`. That is a local format assertion only; it does not establish organizer authenticity, portal acceptance, scientific validation, or uniqueness.
- Its old report used a `promote` verdict and quoted a purported holdout result. That verdict and number are **superseded and unverified**: the original candidate has no current qualifying run card, no reproduced spatial hide-and-recover evaluation with confidence interval, and no complete registry comparison available in this checkout. Do not cite the old value as HOLDOUT-DTI or leaderboard performance.
- The merged mainline retraction receipt `evidence/unique_hyp_kth_therm_mask_retraction_20261029.json` records a pinned-mirror saved-byte audit: 99.9017% directed 3-pixel overlap with the lattice, exceeding the literal duplicate threshold. Nine-site overlap is below the threshold, but that does not clear a lattice duplicate. The mirror is not organizer-authenticated.

The file was moved out of the public submission-download directory after review found the README/legacy executive page gave a false green-light to this old candidate. The active project pages must be rebuilt with `python scripts/build_site.py`; they must remain negative until all gates pass. See `docs/data/unique-hyp-kth-therm-mask-20261028-zeros.json` for the machine-readable supersession record.
