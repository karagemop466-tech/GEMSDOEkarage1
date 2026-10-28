#!/usr/bin/env bash
# Restore SHA-256-pinned third-party mirrors; hashes do not authenticate organizer
# origin or establish licensing. This does not download directly from DrivenData.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_BIN="${REPO_ROOT}/.venv/bin/python"
if [[ ! -x "${PY_BIN}" ]]; then
  PY_BIN="python3"
fi

exec "${PY_BIN}" "${REPO_ROOT}/scripts/restore_karage1_data.py" "$@"
