"""Offline storage helper for FluxLoop traces and observations."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Tuple
from uuid import UUID

from .config import get_config
from .models import ObservationData, TraceData
from .serialization import serialize_observation, serialize_trace


class OfflineStore:
    """Persist traces and observations to local JSON artifacts."""

    def __init__(self) -> None:
        self.config = get_config()
        self.base_dir = Path(self.config.offline_store_dir)
        self.traces_file = self.base_dir / "traces.jsonl"
        self.observations_file = self.base_dir / "observations.jsonl"

        if self.config.offline_store_enabled:
            self.base_dir.mkdir(parents=True, exist_ok=True)

    def record_traces(self, traces: Iterable[TraceData]) -> None:
        if not self.config.offline_store_enabled:
            return

        if not self.traces_file.exists():
            self.traces_file.write_text("")

        with self.traces_file.open("a") as fp:
            for trace in traces:
                fp.write(json.dumps(serialize_trace(trace)) + os.linesep)

    def record_observations(
        self, items: Iterable[Tuple[UUID, ObservationData]]
    ) -> None:
        if not self.config.offline_store_enabled:
            return

        if not self.observations_file.exists():
            self.observations_file.write_text("")

        with self.observations_file.open("a") as fp:
            for trace_id, observation in items:
                payload = serialize_observation(observation)
                payload["trace_id"] = str(trace_id)
                fp.write(json.dumps(payload) + os.linesep)

