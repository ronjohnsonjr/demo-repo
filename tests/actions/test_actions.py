"""Tests for GitHub Actions endpoints.

Validates workflow and workflow run listing for public repos.
"""

import pytest

from data.actions_constants import (
    TEST_ACTIONS_OWNER,
    TEST_ACTIONS_REPO,
    WORKFLOW_REQUIRED_FIELDS,
    WORKFLOW_RUN_REQUIRED_FIELDS,
)
from utils.api.github_api import GitHubAPI
from utils.testing.helpers import assert_json_keys


@pytest.mark.test_actions
class TestListWorkflows:
    """GET /repos/{owner}/{repo}/actions/workflows — list workflows."""

    def test_list_workflows_returns_count(self, api: GitHubAPI):
        """Verify workflow listing includes total_count."""
        result = api.actions.list_workflows(TEST_ACTIONS_OWNER, TEST_ACTIONS_REPO)
        assert "total_count" in result
        assert result["total_count"] > 0

    def test_list_workflows_returns_workflows(self, api: GitHubAPI):
        """Verify workflow listing includes workflow objects."""
        result = api.actions.list_workflows(TEST_ACTIONS_OWNER, TEST_ACTIONS_REPO)
        assert "workflows" in result
        assert isinstance(result["workflows"], list)
        assert len(result["workflows"]) > 0

    def test_workflow_has_required_fields(self, api: GitHubAPI):
        """Verify each workflow has required fields."""
        result = api.actions.list_workflows(TEST_ACTIONS_OWNER, TEST_ACTIONS_REPO)
        for workflow in result["workflows"][:3]:
            assert "id" in workflow
            assert "name" in workflow
            assert "path" in workflow
            assert "state" in workflow


@pytest.mark.test_actions
class TestListWorkflowRuns:
    """GET /repos/{owner}/{repo}/actions/runs — list workflow runs."""

    def test_list_runs_returns_count(self, api: GitHubAPI):
        """Verify run listing includes total_count."""
        result = api.actions.list_workflow_runs(TEST_ACTIONS_OWNER, TEST_ACTIONS_REPO)
        assert "total_count" in result

    def test_list_runs_returns_runs(self, api: GitHubAPI):
        """Verify run listing includes run objects."""
        result = api.actions.list_workflow_runs(TEST_ACTIONS_OWNER, TEST_ACTIONS_REPO, per_page=3)
        assert "workflow_runs" in result
        assert isinstance(result["workflow_runs"], list)

    def test_run_has_required_fields(self, api: GitHubAPI):
        """Verify each run has required fields."""
        result = api.actions.list_workflow_runs(TEST_ACTIONS_OWNER, TEST_ACTIONS_REPO, per_page=3)
        for run in result["workflow_runs"][:3]:
            assert "id" in run
            assert "name" in run
            assert "status" in run
            assert "workflow_id" in run
