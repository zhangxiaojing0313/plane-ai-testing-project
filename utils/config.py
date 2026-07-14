"""
Plane API configuration loaded from .env.

API Key is loaded into memory only and never printed, logged, or written to disk.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)


class APIConfig:
    """Plane API configuration from environment variables."""

    BASE_URL: str = os.getenv("PLANE_BASE_URL", "http://192.168.146.132:8090")
    API_BASE_URL: str = os.getenv("PLANE_API_BASE_URL", f"{BASE_URL}/api")
    API_KEY: str = os.getenv("PLANE_API_KEY", "")
    WORKSPACE_SLUG: str = os.getenv("PLANE_WORKSPACE_SLUG", "qa-lab")
    PROJECT_ID: str = os.getenv("PLANE_PROJECT_ID", "")

    # Request defaults
    DEFAULT_TIMEOUT: int = 15
    MAX_RETRIES: int = 2

    @classmethod
    def get_headers(cls) -> dict:
        """Return request headers with API Key (value never logged)."""
        return {
            "X-API-Key": cls.API_KEY,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @classmethod
    def redact(cls, text: str) -> str:
        """Redact API Key from any text before logging."""
        if cls.API_KEY and cls.API_KEY in text:
            text = text.replace(cls.API_KEY, "[REDACTED]")
        return text

    @classmethod
    def validate(cls) -> list:
        """Check required config values are set. Returns list of missing keys."""
        missing = []
        if not cls.BASE_URL:
            missing.append("PLANE_BASE_URL")
        if not cls.API_KEY:
            missing.append("PLANE_API_KEY")
        if not cls.WORKSPACE_SLUG:
            missing.append("PLANE_WORKSPACE_SLUG")
        if not cls.PROJECT_ID:
            missing.append("PLANE_PROJECT_ID")
        return missing

    @classmethod
    def summary(cls) -> str:
        """Return a safe summary of config (no secrets)."""
        return (
            f"BASE_URL={cls.BASE_URL}\n"
            f"API_BASE_URL={cls.API_BASE_URL}\n"
            f"WORKSPACE_SLUG={cls.WORKSPACE_SLUG}\n"
            f"PROJECT_ID={cls.PROJECT_ID}\n"
            f"API_KEY=configured={bool(cls.API_KEY)}"
        )
