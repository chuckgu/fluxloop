"""
Criteria commands for listing evaluation criteria bundles.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console

from ..config_loader import load_project_config
from ..constants import DEFAULT_CONFIG_PATH, DEFAULT_ROOT_DIR_NAME


app = typer.Typer(help="Inspect pulled evaluation criteria.")
console = Console()


@app.command()
def show(
    config_file: Path = typer.Option(
        DEFAULT_CONFIG_PATH, "--config", "-c", help="Config file to resolve project root"
    ),
    project: Optional[str] = typer.Option(None, "--project", help="Project name"),
    root: Path = typer.Option(Path(DEFAULT_ROOT_DIR_NAME), "--root", help="Root dir"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed criteria"),
):
    """
    Show locally cached evaluation criteria.
    """
    _, project_root = load_project_config(config_file, project=project, root=root)
    criteria_dir = project_root / ".fluxloop" / "criteria"

    if not criteria_dir.exists():
        console.print("[yellow]No criteria found. Run 'fluxloop sync pull' first.[/yellow]")
        raise typer.Exit(0)

    for criteria_file in sorted(criteria_dir.glob("*.yaml")):
        payload = yaml.safe_load(criteria_file.read_text()) or {}
        if not isinstance(payload, dict):
            continue
        name = payload.get("name") or criteria_file.stem
        version = payload.get("version") or "N/A"
        console.print(f"\n[bold]{name}[/bold] (v{version})")
        items = payload.get("items") or []
        if items:
            console.print("  [dim]Items:[/dim]")
            for item in items:
                console.print(f"  - {item}")
        if verbose and payload.get("details"):
            console.print("  [dim]Details:[/dim]")
            for detail in payload.get("details") or []:
                priority = detail.get("priority", "optional")
                desc = detail.get("description", "")
                console.print(f"  [{priority}] {desc}")
