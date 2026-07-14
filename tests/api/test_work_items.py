"""
Plane API Work Item (Issue) Tests (v1 API Key auth).

Covers:
- List work items
- Get work item detail
- Non-existent work item returns 404
- Create/update/delete work item (destructive)
"""

import pytest

from utils.api_client import APIClient
from utils.data_factory import make_issue_payload, make_issue_update_payload, utc_timestamp


# ---------------------------------------------------------------------------
# Read-only tests
# ---------------------------------------------------------------------------


class TestWorkItemList:
    """Tests for GET /api/v1/.../projects/<pid>/issues/ (list)."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_list_issues_returns_200(self, client: APIClient, workspace_slug: str, project_id: str):
        """GET issues list returns 200."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues/"
        resp = client.get(path)
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:500]}"
        )
        data = resp.json()
        assert isinstance(data, (dict, list)), f"Expected dict/list, got {type(data)}"

    @pytest.mark.api
    @pytest.mark.regression
    def test_issue_list_pagination_structure(self, client: APIClient, workspace_slug: str, project_id: str):
        """Issue list response has pagination structure."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues/"
        resp = client.get(path)
        assert resp.status_code == 200
        data = resp.json()

        if isinstance(data, dict):
            assert "results" in data or "count" in data or "next_cursor" in data or "next" in data, (
                f"Pagination fields missing: keys={list(data.keys())[:10]}"
            )
            if "results" in data:
                assert isinstance(data["results"], list)

    @pytest.mark.api
    def test_issue_list_items_have_required_fields(self, client: APIClient, workspace_slug: str, project_id: str):
        """Each issue in the list has id, name, and sequence_id."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues/"
        resp = client.get(path)
        assert resp.status_code == 200
        data = resp.json()

        if isinstance(data, dict):
            items = data.get("results", [])
        elif isinstance(data, list):
            items = data
        else:
            items = []

        if len(items) > 0:
            for item in items[:3]:
                assert "id" in item, f"Issue missing 'id': {item}"
                assert "name" in item, f"Issue missing 'name': {item}"
                assert "sequence_id" in item or "project_id" in item, (
                    f"Issue missing required field: keys={list(item.keys())[:10]}"
                )


class TestWorkItemDetail:
    """Tests for GET /api/v1/.../projects/<pid>/issues/<id>/ (detail)."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_first_issue_detail(self, client: APIClient, workspace_slug: str, project_id: str):
        """Fetch the first issue from list, then get its detail."""
        list_path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues/"
        resp = client.get(list_path)
        assert resp.status_code == 200
        data = resp.json()

        if isinstance(data, dict):
            items = data.get("results", [])
        elif isinstance(data, list):
            items = data
        else:
            items = []

        if len(items) == 0:
            pytest.skip("No existing work items to fetch detail for")

        first_id = items[0]["id"]
        detail_path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues/{first_id}/"
        detail_resp = client.get(detail_path)
        assert detail_resp.status_code == 200, (
            f"Expected 200 for issue {first_id}, got {detail_resp.status_code}"
        )
        detail = detail_resp.json()
        assert detail.get("id") == first_id, (
            f"ID mismatch: {detail.get('id')} != {first_id}"
        )
        assert "name" in detail

    @pytest.mark.api
    @pytest.mark.regression
    def test_issue_detail_has_expected_fields(self, client: APIClient, workspace_slug: str, project_id: str):
        """Issue detail includes description_html, state, priority, etc."""
        list_path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues/"
        resp = client.get(list_path)
        assert resp.status_code == 200
        data = resp.json()

        if isinstance(data, dict):
            items = data.get("results", [])
        else:
            items = data

        if len(items) == 0:
            pytest.skip("No existing work items to validate detail fields")

        first_id = items[0]["id"]
        detail_resp = client.get(
            f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues/{first_id}/"
        )
        assert detail_resp.status_code == 200
        detail = detail_resp.json()

        expected_fields = ["id", "name", "sequence_id", "state", "priority", "created_at"]
        for field in expected_fields:
            assert field in detail, f"Missing field '{field}' in issue detail"


class TestWorkItemNotFound:
    """Negative tests for non-existent issues."""

    @pytest.mark.api
    @pytest.mark.negative
    def test_nonexistent_issue_returns_404(self, client: APIClient, workspace_slug: str, project_id: str):
        """GET non-existent issue ID returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues/{fake_id}/"
        resp = client.get(path)
        assert resp.status_code == 404, (
            f"Expected 404 for fake issue, got {resp.status_code}: {resp.text[:300]}"
        )


# ---------------------------------------------------------------------------
# Destructive (write) tests — isolated with auto-cleanup
# ---------------------------------------------------------------------------


class TestWorkItemLifecycle:
    """Create → Read → Update → Verify → Delete lifecycle test.

    Uses AUTO-D3 naming convention for easy identification.
    Cleanup runs regardless of pass/fail.
    """

    @pytest.fixture(autouse=True)
    def _cleanup(self, client: APIClient, workspace_slug: str, project_id: str):
        """Ensure test issue is deleted after test (pass or fail)."""
        self._created_id: str | None = None
        self._client = client
        self._ws = workspace_slug
        self._pid = project_id
        yield
        # Cleanup
        if self._created_id:
            try:
                del_path = f"/api/v1/workspaces/{self._ws}/projects/{self._pid}/issues/{self._created_id}/"
                del_resp = self._client.delete(del_path)
                if del_resp.status_code in (200, 204):
                    pass  # Successfully cleaned up
            except Exception:
                pass  # Best-effort cleanup

    @pytest.mark.api
    @pytest.mark.destructive
    def test_work_item_full_lifecycle(self, client: APIClient, workspace_slug: str, project_id: str):
        """Create → Read → Update → Verify → Delete a test work item."""
        base = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/issues"

        # 1. Count current items
        resp_before = client.get(f"{base}/")
        assert resp_before.status_code == 200
        data_before = resp_before.json()
        if isinstance(data_before, dict):
            count_before = len(data_before.get("results", []))
        else:
            count_before = len(data_before)

        # 2. Create
        title = f"AUTO-D3-{utc_timestamp()}-API-TEST"
        create_payload = {
            "name": title,
            "description_html": "<p>Automated test issue — will be deleted.</p>",
            "priority": "low",
        }
        create_resp = client.post(f"{base}/", json=create_payload)
        assert create_resp.status_code == 201, (
            f"Expected 201 on create, got {create_resp.status_code}: {create_resp.text[:500]}"
        )
        created = create_resp.json()
        created_id = created["id"]
        self._created_id = created_id
        assert created["name"] == title, (
            f"Title mismatch: {created['name']} != {title}"
        )

        # 3. Read back and verify
        detail_resp = client.get(f"{base}/{created_id}/")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["name"] == title
        assert detail["priority"] == "low"

        # 4. Update (change description and priority)
        update_payload = make_issue_update_payload(
            description_html="<p>Updated by automated test.</p>",
            priority="urgent",
        )
        patch_resp = client.patch(f"{base}/{created_id}/", json=update_payload)
        assert patch_resp.status_code in (200, 201, 204), (
            f"Expected 200/201/204 on update, got {patch_resp.status_code}: {patch_resp.text[:300]}"
        )

        # 5. Verify update
        verify_resp = client.get(f"{base}/{created_id}/")
        assert verify_resp.status_code == 200
        verify = verify_resp.json()
        assert "Updated by automated test" in verify.get("description_html", ""), (
            f"Description not updated: {verify.get('description_html', '')[:200]}"
        )
        assert verify["priority"] == "urgent", (
            f"Priority not updated: {verify['priority']}"
        )

        # 6. Delete
        del_resp = client.delete(f"{base}/{created_id}/")
        assert del_resp.status_code in (200, 204), (
            f"Expected 200/204 on delete, got {del_resp.status_code}: {del_resp.text[:300]}"
        )
        self._created_id = None  # Already deleted, skip cleanup

        # 7. Verify deletion (should 404 or not in list)
        verify_del = client.get(f"{base}/{created_id}/")
        assert verify_del.status_code in (404, 410), (
            f"Expected 404/410 after delete, got {verify_del.status_code}"
        )

        # 8. Confirm not in list
        resp_after = client.get(f"{base}/")
        assert resp_after.status_code == 200
        data_after = resp_after.json()
        if isinstance(data_after, dict):
            items_after = data_after.get("results", [])
        else:
            items_after = data_after
        after_ids = [i["id"] for i in items_after if isinstance(i, dict)]
        assert created_id not in after_ids, (
            f"Deleted issue {created_id} still appears in list"
        )
