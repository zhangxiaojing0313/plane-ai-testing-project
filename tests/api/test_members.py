"""
Plane API Members, Cycles & Modules Tests (v1 API Key auth).

Covers:
- List project members
- List project cycles
- List project modules
"""

import pytest

from utils.api_client import APIClient


class TestMembers:
    """Tests for GET /api/v1/.../members/."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_list_members_returns_200(self, client: APIClient, workspace_slug: str, project_id: str):
        """GET members returns 200 with a list."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/members/"
        resp = client.get(path)
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:500]}"
        )
        data = resp.json()
        if isinstance(data, dict):
            items = data.get("results", [])
        else:
            items = data
        assert isinstance(items, list), f"Expected list, got {type(items)}"
        assert len(items) > 0, "Expected at least one member (project creator)"

    @pytest.mark.api
    @pytest.mark.regression
    def test_members_have_member_field(self, client: APIClient, workspace_slug: str, project_id: str):
        """Each project member has a nested 'member' object with user details."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/members/"
        resp = client.get(path)
        assert resp.status_code == 200
        data = resp.json()
        if isinstance(data, dict):
            items = data.get("results", [])
        else:
            items = data

        for member_entry in items[:3]:
            assert "member" in member_entry or "id" in member_entry, (
                f"Member entry missing identifying field: keys={list(member_entry.keys())[:5]}"
            )


class TestCycles:
    """Tests for GET /api/v1/.../cycles/."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_list_cycles_returns_200(self, client: APIClient, workspace_slug: str, project_id: str):
        """GET cycles returns 200."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/cycles/"
        resp = client.get(path)
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:500]}"
        )
        data = resp.json()
        if isinstance(data, dict):
            items = data.get("results", [])
        else:
            items = data
        assert isinstance(items, list), f"Expected list, got {type(items)}"


class TestModules:
    """Tests for GET /api/v1/.../modules/."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_list_modules_returns_200(self, client: APIClient, workspace_slug: str, project_id: str):
        """GET modules returns 200."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/modules/"
        resp = client.get(path)
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:500]}"
        )
        data = resp.json()
        if isinstance(data, dict):
            items = data.get("results", [])
        else:
            items = data
        assert isinstance(items, list), f"Expected list, got {type(items)}"
