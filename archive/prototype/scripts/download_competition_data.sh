#!/usr/bin/env bash
# download_competition_data.sh — GEMSDOE competition data placement.
#
# BLOCKER: training_features.tif, labels.tif, sample_submission.tif and
# 1m_DEM_links.csv require DrivenData authentication (verified redirect to
# login at https://www.drivendata.org/competitions/306/competition-doe-gems/data/).
# They CANNOT be auto-downloaded from this sandbox (Dropbox mirrors are also
# out of network reach). Run this script on an authenticated machine, then
# place the files into data/ and run scripts/prepare_data.py.
#
# Official sources:
#   Competition data tab (login required):
#     https://www.drivendata.org/competitions/306/competition-doe-gems/data/
#   Problem description:
#     https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
#   Submission format:
#     https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/  (see also /page/983/ in GEMSDOE36 research)
#   Reference solution:
#     https://github.com/drivendataorg/gems-prize-reference-solution
#   Submission rules PDF:
#     https://docs.nlr.gov/docs/fy26osti/96647.pdf
#   OpenEI GDR #1391 (INGENIOUS catalogue):
#     https://gdr.openei.org/submissions/1391
#   USGS 3DEP 10 m DEM:
#     https://www.usgs.gov/3d-elevation-program
#   USGS QFaults:
#     https://www.usgs.gov/programs/earthquake-hazards/faults
#   US Census TIGER/Line:
#     https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
#
# Dropbox mirrors (reported in project research; network-blocked here):
#   GEMS_96647.pdf, example_submission.tif, existing_faults.tif,
#   gems-geodawn-numerical-features.tif, Digital-elevation-model-links-JSON.pdf

set -euo pipefail

DEST="${1:-data}"
mkdir -p "$DEST"

echo "================================================================"
echo "GEMSDOE competition data placement"
echo "================================================================"
echo ""
echo "This script documents where the competition data comes from. It does NOT"
echo "auto-download auth-gated files. DrivenData login is required."
echo ""
echo "Files to place in $DEST/:"
echo "  - training_features.tif   (feature stack, DrivenData data tab)"
echo "  - labels.tif              (withheld fault labels, DrivenData data tab)"
echo "  - sample_submission.tif   (submission grid: CRS/shape/transform reference)"
echo "  - 1m_DEM_links.csv        (DEM tile links, DrivenData data tab)"
echo "  - existing_faults.tif     (USGS/INGENIOUS catalogue faults, optional)"
echo ""
echo "Steps on an authenticated machine:"
echo "  1. Log in to https://www.drivendata.org/competitions/306/competition-doe-gems/data/"
echo "  2. Download training_features.tif, labels.tif, sample_submission.tif, 1m_DEM_links.csv"
echo "  3. Place them in $DEST/"
echo "  4. Run:  python scripts/prepare_data.py"
echo ""
echo "OpenEI GDR #1391 (INGENIOUS catalogue, public):"
echo "  https://gdr.openei.org/submissions/1391"
echo ""
echo "Once data are in place, the full pipeline is:"
echo "  bash scripts/download_competition_data.sh   (auth machine, place files)"
echo "  python scripts/prepare_data.py              (build feature stack)"
echo "  python scripts/generate_submission.py       (generate candidate TIF)"
echo "  python scripts/align_to_competition_grid.py --reference data/sample_submission.tif"
echo "  python scripts/submission_writer.py --reference data/sample_submission.tif"
echo "  python scripts/validate_submission.py       (gates + verdict)"
echo "================================================================"

exit 0
