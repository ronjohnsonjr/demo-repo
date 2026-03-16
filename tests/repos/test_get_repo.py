"""Tests for GET /repos/{owner}/{repo} endpoint.

Validates repository retrieval, response schema, known-value assertions,
and error handling for the core repository endpoint.
"""

import pytest
from jsonschema import validate

from data.constants import HTTP_200_OK, HTTP_404_NOT_FOUND
from data.repos_constants import (
    HELLO_WORLD_EXPECTED,
    POPULAR_REPOS,
    REPO_OWNER_REQUIRED_FIELDS,
    REPO_REQUIRED_FIELDS,
    TEST_REPO_NAME,
    TEST_REPO_OWNER,
)
from utils.api.github_api import GitHubAPI
from utils.testing.helpers import assert_json_keys, assert_status_code
from utils.testing.schemas import REPO_SCHEMA


@pytest.mark.test_repos
class TestGetRepo:
    """GET /repos/{owner}/{repo} — retrieve a single repository."""

    def test_get_repo_returns_200(self, api: GitHubAPI):
        """Verify that fetching a known public repo returns HTTP 200."""
        # Setup
        owner, repo = TEST_REPO_OWNER, TEST_REPO_NAME

        # Action
        result = api.repos.get_repo(owner, repo)

        # Assertions
        assert result["full_name"] == f"{owner}/{repo}"

    def test_get_repo_response_schema(self, api: GitHubAPI):
        """Verify response matches the expected JSON schema."""
        result = api.repos.get_repo(TEST_REPO_OWNER, TEST_REPO_NAME)
        validate(instance=result, schema=REPO_SCHEMA)

    def test_get_repo_required_fields(self, api: GitHubAPI):
        """Verify all required fields are present in the response."""
        result = api.repos.get_repo(TEST_REPO_OWNER, TEST_REPO_NAME)
        assert_json_keys(result, REPO_REQUIRED_FIELDS)

    def test_get_repo_owner_fields(self, api: GitHubAPI):
        """Verify the nested owner object has required fields."""
        result = api.repos.get_repo(TEST_REPO_OWNER, TEST_REPO_NAME)
        assert_json_keys(result["owner"], REPO_OWNER_REQUIRED_FIELDS)

    def test_get_repo_known_values(self, api: GitHubAPI):
        """Verify known stable values for octocat/Hello-World."""
        result = api.repos.get_repo(TEST_REPO_OWNER, TEST_REPO_NAME)

        assert result["name"] == HELLO_WORLD_EXPECTED["name"]
        assert result["full_name"] == HELLO_WORLD_EXPECTED["full_name"]
        assert result["fork"] == HELLO_WORLD_EXPECTED["fork"]
        assert result["owner"]["login"] == HELLO_WORLD_EXPECTED["owner_login"]

    def test_get_repo_not_found(self, api: GitHubAPI):
        """Verify HTTP 404 for a nonexistent repository."""
        resp = api.client.get("/repos/nonexistent-user-abc123/nonexistent-repo-xyz789")
        assert_status_code(resp, HTTP_404_NOT_FOUND)

    @pytest.mark.parametrize("owner,repo", POPULAR_REPOS)
    def test_get_popular_repos(self, api: GitHubAPI, owner: str, repo: str):
        """Verify multiple well-known public repos are accessible."""
        result = api.repos.get_repo(owner, repo)
        assert result["full_name"] == f"{owner}/{repo}"
        assert result["id"] > 0


@pytest.mark.test_repos
class TestRepoBranches:
    """GET /repos/{owner}/{repo}/branches — list branches."""

    def test_list_branches_returns_list(self, api: GitHubAPI):
        """Verify branch listing returns a non-empty list."""
        branches = api.repos.list_branches(TEST_REPO_OWNER, TEST_REPO_NAME)
        assert isinstance(branches, list)
        assert len(branches) > 0

    def test_branch_has_name_and_commit(self, api: GitHubAPI):
        """Verify each branch has a name and commit SHA."""
        branches = api.repos.list_branches(TEST_REPO_OWNER, TEST_REPO_NAME)
        for branch in branches:
            assert "name" in branch
            assert "commit" in branch
            assert "sha" in branch["commit"]

    def test_default_branch_exists(self, api: GitHubAPI):
        """Verify the default branch (master) is in the branch list."""
        branches = api.repos.list_branches(TEST_REPO_OWNER, TEST_REPO_NAME)
        branch_names = [b["name"] for b in branches]
        assert "master" in branch_names


@pytest.mark.test_repos
class TestRepoContributors:
    """GET /repos/{owner}/{repo}/contributors — list contributors."""

    def test_list_contributors_returns_list(self, api: GitHubAPI):
        """Verify contributor listing returns a non-empty list."""
        contributors = api.repos.list_contributors(TEST_REPO_OWNER, TEST_REPO_NAME)
        assert isinstance(contributors, list)
        assert len(contributors) > 0

    def test_contributor_has_required_fields(self, api: GitHubAPI):
        """Verify each contributor has login, id, and contributions."""
        contributors = api.repos.list_contributors(TEST_REPO_OWNER, TEST_REPO_NAME)
        for contrib in contributors:
            assert "login" in contrib
            assert "id" in contrib
            assert "contributions" in contrib
            assert contrib["contributions"] > 0


@pytest.mark.test_repos
class TestRepoLanguages:
    """GET /repos/{owner}/{repo}/languages — list languages."""

    def test_list_languages_returns_dict(self, api: GitHubAPI):
        """Verify languages endpoint returns a dict of language:bytes."""
        languages = api.repos.list_languages("microsoft", "vscode")
        assert isinstance(languages, dict)
        assert len(languages) > 0

    def test_language_values_are_positive_ints(self, api: GitHubAPI):
        """Verify each language has a positive byte count."""
        languages = api.repos.list_languages("microsoft", "vscode")
        for lang, byte_count in languages.items():
            assert isinstance(lang, str)
            assert isinstance(byte_count, int)
            assert byte_count > 0


@pytest.mark.test_repos
class TestRepoCommits:
    """GET /repos/{owner}/{repo}/commits — list commits."""

    def test_list_commits_returns_list(self, api: GitHubAPI):
        """Verify commit listing returns a non-empty list."""
        commits = api.repos.list_commits(TEST_REPO_OWNER, TEST_REPO_NAME)
        assert isinstance(commits, list)
        assert len(commits) > 0

    def test_commit_has_sha_and_message(self, api: GitHubAPI):
        """Verify each commit has a SHA and commit message."""
        commits = api.repos.list_commits(TEST_REPO_OWNER, TEST_REPO_NAME)
        for commit in commits:
            assert "sha" in commit
            assert len(commit["sha"]) == 40
            assert "commit" in commit
            assert "message" in commit["commit"]
