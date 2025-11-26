"""
Pytest fixtures for executing FluxLoop experiments (Week 2/4 deliverables).
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping, MutableMapping, Optional, Sequence, Union

import pytest
import yaml

from fluxloop_cli.config_loader import load_experiment_config, merge_config_overrides
from fluxloop_cli.runner import ExperimentRunner

from .types import (
    FluxLoopRunnerRequest,
    FluxLoopTestResult,
)

PathLike = Union[str, Path]
RunnerCallable = Callable[..., FluxLoopTestResult]
WORKSPACE_DIR_NAME = ".fluxloop_pytest"


def _build_request(
    *,
    project_root: PathLike,
    simulation_config: Optional[PathLike],
    overrides: Optional[Mapping[str, Any]],
    mode: str,
    timeout: Optional[int],
    env: Optional[Mapping[str, str]],
) -> FluxLoopRunnerRequest:
    request = FluxLoopRunnerRequest(
        project_root=Path(project_root),
        simulation_config=Path(simulation_config) if simulation_config else None,
        mode=mode,
    )
    if timeout is not None:
        request.timeout_seconds = timeout
    if overrides:
        request.overrides.merge(overrides)
    if env:
        request.extra_env.update({k: str(v) for k, v in env.items()})
    request.resolve_paths()
    return request


def _determine_config_path(request: FluxLoopRunnerRequest) -> Path:
    if request.simulation_config and request.simulation_config.exists():
        return request.simulation_config

    candidates: Sequence[Path] = (
        request.project_root / "configs",
        request.project_root / "setting.yaml",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Could not locate configs/ or setting.yaml under {request.project_root}"
    )


@contextlib.contextmanager
def _patched_environ(values: Mapping[str, str]):
    previous: MutableMapping[str, Optional[str]] = {}
    try:
        for key, value in values.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = value
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def _build_result_payload(runner: ExperimentRunner) -> dict[str, Any]:
    results = runner.results
    payload = {
        "results": {
            "total_runs": results.get("total_runs", 0),
            "failed": results.get("failed", 0),
            "success_rate": results.get("success_rate", 0.0),
            "avg_duration_ms": results.get("avg_duration_ms", 0.0),
        },
        "errors": results.get("errors", []),
        "output_dir": str(runner.output_dir),
    }
    return payload


def _build_result_object(runner: ExperimentRunner) -> FluxLoopTestResult:
    payload = _build_result_payload(runner)
    trace_summary_path = runner.output_dir / "trace_summary.jsonl"
    if not trace_summary_path.exists():
        trace_summary_path = None
    per_trace_path = runner.output_dir / "per_trace_analysis" / "per_trace.jsonl"
    if not per_trace_path.exists():
        per_trace_path = None
    return FluxLoopTestResult.from_summary(
        payload,
        trace_summary_path=trace_summary_path,
        per_trace_path=per_trace_path,
    )


def _run_with_timeout(
    runner: ExperimentRunner,
    *,
    timeout: Optional[int],
) -> None:
    async def _execute():
        coroutine = runner.run_experiment()
        if timeout is not None:
            return await asyncio.wait_for(coroutine, timeout=timeout)
        return await coroutine

    try:
        asyncio.run(_execute())
    except asyncio.TimeoutError as exc:
        raise AssertionError(
            f"FluxLoop experiment exceeded timeout ({timeout}s)"
        ) from exc


def _load_config_with_overrides(
    request: FluxLoopRunnerRequest,
    *,
    require_inputs_file: bool,
):
    config_path = _determine_config_path(request)
    config = load_experiment_config(
        config_path,
        require_inputs_file=require_inputs_file,
    )
    overrides = request.overrides.normalized()
    if overrides:
        source_dir = config.get_source_dir()
        config = merge_config_overrides(config, overrides)
        if source_dir:
            config.set_source_dir(source_dir)
    return config


def _run_via_sdk(
    request: FluxLoopRunnerRequest,
    *,
    require_inputs_file: bool,
) -> FluxLoopTestResult:
    config = _load_config_with_overrides(
        request,
        require_inputs_file=require_inputs_file,
    )

    runner = ExperimentRunner(config)

    with _patched_environ(request.extra_env):
        _run_with_timeout(runner, timeout=request.timeout_seconds)

    return _build_result_object(runner)


def _workspace_dir(project_root: Path) -> Path:
    workspace = project_root / WORKSPACE_DIR_NAME
    workspace.mkdir(exist_ok=True)
    return workspace


def _abs_path(value: Optional[str], base: Path) -> Optional[str]:
    if not value:
        return value
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str((base / path).resolve())


def _config_to_python_dict(config) -> dict[str, Any]:
    if hasattr(config, "model_dump"):
        return config.model_dump(mode="json")  # type: ignore[call-arg]
    return config.to_dict()


def _materialize_cli_config(
    config,
    request: FluxLoopRunnerRequest,
    workspace: Path,
) -> tuple[Path, Path]:
    source_dir = config.get_source_dir() or request.project_root
    config_dict = _config_to_python_dict(config)
    outputs_base = (workspace / "outputs").resolve()
    outputs_base.mkdir(exist_ok=True)
    config_dict["output_directory"] = str(outputs_base)

    if config_dict.get("inputs_file"):
        config_dict["inputs_file"] = _abs_path(config_dict["inputs_file"], source_dir)

    runner_dict = config_dict.get("runner") or {}
    if runner_dict.get("working_directory"):
        runner_dict["working_directory"] = _abs_path(
            runner_dict["working_directory"], source_dir
        )
    python_paths = runner_dict.get("python_path") or []
    runner_dict["python_path"] = [
        _abs_path(entry, source_dir) for entry in python_paths if entry
    ]
    config_dict["runner"] = runner_dict

    replay_args = config_dict.get("replay_args") or {}
    if replay_args.get("recording_file"):
        replay_args["recording_file"] = _abs_path(replay_args["recording_file"], source_dir)
    config_dict["replay_args"] = replay_args

    config_path = request.project_root / f".cli_config_{uuid.uuid4().hex}.yaml"
    with open(config_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(config_dict, handle, sort_keys=False)
    return config_path, outputs_base


def _update_pythonpath(env: MutableMapping[str, str], project_root: Path) -> None:
    existing = env.get("PYTHONPATH")
    entries = [str(project_root)]
    if existing:
        entries.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(entries)


def _append_log(path: Path, content: str) -> None:
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(content)
        if not content.endswith("\n"):
            handle.write("\n")


def _invoke_cli_command(
    args: list[str],
    *,
    env: Mapping[str, str],
    cwd: Path,
    timeout: Optional[int],
    stdout_log: Path,
    stderr_log: Path,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        [sys.executable, "-m", "fluxloop_cli.main", *args],
        text=True,
        capture_output=True,
        cwd=str(cwd),
        env=dict(env),
        timeout=timeout,
    )
    _append_log(stdout_log, f"$ fluxloop {' '.join(args)}")
    _append_log(stdout_log, proc.stdout)
    _append_log(stderr_log, proc.stderr)
    return proc


def _latest_experiment_dir(outputs_base: Path) -> Path:
    candidates = [p for p in outputs_base.iterdir() if p.is_dir()]
    if not candidates:
        raise AssertionError(f"No experiment directories found under {outputs_base}")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _run_via_cli(
    request: FluxLoopRunnerRequest,
    *,
    require_inputs_file: bool,
) -> FluxLoopTestResult:
    config = _load_config_with_overrides(
        request,
        require_inputs_file=require_inputs_file,
    )
    workspace = _workspace_dir(request.project_root)
    logs_dir = workspace / "logs"
    logs_dir.mkdir(exist_ok=True)

    run_id = uuid.uuid4().hex
    stdout_log = logs_dir / f"{run_id}.stdout.log"
    stderr_log = logs_dir / f"{run_id}.stderr.log"

    config_path, outputs_base = _materialize_cli_config(config, request, workspace)

    env = os.environ.copy()
    env.update({k: v for k, v in request.extra_env.items()})
    _update_pythonpath(env, request.project_root)

    existing_dirs = {
        entry.name for entry in outputs_base.iterdir() if entry.is_dir()
    }

    try:
        run_args = [
            "run",
            "experiment",
            "--config",
            str(config_path),
            "--yes",
            "--no-display",
            "--no-collector",
        ]
        run_proc = _invoke_cli_command(
            run_args,
            env=env,
            cwd=request.project_root,
            timeout=request.timeout_seconds,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
        )
        if run_proc.returncode != 0:
            raise AssertionError(
                f"fluxloop run experiment failed (see {stderr_log})"
            )

        created_dirs = [
            entry
            for entry in outputs_base.iterdir()
            if entry.is_dir() and entry.name not in existing_dirs
        ]
        if created_dirs:
            experiment_dir = max(created_dirs, key=lambda p: p.stat().st_mtime)
        else:
            experiment_dir = _latest_experiment_dir(outputs_base)

        parse_args = [
            "parse",
            "experiment",
            str(experiment_dir),
            "--overwrite",
        ]
        parse_proc = _invoke_cli_command(
            parse_args,
            env=env,
            cwd=request.project_root,
            timeout=request.timeout_seconds,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
        )
        if parse_proc.returncode != 0:
            raise AssertionError(
                f"fluxloop parse experiment failed (see {stderr_log})"
            )

        summary_path = experiment_dir / "summary.json"
        if not summary_path.exists():
            raise AssertionError(f"summary.json missing under {experiment_dir}")
        summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
        summary_payload["output_dir"] = str(experiment_dir)

        trace_summary_path = experiment_dir / "trace_summary.jsonl"
        if not trace_summary_path.exists():
            trace_summary_path = None

        per_trace_path = experiment_dir / "per_trace_analysis" / "per_trace.jsonl"
        if not per_trace_path.exists():
            per_trace_path = None

        cli_command = f"fluxloop {' '.join(run_args)}"

        return FluxLoopTestResult.from_summary(
            summary_payload,
            trace_summary_path=trace_summary_path,
            per_trace_path=per_trace_path,
            stdout_path=stdout_log,
            stderr_path=stderr_log,
            cli_command=cli_command,
        )
    finally:
        with contextlib.suppress(FileNotFoundError):
            config_path.unlink()


def _build_runner_fixture(mode: str) -> RunnerCallable:
    def _runner(
        *,
        project_root: PathLike,
        simulation_config: Optional[PathLike] = None,
        overrides: Optional[Mapping[str, Any]] = None,
        timeout: Optional[int] = None,
        env: Optional[Mapping[str, str]] = None,
        require_inputs_file: bool = True,
    ) -> FluxLoopTestResult:
        request = _build_request(
            project_root=project_root,
            simulation_config=simulation_config,
            overrides=overrides,
            mode=mode,
            timeout=timeout,
            env=env,
        )
        if mode == "cli":
            return _run_via_cli(
                request,
                require_inputs_file=require_inputs_file,
            )
        return _run_via_sdk(
            request,
            require_inputs_file=require_inputs_file,
        )

    return _runner


@pytest.fixture
def fluxloop_runner() -> RunnerCallable:
    """
    Execute experiments via the SDK path (default fixture).
    """

    return _build_runner_fixture("sdk")


@pytest.fixture
def fluxloop_cli() -> RunnerCallable:
    """
    Execute experiments via the CLI path (subprocess parity).
    """

    return _build_runner_fixture("cli")

