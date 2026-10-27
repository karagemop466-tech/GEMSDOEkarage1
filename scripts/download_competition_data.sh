#!/usr/bin/env bash
# Download the official GEMS Prize Challenge competition data into ./data/.
#
# THIS SCRIPT CANNOT RUN INSIDE THIS SANDBOX. The sandbox's outbound network
# allowlist is limited to: github.com, codeload.github.com, api.github.com,
# registry.npmjs.org, pypi.org, files.pythonhosted.org. None of the required
# hosts below are reachable from here. Run this script yourself on a machine
# with normal internet access (see docs/LIMITATIONS.md for the full
# explanation and a line-by-line verification of what was/was not reachable).
#
# Two official distribution channels exist for the same files:
#
#   A) DrivenData data tab (requires a free DrivenData account + competition
#      enrollment -- "Compete!" button):
#      https://www.drivendata.org/competitions/306/competition-doe-gems/data/
#      Files: training_features.tif, labels.tif, sample_submission.tif,
#             1m_DEM_links.csv
#
#   B) Public Dropbox mirror (as supplied in the project brief,
#      docs/PROJECT_BRIEF.md) -- we could not independently confirm these
#      Dropbox links are owned/maintained by DrivenData/NLR; verify the
#      PDF's letterhead and content against the official rules before
#      trusting it as your data source:
#      - GEMS_96647.pdf (submission/program description PDF)
#      - example_submission.tif  (same role as sample_submission.tif)
#      - existing_faults.tif     (same role as labels.tif)
#      - gems-geodawn-numerical-features.tif (same role as training_features.tif)
#      - Digital-elevation-model-links-JSON.pdf (1 m DEM link list)
#
# Prefer channel (A); it is the competition's own authenticated source of
# truth. Use channel (B) only as a fallback and re-verify file hashes/shape
# against the grid asserted in src/gems/grid.py before trusting it.

set -euo pipefail
mkdir -p data

cat <<'EOF'
=====================================================================
MANUAL STEP REQUIRED (no credentials are stored or requested by this
project -- do this yourself in a browser):

1. Create/sign in to a DrivenData account and click "Compete!" on
   https://www.drivendata.org/competitions/306/competition-doe-gems/
2. Open the data tab:
   https://www.drivendata.org/competitions/306/competition-doe-gems/data/
3. Download these 4 files into ./data/ :
     - training_features.tif
     - labels.tif
     - sample_submission.tif
     - 1m_DEM_links.csv
4. Re-run: python scripts/prepare_data.py
   It will assert each file's CRS/shape/transform against
   src/gems/grid.py::GEMS_GRID and FAIL LOUDLY (not silently) if your
   downloaded sample_submission.tif does not match -- in that case,
   GEMS_GRID must be corrected to match the real file; the real file is
   always the ground truth, never this repo's cached constant.
=====================================================================
EOF
