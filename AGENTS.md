# Agents Guide — GitHub API Test Automation

## For All Agents
- Run `make lint` before committing any code changes.
- Run `make test` after any code change to verify nothing is broken.
- Never commit files matching patterns in `.gitignore`.
- Never commit secrets, tokens, or `.env` files.

## For Coding Agents
- Follow patterns in `CLAUDE.md` strictly.
- Import constants from `data/` modules — never hardcode URLs, status codes, or endpoint paths.
- Add new test files under the appropriate `tests/` subdirectory.
- Add new utility modules under the appropriate `utils/` subdirectory.
- Every new test class needs the correct `@pytest.mark` decorator.
- Every new test function needs a Google-style docstring.

## For Review Agents
- Check that all imports use the project's constant modules.
- Verify test docstrings follow the rule-of-three format (Summary, Setup/Action/Assertions).
- Ensure no hardcoded URLs or API tokens appear in test code.
- Verify rate limiting is respected (no raw `requests.get()` calls).
