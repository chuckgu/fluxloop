"""
Config command for managing configuration.
"""

import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command()
def show(
    config_file: Path = typer.Option(
        Path("fluxloop.yaml"),
        "--file",
        "-f",
        help="Configuration file to show",
    ),
    format: str = typer.Option(
        "yaml",
        "--format",
        help="Output format (yaml, json)",
    ),
):
    """
    Show current configuration.
    """
    if not config_file.exists():
        console.print(f"[red]Error:[/red] Configuration file not found: {config_file}")
        raise typer.Exit(1)
    
    content = config_file.read_text()
    
    if format == "json":
        # Convert YAML to JSON
        import yaml
        import json
        data = yaml.safe_load(content)
        content = json.dumps(data, indent=2)
        lexer = "json"
    else:
        lexer = "yaml"
    
    syntax = Syntax(content, lexer, theme="monokai", line_numbers=True)
    console.print(syntax)


@app.command()
def set(
    key: str = typer.Argument(
        ...,
        help="Configuration key to set (e.g., iterations, runner.timeout)",
    ),
    value: str = typer.Argument(
        ...,
        help="Value to set",
    ),
    config_file: Path = typer.Option(
        Path("fluxloop.yaml"),
        "--file",
        "-f",
        help="Configuration file to update",
    ),
):
    """
    Set a configuration value.
    
    Examples:
    - fluxloop config set iterations 20
    - fluxloop config set runner.timeout 300
    """
    if not config_file.exists():
        console.print(f"[red]Error:[/red] Configuration file not found: {config_file}")
        raise typer.Exit(1)
    
    import yaml
    
    # Load configuration
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    # Parse key path
    keys = key.split(".")
    current = config
    
    # Navigate to the key
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    # Set the value
    final_key = keys[-1]
    
    # Try to parse value as appropriate type
    try:
        # Try as number
        if "." in value:
            parsed_value = float(value)
        else:
            parsed_value = int(value)
    except ValueError:
        # Try as boolean
        if value.lower() in ("true", "false"):
            parsed_value = value.lower() == "true"
        else:
            # Keep as string
            parsed_value = value
    
    current[final_key] = parsed_value
    
    # Save configuration
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    console.print(f"[green]✓[/green] Set {key} = {parsed_value}")


@app.command()
def env(
    show_values: bool = typer.Option(
        False,
        "--show-values",
        "-s",
        help="Show actual values (be careful with secrets)",
    ),
):
    """
    Show environment variables used by FluxLoop.
    """
    env_vars = [
        ("FLUXLOOP_COLLECTOR_URL", "Collector service URL", "http://localhost:8000"),
        ("FLUXLOOP_API_KEY", "API key for authentication", None),
        ("FLUXLOOP_ENABLED", "Enable/disable tracing", "true"),
        ("FLUXLOOP_DEBUG", "Enable debug mode", "false"),
        ("FLUXLOOP_SAMPLE_RATE", "Trace sampling rate (0-1)", "1.0"),
        ("FLUXLOOP_SERVICE_NAME", "Service name for traces", None),
        ("FLUXLOOP_ENVIRONMENT", "Environment (dev/staging/prod)", "development"),
        ("OPENAI_API_KEY", "OpenAI API key", None),
        ("ANTHROPIC_API_KEY", "Anthropic API key", None),
    ]
    
    table = Table(title="FluxLoop Environment Variables")
    table.add_column("Variable", style="cyan")
    table.add_column("Description")
    table.add_column("Current Value")
    table.add_column("Default", style="dim")
    
    for var_name, description, default in env_vars:
        current = os.getenv(var_name)
        
        if current:
            if show_values or not var_name.endswith("_KEY"):
                display_value = current
            else:
                # Mask API keys
                display_value = "****" + current[-4:] if len(current) > 4 else "****"
            display_value = f"[green]{display_value}[/green]"
        else:
            display_value = "[yellow]Not set[/yellow]"
        
        table.add_row(
            var_name,
            description,
            display_value,
            default or "-"
        )
    
    console.print(table)
    
    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        console.print(f"\n[dim]Loading from:[/dim] {env_file}")
    else:
        console.print("\n[yellow]No .env file found[/yellow]")
        console.print("Create one with: [cyan]fluxloop init project[/cyan]")


@app.command()
def validate(
    config_file: Path = typer.Option(
        Path("fluxloop.yaml"),
        "--file",
        "-f",
        help="Configuration file to validate",
    ),
):
    """
    Validate configuration file.
    """
    if not config_file.exists():
        console.print(f"[red]Error:[/red] Configuration file not found: {config_file}")
        raise typer.Exit(1)
    
    from ..config_loader import load_experiment_config
    
    console.print(f"Validating: [cyan]{config_file}[/cyan]\n")
    
    try:
        config = load_experiment_config(config_file)
        
        # Show validation results
        console.print("[green]✓[/green] Configuration is valid!\n")
        
        # Show summary
        table = Table(show_header=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value")
        
        table.add_row("Experiment Name", config.name)
        table.add_row("Iterations", str(config.iterations))
        table.add_row("Personas", str(len(config.personas)))
        table.add_row("Variations", str(config.variation_count))
        table.add_row("Total Runs", str(config.estimate_total_runs()))
        table.add_row("Runner Module", config.runner.module_path)
        table.add_row("Evaluators", str(len(config.evaluators)))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗ Validation failed:[/red] {e}")
        raise typer.Exit(1)
