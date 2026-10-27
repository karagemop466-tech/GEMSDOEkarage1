#!/usr/bin/env bash
# Placeholder for data placement blocker documented in docs/index.html
# The competition data requires DrivenData login and cannot be auto-downloaded from open internet.
# Steps for unrestricted machine:
# 1. Login at https://www.drivendata.org/competitions/306/competition-doe-gems/data/
# 2. Download training_features.tif, labels.tif, sample_submission.tif, 1m_DEM_links.csv into data/
# 3. Run python scripts/prepare_data.py to build cached feature stack
# Official mirror (requires login redirect check documented as 302 to login):
# https://gdr.openei.org/submissions/1391 (free GDR regional compilation, verified accessible)
set -e
echo "This script is a placeholder — data placement must be done manually on unrestricted machine (see README & docs/index.html Limitations)."
echo "Checked: DrivenData data tab redirects to login (verified 302), cannot auto-download without auth."
mkdir -p data
ls -lh data || echo "data/ is empty — expected blocker"
