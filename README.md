# GitHub API Test Automation Framework

A production-grade pytest framework for testing the [GitHub REST API](https://docs.github.com/en/rest). Built as a demo/reference implementation showcasing API test automation best practices.

## Features

- **Structured API facade** — Domain-scoped wrappers (`api.repos.*`, `api.users.*`, etc.)
- **Rate-limit aware** — Automatic throttling via `X-RateLimit-*` header tracking
- **Schema validation** — JSON Schema + lightweight field assertions
- **Database tracking** — SQLite-backed test result recording and regression snapshots
- **Security scanning** — gitleaks, bandit, semgrep, ruff security rules
- **CI/CD ready** — GitHub Actions workflow with lint, test, and security jobs
- **AI-assisted development** — `.claude/` and `.cursor/` rulesets for AI coding assistants

## Project Structure

```
├── .claude/                    # Claude Code rules, commands, agents
│   ├── commands/               # Slash commands
│   └── rules/                  # Project rules and conventions
├── .cursor/                    # Cursor IDE rules
│   └── rules/                  # .mdc ruleset files
├── .github/
│   └── workflows/ci.yml        # CI pipeline
├── config/                     # Configuration (gitignored secrets)
│   ├── config.example.json     # Template for config.json
│   └── db_config.json          # Database configuration
├── data/                       # Constants, test data, expected values
│   ├── constants.py            # Global constants (URLs, status codes, endpoints)
│   ├── repos_constants.py      # Repository test data
│   ├── users_constants.py      # User test data
│   ├── orgs_constants.py       # Organization test data
│   ├── search_constants.py     # Search query test data
│   ├── issues_constants.py     # Issue test data
│   ├── gists_constants.py      # Gist test data
│   └── actions_constants.py    # Actions test data
├── scripts/                    # Utility scripts
│   ├── capture_version_info.py # Capture API version metadata
│   ├── check_rate_limit.py     # Check current rate limit status
│   └── cleanup_test_data.py    # Clean up test artifacts
├── tests/                      # Test suites (endpoint-scoped)
│   ├── repos/                  # Repository endpoint tests
│   ├── users/                  # User endpoint tests
│   ├── orgs/                   # Organization endpoint tests
│   ├── search/                 # Search endpoint tests
│   ├── issues/                 # Issue endpoint tests
│   ├── gists/                  # Gist endpoint tests
│   └── actions/                # Actions endpoint tests
├── utils/                      # Shared utilities
│   ├── api/github_api.py       # GitHubAPI facade (primary interface)
│   ├── http/client.py          # HTTP client with auth & retries
│   ├── database/db.py          # SQLite test result tracker
│   ├── rate_limiting/          # Rate limiter
│   └── testing/                # Test helpers, schemas, assertions
├── conftest.py                 # Root fixtures (api, http_client, rate_limiter)
├── Makefile                    # Build targets
├── pyproject.toml              # Project config (pytest, ruff, mypy, coverage)
└── requirements.txt            # Python dependencies
```

## Quick Start

```bash
# Clone and set up
git clone <repo-url>
cd github-api-automation-pytest
make install

# (Optional) Configure authenticated mode for higher rate limits
cp config/config.example.json config/config.json
# Edit config.json with your GitHub PAT

# Run tests
make test                  # All tests
make test-repos            # Repository tests only
make test-users            # User tests only
pytest -m smoke            # Smoke tests

# Code quality
make lint                  # Ruff + mypy + codespell
make format                # Auto-format
make check                 # All pre-commit hooks
```

## Test Markers

| Marker | Description |
|--------|-------------|
| `test-repos` | Repository endpoint tests |
| `test-users` | User endpoint tests |
| `test-orgs` | Organization endpoint tests |
| `test-search` | Search endpoint tests |
| `test-issues` | Issue endpoint tests |
| `test-gists` | Gist endpoint tests |
| `test-actions` | GitHub Actions endpoint tests |
| `smoke` | Quick smoke tests for CI |
| `slow` | Tests that take longer to run |

## Architecture

### Four Calling Patterns

1. **Facade method** — `api.repos.get_repo("octocat", "Hello-World")` — preferred for most tests
2. **Raw HTTP** — `http_client.get("/repos/octocat/Hello-World")` — for status code / header validation
3. **Parameterized** — `@pytest.mark.parametrize` with test data constants
4. **Schema validation** — `jsonschema.validate(response, REPO_SCHEMA)`

### Rate Limiting

All API calls flow through the `RateLimiter` which reads GitHub's `X-RateLimit-*` headers and automatically pauses when approaching the limit. No manual rate handling needed in tests.

## Contributing

1. Follow the patterns in `CLAUDE.md` and `.cursor/rules/`
2. Add constants to `data/` — never hardcode strings in tests
3. Use the `GitHubAPI` facade — never bypass with raw `requests`
4. Run `make lint && make test` before committing
