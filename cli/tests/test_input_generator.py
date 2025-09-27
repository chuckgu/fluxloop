import pathlib

import pytest

from fluxloop_cli.input_generator import (
    GenerationSettings,
    GenerationError,
    generate_inputs,
)
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
