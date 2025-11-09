from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixtures_path() -> Path:
    """Return the path to the shared test fixtures directory."""
    return Path(__file__).parent / "fixtures"

