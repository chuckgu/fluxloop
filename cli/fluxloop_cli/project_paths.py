"""Utilities for resolving FluxLoop project directories."""

from pathlib import Path
from typing import Optional

from .constants import DEFAULT_CONFIG_FILENAME, DEFAULT_CONFIG_PATH, DEFAULT_ROOT_DIR_NAME


def _normalize_path(path: Path) -> Path:
    return path.expanduser().resolve()


def resolve_root_dir(root: Optional[Path]) -> Path:
    """Resolve the FluxLoop root directory."""
    base = root if root is not None else Path(DEFAULT_ROOT_DIR_NAME)
    if base.is_absolute():
        return _normalize_path(base)
    return _normalize_path(Path.cwd() / base)


def resolve_project_dir(project: str, root: Optional[Path]) -> Path:
    """Resolve the directory for a specific project.

    If project is None, fall back to current working directory.
    """

    root_dir = resolve_root_dir(root)
    return _normalize_path(root_dir / project)


def resolve_project_relative(path: Path, project: Optional[str], root: Optional[Path]) -> Path:
    """Resolve a path relative to the project directory (if provided)."""

    if path.is_absolute():
        return _normalize_path(path)

    if project:
        return _normalize_path(resolve_project_dir(project, root) / path)

    return _normalize_path(Path.cwd() / path)


def resolve_config_path(config_file: Path, project: Optional[str], root: Optional[Path]) -> Path:
    """Resolve the path to a configuration file, honoring project/root settings."""

    if project:
        if config_file == DEFAULT_CONFIG_PATH:
            target = Path(DEFAULT_CONFIG_FILENAME)
        else:
            target = config_file
        return resolve_project_relative(target, project, root)

    if config_file.is_absolute():
        return _normalize_path(config_file)

    return _normalize_path(Path.cwd() / config_file)


def resolve_env_path(env_file: Path, project: Optional[str], root: Optional[Path]) -> Path:
    """Resolve the path for environment variable files."""

    if env_file.is_absolute() and env_file != Path(".env"):
        return _normalize_path(env_file)

    root_dir = resolve_root_dir(root)
    root_env = root_dir / ".env"

    if env_file != Path(".env"):
        return resolve_project_relative(env_file, project, root)

    if project:
        project_dir = resolve_project_dir(project, root)
        project_env = project_dir / ".env"
        return _normalize_path(project_env)

    if root_env.exists():
        return _normalize_path(root_env)

    return _normalize_path(Path.cwd() / env_file)

