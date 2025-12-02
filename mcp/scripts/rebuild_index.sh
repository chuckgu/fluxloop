#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

OUTPUT_DIR="${HOME}/.fluxloop/mcp/index/dev"

echo "[fluxloop-mcp] Rebuilding index into ${OUTPUT_DIR} (base: ${REPO_ROOT})"

pushd "${REPO_ROOT}" >/dev/null
python -m fluxloop_mcp.index.ingestor --output "${OUTPUT_DIR}"
python -m fluxloop_mcp.index.validator || true
popd >/dev/null

DATE_STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > "${OUTPUT_DIR}/manifest.json" <<EOF
{
  "version": "${DATE_STAMP}",
  "description": "Generated via scripts/rebuild_index.sh",
  "generated_at": "${DATE_STAMP}",
  "sources": [
    "docs/**/*.md",
    "packages/website/docs-cli/**/*.md",
    "packages/website/docs-sdk/**/*.md",
    "packages/sdk/**/*.md",
    "samples/**/*.md"
  ]
}
EOF

echo "[fluxloop-mcp] index OK at ${OUTPUT_DIR}"

