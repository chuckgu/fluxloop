from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Mapping, Optional

from fluxloop_cli.testing import FluxLoopTestResult


def _write_file(path: Path, content: str) -> None:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


def _create_sample_project(parent: Path) -> Path:
    project = parent / "project"
    project.mkdir()

    examples_dir = project / "examples"
    examples_dir.mkdir()
    (examples_dir / "__init__.py").write_text("", encoding="utf-8")
    _write_file(
        examples_dir / "simple_agent.py",
        """
        def run(input: str, **_):
            return f"ECHO::{input}"
        """,
    )

    _write_file(
        project / "inputs.yaml",
        """
        inputs:
          - input: "Hello world"
            metadata:
              persona: traveler
              persona_description: Frequent flyer
        """,
    )

    _write_file(
        project / "setting.yaml",
        """
        name: pytest_bridge
        iterations: 1
        save_traces: true
        output_directory: experiments
        runner:
          module_path: examples.simple_agent
          function_name: run
          working_directory: "."
        inputs_file: inputs.yaml
        collector_url: null
        """,
    )

    return project


def _run_with_env(
    runner_callable,
    project_root: Path,
    *,
    overrides: Optional[Mapping[str, object]] = None,
) -> FluxLoopTestResult:
    return runner_callable(
        project_root=project_root,
        simulation_config=project_root / "setting.yaml",
        env={"PYTHONPATH": str(project_root)},
        overrides=overrides,
    )


def test_fluxloop_runner_executes_sample_project(fluxloop_runner, tmp_path: Path) -> None:
    project_root = _create_sample_project(tmp_path)
    result = _run_with_env(fluxloop_runner, project_root)
    result.require_success()
    assert result.total_runs == 1
    assert result.trace_summary_path is not None
    assert result.trace_summary_path.exists()


def test_fluxloop_runner_applies_overrides(fluxloop_runner, tmp_path: Path) -> None:
    project_root = _create_sample_project(tmp_path)
    result = _run_with_env(
        fluxloop_runner,
        project_root,
        overrides={"iterations": 2},
    )
    assert result.total_runs == 2
    assert result.success_rate == 1.0


def test_fluxloop_cli_fixture_matches_runner(fluxloop_cli, tmp_path: Path) -> None:
    project_root = _create_sample_project(tmp_path)
    result = _run_with_env(fluxloop_cli, project_root)
    assert result.succeeded
    assert result.stdout_path is not None
    assert result.stdout_path.exists()
    assert result.stderr_path is not None
    assert result.cli_command is not None
    assert "run experiment" in result.cli_command
    assert result.trace_summary_path is not None

