#!/usr/bin/env bash
# Autonomous SHA-256-verified acquisition & restoration of DOE GEMS competition + GeoDAWN/INGENIOUS external data.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_BIN="${REPO_ROOT}/.venv/bin/python"
if [[ ! -x "${PY_BIN}" ]]; then
  PY_BIN="python3"
fi

exec "${PY_BIN}" "${REPO_ROOT}/scripts/restore_karage1_data.py" "$@"
