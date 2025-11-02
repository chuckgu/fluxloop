"""Utilities for dynamically loading experiment targets."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Callable, Optional, List

from fluxloop.schemas import RunnerConfig


class TargetLoader:
    """Load callables defined by an experiment runner configuration."""

    def __init__(self, config: RunnerConfig, source_dir: Optional[Path] = None) -> None:
        self.config = config
        self.source_dir = source_dir

    def load(self) -> Callable:
        """Return a callable based on the configured target."""

        work_dir = self._resolve_working_directory()
        added_paths: list[str] = []

        if work_dir and work_dir not in sys.path:
            sys.path.insert(0, work_dir)
            added_paths.append(work_dir)

        for extra in self._resolve_python_paths():
            if extra not in sys.path:
                sys.path.insert(0, extra)
                added_paths.append(extra)

        try:
            if self.config.target:
                return self._load_from_target(self.config.target)

            module = importlib.import_module(self.config.module_path)
            return getattr(module, self.config.function_name)
        finally:
            for path_entry in added_paths:
                if path_entry in sys.path:
                    sys.path.remove(path_entry)

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

    def _resolve_python_paths(self) -> List[str]:
        resolved: List[str] = []
        entries = getattr(self.config, "python_path", []) or []

        for entry in entries:
            raw_path = Path(entry)
            if not raw_path.is_absolute():
                base = self.source_dir if self.source_dir else Path.cwd()
                raw_path = (base / raw_path).resolve()
            else:
                raw_path = raw_path.expanduser().resolve()

            resolved.append(str(raw_path))

        return resolved

    def _load_from_target(self, target: str) -> Callable:
        """Resolve a callable from target string.

        Supports:
          - module:function
          - module:variable
          - module:Class.method
          - module:variable.method
        If the first attribute is a class, attempts to construct an instance via:
          - runner.factory if provided (module:callable)
          - zero-argument constructor fallback
        """

        if ":" not in target:
            raise ValueError(
                "Invalid runner.target format. Expected 'module:symbol[.attr]'."
            )

        module_name, attribute_chain = target.split(":", 1)

        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            raise ValueError(
                f"Failed to import module '{module_name}' for target '{target}': {exc}"
            )

        parts = attribute_chain.split(".") if attribute_chain else []
        if not parts:
            raise ValueError(f"Invalid target '{target}': missing attribute path")

        # Resolve first symbol from module
        try:
            obj: Any = getattr(module, parts[0])
        except AttributeError as exc:
            raise ValueError(
                f"Symbol '{parts[0]}' not found in module '{module_name}' for target '{target}'."
            ) from exc

        # If it's a class, construct instance
        if isinstance(obj, type):
            factory = getattr(self.config, "factory", None)
            factory_kwargs = getattr(self.config, "factory_kwargs", {}) or {}
            if factory:
                if ":" not in factory:
                    raise ValueError("runner.factory must be in 'module:callable' format")
                fmod, fname = factory.split(":", 1)
                try:
                    fac_mod = importlib.import_module(fmod)
                    fac = getattr(fac_mod, fname)
                except Exception as exc:
                    raise ValueError(
                        f"Failed to import factory '{factory}' for target '{target}': {exc}"
                    ) from exc
                try:
                    obj = fac(**factory_kwargs)
                except Exception as exc:
                    raise ValueError(
                        f"Factory '{factory}' failed to construct instance: {exc}"
                    ) from exc
            else:
                try:
                    obj = obj()
                except TypeError as exc:
                    raise ValueError(
                        "Cannot construct class without zero-argument constructor. "
                        "Provide runner.factory to construct the instance."
                    ) from exc

        # Traverse remaining attributes
        for attr in parts[1:]:
            try:
                obj = getattr(obj, attr)
            except AttributeError as exc:
                raise ValueError(
                    f"Attribute '{attr}' not found while resolving target '{target}'."
                ) from exc

        if not callable(obj):
            raise ValueError(f"Resolved target '{target}' is not callable.")

        return obj

