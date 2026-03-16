"""High-level GitHub API facade — primary interface for test code.

Mirrors the pattern of SDK-first helpers: tests call ``api.repos.*``,
``api.users.*``, etc. instead of constructing HTTP requests directly.
"""

import logging
from typing import Any

from utils.http.client import GitHubHTTPClient

logger = logging.getLogger(__name__)


class ReposAPI:
    """Repository-related endpoints."""

    def __init__(self, client: GitHubHTTPClient) -> None:
        self._client = client

    def get_repo(self, owner: str, repo: str) -> dict[str, Any]:
        """GET /repos/{owner}/{repo}"""
        resp = self._client.get(f"/repos/{owner}/{repo}")
        resp.raise_for_status()
        return resp.json()

    def list_repos(self, org: str, per_page: int = 30, page: int = 1) -> list[dict[str, Any]]:
        """GET /orgs/{org}/repos"""
        resp = self._client.get(f"/orgs/{org}/repos", params={"per_page": per_page, "page": page})
        resp.raise_for_status()
        return resp.json()

    def list_branches(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """GET /repos/{owner}/{repo}/branches"""
        resp = self._client.get(f"/repos/{owner}/{repo}/branches")
        resp.raise_for_status()
        return resp.json()

    def list_tags(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """GET /repos/{owner}/{repo}/tags"""
        resp = self._client.get(f"/repos/{owner}/{repo}/tags")
        resp.raise_for_status()
        return resp.json()

    def list_contributors(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """GET /repos/{owner}/{repo}/contributors"""
        resp = self._client.get(f"/repos/{owner}/{repo}/contributors")
        resp.raise_for_status()
        return resp.json()

    def list_languages(self, owner: str, repo: str) -> dict[str, int]:
        """GET /repos/{owner}/{repo}/languages"""
        resp = self._client.get(f"/repos/{owner}/{repo}/languages")
        resp.raise_for_status()
        return resp.json()

    def get_readme(self, owner: str, repo: str) -> dict[str, Any]:
        """GET /repos/{owner}/{repo}/readme"""
        resp = self._client.get(f"/repos/{owner}/{repo}/readme")
        resp.raise_for_status()
        return resp.json()

    def list_commits(self, owner: str, repo: str, per_page: int = 10) -> list[dict[str, Any]]:
        """GET /repos/{owner}/{repo}/commits"""
        resp = self._client.get(f"/repos/{owner}/{repo}/commits", params={"per_page": per_page})
        resp.raise_for_status()
        return resp.json()


class UsersAPI:
    """User-related endpoints."""

    def __init__(self, client: GitHubHTTPClient) -> None:
        self._client = client

    def get_user(self, username: str) -> dict[str, Any]:
        """GET /users/{username}"""
        resp = self._client.get(f"/users/{username}")
        resp.raise_for_status()
        return resp.json()

    def list_user_repos(self, username: str, per_page: int = 30) -> list[dict[str, Any]]:
        """GET /users/{username}/repos"""
        resp = self._client.get(f"/users/{username}/repos", params={"per_page": per_page})
        resp.raise_for_status()
        return resp.json()

    def list_followers(self, username: str) -> list[dict[str, Any]]:
        """GET /users/{username}/followers"""
        resp = self._client.get(f"/users/{username}/followers")
        resp.raise_for_status()
        return resp.json()

    def list_following(self, username: str) -> list[dict[str, Any]]:
        """GET /users/{username}/following"""
        resp = self._client.get(f"/users/{username}/following")
        resp.raise_for_status()
        return resp.json()

    def list_user_gists(self, username: str) -> list[dict[str, Any]]:
        """GET /users/{username}/gists"""
        resp = self._client.get(f"/users/{username}/gists")
        resp.raise_for_status()
        return resp.json()

    def list_user_orgs(self, username: str) -> list[dict[str, Any]]:
        """GET /users/{username}/orgs"""
        resp = self._client.get(f"/users/{username}/orgs")
        resp.raise_for_status()
        return resp.json()


class OrgsAPI:
    """Organization-related endpoints."""

    def __init__(self, client: GitHubHTTPClient) -> None:
        self._client = client

    def get_org(self, org: str) -> dict[str, Any]:
        """GET /orgs/{org}"""
        resp = self._client.get(f"/orgs/{org}")
        resp.raise_for_status()
        return resp.json()

    def list_members(self, org: str) -> list[dict[str, Any]]:
        """GET /orgs/{org}/members"""
        resp = self._client.get(f"/orgs/{org}/members")
        resp.raise_for_status()
        return resp.json()

    def list_org_repos(self, org: str, per_page: int = 30) -> list[dict[str, Any]]:
        """GET /orgs/{org}/repos"""
        resp = self._client.get(f"/orgs/{org}/repos", params={"per_page": per_page})
        resp.raise_for_status()
        return resp.json()


class SearchAPI:
    """Search endpoints."""

    def __init__(self, client: GitHubHTTPClient) -> None:
        self._client = client

    def search_repos(self, query: str, per_page: int = 10) -> dict[str, Any]:
        """GET /search/repositories"""
        resp = self._client.get("/search/repositories", params={"q": query, "per_page": per_page})
        resp.raise_for_status()
        return resp.json()

    def search_users(self, query: str, per_page: int = 10) -> dict[str, Any]:
        """GET /search/users"""
        resp = self._client.get("/search/users", params={"q": query, "per_page": per_page})
        resp.raise_for_status()
        return resp.json()

    def search_code(self, query: str, per_page: int = 10) -> dict[str, Any]:
        """GET /search/code"""
        resp = self._client.get("/search/code", params={"q": query, "per_page": per_page})
        resp.raise_for_status()
        return resp.json()

    def search_issues(self, query: str, per_page: int = 10) -> dict[str, Any]:
        """GET /search/issues"""
        resp = self._client.get("/search/issues", params={"q": query, "per_page": per_page})
        resp.raise_for_status()
        return resp.json()


class IssuesAPI:
    """Issue-related endpoints."""

    def __init__(self, client: GitHubHTTPClient) -> None:
        self._client = client

    def list_repo_issues(
        self, owner: str, repo: str, state: str = "open", per_page: int = 10
    ) -> list[dict[str, Any]]:
        """GET /repos/{owner}/{repo}/issues"""
        resp = self._client.get(
            f"/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": per_page},
        )
        resp.raise_for_status()
        return resp.json()

    def get_issue(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        """GET /repos/{owner}/{repo}/issues/{issue_number}"""
        resp = self._client.get(f"/repos/{owner}/{repo}/issues/{issue_number}")
        resp.raise_for_status()
        return resp.json()

    def list_issue_comments(self, owner: str, repo: str, issue_number: int) -> list[dict[str, Any]]:
        """GET /repos/{owner}/{repo}/issues/{issue_number}/comments"""
        resp = self._client.get(f"/repos/{owner}/{repo}/issues/{issue_number}/comments")
        resp.raise_for_status()
        return resp.json()

    def list_labels(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """GET /repos/{owner}/{repo}/labels"""
        resp = self._client.get(f"/repos/{owner}/{repo}/labels")
        resp.raise_for_status()
        return resp.json()


class GistsAPI:
    """Gist-related endpoints."""

    def __init__(self, client: GitHubHTTPClient) -> None:
        self._client = client

    def list_public_gists(self, per_page: int = 10) -> list[dict[str, Any]]:
        """GET /gists/public"""
        resp = self._client.get("/gists/public", params={"per_page": per_page})
        resp.raise_for_status()
        return resp.json()

    def get_gist(self, gist_id: str) -> dict[str, Any]:
        """GET /gists/{gist_id}"""
        resp = self._client.get(f"/gists/{gist_id}")
        resp.raise_for_status()
        return resp.json()


class ActionsAPI:
    """GitHub Actions endpoints (public repos only)."""

    def __init__(self, client: GitHubHTTPClient) -> None:
        self._client = client

    def list_workflows(self, owner: str, repo: str) -> dict[str, Any]:
        """GET /repos/{owner}/{repo}/actions/workflows"""
        resp = self._client.get(f"/repos/{owner}/{repo}/actions/workflows")
        resp.raise_for_status()
        return resp.json()

    def list_workflow_runs(self, owner: str, repo: str, per_page: int = 5) -> dict[str, Any]:
        """GET /repos/{owner}/{repo}/actions/runs"""
        resp = self._client.get(f"/repos/{owner}/{repo}/actions/runs", params={"per_page": per_page})
        resp.raise_for_status()
        return resp.json()


class GitHubAPI:
    """Unified facade that exposes domain-specific sub-APIs.

    Usage in tests::

        def test_something(api: GitHubAPI):
            repo = api.repos.get_repo("octocat", "Hello-World")
            user = api.users.get_user("octocat")
    """

    def __init__(self, client: GitHubHTTPClient) -> None:
        self.client = client
        self.repos = ReposAPI(client)
        self.users = UsersAPI(client)
        self.orgs = OrgsAPI(client)
        self.search = SearchAPI(client)
        self.issues = IssuesAPI(client)
        self.gists = GistsAPI(client)
        self.actions = ActionsAPI(client)
