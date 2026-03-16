"""Constants specific to organization endpoint tests."""

TEST_ORG = "github"
TEST_ORG_ID = 9919

TEST_ORGS = [
    "github",
    "google",
    "microsoft",
    "facebook",
]

ORG_REQUIRED_FIELDS = [
    "login",
    "id",
    "url",
    "description",
    "name",
    "public_repos",
    "public_gists",
    "followers",
    "following",
    "created_at",
]

GITHUB_ORG_EXPECTED = {
    "login": "github",
    "type": "Organization",
}
