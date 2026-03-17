"""Unit tests for utils/http/client.py.

Validates GitHubHTTPClient construction, URL building, HTTP method dispatch,
exponential backoff retry logic, and session teardown.
"""

import unittest.mock
from unittest.mock import MagicMock, patch, call

import pytest
import requests
from tenacity import RetryError

from data.constants import BASE_URL, GITHUB_API_VERSION
from utils.http.client import GitHubHTTPClient
from utils.rate_limiting.rate_limiter import RateLimiter


def _make_mock_response(status_code: int = 200, json_body: dict | None = None) -> MagicMock:
    """Build a mock requests.Response with the given status code."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.headers = {}
    mock_resp.reason = requests.status_codes._codes.get(status_code, [""])[0]
    mock_resp.json.return_value = json_body or {}
    return mock_resp


@pytest.mark.test_http
class TestGitHubHTTPClientInit:
    """Tests for GitHubHTTPClient.__init__."""

    def test_base_url_trailing_slash_stripped(self):
        """Verify trailing slashes are removed from base_url.

        Setup: Instantiate client with a trailing-slash URL.
        Action: Read client.base_url.
        Assertions: The trailing slash is absent.
        """
        # Setup / Action
        client = GitHubHTTPClient(base_url="https://api.github.com/")

        # Assertions
        assert client.base_url == "https://api.github.com"

    def test_auth_header_set_when_token_provided(self):
        """Verify the Authorization header is set when a token is given.

        Setup: Instantiate client with a bearer token.
        Action: Read the Authorization header from the session.
        Assertions: Header value equals 'Bearer <token>'.
        """
        # Setup / Action
        client = GitHubHTTPClient(base_url=BASE_URL, token="test-token-xyz")

        # Assertions
        assert client.session.headers["Authorization"] == "Bearer test-token-xyz"

    def test_no_auth_header_without_token(self):
        """Verify Authorization header is absent when no token is provided.

        Setup: Instantiate client without a token.
        Action: Check session headers.
        Assertions: 'Authorization' key is not in the session headers.
        """
        # Setup / Action
        client = GitHubHTTPClient(base_url=BASE_URL)

        # Assertions
        assert "Authorization" not in client.session.headers

    def test_accept_header_set(self):
        """Verify the Accept header is set to the GitHub media type.

        Setup: Instantiate a default client.
        Action: Read the Accept header.
        Assertions: Header equals 'application/vnd.github+json'.
        """
        # Setup / Action
        client = GitHubHTTPClient(base_url=BASE_URL)

        # Assertions
        assert client.session.headers["Accept"] == "application/vnd.github+json"

    def test_api_version_header_set(self):
        """Verify X-GitHub-Api-Version header is set correctly.

        Setup: Instantiate client with a specific api_version.
        Action: Read the X-GitHub-Api-Version header.
        Assertions: Header matches the provided version string.
        """
        # Setup / Action
        client = GitHubHTTPClient(base_url=BASE_URL, api_version=GITHUB_API_VERSION)

        # Assertions
        assert client.session.headers["X-GitHub-Api-Version"] == GITHUB_API_VERSION

    def test_default_rate_limiter_created(self):
        """Verify a RateLimiter is created automatically when none is supplied.

        Setup: Instantiate client without rate_limiter argument.
        Action: Check client.rate_limiter.
        Assertions: rate_limiter is a RateLimiter instance.
        """
        # Setup / Action
        client = GitHubHTTPClient(base_url=BASE_URL)

        # Assertions
        assert isinstance(client.rate_limiter, RateLimiter)

    def test_custom_rate_limiter_used(self):
        """Verify a supplied RateLimiter is used instead of creating a new one.

        Setup: Create a custom RateLimiter and pass it to the client.
        Action: Read client.rate_limiter.
        Assertions: client.rate_limiter is the same object that was passed in.
        """
        # Setup
        custom_limiter = RateLimiter(buffer=10)

        # Action
        client = GitHubHTTPClient(base_url=BASE_URL, rate_limiter=custom_limiter)

        # Assertions
        assert client.rate_limiter is custom_limiter


@pytest.mark.test_http
class TestBuildUrl:
    """Tests for GitHubHTTPClient._build_url."""

    def test_combines_base_and_endpoint(self):
        """Verify endpoint is appended to base_url correctly.

        Setup: Client with base_url='https://api.github.com'.
        Action: Call _build_url('/repos/octocat/Hello-World').
        Assertions: Returns the full URL string.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)

        # Action
        url = client._build_url("/repos/octocat/Hello-World")

        # Assertions
        assert url == "https://api.github.com/repos/octocat/Hello-World"

    def test_strips_leading_slash_from_endpoint(self):
        """Verify leading slashes on the endpoint are not doubled.

        Setup: Client with base_url='https://api.github.com'.
        Action: Call _build_url with a leading slash.
        Assertions: URL contains exactly one slash between host and path.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)

        # Action
        url = client._build_url("/users/octocat")

        # Assertions
        assert url == "https://api.github.com/users/octocat"
        assert "//users" not in url


@pytest.mark.test_http
class TestGetMethod:
    """Tests for GitHubHTTPClient.get."""

    def test_successful_get_returns_response(self):
        """Verify a successful GET returns the mock response.

        Setup: Mock session.get to return a 200 response.
        Action: Call client.get('/users/octocat').
        Assertions: Response status code is 200.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)
        mock_response = _make_mock_response(200)
        client.session.get = MagicMock(return_value=mock_response)

        # Action
        response = client.get("/users/octocat")

        # Assertions
        assert response.status_code == 200

    def test_get_passes_params_to_session(self):
        """Verify query params are forwarded to requests.Session.get.

        Setup: Mock session.get.
        Action: Call client.get with params={'per_page': 10}.
        Assertions: session.get was called with the params argument.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)
        mock_response = _make_mock_response(200)
        client.session.get = MagicMock(return_value=mock_response)

        # Action
        client.get("/repos", params={"per_page": 10})

        # Assertions
        call_kwargs = client.session.get.call_args[1]
        assert call_kwargs["params"] == {"per_page": 10}

    def test_get_updates_rate_limiter_headers(self):
        """Verify response headers are passed to the rate limiter after each GET.

        Setup: Mock session.get with a response containing X-RateLimit-Remaining.
        Action: Call client.get.
        Assertions: rate_limiter.update_from_headers is called with the response headers.
        """
        # Setup
        mock_limiter = MagicMock()  # no spec -- allows attribute access freely
        mock_limiter.state.remaining = 60

        client = GitHubHTTPClient(base_url=BASE_URL, rate_limiter=mock_limiter)
        mock_response = _make_mock_response(200)
        mock_response.headers = {"X-RateLimit-Remaining": "4999"}
        client.session.get = MagicMock(return_value=mock_response)

        # Action
        client.get("/users/octocat")

        # Assertions
        mock_limiter.update_from_headers.assert_called_once_with({"X-RateLimit-Remaining": "4999"})


@pytest.mark.test_http
class TestPostMethod:
    """Tests for GitHubHTTPClient.post."""

    def test_successful_post_returns_response(self):
        """Verify POST returns the response from the underlying session.

        Setup: Mock session.post to return a 201 response.
        Action: Call client.post('/repos/octocat/Hello-World/issues', json_data={...}).
        Assertions: Response status code is 201.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)
        mock_response = _make_mock_response(201)
        client.session.post = MagicMock(return_value=mock_response)

        # Action
        response = client.post("/repos/octocat/Hello-World/issues", json_data={"title": "Bug"})

        # Assertions
        assert response.status_code == 201

    def test_post_sends_json_body(self):
        """Verify the JSON body is forwarded to requests.Session.post.

        Setup: Mock session.post.
        Action: Call client.post with a json_data dict.
        Assertions: session.post was called with json=json_data.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)
        mock_response = _make_mock_response(201)
        client.session.post = MagicMock(return_value=mock_response)
        body = {"title": "Test issue", "body": "Description"}

        # Action
        client.post("/issues", json_data=body)

        # Assertions
        call_kwargs = client.session.post.call_args[1]
        assert call_kwargs["json"] == body


@pytest.mark.test_http
class TestPatchMethod:
    """Tests for GitHubHTTPClient.patch."""

    def test_successful_patch_returns_response(self):
        """Verify PATCH returns the session response.

        Setup: Mock session.patch to return a 200 response.
        Action: Call client.patch with a json body.
        Assertions: Response status code is 200.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)
        mock_response = _make_mock_response(200)
        client.session.patch = MagicMock(return_value=mock_response)

        # Action
        response = client.patch("/repos/octocat/Hello-World", json_data={"description": "Updated"})

        # Assertions
        assert response.status_code == 200


@pytest.mark.test_http
class TestPutMethod:
    """Tests for GitHubHTTPClient.put."""

    def test_successful_put_returns_response(self):
        """Verify PUT returns the session response.

        Setup: Mock session.put to return a 204 response.
        Action: Call client.put.
        Assertions: Response status code is 204.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)
        mock_response = _make_mock_response(204)
        client.session.put = MagicMock(return_value=mock_response)

        # Action
        response = client.put("/user/starred/octocat/Hello-World")

        # Assertions
        assert response.status_code == 204


@pytest.mark.test_http
class TestDeleteMethod:
    """Tests for GitHubHTTPClient.delete."""

    def test_successful_delete_returns_response(self):
        """Verify DELETE returns the session response.

        Setup: Mock session.delete to return a 204 response.
        Action: Call client.delete.
        Assertions: Response status code is 204.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)
        mock_response = _make_mock_response(204)
        client.session.delete = MagicMock(return_value=mock_response)

        # Action
        response = client.delete("/repos/octocat/Hello-World/labels/99")

        # Assertions
        assert response.status_code == 204


@pytest.mark.test_http
class TestCloseMethod:
    """Tests for GitHubHTTPClient.close."""

    def test_close_calls_session_close(self):
        """Verify close() delegates to the underlying session.

        Setup: Instantiate a client.
        Action: Call client.close().
        Assertions: session.close() was called exactly once.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)
        client.session.close = MagicMock()

        # Action
        client.close()

        # Assertions
        client.session.close.assert_called_once()


@pytest.mark.test_http
class TestRetryLogic:
    """Tests for retry behavior (exponential backoff on transient errors)."""

    def test_retries_on_connection_error_then_succeeds(self):
        """Verify the client retries after a transient ConnectionError and succeeds.

        Setup: Mock session.get to raise ConnectionError once, then return 200.
        Action: Call client.get.
        Assertions: session.get is called twice and the response is returned.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)
        mock_response = _make_mock_response(200)

        client.session.get = MagicMock(
            side_effect=[requests.exceptions.ConnectionError("timeout"), mock_response]
        )

        # Action -- patch sleep to avoid waiting
        with patch("time.sleep"):
            response = client.get("/users/octocat")

        # Assertions
        assert response.status_code == 200
        assert client.session.get.call_count == 2

    def test_exhausts_retries_and_raises(self):
        """Verify RetryError is raised after all retry attempts are exhausted.

        Setup: Mock session.get to always raise ConnectionError.
        Action: Call client.get.
        Assertions: tenacity.RetryError is raised after 3 attempts.
        """
        # Setup
        client = GitHubHTTPClient(base_url=BASE_URL)
        client.session.get = MagicMock(
            side_effect=requests.exceptions.ConnectionError("persistent failure")
        )

        # Action / Assertions
        with patch("time.sleep"):
            with pytest.raises(RetryError):
                client.get("/users/octocat")

        # All 3 attempts were made
        assert client.session.get.call_count == 3
