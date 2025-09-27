"""Tests for buffer and offline storage."""

import json
from pathlib import Path

import fluxloop 
from fluxloop.buffer import EventBuffer
from fluxloop.context import FluxLoopContext
from fluxloop.models import ObservationData, ObservationType
from fluxloop.config import reset_config


def _create_buffer(tmp_dir: Path, **config_kwargs) -> EventBuffer:
    reset_config()
    existing = getattr(EventBuffer, "_instance", None)
    if existing is not None:
        existing.shutdown()
        EventBuffer._instance = None
    config_kwargs.setdefault("offline_store_dir", str(tmp_dir))
    fluxloop.configure(**config_kwargs)
    return EventBuffer.get_instance()


def test_offline_storage(tmp_path: Path):
    buffer = _create_buffer(
        tmp_path,
        enabled=True,
        sample_rate=1.0,
        use_collector=False,
        offline_store_enabled=True,
    )

    ctx = FluxLoopContext("test-trace")
    obs = ObservationData(type=ObservationType.EVENT, name="step")

    buffer.add_trace(ctx.trace)
    buffer.add_observation(ctx.trace.id, obs)
    buffer.flush()

    traces_file = tmp_path / "traces.jsonl"
    observations_file = tmp_path / "observations.jsonl"

    assert traces_file.exists()
    assert observations_file.exists()

    with traces_file.open() as fp:
        entries = [json.loads(line) for line in fp if line.strip()]
    assert len(entries) == 1
    assert entries[0]["name"] == "test-trace"


def test_offline_store_on_error(tmp_path: Path):
    buffer = _create_buffer(
        tmp_path,
        enabled=True,
        sample_rate=1.0,
        use_collector=True,
        collector_url="http://invalid-host",
        offline_store_enabled=True,
        debug=True,
    )

    ctx = FluxLoopContext("error-trace")
    obs = ObservationData(type=ObservationType.EVENT, name="step")

    buffer.add_trace(ctx.trace)
    buffer.add_observation(ctx.trace.id, obs)
    buffer.flush()

    traces_file = tmp_path / "traces.jsonl"
    observations_file = tmp_path / "observations.jsonl"

    assert traces_file.exists()
    assert observations_file.exists()

