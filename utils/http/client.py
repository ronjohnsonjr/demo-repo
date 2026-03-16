"""GitHub HTTP client with authentication, rate limiting, and retry logic."""

import logging
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.rate_limiting.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class GitHubHTTPClient:
    """Low-level HTTP client for the GitHub REST API.

    Handles authentication headers, API versioning, rate-limit awareness,
    and automatic retries with exponential backoff.
    """

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        api_version: str = "2022-11-28",
        rate_limiter: RateLimiter | None = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.rate_limiter = rate_limiter or RateLimiter()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": api_version,
                "User-Agent": "github-api-automation-pytest/1.0",
            }
        )
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from a relative endpoint path."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> requests.Response:
        """Send a GET request with rate limiting and retries."""
        self.rate_limiter.wait_if_needed()
        url = self._build_url(endpoint)
        logger.debug("GET %s params=%s", url, params)
        response = self.session.get(url, params=params, timeout=self.timeout)
        self.rate_limiter.update_from_headers(response.headers)
        logger.debug("Response: %s %s", response.status_code, response.reason)
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def post(self, endpoint: str, json_data: dict[str, Any] | None = None) -> requests.Response:
        """Send a POST request with rate limiting and retries."""
        self.rate_limiter.wait_if_needed()
        url = self._build_url(endpoint)
        logger.debug("POST %s body=%s", url, json_data)
        response = self.session.post(url, json=json_data, timeout=self.timeout)
        self.rate_limiter.update_from_headers(response.headers)
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def patch(self, endpoint: str, json_data: dict[str, Any] | None = None) -> requests.Response:
        """Send a PATCH request with rate limiting and retries."""
        self.rate_limiter.wait_if_needed()
        url = self._build_url(endpoint)
        logger.debug("PATCH %s body=%s", url, json_data)
        response = self.session.patch(url, json=json_data, timeout=self.timeout)
        self.rate_limiter.update_from_headers(response.headers)
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def put(self, endpoint: str, json_data: dict[str, Any] | None = None) -> requests.Response:
        """Send a PUT request with rate limiting and retries."""
        self.rate_limiter.wait_if_needed()
        url = self._build_url(endpoint)
        logger.debug("PUT %s body=%s", url, json_data)
        response = self.session.put(url, json=json_data, timeout=self.timeout)
        self.rate_limiter.update_from_headers(response.headers)
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def delete(self, endpoint: str) -> requests.Response:
        """Send a DELETE request with rate limiting and retries."""
        self.rate_limiter.wait_if_needed()
        url = self._build_url(endpoint)
        logger.debug("DELETE %s", url)
        response = self.session.delete(url, timeout=self.timeout)
        self.rate_limiter.update_from_headers(response.headers)
        return response

    def close(self) -> None:
        """Close the underlying requests session."""
        self.session.close()
