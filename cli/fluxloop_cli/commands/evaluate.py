"""Evaluate command for scoring experiment outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..evaluation import EvaluationOptions, load_evaluation_config, run_evaluation

console = Console()
app = typer.Typer(help="Evaluate experiment outputs and generate reports.")


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
        Path("evaluation"),
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
        help="LLM API key for judge evaluators (optional)",
        envvar="FLUXLOOP_LLM_API_KEY",
    ),
    sample_rate: Optional[float] = typer.Option(
        None,
        "--sample-rate",
        help="Override LLM evaluation sample rate (0.0-1.0)",
    ),
    max_llm_calls: Optional[int] = typer.Option(
        None,
        "--max-llm",
        help="Maximum number of LLM evaluations to run",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose logging",
    ),
):
    """
    Evaluate experiment outputs and generate aggregate reports.
    """

    resolved_experiment_dir = experiment_dir.resolve()
    if not resolved_experiment_dir.is_dir():
        raise typer.BadParameter(f"Experiment directory not found: {resolved_experiment_dir}")

    if not config.is_absolute():
        config_path = (Path.cwd() / config).resolve()
    else:
        config_path = config

    if sample_rate is not None and not 0.0 <= sample_rate <= 1.0:
        raise typer.BadParameter("--sample-rate must be between 0.0 and 1.0")

    if max_llm_calls is not None and max_llm_calls < 0:
        raise typer.BadParameter("--max-llm must be a non-negative integer")

    try:
        evaluation_config = load_evaluation_config(config_path)
    except FileNotFoundError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise typer.BadParameter(f"Failed to load evaluation config: {exc}") from exc

    output_dir = output
    if not output_dir.is_absolute():
        output_dir = resolved_experiment_dir / output_dir

    options = EvaluationOptions(
        output_dir=output_dir,
        overwrite=overwrite,
        llm_api_key=llm_api_key,
        sample_rate=sample_rate,
        max_llm_calls=max_llm_calls,
        verbose=verbose,
    )

    console.print(
        f"📊 Evaluating experiment at [cyan]{resolved_experiment_dir}[/cyan]\n"
        f"⚙️  Config: [magenta]{config_path}[/magenta]\n"
        f"📁 Output: [green]{output_dir}[/green]"
    )

    summary = run_evaluation(resolved_experiment_dir, evaluation_config, options)

    if verbose:
        console.print("\n[bold]Summary[/bold]")
        for key, value in summary.items():
            console.print(f"• {key}: {value}")


