"""Tests for issue-related endpoints.

Validates issue listing, retrieval, comments, and labels.
"""

import pytest

from data.constants import HTTP_200_OK, HTTP_404_NOT_FOUND
from data.issues_constants import (
    ISSUE_REQUIRED_FIELDS,
    ISSUE_STATES,
    TEST_ISSUE_NUMBER,
    TEST_ISSUES_OWNER,
    TEST_ISSUES_REPO,
)
from utils.api.github_api import GitHubAPI
from utils.testing.helpers import assert_json_keys, assert_status_code


@pytest.mark.test_issues
class TestListIssues:
    """GET /repos/{owner}/{repo}/issues — list repository issues."""

    def test_list_issues_returns_list(self, api: GitHubAPI):
        """Verify issue listing returns a list."""
        issues = api.issues.list_repo_issues(TEST_ISSUES_OWNER, TEST_ISSUES_REPO)
        assert isinstance(issues, list)

    def test_list_issues_default_state_is_open(self, api: GitHubAPI):
        """Verify default state filter returns open issues."""
        issues = api.issues.list_repo_issues(TEST_ISSUES_OWNER, TEST_ISSUES_REPO, state="open")
        for issue in issues[:5]:
            assert issue["state"] == "open"

    def test_list_closed_issues(self, api: GitHubAPI):
        """Verify closed state filter works."""
        issues = api.issues.list_repo_issues(TEST_ISSUES_OWNER, TEST_ISSUES_REPO, state="closed")
        for issue in issues[:5]:
            assert issue["state"] == "closed"

    def test_issue_has_required_fields(self, api: GitHubAPI):
        """Verify each issue has all required fields."""
        issues = api.issues.list_repo_issues(TEST_ISSUES_OWNER, TEST_ISSUES_REPO, per_page=5)
        for issue in issues:
            assert_json_keys(issue, ISSUE_REQUIRED_FIELDS)


@pytest.mark.test_issues
class TestGetIssue:
    """GET /repos/{owner}/{repo}/issues/{issue_number} — get a single issue."""

    def test_get_issue_by_number(self, api: GitHubAPI):
        """Verify fetching a specific issue by number."""
        issue = api.issues.get_issue(TEST_ISSUES_OWNER, TEST_ISSUES_REPO, TEST_ISSUE_NUMBER)
        assert issue["number"] == TEST_ISSUE_NUMBER

    def test_get_issue_has_required_fields(self, api: GitHubAPI):
        """Verify the issue response has all required fields."""
        issue = api.issues.get_issue(TEST_ISSUES_OWNER, TEST_ISSUES_REPO, TEST_ISSUE_NUMBER)
        assert_json_keys(issue, ISSUE_REQUIRED_FIELDS)

    def test_get_nonexistent_issue(self, api: GitHubAPI):
        """Verify HTTP 404 for a nonexistent issue number."""
        resp = api.client.get(f"/repos/{TEST_ISSUES_OWNER}/{TEST_ISSUES_REPO}/issues/999999999")
        assert_status_code(resp, HTTP_404_NOT_FOUND)


@pytest.mark.test_issues
class TestIssueComments:
    """GET /repos/{owner}/{repo}/issues/{number}/comments — list comments."""

    def test_list_comments_returns_list(self, api: GitHubAPI):
        """Verify comment listing returns a list."""
        comments = api.issues.list_issue_comments(
            TEST_ISSUES_OWNER, TEST_ISSUES_REPO, TEST_ISSUE_NUMBER
        )
        assert isinstance(comments, list)


@pytest.mark.test_issues
class TestLabels:
    """GET /repos/{owner}/{repo}/labels — list labels."""

    def test_list_labels_returns_list(self, api: GitHubAPI):
        """Verify label listing returns a list."""
        labels = api.issues.list_labels(TEST_ISSUES_OWNER, TEST_ISSUES_REPO)
        assert isinstance(labels, list)

    def test_label_has_name_and_color(self, api: GitHubAPI):
        """Verify each label has name and color fields."""
        labels = api.issues.list_labels(TEST_ISSUES_OWNER, TEST_ISSUES_REPO)
        for label in labels[:5]:
            assert "name" in label
            assert "color" in label
