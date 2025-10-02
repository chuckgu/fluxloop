"""Utilities for dynamically loading experiment targets."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Callable, Optional

from fluxloop.schemas import RunnerConfig


class TargetLoader:
    """Load callables defined by an experiment runner configuration."""

    def __init__(self, config: RunnerConfig, source_dir: Optional[Path] = None) -> None:
        self.config = config
        self.source_dir = source_dir

    def load(self) -> Callable:
        """Return a callable based on the configured target."""

        work_dir = self._resolve_working_directory()
        remove_path = False

        if work_dir and work_dir not in sys.path:
            sys.path.insert(0, work_dir)
            remove_path = True

        try:
            if self.config.target:
                return self._load_from_target(self.config.target)

            module = importlib.import_module(self.config.module_path)
            return getattr(module, self.config.function_name)
        finally:
            if remove_path:
                sys.path.remove(work_dir)

    def _resolve_working_directory(self) -> str | None:
        if not self.config.working_directory:
            return None

        raw_path = Path(self.config.working_directory)
        if not raw_path.is_absolute() and self.source_dir:
            raw_path = (self.source_dir / raw_path).resolve()
        else:
            raw_path = raw_path.expanduser().resolve()

        path = raw_path
        return str(path)

    def _load_from_target(self, target: str) -> Callable:
        if ":" not in target:
            raise ValueError(
                "Invalid runner.target format. Expected 'module:function' or 'module:Class.method'."
            )

        module_name, attribute_part = target.split(":", 1)

        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            raise ValueError(f"Failed to import module '{module_name}' for target '{target}': {exc}")

        if "." in attribute_part:
            class_name, method_name = attribute_part.split(".", 1)
            try:
                cls = getattr(module, class_name)
            except AttributeError as exc:
                raise ValueError(
                    f"Class '{class_name}' not found in module '{module_name}' for target '{target}'."
                ) from exc

            try:
                instance = cls()
            except TypeError as exc:
                raise ValueError(
                    "MVP limitation: only classes with zero-argument constructors are supported."
                ) from exc

            try:
                return getattr(instance, method_name)
            except AttributeError as exc:
                raise ValueError(
                    f"Method '{method_name}' not found on class '{class_name}' for target '{target}'."
                ) from exc

        try:
            return getattr(module, attribute_part)
        except AttributeError as exc:
            raise ValueError(
                f"Function or attribute '{attribute_part}' not found in module '{module_name}' for target '{target}'."
            ) from exc

