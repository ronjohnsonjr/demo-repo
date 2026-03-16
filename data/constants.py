"""Global constants shared across all test modules.

Convention: Import from here instead of hardcoding strings.
"""

# ---------------------------------------------------------------------------
# API Base Configuration
# ---------------------------------------------------------------------------
BASE_URL = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"

# ---------------------------------------------------------------------------
# HTTP Status Codes
# ---------------------------------------------------------------------------
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_301_MOVED = 301
HTTP_304_NOT_MODIFIED = 304
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_422_UNPROCESSABLE = 422
HTTP_429_RATE_LIMITED = 429
HTTP_500_SERVER_ERROR = 500

# ---------------------------------------------------------------------------
# Endpoint Path Templates
# ---------------------------------------------------------------------------
ENDPOINT_REPOS = "/repos/{owner}/{repo}"
ENDPOINT_REPO_BRANCHES = "/repos/{owner}/{repo}/branches"
ENDPOINT_REPO_TAGS = "/repos/{owner}/{repo}/tags"
ENDPOINT_REPO_CONTRIBUTORS = "/repos/{owner}/{repo}/contributors"
ENDPOINT_REPO_LANGUAGES = "/repos/{owner}/{repo}/languages"
ENDPOINT_REPO_README = "/repos/{owner}/{repo}/readme"
ENDPOINT_REPO_COMMITS = "/repos/{owner}/{repo}/commits"
ENDPOINT_REPO_ISSUES = "/repos/{owner}/{repo}/issues"
ENDPOINT_REPO_LABELS = "/repos/{owner}/{repo}/labels"

ENDPOINT_USERS = "/users/{username}"
ENDPOINT_USER_REPOS = "/users/{username}/repos"
ENDPOINT_USER_FOLLOWERS = "/users/{username}/followers"
ENDPOINT_USER_FOLLOWING = "/users/{username}/following"
ENDPOINT_USER_GISTS = "/users/{username}/gists"
ENDPOINT_USER_ORGS = "/users/{username}/orgs"

ENDPOINT_ORGS = "/orgs/{org}"
ENDPOINT_ORG_MEMBERS = "/orgs/{org}/members"
ENDPOINT_ORG_REPOS = "/orgs/{org}/repos"

ENDPOINT_SEARCH_REPOS = "/search/repositories"
ENDPOINT_SEARCH_USERS = "/search/users"
ENDPOINT_SEARCH_CODE = "/search/code"
ENDPOINT_SEARCH_ISSUES = "/search/issues"

ENDPOINT_GISTS_PUBLIC = "/gists/public"
ENDPOINT_GISTS = "/gists/{gist_id}"

ENDPOINT_ACTIONS_WORKFLOWS = "/repos/{owner}/{repo}/actions/workflows"
ENDPOINT_ACTIONS_RUNS = "/repos/{owner}/{repo}/actions/runs"

# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------
RATE_LIMIT_AUTHENTICATED = 5000
RATE_LIMIT_UNAUTHENTICATED = 60
RATE_LIMIT_SEARCH = 30  # Search API has its own lower limit
RATE_LIMIT_BUFFER = 5

# ---------------------------------------------------------------------------
# Pagination Defaults
# ---------------------------------------------------------------------------
DEFAULT_PER_PAGE = 30
MAX_PER_PAGE = 100
