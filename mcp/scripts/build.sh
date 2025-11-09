#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 executable not found" >&2
  exit 1
fi

if ! python3 -m pip show build >/dev/null 2>&1; then
  echo "Python package 'build' not found. Install it with: python3 -m pip install build" >&2
  exit 1
fi

rm -rf "${PACKAGE_ROOT}/dist" "${PACKAGE_ROOT}/build"

python3 -m build "${PACKAGE_ROOT}"

echo "MCP package artifacts are available in ${PACKAGE_ROOT}/dist"


