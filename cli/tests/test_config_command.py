import textwrap
from pathlib import Path

from typer.testing import CliRunner

from fluxloop_cli.commands import config as config_cmd

actions_runner = CliRunner()


def _setup_config_dirs(tmp_path: Path) -> Path:
    config_dir = tmp_path / "configs"
    config_dir.mkdir(exist_ok=True)

    (config_dir / "project.yaml").write_text(
        textwrap.dedent(
            """
            name: demo
            """
        ).strip()
    )

    (config_dir / "simulation.yaml").write_text(
        textwrap.dedent(
            """
            name: demo_experiment
            runner:
              module_path: examples.simple_agent
              function_name: run
            """
        ).strip()
    )

    input_path = config_dir / "input.yaml"
    input_path.write_text(
        textwrap.dedent(
            """
            base_inputs:
              - input: "Hello"
            """
        ).strip()
    )

    return input_path


def test_set_llm_updates_env_and_config(tmp_path: Path) -> None:
    input_config = _setup_config_dirs(tmp_path)

    env_file = tmp_path / ".env"
    env_file.write_text("FLUXLOOP_ENVIRONMENT=development\n")

    result = actions_runner.invoke(
        config_cmd.app,
        [
            "set-llm",
            "openai",
            "sk-test",
            "--model",
            "gpt-4.1-mini",
            "--file",
            str(input_config),
            "--env-file",
            str(env_file),
        ],
    )

    assert result.exit_code == 0, result.output
    env_contents = dict(
        line.split("=", 1) for line in env_file.read_text().strip().splitlines()
    )
    assert env_contents.get("OPENAI_API_KEY") == "sk-test"

    updated = input_config.read_text()
    assert "provider: openai" in updated
    assert "model: gpt-4.1-mini" in updated


def test_set_llm_requires_supported_provider(tmp_path: Path) -> None:
    input_config = _setup_config_dirs(tmp_path)

    result = actions_runner.invoke(
        config_cmd.app,
        [
            "set-llm",
            "unsupported",
            "token",
            "--file",
            str(input_config),
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported provider" in result.output

