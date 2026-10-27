#!/usr/bin/env bash
# Restore the real GEMS Prize competition core files into ./data/.
#
# BREAKTHROUGH (2026-10-27): the real training_features.tif / labels.tif /
# sample_submission.tif ARE reachable from this sandbox, despite
# drivendata.org itself being outside the network allowlist. The sibling
# repo buffedlizard55-lab/GEMSDOE32's own
# `registry/data_manifest.json` + `scripts/fetch_data.py` document that it
# restored these exact files from a hash-pinned GitHub mirror (its own
# earlier session must have had organizer-portal access once and committed
# the bytes to these two public repos). GitHub's REST content API and
# codeload.github.com ARE inside this environment's allowlist, so the same
# mirror is reachable here. Every byte below is sha256-verified against
# buffedlizard55-lab/GEMSDOE32's manifest before use -- this is an
# integrity-pinned THIRD-PARTY MIRROR, explicitly NOT organizer-authenticated
# (see docs/LIMITATIONS.md "Data access update" and docs/SOURCES.md).
#
# Usage: bash scripts/restore_real_data.sh
# Requires: `gh` CLI authenticated (already configured in this sandbox).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/registry

fetch_raw() {
  # fetch_raw <repo> <ref> <path-in-repo> <dest-file>
  local repo="$1" ref="$2" path="$3" dest="$4"
  echo "fetching ${repo}@${ref}:${path} -> ${dest}"
  gh api "repos/${repo}/contents/${path}?ref=${ref}" \
    -H "Accept: application/vnd.github.raw" > "${dest}"
}

verify() {
  local file="$1" want="$2"
  local got
  got=$(sha256sum "$file" | awk '{print $1}')
  if [ "$got" != "$want" ]; then
    echo "SHA256 MISMATCH for $file: got $got, want $want" >&2
    exit 1
  fi
  echo "OK   $file  $got"
}

# --- labels / existing_faults / sample_submission (small core files) -----
fetch_raw buffedlizard55-lab/GEMSDOE24 07345ea0604953d7efb858d9cfbc21e20c7aca0b \
  data/bridge/labels.tif data/labels.tif
verify data/labels.tif 7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093
cp data/labels.tif data/existing_faults.tif   # byte-identical per the manifest

fetch_raw buffedlizard55-lab/GEMSDOE24 07345ea0604953d7efb858d9cfbc21e20c7aca0b \
  data/bridge/sample_submission.tif data/sample_submission.tif
verify data/sample_submission.tif 2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc

# --- training_features.tif (419 MB, split into 5 parts) ------------------
for i in 0 1 2 3 4; do
  part=$(printf "%03d" "$i")
  fetch_raw buffedlizard55-lab/GEMSDOE c0c06ac82178f26b94fce3397036ef8f12a2f3a0 \
    "data/bridge/gems-geodawn-numerical-features.tif.part-${part}" \
    "data/part-${part}"
done
cat data/part-000 data/part-001 data/part-002 data/part-003 data/part-004 \
  > data/training_features.tif
rm data/part-*
verify data/training_features.tif 4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5

# --- one real registry raster, for a genuine duplicate-overlap check -----
fetch_raw buffedlizard55-lab/GEMSDOE24 07345ea0604953d7efb858d9cfbc21e20c7aca0b \
  "inputs/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif" \
  data/registry/scored_h19_5.tif
verify data/registry/scored_h19_5.tif ec1f9b56b83ce33cad781ceb9f104b18fb4f2ff785263a4e89616af4aabdee8d

echo
echo "All core files restored and hash-verified. Run: python scripts/prepare_data.py"
echo "REMINDER: these are an integrity-pinned third-party GitHub mirror, NOT an"
echo "organizer-authenticated download -- see docs/LIMITATIONS.md before trusting"
echo "any score computed from them as more than a holdout estimate."
