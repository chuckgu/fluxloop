"""Utilities for ensuring a local MCP index is available."""

from __future__ import annotations

import json
import logging
import shutil
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_INDEX_PACKAGE = "fluxloop_mcp.data.default_index"
DEFAULT_OUTPUT_DIR = Path.home() / ".fluxloop" / "mcp" / "index" / "dev"
MANIFEST_FILENAME = "manifest.json"
CHUNK_FILENAME = "chunks.jsonl"


def ensure_index(target_dir: Optional[Path] = None, *, force: bool = False) -> Path:
    """Ensure that a usable MCP index exists on the local machine."""

    output_dir = Path(target_dir) if target_dir else DEFAULT_OUTPUT_DIR

    try:
        packaged_manifest = _load_packaged_manifest()
    except FileNotFoundError:
        logger.debug("No packaged manifest found; skipping index bootstrap.")
        return output_dir

    if not force and _index_matches(output_dir, packaged_manifest):
        return output_dir

    logger.info("Installing bundled MCP index into %s", output_dir)
    _write_packaged_index(output_dir, packaged_manifest)
    return output_dir


def _index_matches(output_dir: Path, packaged_manifest: Dict[str, Any]) -> bool:
    manifest_path = output_dir / MANIFEST_FILENAME
    chunk_path = output_dir / CHUNK_FILENAME
    if not manifest_path.exists() or not chunk_path.exists():
        return False

    try:
        current_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    return current_manifest.get("version") == packaged_manifest.get("version")


def _write_packaged_index(output_dir: Path, packaged_manifest: Dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    _copy_resource(CHUNK_FILENAME, output_dir / CHUNK_FILENAME)
    manifest_path = output_dir / MANIFEST_FILENAME
    manifest_path.write_text(json.dumps(packaged_manifest, indent=2) + "\n", encoding="utf-8")


def _copy_resource(resource_name: str, destination: Path) -> None:
    resource = resources.files(DEFAULT_INDEX_PACKAGE) / resource_name
    with resources.as_file(resource) as source_path:
        shutil.copy2(source_path, destination)


def _load_packaged_manifest() -> Dict[str, Any]:
    resource = resources.files(DEFAULT_INDEX_PACKAGE) / MANIFEST_FILENAME
    return json.loads(resource.read_text(encoding="utf-8"))


