import pathlib
import asyncio

import pytest

from fluxloop_cli.config_loader import load_experiment_config
from fluxloop_cli.input_generator import (
    GenerationSettings,
    GenerationError,
    generate_inputs,
)
from fluxloop_cli.runner import ExperimentRunner
from schemas.config import ExperimentConfig, RunnerConfig


@pytest.fixture
def base_config(tmp_path: pathlib.Path) -> ExperimentConfig:
    return ExperimentConfig(
        name="test",
        runner=RunnerConfig(module_path="examples.simple_agent", function_name="run"),
        base_inputs=[{"input": "Hello"}, {"input": "World"}],
        personas=[],
    )


def test_generate_inputs_basic(base_config: ExperimentConfig) -> None:
    result = generate_inputs(base_config, GenerationSettings())
    assert len(result.entries) == 2
    assert result.entries[0].input == "Hello"
    assert result.entries[1].input == "World"


def test_generate_inputs_with_limit(base_config: ExperimentConfig) -> None:
    settings = GenerationSettings(limit=1)
    result = generate_inputs(base_config, settings)
    assert len(result.entries) == 1


def test_generate_inputs_requires_base_inputs(base_config: ExperimentConfig) -> None:
    base_config.base_inputs = []
    with pytest.raises(GenerationError):
        generate_inputs(base_config, GenerationSettings())


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

    config_path = project_dir / "fluxloop.yaml"
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
    config_path = tmp_path / "fluxloop.yaml"
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
