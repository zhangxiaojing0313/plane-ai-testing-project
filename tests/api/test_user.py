"""
Plane API User Tests (v1 API Key auth).

Note: API v1 has limited user endpoints compared to the main /api/ prefix.
Only /api/v1/users/me/ is confirmed available.

v1 user response fields (confirmed):
  id, first_name, last_name, email, avatar, avatar_url, display_name
"""

import pytest

from utils.api_client import APIClient


class TestCurrentUser:
    """Tests for /api/v1/users/me/."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_current_user_returns_200(self, client: APIClient):
        """GET /api/v1/users/me/ returns 200 with valid user structure."""
        resp = client.get("/api/v1/users/me/")
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}"
        )
        data = resp.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
        assert "id" in data
        assert len(data["id"]) > 0

    @pytest.mark.api
    @pytest.mark.regression
    def test_current_user_has_expected_fields(self, client: APIClient):
        """v1 User response includes core profile fields."""
        resp = client.get("/api/v1/users/me/")
        assert resp.status_code == 200
        data = resp.json()
        # Confirmed v1 user response fields
        expected_fields = ["id", "email", "first_name", "last_name", "display_name"]
        for field in expected_fields:
            assert field in data, f"Missing field '{field}' in v1 user response"

    @pytest.mark.api
    def test_current_user_email_format(self, client: APIClient):
        """Current user email contains @ (sanity check)."""
        resp = client.get("/api/v1/users/me/")
        assert resp.status_code == 200
        data = resp.json()
        email = data.get("email", "")
        assert "@" in email, f"Email format invalid: {email}"
