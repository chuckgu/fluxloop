#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

OUTPUT_DIR="${HOME}/.fluxloop/mcp/index/dev"

echo "[fluxloop-mcp] Rebuilding index into ${OUTPUT_DIR}"

python -m fluxloop_mcp.index.ingestor --output "${OUTPUT_DIR}"
python -m fluxloop_mcp.index.validator || true

