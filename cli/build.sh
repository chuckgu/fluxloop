#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 executable not found" >&2
  exit 1
fi

if ! python3 -m pip show build >/dev/null 2>&1; then
  echo "Python package 'build' not found. Install it with: python3 -m pip install build" >&2
  exit 1
fi

rm -rf "${SCRIPT_DIR}/dist" "${SCRIPT_DIR}/build"

python3 -m build "${SCRIPT_DIR}"

echo "CLI package artifacts are available in ${SCRIPT_DIR}/dist"

