"""
DB Work Item Consistency Tests (write lifecycle)
DB-003: API create -> DB exists
DB-004: API update -> DB synchronized
DB-005: API vs DB field comparison
DB-006: Delete mechanism (soft delete)
DB-007: Cleanup verification

All API requests use 429 retry with exponential backoff.
All created AUTO-D4-DB items are tracked and cleaned up via fixture.
"""
import pytest
import sys
import os
import time
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from utils.db_client import run_query, query_one_row, query_all_rows, query_count
from utils.config import APIConfig as cfg

BASE = cfg.BASE_URL
WS = cfg.WORKSPACE_SLUG
PID = cfg.PROJECT_ID
API_KEY = cfg.API_KEY

API_HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
ISSUES_URL = f"{BASE}/api/v1/workspaces/{WS}/projects/{PID}/issues/"

# Exponential backoff delays for 429 retry (seconds)
_RETRY_BACKOFFS = [2, 4, 8, 16, 32]
_MAX_RETRIES = 5


def _generate_title():
    ts = time.strftime("%Y-%m-%dT%H-%M-%S", time.gmtime())
    return f"AUTO-D4-DB-{ts}"


def _api_request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    """Make an API request with 429-specific retry and exponential backoff.

    Only HTTP 429 triggers a retry. Retry-After header is respected when
    present; otherwise exponential backoff is used. Other 4xx/5xx status
    codes are returned immediately without retry.

    Logs only attempt number, status code, and wait seconds.
    Never logs API Key, cookies, passwords, or full request headers.
    """
    if "headers" not in kwargs:
        kwargs["headers"] = API_HEADERS
    if "timeout" not in kwargs:
        kwargs["timeout"] = 15

    for attempt in range(_MAX_RETRIES + 1):
        resp = requests.request(method, url, **kwargs)
        if resp.status_code != 429:
            return resp
        if attempt >= _MAX_RETRIES:
            return resp

        retry_after = resp.headers.get("Retry-After")
        if retry_after is not None:
            try:
                wait = int(retry_after)
            except (ValueError, TypeError):
                wait = _RETRY_BACKOFFS[attempt]
        else:
            wait = _RETRY_BACKOFFS[attempt]

        print(f"429 retry: attempt={attempt+1}, status=429, wait={wait}s")
        time.sleep(wait)

    return resp


def _api_create(title: str, **kwargs) -> dict:
    """Create a work item via API (with 429 retry)."""
    payload = {"name": title, **kwargs}
    resp = _api_request_with_retry("POST", ISSUES_URL, json=payload)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"API create failed: status={resp.status_code}")
    return resp.json()


def _api_get(issue_id: str) -> dict:
    """Get a work item via API (with 429 retry)."""
    resp = _api_request_with_retry("GET", f"{ISSUES_URL}{issue_id}/")
    if resp.status_code != 200:
        raise RuntimeError(f"API get failed: status={resp.status_code}")
    return resp.json()


def _api_update(issue_id: str, **kwargs) -> dict:
    """Update a work item via API (with 429 retry)."""
    resp = _api_request_with_retry("PATCH", f"{ISSUES_URL}{issue_id}/", json=kwargs)
    if resp.status_code != 200:
        raise RuntimeError(f"API update failed: status={resp.status_code}")
    return resp.json()


def _api_delete(issue_id: str) -> int:
    """Delete a work item via API (with 429 retry). Returns status code."""
    resp = _api_request_with_retry("DELETE", f"{ISSUES_URL}{issue_id}/")
    return resp.status_code


@pytest.mark.db
@pytest.mark.destructive
class TestWorkItemDBConsistency:
    """DB-003 through DB-007: Full lifecycle with DB verification.

    All created AUTO-D4-DB items are tracked in self.created_ids and
    cleaned up via the _manage_test_data fixture, which runs in teardown
    regardless of test outcome (pass, fail, or exception).

    Cleanup uses API DELETE only - never direct SQL DELETE.
    """

    created_ids: list = []

    @pytest.fixture(autouse=True)
    def _manage_test_data(self):
        """Fixture: track created IDs; guaranteed API cleanup on teardown.

        Uses yield/finalizer pattern so cleanup runs:
        - when tests pass
        - when assertions fail
        - when 429 or other exceptions occur
        """
        # Setup: ensure clean list for this test
        self.created_ids = []
        yield
        # Teardown: always attempt cleanup of tracked items via API
        for issue_id in self.created_ids:
            try:
                _api_request_with_retry("DELETE", f"{ISSUES_URL}{issue_id}/")
            except Exception:
                pass

    def test_db003_api_create_db_exists(self):
        """DB-003: Create via API -> verify in database."""
        title = _generate_title()
        api_data = _api_create(title)
        issue_id = api_data.get("id")
        assert issue_id, f"No ID in API response: {api_data}"
        self.created_ids.append(issue_id)

        # Verify in DB
        row = query_one_row("issue_by_id", {"issue_id": issue_id})
        assert row is not None, f"Created issue {issue_id} not found in DB"
        assert row[1] == title, f"Title mismatch: DB={row[1]} API={title}"
        assert row[5] == PID, f"Project FK mismatch: {row[5]} vs {PID}"
        # created_at not null
        assert row[9] != "", "created_at is empty"

    def test_db003_workspace_fk(self):
        """DB-003 extension: Verify workspace FK is correct."""
        title = _generate_title()
        api_data = _api_create(title)
        issue_id = api_data.get("id")
        self.created_ids.append(issue_id)

        row = query_one_row("issue_by_id", {"issue_id": issue_id})
        assert row is not None
        # workspace_id is index 6
        ws_id = row[6]
        # Verify workspace exists
        ws_row = query_one_row("workspace_by_slug", {"slug": WS})
        assert ws_row is not None, f"Workspace '{WS}' not found"
        assert ws_row[0] == ws_id, f"Workspace FK mismatch: {ws_id}"

    def test_db004_api_update_db_sync(self):
        """DB-004: Update via API -> verify DB synchronized."""
        title = _generate_title()
        api_data = _api_create(title)
        issue_id = api_data.get("id")
        self.created_ids.append(issue_id)

        # Record original state
        original = query_one_row("issue_by_id", {"issue_id": issue_id})
        # index 10 = updated_at
        orig_updated_at = original[10] if len(original) > 10 else ""

        # Update via API
        new_title = f"{title}-UPDATED"
        _api_update(issue_id, name=new_title, priority="high")

        # Give DB a moment
        time.sleep(0.5)

        # Verify in DB
        updated = query_one_row("issue_by_id", {"issue_id": issue_id})
        assert updated is not None
        assert updated[1] == new_title, f"Title not updated: {updated[1]}"
        assert "high" in str(updated[3]).lower(), f"Priority not updated: {updated[3]}"

        # updated_at should have changed
        new_updated_at = updated[10] if len(updated) > 10 else ""
        assert new_updated_at != orig_updated_at, (
            f"updated_at did not change: was {orig_updated_at}, still {new_updated_at}"
        )

    def test_db005_api_vs_db_consistency(self):
        """DB-005: Compare API response fields with DB values."""
        title = _generate_title()
        api_data = _api_create(title, priority="medium")
        issue_id = api_data.get("id")
        self.created_ids.append(issue_id)

        # Get from API
        api_detail = _api_get(issue_id)

        # Get from DB
        db_row = query_one_row("issue_by_id", {"issue_id": issue_id})
        assert db_row is not None

        # Compare key fields
        assert api_detail.get("name") == db_row[1], (
            f"name mismatch: API={api_detail.get('name')} DB={db_row[1]}"
        )
        # Note: Plane v1 API does NOT return project_id directly in issue detail response.
        # The project association is implicit (part of the URL path).
        # DB has project_id; API v1 embeds project context in the URL structure instead.
        # Priority: API returns 'medium', DB stores 'medium'
        api_priority = api_detail.get("priority", "").lower()
        db_priority = str(db_row[3]).lower()
        assert api_priority == db_priority, (
            f"priority mismatch: API={api_priority} DB={db_priority}"
        )
        # Verify DB project_id is correct (known from config)
        assert db_row[5] == PID, f"DB project_id mismatch: {db_row[5]} vs expected {PID}"

    def test_db006_delete_mechanism(self):
        """DB-006: Verify delete is soft delete (deleted_at set, record preserved)."""
        title = _generate_title()
        api_data = _api_create(title)
        issue_id = api_data.get("id")
        self.created_ids.append(issue_id)

        # Delete via API
        status = _api_delete(issue_id)
        assert status == 204, f"Delete returned {status}, expected 204"

        # Give DB a moment
        time.sleep(0.5)

        # Check DB - record should still exist with deleted_at set
        row = query_one_row("issue_by_id", {"issue_id": issue_id})
        assert row is not None, "Record physically deleted (should be soft-deleted)"

        # deleted_at is index 13
        deleted_at = row[13] if len(row) > 13 else ""
        assert deleted_at != "", (
            f"Soft delete not applied: deleted_at is empty. "
            f"Plane v1.3.1 uses soft delete (deleted_at timestamp). "
            f"Record preserved with deleted_at={deleted_at}"
        )

    def test_db007_cleanup(self):
        """DB-007: Actively clean up AUTO-D4-DB data, then verify zero residue.

        Steps:
        1. Delete all tracked IDs from this run via API (with 429 retry)
        2. Query DB for any remaining AUTO-D4-DB items
        3. Delete any stragglers via API (handles build #3 residue)
        4. Re-query DB and assert count is zero
        """
        # Step 1: Clean up tracked IDs from this test run
        for issue_id in self.created_ids:
            try:
                _api_request_with_retry("DELETE", f"{ISSUES_URL}{issue_id}/")
            except Exception:
                pass

        # Step 2: Find and clean up any remaining AUTO-D4-DB items
        # (includes residue from prior builds, e.g. build #3)
        remaining = query_all_rows("cleanup_auto_items", {"pattern": "AUTO-D4-DB-%"})
        for item in remaining:
            if len(item) >= 1:
                iid = item[0]
                try:
                    _api_request_with_retry("DELETE", f"{ISSUES_URL}{iid}/")
                except Exception:
                    pass
                time.sleep(0.2)

        # Step 3: Wait for DB consistency
        time.sleep(0.5)

        # Step 4: Final verification - must be zero
        count = query_count("issue_count_by_name_pattern", {"pattern": "AUTO-D4-DB-%"})
        assert count == 0, f"Leftover AUTO-D4-DB items: {count}"
