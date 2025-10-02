"""Tests for ArgBinder."""

import json
from pathlib import Path

import pytest

from fluxloop.schemas import ExperimentConfig, ReplayArgsConfig, RunnerConfig
from fluxloop_cli.arg_binder import ArgBinder


def build_config(**overrides):
    payload = {
        "name": "test",
        "runner": {
            "module_path": "examples.simple_agent",
            "function_name": "run",
        },
        "base_inputs": [{"input": "seed"}],
    }
    payload.update(overrides)

    return ExperimentConfig(**payload)


def test_bind_without_replay():
    def handler(input_text: str) -> str:
        return input_text

    config = build_config()
    binder = ArgBinder(config)

    kwargs = binder.bind_call_args(handler, runtime_input="hello")

    assert kwargs == {"input_text": "hello"}


def test_bind_with_replay(tmp_path: Path):
    recording = {
        "target": "pkg.mod:Handler.handle",
        "kwargs": {
            "data": {"content": "old"},
            "send_message_callback": "<builtin:collector.send>",
        },
    }
    recording_file = tmp_path / "recording.jsonl"
    recording_file.write_text(json.dumps(recording) + "\n", encoding="utf-8")

    config = build_config(
        replay_args=ReplayArgsConfig(
            enabled=True,
            recording_file=str(recording_file),
            override_param_path="data.content",
        )
    )
    config.runner.target = "pkg.mod:Handler.handle"
    config.set_source_dir(tmp_path)

    binder = ArgBinder(config)

    def handler(data, send_message_callback):
        return data, send_message_callback

    kwargs = binder.bind_call_args(handler, runtime_input="new")

    assert kwargs["data"]["content"] == "new"
    assert callable(kwargs["send_message_callback"])
    assert hasattr(kwargs["send_message_callback"], "messages")


def test_raises_for_missing_callable_mapping(tmp_path: Path):
    recording = {
        "target": "pkg.mod:Handler.handle",
        "kwargs": {"custom_callback": "<callable:custom>"},
    }
    recording_file = tmp_path / "recording.jsonl"
    recording_file.write_text(json.dumps(recording) + "\n", encoding="utf-8")

    config = build_config(
        replay_args=ReplayArgsConfig(
            enabled=True,
            recording_file=str(recording_file),
            callable_providers={},
            override_param_path=None,
        )
    )
    config.runner.target = "pkg.mod:Handler.handle"
    config.set_source_dir(tmp_path)

    binder = ArgBinder(config)

    def handler(custom_callback=None):
        return custom_callback

    with pytest.raises(ValueError, match="Missing callable providers"):
        binder.bind_call_args(handler, runtime_input="test")

