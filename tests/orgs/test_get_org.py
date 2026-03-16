"""Tests for organization endpoints.

Validates org profile retrieval, member listing, and repo listing.
"""

import pytest
from jsonschema import validate

from data.constants import HTTP_200_OK, HTTP_404_NOT_FOUND
from data.orgs_constants import (
    GITHUB_ORG_EXPECTED,
    ORG_REQUIRED_FIELDS,
    TEST_ORG,
    TEST_ORGS,
)
from utils.api.github_api import GitHubAPI
from utils.testing.helpers import assert_json_keys, assert_status_code
from utils.testing.schemas import ORG_SCHEMA


@pytest.mark.test_orgs
class TestGetOrg:
    """GET /orgs/{org} — retrieve organization profile."""

    def test_get_org_returns_profile(self, api: GitHubAPI):
        """Verify fetching a known org returns its profile."""
        result = api.orgs.get_org(TEST_ORG)
        assert result["login"] == TEST_ORG

    def test_get_org_response_schema(self, api: GitHubAPI):
        """Verify response matches the expected JSON schema."""
        result = api.orgs.get_org(TEST_ORG)
        validate(instance=result, schema=ORG_SCHEMA)

    def test_get_org_required_fields(self, api: GitHubAPI):
        """Verify all required fields are present."""
        result = api.orgs.get_org(TEST_ORG)
        assert_json_keys(result, ORG_REQUIRED_FIELDS)

    def test_get_org_known_values(self, api: GitHubAPI):
        """Verify known stable values for 'github' org."""
        result = api.orgs.get_org(TEST_ORG)
        assert result["login"] == GITHUB_ORG_EXPECTED["login"]
        assert result["type"] == GITHUB_ORG_EXPECTED["type"]

    def test_get_org_not_found(self, api: GitHubAPI):
        """Verify HTTP 404 for a nonexistent organization."""
        resp = api.client.get("/orgs/nonexistent-org-abc123xyz789")
        assert_status_code(resp, HTTP_404_NOT_FOUND)

    @pytest.mark.parametrize("org", TEST_ORGS)
    def test_get_multiple_orgs(self, api: GitHubAPI, org: str):
        """Verify multiple well-known orgs are accessible."""
        result = api.orgs.get_org(org)
        assert result["login"] == org
        assert result["id"] > 0


@pytest.mark.test_orgs
class TestOrgMembers:
    """GET /orgs/{org}/members — list organization members."""

    def test_list_members_returns_list(self, api: GitHubAPI):
        """Verify member listing returns a list."""
        members = api.orgs.list_members(TEST_ORG)
        assert isinstance(members, list)

    def test_member_has_login(self, api: GitHubAPI):
        """Verify each member has login and id fields."""
        members = api.orgs.list_members(TEST_ORG)
        for member in members[:5]:
            assert "login" in member
            assert "id" in member


@pytest.mark.test_orgs
class TestOrgRepos:
    """GET /orgs/{org}/repos — list organization repositories."""

    def test_list_org_repos_returns_list(self, api: GitHubAPI):
        """Verify org repo listing returns a non-empty list."""
        repos = api.orgs.list_org_repos(TEST_ORG, per_page=5)
        assert isinstance(repos, list)
        assert len(repos) > 0

    def test_org_repos_have_full_name(self, api: GitHubAPI):
        """Verify each repo includes full_name with org prefix."""
        repos = api.orgs.list_org_repos(TEST_ORG, per_page=5)
        for repo in repos:
            assert "full_name" in repo
