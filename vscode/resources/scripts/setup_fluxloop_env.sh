#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: setup_fluxloop_env.sh [OPTIONS]

Options:
  --python PATH              Python executable to use (default: python3)
  --target-source-root PATH  Optional value for fluxloop.targetSourceRoot
  --skip-doctor              Do not run fluxloop doctor after setup
  -h, --help                 Show this help message

This script configures a virtual environment for FluxLoop projects.
EOF
}

PYTHON_CMD=${PYTHON:-python3}
TARGET_SOURCE_ROOT=""
RUN_DOCTOR=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --python)
      PYTHON_CMD=$2; shift 2;;
    --python=*)
      PYTHON_CMD=${1#*=}; shift;;
    --target-source-root)
      TARGET_SOURCE_ROOT=$2; shift 2;;
    --target-source-root=*)
      TARGET_SOURCE_ROOT=${1#*=}; shift;;
    --skip-doctor)
      RUN_DOCTOR=false; shift;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1;;
  esac
done

ROOT_DIR="$(pwd)"
VENV_DIR="$ROOT_DIR/.venv"

echo "➤ Using Python: ${PYTHON_CMD}"
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  echo "✗ Python executable '${PYTHON_CMD}' not found." >&2
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "➤ Creating virtual environment at $VENV_DIR"
  "$PYTHON_CMD" -m venv "$VENV_DIR"
else
  echo "➤ Virtual environment already exists at $VENV_DIR"
fi

echo "➤ Installing FluxLoop packages"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install fluxloop-cli fluxloop fluxloop-mcp

if [[ -n "$TARGET_SOURCE_ROOT" ]]; then
  WORKSPACE_SETTINGS_DIR="$ROOT_DIR/.vscode"
  WORKSPACE_SETTINGS_FILE="$WORKSPACE_SETTINGS_DIR/settings.json"
  echo "➤ Writing VS Code workspace settings ($WORKSPACE_SETTINGS_FILE)"
  mkdir -p "$WORKSPACE_SETTINGS_DIR"
  cat >"$WORKSPACE_SETTINGS_FILE" <<JSON
{
  "fluxloop.targetSourceRoot": "${TARGET_SOURCE_ROOT}",
  "fluxloop.executionMode": "workspace"
}
JSON
else
  echo "➤ Skipping VS Code settings (no --target-source-root provided)"
fi

if $RUN_DOCTOR; then
  echo "➤ Running fluxloop doctor"
  "$VENV_DIR/bin/fluxloop" doctor || true
else
  echo "➤ Skipping doctor run (--skip-doctor)"
fi

deactivate

cat <<'EOF'

Setup complete! Next steps:
  1. Open this folder in VS Code (or reload window).
  2. Run "FluxLoop: Select Environment" if prompted.
  3. Use "FluxLoop: Show Environment Info" or "FluxLoop: Run Doctor" to confirm the environment.

EOF


