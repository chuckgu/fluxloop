"""
Common CLI options for FluxLoop commands.

Provides reusable Typer options that can be shared across commands.
"""

from pathlib import Path
from typing import Optional

import typer


# API URL option - used across all API commands
def api_url_option() -> Optional[str]:
    """
    Reusable --api-url option.

    Returns:
        Typer option for API URL override.
    """
    return typer.Option(
        None,
        "--api-url",
        help="FluxLoop API base URL (overrides environment variables)",
    )


# Quiet mode option - suppress non-essential output
def quiet_option() -> bool:
    """
    Reusable --quiet option.

    Returns:
        Typer option for quiet mode.
    """
    return typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress non-essential output",
    )


# Dry-run option - preview without making changes
def dry_run_option() -> bool:
    """
    Reusable --dry-run option.

    Returns:
        Typer option for dry-run mode.
    """
    return typer.Option(
        False,
        "--dry-run",
        help="Preview changes without saving to database",
    )


# File option - load payload from file
def file_option() -> Optional[Path]:
    """
    Reusable --file option for loading payloads.

    Returns:
        Typer option for payload file path.
    """
    return typer.Option(
        None,
        "--file",
        "-f",
        help="Load payload from YAML or JSON file",
        exists=False,  # We'll validate existence in load_payload_file
    )
