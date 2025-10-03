import asyncio
import pathlib
from typing import List

import pytest

from fluxloop_cli.config_loader import load_experiment_config
from fluxloop_cli.input_generator import (
    GenerationError,
    GenerationResult,
    GenerationSettings,
    generate_inputs,
)
from fluxloop_cli.llm_generator import DEFAULT_STRATEGIES, generate_llm_inputs
from fluxloop_cli.runner import ExperimentRunner
from fluxloop_cli.validators import parse_variation_strategies
from fluxloop.schemas import ExperimentConfig, InputGenerationMode, RunnerConfig


@pytest.fixture
def base_config(tmp_path: pathlib.Path) -> ExperimentConfig:
    return ExperimentConfig(
        name="test",
        runner=RunnerConfig(module_path="examples.simple_agent", function_name="run"),
        base_inputs=[{"input": "Hello"}, {"input": "World"}],
        personas=[],
    )


def test_generate_inputs_requires_base_inputs(base_config: ExperimentConfig) -> None:
    base_config.base_inputs = []
    with pytest.raises(GenerationError):
        generate_inputs(base_config, GenerationSettings())


class StubLLMClient:
    """Minimal stub that mimics the LLMClient protocol."""

    def __init__(self) -> None:
        self.calls: List[dict] = []

    async def generate(self, *, prompts, config, llm_config):
        self.calls.append({
            "prompts": prompts,
            "config_name": config.name,
            "model": llm_config.model,
        })
        outputs = []
        for (_, metadata) in prompts:
            outputs.append({
                "input": f"Generated for {metadata['strategy']}",
                "metadata": metadata,
            })
        return outputs


def test_generate_inputs_llm_mode(base_config: ExperimentConfig) -> None:
    base_config.input_generation.mode = InputGenerationMode.LLM
    base_config.input_generation.llm.enabled = True
    base_config.variation_strategies = []

    stub = StubLLMClient()
    settings = GenerationSettings(llm_client=stub)

    result = generate_inputs(base_config, settings)

    assert len(result.entries) == len(base_config.base_inputs) * 3
    assert result.metadata["generation_mode"] == InputGenerationMode.LLM.value
    assert stub.calls[0]["model"] == base_config.input_generation.llm.model


def test_load_external_inputs_relative(tmp_path: pathlib.Path) -> None:
    project_dir = tmp_path / "project"
    inputs_dir = project_dir / "inputs"
    inputs_dir.mkdir(parents=True)
    inputs_file = inputs_dir / "generated.yaml"
    inputs_file.write_text(
        """
inputs:
  - input: "One"
  - input: "Two"
""".strip()
    )

    config_path = project_dir / "setting.yaml"
    config_path.write_text(
        """
name: relative_test
iterations: 1
base_inputs: []
inputs_file: inputs/generated.yaml
runner:
  module_path: examples.simple_agent
  function_name: run
""".strip()
    )

    config = load_experiment_config(config_path)
    runner = ExperimentRunner(config, no_collector=True)

    variations = asyncio.run(runner._load_inputs())
    assert len(variations) == 2
    assert config.get_resolved_input_count() == 2
    assert variations[0]["input"] == "One"


def test_resolved_input_count_from_loader(tmp_path: pathlib.Path) -> None:
    config_path = tmp_path / "setting.yaml"
    config_path.write_text(
        """
name: loader_count
iterations: 2
variation_count: 3
base_inputs:
  - input: "A"
  - input: "B"
runner:
  module_path: examples.simple_agent
  function_name: run
""".strip()
    )

    config = load_experiment_config(config_path)
    assert config.get_resolved_input_count() == 6
    assert config.estimate_total_runs() == 12


def test_openai_payload_omits_reasoning_and_text_when_unset(monkeypatch):
    calls = []

    async def fake_request_openai(client, *, config, payload):
        calls.append(payload)
        return {"choices": [{"message": {"content": "generated"}}]}

    monkeypatch.setattr(
        "fluxloop_cli.llm_generator._request_openai",
        fake_request_openai,
    )

    config = ExperimentConfig(
        name="test",
        runner={"module_path": "examples.simple_agent", "function_name": "run"},
        base_inputs=[{"input": "hello"}],
        input_generation={
            "mode": "llm",
            "llm": {
                "enabled": True,
                "provider": "openai",
                "model": "gpt-4o-mini",
            },
        },
    )

    settings = GenerationSettings(limit=1)
    result = generate_llm_inputs(config=config, strategies=DEFAULT_STRATEGIES[:1], settings=settings)

    assert result
    payload = calls[0]
    assert "reasoning" not in payload
    assert "text" not in payload
