"""Tests for listing repositories (org repos, user repos).

Validates pagination, sorting, and filtering behavior.
"""

import pytest

from data.constants import DEFAULT_PER_PAGE, MAX_PER_PAGE
from data.repos_constants import TEST_REPO_OWNER
from utils.api.github_api import GitHubAPI


@pytest.mark.test_repos
class TestListOrgRepos:
    """GET /orgs/{org}/repos — list repositories for an organization."""

    def test_list_org_repos_returns_list(self, api: GitHubAPI):
        """Verify org repo listing returns a list."""
        repos = api.repos.list_repos("github")
        assert isinstance(repos, list)
        assert len(repos) > 0

    def test_list_org_repos_respects_per_page(self, api: GitHubAPI):
        """Verify per_page parameter limits results."""
        repos = api.repos.list_repos("google", per_page=5)
        assert len(repos) <= 5

    def test_list_org_repos_pagination(self, api: GitHubAPI):
        """Verify pagination returns different results per page."""
        page1 = api.repos.list_repos("microsoft", per_page=5, page=1)
        page2 = api.repos.list_repos("microsoft", per_page=5, page=2)

        page1_ids = {r["id"] for r in page1}
        page2_ids = {r["id"] for r in page2}
        assert page1_ids.isdisjoint(page2_ids), "Pages should not overlap"

    def test_each_repo_has_full_name(self, api: GitHubAPI):
        """Verify each repo in the listing has a full_name."""
        repos = api.repos.list_repos("github", per_page=10)
        for repo in repos:
            assert "full_name" in repo
            assert "/" in repo["full_name"]


@pytest.mark.test_repos
class TestListUserRepos:
    """GET /users/{username}/repos — list a user's repositories."""

    def test_list_user_repos_returns_list(self, api: GitHubAPI):
        """Verify user repo listing returns a list."""
        repos = api.users.list_user_repos(TEST_REPO_OWNER)
        assert isinstance(repos, list)
        assert len(repos) > 0

    def test_user_repos_belong_to_user(self, api: GitHubAPI):
        """Verify all repos belong to the queried user."""
        repos = api.users.list_user_repos(TEST_REPO_OWNER, per_page=10)
        for repo in repos:
            assert repo["owner"]["login"] == TEST_REPO_OWNER
