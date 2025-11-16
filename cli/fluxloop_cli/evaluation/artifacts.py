"""
Utilities for working with structured per-trace artifacts produced by `fluxloop parse`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class PerTraceRecord:
    """Structured trace artifact consumed by the evaluation pipeline."""

    data: Dict[str, Any]

    @property
    def trace(self) -> Dict[str, Any]:
        """Return the trace payload used for scoring."""

        return self.data

    @property
    def trace_id(self) -> Optional[str]:
        return self.data.get("trace_id")


def _default_per_trace_path(experiment_dir: Path) -> Path:
    return experiment_dir / "per_trace_analysis" / "per_trace.jsonl"


def load_per_trace_records(
    experiment_dir: Path,
    source_path: Optional[Path] = None,
) -> List[PerTraceRecord]:
    """
    Load structured per-trace artifacts from disk.

    Raises:
        FileNotFoundError: When the per-trace file is missing.
        ValueError: When the file contains invalid JSON or non-object entries.
    """

    path = source_path or _default_per_trace_path(experiment_dir)
    if not path.exists():
        raise FileNotFoundError(
            f"Structured per-trace artifacts not found at {path}. "
            "Run `fluxloop parse` before evaluating."
        )

    records: List[PerTraceRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path} at line {line_no}: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(
                    f"Per-trace entry at line {line_no} must be a JSON object, "
                    f"but got {type(payload).__name__}"
                )
            records.append(PerTraceRecord(data=payload))

    return records


__all__ = ["PerTraceRecord", "load_per_trace_records"]

