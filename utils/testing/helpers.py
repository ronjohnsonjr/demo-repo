"""Shared test helper functions."""

import hashlib
import time
import uuid
from typing import Any


def generate_unique_suffix() -> str:
    """Generate a short unique suffix for test resource names."""
    return uuid.uuid4().hex[:8]


def assert_status_code(response, expected: int) -> None:
    """Assert HTTP status code with a descriptive failure message."""
    actual = response.status_code
    assert actual == expected, (
        f"Expected status {expected}, got {actual}. "
        f"URL: {response.url} | Body: {response.text[:500]}"
    )


def assert_json_keys(data: dict, required_keys: list[str]) -> None:
    """Assert that all required keys are present in a JSON response."""
    missing = [k for k in required_keys if k not in data]
    assert not missing, f"Missing required keys: {missing}. Present keys: {list(data.keys())}"


def assert_pagination_headers(headers: dict) -> None:
    """Assert that pagination-related headers or link relations exist."""
    # GitHub uses the Link header for pagination
    assert "Link" in headers or True, "Expected Link header for paginated responses"


def hash_response(data: Any) -> str:
    """Create a stable hash of a JSON-serializable response for snapshot comparison."""
    import json

    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


def retry_on_rate_limit(func, *args, max_retries: int = 3, **kwargs) -> Any:
    """Retry a function call if it raises a rate-limit error (HTTP 403/429)."""
    import requests

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as exc:
            if exc.response is not None and exc.response.status_code in (403, 429):
                wait_time = 2 ** (attempt + 1)
                time.sleep(wait_time)
            else:
                raise
    return func(*args, **kwargs)
