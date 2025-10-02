"""Tests for generating inputs from a recording template."""

import json
from pathlib import Path

from fluxloop.schemas import ExperimentConfig, ReplayArgsConfig
from fluxloop_cli.commands.generate import _load_recording_template
import pytest

from fluxloop_cli.input_generator import GenerationSettings, GenerationError, generate_inputs


class StubLLMClient:
    def generate(self, *, prompts, config, llm_config):
        return [
            {
                "input": f"variation-{index}",
                "metadata": {"strategy": prompt_meta.get("strategy")},
            }
            for index, (_, prompt_meta) in enumerate(prompts)
        ]


def build_config(tmp_path: Path) -> ExperimentConfig:
    payload = {
        "name": "test",
        "runner": {
            "module_path": "examples.simple_agent",
            "function_name": "run",
        },
        "base_inputs": [{"input": "hello"}],
        "input_generation": {"mode": "llm", "llm": {"enabled": True}},
        "replay_args": ReplayArgsConfig(
            enabled=True,
            recording_file=str(tmp_path / "recording.jsonl"),
        ),
    }
    config = ExperimentConfig(**payload)
    config.set_source_dir(tmp_path)
    return config


def test_load_recording_template(tmp_path: Path) -> None:
    data = {
        "target": "pkg.mod:Handler.handle",
        "kwargs": {
            "data": {"content": "Base message"},
        },
    }
    recording_file = tmp_path / "recording.jsonl"
    recording_file.write_text(json.dumps(data) + "\n", encoding="utf-8")

    config = build_config(tmp_path)
    template = _load_recording_template(recording_file, config)

    assert template["base_content"] == "Base message"
    assert template["target"] == "pkg.mod:Handler.handle"


def test_generate_inputs_from_recording(tmp_path: Path) -> None:
    data = {
        "target": "pkg.mod:Handler.handle",
        "kwargs": {
            "data": {"content": "Original"},
        },
    }
    recording_file = tmp_path / "recording.jsonl"
    recording_file.write_text(json.dumps(data) + "\n", encoding="utf-8")

    config = build_config(tmp_path)
    template = _load_recording_template(recording_file, config)

    settings = GenerationSettings(llm_client=StubLLMClient())
    result = generate_inputs(
        config,
        settings,
        recording_template=template,
    )

    assert len(result.entries) == 3
    for entry in result.entries:
        assert entry.metadata.get("args_template") == "use_recorded"
        assert entry.metadata.get("template_kwargs") == template["full_kwargs"]
    assert result.metadata.get("recording_target") == "pkg.mod:Handler.handle"

