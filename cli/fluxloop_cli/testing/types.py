"""
Core data structures for the Pytest bridge (Week 1 deliverables).

These definitions capture the request/result contract so fixtures can be
implemented later without changing user-facing APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence


FluxLoopRunnerMode = str  # Literal["sdk", "cli"] 예정, but keep flexible for now


@dataclass(slots=True)
class FluxLoopRunnerOverrides:
    """User supplied key-path → value overrides for ExperimentConfig."""

    values: MutableMapping[str, Any] = field(default_factory=dict)

    def normalized(self) -> Dict[str, Any]:
        """Return a shallow copy for downstream mutation safety."""
        return dict(self.values)

    def merge(self, *overrides: Mapping[str, Any]) -> "FluxLoopRunnerOverrides":
        merged = self.normalized()
        for item in overrides:
            merged.update(item)
        self.values = merged
        return self


@dataclass(slots=True)
class FluxLoopRunnerRequest:
    """
    Normalized request payload consumed by the future pytest fixtures.

    `project_root` is required so we can locate configs/ and .env files.
    """

    project_root: Path
    simulation_config: Optional[Path] = None
    mode: FluxLoopRunnerMode = "sdk"
    overrides: FluxLoopRunnerOverrides = field(default_factory=FluxLoopRunnerOverrides)
    timeout_seconds: Optional[int] = 600
    extra_env: MutableMapping[str, str] = field(default_factory=dict)

    def resolve_paths(self) -> None:
        """
        Ensure all paths are absolute so fixtures can run from any cwd.
        """
        self.project_root = self.project_root.expanduser().resolve()
        if self.simulation_config is not None:
            config_path = self.simulation_config
            if not config_path.is_absolute():
                config_path = self.project_root / config_path
            self.simulation_config = config_path.expanduser().resolve()


@dataclass(slots=True)
class FluxLoopTestError:
    """Represents a single failure entry from the experiment summary."""

    iteration: Optional[int]
    persona: Optional[str]
    input_text: Optional[str]
    message: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "FluxLoopTestError":
        return cls(
            iteration=payload.get("iteration"),
            persona=payload.get("persona"),
            input_text=payload.get("input"),
            message=str(payload.get("error", "")),
        )


@dataclass(slots=True)
class FluxLoopTestResult:
    """Aggregate summary emitted back to pytest test functions."""

    total_runs: int
    failed_runs: int
    success_rate: float
    avg_duration_ms: float
    output_dir: Path
    summary_path: Path
    trace_summary_path: Optional[Path]
    per_trace_path: Optional[Path]
    stdout_path: Optional[Path] = None
    stderr_path: Optional[Path] = None
    cli_command: Optional[str] = None
    errors: Sequence[FluxLoopTestError] = field(default_factory=tuple)

    @property
    def succeeded(self) -> bool:
        return self.failed_runs == 0

    def require_success(self, *, label: Optional[str] = None) -> None:
        if self.succeeded:
            return
        reason = label or "FluxLoop experiment"
        details = "; ".join(err.message for err in self.errors[:3]) or "unknown failure"
        raise AssertionError(f"{reason} failed ({self.failed_runs} runs): {details}")

    @classmethod
    def from_summary(
        cls,
        summary: Mapping[str, Any],
        *,
        trace_summary_path: Optional[Path] = None,
        per_trace_path: Optional[Path] = None,
        stdout_path: Optional[Path] = None,
        stderr_path: Optional[Path] = None,
        cli_command: Optional[str] = None,
    ) -> "FluxLoopTestResult":
        results = summary.get("results", {})
        errors = [FluxLoopTestError.from_dict(raw) for raw in summary.get("errors", [])]
        output_dir = Path(summary.get("output_dir", summary.get("name", "experiments"))).expanduser()
        summary_path = output_dir / "summary.json"
        return cls(
            total_runs=int(results.get("total_runs", 0)),
            failed_runs=int(results.get("failed", 0)),
            success_rate=float(results.get("success_rate", 0.0)),
            avg_duration_ms=float(results.get("avg_duration_ms", 0.0)),
            output_dir=output_dir,
            summary_path=summary_path,
            trace_summary_path=trace_summary_path,
            per_trace_path=per_trace_path,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            cli_command=cli_command,
            errors=tuple(errors),
        )


@dataclass(slots=True)
class FluxLoopTestScenario:
    """Design-time catalog of QA scenarios the fixtures must support."""

    name: str
    description: str
    tags: Sequence[str] = field(default_factory=tuple)


DEFAULT_SCENARIOS: Sequence[FluxLoopTestScenario] = (
    FluxLoopTestScenario(
        name="single-turn-sync",
        description="Basic python function target without multi-turn supervisor.",
        tags=("sdk", "happy-path"),
    ),
    FluxLoopTestScenario(
        name="multi-turn-supervisor",
        description="ConversationSupervisor enabled with scripted user turns.",
        tags=("sdk", "multi-turn"),
    ),
    FluxLoopTestScenario(
        name="subprocess-jsonl",
        description="Runner configured via subprocess JSONL stream to validate CLI parity.",
        tags=("cli", "subprocess"),
    ),
    FluxLoopTestScenario(
        name="mcp-adapter",
        description="MCP server target requiring environment injection and guard handling.",
        tags=("sdk", "mcp"),
    ),
    FluxLoopTestScenario(
        name="failure-capture",
        description="Intentional failure to verify error surfaces and pytest assertion formatting.",
        tags=("sdk", "negative"),
    ),
)


__all__ = [
    "FluxLoopRunnerMode",
    "FluxLoopRunnerOverrides",
    "FluxLoopRunnerRequest",
    "FluxLoopTestError",
    "FluxLoopTestResult",
    "FluxLoopTestScenario",
    "DEFAULT_SCENARIOS",
]

