"""
Scenario management commands for FluxLoop CLI.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..api_utils import (
    handle_api_error,
    load_payload_file,
    resolve_api_url,
    save_cache_file,
)
from ..http_client import create_authenticated_client, post_with_retry
from ..context_manager import (
    get_current_project_id,
    get_current_scenario_id,
    set_scenario,
)

app = typer.Typer(help="Manage test scenarios")
console = Console()


@app.command()
def refine(
    scenario_id: str = typer.Option(..., "--scenario-id", help="Scenario ID to refine"),
    apply: bool = typer.Option(
        False, "--apply", help="Apply refinements to scenario"
    ),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Load payload from YAML or JSON file"
    ),
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="FluxLoop API base URL"
    ),
):
    """
    Refine scenario goal and constraints using AI.
    """
    api_url = resolve_api_url(api_url)

    # Build payload
    payload: Dict[str, Any] = {
        "scenario_id": scenario_id,
        "apply": apply,
    }

    # Override with file if provided
    if file:
        file_data = load_payload_file(file)
        payload.update(file_data)

    try:
        console.print("[cyan]Refining scenario...[/cyan]")

        client = create_authenticated_client(api_url, use_jwt=True)
        resp = post_with_retry(client, "/api/scenarios/refine", payload=payload)

        handle_api_error(resp, f"scenario {scenario_id}")

        data = resp.json()

        # Display results
        console.print()
        console.print("[green]✓[/green] Scenario refinement complete")

        if "goal" in data:
            console.print(f"\n[bold]Goal:[/bold] {data['goal']}")

        if "constraints" in data and data["constraints"]:
            console.print(f"\n[bold]Constraints:[/bold]")
            for constraint in data["constraints"]:
                console.print(f"  - {constraint}")

        # Save to cache
        cache_path = save_cache_file(
            "scenarios", f"{scenario_id}.yaml", data
        )
        console.print(f"\n[dim]Saved to: {cache_path}[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Refinement failed: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def create(
    name: str = typer.Option(..., "--name", help="Scenario name"),
    project_id: Optional[str] = typer.Option(
        None, "--project-id", help="Project ID (defaults to current context)"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", help="Scenario description"
    ),
    config_file: Optional[Path] = typer.Option(
        None, "--config-file", help="Path to config file for snapshot"
    ),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Load full payload from YAML or JSON file"
    ),
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="FluxLoop API base URL"
    ),
    select: bool = typer.Option(
        True, "--select/--no-select", help="Automatically select the created scenario"
    ),
):
    """
    Create a new test scenario.
    
    Uses current project from context if --project-id is not specified.
    """
    api_url = resolve_api_url(api_url)
    
    # Use context if no project_id specified
    if not project_id:
        project_id = get_current_project_id()
        if not project_id:
            console.print("[yellow]No project selected.[/yellow]")
            console.print("[dim]Select one with: fluxloop context set-project <id>[/dim]")
            raise typer.Exit(1)

    # Build payload
    payload: Dict[str, Any] = {
        "name": name,
        "project_id": project_id,
        "config_snapshot": {},  # Default empty snapshot (required by backend)
    }

    if description:
        payload["description"] = description

    if config_file:
        if not config_file.exists():
            raise typer.BadParameter(f"Config file not found: {config_file}")
        config_data = load_payload_file(config_file)
        payload["config_snapshot"] = config_data

    # Override with file if provided
    if file:
        file_data = load_payload_file(file)
        payload.update(file_data)

    try:
        console.print("[cyan]Creating scenario...[/cyan]")

        client = create_authenticated_client(api_url, use_jwt=True)
        resp = post_with_retry(client, "/api/scenarios", payload=payload)

        handle_api_error(resp, "scenario creation")

        data = resp.json()
        scenario_id = data.get('scenario_id', data.get('id', 'N/A'))
        scenario_name = data.get('name', name)

        console.print()
        console.print(
            f"[green]✓[/green] Scenario created: [bold]{scenario_id}[/bold]"
        )
        console.print(f"  Name: {scenario_name}")

        if "description" in data:
            console.print(f"  Description: {data['description']}")
        
        # Automatically select if requested
        if select and scenario_id != 'N/A':
            set_scenario(scenario_id, scenario_name)
            console.print(f"[green]✓[/green] Scenario selected as current context")

    except Exception as e:
        console.print(f"[red]✗[/red] Creation failed: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def generate(
    intent: Optional[str] = typer.Option(
        None, "--intent", help="User intent description"
    ),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Load payload from YAML or JSON file"
    ),
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="FluxLoop API base URL"
    ),
):
    """
    Generate scenario using Alignment Agent from user intent.
    """
    api_url = resolve_api_url(api_url)

    # Build payload
    payload: Dict[str, Any] = {}

    if intent:
        payload["intent"] = intent

    # Override with file if provided
    if file:
        file_data = load_payload_file(file)
        payload.update(file_data)

    if "intent" not in payload:
        raise typer.BadParameter("Either --intent or --file with 'intent' field is required")

    try:
        console.print("[cyan]Generating scenario from intent...[/cyan]")

        client = create_authenticated_client(api_url, use_jwt=True)
        resp = post_with_retry(client, "/api/scenarios/generate", payload=payload)

        handle_api_error(resp, "scenario generation")

        data = resp.json()

        console.print()
        console.print("[green]✓[/green] Scenario generated")

        if "scenario_id" in data:
            console.print(f"  Scenario ID: [bold]{data['scenario_id']}[/bold]")

        if "name" in data:
            console.print(f"  Name: {data['name']}")

        if "goal" in data:
            console.print(f"  Goal: {data['goal']}")

        if "constraints" in data and data["constraints"]:
            console.print(f"\n  Constraints:")
            for constraint in data["constraints"]:
                console.print(f"    - {constraint}")

    except Exception as e:
        console.print(f"[red]✗[/red] Generation failed: {e}", style="bold red")
        raise typer.Exit(1)


@app.command("list")
def list_scenarios(
    project_id: Optional[str] = typer.Option(
        None, "--project-id", help="Filter by project ID (defaults to current context)"
    ),
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="FluxLoop API base URL"
    ),
):
    """
    List all scenarios for a project.
    
    Uses current project from context if --project-id is not specified.
    """
    api_url = resolve_api_url(api_url)
    
    # Use context if no project_id specified
    if not project_id:
        project_id = get_current_project_id()
        if not project_id:
            console.print("[yellow]No project selected.[/yellow]")
            console.print("[dim]Select one with: fluxloop context set-project <id>[/dim]")
            raise typer.Exit(1)

    try:
        client = create_authenticated_client(api_url, use_jwt=True)

        # Build query params
        params = {"project_id": project_id}

        resp = client.get("/api/scenarios", params=params)
        handle_api_error(resp, "scenarios list")

        data = resp.json()
        scenarios = data if isinstance(data, list) else data.get("scenarios", [])
        
        # Get current scenario to mark selected
        current_scenario_id = get_current_scenario_id()

        if not scenarios:
            console.print("[yellow]No scenarios found.[/yellow]")
            console.print("[dim]Create one with: fluxloop scenarios create --name <name>[/dim]")
            return

        # Create table
        table = Table(title=f"Scenarios (Project: {project_id})")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Created", style="dim")
        table.add_column("Selected", style="green")

        for scenario in scenarios:
            scenario_id = scenario.get("id", scenario.get("scenario_id", "N/A"))
            is_selected = "✓" if scenario_id == current_scenario_id else ""
            table.add_row(
                scenario_id,
                scenario.get("name", "N/A"),
                scenario.get("created_at", "N/A"),
                is_selected,
            )

        console.print(table)
        console.print()
        console.print("[dim]Select a scenario: fluxloop context set-scenario <id>[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] List failed: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def show(
    scenario_id: str = typer.Option(..., "--scenario-id", help="Scenario ID to show"),
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="FluxLoop API base URL"
    ),
):
    """
    Show scenario details.
    """
    api_url = resolve_api_url(api_url)

    try:
        client = create_authenticated_client(api_url, use_jwt=True)
        resp = client.get(f"/api/scenarios/{scenario_id}")

        handle_api_error(resp, f"scenario {scenario_id}")

        data = resp.json()

        # Build panel content
        content_lines = []

        if "name" in data:
            content_lines.append(f"[bold]Name:[/bold] {data['name']}")

        if "goal" in data:
            content_lines.append(f"\n[bold]Goal:[/bold]\n{data['goal']}")

        if "constraints" in data and data["constraints"]:
            content_lines.append(f"\n[bold]Constraints:[/bold]")
            for constraint in data["constraints"]:
                content_lines.append(f"  - {constraint}")

        if "personas" in data and data["personas"]:
            content_lines.append(f"\n[bold]Personas:[/bold] {len(data['personas'])} configured")

        if "created_at" in data:
            content_lines.append(f"\n[dim]Created: {data['created_at']}[/dim]")

        panel = Panel(
            "\n".join(content_lines),
            title=f"[bold blue]Scenario: {scenario_id}[/bold blue]",
            border_style="blue",
        )

        console.print(panel)

    except Exception as e:
        console.print(f"[red]✗[/red] Show failed: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def update(
    scenario_id: str = typer.Option(..., "--scenario-id", help="Scenario ID to update"),
    file: Path = typer.Option(..., "--file", "-f", help="Load update payload from YAML or JSON file"),
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="FluxLoop API base URL"
    ),
):
    """
    Update scenario fields.
    """
    api_url = resolve_api_url(api_url)

    # Load payload from file
    payload = load_payload_file(file)

    try:
        console.print(f"[cyan]Updating scenario {scenario_id}...[/cyan]")

        client = create_authenticated_client(api_url, use_jwt=True)
        resp = client.patch(f"/api/scenarios/{scenario_id}", json=payload)

        handle_api_error(resp, f"scenario {scenario_id}")

        data = resp.json()

        console.print()
        console.print(f"[green]✓[/green] Scenario updated: [bold]{scenario_id}[/bold]")

        if "name" in data:
            console.print(f"  Name: {data['name']}")

    except Exception as e:
        console.print(f"[red]✗[/red] Update failed: {e}", style="bold red")
        raise typer.Exit(1)
