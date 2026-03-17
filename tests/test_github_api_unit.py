"""Unit tests for utils/api/github_api.py.

Tests all domain API facade classes (ReposAPI, UsersAPI, OrgsAPI, SearchAPI,
IssuesAPI, GistsAPI, ActionsAPI) and the unified GitHubAPI facade using a
fully mocked GitHubHTTPClient. No live network traffic is generated.

Also exercises all data constants and schema modules to ensure they load
correctly and export the expected symbols.
"""

import unittest.mock
from unittest.mock import MagicMock, patch

import pytest
import requests

from data.constants import (
    BASE_URL,
    GITHUB_API_VERSION,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE,
    HTTP_429_RATE_LIMITED,
    RATE_LIMIT_AUTHENTICATED,
    RATE_LIMIT_UNAUTHENTICATED,
    RATE_LIMIT_BUFFER,
    ENDPOINT_REPOS,
    ENDPOINT_USERS,
    ENDPOINT_ORGS,
    ENDPOINT_SEARCH_REPOS,
    ENDPOINT_GISTS_PUBLIC,
    ENDPOINT_ACTIONS_WORKFLOWS,
)
from data.repos_constants import (
    TEST_REPO_OWNER,
    TEST_REPO_NAME,
    TEST_REPO_FULL_NAME,
    POPULAR_REPOS,
    REPO_REQUIRED_FIELDS,
)
from data.users_constants import TEST_USERNAME, TEST_USER_ID, USER_REQUIRED_FIELDS
from data.orgs_constants import TEST_ORG, TEST_ORG_ID, ORG_REQUIRED_FIELDS
from data.issues_constants import TEST_ISSUES_OWNER, TEST_ISSUES_REPO, ISSUE_REQUIRED_FIELDS
from data.search_constants import SEARCH_QUERIES_REPOS, SEARCH_REQUIRED_FIELDS
from data.gists_constants import GIST_REQUIRED_FIELDS
from data.actions_constants import TEST_ACTIONS_OWNER, TEST_ACTIONS_REPO, WORKFLOW_REQUIRED_FIELDS
from utils.api.github_api import (
    ActionsAPI,
    GistsAPI,
    GitHubAPI,
    IssuesAPI,
    OrgsAPI,
    ReposAPI,
    SearchAPI,
    UsersAPI,
)
from utils.http.client import GitHubHTTPClient
from utils.testing.schemas import (
    REPO_SCHEMA,
    USER_SCHEMA,
    ORG_SCHEMA,
    SEARCH_RESULT_SCHEMA,
    ISSUE_SCHEMA,
    GIST_SCHEMA,
    WORKFLOW_SCHEMA,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _mock_client(json_return_value: dict | list | None = None) -> MagicMock:
    """Return a mocked GitHubHTTPClient.

    The mock's get/post/patch/put/delete all return a fake 200 response with
    the given JSON body.
    """
    client = MagicMock(spec=GitHubHTTPClient)
    mock_response = MagicMock()
    mock_response.status_code = HTTP_200_OK
    mock_response.headers = {}
    if json_return_value is None:
        json_return_value = {}
    mock_response.json.return_value = json_return_value
    mock_response.raise_for_status = MagicMock()  # no-op
    client.get.return_value = mock_response
    client.post.return_value = mock_response
    client.patch.return_value = mock_response
    client.put.return_value = mock_response
    client.delete.return_value = mock_response
    return client


# ---------------------------------------------------------------------------
# Data constants coverage
# ---------------------------------------------------------------------------


@pytest.mark.test_testing
class TestDataConstantsAreLoaded:
    """Verify all data constant modules export expected symbols.

    These tests ensure every constants module is imported and its key values
    are of the correct type, contributing to data/ coverage.
    """

    def test_http_status_constants_are_integers(self):
        """Verify all HTTP status code constants are integers.

        Setup: Import HTTP status constants.
        Action: Check their types.
        Assertions: All are ints with expected values.
        """
        # Assertions
        assert HTTP_200_OK == 200
        assert HTTP_201_CREATED == 201
        assert HTTP_204_NO_CONTENT == 204
        assert HTTP_400_BAD_REQUEST == 400
        assert HTTP_401_UNAUTHORIZED == 401
        assert HTTP_403_FORBIDDEN == 403
        assert HTTP_404_NOT_FOUND == 404
        assert HTTP_422_UNPROCESSABLE == 422
        assert HTTP_429_RATE_LIMITED == 429

    def test_rate_limit_constants(self):
        """Verify rate limit constants have expected values.

        Setup: Import rate limit constants.
        Action: Check values.
        Assertions: Authenticated limit > unauthenticated, buffer is positive.
        """
        # Assertions
        assert RATE_LIMIT_AUTHENTICATED == 5000
        assert RATE_LIMIT_UNAUTHENTICATED == 60
        assert RATE_LIMIT_BUFFER == 5

    def test_endpoint_constants_are_strings(self):
        """Verify endpoint path templates are non-empty strings.

        Setup: Import endpoint constants.
        Action: Check types.
        Assertions: All are strings containing '{'.
        """
        # Assertions
        for ep in [ENDPOINT_REPOS, ENDPOINT_USERS, ENDPOINT_ORGS, ENDPOINT_ACTIONS_WORKFLOWS]:
            assert isinstance(ep, str)
            assert "{" in ep

    def test_repos_constants_types(self):
        """Verify repos_constants exports expected types.

        Setup: Import repos constants.
        Action: Check types.
        Assertions: Strings and lists of the correct shape.
        """
        # Assertions
        assert isinstance(TEST_REPO_OWNER, str)
        assert isinstance(TEST_REPO_NAME, str)
        assert isinstance(TEST_REPO_FULL_NAME, str)
        assert isinstance(POPULAR_REPOS, list)
        assert len(POPULAR_REPOS) > 0
        assert isinstance(REPO_REQUIRED_FIELDS, list)

    def test_users_constants_types(self):
        """Verify users_constants exports expected types.

        Setup: Import users constants.
        Action: Check types.
        Assertions: Username is a string, ID is an int.
        """
        # Assertions
        assert isinstance(TEST_USERNAME, str)
        assert isinstance(TEST_USER_ID, int)
        assert isinstance(USER_REQUIRED_FIELDS, list)

    def test_orgs_constants_types(self):
        """Verify orgs_constants exports expected types.

        Setup: Import orgs constants.
        Action: Check types.
        Assertions: Org name is a string, ID is an int.
        """
        # Assertions
        assert isinstance(TEST_ORG, str)
        assert isinstance(TEST_ORG_ID, int)
        assert isinstance(ORG_REQUIRED_FIELDS, list)

    def test_issues_constants_types(self):
        """Verify issues_constants exports expected types.

        Setup: Import issues constants.
        Action: Check types.
        Assertions: Strings and lists of the correct types.
        """
        # Assertions
        assert isinstance(TEST_ISSUES_OWNER, str)
        assert isinstance(TEST_ISSUES_REPO, str)
        assert isinstance(ISSUE_REQUIRED_FIELDS, list)

    def test_search_constants_types(self):
        """Verify search_constants exports expected types.

        Setup: Import search constants.
        Action: Check types.
        Assertions: Query lists are non-empty lists of strings.
        """
        # Assertions
        assert isinstance(SEARCH_QUERIES_REPOS, list)
        assert len(SEARCH_QUERIES_REPOS) > 0
        assert all(isinstance(q, str) for q in SEARCH_QUERIES_REPOS)
        assert isinstance(SEARCH_REQUIRED_FIELDS, list)

    def test_gists_constants_types(self):
        """Verify gists_constants exports expected types.

        Setup: Import gists constants.
        Action: Check types.
        Assertions: Required fields list is non-empty.
        """
        # Assertions
        assert isinstance(GIST_REQUIRED_FIELDS, list)
        assert len(GIST_REQUIRED_FIELDS) > 0

    def test_actions_constants_types(self):
        """Verify actions_constants exports expected types.

        Setup: Import actions constants.
        Action: Check types.
        Assertions: Owner and repo are strings, field list is non-empty.
        """
        # Assertions
        assert isinstance(TEST_ACTIONS_OWNER, str)
        assert isinstance(TEST_ACTIONS_REPO, str)
        assert isinstance(WORKFLOW_REQUIRED_FIELDS, list)

    def test_schemas_are_dicts(self):
        """Verify all JSON schema objects are dictionaries.

        Setup: Import schema constants.
        Action: Check types.
        Assertions: All schemas are dicts with 'type' key.
        """
        # Assertions
        for schema in [REPO_SCHEMA, USER_SCHEMA, ORG_SCHEMA, SEARCH_RESULT_SCHEMA, ISSUE_SCHEMA, GIST_SCHEMA, WORKFLOW_SCHEMA]:
            assert isinstance(schema, dict)
            assert "type" in schema


# ---------------------------------------------------------------------------
# ReposAPI
# ---------------------------------------------------------------------------


@pytest.mark.test_testing
class TestReposAPIUnit:
    """Unit tests for ReposAPI using a mocked HTTP client."""

    def test_get_repo_calls_correct_endpoint(self):
        """Verify get_repo calls GET /repos/{owner}/{repo}.

        Setup: Mocked client returning a repo dict.
        Action: Call api.get_repo('octocat', 'Hello-World').
        Assertions: client.get called with correct path; return value matches mock.
        """
        # Setup
        body = {"id": 1, "name": "Hello-World", "full_name": "octocat/Hello-World"}
        client = _mock_client(body)
        api = ReposAPI(client)

        # Action
        result = api.get_repo("octocat", "Hello-World")

        # Assertions
        client.get.assert_called_once_with("/repos/octocat/Hello-World")
        assert result == body

    def test_list_repos_calls_org_endpoint(self):
        """Verify list_repos calls GET /orgs/{org}/repos with pagination params.

        Setup: Mocked client returning a list.
        Action: Call api.list_repos('github').
        Assertions: client.get called with correct path and params.
        """
        # Setup
        client = _mock_client([{"id": 1}])
        api = ReposAPI(client)

        # Action
        result = api.list_repos("github")

        # Assertions
        client.get.assert_called_once_with(
            "/orgs/github/repos", params={"per_page": 30, "page": 1}
        )

    def test_list_branches_calls_endpoint(self):
        """Verify list_branches calls GET /repos/{owner}/{repo}/branches.

        Setup: Mocked client.
        Action: Call api.list_branches.
        Assertions: client.get called with branches path.
        """
        # Setup
        client = _mock_client([{"name": "main"}])
        api = ReposAPI(client)

        # Action
        result = api.list_branches("octocat", "Hello-World")

        # Assertions
        client.get.assert_called_once_with("/repos/octocat/Hello-World/branches")

    def test_list_tags_calls_endpoint(self):
        """Verify list_tags calls GET /repos/{owner}/{repo}/tags.

        Setup: Mocked client.
        Action: Call api.list_tags.
        Assertions: client.get called with tags path.
        """
        # Setup
        client = _mock_client([])
        api = ReposAPI(client)

        # Action
        api.list_tags("octocat", "Hello-World")

        # Assertions
        client.get.assert_called_once_with("/repos/octocat/Hello-World/tags")

    def test_list_contributors_calls_endpoint(self):
        """Verify list_contributors calls GET /repos/{owner}/{repo}/contributors.

        Setup: Mocked client.
        Action: Call api.list_contributors.
        Assertions: client.get called with contributors path.
        """
        # Setup
        client = _mock_client([])
        api = ReposAPI(client)

        # Action
        api.list_contributors("octocat", "Hello-World")

        # Assertions
        client.get.assert_called_once_with("/repos/octocat/Hello-World/contributors")

    def test_list_languages_calls_endpoint(self):
        """Verify list_languages calls GET /repos/{owner}/{repo}/languages.

        Setup: Mocked client.
        Action: Call api.list_languages.
        Assertions: client.get called with languages path.
        """
        # Setup
        client = _mock_client({"Python": 10000})
        api = ReposAPI(client)

        # Action
        result = api.list_languages("microsoft", "vscode")

        # Assertions
        client.get.assert_called_once_with("/repos/microsoft/vscode/languages")
        assert result == {"Python": 10000}

    def test_get_readme_calls_endpoint(self):
        """Verify get_readme calls GET /repos/{owner}/{repo}/readme.

        Setup: Mocked client.
        Action: Call api.get_readme.
        Assertions: client.get called with readme path.
        """
        # Setup
        client = _mock_client({"name": "README.md"})
        api = ReposAPI(client)

        # Action
        api.get_readme("octocat", "Hello-World")

        # Assertions
        client.get.assert_called_once_with("/repos/octocat/Hello-World/readme")

    def test_list_commits_calls_endpoint_with_per_page(self):
        """Verify list_commits calls with per_page parameter.

        Setup: Mocked client.
        Action: Call api.list_commits with per_page=5.
        Assertions: client.get called with correct params.
        """
        # Setup
        client = _mock_client([])
        api = ReposAPI(client)

        # Action
        api.list_commits("octocat", "Hello-World", per_page=5)

        # Assertions
        client.get.assert_called_once_with(
            "/repos/octocat/Hello-World/commits", params={"per_page": 5}
        )


# ---------------------------------------------------------------------------
# UsersAPI
# ---------------------------------------------------------------------------


@pytest.mark.test_testing
class TestUsersAPIUnit:
    """Unit tests for UsersAPI using a mocked HTTP client."""

    def test_get_user_calls_endpoint(self):
        """Verify get_user calls GET /users/{username}.

        Setup: Mocked client returning user body.
        Action: Call api.get_user('octocat').
        Assertions: client.get called with correct path.
        """
        # Setup
        body = {"login": "octocat", "id": 583231}
        client = _mock_client(body)
        api = UsersAPI(client)

        # Action
        result = api.get_user("octocat")

        # Assertions
        client.get.assert_called_once_with("/users/octocat")
        assert result == body

    def test_list_user_repos_calls_endpoint(self):
        """Verify list_user_repos calls GET /users/{username}/repos.

        Setup: Mocked client.
        Action: Call api.list_user_repos.
        Assertions: client.get called with repos path.
        """
        # Setup
        client = _mock_client([])
        api = UsersAPI(client)

        # Action
        api.list_user_repos("octocat")

        # Assertions
        client.get.assert_called_once_with("/users/octocat/repos", params={"per_page": 30})

    def test_list_followers_calls_endpoint(self):
        """Verify list_followers calls GET /users/{username}/followers.

        Setup: Mocked client.
        Action: Call api.list_followers.
        Assertions: client.get called with followers path.
        """
        # Setup
        client = _mock_client([])
        api = UsersAPI(client)
        api.list_followers("octocat")
        client.get.assert_called_once_with("/users/octocat/followers")

    def test_list_following_calls_endpoint(self):
        """Verify list_following calls GET /users/{username}/following.

        Setup: Mocked client.
        Action: Call api.list_following.
        Assertions: client.get called with following path.
        """
        # Setup
        client = _mock_client([])
        api = UsersAPI(client)
        api.list_following("octocat")
        client.get.assert_called_once_with("/users/octocat/following")

    def test_list_user_gists_calls_endpoint(self):
        """Verify list_user_gists calls GET /users/{username}/gists.

        Setup: Mocked client.
        Action: Call api.list_user_gists.
        Assertions: client.get called with gists path.
        """
        # Setup
        client = _mock_client([])
        api = UsersAPI(client)
        api.list_user_gists("octocat")
        client.get.assert_called_once_with("/users/octocat/gists")

    def test_list_user_orgs_calls_endpoint(self):
        """Verify list_user_orgs calls GET /users/{username}/orgs.

        Setup: Mocked client.
        Action: Call api.list_user_orgs.
        Assertions: client.get called with orgs path.
        """
        # Setup
        client = _mock_client([])
        api = UsersAPI(client)
        api.list_user_orgs("octocat")
        client.get.assert_called_once_with("/users/octocat/orgs")


# ---------------------------------------------------------------------------
# OrgsAPI
# ---------------------------------------------------------------------------


@pytest.mark.test_testing
class TestOrgsAPIUnit:
    """Unit tests for OrgsAPI using a mocked HTTP client."""

    def test_get_org_calls_endpoint(self):
        """Verify get_org calls GET /orgs/{org}.

        Setup: Mocked client.
        Action: Call api.get_org.
        Assertions: client.get called with correct path.
        """
        # Setup
        body = {"login": "github", "id": 9919}
        client = _mock_client(body)
        api = OrgsAPI(client)

        # Action
        result = api.get_org("github")

        # Assertions
        client.get.assert_called_once_with("/orgs/github")
        assert result == body

    def test_list_members_calls_endpoint(self):
        """Verify list_members calls GET /orgs/{org}/members.

        Setup: Mocked client.
        Action: Call api.list_members.
        Assertions: client.get called with members path.
        """
        # Setup
        client = _mock_client([])
        api = OrgsAPI(client)
        api.list_members("github")
        client.get.assert_called_once_with("/orgs/github/members")

    def test_list_org_repos_calls_endpoint(self):
        """Verify list_org_repos calls GET /orgs/{org}/repos.

        Setup: Mocked client.
        Action: Call api.list_org_repos.
        Assertions: client.get called with repos path and per_page param.
        """
        # Setup
        client = _mock_client([])
        api = OrgsAPI(client)
        api.list_org_repos("github", per_page=10)
        client.get.assert_called_once_with("/orgs/github/repos", params={"per_page": 10})


# ---------------------------------------------------------------------------
# SearchAPI
# ---------------------------------------------------------------------------


@pytest.mark.test_testing
class TestSearchAPIUnit:
    """Unit tests for SearchAPI using a mocked HTTP client."""

    def test_search_repos_calls_endpoint(self):
        """Verify search_repos calls GET /search/repositories with q param.

        Setup: Mocked client.
        Action: Call api.search_repos.
        Assertions: client.get called with query params.
        """
        # Setup
        body = {"total_count": 1, "incomplete_results": False, "items": []}
        client = _mock_client(body)
        api = SearchAPI(client)

        # Action
        result = api.search_repos("language:python", per_page=5)

        # Assertions
        client.get.assert_called_once_with(
            "/search/repositories", params={"q": "language:python", "per_page": 5}
        )
        assert result == body

    def test_search_users_calls_endpoint(self):
        """Verify search_users calls GET /search/users.

        Setup: Mocked client.
        Action: Call api.search_users.
        Assertions: client.get called with correct params.
        """
        # Setup
        client = _mock_client({"total_count": 0, "items": []})
        api = SearchAPI(client)
        api.search_users("torvalds", per_page=5)
        client.get.assert_called_once_with(
            "/search/users", params={"q": "torvalds", "per_page": 5}
        )

    def test_search_code_calls_endpoint(self):
        """Verify search_code calls GET /search/code.

        Setup: Mocked client.
        Action: Call api.search_code.
        Assertions: client.get called with code search path.
        """
        # Setup
        client = _mock_client({"total_count": 0, "items": []})
        api = SearchAPI(client)
        api.search_code("filename:pytest.ini", per_page=5)
        client.get.assert_called_once_with(
            "/search/code", params={"q": "filename:pytest.ini", "per_page": 5}
        )

    def test_search_issues_calls_endpoint(self):
        """Verify search_issues calls GET /search/issues.

        Setup: Mocked client.
        Action: Call api.search_issues.
        Assertions: client.get called with issues search path.
        """
        # Setup
        client = _mock_client({"total_count": 0, "items": []})
        api = SearchAPI(client)
        api.search_issues("repo:octocat/Hello-World is:open", per_page=5)
        client.get.assert_called_once_with(
            "/search/issues",
            params={"q": "repo:octocat/Hello-World is:open", "per_page": 5},
        )


# ---------------------------------------------------------------------------
# IssuesAPI
# ---------------------------------------------------------------------------


@pytest.mark.test_testing
class TestIssuesAPIUnit:
    """Unit tests for IssuesAPI using a mocked HTTP client."""

    def test_list_repo_issues_calls_endpoint(self):
        """Verify list_repo_issues calls correct endpoint with state param.

        Setup: Mocked client.
        Action: Call api.list_repo_issues.
        Assertions: client.get called with state and per_page.
        """
        # Setup
        client = _mock_client([])
        api = IssuesAPI(client)

        # Action
        api.list_repo_issues("octocat", "Hello-World", state="open", per_page=5)

        # Assertions
        client.get.assert_called_once_with(
            "/repos/octocat/Hello-World/issues",
            params={"state": "open", "per_page": 5},
        )

    def test_get_issue_calls_endpoint(self):
        """Verify get_issue calls GET /repos/{owner}/{repo}/issues/{number}.

        Setup: Mocked client.
        Action: Call api.get_issue.
        Assertions: client.get called with issue number in path.
        """
        # Setup
        body = {"id": 1, "number": 1, "title": "Found a bug"}
        client = _mock_client(body)
        api = IssuesAPI(client)

        # Action
        result = api.get_issue("octocat", "Hello-World", 1)

        # Assertions
        client.get.assert_called_once_with("/repos/octocat/Hello-World/issues/1")
        assert result == body

    def test_list_issue_comments_calls_endpoint(self):
        """Verify list_issue_comments calls the comments sub-path.

        Setup: Mocked client.
        Action: Call api.list_issue_comments.
        Assertions: client.get called with comments path.
        """
        # Setup
        client = _mock_client([])
        api = IssuesAPI(client)
        api.list_issue_comments("octocat", "Hello-World", 1)
        client.get.assert_called_once_with("/repos/octocat/Hello-World/issues/1/comments")

    def test_list_labels_calls_endpoint(self):
        """Verify list_labels calls GET /repos/{owner}/{repo}/labels.

        Setup: Mocked client.
        Action: Call api.list_labels.
        Assertions: client.get called with labels path.
        """
        # Setup
        client = _mock_client([])
        api = IssuesAPI(client)
        api.list_labels("octocat", "Hello-World")
        client.get.assert_called_once_with("/repos/octocat/Hello-World/labels")


# ---------------------------------------------------------------------------
# GistsAPI
# ---------------------------------------------------------------------------


@pytest.mark.test_testing
class TestGistsAPIUnit:
    """Unit tests for GistsAPI using a mocked HTTP client."""

    def test_list_public_gists_calls_endpoint(self):
        """Verify list_public_gists calls GET /gists/public.

        Setup: Mocked client.
        Action: Call api.list_public_gists.
        Assertions: client.get called with per_page param.
        """
        # Setup
        client = _mock_client([])
        api = GistsAPI(client)
        api.list_public_gists(per_page=5)
        client.get.assert_called_once_with("/gists/public", params={"per_page": 5})

    def test_get_gist_calls_endpoint(self):
        """Verify get_gist calls GET /gists/{gist_id}.

        Setup: Mocked client.
        Action: Call api.get_gist.
        Assertions: client.get called with gist_id in path.
        """
        # Setup
        body = {"id": "abc123", "public": True}
        client = _mock_client(body)
        api = GistsAPI(client)

        # Action
        result = api.get_gist("abc123")

        # Assertions
        client.get.assert_called_once_with("/gists/abc123")
        assert result == body


# ---------------------------------------------------------------------------
# ActionsAPI
# ---------------------------------------------------------------------------


@pytest.mark.test_testing
class TestActionsAPIUnit:
    """Unit tests for ActionsAPI using a mocked HTTP client."""

    def test_list_workflows_calls_endpoint(self):
        """Verify list_workflows calls GET /repos/{owner}/{repo}/actions/workflows.

        Setup: Mocked client.
        Action: Call api.list_workflows.
        Assertions: client.get called with workflows path.
        """
        # Setup
        body = {"total_count": 1, "workflows": []}
        client = _mock_client(body)
        api = ActionsAPI(client)

        # Action
        result = api.list_workflows("actions", "checkout")

        # Assertions
        client.get.assert_called_once_with("/repos/actions/checkout/actions/workflows")
        assert result == body

    def test_list_workflow_runs_calls_endpoint(self):
        """Verify list_workflow_runs calls GET /repos/{owner}/{repo}/actions/runs.

        Setup: Mocked client.
        Action: Call api.list_workflow_runs.
        Assertions: client.get called with per_page param.
        """
        # Setup
        client = _mock_client({"total_count": 0, "workflow_runs": []})
        api = ActionsAPI(client)
        api.list_workflow_runs("actions", "checkout", per_page=3)
        client.get.assert_called_once_with(
            "/repos/actions/checkout/actions/runs", params={"per_page": 3}
        )


# ---------------------------------------------------------------------------
# GitHubAPI (unified facade)
# ---------------------------------------------------------------------------


@pytest.mark.test_testing
class TestGitHubAPIFacadeUnit:
    """Unit tests for the unified GitHubAPI facade."""

    def test_facade_exposes_all_sub_apis(self):
        """Verify GitHubAPI wires up all seven domain sub-APIs.

        Setup: Instantiate GitHubAPI with a mocked HTTP client.
        Action: Read each sub-API attribute.
        Assertions: All seven sub-APIs are correctly typed.
        """
        # Setup
        client = _mock_client()
        api = GitHubAPI(client=client)

        # Assertions
        assert isinstance(api.repos, ReposAPI)
        assert isinstance(api.users, UsersAPI)
        assert isinstance(api.orgs, OrgsAPI)
        assert isinstance(api.search, SearchAPI)
        assert isinstance(api.issues, IssuesAPI)
        assert isinstance(api.gists, GistsAPI)
        assert isinstance(api.actions, ActionsAPI)

    def test_facade_delegates_repos(self):
        """Verify api.repos.get_repo delegates to the HTTP client.

        Setup: Mocked client returning a repo body.
        Action: Call api.repos.get_repo through the facade.
        Assertions: Response equals the mocked body.
        """
        # Setup
        body = {"id": 1, "name": "Hello-World", "full_name": "octocat/Hello-World"}
        client = _mock_client(body)
        api = GitHubAPI(client=client)

        # Action
        result = api.repos.get_repo("octocat", "Hello-World")

        # Assertions
        assert result == body

    def test_facade_delegates_users(self):
        """Verify api.users.get_user delegates to the HTTP client.

        Setup: Mocked client returning a user body.
        Action: Call api.users.get_user through the facade.
        Assertions: Response equals the mocked body.
        """
        # Setup
        body = {"login": "octocat", "id": 583231}
        client = _mock_client(body)
        api = GitHubAPI(client=client)

        # Action
        result = api.users.get_user("octocat")

        # Assertions
        assert result == body

    def test_facade_delegates_search(self):
        """Verify api.search.search_repos delegates to the HTTP client.

        Setup: Mocked client returning a search result.
        Action: Call api.search.search_repos through the facade.
        Assertions: Response matches mocked result.
        """
        # Setup
        body = {"total_count": 1, "incomplete_results": False, "items": []}
        client = _mock_client(body)
        api = GitHubAPI(client=client)

        # Action
        result = api.search.search_repos("language:python")

        # Assertions
        assert result["total_count"] == 1
