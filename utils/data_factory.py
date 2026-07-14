"""
Test data factory for Plane API automation.

Generates test-safe identifiers and payloads.
All created resources follow the AUTO-D3 naming convention for easy identification and cleanup.
"""

from datetime import datetime, timezone


def utc_timestamp() -> str:
    """Return UTC timestamp string suitable for test resource names."""
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def test_issue_title() -> str:
    """Generate a unique test Work Item title.

    Format: AUTO-D3-<UTC timestamp>-API-TEST
    """
    return f"AUTO-D3-{utc_timestamp()}-API-TEST"


def make_issue_payload(
    name: str | None = None,
    description_html: str | None = None,
    priority: str | None = None,
    state_id: str | None = None,
) -> dict:
    """Build a minimal create-issue payload.

    Only `name` is required by the Plane API.
    """
    payload: dict = {"name": name or test_issue_title()}
    if description_html is not None:
        payload["description_html"] = description_html
    if priority is not None:
        payload["priority"] = priority
    if state_id is not None:
        payload["state"] = state_id
    return payload


def make_issue_update_payload(
    name: str | None = None,
    description_html: str | None = None,
    priority: str | None = None,
    state_id: str | None = None,
) -> dict:
    """Build a partial update payload (only includes non-None fields)."""
    payload: dict = {}
    if name is not None:
        payload["name"] = name
    if description_html is not None:
        payload["description_html"] = description_html
    if priority is not None:
        payload["priority"] = priority
    if state_id is not None:
        payload["state"] = state_id
    return payload
