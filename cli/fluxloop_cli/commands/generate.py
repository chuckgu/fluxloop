"""Generate command for producing input datasets."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..config_loader import load_experiment_config
from ..input_generator import GenerationSettings, generate_inputs

app = typer.Typer()
console = Console()


@app.command()
def inputs(
    config_file: Path = typer.Option(
        Path("fluxloop.yaml"),
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
):
    """Generate input variations for review before running experiments."""
    if not config_file.exists():
        console.print(f"[red]Error:[/red] Configuration file not found: {config_file}")
        raise typer.Exit(1)

    if output_file.exists() and not overwrite and not dry_run:
        console.print(
            f"[red]Error:[/red] Output file already exists: {output_file}\n"
            "Use --overwrite to replace it."
        )
        raise typer.Exit(1)

    console.print(f"📋 Loading configuration from: [cyan]{config_file}[/cyan]")
    try:
        config = load_experiment_config(config_file)
    except Exception as exc:
        console.print(f"[red]Error loading configuration:[/red] {exc}")
        raise typer.Exit(1)

    settings = GenerationSettings(limit=limit, dry_run=dry_run)

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

    console.print(
        "\n[bold green]Generation complete![/bold green]"
        f"\n📝 Inputs written to: [cyan]{output_file}[/cyan]"
        f"\n✨ Total inputs: [green]{len(result.entries)}[/green]"
    )
