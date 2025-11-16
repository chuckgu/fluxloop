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


def test_run_experiment_passes_turn_progress_callback(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    inputs_path = tmp_path / "inputs.yaml"

    _write_inputs(inputs_path)
    _write_config(config_path, inputs_path.name)

    captured = {}

    async def fake_run_experiment(self, *, progress_callback=None, turn_progress_callback=None):
        captured["turn_callback"] = turn_progress_callback
        if progress_callback:
            progress_callback()
        if turn_progress_callback:
            turn_progress_callback(1, 5, "Hello there")
            turn_progress_callback(1, 5, None)
        return {
            "input_count": 1,
            "total_runs": 1,
            "successful": 1,
            "failed": 0,
            "success_rate": 1.0,
            "avg_duration_ms": 0,
            "output_dir": str(tmp_path / "outputs"),
        }

    monkeypatch.setattr(
        "fluxloop_cli.commands.run.ExperimentRunner.run_experiment",
        fake_run_experiment,
    )
    monkeypatch.setattr(
        "fluxloop_cli.commands.run.typer.confirm",
        lambda *args, **kwargs: True,
    )

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
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert captured.get("turn_callback") is not None