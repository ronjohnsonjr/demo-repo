# Testing Strategy

## Test Organization
- Tests live under `tests/` in endpoint-scoped subdirectories: `repos/`, `users/`, `orgs/`, `search/`, `issues/`, `gists/`, `actions/`.
- Each test file focuses on a single endpoint or closely related group.
- Use `@pytest.mark.<domain>` markers for selective test execution.

## Test Structure (Rule of Three)
Every test function should follow this pattern:
1. **Setup** — Prepare test data, configure fixtures
2. **Action** — Call the API endpoint under test
3. **Assertions** — Verify response status, schema, and values

## Fixtures
- `api` (session-scoped) — Primary `GitHubAPI` facade instance
- `http_client` (session-scoped) — Low-level HTTP client with auth and rate limiting
- `rate_limiter` (session-scoped) — Shared rate limiter
- `unique_suffix` (function-scoped) — Unique string for test resource naming

## Schema Validation
- Use `jsonschema.validate()` with schemas from `utils/testing/schemas.py`.
- Use `assert_json_keys()` for lightweight required-field checks.

## Running Tests
```bash
make test              # all tests
make test-repos        # repos only
make test-users        # users only
pytest -m smoke        # smoke tests
```
