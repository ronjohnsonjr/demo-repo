"""Tests for GitHub Search API endpoints.

Validates search across repositories, users, issues, and code.
"""

import pytest
from jsonschema import validate

from data.search_constants import (
    SEARCH_QUERIES_ISSUES,
    SEARCH_QUERIES_REPOS,
    SEARCH_QUERIES_USERS,
    SEARCH_REQUIRED_FIELDS,
)
from utils.api.github_api import GitHubAPI
from utils.testing.helpers import assert_json_keys
from utils.testing.schemas import SEARCH_RESULT_SCHEMA


@pytest.mark.test_search
class TestSearchRepos:
    """GET /search/repositories — search for repositories."""

    def test_search_repos_returns_results(self, api: GitHubAPI):
        """Verify a broad search returns results."""
        result = api.search.search_repos("language:python stars:>50000")
        assert result["total_count"] > 0
        assert len(result["items"]) > 0

    def test_search_repos_response_schema(self, api: GitHubAPI):
        """Verify search response matches expected schema."""
        result = api.search.search_repos("tetris")
        validate(instance=result, schema=SEARCH_RESULT_SCHEMA)

    def test_search_repos_required_fields(self, api: GitHubAPI):
        """Verify search response has required fields."""
        result = api.search.search_repos("django")
        assert_json_keys(result, SEARCH_REQUIRED_FIELDS)

    def test_search_repos_respects_per_page(self, api: GitHubAPI):
        """Verify per_page limits the number of items."""
        result = api.search.search_repos("python", per_page=3)
        assert len(result["items"]) <= 3

    @pytest.mark.parametrize("query", SEARCH_QUERIES_REPOS)
    def test_search_repos_various_queries(self, api: GitHubAPI, query: str):
        """Verify various search queries return results."""
        result = api.search.search_repos(query)
        assert result["total_count"] > 0

    def test_search_repos_empty_query_returns_error(self, api: GitHubAPI):
        """Verify empty/invalid search returns a validation error."""
        resp = api.client.get("/search/repositories", params={"q": ""})
        assert resp.status_code == 422


@pytest.mark.test_search
class TestSearchUsers:
    """GET /search/users — search for users."""

    def test_search_users_returns_results(self, api: GitHubAPI):
        """Verify user search returns results."""
        result = api.search.search_users("torvalds")
        assert result["total_count"] > 0

    @pytest.mark.parametrize("query", SEARCH_QUERIES_USERS)
    def test_search_users_various_queries(self, api: GitHubAPI, query: str):
        """Verify various user search queries return results."""
        result = api.search.search_users(query)
        assert result["total_count"] > 0

    def test_search_users_items_have_login(self, api: GitHubAPI):
        """Verify each user result has a login field."""
        result = api.search.search_users("octocat")
        for item in result["items"][:5]:
            assert "login" in item


@pytest.mark.test_search
class TestSearchIssues:
    """GET /search/issues — search for issues and pull requests."""

    def test_search_issues_returns_results(self, api: GitHubAPI):
        """Verify issue search returns results."""
        result = api.search.search_issues("repo:facebook/react is:issue is:open")
        assert result["total_count"] > 0

    @pytest.mark.parametrize("query", SEARCH_QUERIES_ISSUES)
    def test_search_issues_various_queries(self, api: GitHubAPI, query: str):
        """Verify various issue queries return results."""
        result = api.search.search_issues(query)
        assert result["total_count"] > 0
