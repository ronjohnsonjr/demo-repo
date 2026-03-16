"""Constants specific to repository endpoint tests."""

# Well-known public repos used as test fixtures
TEST_REPO_OWNER = "octocat"
TEST_REPO_NAME = "Hello-World"
TEST_REPO_FULL_NAME = f"{TEST_REPO_OWNER}/{TEST_REPO_NAME}"

# Large / popular repos for pagination and stress tests
POPULAR_REPOS = [
    ("torvalds", "linux"),
    ("microsoft", "vscode"),
    ("facebook", "react"),
    ("tensorflow", "tensorflow"),
]

# Expected fields in a repository response
REPO_REQUIRED_FIELDS = [
    "id",
    "name",
    "full_name",
    "owner",
    "html_url",
    "description",
    "fork",
    "url",
    "created_at",
    "updated_at",
    "stargazers_count",
    "watchers_count",
    "forks_count",
    "default_branch",
]

REPO_OWNER_REQUIRED_FIELDS = [
    "login",
    "id",
    "avatar_url",
    "type",
]

# Known values for Hello-World repo (stable, owned by GitHub)
HELLO_WORLD_EXPECTED = {
    "name": "Hello-World",
    "full_name": "octocat/Hello-World",
    "fork": False,
    "default_branch": "master",
    "owner_login": "octocat",
}
