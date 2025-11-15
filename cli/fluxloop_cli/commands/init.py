"""
Initialize command for creating new FluxLoop projects.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.tree import Tree

from ..templates import (
    create_project_config,
    create_input_config,
    create_simulation_config,
    create_evaluation_config,
    create_sample_agent,
    create_gitignore,
    create_env_file,
)
from ..project_paths import resolve_root_dir, resolve_project_dir
from ..constants import (
    DEFAULT_ROOT_DIR_NAME,
    CONFIG_DIRECTORY_NAME,
    CONFIG_SECTION_FILENAMES,
    CONFIG_SECTION_ORDER,
)

app = typer.Typer()
console = Console()


@app.command()
def project(
    path: Path = typer.Argument(
        Path(DEFAULT_ROOT_DIR_NAME),
        help="Root directory for FluxLoop projects",
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Project name",
    ),
    with_example: bool = typer.Option(
        True,
        "--with-example/--no-example",
        help="Include example agent",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files",
    ),
):
    """
    Initialize a new FluxLoop project.
    
    This command creates:
    - configs/: Separated configuration files (project/input/simulation/evaluation)
    - .env: Environment variables template
    - examples/: Sample agent code (optional)
    """
    # Resolve path
    root_dir = resolve_root_dir(path)

    if not root_dir.exists():
        console.print(f"[dim]Creating FluxLoop root directory at {root_dir}[/dim]")
        root_dir.mkdir(parents=True, exist_ok=True)

    if not name:
        current = Path.cwd()
        if current.parent == root_dir:
            project_name = current.name
        else:
            console.print(
                "[red]Error:[/red] Project name must be provided when running outside the FluxLoop root directory."
            )
            raise typer.Exit(1)
    else:
        project_name = name
    project_path = resolve_project_dir(project_name, root_dir)

    console.print(f"\n[bold blue]Initializing FluxLoop project:[/bold blue] {project_name}")
    console.print(f"[dim]Location: {project_path}[/dim]\n")
    
    console.print(f"\n[bold blue]Initializing FluxLoop project:[/bold blue] {project_name}")
    console.print(f"[dim]Location: {project_path}[/dim]\n")
    
    # Check if directory exists
    if not project_path.exists():
        if Confirm.ask(f"Directory {project_path} doesn't exist. Create it?"):
            project_path.mkdir(parents=True)
        else:
            raise typer.Abort()
    
    # Check for existing files
    config_dir = project_path / CONFIG_DIRECTORY_NAME
    section_paths = {
        key: config_dir / CONFIG_SECTION_FILENAMES[key]
        for key in CONFIG_SECTION_FILENAMES
    }
    env_file = project_path / ".env"
    gitignore_file = project_path / ".gitignore"
    
    if not force:
        existing_files = []
        for key in CONFIG_SECTION_ORDER:
            path = section_paths[key]
            if path.exists():
                existing_files.append(path.relative_to(project_path).as_posix())
        if env_file.exists():
            existing_files.append(".env")
        
        if existing_files:
            console.print(
                f"[yellow]Warning:[/yellow] The following files already exist: {', '.join(existing_files)}"
            )
            if not Confirm.ask("Overwrite existing files?", default=False):
                raise typer.Abort()
    
    # Create configuration files
    console.print("📝 Creating configuration files...")
    config_dir.mkdir(exist_ok=True)

    section_writers = {
        "project": lambda: create_project_config(project_name),
        "input": create_input_config,
        "simulation": lambda: create_simulation_config(project_name),
        "evaluation": create_evaluation_config,
    }

    for key in CONFIG_SECTION_ORDER:
        content = section_writers[key]()  # type: ignore[operator]
        section_path = section_paths[key]
        section_path.write_text(content)
    
    # Create project .env (single source of truth)
    console.print("🔐 Creating project .env...")
    recordings_dir = project_path / "recordings"
    recordings_dir.mkdir(exist_ok=True)
    env_file.write_text(create_env_file())
    
    # Update .gitignore
    if not gitignore_file.exists():
        console.print("📄 Creating .gitignore...")
        gitignore_content = create_gitignore()
        gitignore_file.write_text(gitignore_content)
    
    # Create example agent if requested
    if with_example:
        console.print("🤖 Creating example agent...")
        examples_dir = project_path / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        agent_file = examples_dir / "simple_agent.py"
        agent_content = create_sample_agent()
        agent_file.write_text(agent_content)
    
    # Display created structure
    console.print("\n[bold green]✓ Project initialized successfully![/bold green]\n")
    
    tree = Tree(f"[bold]{project_name}/[/bold]")
    configs_node = tree.add(f"📁 {CONFIG_DIRECTORY_NAME}/")
    for key in CONFIG_SECTION_ORDER:
        configs_node.add(f"📄 {CONFIG_SECTION_FILENAMES[key]}")
    tree.add("🔐 .env")
    tree.add("📄 .gitignore")
    tree.add("📁 recordings/")
    
    if with_example:
        examples_tree = tree.add("📁 examples/")
        examples_tree.add("🐍 simple_agent.py")
    
    console.print(tree)
    
    # Show next steps
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Review configs in [cyan]configs/[/cyan] (project/input/simulation/evaluation)")
    console.print("2. Configure secrets via [cyan].env[/cyan] or [green]fluxloop config set-llm[/green]")
    if with_example:
        console.print("3. Customize the sample agent in [cyan]examples/simple_agent.py[/cyan]")
    else:
        console.print("3. Create your agent: [green]fluxloop init agent <name>[/green]")
    console.print("4. Generate inputs: [green]fluxloop generate inputs[/green]")
    console.print("5. Run the experiment: [green]fluxloop run experiment[/green]")
    console.print("6. Parse outputs: [green]fluxloop parse experiment[/green]")
    console.print("7. Evaluate results (optional): [green]fluxloop evaluate experiment[/green]")
    console.print("8. Diagnose environment anytime: [green]fluxloop doctor[/green]")


@app.command()
def agent(
    name: str = typer.Argument(
        ...,
        help="Name of the agent module",
    ),
    path: Path = typer.Option(
        Path.cwd(),
        "--path",
        "-p",
        help="Directory to create the agent in",
    ),
    template: str = typer.Option(
        "simple",
        "--template",
        "-t",
        help="Agent template to use (simple, langchain, langgraph)",
    ),
):
    """
    Create a new agent from a template.
    """
    # Validate template
    valid_templates = ["simple", "langchain", "langgraph"]
    if template not in valid_templates:
        console.print(
            f"[red]Error:[/red] Invalid template '{template}'. "
            f"Choose from: {', '.join(valid_templates)}"
        )
        raise typer.Exit(1)
    
    # Create agent file
    agent_dir = path / "agents"
    agent_dir.mkdir(exist_ok=True)
    
    agent_file = agent_dir / f"{name}.py"
    
    if agent_file.exists():
        if not Confirm.ask(f"Agent {name}.py already exists. Overwrite?", default=False):
            raise typer.Abort()
    
    # Create agent based on template
    console.print(f"🤖 Creating {template} agent: {name}")
    
    if template == "simple":
        content = create_sample_agent()
    else:
        # TODO: Add more templates
        content = create_sample_agent()
    
    agent_file.write_text(content)
    
    console.print(f"[green]✓[/green] Agent created: {agent_file}")
    console.print("\nTo use this agent, update your setting.yaml:")
    console.print(f"  runner.module_path: agents.{name}")
    console.print("  runner.function_name: run")
