"""
Authentication token management for FluxLoop CLI.

Handles device-code flow authentication, token storage, and refresh logic.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import httpx


@dataclass
class AuthToken:
    """
    Authentication token data structure.
    
    User-scoped JWT: project_id is NOT included in the token.
    Project selection is handled via local context (.fluxloop/context.json).
    """

    access_token: str
    refresh_token: str
    expires_at: str  # ISO 8601 format
    user_id: str
    user_email: str

    @classmethod
    def from_dict(cls, data: dict) -> AuthToken:
        """Create AuthToken from dictionary."""
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=data["expires_at"],
            user_id=data["user_id"],
            user_email=data.get("user_email", ""),
        )

    def to_dict(self) -> dict:
        """Convert AuthToken to dictionary."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "user_id": self.user_id,
            "user_email": self.user_email,
        }


@dataclass
class DeviceCodeResponse:
    """Device code flow initiation response."""

    device_code: str
    user_code: str
    verification_url: str
    expires_in: int
    interval: int


def get_auth_token_path() -> Path:
    """Get the path to the auth token file."""
    return ensure_fluxloop_home() / "auth.json"


def ensure_fluxloop_home() -> Path:
    """Ensure ~/.fluxloop/ directory exists and return its path."""
    fluxloop_home = Path.home() / ".fluxloop"
    fluxloop_home.mkdir(parents=True, exist_ok=True)
    return fluxloop_home


def load_auth_token() -> Optional[AuthToken]:
    """
    Load authentication token from ~/.fluxloop/auth.json.

    Returns:
        AuthToken if found and valid, None otherwise.
    """
    token_path = get_auth_token_path()

    if not token_path.exists():
        return None

    try:
        data = json.loads(token_path.read_text())
        return AuthToken.from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Log error but don't crash - treat as missing token
        print(f"Warning: Failed to load auth token: {e}")
        return None


def save_auth_token(token: AuthToken) -> None:
    """
    Save authentication token to ~/.fluxloop/auth.json with secure permissions.

    Args:
        token: AuthToken to save.
    """
    token_path = get_auth_token_path()

    # Write token data
    token_path.write_text(json.dumps(token.to_dict(), indent=2))

    # Set file permissions to 600 (read/write for owner only)
    token_path.chmod(0o600)


def delete_auth_token() -> None:
    """Delete the authentication token file."""
    token_path = get_auth_token_path()

    if token_path.exists():
        token_path.unlink()


def is_token_expired(token: AuthToken) -> bool:
    """
    Check if the token is expired or will expire soon.

    Uses a 5-minute buffer to allow for network latency and refresh time.

    Args:
        token: AuthToken to check.

    Returns:
        True if token is expired or will expire within 5 minutes.
    """
    try:
        # Parse ISO 8601 timestamp
        expires_at = datetime.fromisoformat(token.expires_at.replace("Z", "+00:00"))

        # Add timezone info if missing
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # Current time with 5-minute buffer
        now_with_buffer = datetime.now(timezone.utc) + timedelta(minutes=5)

        return expires_at <= now_with_buffer
    except (ValueError, AttributeError) as e:
        # If we can't parse the timestamp, treat as expired
        print(f"Warning: Failed to parse token expiry: {e}")
        return True


def format_expires_at(expires_at: str) -> str:
    """
    Format expiry timestamp as human-readable string.

    Args:
        expires_at: ISO 8601 timestamp string.

    Returns:
        Formatted string like "2h 30m remaining" or "expired".
    """
    try:
        expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))

        # Add timezone info if missing
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        delta = expires - now

        if delta.total_seconds() <= 0:
            return "expired"

        # Convert to hours and minutes
        total_minutes = int(delta.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours > 0:
            return f"{hours}h {minutes}m remaining"
        else:
            return f"{minutes}m remaining"
    except (ValueError, AttributeError):
        return "unknown"


def start_device_code_flow(api_url: str) -> DeviceCodeResponse:
    """
    Start device-code authentication flow.

    Args:
        api_url: Base URL of the FluxLoop API.

    Returns:
        DeviceCodeResponse with device_code, user_code, and verification URL.

    Raises:
        httpx.HTTPError: If API request fails.
    """
    url = api_url.rstrip("/") + "/api/cli-connect/start"

    with httpx.Client(timeout=10.0) as client:
        resp = client.post(url, json={})
        resp.raise_for_status()
        data = resp.json()

    expires_in = data.get("expires_in")
    if expires_in is None:
        expires_in = data.get("expires_in_sec", 600)
    interval = data.get("interval")
    if interval is None:
        interval = data.get("interval_sec", 5)

    return DeviceCodeResponse(
        device_code=data["device_code"],
        user_code=data["user_code"],
        verification_url=data["verification_url"],
        expires_in=expires_in,
        interval=interval,
    )


def poll_device_code(
    api_url: str, device_code: str, interval: int = 5, timeout: int = 300
) -> AuthToken:
    """
    Poll for device-code completion.

    Args:
        api_url: Base URL of the FluxLoop API.
        device_code: Device code from start_device_code_flow.
        interval: Polling interval in seconds.
        timeout: Maximum time to wait in seconds (default: 5 minutes).

    Returns:
        AuthToken when user approves authentication.

    Raises:
        TimeoutError: If polling times out.
        ValueError: If user denies authentication or code expires.
        httpx.HTTPError: If API request fails.
    """
    url = api_url.rstrip("/") + "/api/cli-connect/complete"
    start_time = time.time()

    with httpx.Client(timeout=10.0) as client:
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError("Authentication timeout exceeded")

            resp = client.post(url, json={"device_code": device_code})
            resp.raise_for_status()
            data = resp.json()

            # Check for pending status
            if data.get("status") == "pending":
                time.sleep(interval)
                continue

            status = data.get("status")
            if status == "denied":
                raise ValueError("User denied authentication")
            if status == "expired":
                raise ValueError("Authentication code has expired")
            if status not in {"approved", "pending"}:
                raise ValueError(f"Authentication error: {status}")

            credential = data.get("credential") or {}
            access_token = credential.get("access_token")
            if not access_token:
                raise ValueError("Authentication response missing access token")

            expires_at = credential.get("expires_at")
            if not expires_at:
                expires_at = (
                    datetime.now(timezone.utc) + timedelta(seconds=3600)
                ).isoformat()

            return AuthToken(
                access_token=access_token,
                refresh_token=credential.get("refresh_token", ""),
                expires_at=expires_at,
                user_id=credential.get("user_id", ""),
                user_email=credential.get("user_email", ""),
            )


def refresh_access_token(api_url: str, refresh_token: str) -> AuthToken:
    """
    Refresh access token using refresh token.

    Args:
        api_url: Base URL of the FluxLoop API.
        refresh_token: Refresh token from previous authentication.

    Returns:
        New AuthToken with refreshed access_token.

    Raises:
        ValueError: If refresh token is invalid.
        httpx.HTTPError: If API request fails.
    """
    url = api_url.rstrip("/") + "/api/cli-connect/refresh"

    with httpx.Client(timeout=10.0) as client:
        resp = client.post(url, json={"refresh_token": refresh_token})
        resp.raise_for_status()
        data = resp.json()

    credential = data.get("credential") or {}
    access_token = credential.get("access_token")
    if not access_token:
        raise ValueError("Token refresh failed. Please login again.")

    # Load existing token to preserve user info if response omits it
    existing_token = load_auth_token()
    user_id = credential.get("user_id") or (existing_token.user_id if existing_token else "")
    user_email = credential.get("user_email") or (existing_token.user_email if existing_token else "")

    expires_at = credential.get("expires_at")
    if not expires_at:
        expires_at = (
            datetime.now(timezone.utc) + timedelta(seconds=3600)
        ).isoformat()

    return AuthToken(
        access_token=access_token,
        refresh_token=credential.get("refresh_token", refresh_token),
        expires_at=expires_at,
        user_id=user_id,
        user_email=user_email,
    )


def ensure_valid_token(api_url: str) -> Optional[AuthToken]:
    """
    Ensure a valid token exists, refreshing if necessary.

    Args:
        api_url: Base URL of the FluxLoop API.

    Returns:
        Valid AuthToken, or None if unable to get/refresh token.
    """
    # Load existing token
    token = load_auth_token()
    if not token:
        return None

    # Check if token is expired
    if not is_token_expired(token):
        return token

    # Try to refresh
    try:
        refreshed_token = refresh_access_token(api_url, token.refresh_token)
        save_auth_token(refreshed_token)
        return refreshed_token
    except Exception as e:
        print(f"Warning: Failed to refresh token: {e}")
        return None
