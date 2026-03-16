"""Tests for GET /users/{username} endpoint.

Validates user profile retrieval, response schema, and known-value assertions.
"""

import pytest
from jsonschema import validate

from data.constants import HTTP_200_OK, HTTP_404_NOT_FOUND
from data.users_constants import (
    OCTOCAT_EXPECTED,
    TEST_USER_ID,
    TEST_USERNAME,
    TEST_USERS,
    USER_REQUIRED_FIELDS,
)
from utils.api.github_api import GitHubAPI
from utils.testing.helpers import assert_json_keys, assert_status_code
from utils.testing.schemas import USER_SCHEMA


@pytest.mark.test_users
class TestGetUser:
    """GET /users/{username} — retrieve a user profile."""

    def test_get_user_returns_profile(self, api: GitHubAPI):
        """Verify fetching a known user returns their profile."""
        result = api.users.get_user(TEST_USERNAME)
        assert result["login"] == TEST_USERNAME

    def test_get_user_response_schema(self, api: GitHubAPI):
        """Verify response matches the expected JSON schema."""
        result = api.users.get_user(TEST_USERNAME)
        validate(instance=result, schema=USER_SCHEMA)

    def test_get_user_required_fields(self, api: GitHubAPI):
        """Verify all required fields are present."""
        result = api.users.get_user(TEST_USERNAME)
        assert_json_keys(result, USER_REQUIRED_FIELDS)

    def test_get_user_known_values(self, api: GitHubAPI):
        """Verify known stable values for octocat."""
        result = api.users.get_user(TEST_USERNAME)

        assert result["login"] == OCTOCAT_EXPECTED["login"]
        assert result["id"] == OCTOCAT_EXPECTED["id"]
        assert result["type"] == OCTOCAT_EXPECTED["type"]

    def test_get_user_not_found(self, api: GitHubAPI):
        """Verify HTTP 404 for a nonexistent user."""
        resp = api.client.get("/users/this-user-definitely-does-not-exist-abc123xyz")
        assert_status_code(resp, HTTP_404_NOT_FOUND)

    @pytest.mark.parametrize("username", TEST_USERS)
    def test_get_multiple_users(self, api: GitHubAPI, username: str):
        """Verify multiple well-known users are accessible."""
        result = api.users.get_user(username)
        assert result["login"] == username
        assert result["id"] > 0

    def test_user_has_public_repos(self, api: GitHubAPI):
        """Verify user has public_repos count field."""
        result = api.users.get_user(TEST_USERNAME)
        assert "public_repos" in result
        assert isinstance(result["public_repos"], int)
        assert result["public_repos"] >= 0


@pytest.mark.test_users
class TestUserFollowers:
    """GET /users/{username}/followers — list followers."""

    def test_list_followers_returns_list(self, api: GitHubAPI):
        """Verify follower listing returns a list."""
        followers = api.users.list_followers(TEST_USERNAME)
        assert isinstance(followers, list)

    def test_follower_has_login(self, api: GitHubAPI):
        """Verify each follower has a login field."""
        followers = api.users.list_followers(TEST_USERNAME)
        for follower in followers[:5]:  # check first 5
            assert "login" in follower
            assert "id" in follower


@pytest.mark.test_users
class TestUserFollowing:
    """GET /users/{username}/following — list users followed by a user."""

    def test_list_following_returns_list(self, api: GitHubAPI):
        """Verify following listing returns a list."""
        following = api.users.list_following(TEST_USERNAME)
        assert isinstance(following, list)


@pytest.mark.test_users
class TestUserOrgs:
    """GET /users/{username}/orgs — list organizations for a user."""

    def test_list_user_orgs_returns_list(self, api: GitHubAPI):
        """Verify org listing returns a list."""
        orgs = api.users.list_user_orgs(TEST_USERNAME)
        assert isinstance(orgs, list)
