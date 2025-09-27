"""Utilities for serializing trace and observation data."""

from __future__ import annotations

from datetime import datetime
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

    return data

