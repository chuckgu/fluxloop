"""Evaluate command for generating interactive reports."""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

import typer
import yaml
from rich.console import Console

from ..environment import load_env_chain
from ..evaluation import load_evaluation_config
from ..evaluation.artifacts import load_per_trace_records, load_trace_summary_records
from ..evaluation.report.pipeline import ReportPipeline

console = Console()
app = typer.Typer(help="Evaluate experiment outputs and generate interactive reports.")
logger = logging.getLogger(__name__)


def _load_yaml_file(path: Optional[Path]) -> dict:
    if not path or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if isinstance(data, dict):
        return data
    return {}


def _resolve_project_root(config_path: Path) -> Path:
    config_dir = config_path.parent
    return config_dir.parent if config_dir.name == "configs" else config_dir


def _find_config_file(config_path: Path, filename: str) -> Optional[Path]:
    config_dir = config_path.parent
    project_root = _resolve_project_root(config_path)
    candidates = [
        config_dir / filename,
        project_root / "configs" / filename,
        project_root / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _prepare_output_directory(path: Path, overwrite: bool) -> None:
    if path.exists():
        if not overwrite:
            raise typer.BadParameter(
                f"Output directory already exists: {path}. Use --overwrite to replace it."
            )
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _load_generated_inputs_data(input_config: Dict[str, any], project_root: Path) -> Dict[str, any]:
    """
    Load generated inputs (variations) from the configured inputs file, if available.
    """

    inputs_file_value = input_config.get("inputs_file") or "inputs/generated.yaml"
    inputs_path = Path(inputs_file_value)
    if not inputs_path.is_absolute():
        inputs_path = (project_root / inputs_path).resolve()

    if not inputs_path.exists():
        logger.debug("Generated inputs file not found at %s", inputs_path)
        return {}

    try:
        with inputs_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to load generated inputs file %s: %s", inputs_path, exc)
        return {}

    inputs_list: List[Dict[str, any]] = []
    generation_cfg: Dict[str, any] = {}
    if isinstance(payload, dict):
        inputs_list = payload.get("inputs") or payload.get("variations") or []
        generation_cfg = payload.get("generation_config") or {}
    elif isinstance(payload, list):
        inputs_list = payload
    else:
        logger.debug("Generated inputs file %s did not contain a supported structure", inputs_path)
        return {}

    variations: List[Dict[str, str]] = []
    for entry in inputs_list:
        if not isinstance(entry, dict):
            continue
        text = entry.get("input")
        if not text:
            continue
        metadata = entry.get("metadata") or {}
        persona = entry.get("persona") or metadata.get("persona")
        strategy = entry.get("strategy") or metadata.get("variation_strategy") or metadata.get("strategy")

        variations.append(
            {
                "persona": (persona or "unknown").strip(),
                "strategy": (strategy or "base").strip(),
                "input": text.strip(),
            }
        )

    generator_model = generation_cfg.get("model") or generation_cfg.get("generator_model")
    provider = generation_cfg.get("provider")
    if generator_model and provider and "/" not in str(generator_model):
        generator_model = f"{provider}/{generator_model}"

    return {
        "path": str(inputs_path),
        "variations": variations,
        "generator_model": generator_model or input_config.get("input_generation", {})
        .get("llm", {})
        .get("model"),
        "strategies": generation_cfg.get("strategies") or input_config.get("variation_strategies", []),
    }


@app.command()
def experiment(
    experiment_dir: Path = typer.Argument(
        ...,
        help="Path to the experiment output directory",
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
    ),
    config: Path = typer.Option(
        Path("configs/evaluation.yaml"),
        "--config",
        "-c",
        help="Path to evaluation configuration file",
    ),
    output: Path = typer.Option(
        Path("evaluation_report"),
        "--output",
        "-o",
        help="Output directory name (relative to the experiment directory)",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite output directory if it already exists",
    ),
    llm_api_key: Optional[str] = typer.Option(
        None,
        "--llm-api-key",
        help="LLM API key for report generation (optional)",
        envvar="FLUXLOOP_LLM_API_KEY",
    ),
    per_trace: Optional[Path] = typer.Option(
        None,
        "--per-trace",
        help="Path to structured per-trace JSONL generated by `fluxloop parse`",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose logging",
    ),
):
    """
    Evaluate experiment outputs and generate an interactive HTML report.
    """

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
    )

    resolved_experiment_dir = experiment_dir.resolve()
    if not resolved_experiment_dir.is_dir():
        raise typer.BadParameter(f"Experiment directory not found: {resolved_experiment_dir}")

    config_path = config.resolve() if config.is_absolute() else (Path.cwd() / config).resolve()
    project_root = _resolve_project_root(config_path)

    if per_trace is not None:
        per_trace_path = per_trace.resolve() if per_trace.is_absolute() else (Path.cwd() / per_trace).resolve()
    else:
        per_trace_path = resolved_experiment_dir / "per_trace_analysis" / "per_trace.jsonl"

    per_trace_records = load_per_trace_records(resolved_experiment_dir, per_trace_path)
    trace_records = [record.trace for record in per_trace_records]
    if not trace_records:
        raise typer.BadParameter("No traces found in per-trace artifacts.")

    trace_summary_path = resolved_experiment_dir / "trace_summary.jsonl"
    trace_summaries = load_trace_summary_records(resolved_experiment_dir, trace_summary_path)
    if not trace_summaries:
        raise typer.BadParameter("No traces found in trace summary artifacts.")

    try:
        evaluation_config = load_evaluation_config(config_path)
    except FileNotFoundError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise typer.BadParameter(f"Failed to load evaluation config: {exc}") from exc

    def _log_env_error(path: Path, exc: Exception) -> None:
        console.log(
            f"[yellow]Warning:[/yellow] Failed to load environment from {path}: {exc}"
        )

    load_env_chain(
        evaluation_config.get_source_dir(),
        refresh_config=True,
        on_error=_log_env_error,
    )

    if llm_api_key is None:
        llm_api_key = os.getenv("FLUXLOOP_LLM_API_KEY") or os.getenv("OPENAI_API_KEY")

    output_dir = output if output.is_absolute() else (resolved_experiment_dir / output)
    _prepare_output_directory(output_dir, overwrite)

    input_config_path = _find_config_file(config_path, "input.yaml")
    project_config_path = _find_config_file(config_path, "project.yaml")

    input_config = _load_yaml_file(input_config_path)
    project_config = _load_yaml_file(project_config_path)
    generated_inputs = _load_generated_inputs_data(input_config, project_root)

    config_bundle = {
        "name": project_config.get("name") or resolved_experiment_dir.name,
        "evaluation": asdict(evaluation_config),
        "input": input_config,
        "generated_inputs": generated_inputs,
    }

    pipeline = ReportPipeline(
        config=config_bundle,
        output_dir=output_dir,
        api_key=llm_api_key,
    )

    message_lines = [
        f"📊 Evaluating experiment at [cyan]{resolved_experiment_dir}[/cyan]",
        f"⚙️  Config: [magenta]{config_path}[/magenta]",
        f"🧵 Per-trace data: [blue]{per_trace_path}[/blue]",
        f"📄 Trace summary: [blue]{trace_summary_path}[/blue]",
        f"📁 Output: [green]{output_dir}[/green]",
    ]
    console.print("\n".join(message_lines))

    artifacts = asyncio.run(pipeline.run(trace_records, trace_summaries))
    console.print(f"\n✅ Report ready: [bold cyan]{artifacts.html_path}[/bold cyan]")



