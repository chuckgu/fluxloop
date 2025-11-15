"""Record command for managing argument recording mode."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import typer
from rich.console import Console
from rich.table import Table
from ruamel.yaml import YAML, CommentedMap

from ..constants import DEFAULT_ROOT_DIR_NAME
from ..project_paths import (
    resolve_env_path,
    resolve_project_dir,
    resolve_config_section_path,
)
from ..config_schema import CONFIG_SECTION_FILENAMES


app = typer.Typer()
console = Console()
_yaml = YAML()
_yaml.indent(mapping=2, sequence=4, offset=2)
_yaml.preserve_quotes = True


def _load_env(env_path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def _write_env(env_path: Path, values: Dict[str, str]) -> None:
    env_path.write_text("\n".join(f"{k}={v}" for k, v in values.items()) + "\n")


def _update_simulation(recording_enabled: bool, project: Optional[str], root: Path) -> None:
    try:
        simulation_path = resolve_config_section_path("simulation", project, root)
    except KeyError:
        return

    if simulation_path.exists():
        with simulation_path.open("r", encoding="utf-8") as handle:
            loaded = _yaml.load(handle) or CommentedMap()
    else:
        loaded = CommentedMap()

    if not isinstance(loaded, CommentedMap):
        loaded = CommentedMap(loaded)

    replay = loaded.get("replay_args")
    if not isinstance(replay, CommentedMap):
        replay = CommentedMap(replay or {})
        loaded["replay_args"] = replay

    replay["enabled"] = recording_enabled

    simulation_path.parent.mkdir(parents=True, exist_ok=True)
    with simulation_path.open("w", encoding="utf-8") as handle:
        _yaml.dump(loaded, handle)


@app.command()
def enable(
    project: Optional[str] = typer.Option(None, "--project", help="Project name"),
    root: Path = typer.Option(Path(DEFAULT_ROOT_DIR_NAME), "--root", help="FluxLoop root directory"),
    recording_file: Path = typer.Option(
        Path("recordings/args_recording.jsonl"),
        "--file",
        help="Recording file path relative to project",
    ),
):
    """Enable recording mode by updating .env and simulation config."""

    env_path = resolve_env_path(Path(".env"), project, root)
    env_values = _load_env(env_path)
    env_values["FLUXLOOP_RECORD_ARGS"] = "true"
    env_values["FLUXLOOP_RECORDING_FILE"] = str(recording_file)

    env_path.parent.mkdir(parents=True, exist_ok=True)
    _write_env(env_path, env_values)

    _update_simulation(True, project, root)

    console.print(
        f"[green]✓[/green] Recording enabled. Edit {env_path} or configs/simulation.yaml to adjust settings."
    )


@app.command()
def disable(
    project: Optional[str] = typer.Option(None, "--project", help="Project name"),
    root: Path = typer.Option(Path(DEFAULT_ROOT_DIR_NAME), "--root", help="FluxLoop root directory"),
):
    """Disable recording mode and reset settings."""

    env_path = resolve_env_path(Path(".env"), project, root)
    env_values = _load_env(env_path)
    env_values["FLUXLOOP_RECORD_ARGS"] = "false"
    env_path.parent.mkdir(parents=True, exist_ok=True)
    _write_env(env_path, env_values)

    _update_simulation(False, project, root)

    console.print("[green]✓[/green] Recording disabled.")


@app.command()
def status(
    project: Optional[str] = typer.Option(None, "--project", help="Project name"),
    root: Path = typer.Option(Path(DEFAULT_ROOT_DIR_NAME), "--root", help="FluxLoop root directory"),
):
    """Display current recording status."""

    env_path = resolve_env_path(Path(".env"), project, root)
    env_values = _load_env(env_path)
    record_args = env_values.get("FLUXLOOP_RECORD_ARGS", "false").lower() == "true"
    recording_file = env_values.get("FLUXLOOP_RECORDING_FILE", "(default)")

    simulation_path = resolve_config_section_path("simulation", project, root)
    simulation_exists = simulation_path.exists()

    table = Table(title="Recording Status", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Mode", "ENABLED" if record_args else "disabled")
    table.add_row("Recording File", recording_file)
    table.add_row(".env Path", str(env_path))
    table.add_row("Simulation Config", str(simulation_path) if simulation_exists else "(missing)")

    console.print(table)

    project_dir = (
        resolve_project_dir(project, root)
        if project
        else Path.cwd()
    )
    recordings_dir = project_dir / Path(recording_file).parent

    if recordings_dir.exists():
        console.print(
            f"\n[dim]Recording directory:[/dim] {recordings_dir}\n"
        )
    else:
        console.print(
            f"\n[yellow]Recording directory does not exist yet:[/yellow] {recordings_dir}\n"
        )
