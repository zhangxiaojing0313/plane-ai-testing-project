"""
Plane API States & Labels Tests (v1 API Key auth).

Covers:
- List project states
- List project labels (path: labels/, not issue-labels/ in v1)
"""

import pytest

from utils.api_client import APIClient


class TestStates:
    """Tests for GET /api/v1/.../states/."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_list_states_returns_200(self, client: APIClient, workspace_slug: str, project_id: str):
        """GET states returns 200 with a list."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/states/"
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
        assert len(items) > 0, "Expected at least one state (project defaults)"

    @pytest.mark.api
    @pytest.mark.regression
    def test_states_have_expected_fields(self, client: APIClient, workspace_slug: str, project_id: str):
        """Each state has id, name, color, and group fields."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/states/"
        resp = client.get(path)
        assert resp.status_code == 200
        data = resp.json()
        if isinstance(data, dict):
            items = data.get("results", [])
        else:
            items = data

        for state in items[:3]:
            for field in ["id", "name", "color", "group"]:
                assert field in state, f"State missing '{field}': keys={list(state.keys())}"


class TestLabels:
    """Tests for GET /api/v1/.../labels/ (v1 uses 'labels', not 'issue-labels')."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_list_labels_returns_200(self, client: APIClient, workspace_slug: str, project_id: str):
        """GET labels returns 200."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/labels/"
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

    @pytest.mark.api
    @pytest.mark.regression
    def test_labels_have_expected_fields(self, client: APIClient, workspace_slug: str, project_id: str):
        """Each label has id, name, and color fields."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/labels/"
        resp = client.get(path)
        assert resp.status_code == 200
        data = resp.json()
        if isinstance(data, dict):
            items = data.get("results", [])
        else:
            items = data

        if len(items) > 0:
            for label in items[:3]:
                for field in ["id", "name", "color"]:
                    assert field in label, (
                        f"Label missing '{field}': keys={list(label.keys())}"
                    )
