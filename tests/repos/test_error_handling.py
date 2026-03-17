"""Error handling tests for repository endpoints.

Validates HTTP 400, 401, 403, 422, and 429 responses using mocked HTTP calls
so no live network requests are made.
"""

import unittest.mock
from unittest.mock import MagicMock, patch

import pytest
import requests

from data.constants import (
    BASE_URL,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE,
    HTTP_429_RATE_LIMITED,
)
from utils.http.client import GitHubHTTPClient
from utils.testing.helpers import assert_status_code


def _mock_client_with_response(status_code: int) -> GitHubHTTPClient:
    """Return a GitHubHTTPClient whose session.get always returns status_code."""
    client = GitHubHTTPClient(base_url=BASE_URL)
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.headers = {}
    mock_resp.url = f"{BASE_URL}/test"
    mock_resp.text = f'{{"message": "HTTP {status_code}"}}'
    client.session.get = MagicMock(return_value=mock_resp)
    return client


@pytest.mark.test_error_handling
class TestRepoBadRequest:
    """Test 400 Bad Request handling for repository endpoints."""

    def test_bad_request_returns_400(self):
        """Verify that a 400 response is returned unchanged for bad requests.

        Setup: Mock HTTP client configured to return 400.
        Action: GET a repository endpoint.
        Assertions: Response status code is 400.
        """
        # Setup
        client = _mock_client_with_response(HTTP_400_BAD_REQUEST)

        # Action
        resp = client.get("/repos/octocat/Hello-World")

        # Assertions
        assert_status_code(resp, HTTP_400_BAD_REQUEST)


@pytest.mark.test_error_handling
class TestRepoUnauthorized:
    """Test 401 Unauthorized handling for repository endpoints."""

    def test_unauthorized_returns_401(self):
        """Verify that a 401 response is detected when auth token is invalid.

        Setup: Mock HTTP client configured to return 401.
        Action: GET a repository endpoint without a valid token.
        Assertions: Response status code is 401.
        """
        # Setup
        client = _mock_client_with_response(HTTP_401_UNAUTHORIZED)

        # Action
        resp = client.get("/repos/octocat/Hello-World")

        # Assertions
        assert_status_code(resp, HTTP_401_UNAUTHORIZED)

    def test_unauthorized_on_private_endpoint(self):
        """Verify 401 is returned when accessing a restricted endpoint without auth.

        Setup: Mock HTTP client returning 401.
        Action: GET /user (authenticated-only endpoint).
        Assertions: Response status code is 401.
        """
        # Setup
        client = _mock_client_with_response(HTTP_401_UNAUTHORIZED)

        # Action
        resp = client.get("/user")

        # Assertions
        assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.test_error_handling
class TestRepoForbidden:
    """Test 403 Forbidden handling for repository endpoints."""

    def test_forbidden_returns_403(self):
        """Verify that a 403 response is detected for forbidden actions.

        Setup: Mock HTTP client configured to return 403.
        Action: GET a protected repository endpoint.
        Assertions: Response status code is 403.
        """
        # Setup
        client = _mock_client_with_response(HTTP_403_FORBIDDEN)

        # Action
        resp = client.get("/repos/private-org/private-repo")

        # Assertions
        assert_status_code(resp, HTTP_403_FORBIDDEN)


@pytest.mark.test_error_handling
class TestRepoUnprocessable:
    """Test 422 Unprocessable Entity handling."""

    def test_unprocessable_entity_returns_422(self):
        """Verify that a 422 response is detected for validation errors.

        Setup: Mock HTTP client configured to return 422.
        Action: GET an endpoint that triggers a validation error.
        Assertions: Response status code is 422.
        """
        # Setup
        client = _mock_client_with_response(HTTP_422_UNPROCESSABLE)

        # Action
        resp = client.get("/repos/octocat/Hello-World/issues")

        # Assertions
        assert_status_code(resp, HTTP_422_UNPROCESSABLE)


@pytest.mark.test_error_handling
class TestRepoRateLimited:
    """Test 429 Rate Limited handling for repository endpoints."""

    def test_rate_limited_returns_429(self):
        """Verify that a 429 response is detected when rate limit is exceeded.

        Setup: Mock HTTP client configured to return 429.
        Action: GET a repository endpoint.
        Assertions: Response status code is 429.
        """
        # Setup
        client = _mock_client_with_response(HTTP_429_RATE_LIMITED)

        # Action
        resp = client.get("/repos/octocat/Hello-World")

        # Assertions
        assert_status_code(resp, HTTP_429_RATE_LIMITED)

    def test_rate_limited_status_code_is_429(self):
        """Verify the rate-limited constant equals 429.

        Setup: Import the HTTP_429_RATE_LIMITED constant.
        Action: Check its value.
        Assertions: Value equals 429.
        """
        # Assertions
        assert HTTP_429_RATE_LIMITED == 429
