"""Utilities for serializing trace and observation data."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict
from uuid import UUID

from .models import ObservationData, TraceData


def _convert_uuid(value: UUID | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _convert_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    # Use ISO 8601 format with UTC indicator when possible
    iso = value.isoformat()
    if value.tzinfo is None:
        return iso + "Z"
    return iso


def _make_json_safe(value: Any) -> Any:
    """Recursively convert values so they can be JSON-serialized."""

    if isinstance(value, datetime):
        return _convert_datetime(value)

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {str(key): _make_json_safe(val) for key, val in value.items()}

    if isinstance(value, (list, tuple, set, frozenset)):
        return [
            _make_json_safe(item)
            for item in value
        ]

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    return repr(value)


def serialize_trace(trace: TraceData) -> Dict[str, Any]:
    """Convert TraceData into a JSON-serializable dictionary."""

    data = trace.model_dump(exclude_none=True)

    if trace.id:
        data["id"] = _convert_uuid(trace.id)
    if trace.session_id:
        data["session_id"] = _convert_uuid(trace.session_id)

    if trace.start_time:
        data["start_time"] = _convert_datetime(trace.start_time)
    if trace.end_time:
        data["end_time"] = _convert_datetime(trace.end_time)

    if "metadata" in data:
        data["metadata"] = _make_json_safe(data["metadata"])

    if "input" in data:
        data["input"] = _make_json_safe(data["input"])

    if "output" in data:
        data["output"] = _make_json_safe(data["output"])

    return data


def serialize_observation(observation: ObservationData) -> Dict[str, Any]:
    """Convert ObservationData into a JSON-serializable dictionary."""

    data = observation.model_dump(exclude_none=True)

    if observation.id:
        data["id"] = _convert_uuid(observation.id)
    if observation.trace_id:
        data["trace_id"] = _convert_uuid(observation.trace_id)
    if observation.parent_observation_id:
        data["parent_observation_id"] = _convert_uuid(observation.parent_observation_id)

    if observation.start_time:
        data["start_time"] = _convert_datetime(observation.start_time)
    if observation.end_time:
        data["end_time"] = _convert_datetime(observation.end_time)

    if "metadata" in data:
        data["metadata"] = _make_json_safe(data["metadata"])

    if "input" in data:
        data["input"] = _make_json_safe(data["input"])

    if "output" in data:
        data["output"] = _make_json_safe(data["output"])

    if "llm_parameters" in data:
        data["llm_parameters"] = _make_json_safe(data["llm_parameters"])

    return data

