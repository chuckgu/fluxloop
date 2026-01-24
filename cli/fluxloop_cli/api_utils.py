"""
Common API utilities for FluxLoop CLI commands.

Provides reusable functions for API URL resolution, payload handling,
cache management, and error handling.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import typer
import yaml
from rich.console import Console

console = Console()


def resolve_api_url(override: Optional[str]) -> str:
    """
    Resolve API URL from override or environment variables.

    Priority:
    1. Override parameter
    2. FLUXLOOP_API_URL
    3. FLUXLOOP_SYNC_URL
    4. Default: https://api.fluxloop.ai

    Args:
        override: Optional URL override.

    Returns:
        Resolved API URL (trailing slash removed).
    """
    url = (
        override
        or os.getenv("FLUXLOOP_API_URL")
        or os.getenv("FLUXLOOP_SYNC_URL")
        or "https://api.fluxloop.ai"
    )
    return url.rstrip("/")


def load_payload_file(file_path: Path) -> Dict[str, Any]:
    """
    Load payload from YAML or JSON file.

    Args:
        file_path: Path to YAML or JSON file.

    Returns:
        Parsed payload dictionary.

    Raises:
        typer.BadParameter: If file doesn't exist, has invalid extension, or parsing fails.
    """
    if not file_path.exists():
        raise typer.BadParameter(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    try:
        content = file_path.read_text()

        if suffix in [".yaml", ".yml"]:
            data = yaml.safe_load(content)
        elif suffix == ".json":
            data = json.loads(content)
        else:
            raise typer.BadParameter(
                f"Unsupported file format: {suffix}. Use .yaml, .yml, or .json"
            )

        if not isinstance(data, dict):
            raise typer.BadParameter(
                f"File must contain a dictionary/object, got {type(data).__name__}"
            )

        return data

    except yaml.YAMLError as e:
        raise typer.BadParameter(f"Invalid YAML: {e}")
    except json.JSONDecodeError as e:
        raise typer.BadParameter(f"Invalid JSON: {e}")


def ensure_cache_dir(subdir: str) -> Path:
    """
    Ensure ~/.fluxloop/{subdir} directory exists and return its path.

    Args:
        subdir: Subdirectory name under ~/.fluxloop/.

    Returns:
        Path to cache directory.
    """
    cache_dir = Path.home() / ".fluxloop" / subdir
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def save_cache_file(subdir: str, filename: str, data: dict) -> Path:
    """
    Save data to cache file in YAML format.

    Args:
        subdir: Subdirectory name under ~/.fluxloop/.
        filename: Cache file name.
        data: Dictionary to save.

    Returns:
        Path to saved cache file.
    """
    cache_dir = ensure_cache_dir(subdir)
    cache_path = cache_dir / filename

    cache_path.write_text(yaml.dump(data, indent=2, allow_unicode=True))

    return cache_path


def handle_api_error(resp: httpx.Response, context: str) -> None:
    """
    Handle common API error responses with helpful messages.

    Args:
        resp: HTTP response to check.
        context: Context description for error messages (e.g., "scenario", "persona").

    Raises:
        typer.Exit: If response indicates an error.
    """
    if resp.status_code == 401:
        console.print(
            "[red]✗[/red] Authentication required. Run [bold]fluxloop auth login[/bold] or login again if token expired.",
            style="bold red",
        )
        raise typer.Exit(1)

    elif resp.status_code == 403:
        console.print(
            "[red]✗[/red] Permission denied. Check your project access permissions.",
            style="bold red",
        )
        raise typer.Exit(1)

    elif resp.status_code == 404:
        console.print(
            f"[red]✗[/red] Resource not found: {context}",
            style="bold red",
        )
        raise typer.Exit(1)

    elif resp.status_code == 422:
        # Try to extract validation errors
        try:
            error_data = resp.json()
            if "detail" in error_data:
                detail = error_data["detail"]
                if isinstance(detail, list):
                    # FastAPI validation errors
                    errors = []
                    for err in detail:
                        field = " -> ".join(str(loc) for loc in err.get("loc", []))
                        msg = err.get("msg", "")
                        errors.append(f"  - {field}: {msg}")
                    console.print(
                        "[red]✗[/red] Invalid request data:",
                        style="bold red",
                    )
                    for err in errors:
                        console.print(err)
                else:
                    console.print(
                        f"[red]✗[/red] Invalid request data: {detail}",
                        style="bold red",
                    )
            else:
                console.print(
                    f"[red]✗[/red] Invalid request data: {resp.text}",
                    style="bold red",
                )
        except Exception:
            console.print(
                "[red]✗[/red] Invalid request data",
                style="bold red",
            )
        raise typer.Exit(1)

    elif resp.status_code >= 500:
        console.print(
            "[red]✗[/red] Server error. Please try again later.",
            style="bold red",
        )
        console.print(f"[dim]Status: {resp.status_code}[/dim]")
        raise typer.Exit(1)

    elif not resp.is_success:
        console.print(
            f"[red]✗[/red] Request failed: {resp.status_code}",
            style="bold red",
        )
        console.print(f"[dim]{resp.text}[/dim]")
        raise typer.Exit(1)
