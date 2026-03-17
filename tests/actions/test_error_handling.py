"""Error handling tests for GitHub Actions endpoints.

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
    ENDPOINT_ACTIONS_WORKFLOWS,
)
from utils.http.client import GitHubHTTPClient
from utils.testing.helpers import assert_status_code


def _mock_client(status_code: int) -> GitHubHTTPClient:
    """Return a GitHubHTTPClient whose GET always returns status_code."""
    client = GitHubHTTPClient(base_url=BASE_URL)
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.headers = {}
    mock_resp.url = f"{BASE_URL}/repos/actions/checkout/actions/workflows"
    mock_resp.text = f'{{"message": "HTTP {status_code}"}}'
    client.session.get = MagicMock(return_value=mock_resp)
    return client


@pytest.mark.test_error_handling
class TestActionsErrorHandling:
    """Error code tests for GitHub Actions endpoints."""

    def test_bad_request_400(self):
        """Verify 400 for malformed Actions requests.

        Setup: Mock client returning 400.
        Action: GET workflows endpoint.
        Assertions: Status code is 400.
        """
        # Setup
        client = _mock_client(HTTP_400_BAD_REQUEST)

        # Action
        resp = client.get(ENDPOINT_ACTIONS_WORKFLOWS.format(owner="actions", repo="checkout"))

        # Assertions
        assert_status_code(resp, HTTP_400_BAD_REQUEST)

    def test_unauthorized_401(self):
        """Verify 401 for unauthenticated Actions requests.

        Setup: Mock client returning 401.
        Action: GET workflows endpoint.
        Assertions: Status code is 401.
        """
        # Setup
        client = _mock_client(HTTP_401_UNAUTHORIZED)

        # Action
        resp = client.get("/repos/actions/checkout/actions/workflows")

        # Assertions
        assert_status_code(resp, HTTP_401_UNAUTHORIZED)

    def test_forbidden_403(self):
        """Verify 403 for Actions on a private repository.

        Setup: Mock client returning 403.
        Action: GET workflows endpoint.
        Assertions: Status code is 403.
        """
        # Setup
        client = _mock_client(HTTP_403_FORBIDDEN)

        # Action
        resp = client.get("/repos/private-org/private-repo/actions/workflows")

        # Assertions
        assert_status_code(resp, HTTP_403_FORBIDDEN)

    def test_unprocessable_422(self):
        """Verify 422 for invalid workflow trigger parameters.

        Setup: Mock client returning 422.
        Action: GET workflows endpoint.
        Assertions: Status code is 422.
        """
        # Setup
        client = _mock_client(HTTP_422_UNPROCESSABLE)

        # Action
        resp = client.get("/repos/actions/checkout/actions/workflows")

        # Assertions
        assert_status_code(resp, HTTP_422_UNPROCESSABLE)

    def test_rate_limited_429(self):
        """Verify 429 for rate-limited Actions requests.

        Setup: Mock client returning 429.
        Action: GET workflows endpoint.
        Assertions: Status code is 429.
        """
        # Setup
        client = _mock_client(HTTP_429_RATE_LIMITED)

        # Action
        resp = client.get("/repos/actions/checkout/actions/workflows")

        # Assertions
        assert_status_code(resp, HTTP_429_RATE_LIMITED)
