"""Tests for ArgBinder."""

import json
import inspect
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
    old_recording = {
        "target": "pkg.mod:Handler.handle",
        "kwargs": {
            "data": {"content": "old"},
            "send_message_callback": "<builtin:collector.send>",
        },
    }
    new_recording = {
        "target": "pkg.mod:Handler.handle",
        "kwargs": {
            "data": {"content": "new"},
            "send_message_callback": "<builtin:collector.send>",
        },
    }
    recording_file = tmp_path / "recording.jsonl"
    recording_file.write_text(
        json.dumps(old_recording) + "\n" + json.dumps(new_recording) + "\n",
        encoding="utf-8",
    )

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

    kwargs = binder.bind_call_args(handler, runtime_input="override")

    assert kwargs["data"]["content"] == "override"
    assert callable(kwargs["send_message_callback"])
    assert hasattr(kwargs["send_message_callback"], "messages")

    result = kwargs["send_message_callback"]("conn-1", {"text": "hello"})
    assert hasattr(result, "__await__")
    assert kwargs["send_message_callback"].messages[-1] == (("conn-1", {"text": "hello"}), {})


@pytest.mark.asyncio
async def test_async_callback_is_awaitable(tmp_path: Path):
    recording = {
        "target": "pkg.mod:Handler.handle",
        "kwargs": {
            "data": {"content": "async"},
            "send_message_callback": "<builtin:collector.send:async>",
            "send_error_callback": "<builtin:collector.error:async>",
        },
    }
    recording_file = tmp_path / "recording.jsonl"
    recording_file.write_text(json.dumps(recording) + "\n", encoding="utf-8")

    config = build_config(
        replay_args=ReplayArgsConfig(
            enabled=True,
            recording_file=str(recording_file),
            callable_providers={
                "send_message_callback": "builtin:collector.send",
                "send_error_callback": "builtin:collector.error",
            },
        )
    )
    config.runner.target = "pkg.mod:Handler.handle"
    config.set_source_dir(tmp_path)

    binder = ArgBinder(config)

    async def handler(data, send_message_callback, send_error_callback):
        await send_message_callback("conn-async", data)
        await send_error_callback("conn-async", "boom")
        return data

    kwargs = binder.bind_call_args(handler, runtime_input="ignored")

    send_cb = kwargs["send_message_callback"]
    error_cb = kwargs["send_error_callback"]

    assert inspect.iscoroutinefunction(send_cb)
    assert inspect.iscoroutinefunction(error_cb)

    await handler(**kwargs)

    expected_data = kwargs["data"]
    assert send_cb.messages[-1] == (("conn-async", expected_data), {})
    assert error_cb.errors[-1] == (("conn-async", "boom"), {})


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

