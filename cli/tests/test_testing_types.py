from pathlib import Path

import pytest

from fluxloop_cli.testing import (
    DEFAULT_SCENARIOS,
    FluxLoopRunnerOverrides,
    FluxLoopRunnerRequest,
    FluxLoopTestError,
    FluxLoopTestResult,
)


def test_runner_request_resolves_paths(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "configs").mkdir()
    request = FluxLoopRunnerRequest(
        project_root=project_root,
        simulation_config=Path("configs/simulation.yaml"),
    )
    request.resolve_paths()
    assert request.project_root.is_absolute()
    assert request.simulation_config is not None
    assert request.simulation_config.is_absolute()
    assert request.simulation_config.name == "simulation.yaml"


def test_overrides_merge_and_normalize() -> None:
    overrides = FluxLoopRunnerOverrides({"runner.target": "foo:run"})
    overrides.merge({"multi_turn.enabled": True})
    normalized = overrides.normalized()
    assert normalized["runner.target"] == "foo:run"
    assert normalized["multi_turn.enabled"] is True
    # ensure copy
    normalized["runner.target"] = "bar:run"
    assert overrides.values["runner.target"] == "foo:run"


def test_result_from_summary_and_require_success(tmp_path: Path) -> None:
    summary_dir = tmp_path / "exp"
    summary_dir.mkdir()
    summary_payload = {
        "results": {"total_runs": 2, "failed": 1, "success_rate": 0.5, "avg_duration_ms": 120},
        "errors": [
            {"iteration": 0, "persona": "alpha", "input": "hi", "error": "boom"},
        ],
        "output_dir": str(summary_dir),
    }
    result = FluxLoopTestResult.from_summary(summary_payload)
    assert result.failed_runs == 1
    assert not result.succeeded
    with pytest.raises(AssertionError):
        result.require_success(label="smoke")


def test_default_scenarios_cover_key_tags() -> None:
    tags = {tag for scenario in DEFAULT_SCENARIOS for tag in scenario.tags}
    assert {"sdk", "cli", "negative"}.issubset(tags)


def test_error_from_dict_handles_missing_fields() -> None:
    error = FluxLoopTestError.from_dict({})
    assert error.message == ""
    assert error.iteration is None

