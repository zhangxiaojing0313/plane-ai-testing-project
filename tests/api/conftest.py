"""
Shared pytest fixtures for Plane API automation.

All fixtures use the real Plane API. No mocks.
API Key is handled in memory and never exposed in logs or reports.
"""

import logging
import pytest

from utils.api_client import APIClient
from utils.config import APIConfig

# Configure logging (safe: no API Key in format strings)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("plane-api-tests")


def pytest_configure(config):
    """Validate environment before running any tests."""
    missing = APIConfig.validate()
    if missing:
        pytest.exit(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Check .env file."
        )


# ---------------------------------------------------------------------------
# Session-scoped: one API client for the entire test run
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def api_config() -> APIConfig:
    """Provide APIConfig to tests (safe — no secrets exposed)."""
    return APIConfig


@pytest.fixture(scope="session")
def client() -> APIClient:
    """Create a single APIClient for the test session (connection reuse)."""
    cl = APIClient()
    yield cl
    cl.close()


# ---------------------------------------------------------------------------
# Function-scoped conveniences
# ---------------------------------------------------------------------------


@pytest.fixture
def workspace_slug(api_config: APIConfig) -> str:
    """Workspace slug from environment."""
    return api_config.WORKSPACE_SLUG


@pytest.fixture
def project_id(api_config: APIConfig) -> str:
    """Target project ID from environment."""
    return api_config.PROJECT_ID


@pytest.fixture
def base_api_path(api_config: APIConfig) -> str:
    """Base API path (no trailing slash)."""
    return api_config.API_BASE_URL


@pytest.fixture
def project_api_path(workspace_slug: str, project_id: str) -> str:
    """Return /api/workspaces/<slug>/projects/<pid> path prefix."""
    return f"/api/workspaces/{workspace_slug}/projects/{project_id}"


# ---------------------------------------------------------------------------
# Cleanup tracking (for destructive tests)
# ---------------------------------------------------------------------------


@pytest.fixture
def created_resources() -> list:
    """Track resources created during a test for automatic cleanup."""
    resources: list = []
    yield resources
    # Cleanup happens in the destructive test's own fixture
