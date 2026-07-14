"""
Plane API Authentication Tests (v1 API Key auth).

Covers:
- Valid API Key → 200
- Missing API Key → 401/403 (v1 behavior)
- Invalid API Key → 403 (Plane v1.3.1 returns 403 for invalid tokens)
"""

import pytest
import requests

from utils.api_client import APIClient

USER_ME_PATH = "/api/v1/users/me/"


class TestAuthValidKey:
    """Tests with a valid API Key."""

    @pytest.mark.api
    @pytest.mark.smoke
    def test_valid_api_key_returns_200(self, client: APIClient):
        """GET /api/v1/users/me/ with valid X-API-Key returns 200 + user data."""
        resp = client.get(USER_ME_PATH)
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:500]}"
        )
        data = resp.json()
        assert "id" in data, f"Response missing 'id': {data}"
        assert "email" in data, "Response missing 'email'"

    @pytest.mark.api
    @pytest.mark.regression
    def test_valid_api_key_user_has_expected_fields(self, client: APIClient):
        """v1 User response includes core profile fields."""
        resp = client.get(USER_ME_PATH)
        assert resp.status_code == 200
        data = resp.json()
        # API v1 user response fields (confirmed from real response)
        expected_fields = ["id", "email", "first_name", "last_name", "display_name"]
        for field in expected_fields:
            assert field in data, f"Missing field '{field}' in v1 user response"


class TestAuthMissingKey:
    """Tests without an API Key."""

    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.negative
    def test_no_api_key_header_returns_auth_error(self):
        """GET /api/v1/users/me/ without X-API-Key header returns auth error (401 or 403)."""
        import requests as req

        from utils.config import APIConfig

        url = f"{APIConfig.BASE_URL}{USER_ME_PATH}"
        # Send request with NO X-API-Key header at all
        resp = req.get(url, headers={"Accept": "application/json"}, timeout=15)
        # Plane v1 returns either 401 or 403 for missing auth
        assert resp.status_code in (401, 403), (
            f"Expected 401 or 403, got {resp.status_code}: {resp.text[:500]}"
        )


class TestAuthInvalidKey:
    """Tests with an invalid API Key."""

    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.negative
    def test_invalid_api_key_returns_403(self):
        """GET /api/v1/users/me/ with invalid X-API-Key returns 403.

        Plane v1.3.1 returns 403 with 'Given API token is not valid' for bad tokens.
        """
        client = APIClient(api_key="plane_invalid_fake_key_12345")
        resp = client.get(USER_ME_PATH)
        assert resp.status_code == 403, (
            f"Expected 403, got {resp.status_code}: {resp.text[:500]}"
        )
        data = resp.json()
        assert "not valid" in data.get("detail", "").lower(), (
            f"Unexpected error message: {data}"
        )
        client.close()

    @pytest.mark.api
    @pytest.mark.negative
    def test_empty_api_key_returns_403(self):
        """GET /api/v1/users/me/ with X-API-Key: '' returns 403.

        Note: The API client's _headers method sends X-API-Key even when empty.
        Plane treats an empty API Key as invalid → 403.
        """
        import requests as req

        from utils.config import APIConfig

        url = f"{APIConfig.BASE_URL}{USER_ME_PATH}"
        resp = req.get(
            url,
            headers={"Accept": "application/json", "X-API-Key": ""},
            timeout=15,
        )
        # Plane v1.3.1: empty API key string returns auth error
        assert resp.status_code in (401, 403), (
            f"Expected 401/403 for empty API key, got {resp.status_code}: {resp.text[:300]}"
        )
