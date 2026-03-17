"""Root conftest.py -- shared fixtures for GitHub API test automation."""

import json
import logging
import os
import time
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv

from data.constants import BASE_URL, GITHUB_API_VERSION
from utils.http.client import GitHubHTTPClient
from utils.api.github_api import GitHubAPI
from utils.rate_limiting.rate_limiter import RateLimiter
from utils.testing.helpers import generate_unique_suffix

load_dotenv()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Session-scoped fixtures (shared across all tests in a session)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def github_token() -> str | None:
    """Retrieve GitHub personal access token from env or config.

    Returns None for unauthenticated mode (lower rate limits apply).
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        config_path = Path("config/config.json")
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            token = config.get("github_token")
    if token:
        logger.info("GitHub token loaded -- authenticated mode (5000 req/hr)")
    else:
        logger.warning("No GitHub token found -- unauthenticated mode (60 req/hr)")
    return token


@pytest.fixture(scope="session")
def rate_limiter() -> RateLimiter:
    """Session-wide rate limiter to respect GitHub API limits."""
    return RateLimiter()


@pytest.fixture(scope="session")
def http_client(github_token, rate_limiter) -> GitHubHTTPClient:
    """Session-scoped HTTP client with auth headers and rate limiting."""
    client = GitHubHTTPClient(
        base_url=BASE_URL,
        token=github_token,
        api_version=GITHUB_API_VERSION,
        rate_limiter=rate_limiter,
    )
    logger.info("HTTP client initialized: base_url=%s", BASE_URL)
    return client


@pytest.fixture(scope="session")
def api(http_client) -> GitHubAPI:
    """Session-scoped GitHub API wrapper -- the primary interface for tests."""
    return GitHubAPI(client=http_client)


# ---------------------------------------------------------------------------
# Function-scoped fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def unique_suffix() -> str:
    """Generate a unique suffix for test resource names."""
    return generate_unique_suffix()


@pytest.fixture(autouse=True)
def _log_test_boundaries(request):
    """Log the start and end of every test for debugging."""
    test_name = request.node.name
    logger.info(">>> START: %s", test_name)
    start = time.time()
    yield
    elapsed = time.time() - start
    logger.info("<<< END:   %s (%.2fs)", test_name, elapsed)


# ---------------------------------------------------------------------------
# Pytest hooks
# ---------------------------------------------------------------------------


def pytest_configure(config):
    """Register custom markers."""
    for marker in [
        "test_repos: Repository endpoint tests",
        "test_users: User endpoint tests",
        "test_orgs: Organization endpoint tests",
        "test_search: Search endpoint tests",
        "test_issues: Issue endpoint tests",
        "test_gists: Gist endpoint tests",
        "test_actions: Actions endpoint tests",
        "smoke: Quick smoke tests for CI",
        "slow: Tests that take longer to run",
        "test_rate_limiting: Rate limiter unit tests",
        "test_http: HTTP client unit tests",
        "test_database: Database utility unit tests",
        "test_testing: Testing helper and API unit tests",
        "test_error_handling: Error handling tests for HTTP error codes",
    ]:
        config.addinivalue_line("markers", marker)
