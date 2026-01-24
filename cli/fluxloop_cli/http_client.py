"""
HTTP client with integrated authentication for FluxLoop CLI.

Provides unified authentication handling for both JWT (user auth) and API Key (CI/CD auth).
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import httpx

from .auth_manager import ensure_valid_token


class FluxLoopAPIError(Exception):
    """Exception for FluxLoop API errors with helpful messages."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def create_authenticated_client(
    api_url: str,
    use_jwt: bool = True,
    timeout: float = 30.0,
) -> httpx.Client:
    """
    Create an HTTP client with authentication headers.

    Authentication priority:
    1. If use_jwt=True: Try JWT authentication (requires login)
    2. Fall back to API Key from environment variables
    3. Raise error if neither is available

    Args:
        api_url: Base URL of the FluxLoop API.
        use_jwt: Whether to use JWT authentication (default: True).
        timeout: Request timeout in seconds.

    Returns:
        Configured httpx.Client with authentication headers.

    Raises:
        FluxLoopAPIError: If authentication is not available.
    """
    headers: Dict[str, str] = {}

    # Try JWT authentication
    if use_jwt:
        token = ensure_valid_token(api_url)
        if token:
            headers["Authorization"] = f"Bearer {token.access_token}"
            return httpx.Client(
                base_url=api_url,
                timeout=timeout,
                headers=headers,
            )

    # Fall back to API Key
    api_key = (
        os.getenv("FLUXLOOP_SYNC_API_KEY")
        or os.getenv("FLUXLOOP_API_KEY")
    )
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        return httpx.Client(
            base_url=api_url,
            timeout=timeout,
            headers=headers,
        )

    # No authentication available
    if use_jwt:
        raise FluxLoopAPIError(
            "Login required. Run 'fluxloop auth login'."
        )
    else:
        raise FluxLoopAPIError(
            "API Key not set. Run 'fluxloop config set-sync-key'."
        )


def post_with_retry(
    client: httpx.Client,
    endpoint: str,
    *,
    payload: Dict[str, Any],
    max_retries: int = 3,
    backoff_seconds: float = 1.0,
) -> httpx.Response:
    """
    POST request with automatic retry on transient failures.

    Args:
        client: httpx.Client instance.
        endpoint: API endpoint path.
        payload: JSON payload to send.
        max_retries: Maximum number of retry attempts.
        backoff_seconds: Initial backoff time (doubles on each retry).

    Returns:
        Response object on success.

    Raises:
        FluxLoopAPIError: On authentication or permission errors.
        httpx.HTTPError: On other HTTP errors after retries.
    """
    attempt = 0
    last_exception = None

    while attempt <= max_retries:
        try:
            resp = client.post(endpoint, json=payload)
            _handle_error_response(resp)
            resp.raise_for_status()
            return resp
        except FluxLoopAPIError:
            # Don't retry auth errors
            raise
        except httpx.HTTPError as e:
            last_exception = e
            attempt += 1
            if attempt > max_retries:
                break
            time.sleep(backoff_seconds * (2 ** (attempt - 1)))

    # All retries exhausted
    if last_exception:
        raise last_exception
    raise httpx.HTTPError("Request failed after retries")


def _handle_error_response(resp: httpx.Response) -> None:
    """
    Handle common API error responses with helpful messages.

    Args:
        resp: Response to check.

    Raises:
        FluxLoopAPIError: If response indicates auth/permission error.
    """
    if resp.status_code == 401:
        raise FluxLoopAPIError(
            "Authentication required. Run 'fluxloop auth login' or login again if token expired.",
            status_code=401,
        )
    elif resp.status_code == 403:
        raise FluxLoopAPIError(
            "Permission denied. Check your project access permissions.",
            status_code=403,
        )
