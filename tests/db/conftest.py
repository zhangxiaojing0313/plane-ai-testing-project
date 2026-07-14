"""
DB test fixtures — safe, read-only PostgreSQL access via docker exec.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from utils.db_client import run_query, query_one_row, query_all_rows, query_count


@pytest.fixture(scope="session")
def db_container():
    """Verify the PostgreSQL container is accessible."""
    try:
        output = run_query("table_exists", {"table": "issues"})
        assert "t" in output, f"Table 'issues' not found: {output}"
        return True
    except Exception as e:
        pytest.fail(f"Database container not accessible: {e}")


@pytest.fixture(scope="session")
def known_issue_id():
    """Return the UUID of the known manual work item."""
    return "b4d5afaa-b7f1-483e-8bfb-4c9e1b4a21f7"


@pytest.fixture(scope="session")
def known_project_id():
    """Return the Plane QA Project UUID."""
    return "0c1cf73f-2d88-430b-812b-2e1c7f010c3c"


@pytest.fixture(scope="session")
def known_workspace_id():
    """Return the QA Lab workspace UUID."""
    return "2595af84-a3e7-4f06-a8dc-974b6f462eaa"
