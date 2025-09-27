"""Generate command for producing input datasets."""

import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from ..config_loader import load_experiment_config
from ..input_generator import GenerationSettings, generate_inputs
from ..llm_generator import DEFAULT_STRATEGIES
from ..validators import parse_variation_strategies
from ..constants import DEFAULT_CONFIG_PATH, locate_config_file
from schemas.config import InputGenerationMode, VariationStrategy

app = typer.Typer()
console = Console()


@app.command()
def inputs(
    config_file: Path = typer.Option(
        DEFAULT_CONFIG_PATH,
        "--config",
        "-c",
        help="Path to experiment configuration file",
    ),
    output_file: Path = typer.Option(
        ...,
        "--output",
        "-o",
        help="Path to write generated inputs file",
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-l",
        help="Maximum number of inputs to generate",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print planned generation without creating a file",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Allow overwriting an existing output file",
    ),
    mode: Optional[InputGenerationMode] = typer.Option(
        None,
        "--mode",
        case_sensitive=False,
        help="Generation mode: deterministic or llm",
    ),
    strategy: List[str] = typer.Option(  # type: ignore[assignment]
        None,
        "--strategy",
        "-s",
        help="Variation strategy to request (repeatable)",
    ),
    llm_provider: Optional[str] = typer.Option(
        None,
        "--llm-provider",
        help="Override LLM provider for input generation",
    ),
    llm_model: Optional[str] = typer.Option(
        None,
        "--llm-model",
        help="Override LLM model identifier",
    ),
    llm_api_key: Optional[str] = typer.Option(
        None,
        "--llm-api-key",
        help="API key for LLM provider (falls back to FLUXLOOP_LLM_API_KEY)",
    ),
):
    """Generate input variations for review before running experiments."""
    resolved_config = locate_config_file(config_file)
    if not resolved_config.exists():
        console.print(f"[red]Error:[/red] Configuration file not found: {config_file}")
        raise typer.Exit(1)

    if output_file.exists() and not overwrite and not dry_run:
        console.print(
            f"[red]Error:[/red] Output file already exists: {output_file}\n"
            "Use --overwrite to replace it."
        )
        raise typer.Exit(1)

    console.print(f"📋 Loading configuration from: [cyan]{resolved_config}[/cyan]")
    try:
        config = load_experiment_config(resolved_config)
    except Exception as exc:
        console.print(f"[red]Error loading configuration:[/red] {exc}")
        raise typer.Exit(1)

    strategies: Optional[List[VariationStrategy]] = None
    if strategy:
        strategies = parse_variation_strategies(strategy)

    # Apply CLI overrides to configuration
    if mode:
        config.input_generation.mode = mode
        if mode == InputGenerationMode.LLM:
            config.input_generation.llm.enabled = True

    if llm_provider:
        config.input_generation.llm.provider = llm_provider
        config.input_generation.llm.enabled = True

    if llm_model:
        config.input_generation.llm.model = llm_model
        config.input_generation.llm.enabled = True

    resolved_api_key = (
        llm_api_key
        or config.input_generation.llm.api_key
        or os.getenv("FLUXLOOP_LLM_API_KEY")
    )

    if resolved_api_key:
        config.input_generation.llm.api_key = resolved_api_key

    if (
        config.input_generation.mode == InputGenerationMode.LLM
        and not config.input_generation.llm.api_key
    ):
        console.print(
            "[yellow]Warning:[/yellow] LLM mode requested but no API key provided."
        )

    settings = GenerationSettings(
        limit=limit,
        dry_run=dry_run,
        mode=mode,
        strategies=strategies,
        llm_api_key_override=llm_api_key,
    )

    try:
        result = generate_inputs(config, settings)
    except Exception as exc:
        console.print(f"[red]Generation failed:[/red] {exc}")
        if "--debug" in sys.argv:
            console.print_exception()
        raise typer.Exit(1)

    if dry_run:
        console.print("\n[yellow]Dry run mode - no file written[/yellow]")
        console.print(f"Planned inputs: {len(result.entries)}")
        return

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(result.to_yaml(), encoding="utf-8")

    strategies_used = result.metadata.get("strategies") or [s.value for s in DEFAULT_STRATEGIES]

    console.print(
        "\n[bold green]Generation complete![/bold green]"
        f"\n📝 Inputs written to: [cyan]{output_file}[/cyan]"
        f"\n✨ Total inputs: [green]{len(result.entries)}[/green]"
        f"\n🧠 Mode: [magenta]{result.metadata.get('generation_mode', 'deterministic')}[/magenta]"
        f"\n🎯 Strategies: [cyan]{', '.join(strategy for strategy in strategies_used)}[/cyan]"
    )
