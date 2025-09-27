import textwrap
from pathlib import Path

from typer.testing import CliRunner

from fluxloop_cli.commands import config as config_cmd


runner = CliRunner()


def test_set_llm_updates_env_and_config(tmp_path: Path, monkeypatch) -> None:
    config_file = tmp_path / "setting.yaml"
    config_file.write_text(
        textwrap.dedent(
            """
            name: demo
            base_inputs:
              - input: "Hello"
            runner:
              module_path: examples.simple_agent
              function_name: run
            """
        ).strip()
    )

    env_file = tmp_path / ".env"
    env_file.write_text("FLUXLOOP_ENVIRONMENT=development\n")

    result = runner.invoke(
        config_cmd.app,
        [
            "set-llm",
            "openai",
            "sk-test",
            "--model",
            "gpt-4.1-mini",
            "--file",
            str(config_file),
            "--env-file",
            str(env_file),
        ],
    )

    assert result.exit_code == 0, result.output
    env_contents = env_file.read_text().strip().splitlines()
    assert "OPENAI_API_KEY=sk-test" in env_contents

    updated = config_file.read_text()
    assert "provider: openai" in updated
    assert "model: gpt-4.1-mini" in updated


def test_set_llm_requires_supported_provider(tmp_path: Path) -> None:
    config_file = tmp_path / "setting.yaml"
    config_file.write_text("name: demo\nrunner:\n  module_path: examples.simple_agent\n  function_name: run\n")

    result = runner.invoke(
        config_cmd.app,
        [
            "set-llm",
            "unsupported",
            "token",
            "--file",
            str(config_file),
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported provider" in result.output

