from pathlib import Path

from typer.testing import CliRunner

from fluxloop_cli.main import app


runner = CliRunner()


def _write_simulation_config(path: Path) -> None:
    config_dir = path / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "simulation.yaml").write_text("name: test\n", encoding="utf-8")


def test_pytest_template_command_generates_smoke_test(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    _write_simulation_config(project)

    result = runner.invoke(
        app,
        [
            "init",
            "pytest-template",
            str(project),
        ],
    )

    assert result.exit_code == 0, result.stdout
    test_file = project / "tests" / "test_fluxloop_smoke.py"
    assert test_file.exists()
    contents = test_file.read_text()
    assert "fluxloop_runner" in contents
    assert "configs/simulation.yaml" in contents


def test_pytest_template_falls_back_to_setting(tmp_path: Path) -> None:
    project = tmp_path / "legacy"
    project.mkdir()
    (project / "setting.yaml").write_text("name: legacy\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "init",
            "pytest-template",
            str(project),
            "--tests-dir",
            "qa",
            "--filename",
            "test_smoke.py",
        ],
    )

    assert result.exit_code == 0, result.stdout
    test_file = project / "qa" / "test_smoke.py"
    assert test_file.exists()
    contents = test_file.read_text()
    assert "setting.yaml" in contents

