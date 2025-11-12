"""
Main CLI application entry point.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .commands import config, doctor, evaluate, generate, init, parse, record, run, status

# Create the main Typer app
app = typer.Typer(
    name="fluxloop",
    help="FluxLoop CLI - Run simulations and manage experiments for AI agents",
    add_completion=True,
    rich_markup_mode="rich",
)

# Create console for rich output
console = Console()

# Add subcommands
app.add_typer(init.app, name="init", help="Initialize a new FluxLoop project")
app.add_typer(run.app, name="run", help="Run simulations and experiments")
app.add_typer(status.app, name="status", help="Check status and view results")
app.add_typer(config.app, name="config", help="Manage configuration")
app.add_typer(generate.app, name="generate", help="Generate input datasets")
app.add_typer(parse.app, name="parse", help="Parse experiments into readable files")
app.add_typer(record.app, name="record", help="Manage recording mode and settings")
app.add_typer(doctor.app, name="doctor", help="Diagnose CLI and MCP environment issues")
app.add_typer(evaluate.app, name="evaluate", help="Evaluate experiment results")


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]FluxLoop CLI[/bold blue] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose output",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode",
    ),
):
    """
    FluxLoop CLI - Simulation and observability for AI agents.
    
    Use [bold]fluxloop --help[/bold] to see available commands.
    """
    # Store global options in context
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug
    
    if debug:
        console.print("[dim]Debug mode enabled[/dim]")


@app.command()
def hello(
    name: str = typer.Argument("World", help="Name to greet"),
):
    """
    Simple hello command to test the CLI.
    """
    console.print(
        Panel(
            f"[bold green]Hello, {name}![/bold green]\n\n"
            f"Welcome to FluxLoop CLI v{__version__}",
            title="[bold blue]FluxLoop[/bold blue]",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    app()
