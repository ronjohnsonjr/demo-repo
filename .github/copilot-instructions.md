# Copilot Instructions — GitHub API Test Automation

## Project Context
This is a pytest-based API test automation framework targeting the GitHub REST API.

## Key Conventions
- Use `GitHubAPI` facade methods instead of raw HTTP requests
- Import all constants from `data/` modules — never hardcode URLs or status codes
- Follow Google-style docstrings for all functions
- Every test needs a `@pytest.mark.<domain>` decorator
- Use `jsonschema.validate()` for response schema validation
- Never bypass the rate limiter — always use fixtures

## File Locations
- Tests: `tests/<domain>/test_*.py`
- API wrappers: `utils/api/github_api.py`
- HTTP client: `utils/http/client.py`
- Constants: `data/constants.py` and `data/<domain>_constants.py`
- Schemas: `utils/testing/schemas.py`
