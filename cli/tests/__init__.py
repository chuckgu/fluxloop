import sys
from pathlib import Path

# Ensure the local SDK package is importable during tests (fluxloop.schemas etc.)
_CURRENT_DIR = Path(__file__).resolve()
_PACKAGES_ROOT = _CURRENT_DIR.parents[2]  # .../packages
_SDK_PATH = _PACKAGES_ROOT / "sdk"

if _SDK_PATH.exists():
    sys.path.insert(0, str(_SDK_PATH))

