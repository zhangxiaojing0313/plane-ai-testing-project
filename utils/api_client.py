"""
Plane API client with requests.Session for connection reuse.

Features:
- Session-based connection pooling
- Configurable timeout (default 15s)
- X-API-Key redaction in all log/error output
- Safe request/response logging (no secrets)
"""

import logging
import time
from typing import Optional, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.config import APIConfig

logger = logging.getLogger("plane-api-client")


class APIClient:
    """HTTP client for Plane API with session reuse and safe logging."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
    ):
        self.base_url = (base_url or APIConfig.BASE_URL).rstrip("/")
        self.api_key = api_key or APIConfig.API_KEY
        self.timeout = timeout or APIConfig.DEFAULT_TIMEOUT

        self.session = requests.Session()

        # Retry strategy for transient errors
        retry_strategy = Retry(
            total=APIConfig.MAX_RETRIES,
            backoff_factor=0.5,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _headers(self, extra: dict | None = None) -> dict:
        """Build request headers. X-API-Key never printed."""
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if extra:
            headers.update(extra)
        return headers

    @staticmethod
    def _safe_headers(headers: dict) -> dict:
        """Return a copy of headers with X-API-Key redacted for logging."""
        safe = {}
        for k, v in headers.items():
            if k.lower() == "x-api-key":
                safe[k] = "[REDACTED]"
            else:
                safe[k] = v
        return safe

    def _url(self, path: str) -> str:
        """Build full URL from path (handles both relative and absolute)."""
        if path.startswith("http"):
            return path
        return urljoin(self.base_url + "/", path.lstrip("/"))

    # ---- Core request methods ----

    def get(
        self,
        path: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int | None = None,
    ) -> requests.Response:
        """GET request with safe logging."""
        url = self._url(path)
        hdrs = self._headers(headers)
        t = timeout or self.timeout

        logger.debug("GET %s params=%s headers=%s", url, params, self._safe_headers(hdrs))
        start = time.monotonic()

        try:
            resp = self.session.get(url, params=params, headers=hdrs, timeout=t)
        except requests.RequestException:
            logger.exception("GET %s failed", url)
            raise

        elapsed = time.monotonic() - start
        logger.info(
            "GET %s -> %s (%d bytes, %.2fs)",
            url,
            resp.status_code,
            len(resp.content),
            elapsed,
        )
        return resp

    def post(
        self,
        path: str,
        json: dict | None = None,
        data: Any = None,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int | None = None,
    ) -> requests.Response:
        """POST request with safe logging."""
        url = self._url(path)
        hdrs = self._headers(headers)
        t = timeout or self.timeout

        logger.debug("POST %s json=%s headers=%s", url, json, self._safe_headers(hdrs))
        start = time.monotonic()

        try:
            resp = self.session.post(
                url, json=json, data=data, params=params, headers=hdrs, timeout=t
            )
        except requests.RequestException:
            logger.exception("POST %s failed", url)
            raise

        elapsed = time.monotonic() - start
        logger.info(
            "POST %s -> %s (%d bytes, %.2fs)",
            url,
            resp.status_code,
            len(resp.content),
            elapsed,
        )
        return resp

    def patch(
        self,
        path: str,
        json: dict | None = None,
        headers: dict | None = None,
        timeout: int | None = None,
    ) -> requests.Response:
        """PATCH request with safe logging."""
        url = self._url(path)
        hdrs = self._headers(headers)
        t = timeout or self.timeout

        logger.debug("PATCH %s json=%s headers=%s", url, json, self._safe_headers(hdrs))
        start = time.monotonic()

        try:
            resp = self.session.patch(url, json=json, headers=hdrs, timeout=t)
        except requests.RequestException:
            logger.exception("PATCH %s failed", url)
            raise

        elapsed = time.monotonic() - start
        logger.info(
            "PATCH %s -> %s (%d bytes, %.2fs)",
            url,
            resp.status_code,
            len(resp.content),
            elapsed,
        )
        return resp

    def delete(
        self,
        path: str,
        headers: dict | None = None,
        timeout: int | None = None,
    ) -> requests.Response:
        """DELETE request with safe logging."""
        url = self._url(path)
        hdrs = self._headers(headers)
        t = timeout or self.timeout

        logger.debug("DELETE %s headers=%s", url, self._safe_headers(hdrs))
        start = time.monotonic()

        try:
            resp = self.session.delete(url, headers=hdrs, timeout=t)
        except requests.RequestException:
            logger.exception("DELETE %s failed", url)
            raise

        elapsed = time.monotonic() - start
        logger.info(
            "DELETE %s -> %s (%d bytes, %.2fs)",
            url,
            resp.status_code,
            len(resp.content),
            elapsed,
        )
        return resp

    # ---- Convenience helpers ----

    def get_json(
        self,
        path: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> tuple[requests.Response, dict | list | None]:
        """GET and parse JSON response. Returns (response, json_data)."""
        resp = self.get(path, params=params, headers=headers)
        try:
            data = resp.json()
        except ValueError:
            data = None
        return resp, data

    def close(self):
        """Close the underlying session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
