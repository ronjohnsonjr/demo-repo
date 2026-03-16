"""Constants specific to user endpoint tests."""

# Well-known public users for testing
TEST_USERNAME = "octocat"
TEST_USER_ID = 583231

# Additional test users
TEST_USERS = [
    "octocat",
    "torvalds",
    "defunkt",
    "mojombo",
]

# Expected fields in a user profile response
USER_REQUIRED_FIELDS = [
    "login",
    "id",
    "avatar_url",
    "type",
    "html_url",
    "name",
    "public_repos",
    "followers",
    "following",
    "created_at",
]

# Known values for octocat (GitHub's mascot account — stable)
OCTOCAT_EXPECTED = {
    "login": "octocat",
    "id": 583231,
    "type": "User",
}
