# Changelog

## [1.0.0] - 2026-03-16

### Added
- Initial project scaffold with full directory structure
- GitHub REST API test framework targeting 7 endpoint domains
- `GitHubAPI` facade with sub-APIs: repos, users, orgs, search, issues, gists, actions
- `GitHubHTTPClient` with auth, rate limiting, and retry logic
- `RateLimiter` with automatic `X-RateLimit-*` header tracking
- `TestResultDB` for SQLite-backed test result recording
- JSON Schema validation via `utils/testing/schemas.py`
- Test suites for all 7 endpoint domains (70+ test cases)
- Comprehensive `.claude/` ruleset (7 rules, 3 commands)
- Comprehensive `.cursor/` ruleset (16 .mdc files)
- CI/CD pipeline via GitHub Actions (lint, test, security)
- Pre-commit hooks: ruff, mypy, codespell, gitleaks, bandit
- Utility scripts: version capture, rate limit check, cleanup
