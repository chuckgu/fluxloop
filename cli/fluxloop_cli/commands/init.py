"""
Initialize command for creating new FluxLoop scenarios.

Architecture:
- `fluxloop init scenario --name xxx` creates .fluxloop/scenarios/xxx/

Web ↔ Local Mapping:
- Web Project ← .fluxloop/ (workspace)
- Web Scenario ← .fluxloop/scenarios/{name}/ (scenario folder)
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.tree import Tree

from ..templates import (
    create_input_config,
    create_simulation_config,
    create_env_file,
    create_pytest_bridge_template,
    create_agent_wrapper_template,
    create_agents_readme,
)
from ..context_manager import (
    ensure_fluxloop_dir,
    ensure_scenarios_dir,
    set_scenario,
    load_project_connection,
)
from ..constants import (
    CONFIG_DIRECTORY_NAME,
    CONFIG_SECTION_FILENAMES,
    SCENARIOS_DIR_NAME,
    STATE_DIR_NAME,
    SCENARIO_CONFIG_FILENAME,
)

app = typer.Typer()
console = Console()


@app.command()
def scenario(
    name: str = typer.Argument(
        ...,
        help="Scenario name (will create .fluxloop/scenarios/{name}/)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files",
    ),
    link: Optional[str] = typer.Option(
        None,
        "--link",
        help="Link to existing Web Scenario ID",
    ),
    create_remote: bool = typer.Option(
        False,
        "--create-remote",
        help="Also create Scenario on the Web (requires login and project selection)",
    ),
):
    """
    Initialize a new FluxLoop scenario.
    
    Creates the scenario folder structure at .fluxloop/scenarios/{name}/:
    - configs/: Configuration files (scenario/input/simulation)
    - agents/: Agent code
    - inputs/: Input data
    - experiments/: Test results
    - .state/: Sync state (created on first sync)
    
    Web Mapping:
    - This local scenario maps to a Web Scenario
    - Use --link to connect to an existing Web Scenario
    - Use --create-remote to create a new Web Scenario
    """
    # Ensure workspace exists
    ensure_fluxloop_dir()
    scenarios_dir = ensure_scenarios_dir()
    
    scenario_path = scenarios_dir / name

    console.print(f"\n[bold blue]Initializing FluxLoop scenario:[/bold blue] {name}")
    console.print(f"[dim]Location: {scenario_path}[/dim]")
    print(f"SCENARIO_PATH: {scenario_path}")
    
    # Check if directory exists
    if scenario_path.exists() and not force:
        console.print(f"[yellow]Warning:[/yellow] Scenario '{name}' already exists.")
        if not Confirm.ask("Overwrite existing files?", default=False):
            raise typer.Abort()
    
    scenario_path.mkdir(parents=True, exist_ok=True)
    
    # Create config directory and files
    config_dir = scenario_path / CONFIG_DIRECTORY_NAME
    config_dir.mkdir(exist_ok=True)

    console.print("\n📝 Creating configuration files...")
    
    # Create scenario.yaml
    scenario_config_path = config_dir / SCENARIO_CONFIG_FILENAME
    scenario_config_content = _create_scenario_config(name)
    scenario_config_path.write_text(scenario_config_content)
    console.print(f"  [green]✓[/green] {SCENARIO_CONFIG_FILENAME}")
    
    # Create other config files
    (config_dir / "input.yaml").write_text(create_input_config())
    console.print("  [green]✓[/green] input.yaml")
    
    (config_dir / "simulation.yaml").write_text(create_simulation_config(name))
    console.print("  [green]✓[/green] simulation.yaml")
    
    # Create .env
    env_file = scenario_path / ".env"
    env_file.write_text(create_env_file())
    console.print("  [green]✓[/green] .env")
    
    # Create agents directory
    agents_dir = scenario_path / "agents"
    agents_dir.mkdir(exist_ok=True)
    (agents_dir / "__init__.py").write_text('"""FluxLoop agent wrappers."""\n')
    (agents_dir / "_template_wrapper.py").write_text(create_agent_wrapper_template())
    (agents_dir / "README.md").write_text(create_agents_readme())
    console.print("  [green]✓[/green] agents/")
    
    # Create other directories
    (scenario_path / "inputs").mkdir(exist_ok=True)
    (scenario_path / "experiments").mkdir(exist_ok=True)
    # Note: recordings/ is created on-demand when recording is enabled
    
    # Handle Web Scenario linking/creation
    scenario_id = None
    if link:
        # Link to existing Web Scenario
        scenario_id = link
        set_scenario(scenario_id, name, f"{SCENARIOS_DIR_NAME}/{name}")
        console.print(f"\n[green]✓[/green] Linked to Web Scenario: {scenario_id}")
        print(f"SCENARIO_LINKED: {scenario_id}")
    elif create_remote:
        # Create Web Scenario (requires login and project selection)
        project_conn = load_project_connection()
        if not project_conn:
            console.print("\n[yellow]Warning:[/yellow] No Web Project selected.")
            console.print("[dim]Run 'fluxloop projects select' first to create remote scenario.[/dim]")
        else:
            console.print(f"\n[dim]Creating Web Scenario in project: {project_conn.project_name}...[/dim]")
            console.print("[yellow]Note:[/yellow] Remote creation not yet implemented.")
            console.print(f"[dim]Run 'fluxloop scenarios create --name {name}' manually.[/dim]")
    
    # Display created structure
    console.print("\n[bold green]✓ Scenario initialized successfully![/bold green]")
    print(f"SCENARIO_CREATED: {name}")
    
    tree = Tree(f"[bold].fluxloop/scenarios/{name}/[/bold]")
    configs_node = tree.add("📁 configs/")
    configs_node.add(f"📄 {SCENARIO_CONFIG_FILENAME}")
    configs_node.add("📄 input.yaml")
    configs_node.add("📄 simulation.yaml")
    
    agents_node = tree.add("📁 agents/")
    agents_node.add("📄 _template_wrapper.py")
    
    tree.add("📁 inputs/")
    tree.add("📁 experiments/")
    tree.add("🔐 .env")
    
    console.print(tree)
    
    # Show next steps
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"1. cd [cyan].fluxloop/scenarios/{name}[/cyan]")
    console.print("2. Configure your agent in [cyan]configs/simulation.yaml[/cyan]")
    console.print("3. Add test inputs: [green]fluxloop sync pull[/green] or edit [cyan]inputs/[/cyan]")
    console.print("4. Run tests: [green]fluxloop test[/green]")
    
    if not link and not create_remote:
        console.print("\n[dim]To connect to Web:[/dim]")
        console.print("  • [green]fluxloop projects select[/green] - Select a Web Project")
        console.print(f"  • [green]fluxloop scenarios create --name {name}[/green] - Create Web Scenario")


def _create_scenario_config(scenario_name: str) -> str:
    """Create scenario.yaml content."""
    return f'''# FluxLoop Scenario Configuration
# ------------------------------------------------------------
# Describes this scenario's metadata and settings.
# Maps to a Web Scenario in FluxLoop.
name: {scenario_name}
description: AI agent test scenario
version: 1.0.0

# Source root for the agent code (relative to this scenario)
source_root: ""

# Optional collector settings (leave null if using offline mode only)
collector_url: null
collector_api_key: null

# Tags and metadata for categorization
tags:
  - simulation
  - testing

metadata:
  team: development
  environment: local
  service_context: ""
'''


@app.command("pytest-template")
def pytest_template(
    scenario_root: Path = typer.Argument(
        Path.cwd(),
        help="Scenario root containing configs/",
    ),
    tests_dir: str = typer.Option(
        "tests",
        "--tests-dir",
        help="Directory (relative to scenario root) where tests live",
    ),
    filename: str = typer.Option(
        "test_fluxloop_smoke.py",
        "--filename",
        help="Test file name to create inside the tests directory",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing template without confirmation",
    ),
) -> None:
    """Scaffold a pytest smoke test that uses the FluxLoop runner fixtures."""
    root_path = scenario_root.expanduser().resolve()
    if not root_path.exists():
        console.print(f"[red]Error:[/red] Scenario root {root_path} does not exist.")
        raise typer.Exit(1)

    tests_path = (root_path / tests_dir).resolve()
    tests_path.mkdir(parents=True, exist_ok=True)

    target_file = tests_path / filename

    if target_file.exists() and not force:
        if not Confirm.ask(f"{target_file} already exists. Overwrite?", default=False):
            raise typer.Abort()

    configs_sim = root_path / CONFIG_DIRECTORY_NAME / CONFIG_SECTION_FILENAMES["simulation"]

    if configs_sim.exists():
        relative_config = configs_sim.relative_to(root_path).as_posix()
    else:
        relative_config = f"{CONFIG_DIRECTORY_NAME}/{CONFIG_SECTION_FILENAMES['simulation']}"
        console.print(
            "[yellow]Warning:[/yellow] Could not find configs/simulation.yaml. "
            "Template will reference the default simulation path."
        )

    template_content = create_pytest_bridge_template(relative_config)
    target_file.write_text(template_content, encoding="utf-8")

    console.print(
        f"[green]✓[/green] Pytest template created at [cyan]{target_file}[/cyan]. "
        "Run [bold]pytest -k fluxloop_smoke[/bold] to execute the sample test."
    )


