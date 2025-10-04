"""Parse command for generating human-readable experiment artifacts."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional

import typer
from rich.console import Console

console = Console()
app = typer.Typer()


@dataclass
class Observation:
    """A single observation entry parsed from observations.jsonl."""

    trace_id: str
    type: str
    name: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    level: Optional[str]
    input: Optional[dict]
    output: Optional[dict]
    raw: dict

    @property
    def duration_ms(self) -> Optional[float]:
        """Return duration in milliseconds if timestamps are available."""

        if not self.start_time or not self.end_time:
            return None

        try:
            start = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
            return (end - start).total_seconds() * 1000
        except ValueError:
            return None


@dataclass
class TraceSummary:
    """Reduced structure for entries inside trace_summary.jsonl."""

    trace_id: str
    iteration: int
    persona: Optional[str]
    input_text: str
    output_text: Optional[str]
    duration_ms: float
    success: bool
    raw: dict


def _load_observations(path: Path) -> Dict[str, List[Observation]]:
    """Load observations grouped by trace_id."""

    grouped: Dict[str, List[Observation]] = defaultdict(list)
    if not path.exists():
        raise FileNotFoundError(f"observations.jsonl not found at {path}")

    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON in observations.jsonl at line {line_no}: {exc}"
                ) from exc

            trace_id = payload.get("trace_id")
            if not trace_id:
                # Observations without trace are not relevant for per-trace visualization
                continue

            grouped[trace_id].append(
                Observation(
                    trace_id=trace_id,
                    type=payload.get("type", "unknown"),
                    name=payload.get("name"),
                    start_time=payload.get("start_time"),
                    end_time=payload.get("end_time"),
                    level=payload.get("level"),
                    input=payload.get("input"),
                    output=payload.get("output"),
                    raw=payload,
                )
            )

    return grouped


def _load_trace_summaries(path: Path) -> Iterable[TraceSummary]:
    """Yield trace summaries from trace_summary.jsonl."""

    if not path.exists():
        raise FileNotFoundError(f"trace_summary.jsonl not found at {path}")

    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON in trace_summary.jsonl at line {line_no}: {exc}"
                ) from exc

            trace_id = payload.get("trace_id")
            if not trace_id:
                continue

            yield TraceSummary(
                trace_id=trace_id,
                iteration=payload.get("iteration", 0),
                persona=payload.get("persona"),
                input_text=payload.get("input", ""),
                output_text=payload.get("output"),
                duration_ms=payload.get("duration_ms", 0.0),
                success=payload.get("success", False),
                raw=payload,
            )


def _format_json_block(data: Optional[dict], *, indent: int = 2) -> str:
    """Render a JSON dictionary as a fenced code block."""

    if data is None:
        return "(no data)"

    try:
        return "```json\n" + json.dumps(data, indent=indent, ensure_ascii=False) + "\n```"
    except (TypeError, ValueError):
        # Fallback to raw repr when data contains non-serializable content
        return "```\n" + repr(data) + "\n```"


def _format_markdown(
    trace: TraceSummary,
    observations: List[Observation],
) -> str:
    """Create markdown visualization for a single trace."""

    observations_sorted = sorted(
        observations,
        key=lambda obs: (obs.start_time or "", obs.end_time or ""),
    )

    header = (
        "---\n"
        f"trace_id: \"{trace.trace_id}\"\n"
        f"iteration: {trace.iteration}\n"
        f"persona: {json.dumps(trace.persona) if trace.persona else 'null'}\n"
        f"duration_ms: {trace.duration_ms:.2f}\n"
        f"success: {'true' if trace.success else 'false'}\n"
        "---\n\n"
    )

    summary_section = (
        "# Trace Analysis\n\n"
        "## Summary\n"
        f"- Trace ID: `{trace.trace_id}`\n"
        f"- Iteration: `{trace.iteration}`\n"
        f"- Persona: `{trace.persona or 'N/A'}`\n"
        f"- Duration: `{trace.duration_ms:.2f} ms`\n"
        f"- Success: `{trace.success}`\n"
        "\n"
        "### Input\n"
        f"{_format_json_block({'input': trace.input_text})}\n\n"
        "### Output\n"
        f"{_format_json_block({'output': trace.output_text})}\n\n"
    )

    timeline_lines = ["## Timeline\n"]

    for index, obs in enumerate(observations_sorted, start=1):
        duration = obs.duration_ms
        duration_str = f"{duration:.2f} ms" if duration is not None else "N/A"
        start = obs.start_time or "N/A"
        end = obs.end_time or "N/A"
        timeline_lines.append(
            "---\n"
            f"### Step {index}: [{obs.type}] {obs.name or 'unknown'}\n"
            f"- Start: `{start}`\n"
            f"- End: `{end}`\n"
            f"- Duration: `{duration_str}`\n"
            f"- Level: `{obs.level or 'N/A'}`\n"
            "\n"
            "**Input**\n"
            f"{_format_json_block(obs.input)}\n\n"
            "**Output**\n"
            f"{_format_json_block(obs.output)}\n\n"
        )

    if not observations_sorted:
        timeline_lines.append("(no observations recorded)\n")

    return header + summary_section + "".join(timeline_lines)


def _slugify(name: str) -> str:
    """Create a filesystem-safe slug from a trace identifier."""

    return "".join(c if c.isalnum() or c in {"-", "_"} else "-" for c in name)


def _ensure_experiment_dir(path: Path) -> Path:
    if not path.is_dir():
        raise typer.BadParameter(f"Experiment directory not found: {path}")
    return path


@app.command()
def experiment(
    experiment_dir: Path = typer.Argument(..., help="Path to the experiment output directory"),
    output: Path = typer.Option(
        Path("per_trace_analysis"),
        "--output",
        "-o",
        help="Directory name (relative to experiment_dir) to store parsed files",
    ),
    fmt: Literal["md"] = typer.Option(
        "md",
        "--format",
        "-f",
        help="Output format (currently only 'md' supported)",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite the output directory if it already exists",
    ),
):
    """Parse experiment artifacts into readable per-trace files."""

    if fmt != "md":
        raise typer.BadParameter("Only 'md' format is currently supported")

    experiment_dir = _ensure_experiment_dir(experiment_dir)
    output_dir = experiment_dir / output

    if output_dir.exists():
        if not overwrite:
            raise typer.BadParameter(
                f"Output directory already exists: {output_dir}. Use --overwrite to replace."
            )
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    console.print(
        f"📂 Loading experiment from: [cyan]{experiment_dir.resolve()}[/cyan]"
    )

    observations_path = experiment_dir / "observations.jsonl"
    trace_summary_path = experiment_dir / "trace_summary.jsonl"

    observations = _load_observations(observations_path)
    summaries = list(_load_trace_summaries(trace_summary_path))

    if not summaries:
        console.print("[yellow]No trace summaries found. Nothing to parse.[/yellow]")
        raise typer.Exit(0)

    console.print(
        f"📝 Found {len(summaries)} trace summaries. Generating markdown..."
    )

    for summary in summaries:
        trace_observations = observations.get(summary.trace_id, [])
        content = _format_markdown(summary, trace_observations)
        file_name = f"{summary.iteration:02d}_{_slugify(summary.trace_id)}.{fmt}"
        target_path = output_dir / file_name
        target_path.write_text(content, encoding="utf-8")

    console.print(
        f"✅ Generated {len(summaries)} files in: [green]{output_dir.resolve()}[/green]"
    )


