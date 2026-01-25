"""
Local context management commands for FluxLoop CLI.

Manages the current working context (project, scenario) stored in .fluxloop/context.json.
"""

import os
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..context_manager import (
    load_context,
    save_context,
    clear_context,
    set_project,
    set_scenario,
    set_bundle,
    get_context_file_path,
    LocalContext,
)
from ..http_client import create_authenticated_client
from ..api_utils import handle_api_error, resolve_api_url

app = typer.Typer(help="Manage local working context (project/scenario selection)")
console = Console()


@app.command("show")
def show_context():
    """
    Show current local context (selected project, scenario, bundle).
    """
    context = load_context()
    context_path = get_context_file_path()
    
    if not context or (not context.current_project and not context.current_scenario):
        console.print("[yellow]No context set.[/yellow]")
        console.print(f"[dim]Context file: {context_path}[/dim]")
        console.print()
        console.print("[dim]Set context with:[/dim]")
        console.print("[dim]  fluxloop context set-project <id>[/dim]")
        console.print("[dim]  fluxloop context set-scenario <id>[/dim]")
        return
    
    # Build display
    content_lines = []
    
    if context.current_project:
        content_lines.append(f"[bold cyan]Project:[/bold cyan]")
        content_lines.append(f"  ID: [dim]{context.current_project.id}[/dim]")
        content_lines.append(f"  Name: [bold]{context.current_project.name}[/bold]")
    
    if context.current_scenario:
        content_lines.append(f"\n[bold cyan]Scenario:[/bold cyan]")
        content_lines.append(f"  ID: [dim]{context.current_scenario.id}[/dim]")
        content_lines.append(f"  Name: [bold]{context.current_scenario.name}[/bold]")
    
    if context.current_bundle:
        content_lines.append(f"\n[bold cyan]Bundle:[/bold cyan]")
        content_lines.append(f"  ID: [dim]{context.current_bundle.id}[/dim]")
        content_lines.append(f"  Version: {context.current_bundle.version}")
    
    if context.last_updated:
        content_lines.append(f"\n[dim]Last updated: {context.last_updated}[/dim]")
    
    panel = Panel(
        "\n".join(content_lines),
        title="[bold blue]Current Context[/bold blue]",
        border_style="blue",
    )
    console.print(panel)
    console.print(f"[dim]Context file: {context_path}[/dim]")


@app.command("set-project")
def set_project_cmd(
    project_id: str = typer.Argument(..., help="Project ID to select"),
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="FluxLoop API base URL"
    ),
):
    """
    Set the current project in local context.
    
    This also clears the current scenario and bundle.
    """
    api_url = resolve_api_url(api_url)
    
    try:
        # Verify project exists by fetching it
        client = create_authenticated_client(api_url, use_jwt=True)
        resp = client.get(f"/api/projects/{project_id}")
        handle_api_error(resp, "get project")
        
        data = resp.json()
        project_name = data.get("name", data.get("project_name", project_id))
        
        # Set context
        context = set_project(project_id, project_name)
        
        console.print(f"[green]✓[/green] Project set: {project_name} ([dim]{project_id}[/dim])")
        
        if context.current_scenario is None:
            console.print("[dim]Scenario cleared. Select one with: fluxloop scenarios list[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to set project: {e}", style="bold red")
        raise typer.Exit(1)


@app.command("set-scenario")
def set_scenario_cmd(
    scenario_id: str = typer.Argument(..., help="Scenario ID to select"),
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="FluxLoop API base URL"
    ),
):
    """
    Set the current scenario in local context.
    
    This also clears the current bundle.
    """
    api_url = resolve_api_url(api_url)
    
    try:
        # Verify scenario exists by fetching it
        client = create_authenticated_client(api_url, use_jwt=True)
        resp = client.get(f"/api/scenarios/{scenario_id}")
        handle_api_error(resp, "get scenario")
        
        data = resp.json()
        scenario_name = data.get("name", data.get("scenario_name", scenario_id))
        
        # Set context
        context = set_scenario(scenario_id, scenario_name)
        
        console.print(f"[green]✓[/green] Scenario set: {scenario_name} ([dim]{scenario_id}[/dim])")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to set scenario: {e}", style="bold red")
        raise typer.Exit(1)


@app.command("set-bundle")
def set_bundle_cmd(
    bundle_id: str = typer.Argument(..., help="Bundle ID to select"),
    version: str = typer.Option("latest", "--version", "-v", help="Bundle version"),
):
    """
    Set the current bundle in local context.
    """
    try:
        set_bundle(bundle_id, version)
        console.print(f"[green]✓[/green] Bundle set: {bundle_id} (version: {version})")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to set bundle: {e}", style="bold red")
        raise typer.Exit(1)


@app.command("clear")
def clear_context_cmd():
    """
    Clear all local context (project, scenario, bundle).
    """
    clear_context()
    console.print("[green]✓[/green] Context cleared")
    console.print("[dim]Run [bold]fluxloop projects list[/bold] to see your projects.[/dim]")
