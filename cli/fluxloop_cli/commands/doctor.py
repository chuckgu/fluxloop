"""
Doctor command for diagnosing FluxLoop environment issues.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

from ..project_paths import resolve_config_directory, resolve_config_path
from ..constants import DEFAULT_CONFIG_PATH, DEFAULT_ROOT_DIR_NAME

app = typer.Typer(
    help="Diagnose FluxLoop CLI, MCP and environment setup.",
    invoke_without_command=True,
    no_args_is_help=False,
)
console = Console()


@dataclass
class CommandResult:
    success: bool
    path: Optional[str]
    output: Optional[str]
    error: Optional[str]


def _which(executable: str) -> Optional[str]:
    from shutil import which

    return which(executable)


def _run_command(command: str, *args: str) -> CommandResult:
    candidate = _which(command)
    if not candidate:
        return CommandResult(False, None, None, f"{command} not found on PATH")

    try:
        completed = subprocess.run(
            [candidate, *args],
            capture_output=True,
            text=True,
            check=True,
        )
        return CommandResult(True, candidate, completed.stdout.strip(), completed.stderr.strip() or None)
    except subprocess.CalledProcessError as exc:
        return CommandResult(
            False,
            candidate,
            exc.stdout.strip() or None,
            exc.stderr.strip() or exc.stdout.strip() or str(exc),
        )


def _detect_virtual_environment() -> Dict[str, Any]:
    env_vars = {
        "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV"),
        "CONDA_PREFIX": os.environ.get("CONDA_PREFIX"),
        "UV_PROJECT_ENV": os.environ.get("UV_PROJECT_ENV"),
    }
    virtualized = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    return {
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "virtual_env": virtualized,
        "virtual_env_path": (
            env_vars["VIRTUAL_ENV"]
            or env_vars["CONDA_PREFIX"]
            or (Path(sys.prefix).as_posix() if virtualized else None)
        ),
        "environment_variables": {k: v for k, v in env_vars.items() if v},
    }


def _check_index_directory(index_dir: Path) -> Dict[str, Any]:
    exists = index_dir.exists()
    chunks_file = index_dir / "chunks.jsonl"
    chunks_exists = chunks_file.exists()
    chunks_size = chunks_file.stat().st_size if chunks_exists else 0
    return {
        "exists": exists,
        "path": index_dir.as_posix(),
        "chunks_exists": chunks_exists,
        "chunks_size": chunks_size,
    }


def _resolve_project_info(root: Path, project: Optional[str]) -> Dict[str, Any]:
    config_path = resolve_config_path(DEFAULT_CONFIG_PATH, project, root)
    config_dir = resolve_config_directory(project, root)
    return {
        "root": str(root.resolve()),
        "config_directory": str(config_dir.resolve()),
        "project_yaml": str(config_path.resolve()),
        "project_yaml_exists": config_path.exists(),
        "config_directory_exists": config_dir.exists(),
    }


def _run_diagnostics(
    project: Optional[str],
    root: Path,
    index_dir: Optional[Path],
    output_json: bool,
) -> None:
    console.print(Panel.fit("FluxLoop Environment Doctor", border_style="blue"))

    virtual_info = _detect_virtual_environment()
    fluxloop_result = _run_command("fluxloop", "--version")
    mcp_result = _run_command("fluxloop-mcp", "--help")
    python_result = _run_command(sys.executable, "--version")

    resolved_root = root
    project_info = _resolve_project_info(resolved_root, project)
    resolved_index_dir = (
        index_dir
        if index_dir is not None
        else Path.home() / ".fluxloop" / "mcp" / "index" / "dev"
    )
    index_info = _check_index_directory(resolved_index_dir)

    diagnostics = {
        "python": {
            "executable": sys.executable,
            "version": virtual_info["python_version"],
            "platform": virtual_info["platform"],
            "command_output": python_result.output,
        },
        "virtual_environment": virtual_info,
        "fluxloop_cli": asdict(fluxloop_result),
        "fluxloop_mcp": asdict(mcp_result),
        "project": project_info,
        "mcp_index": index_info,
    }

    if output_json:
        typer.echo(json.dumps(diagnostics, indent=2, default=str))
        raise typer.Exit()

    items_panel = Table(show_header=False, box=None)
    items_panel.add_column("Component", style="cyan", no_wrap=True)
    items_panel.add_column("Status")
    items_panel.add_column("Details", style="dim")

    items_panel.add_row(
        "Python",
        "[green]✓[/green]" if python_result.success else "[red]✗[/red]",
        f"{virtual_info['python_version']} ({sys.executable})",
    )

    items_panel.add_row(
        "Virtual Env",
        "[green]✓[/green]" if virtual_info["virtual_env"] else "[yellow]–[/yellow]",
        virtual_info["virtual_env_path"] or "Global interpreter",
    )

    items_panel.add_row(
        "FluxLoop CLI",
        "[green]✓[/green]" if fluxloop_result.success else "[red]✗[/red]",
        fluxloop_result.path or fluxloop_result.error or "Not found",
    )

    items_panel.add_row(
        "FluxLoop MCP",
        "[green]✓[/green]" if mcp_result.success else "[red]✗[/red]",
        mcp_result.path or mcp_result.error or "Not found",
    )

    index_status = "[green]✓[/green]" if index_info["exists"] else "[yellow]–[/yellow]"
    index_details = index_info["path"]
    if index_info["exists"]:
        chunk_detail = (
            f"chunks.jsonl ({index_info['chunks_size']} bytes)"
            if index_info["chunks_exists"]
            else "missing chunks.jsonl"
        )
        index_details = f"{index_details} • {chunk_detail}"

    items_panel.add_row("MCP Index", index_status, index_details)

    config_status = (
        "[green]✓[/green]" if project_info["project_yaml_exists"] else "[yellow]–[/yellow]"
    )
    config_details = (
        f"{project_info['project_yaml']} (project.yaml)"
        if project_info["project_yaml_exists"]
        else "Run: fluxloop init project"
    )
    items_panel.add_row("Project Config", config_status, config_details)

    console.print(Padding(items_panel, (1, 0, 1, 0)))

    if fluxloop_result.error or mcp_result.error:
        console.print("[bold red]Errors[/bold red]")
        if fluxloop_result.error:
            console.print(f"• FluxLoop CLI: {fluxloop_result.error}")
        if mcp_result.error:
            console.print(f"• fluxloop-mcp: {mcp_result.error}")
        console.print()

    if diagnostics["fluxloop_cli"]["output"]:
        console.print(Panel(diagnostics["fluxloop_cli"]["output"], title="fluxloop --version", border_style="green"))
    if diagnostics["fluxloop_mcp"]["output"]:
        console.print(Panel(diagnostics["fluxloop_mcp"]["output"], title="fluxloop-mcp --help", border_style="green"))

    console.print(Padding(Panel.fit("Doctor completed", border_style="green"), (1, 0, 0, 0)))


@app.callback()
def doctor_callback(
    ctx: typer.Context,
    project: Optional[str] = typer.Option(
        None, "--project", "-p", help="Project name under the FluxLoop root directory."
    ),
    root: Path = typer.Option(
        Path(DEFAULT_ROOT_DIR_NAME),
        "--root",
        help="FluxLoop root directory (defaults to ./fluxloop).",
    ),
    index_dir: Optional[Path] = typer.Option(
        None,
        "--index-dir",
        help="Override FluxLoop MCP index directory.",
    ),
    output_json: bool = typer.Option(
        False,
        "--json",
        help="Output diagnostic information as JSON.",
    ),
) -> None:
    """
    Diagnose the FluxLoop CLI, MCP installation, virtual environment, and project configuration.
    """
    if ctx.invoked_subcommand:
        return
    _run_diagnostics(project, root, index_dir, output_json)

