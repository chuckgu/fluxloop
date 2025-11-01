"""Configuration section definitions and merge strategy for FluxLoop CLI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

from .constants import (
    CONFIG_DIRECTORY_NAME,
    CONFIG_SECTION_FILENAMES,
    CONFIG_SECTION_ORDER,
    DEFAULT_CONFIG_FILENAME,
    LEGACY_CONFIG_FILENAMES,
)


@dataclass(frozen=True)
class ConfigSection:
    """Represents an individual configuration section file."""

    key: str
    filename: str
    description: str
    required: bool = False

    def resolve_path(self, root: Path) -> Path:
        """Return the canonical path to this section within a project root."""

        return root / CONFIG_DIRECTORY_NAME / self.filename


CONFIG_SECTIONS: Tuple[ConfigSection, ...] = (
    ConfigSection(
        key="project",
        filename=CONFIG_SECTION_FILENAMES["project"],
        description="Project metadata, collector configuration, and shared defaults.",
        required=True,
    ),
    ConfigSection(
        key="input",
        filename=CONFIG_SECTION_FILENAMES["input"],
        description="Personas, base inputs, and input generation settings.",
    ),
    ConfigSection(
        key="simulation",
        filename=CONFIG_SECTION_FILENAMES["simulation"],
        description="Experiment execution parameters (runner, iterations, environments).",
        required=True,
    ),
    ConfigSection(
        key="evaluation",
        filename=CONFIG_SECTION_FILENAMES["evaluation"],
        description="Post-run evaluation pipelines and scoring strategies.",
    ),
)

CONFIG_SECTION_BY_KEY: Dict[str, ConfigSection] = {
    section.key: section for section in CONFIG_SECTIONS
}

CONFIG_REQUIRED_KEYS: Tuple[str, ...] = tuple(
    section.key for section in CONFIG_SECTIONS if section.required
)


def iter_section_paths(root: Path) -> Iterable[Path]:
    """Yield section paths in merge order for the given project root."""

    for key in CONFIG_SECTION_ORDER:
        section = CONFIG_SECTION_BY_KEY[key]
        yield section.resolve_path(root)


def is_legacy_config(filename: str) -> bool:
    """Return True if filename refers to a legacy single-file configuration."""

    return filename in (DEFAULT_CONFIG_FILENAME, *LEGACY_CONFIG_FILENAMES)


MERGE_PRIORITY: Tuple[str, ...] = CONFIG_SECTION_ORDER
"""Order in which configuration sections should be merged."""

