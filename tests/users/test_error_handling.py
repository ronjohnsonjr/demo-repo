"""Error handling tests for user endpoints.

Validates HTTP 400, 401, 403, 422, and 429 responses using mocked HTTP calls.
"""

from unittest.mock import MagicMock

import pytest
import requests

from data.constants import (
    BASE_URL,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE,
    HTTP_429_RATE_LIMITED,
    ENDPOINT_USERS,
)
from utils.http.client import GitHubHTTPClient
from utils.testing.helpers import assert_status_code


def _mock_client(status_code: int) -> GitHubHTTPClient:
    """Return a GitHubHTTPClient whose GET always returns status_code."""
    client = GitHubHTTPClient(base_url=BASE_URL)
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.headers = {}
    mock_resp.url = f"{BASE_URL}/users/test"
    mock_resp.text = f'{{"message": "HTTP {status_code}"}}'
    client.session.get = MagicMock(return_value=mock_resp)
    return client


@pytest.mark.test_error_handling
class TestUserErrorHandling:
    """Error code tests for /users/{username} endpoint."""

    def test_bad_request_400(self):
        """Verify 400 is returned for a malformed user request.

        Setup: Mock client returning 400.
        Action: GET /users/... endpoint.
        Assertions: Status code is 400.
        """
        # Setup
        client = _mock_client(HTTP_400_BAD_REQUEST)

        # Action
        resp = client.get(ENDPOINT_USERS.format(username="bad-user"))

        # Assertions
        assert_status_code(resp, HTTP_400_BAD_REQUEST)

    def test_unauthorized_401(self):
        """Verify 401 is returned for requests without valid authentication.

        Setup: Mock client returning 401.
        Action: GET /users endpoint.
        Assertions: Status code is 401.
        """
        # Setup
        client = _mock_client(HTTP_401_UNAUTHORIZED)

        # Action
        resp = client.get("/users/octocat")

        # Assertions
        assert_status_code(resp, HTTP_401_UNAUTHORIZED)

    def test_forbidden_403(self):
        """Verify 403 is returned when access is forbidden.

        Setup: Mock client returning 403.
        Action: GET /users endpoint.
        Assertions: Status code is 403.
        """
        # Setup
        client = _mock_client(HTTP_403_FORBIDDEN)

        # Action
        resp = client.get("/users/private-user")

        # Assertions
        assert_status_code(resp, HTTP_403_FORBIDDEN)

    def test_unprocessable_422(self):
        """Verify 422 is returned for unprocessable entity payloads.

        Setup: Mock client returning 422.
        Action: GET /users endpoint.
        Assertions: Status code is 422.
        """
        # Setup
        client = _mock_client(HTTP_422_UNPROCESSABLE)

        # Action
        resp = client.get("/users/invalid-payload")

        # Assertions
        assert_status_code(resp, HTTP_422_UNPROCESSABLE)

    def test_rate_limited_429(self):
        """Verify 429 is returned when the rate limit is exceeded.

        Setup: Mock client returning 429.
        Action: GET /users endpoint.
        Assertions: Status code is 429.
        """
        # Setup
        client = _mock_client(HTTP_429_RATE_LIMITED)

        # Action
        resp = client.get("/users/octocat")

        # Assertions
        assert_status_code(resp, HTTP_429_RATE_LIMITED)
