"""
Local context management commands for FluxLoop CLI.

v2 Architecture:
- .fluxloop/project.json: Web Project connection (use `fluxloop projects select`)
- .fluxloop/context.json: Current scenario pointer
"""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from ..context_manager import (
    load_context,
    clear_context,
    set_scenario,
    set_bundle,
    get_context_file_path,
    load_project_connection,
)
from ..http_client import create_authenticated_client
from ..api_utils import handle_api_error, resolve_api_url

app = typer.Typer(help="Manage local working context (scenario selection)")
console = Console()


@app.command("show")
def show_context():
    """
    Show current local context (Web Project, scenario, bundle, workflow state).
    """
    project_conn = load_project_connection()
    context = load_context()
    context_path = get_context_file_path()
    
    if not project_conn and (not context or not context.current_scenario):
        console.print("[yellow]No context set.[/yellow]")
        console.print(f"[dim]Context file: {context_path}[/dim]")
        console.print()
        console.print("[dim]Set context with:[/dim]")
        console.print("[dim]  fluxloop projects select <id>  - Select Web Project[/dim]")
        console.print("[dim]  fluxloop scenarios select <id> - Select Web Scenario[/dim]")
        return
    
    # Build display
    content_lines = []
    
    # Workflow State (if exists)
    if context and context.workflow_state:
        ws = context.workflow_state
        content_lines.append(f"[bold magenta]Workflow State:[/bold magenta]")
        content_lines.append(f"  Phase: [bold]{ws.phase}[/bold]")
        if ws.completed_steps:
            content_lines.append(f"  Completed: {', '.join(ws.completed_steps)}")
        if ws.last_action:
            content_lines.append(f"  Last action: [dim]{ws.last_action}[/dim]")
        content_lines.append("")
    
    # Web Project
    if project_conn:
        content_lines.append(f"[bold cyan]Web Project:[/bold cyan]")
        content_lines.append(f"  ID: [dim]{project_conn.project_id}[/dim]")
        content_lines.append(f"  Name: [bold]{project_conn.project_name}[/bold]")
        # Show description from resources if available
        if context and context.resources and context.resources.project:
            if context.resources.project.description:
                content_lines.append(f"  Desc: {context.resources.project.description}")
    
    # Scenario
    if context and context.current_scenario:
        content_lines.append(f"\n[bold cyan]Scenario:[/bold cyan]")
        content_lines.append(f"  ID: [dim]{context.current_scenario.id}[/dim]")
        content_lines.append(f"  Name: [bold]{context.current_scenario.name}[/bold]")
        if context.current_scenario.local_path:
            content_lines.append(f"  Local: [dim]{context.current_scenario.local_path}[/dim]")
        # Show description from resources if available
        if context.resources and context.resources.scenario:
            if context.resources.scenario.description:
                content_lines.append(f"  Desc: {context.resources.scenario.description}")
    
    # Input Set (from resources)
    if context and context.resources and context.resources.input_set:
        inp = context.resources.input_set
        content_lines.append(f"\n[bold cyan]Input Set:[/bold cyan]")
        content_lines.append(f"  ID: [dim]{inp.id}[/dim]")
        if inp.count is not None:
            content_lines.append(f"  Count: {inp.count}")
        if inp.tag:
            content_lines.append(f"  Tag: {inp.tag}")
    
    # Bundle
    if context and context.current_bundle:
        content_lines.append(f"\n[bold cyan]Bundle:[/bold cyan]")
        content_lines.append(f"  ID: [dim]{context.current_bundle.id}[/dim]")
        content_lines.append(f"  Version: {context.current_bundle.version}")
        # Show description from resources if available
        if context.resources and context.resources.bundle:
            if context.resources.bundle.description:
                content_lines.append(f"  Desc: {context.resources.bundle.description}")
    
    if context and context.last_updated:
        content_lines.append(f"\n[dim]Last updated: {context.last_updated}[/dim]")
    
    panel = Panel(
        "\n".join(content_lines),
        title="[bold blue]Current Context[/bold blue]",
        border_style="blue",
    )
    console.print(panel)
    console.print(f"[dim]Context file: {context_path}[/dim]")


@app.command("set-project", deprecated=True)
def set_project_cmd(
    project_id: str = typer.Argument(..., help="Project ID to select"),
):
    """
    [Deprecated] Use 'fluxloop projects select' instead.
    """
    console.print("[yellow]⚠ This command is deprecated.[/yellow]")
    console.print()
    console.print("Use instead:")
    console.print(f"  [green]fluxloop projects select {project_id}[/green]")
    raise typer.Exit(1)


@app.command("set-scenario", deprecated=True)
def set_scenario_cmd(
    scenario_id: str = typer.Argument(..., help="Scenario ID to select"),
):
    """
    [Deprecated] Use 'fluxloop scenarios select' instead.
    """
    console.print("[yellow]⚠ This command is deprecated.[/yellow]")
    console.print()
    console.print("Use instead:")
    console.print(f"  [green]fluxloop scenarios select {scenario_id}[/green]")
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
