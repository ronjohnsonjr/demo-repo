# Rate Limiting

## GitHub API Limits
- **Authenticated**: 5,000 requests/hour
- **Unauthenticated**: 60 requests/hour
- **Search API**: 30 requests/minute (separate limit)

## Implementation
- `utils/rate_limiting/rate_limiter.py` tracks `X-RateLimit-*` response headers
- Automatically sleeps when remaining quota drops below buffer (default: 5)
- Integrated into `GitHubHTTPClient` — all requests are rate-limited automatically

## Guidelines
- Never create HTTP clients outside of the fixture system.
- The `rate_limiter` fixture is session-scoped — shared across all tests.
- For search-heavy tests, consider limiting `per_page` to reduce API calls.
- Monitor `rate_limiter.total_requests` for debugging rate issues.
