"""Constants specific to issue endpoint tests."""

# Well-known repo with issues for testing
TEST_ISSUES_OWNER = "octocat"
TEST_ISSUES_REPO = "Hello-World"

# Issue #1 in Hello-World is well-known and stable
TEST_ISSUE_NUMBER = 1

ISSUE_REQUIRED_FIELDS = [
    "id",
    "number",
    "title",
    "state",
    "user",
    "created_at",
    "updated_at",
]

ISSUE_STATES = ["open", "closed", "all"]

LABEL_REQUIRED_FIELDS = [
    "id",
    "name",
    "color",
    "description",
]
