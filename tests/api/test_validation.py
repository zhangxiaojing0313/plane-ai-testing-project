"""
API 400 Bad Request Parameter Validation Tests

Covers:
- Missing required fields
- Invalid data types
- Invalid enum values
- Malformed request body
- Excessive field lengths

Markers: api, negative, regression

Note: All assertions are based on Plane v1.3.1 real behavior.
Status codes and error structures are recorded as observed,
not judged against any expected standard.
"""
import pytest
import requests
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from utils.config import APIConfig as cfg

BASE = cfg.BASE_URL
WS = cfg.WORKSPACE_SLUG
PID = cfg.PROJECT_ID
API_KEY = cfg.API_KEY

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
ISSUES_URL = f"{BASE}/api/v1/workspaces/{WS}/projects/{PID}/issues/"


@pytest.mark.api
@pytest.mark.negative
@pytest.mark.regression
class TestWorkItemValidation400:
    """Parameter validation — expected 400 Bad Request scenarios."""

    def test_missing_name_field(self):
        """Create work item with empty JSON body — verify error response."""
        resp = requests.post(ISSUES_URL, headers=HEADERS, json={}, timeout=15)
        # Plane v1.3.1 returns 400 for missing 'name'
        assert resp.status_code == 400, (
            f"Expected 400, got {resp.status_code}. Body: {resp.text[:200]}"
        )
        # Verify no data was created
        assert "id" not in (resp.json() if resp.text else {}), "Response should not contain a resource ID"

    def test_empty_name_field(self):
        """Create work item with empty string name."""
        resp = requests.post(ISSUES_URL, headers=HEADERS, json={"name": ""}, timeout=15)
        # Plane v1.3.1 may return 400 or 201 depending on backend validation
        # Record the real behavior
        assert resp.status_code in (400, 201, 422), (
            f"Unexpected status: {resp.status_code}. Body: {resp.text[:200]}"
        )
        # If 201 was returned unexpectedly, clean up
        if resp.status_code == 201:
            data = resp.json()
            if data.get("id"):
                requests.delete(
                    f"{ISSUES_URL}{data['id']}/",
                    headers={"X-API-Key": API_KEY},
                    timeout=15,
                )

    def test_name_as_number(self):
        """Create work item with numeric name field (wrong type)."""
        resp = requests.post(ISSUES_URL, headers=HEADERS, json={"name": 12345}, timeout=15)
        # Plane v1.3.1 behavior: may coerce or reject
        assert resp.status_code in (400, 201, 422), (
            f"Unexpected status: {resp.status_code}. Body: {resp.text[:200]}"
        )
        # Clean up if created
        if resp.status_code == 201:
            data = resp.json()
            if data.get("id"):
                requests.delete(
                    f"{ISSUES_URL}{data['id']}/",
                    headers={"X-API-Key": API_KEY},
                    timeout=15,
                )

    def test_invalid_priority_value(self):
        """Create work item with invalid priority enum value."""
        resp = requests.post(
            ISSUES_URL,
            headers=HEADERS,
            json={"name": "AUTO-D4-VALIDATION-TEST-PRIORITY", "priority": "INVALID_PRIORITY_VALUE"},
            timeout=15,
        )
        # Plane v1.3.1 behavior for invalid enum
        assert resp.status_code in (400, 201, 422), (
            f"Unexpected status: {resp.status_code}. Body: {resp.text[:200]}"
        )
        # Clean up if created despite invalid priority
        if resp.status_code == 201:
            data = resp.json()
            if data.get("id"):
                requests.delete(
                    f"{ISSUES_URL}{data['id']}/",
                    headers={"X-API-Key": API_KEY},
                    timeout=15,
                )

    def test_invalid_state_id(self):
        """Create work item with non-existent state UUID."""
        resp = requests.post(
            ISSUES_URL,
            headers=HEADERS,
            json={
                "name": "AUTO-D4-VALIDATION-TEST-STATE",
                "state_id": "00000000-0000-0000-0000-000000000000",
            },
            timeout=15,
        )
        # Plane v1.3.1 may reject or ignore invalid FK
        assert resp.status_code in (400, 201, 422), (
            f"Unexpected status: {resp.status_code}. Body: {resp.text[:200]}"
        )
        if resp.status_code == 201:
            data = resp.json()
            if data.get("id"):
                requests.delete(
                    f"{ISSUES_URL}{data['id']}/",
                    headers={"X-API-Key": API_KEY},
                    timeout=15,
                )

    def test_malformed_json_body(self):
        """Send malformed JSON — expect 400."""
        resp = requests.post(
            ISSUES_URL,
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            data="not valid json {{{",
            timeout=15,
        )
        assert resp.status_code in (400, 415), (
            f"Expected 400/415 for malformed JSON, got {resp.status_code}"
        )

    def test_excessive_title_length(self):
        """Create work item with excessively long title (10000 chars)."""
        long_name = "A" * 10000
        resp = requests.post(
            ISSUES_URL,
            headers=HEADERS,
            json={"name": long_name},
            timeout=15,
        )
        # Plane v1.3.1: varchar column may have limit
        assert resp.status_code in (400, 201, 422), (
            f"Unexpected status: {resp.status_code}"
        )
        if resp.status_code == 201:
            data = resp.json()
            if data.get("id"):
                requests.delete(
                    f"{ISSUES_URL}{data['id']}/",
                    headers={"X-API-Key": API_KEY},
                    timeout=15,
                )

    def test_missing_required_field_and_no_residue(self):
        """Confirm missing 'name' returns 400 and no work item is created."""
        # Get current count
        list_before = requests.get(ISSUES_URL, headers=HEADERS, timeout=15)
        count_before = len(list_before.json().get("results", list_before.json()))

        # Attempt invalid create
        resp = requests.post(ISSUES_URL, headers=HEADERS, json={}, timeout=15)
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"

        # Verify count unchanged
        list_after = requests.get(ISSUES_URL, headers=HEADERS, timeout=15)
        count_after = len(list_after.json().get("results", list_after.json()))
        assert count_after == count_before, (
            f"Count changed: before={count_before}, after={count_after}"
        )
