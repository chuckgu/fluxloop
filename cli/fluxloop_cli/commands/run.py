"""
Run command for executing experiments and simulations.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table

from ..runner import ExperimentRunner
from ..config_loader import load_experiment_config
from ..constants import DEFAULT_CONFIG_PATH, DEFAULT_ROOT_DIR_NAME
from ..project_paths import (
    resolve_config_path,
    resolve_project_relative,
)
from fluxloop.schemas import MultiTurnConfig

app = typer.Typer()
console = Console()


@app.command()
def experiment(
    config_file: Path = typer.Option(
        DEFAULT_CONFIG_PATH,
        "--config",
        "-c",
        help="Path to experiment configuration file",
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
    iterations: Optional[int] = typer.Option(
        None,
        "--iterations",
        "-i",
        help="Override number of iterations",
    ),
    personas: Optional[str] = typer.Option(
        None,
        "--personas",
        "-p",
        help="Comma-separated list of personas to use",
    ),
    multi_turn: Optional[bool] = typer.Option(
        None,
        "--multi-turn/--no-multi-turn",
        help="Enable or disable multi-turn supervisor loop",
    ),
    max_turns: Optional[int] = typer.Option(
        None,
        "--max-turns",
        help="Override maximum number of turns per conversation",
    ),
    auto_approve_tools: Optional[bool] = typer.Option(
        None,
        "--auto-approve-tools/--manual-approve-tools",
        help="Override automatic tool approval behaviour",
    ),
    persona_override: Optional[str] = typer.Option(
        None,
        "--persona-override",
        help="Force a specific persona id during multi-turn execution",
    ),
    supervisor_provider: Optional[str] = typer.Option(
        None,
        "--supervisor-provider",
        help="Override conversation supervisor provider (e.g. openai, mock)",
    ),
    supervisor_model: Optional[str] = typer.Option(
        None,
        "--supervisor-model",
        help="Override conversation supervisor model identifier",
    ),
    supervisor_temperature: Optional[float] = typer.Option(
        None,
        "--supervisor-temperature",
        help="Override conversation supervisor sampling temperature",
    ),
    supervisor_api_key: Optional[str] = typer.Option(
        None,
        "--supervisor-api-key",
        help="API key to use for supervisor calls (overrides environment)",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Override output directory",
    ),
    no_collector: bool = typer.Option(
        False,
        "--no-collector",
        help="Run without sending data to collector",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be run without executing",
    ),
):
    """
    Run an experiment based on configuration file.
    
    This command:
    - Loads experiment configuration
    - Generates prompt variations
    - Runs agent with each variation
    - Collects traces and metrics
    - Generates summary report
    """
    # Check if config file exists
    resolved_config = resolve_config_path(config_file, project, root)
    if not resolved_config.exists():
        console.print(f"[red]Error:[/red] Configuration file not found: {config_file}")
        console.print("\nRun [cyan]fluxloop init project[/cyan] to create a configuration file.")
        raise typer.Exit(1)
    
    # Load configuration
    console.print(f"📋 Loading configuration from: [cyan]{resolved_config}[/cyan]")
    
    try:
        config = load_experiment_config(
            resolved_config,
            project=project,
            root=root,
        )
    except Exception as e:
        console.print(f"[red]Error loading configuration:[/red] {e}")
        raise typer.Exit(1)
    
    # Override configuration if needed
    if iterations is not None:
        config.iterations = iterations
    
    if personas:
        persona_list = [p.strip() for p in personas.split(",")]
        config.personas = [p for p in config.personas if p.name in persona_list]
    
    if output_dir:
        resolved_output = resolve_project_relative(output_dir, project, root)
        config.output_directory = str(resolved_output)

    if any(
        value is not None
        for value in [
            multi_turn,
            max_turns,
            auto_approve_tools,
            persona_override,
            supervisor_provider,
            supervisor_model,
            supervisor_temperature,
            supervisor_api_key,
        ]
    ):
        if config.multi_turn is None:
            config.multi_turn = MultiTurnConfig()
        mt = config.multi_turn
        if multi_turn is not None:
            mt.enabled = multi_turn
        if max_turns is not None:
            mt.max_turns = max_turns
        if auto_approve_tools is not None:
            mt.auto_approve_tools = auto_approve_tools
        if persona_override:
            mt.persona_override = persona_override
        if supervisor_provider:
            mt.supervisor.provider = supervisor_provider
        if supervisor_model:
            mt.supervisor.model = supervisor_model
        if supervisor_temperature is not None:
            mt.supervisor.temperature = supervisor_temperature
        if supervisor_api_key:
            mt.supervisor.api_key = supervisor_api_key
    
    # Load inputs to ensure accurate counts before showing the summary
    try:
        runner = ExperimentRunner(config, no_collector=no_collector)
        loaded_inputs = asyncio.run(runner._load_inputs())  # type: ignore[attr-defined]
    except Exception as e:
        console.print(f"[red]Error preparing inputs:[/red] {e}")
        raise typer.Exit(1)

    config.set_resolved_input_count(len(loaded_inputs))
    total_runs = config.estimate_total_runs()
    
    summary = Table(title="Experiment Summary", show_header=False)
    summary.add_column("Property", style="cyan")
    summary.add_column("Value", style="white")
    
    summary.add_row("Name", config.name)
    summary.add_row("Iterations", str(config.iterations))
    summary.add_row("Personas", str(len(config.personas)))
    summary.add_row(
        "Input Source",
        "external file" if config.has_external_inputs() else "base_inputs",
    )
    if config.multi_turn:
        summary.add_row(
            "Multi-turn",
            "enabled" if config.multi_turn.enabled else "disabled",
        )
        summary.add_row("Max Turns", str(config.multi_turn.max_turns))
        if config.multi_turn.persona_override:
            summary.add_row("Persona Override", config.multi_turn.persona_override)
        summary.add_row(
            "Supervisor Model",
            config.multi_turn.supervisor.model,
        )
    summary.add_row("Total Runs", str(total_runs))
    summary.add_row("Output", config.output_directory)
    
    console.print(summary)
    
    if dry_run:
        console.print("\n[yellow]Dry run mode - no execution will occur[/yellow]")
        return
    
    # Confirm execution
    if total_runs > 100:
        console.print(
            f"\n[yellow]Warning:[/yellow] This will execute {total_runs} runs. "
            "This may take a while and incur API costs."
        )
    else:
        console.print(
            f"\nThis will execute {total_runs} runs."
        )

    if not typer.confirm("Continue?"):
        raise typer.Abort()
    
    # Create runner
    # Run experiment with progress tracking
    console.print("\n[bold green]▶️ Starting experiment...[/bold green]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TextColumn("({task.completed} of {task.total})"),
        console=console,
    ) as progress:
        # Create main task
        main_task = progress.add_task(
            f"Running {config.name}",
            total=total_runs,
        )
        multi_turn_total = (
            config.multi_turn.max_turns
            if config.multi_turn and config.multi_turn.max_turns
            else None
        )
        turn_task = progress.add_task(
            "[cyan]Turn 0/0",
            total=multi_turn_total or 1,
            visible=False,
        )

        def _progress_callback():
            progress.advance(main_task)

        def _turn_progress_callback(
            current_turn: int,
            total_turns: int,
            message: Optional[str] = None,
        ) -> None:
            total = total_turns or 1
            clamped_turn = max(0, current_turn)
            if message is None:
                completed = min(clamped_turn, total)
                description = f"[cyan]Turn {min(clamped_turn, total)}/{total}: complete"
                progress.update(
                    turn_task,
                    total=total,
                    completed=completed,
                    description=description,
                    visible=False,
                )
                return

            if not progress.tasks[turn_task].visible:
                progress.update(turn_task, visible=True)

            preview = message.replace("\n", " ")
            if len(preview) > 40:
                preview = preview[:37] + "..."

            completed = max(0, min(clamped_turn - 1, total))
            description = f"[cyan]Turn {min(clamped_turn, total)}/{total}: {preview}"

            progress.update(
                turn_task,
                total=total,
                completed=completed,
                description=description,
            )

        # Run experiment
        try:
            results = asyncio.run(
                runner.run_experiment(
                    progress_callback=_progress_callback,
                    turn_progress_callback=_turn_progress_callback,
                )
            )
        except KeyboardInterrupt:
            console.print("\n[yellow]Experiment interrupted by user[/yellow]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"\n[red]Error during experiment:[/red] {e}")
            # Debug mode - show full traceback
            if "--debug" in sys.argv:
                console.print_exception()
            raise typer.Exit(1)
    
    config.set_resolved_input_count(results.get("input_count", config.get_input_count()))

    input_total_runs = config.estimate_total_runs()

    if input_total_runs != total_runs:
        console.print(
            f"\n[yellow]Notice:[/yellow] Effective total runs adjusted to {input_total_runs} "
            "after loading inputs."
        )

    _display_results(results)


@app.command()
def single(
    agent_path: str = typer.Argument(
        ...,
        help="Module path to agent (e.g., my_agent.main)",
    ),
    input_text: str = typer.Argument(
        ...,
        help="Input text for the agent",
    ),
    function_name: str = typer.Option(
        "run",
        "--function",
        "-f",
        help="Function name to call",
    ),
    trace_name: Optional[str] = typer.Option(
        None,
        "--trace-name",
        help="Name for the trace",
    ),
    no_collector: bool = typer.Option(
        False,
        "--no-collector",
        help="Run without sending data to collector",
    ),
):
    """
    Run a single agent execution.
    
    Quick way to test an agent without a full experiment configuration.
    """
    console.print(f"🤖 Running agent: [cyan]{agent_path}.{function_name}[/cyan]")
    console.print(f"📝 Input: {input_text[:100]}{'...' if len(input_text) > 100 else ''}")
    
    # Create minimal runner
    from ..runner import SingleRunner
    
    runner = SingleRunner(
        module_path=agent_path,
        function_name=function_name,
        trace_name=trace_name or f"single_{agent_path}",
        no_collector=no_collector,
    )
    
    # Run agent
    console.print("\n[bold]Executing...[/bold]\n")
    
    try:
        result = asyncio.run(runner.run(input_text))
        
        console.print(Panel(
            str(result),
            title="[bold green]Result[/bold green]",
            border_style="green",
        ))
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        # Debug mode - show full traceback
        if "--debug" in sys.argv:
            console.print_exception()
        raise typer.Exit(1)


def _display_results(results: dict):
    """Display experiment results."""
    console.print("\n" + "="*50)
    console.print("[bold green]Experiment Complete![/bold green]")
    console.print("="*50 + "\n")
    
    # Create results table
    table = Table(title="Results Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    # Add metrics
    table.add_row("Total Runs", str(results.get("total_runs", 0)))
    table.add_row("Successful", str(results.get("successful", 0)))
    table.add_row("Failed", str(results.get("failed", 0)))
    
    success_rate = results.get("success_rate", 0) * 100
    table.add_row("Success Rate", f"{success_rate:.1f}%")
    
    avg_duration = results.get("avg_duration_ms", 0)
    table.add_row("Avg Duration", f"{avg_duration:.0f}ms")
    
    console.print(table)
    
    # Show output location
    if results.get("output_dir"):
        console.print(f"\n📁 Results saved to: [cyan]{results['output_dir']}[/cyan]")
    
    # Show trace URLs if available
    if results.get("trace_urls"):
        console.print("\n🔗 View traces:")
        for url in results["trace_urls"][:5]:  # Show first 5
            console.print(f"   {url}")
        if len(results["trace_urls"]) > 5:
            console.print(f"   ... and {len(results['trace_urls']) - 5} more")
