#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
INDEX_DIR="${HOME}/.fluxloop/mcp/index/dev"
DATA_DIR="${PACKAGE_ROOT}/fluxloop_mcp/data/default_index"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[fluxloop-mcp] python3 executable not found" >&2
  exit 1
fi

if ! python3 -m pip show build >/dev/null 2>&1; then
  echo "[fluxloop-mcp] Python package 'build' not found. Install it with: python3 -m pip install build" >&2
  exit 1
fi

echo "[fluxloop-mcp] Rebuilding documentation index via scripts/rebuild_index.sh"
bash "${SCRIPT_DIR}/rebuild_index.sh"

if [[ ! -f "${INDEX_DIR}/chunks.jsonl" ]] || [[ ! -f "${INDEX_DIR}/manifest.json" ]]; then
  echo "[fluxloop-mcp] Expected index artifacts not found in ${INDEX_DIR}" >&2
  exit 1
fi

echo "[fluxloop-mcp] Copying index artifacts into packaged data directory"
mkdir -p "${DATA_DIR}"
cp "${INDEX_DIR}/chunks.jsonl" "${DATA_DIR}/chunks.jsonl"
cp "${INDEX_DIR}/manifest.json" "${DATA_DIR}/manifest.json"

echo "[fluxloop-mcp] Building distribution artifacts"
rm -rf "${PACKAGE_ROOT}/dist" "${PACKAGE_ROOT}/build"
python3 -m build "${PACKAGE_ROOT}"

echo "[fluxloop-mcp] Build complete. Artifacts available in ${PACKAGE_ROOT}/dist"


