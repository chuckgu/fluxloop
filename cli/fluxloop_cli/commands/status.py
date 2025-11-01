"""
Status command for checking system and experiment status.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..constants import DEFAULT_CONFIG_PATH, DEFAULT_ROOT_DIR_NAME
from ..config_schema import CONFIG_SECTION_FILENAMES, CONFIG_REQUIRED_KEYS
from ..project_paths import (
    resolve_config_path,
    resolve_config_directory,
    resolve_root_dir,
    resolve_project_relative,
)

app = typer.Typer()
console = Console()


@app.command()
def check(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information",
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        help="Project name under the FluxLoop root",
    ),
    root: Path = typer.Option(
        Path(DEFAULT_ROOT_DIR_NAME),
        "--root",
        help="FluxLoop root directory",
    ),
):
    """
    Check FluxLoop system status.
    
    Verifies:
    - SDK installation
    - Collector connectivity
    - Configuration validity
    """
    console.print("[bold]FluxLoop Status Check[/bold]\n")
    
    status_table = Table(show_header=False)
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Status")
    status_table.add_column("Details", style="dim")
    
    # Check SDK
    try:
        import fluxloop
        sdk_version = fluxloop.__version__
        status_table.add_row(
            "SDK",
            "[green]✓ Installed[/green]",
            f"Version {sdk_version}"
        )
    except ImportError:
        status_table.add_row(
            "SDK",
            "[red]✗ Not installed[/red]",
            "Run: pip install fluxloop-sdk"
        )
    
    # Check collector connectivity
    try:
        from fluxloop import get_config
        from fluxloop.client import FluxLoopClient
        
        config = get_config()
        client = FluxLoopClient()
        
        # Try to connect (this would need a health endpoint)
        status_table.add_row(
            "Collector",
            "[yellow]? Unknown[/yellow]",
            f"URL: {config.collector_url}"
        )
    except Exception as e:
        status_table.add_row(
            "Collector",
            "[red]✗ Error[/red]",
            str(e) if verbose else "Connection failed"
        )
    
    # Check for configuration file
    resolved_config = resolve_config_path(DEFAULT_CONFIG_PATH, project, root)
    config_dir = resolve_config_directory(project, root)

    missing_sections = [
        CONFIG_SECTION_FILENAMES[key]
        for key in CONFIG_SECTION_FILENAMES
        if not (config_dir / CONFIG_SECTION_FILENAMES[key]).exists()
    ]

    if resolved_config.exists() and not missing_sections:
        status_table.add_row(
            "Config",
            "[green]✓ Found[/green]",
            str(config_dir)
        )
    else:
        detail_parts = []
        if not config_dir.exists():
            detail_parts.append(f"Missing directory: {config_dir}")
        if missing_sections:
            required_missing = [
                name for name in missing_sections
                if _section_key_from_filename(name) in CONFIG_REQUIRED_KEYS
            ]
            if required_missing:
                detail_parts.append(
                    "Missing sections: " + ", ".join(required_missing)
                )
        if not detail_parts:
            detail_parts.append("Run: fluxloop init project")

        status_table.add_row(
            "Config",
            "[yellow]- Incomplete[/yellow]",
            "\n".join(detail_parts)
        )
    
    # Check environment
    import os
    if os.getenv("FLUXLOOP_API_KEY"):
        status_table.add_row(
            "API Key",
            "[green]✓ Set[/green]",
            "****" + os.getenv("FLUXLOOP_API_KEY")[-4:] if verbose else "Configured"
        )
    else:
        status_table.add_row(
            "API Key",
            "[yellow]- Not set[/yellow]",
            "Set FLUXLOOP_API_KEY in .env"
        )
    
    console.print(status_table)
    
    # Show recommendations
    recommendations = []
    if not resolved_config.exists():
        recommendations.append("Initialize a project: [cyan]fluxloop init project[/cyan]")
    if not os.getenv("FLUXLOOP_API_KEY"):
        recommendations.append("Set up API key in .env file")
    
    if recommendations:
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in recommendations:
            console.print(f"  • {rec}")


def _section_key_from_filename(filename: str) -> Optional[str]:
    for key, value in CONFIG_SECTION_FILENAMES.items():
        if value == filename:
            return key
    return None


@app.command()
def experiments(
    output_dir: Path = typer.Option(
        Path("./experiments"),
        "--output",
        "-o",
        help="Directory containing experiment results",
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        help="Project name under the FluxLoop root",
    ),
    root: Path = typer.Option(
        Path(DEFAULT_ROOT_DIR_NAME),
        "--root",
        help="FluxLoop root directory",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        help="Number of experiments to show",
    ),
):
    """
    List recent experiments and their results.
    """
    resolved_output = resolve_project_relative(output_dir, project, root)

    if not resolved_output.exists():
        console.print(f"[yellow]No experiments found in:[/yellow] {resolved_output}")
        console.print("\nRun an experiment first: [cyan]fluxloop run experiment[/cyan]")
        return
    
    # Find experiment directories
    exp_dirs = sorted(
        [d for d in resolved_output.iterdir() if d.is_dir()],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )[:limit]
    
    if not exp_dirs:
        console.print("[yellow]No experiments found[/yellow]")
        return
    
    console.print(f"[bold]Recent Experiments[/bold] (showing {len(exp_dirs)} of {len(list(resolved_output.iterdir()))})\n")
    
    for exp_dir in exp_dirs:
        # Try to load summary
        summary_file = exp_dir / "summary.json"
        if summary_file.exists():
            import json
            summary = json.loads(summary_file.read_text())
            
            # Create mini table for each experiment
            exp_panel = Panel(
                f"[cyan]Name:[/cyan] {summary.get('name', 'Unknown')}\n"
                f"[cyan]Date:[/cyan] {summary.get('date', 'Unknown')}\n"
                f"[cyan]Runs:[/cyan] {summary.get('total_runs', 0)}\n"
                f"[cyan]Success Rate:[/cyan] {summary.get('success_rate', 0)*100:.1f}%\n"
                f"[cyan]Avg Duration:[/cyan] {summary.get('avg_duration_ms', 0):.0f}ms",
                title=f"[bold]{exp_dir.name}[/bold]",
                border_style="blue",
            )
            console.print(exp_panel)
        else:
            console.print(f"📁 {exp_dir.name} [dim](no summary available)[/dim]")
        
        console.print()  # Add spacing


@app.command()
def traces(
    experiment_id: Optional[str] = typer.Argument(
        None,
        help="Experiment ID to show traces for",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        help="Number of traces to show",
    ),
):
    """
    List recent traces from experiments.
    """
    # This would connect to the collector service
    console.print("[yellow]Trace viewing requires collector service[/yellow]")
    console.print("\nThis feature will be available when the collector is running.")
    console.print("For now, check the experiment output directories for trace data.")
