"""
Utilities for applying project environment settings across CLI commands.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable, Optional, Set

import fluxloop

EnvErrorHandler = Callable[[Path, Exception], None]


def load_env_chain(
    source_dir: Optional[Path],
    *,
    additional_paths: Optional[Iterable[Path]] = None,
    refresh_config: bool = True,
    on_error: Optional[EnvErrorHandler] = None,
) -> None:
    """
    Load environment variables from `.env` files related to a project.

    Parameters
    ----------
    source_dir:
        Directory associated with the current config (usually the config file's parent).
    additional_paths:
        Extra `.env` files to consider (applied after the standard chain).
    refresh_config:
        Whether to refresh the fluxloop config after loading.
    on_error:
        Optional callback invoked when loading a path fails.
    """

    if source_dir is None:
        candidates: Iterable[Path] = additional_paths or []
    else:
        resolved_source = source_dir.resolve()
        parents: list[Path] = []
        parent = resolved_source.parent
        if parent != resolved_source:
            parents.append(parent / ".env")
        parents.append(resolved_source / ".env")

        extra = list(additional_paths or [])
        candidates = [*parents, *extra]

    seen: Set[Path] = set()
    for path in candidates:
        # Avoid duplicate loads and normalize the path
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)

        if not resolved.exists():
            continue

        try:
            fluxloop.load_env(resolved, override=True, refresh_config=refresh_config)
        except Exception as exc:  # noqa: BLE001
            if on_error is None:
                raise
            on_error(resolved, exc)


__all__ = ["load_env_chain", "EnvErrorHandler"]


