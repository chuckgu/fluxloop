"""Shared constants for the FluxLoop CLI."""

from pathlib import Path


DEFAULT_CONFIG_FILENAME = "setting.yaml"
LEGACY_CONFIG_FILENAMES = ("fluxloop.yaml",)


DEFAULT_CONFIG_PATH = Path(DEFAULT_CONFIG_FILENAME)


def locate_config_file(requested: Path) -> Path:
    """Return the path to use, falling back to legacy filenames when present."""
    if requested.exists():
        return requested

    if requested.name == DEFAULT_CONFIG_FILENAME:
        for legacy in LEGACY_CONFIG_FILENAMES:
            candidate = requested.with_name(legacy)
            if candidate.exists():
                return candidate

    return requested

