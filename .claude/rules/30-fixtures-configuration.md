# Fixtures & Configuration

## Session-Scoped Fixtures (conftest.py)
- `github_token` — Loads token from env or config/config.json
- `rate_limiter` — Shared rate limiter instance
- `http_client` — Configured `GitHubHTTPClient` with auth and rate limiting
- `api` — `GitHubAPI` facade (primary test interface)

## Function-Scoped Fixtures
- `unique_suffix` — Random string for resource naming
- `_log_test_boundaries` (autouse) — Logs test start/end with timing

## Guidelines
- Prefer the `api` fixture over `http_client` for most tests.
- Use `http_client` only when testing raw HTTP behavior (status codes, headers).
- Never create standalone `requests.Session` instances — always go through fixtures.
- New fixtures should be added to the root `conftest.py` or a domain-specific `conftest.py`.
