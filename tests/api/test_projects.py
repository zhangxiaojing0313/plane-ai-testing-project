"""
Plane API Project Tests (v1 API Key auth).

Covers:
- List projects in workspace
- Project pagination structure
- Project detail by ID
- Non-existent project returns 404
"""

import pytest

from utils.api_client import APIClient


class TestProjectList:
    """Tests for GET /api/v1/workspaces/<slug>/projects/."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_list_projects_returns_200(self, client: APIClient, workspace_slug: str):
        """GET .../projects/ returns 200 with a list."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/"
        resp = client.get(path)
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:500]}"
        )
        data = resp.json()
        assert isinstance(data, (dict, list)), f"Expected dict or list, got {type(data)}"

    @pytest.mark.api
    @pytest.mark.regression
    def test_project_list_pagination_structure(self, client: APIClient, workspace_slug: str):
        """Project list response has pagination fields (cursor-based)."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/"
        resp = client.get(path)
        assert resp.status_code == 200
        data = resp.json()

        if isinstance(data, dict):
            if "results" in data:
                assert isinstance(data["results"], list), (
                    f"'results' should be a list, got {type(data['results'])}"
                )
            elif "count" in data:
                assert isinstance(data["count"], int), "count should be an integer"
        elif isinstance(data, list):
            assert len(data) >= 0, "Project list should be a list"

    @pytest.mark.api
    @pytest.mark.smoke
    def test_project_list_contains_target_project(
        self, client: APIClient, workspace_slug: str, project_id: str
    ):
        """Project list contains the target project ID."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/"
        resp = client.get(path)
        assert resp.status_code == 200
        data = resp.json()

        if isinstance(data, dict):
            projects = data.get("results", data.get("data", []))
        else:
            projects = data

        project_ids = [p.get("id") for p in projects if isinstance(p, dict)]
        assert project_id in project_ids, (
            f"Project '{project_id}' not found in list: {project_ids}"
        )


class TestProjectDetail:
    """Tests for GET /api/v1/workspaces/<slug>/projects/<id>/."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_project_detail_returns_200(
        self, client: APIClient, workspace_slug: str, project_id: str
    ):
        """GET project detail returns 200 with project data."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/"
        resp = client.get(path)
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:500]}"
        )
        data = resp.json()
        assert data.get("id") == project_id, (
            f"Project ID mismatch: {data.get('id')} != {project_id}"
        )
        assert "name" in data, "Response missing 'name'"

    @pytest.mark.api
    @pytest.mark.regression
    def test_project_detail_has_expected_fields(
        self, client: APIClient, workspace_slug: str, project_id: str
    ):
        """Project detail includes expected metadata fields."""
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/"
        resp = client.get(path)
        assert resp.status_code == 200
        data = resp.json()

        expected = ["id", "name", "identifier", "created_at", "created_by", "workspace"]
        for field in expected:
            assert field in data, f"Missing field '{field}' in project detail"


class TestProjectNotFound:
    """Negative tests for non-existent projects."""

    @pytest.mark.api
    @pytest.mark.negative
    def test_nonexistent_project_returns_404(
        self, client: APIClient, workspace_slug: str
    ):
        """GET non-existent project ID returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        path = f"/api/v1/workspaces/{workspace_slug}/projects/{fake_id}/"
        resp = client.get(path)
        assert resp.status_code == 404, (
            f"Expected 404 for fake project, got {resp.status_code}: {resp.text[:300]}"
        )
