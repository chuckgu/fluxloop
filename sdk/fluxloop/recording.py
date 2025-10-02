"""Argument recording utilities for the FluxLoop SDK (MVP implementation)."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


_SENSITIVE_KEY_PATTERNS = [
    "token",
    "password",
    "secret",
    "key",
    "auth",
    "credential",
]

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover - fallback if optional dependency missing
    class BaseModel:  # type: ignore
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


class ArgsRecorder:
    """Simple argument recorder that writes call metadata to a JSONL file."""

    def __init__(self, output_file: Path) -> None:
        self.output_file = output_file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self._iteration_counters: Dict[str, int] = {}

    def record(self, target: str, *, iteration: Optional[int], **kwargs: Any) -> None:
        """Record call arguments for the given target."""

        serializable_kwargs: Dict[str, Any] = {}

        for key, value in kwargs.items():
            if callable(value):
                serializable_kwargs[key] = self._serialize_callable(value)
                continue

            if self._is_sensitive_key(key):
                serializable_kwargs[key] = "***"
                continue

            safe_value = self._coerce_to_json_safe(value)

            try:
                json.dumps(safe_value)
            except (TypeError, ValueError):
                serializable_kwargs[key] = self._serialize_non_json_value(key, value)
            else:
                serializable_kwargs[key] = safe_value

        resolved_iteration = self._resolve_iteration(target, iteration)

        record = {
            "_version": "1",
            "iteration": resolved_iteration,
            "target": target,
            "kwargs": serializable_kwargs,
            "timestamp": datetime.now().isoformat(),
        }

        with self.output_file.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(record, default=str) + "\n")

    def _resolve_iteration(self, target: str, iteration: Optional[int]) -> int:
        if iteration is not None:
            self._iteration_counters[target] = iteration
            return iteration

        next_value = self._iteration_counters.get(target, -1) + 1
        self._iteration_counters[target] = next_value
        return next_value

    def _serialize_callable(self, value: Any) -> str:
        marker = getattr(value, "__fluxloop_builtin__", None)
        if marker:
            return f"<builtin:{marker}>"

        if hasattr(value, "messages"):
            return "<builtin:collector.send>"

        if hasattr(value, "errors"):
            return "<builtin:collector.error>"

        name = getattr(value, "__name__", "unknown")
        return f"<callable:{name}>"

    def _serialize_non_json_value(self, key: str, value: Any) -> Any:
        if self._is_sensitive_key(key):
            return "***"

        coerced = self._coerce_to_json_safe(value)
        try:
            json.dumps(coerced)
            return coerced
        except (TypeError, ValueError):
            representation = repr(value)
            if len(representation) > 100:
                representation = representation[:100]
            return f"<repr:{representation}>"

    def _coerce_to_json_safe(self, value: Any, *, depth: int = 0) -> Any:
        if depth > 3:
            return f"<repr:{type(value).__name__}>"

        if value is None or isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, Mapping):
            result: Dict[str, Any] = {}
            for key, item in value.items():
                mask_key = str(key)
                if self._is_sensitive_key(mask_key):
                    result[mask_key] = "***"
                else:
                    result[mask_key] = self._coerce_to_json_safe(item, depth=depth + 1)
            return result

        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return [
                "***"
                if self._is_collection_with_sensitive_keys(item)
                else self._coerce_to_json_safe(item, depth=depth + 1)
                for item in value
            ]

        if hasattr(value, "__dict__"):
            return {
                str(attr): self._coerce_to_json_safe(attr_value, depth=depth + 1)
                for attr, attr_value in vars(value).items()
                if not attr.startswith("__")
            }

        return value

    def _is_collection_with_sensitive_keys(self, value: Any) -> bool:
        if isinstance(value, Mapping):
            return any(self._is_sensitive_key(str(key)) for key in value.keys())

        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return any(self._is_collection_with_sensitive_keys(item) for item in value)

        return False

    def _is_sensitive_key(self, key: str) -> bool:
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in _SENSITIVE_KEY_PATTERNS)


_global_recorder: Optional[ArgsRecorder] = None

class RecordingConfig(BaseModel):
    iteration_auto_increment: bool = True


_recording_config = RecordingConfig()


def enable_recording(output_file: str) -> None:
    """Enable argument recording by configuring the global recorder."""

    global _global_recorder
    resolved_path = Path(output_file).expanduser().resolve()
    _global_recorder = ArgsRecorder(resolved_path)


def record_call_args(target: str, *, iteration: Optional[int] = None, **kwargs: Any) -> None:
    """Record call arguments if recording is enabled."""

    if _global_recorder is None:
        return

    recorded_iteration = iteration
    if iteration is None and not _recording_config.iteration_auto_increment:
        recorded_iteration = 0

    _global_recorder.record(target, iteration=recorded_iteration, **kwargs)


def disable_recording() -> None:
    """Disable argument recording."""

    global _global_recorder
    _global_recorder = None


def set_recording_options(*, iteration_auto_increment: Optional[bool] = None) -> None:
    """Update global recording behaviour."""

    if iteration_auto_increment is not None:
        _recording_config.iteration_auto_increment = iteration_auto_increment


