"""
Authentication commands for FluxLoop CLI.
"""

import os
import webbrowser
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live

from ..auth_manager import (
    start_device_code_flow,
    poll_device_code,
    save_auth_token,
    load_auth_token,
    delete_auth_token,
    is_token_expired,
    format_expires_at,
)


app = typer.Typer(help="Manage FluxLoop authentication")
console = Console()


def _resolve_api_url(override: Optional[str]) -> str:
    """Resolve API URL from override or environment variables."""
    url = (
        override
        or os.getenv("FLUXLOOP_API_URL")
        or os.getenv("FLUXLOOP_SYNC_URL")
        or "https://api.fluxloop.ai"
    )
    return url.rstrip("/")


@app.command()
def login(
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="FluxLoop API base URL"
    ),
):
    """
    Login to connect your FluxLoop account.
    """
    api_url = _resolve_api_url(api_url)

    try:
        # Start device-code flow
        device_response = start_device_code_flow(api_url)

        # Display login panel
        login_panel = Panel(
            f"[bold cyan]Open this URL in your browser:[/bold cyan]\n"
            f"{device_response.verification_url}\n\n"
            f"[bold yellow]Enter code:[/bold yellow] [bold green]{device_response.user_code}[/bold green]",
            title="[bold blue]FluxLoop CLI Login[/bold blue]",
            border_style="blue",
        )
        console.print(login_panel)
        console.print()

        # Try to open browser automatically
        try:
            webbrowser.open(device_response.verification_url)
            console.print("[dim]Browser opened automatically...[/dim]")
        except Exception:
            console.print("[dim]Please open the browser manually.[/dim]")

        console.print()

        # Poll for completion with spinner
        spinner = Spinner("dots", text="Waiting for approval...")
        with Live(spinner, console=console, refresh_per_second=10):
            token = poll_device_code(
                api_url,
                device_response.device_code,
                interval=device_response.interval,
                timeout=device_response.expires_in,
            )

        # Save token
        save_auth_token(token)

        # Success message (User-scoped, no project selection at login)
        console.print()
        console.print(f"[green]✓[/green] Login successful: [bold]{token.user_email}[/bold]")
        console.print()
        console.print("[dim]Next steps:[/dim]")
        console.print("[dim]  • fluxloop projects list    - View your projects[/dim]")
        console.print("[dim]  • fluxloop context set-project <id>  - Select a project[/dim]")

    except TimeoutError as e:
        console.print(f"\n[red]✗[/red] {e}", style="bold red")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"\n[red]✗[/red] {e}", style="bold red")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]✗[/red] Login failed: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def logout():
    """
    Logout and delete saved authentication information.
    """
    token = load_auth_token()

    if not token:
        console.print("[yellow]Already logged out.[/yellow]")
        return

    delete_auth_token()
    console.print("[green]✓[/green] Logged out successfully")


@app.command()
def status():
    """
    Check current login status.
    """
    token = load_auth_token()

    if not token:
        console.print("[yellow]Not logged in.[/yellow]")
        console.print("[dim]Run [bold]fluxloop auth login[/bold] to login.[/dim]")
        return

    # Check expiration
    expired = is_token_expired(token)
    time_remaining = format_expires_at(token.expires_at)

    if expired:
        console.print("[red]✗[/red] Token has expired")
        console.print("[dim]Run [bold]fluxloop auth login[/bold] to login again.[/dim]")
    else:
        console.print(f"[green]✓[/green] Logged in: [bold]{token.user_email}[/bold]")
        console.print(f"  Token expires: {time_remaining}")
        
        # Show current context if available
        from ..context_manager import load_context
        context = load_context()
        if context:
            if context.current_project:
                console.print(f"  Project: {context.current_project.name} ([dim]{context.current_project.id}[/dim])")
            if context.current_scenario:
                console.print(f"  Scenario: {context.current_scenario.name} ([dim]{context.current_scenario.id}[/dim])")
        else:
            console.print("[dim]  No project selected. Run [bold]fluxloop projects list[/bold] to see your projects.[/dim]")