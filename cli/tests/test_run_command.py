"""Tests for the `fluxloop run experiment` command."""

from pathlib import Path

from typer.testing import CliRunner

from fluxloop_cli.main import app


def _write_inputs(path: Path) -> None:
    payload = """
inputs:
  - input: "Hello there"
    metadata:
      persona: traveler
      persona_description: Frequent business traveler
      service_context: Airline customer support
"""
    path.write_text(payload.strip() + "\n", encoding="utf-8")


def _write_config(path: Path, inputs_filename: str) -> None:
    payload = f"""
name: cli_multi_turn_test
runner:
  module_path: examples.simple_agent.agent
  function_name: run
inputs_file: {inputs_filename}
collector_url: null
"""
    path.write_text(payload.strip() + "\n", encoding="utf-8")


def test_run_experiment_multi_turn_cli(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    inputs_path = tmp_path / "inputs.yaml"

    _write_inputs(inputs_path)
    _write_config(config_path, inputs_path.name)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run",
            "experiment",
            "--config",
            str(config_path),
            "--multi-turn",
            "--max-turns",
            "5",
            "--auto-approve-tools",
            "--supervisor-provider",
            "mock",
            "--supervisor-model",
            "mock-model",
            "--supervisor-temperature",
            "0.3",
            "--persona-override",
            "vip",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.stdout
    stdout = result.stdout
    assert "Multi-turn" in stdout
    assert "enabled" in stdout
    assert "Max Turns" in stdout
    assert "5" in stdout
    assert "mock-model" in stdout

