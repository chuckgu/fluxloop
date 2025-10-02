"""Tests for the argument recording utilities."""

import json
from pathlib import Path
from typing import Optional

import fluxloop


def reset_and_configure(record_args: bool, recording_file: Optional[str] = None) -> None:
    """Helper to reset configuration before enabling/disabling recording."""

    fluxloop.reset_config()
    fluxloop.set_recording_options(iteration_auto_increment=True)
    kwargs = {"record_args": record_args}
    if recording_file is not None:
        kwargs["recording_file"] = recording_file
    fluxloop.configure(debug=False, **kwargs)


def read_single_record(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").splitlines()[0])


def test_record_simple_args(tmp_path):
    """Recording basic kwargs should persist plain JSON values."""

    output_file = tmp_path / "call_args.jsonl"
    reset_and_configure(record_args=True, recording_file=str(output_file))

    fluxloop.record_call_args(
        target="tests.sample:handler",
        connection_id="abc123",
        attempt=1,
    )

    record = read_single_record(output_file)

    assert record["target"] == "tests.sample:handler"
    assert record["kwargs"]["connection_id"] == "abc123"
    assert record["kwargs"]["attempt"] == 1


def test_record_callable_markers(tmp_path):
    """Callable kwargs should be converted into builtin markers."""

    output_file = tmp_path / "call_args.jsonl"
    reset_and_configure(record_args=True, recording_file=str(output_file))

    def send_message(_: str) -> None:
        pass

    send_message.messages = []

    fluxloop.record_call_args(
        target="tests.sample:handler",
        send_message_callback=send_message,
    )

    record = read_single_record(output_file)

    assert record["kwargs"]["send_message_callback"] == "<builtin:collector.send>"


def test_sensitive_keys_are_masked(tmp_path):
    """Values whose keys look sensitive should be masked when serialized."""

    output_file = tmp_path / "call_args.jsonl"
    reset_and_configure(record_args=True, recording_file=str(output_file))

    fluxloop.record_call_args(
        target="tests.sample:handler",
        auth_token="secret-token",
        password="p@ssw0rd",
    )

    record = read_single_record(output_file)

    assert record["kwargs"]["auth_token"] == "***"
    assert record["kwargs"]["password"] == "***"


def test_mapping_is_serialized_as_dict(tmp_path):
    """Mapping-like objects should be coerced into JSON dictionaries."""

    output_file = tmp_path / "call_args.jsonl"
    reset_and_configure(record_args=True, recording_file=str(output_file))

    class CustomMapping(dict):
        pass

    user_connection = CustomMapping(
        user_id="user-123",
        project_id="project-456",
        nested={"token": "secret", "count": 2},
    )

    fluxloop.record_call_args(
        target="tests.sample:handler",
        user_connection=user_connection,
    )

    record = read_single_record(output_file)
    stored = record["kwargs"]["user_connection"]

    assert isinstance(stored, dict)
    assert stored["user_id"] == "user-123"
    assert stored["project_id"] == "project-456"
    assert stored["nested"]["count"] == 2
    # Sensitive key inside nested mapping should be masked
    assert stored["nested"]["token"] == "***"


def test_iteration_auto_increment(tmp_path):
    """Iteration should auto-increment per target when not provided."""

    output_file = tmp_path / "call_args.jsonl"
    reset_and_configure(record_args=True, recording_file=str(output_file))

    fluxloop.record_call_args(target="tests.sample:handler")
    fluxloop.record_call_args(target="tests.sample:handler")
    fluxloop.record_call_args(target="tests.other:handler")

    lines = output_file.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]

    assert records[0]["iteration"] == 0
    assert records[1]["iteration"] == 1
    assert records[2]["iteration"] == 0


def test_iteration_manual_override(tmp_path):
    """Explicit iteration overrides the auto-increment value."""

    output_file = tmp_path / "call_args.jsonl"
    reset_and_configure(record_args=True, recording_file=str(output_file))

    fluxloop.record_call_args(target="tests.sample:handler", iteration=5)
    fluxloop.record_call_args(target="tests.sample:handler")

    records = [json.loads(line) for line in output_file.read_text(encoding="utf-8").splitlines()]
    assert records[0]["iteration"] == 5
    assert records[1]["iteration"] == 6


def test_disable_recording(tmp_path):
    """Disabling recording should prevent additional writes."""

    output_file = tmp_path / "call_args.jsonl"
    reset_and_configure(record_args=True, recording_file=str(output_file))

    fluxloop.record_call_args(target="tests.sample:handler", value="first")

    # Disable recording and attempt another write
    reset_and_configure(record_args=False)
    fluxloop.record_call_args(target="tests.sample:handler", value="second")

    lines = output_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1


